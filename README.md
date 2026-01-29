## Omni Research

### 1. Tổng quan hệ thống (System Overview)

**Omni-Research** là một hệ thống Multi-Agent phân cấp (Hierarchical Agent System) chạy trên Terminal.

- **Input:** Người dùng nhập một chủ đề (VD: "Tương lai của AI Agent").
- **Process:**
  1. **Researcher:** Tự động tìm kiếm, thu thập thông tin từ nhiều nguồn (Tavily/Wiki).
  2. **Writer:** Tổng hợp thông tin, viết thành bài báo Markdown (`.md`).
  3. **Supervisor:** Điều phối luồng đi, không làm việc cụ thể.
  4. **Human (Bạn):** Đóng vai trò kiểm duyệt viên (Editor). Duyệt bài trước khi xuất bản.
- **Output:** File báo cáo nằm trong thư mục `reports/`.

---

### 2. Luồng dữ liệu (Data Flow Diagram)

Đây là bản đồ đường đi của dữ liệu. Bạn cần hiểu rõ cái này để code `State` không bị rối.

**Quy trình chi tiết:**

1. **User** gửi yêu cầu -> **Supervisor**.
2. **Supervisor** phân tích -> Gửi lệnh sang **Researcher**.
3. **Researcher** (Subgraph) chạy vòng lặp tìm kiếm -> Trả về `research_data` (Dữ liệu thô).
4. **Supervisor** nhận dữ liệu -> Gửi sang **Writer**.
5. **Writer** (Subgraph) đọc dữ liệu -> Viết bài -> Trả về `draft` (Bản nháp).
6. **Supervisor** nhận bản nháp -> **TẠM DỪNG (Interrupt)** để hỏi ý kiến User.
7. **User Review:**
   - _Trường hợp 1 (OK):_ User gõ "Approved" -> Gọi **Publisher** -> Lưu file -> Kết thúc.
   - _Trường hợp 2 (Reject):_ User gõ "Sửa đoạn mở bài đi" -> Quay lại **Writer** -> Viết lại -> Lặp lại bước 6.

---

### 3. Định nghĩa State (Data Structures) 💾

Trong LangGraph, State là "trái tim". Chúng ta cần thiết kế State tách biệt để đảm bảo tính đóng gói (Encapsulation).

#### A. `SuperState` (State chung của cả hệ thống)

Đây là cuốn "sổ cái" mà Supervisor cầm.

| **Tên biến**    | **Kiểu dữ liệu**    | **Mô tả**                                                             |
| --------------- | ------------------- | --------------------------------------------------------------------- |
| `messages`      | `list[BaseMessage]` | Lịch sử chat tổng quát với User.                                      |
| `research_data` | `list[str]`         | Danh sách các đoạn thông tin mà Researcher tìm được. (Để Writer đọc). |
| `current_draft` | `str`               | Nội dung bài viết hiện tại.                                           |
| `next_step`     | `str`               | Bước tiếp theo (RESEARCH, WRITE, PUBLISH, FINISH).                    |

#### B. `ResearcherState` (State riêng của đội tìm kiếm)

Chỉ quan tâm việc tìm tin, không quan tâm việc viết bài.

| **Tên biến** | **Kiểu dữ liệu**    | **Mô tả**                              |
| ------------ | ------------------- | -------------------------------------- |
| `topic`      | `str`               | Chủ đề cần tìm (Input từ cha).         |
| `logs`       | `list[BaseMessage]` | Lịch sử chạy tool tìm kiếm (Internal). |
| `findings`   | `list[str]`         | Kết quả tìm được (Output trả về cha).  |

#### C. `WriterState` (State riêng của đội viết bài)

| **Tên biến** | **Kiểu dữ liệu** | **Mô tả**                                         |
| ------------ | ---------------- | ------------------------------------------------- |
| `materials`  | `list[str]`      | Dữ liệu đầu vào (Lấy từ `research_data` của cha). |
| `feedback`   | `str`            | Góp ý của User (nếu có yêu cầu sửa).              |
| `draft`      | `str`            | Bài viết hoàn chỉnh (Output trả về cha).          |

---

### 4. Đặc tả API & Tools

#### Tool 1: `TavilySearch` (Có sẵn)

- **Input:** Query string.
- **Output:** JSON search results.

#### Tool 2: `save_report` (Tự viết)

- **Chức năng:** Lưu string vào file `.md`.
- **Input:**
  - `content`: Nội dung bài viết.
  - `filename`: Tên file (VD: `report_v1.md`).
- **Yêu cầu:** Phải dùng `logger` để ghi log và `@handle_errors` để bắt lỗi IO.

---

### 5. Cấu trúc thư mục (Finalized) 📂

Bạn hãy tạo cây thư mục y hệt như thế này:

Plaintext

```
omni-research/
├── .env                  # Chứa TAVILY_API_KEY
├── logs/                 # Chứa app.log
│   └── app.log
├── reports/              # Nơi xuất file báo cáo
├── src/
│   ├── __init__.py
│   ├── main.py           # [Entry Point] Chạy app, vòng lặp chat
│   ├── state.py          # [Model] Định nghĩa các class TypedDict
│   ├── agents/           # [Controller] Logic các Node
│   │   ├── __init__.py
│   │   ├── researcher.py # Subgraph Tìm kiếm
│   │   ├── writer.py     # Subgraph Viết bài
│   │   └── supervisor.py # Graph Cha + Routing Logic
│   ├── tools/            # [Service] Các công cụ
│   │   ├── __init__.py
│   │   ├── search_tools.py
│   │   └── file_tools.py
│   └── utils/            # [Infrastructure] Tiện ích
│       ├── __init__.py
│       ├── llm.py        # Hàm get_llm()
│       ├── logger.py     # (Đã có)
│       └── exception.py  # (Đã có)
└── pyproject.toml
```

---

### 6. Nhiệm vụ lập trình (Coding Tasks)

Chúng ta sẽ code theo thứ tự từ trong ra ngoài (Bottom-Up) để dễ test:

1. **Phase 1: Foundation (Nền móng)**
   - Code `src/state.py`: Định nghĩa các TypedDict.
   - Code `src/utils/llm.py`: Setup Ollama.
   - Code `src/tools/`: Setup Tavily và File Tool.

2. **Phase 2: Subgraphs (Nhân viên)**
   - Code `src/agents/researcher.py`: ReAct loop tìm kiếm.
   - Code `src/agents/writer.py`: Prompt LLM viết bài từ list dữ liệu.

3. **Phase 3: Supervisor & Main (Sếp & Tích hợp)**
   - Code `src/agents/supervisor.py`: Logic router, Human-in-the-loop.
   - Code `src/main.py`: Chạy CLI.
