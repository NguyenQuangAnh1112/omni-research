import sys

from langchain_core.messages import HumanMessage

from src.agents.supervisor import app
from src.utils.logger import logger


def main():
    print("Gõ 'exit' hoặc 'quit' để thoát.\n")

    config = {"configurable": {"thread_id": "1"}}

    while True:
        user_input = input("\nNhập chủ đề: ").strip()
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

        app.update_state(config=config, values=initial_state)

        while True:
            # Chạy graph cho đến khi dừng (interrupt hoặc kết thúc)
            try:
                for event in app.stream(None, config=config):
                    for key, _ in event.items():
                        print(f"   Using Node: {key}...")
            except Exception as e:
                logger.error(f" Lỗi Graph: {e}")
                break

            # Kiểm tra state sau khi stream dừng
            snapshot = app.get_state(config=config)
            if not snapshot.values:
                break

            state_data = snapshot.values
            next_step = state_data.get("next_step")
            draft = state_data.get("current_draft")

            # Nếu đã hoàn tất
            if next_step == "FINISH":
                print("\nQuy trình hoàn tất! File đã được lưu.")
                print("-" * 50)
                break

            # Kiểm tra xem graph có đang dừng tại interrupt point (human_review) không
            is_pending_review = snapshot.next and "human_review" in snapshot.next
            if is_pending_review and draft:
                print("\n" + "=" * 50)
                print("📄 BẢN NHÁP ĐỀ XUẤT TỪ WRITER:")
                print("=" * 50)
                preview = draft[:1000] + ("..." if len(draft) > 1000 else "")
                print(preview)
                print("=" * 50)

                choice = (
                    input("\nREVIEW: Bạn có duyệt bài này không? (yes/no): ")
                    .strip()
                    .lower()
                )

                if choice in ["y", "yes", "ok", "duyet", "đồng ý"]:
                    print(">> Đã duyệt! Đang tiến hành lưu file...")
                    app.update_state(config=config, values={"next_step": "PUBLISH"})
                    # Tiếp tục vòng lặp để chạy stream() tiếp
                else:
                    feedback = input(">> Hãy nhập yêu cầu sửa đổi (Feedback): ").strip()
                    print(">> Đã gửi yêu cầu cho Writer viết lại.")
                    app.update_state(
                        config=config,
                        values={"next_step": "WRITE", "feedback": feedback},
                    )
                    # Tiếp tục vòng lặp để chạy stream() tiếp
            else:
                # Trạng thái không xác định hoặc graph đã kết thúc
                if not snapshot.next:
                    # Graph đã kết thúc nhưng không ở FINISH
                    logger.warning(f"Graph kết thúc ở trạng thái: {next_step}")
                    break
                else:
                    logger.warning(f"Trạng thái không xác định. next_step={next_step}, pending={snapshot.next}")
                    break


if __name__ == "__main__":
    main()
