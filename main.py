import asyncio
import os
import sys

sys.path.append(os.getcwd())

from langchain_core.messages import HumanMessage

from src.agents.supervisor import app
from src.utils.logger import logger


async def main():
    print("\n🤖 --- OMNI-RESEARCH CLI (STREAMING) --- 🤖")
    print("Gõ 'exit' hoặc 'quit' để thoát.\n")

    config = {"configurable": {"thread_id": "1"}}

    while True:
        try:
            user_input = input("\n👤 Nhập chủ đề: ").strip()
        except KeyboardInterrupt:
            break

        if user_input.lower() in ["exit", "quit"]:
            print("\nTạm biệt.")
            break
        if not user_input:
            continue

        logger.info(f"Bắt đầu quy trình với chủ đề: {user_input}")

        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "next_step": "RESEARCH",
            "feedback": "",
        }

        await app.aupdate_state(config, initial_state)

        while True:
            print("\nCyberspace activity: ", end="", flush=True)

            try:
                async for event in app.astream_events(None, config, version="v2"):
                    kind = event["event"]

                    if kind == "on_tool_start":
                        print(
                            f"\n⚡ Đang dùng công cụ: {event['name']}...",
                            end="\n",
                            flush=True,
                        )

                    elif kind == "on_chat_model_stream":
                        chunk = event["data"]["chunk"]
                        if chunk.content:
                            print(chunk.content, end="", flush=True)

            except Exception as e:
                logger.error(f"\n❌ Lỗi Graph: {e}")
                break

            print("\n")

            snapshot = await app.aget_state(config)

            if not snapshot.values:
                break

            state_data = snapshot.values
            next_step = state_data.get("next_step")
            draft = state_data.get("current_draft")

            if next_step == "FINISH":
                print(f"✅ Quy trình hoàn tất! (File đã lưu)")
                print("-" * 50)
                break

            if next_step == "REVIEW" and draft:
                print("\n" + "=" * 50)
                print("👮‍♂️ CHỜ DUYỆT BÀI (Hệ thống đang tạm dừng)")
                print("=" * 50)

                choice = (
                    input("\nBạn có duyệt bài trên không? (yes/no): ").strip().lower()
                )

                if choice in ["y", "yes", "ok", "duyet", "đồng ý"]:
                    print(">> ✅ Đã duyệt! Đang lưu file...")
                    await app.aupdate_state(config, {"next_step": "PUBLISH"})

                else:
                    feedback = input(">> ✍️ Feedback sửa đổi: ").strip()
                    print(">> Đã gửi yêu cầu viết lại.")
                    await app.aupdate_state(
                        config,
                        {"next_step": "WRITE", "feedback": feedback},
                    )

            elif next_step not in ["RESEARCH", "WRITE", "PUBLISH", "REVIEW", "FINISH"]:
                logger.warning(f"Graph dừng ở trạng thái lạ: {next_step}")
                break


if __name__ == "__main__":
    asyncio.run(main())
