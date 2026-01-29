# test_phase_1.py
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Import các module bạn đã xây
try:
    from src.model.llm import llm  # Tùy cách bạn đặt tên hàm
    from src.tools.file_tools import save_report

    # Lưu ý: Sửa tên biến import dưới đây theo đúng tên bạn đặt trong file search_tools.py
    from src.tools.search_tools import tavily_tool
    from src.utils.logger import logger
except ImportError as e:
    print(f"❌ LỖI IMPORT: {e}")
    print("Bạn hãy kiểm tra lại tên file hoặc tên hàm trong folder src/")
    exit(1)

# Load biến môi trường
load_dotenv()


def run_test():
    print("\n--- 🚀 BẮT ĐẦU TEST PHASE 1 ---\n")

    # 1. TEST LOGGER
    logger.info("Test Logger: Dòng này phải có màu xanh lá.")
    print("✅ Logger OK\n")

    # 2. TEST LLM (Ollama)
    try:
        logger.info("Đang gọi Ollama (Qwen2.5)...")
        # llm = get_llm() # Nếu bạn dùng hàm get_llm
        response = llm.invoke(
            [HumanMessage(content="Chào bạn, hãy nói 'OK' nếu bạn nghe thấy tôi.")]
        )
        logger.info(f"Ollama trả lời: {response.content}")
        print("✅ LLM Connection OK\n")
    except Exception as e:
        logger.error(f"❌ LLM Lỗi: {e}")

    # 3. TEST TAVILY SEARCH
    try:
        logger.info("Đang test Tavily Search...")
        # Giả lập gọi tool
        search_result = tavily_tool.invoke("LangGraph là gì?")
        # Kết quả Tavily thường là string JSON hoặc list
        logger.info(f"Kết quả tìm kiếm (Snippet): {str(search_result)[:100]}...")
        print("✅ Tavily Search OK\n")
    except Exception as e:
        logger.error(f"❌ Tavily Lỗi (Kiểm tra API Key trong .env): {e}")

    # 4. TEST FILE TOOL (Quan trọng: Check đường dẫn tuyệt đối)
    try:
        logger.info("Đang test ghi file report...")
        result = save_report.invoke(
            {
                "content": "# Test File\nĐây là file test tự động.",
                "filename": "test_phase_1.md",
            }
        )
        logger.info(f"Kết quả ghi file: {result}")

        # Kiểm tra xem file có thật sự tồn tại không
        if os.path.exists("reports/test_phase_1.md"):
            print("✅ File Tool OK (Đã thấy file trong folder reports/)")
        else:
            logger.error("❌ File Tool Lỗi: Không thấy file đâu cả!")

    except Exception as e:
        logger.error(f"❌ File Tool Crash: {e}")

    print("\n--- 🎉 KẾT THÚC BÀI TEST ---")


if __name__ == "__main__":
    run_test()
