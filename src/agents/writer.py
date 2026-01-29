from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from src.model.llm import llm
from src.state import WriterState
from src.utils.exception import he
from src.utils.logger import logger

WRITER_SYSTEM_PROMPT = """
Bạn là một Biên tập viên kỹ thuật cấp cao (Senior Technical Editor).
Nhiệm vụ của bạn là tổng hợp các thông tin rời rạc thành một báo cáo chuyên sâu.

QUY TẮC ĐỊNH DẠNG (BẮT BUỘC):
1. Sử dụng định dạng **Markdown** chuẩn.
2. Tiêu đề chính dùng `#` (H1), các mục con dùng `##` (H2) và `###` (H3).
3. Các ý quan trọng phải **in đậm**.
4. Sử dụng danh sách (bullet points) `-` để liệt kê cho dễ đọc.
5. Code hoặc lệnh (nếu có) phải để trong block code (```python ... ```).
6. KHÔNG được trả về lời dẫn chuyện thừa thãi (như "Dưới đây là bài viết...", "Chắc chắn rồi...").
7. Chỉ trả về nội dung bài viết.

MỤC TIÊU:
Bài viết phải có bố cục rõ ràng: Mở bài, Thân bài (chia nhỏ các ý), và Kết luận.
"""


@he
def writer_node(state: WriterState):
    materials = state.get("materials", [])
    feedback = state.get("feedback", "")

    if not materials:
        logger.info("Writer nhận được danh sách tài liệu rỗng.")
        return {"draft": "Lỗi: không có dữ liệu để viết bài."}

    context_str = "\n\n".join(materials)

    user_content = f"Dựa trên tài liệu nghiên cứu sau: \n\n{context_str}\n\nHãy viết một bài báo cáo chi tiết."

    if feedback:
        user_content += f"\n\nLƯU Ý QUAN TRỌNG TỪ NGƯỜI DUYỆT BÀI: {feedback}"

    message = [
        SystemMessage(content=WRITER_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    result = llm.invoke(message)

    return {"draft": result.content}


workflow = StateGraph(WriterState)

workflow.add_node("writer", writer_node)

workflow.add_edge(START, "writer")
workflow.add_edge("writer", END)

writer_graph = workflow.compile()
