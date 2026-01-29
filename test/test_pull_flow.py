import os
import shutil
import sys
from pathlib import Path  # <--- [QUAN TRỌNG] Thêm thư viện này

from langchain_core.messages import HumanMessage

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.supervisor import app
from src.utils.logger import logger

# --- SỬA LẠI ĐOẠN KHỞI TẠO REPORT_DIR ---
# 1. Lấy đường dẫn gốc của project (Parent của thư mục test)
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Trỏ vào thư mục reports bên trong project
REPORT_DIR = BASE_DIR / "reports"

# 3. Đảm bảo thư mục này tồn tại (Nếu chưa có thì tạo mới)
if not REPORT_DIR.exists():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Đã tạo thư mục reports tại: {REPORT_DIR}")


def test_full_system():
    print("\n🚀 --- TEST TỰ ĐỘNG TOÀN BỘ HỆ THỐNG --- 🚀\n")

    # 1. SETUP
    topic = "Test quy trình tự động Omni Research"
    config = {"configurable": {"thread_id": "test_thread_1"}}

    # Xóa file cũ nếu có để test cho chuẩn
    # Logic trong file_tools.py: filename.strip().replace(" ", "_")
    expected_filename = f"report_{topic[:20].strip().replace(' ', '_')}.md"
    expected_path = REPORT_DIR / expected_filename  # Bây giờ dùng toán tử / mới đúng

    if expected_path.exists():
        try:
            os.remove(expected_path)
            print(f"🗑️ Đã xóa file cũ: {expected_filename}")
        except OSError as e:
            print(f"⚠️ Không thể xóa file cũ: {e}")

    print(f"👉 Bước 1: Khởi tạo với chủ đề: '{topic}'")
    initial_state = {
        "messages": [HumanMessage(content=topic)],
        "next_step": "RESEARCH",
        "feedback": "",
    }
    app.update_state(config, initial_state)

    # 2. CHẠY LẦN 1 (Mong đợi: Researcher -> Writer -> Dừng ở REVIEW)
    print("⏳ Đang chạy Researcher & Writer (Có thể mất 10-20s)...")
    try:
        # Chạy graph cho đến khi nó tự dừng
        for event in app.stream(None, config=config):
            for key, value in event.items():
                print(f"   ✓ Đã chạy qua Node: [{key}]")
    except Exception as e:
        print(f"❌ Lỗi khi chạy lần 1: {e}")
        return

    # 3. KIỂM TRA TRẠNG THÁI DỪNG (Interrupt trước human_review)
    snapshot = app.get_state(config)
    if not snapshot.values:
        print("❌ FAIL: State rỗng!")
        return

    state = snapshot.values

    # Check xem graph có đang pending ở interrupt point không
    # snapshot.next cho biết node tiếp theo sẽ chạy
    if snapshot.next and "human_review" in snapshot.next:
        print("\n✅ PASS: Hệ thống đã dừng đúng chỗ để chờ duyệt (interrupt trước human_review).")
        if state.get("current_draft"):
            print(f"   Draft preview: {state['current_draft'][:100]}...")
    else:
        print(
            f"\n❌ FAIL: Hệ thống không dừng đúng chỗ. Next nodes: {snapshot.next}"
        )
        return

    # 4. GIẢ LẬP CON NGƯỜI DUYỆT BÀI (Simulate Human Feedback)
    print("\n👉 Bước 2: Giả lập người dùng bấm 'YES' (Duyệt bài)...")
    # Update state để router biết cần publish
    app.update_state(config, {"next_step": "PUBLISH"})

    # 5. CHẠY LẦN 2 (Mong đợi: human_review → Publisher → FINISH)
    print("⏳ Đang chạy Human Review → Publisher...")
    for event in app.stream(None, config=config):
        for key, value in event.items():
            print(f"   ✓ Đã chạy qua Node: [{key}]")

    # 6. KIỂM TRA KẾT QUẢ CUỐI CÙNG
    snapshot = app.get_state(config)
    final_step = snapshot.values.get("next_step")

    if final_step == "FINISH":
        print("\n✅ PASS: Hệ thống đã chuyển sang trạng thái FINISH.")
    else:
        print(f"\n❌ FAIL: Trạng thái cuối cùng sai: {final_step}")

    # 7. KIỂM TRA FILE CÓ TỒN TẠI KHÔNG
    if expected_path.exists():
        print(f"✅ PASS: File báo cáo đã được tạo tại: {expected_path}")
        print("-" * 30)
        # Đọc thử nội dung
        try:
            with open(expected_path, "r", encoding="utf-8") as f:
                print(f.read()[:200] + "...")
        except Exception as e:
            print(f"⚠️ Có file nhưng không đọc được: {e}")
        print("-" * 30)
    else:
        print(f"❌ FAIL: Không tìm thấy file báo cáo tại {expected_path}")


if __name__ == "__main__":
    test_full_system()
