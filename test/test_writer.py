import os
import sys

# Fix đường dẫn import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.writer import writer_graph
from src.utils.logger import logger


def test_writer():
    print("\n--- ✍️ TEST WRITER AGENT ---\n")

    # 1. Giả lập dữ liệu mà Researcher tìm được
    # (Bịa ra một vài thông tin về CachyOS)
    dummy_materials = [
        "CachyOS là một bản phân phối Linux dựa trên Arch Linux, được tối ưu hóa cho hiệu suất cao.",
        "Nó sử dụng kernel bore-scheduler để cải thiện độ trễ hệ thống.",
        "CachyOS mặc định hỗ trợ file system XFS và Btrfs, cùng với trình cài đặt GUI dễ dùng.",
        "Nó cũng có kho repository riêng với các gói phần mềm được biên dịch lại (v3, v4) để tận dụng tập lệnh CPU hiện đại.",
    ]

    initial_state = {
        "materials": dummy_materials,
        "feedback": "",  # Lần đầu chưa có feedback
        "draft": "",
    }

    logger.info(f"Input Materials: {len(dummy_materials)} đoạn thông tin.")

    # 2. Chạy Graph
    try:
        result = writer_graph.invoke(initial_state)

        print("\n--- 📄 KẾT QUẢ BẢN NHÁP (DRAFT) ---")
        print("-" * 30)
        print(result["draft"])
        print("-" * 30)

        if result["draft"] and "CachyOS" in result["draft"]:
            print("\n✅ TEST THÀNH CÔNG: Writer đã viết bài đúng chủ đề!")
        else:
            print("\n❌ TEST THẤT BẠI: Writer trả về rỗng hoặc sai.")

    except Exception as e:
        logger.error(f"Lỗi Writer: {e}", exc_info=True)


if __name__ == "__main__":
    test_writer()
