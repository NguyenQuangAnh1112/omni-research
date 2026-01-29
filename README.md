### Omni Research

omni-research/
├── .env # Chứa API Key (Tavily, Pinecone...)
├── .gitignore # Bỏ qua file rác, **pycache**, .env
├── pyproject.toml # File quản lý dependency của uv
├── README.md # Hướng dẫn sử dụng
├── data/ # Nơi lưu DB SQLite (Memory)
├── reports/ # Nơi Agent xuất file báo cáo kết quả
└── src/ # Source code chính
├── **init**.py
├── main.py # File chạy chính (Entry point)
├── state.py # Định nghĩa các TypedDict (SuperState, AgentState)
├── tools/ # Chứa code các Tools tùy chỉnh
│ ├── **init**.py
│ ├── search_tools.py # Tavily, Wiki
│ └── file_tools.py # Ghi file
├── agents/ # Chứa logic từng Agent
│ ├── **init**.py
│ ├── researcher.py # Subgraph Researcher
│ ├── writer.py # Subgraph Writer
│ └── supervisor.py # Graph Cha (Router Logic)
└── utils/ # Các hàm phụ trợ
├── **init**.py
└── llm.py # Khởi tạo ChatOllama dùng chung
