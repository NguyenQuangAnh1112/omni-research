# File: test/test_researcher.py
import os
import sys

# Mẹo: Thêm đường dẫn gốc vào sys.path để Python tìm thấy folder 'src'
# Nếu không có dòng này, khi chạy từ trong folder test sẽ bị lỗi "ModuleNotFoundError"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.researcher import researcher_graph
from src.utils.logger import logger


def test_researcher():
    print("\n--- 🧪 TEST RESEARCHER AGENT ---\n")

    # 1. Giả lập Input
    initial_state = {
        "topic": "Các model LLM mã nguồn mở tốt nhất 2025",
        "logs": [],
        "findings": [],
    }

    logger.info(f"Topic: {initial_state['topic']}")

    # 2. Chạy Graph
    try:
        # Sử dụng .stream để in ra từng bước chạy
        for event in researcher_graph.stream(initial_state):
            for key, value in event.items():
                print(f"\n👉 Đang chạy Node: [{key}]")
                # print(value) # Uncomment để xem data chi tiết

        # 3. Lấy kết quả cuối
        final_state = researcher_graph.invoke(initial_state)

        print("\n--- 🏁 KẾT QUẢ CUỐI CÙNG (FINDINGS) ---")
        if final_state["findings"]:
            print(f"✅ Đã tìm thấy {len(final_state['findings'])} dữ liệu.")
            print("-" * 20)
            print(final_state["findings"][0][:500] + "...")  # In 500 ký tự đầu
            print("-" * 20)
        else:
            print("\n❌ TEST THẤT BẠI: Không có findings.")

    except Exception as e:
        logger.error(f"Lỗi khi chạy Researcher: {e}", exc_info=True)


if __name__ == "__main__":
    test_researcher()
