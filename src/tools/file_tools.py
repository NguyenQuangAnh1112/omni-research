import os
from pathlib import Path

from langchain_core.tools import tool

from src.utils.exception import he
from src.utils.logger import logger

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REPORT_DIR = PROJECT_ROOT / "reports"

if not os.path.exists(REPORT_DIR):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


@tool
@he
def save_report(content: str, filename: str):
    """
    Lưu bài viết Markdown vào thư mục 'reports' tại thư mục gốc của dự án.
    """
    logger.info(f"Đang xử lý lưu file: {filename}...")

    filename = filename.strip().replace(" ", "_")
    if not filename.endswith(".md"):
        filename += ".md"

    clean_content = content.strip()

    if not clean_content.startswith("---"):
        from datetime import datetime

        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"---\ntitle: {filename}\ndate: {date_str}\ngenerated_by: Omni-Research-CLI\n---\n\n"
        clean_content = header + clean_content

    file_path = REPORT_DIR / filename

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(clean_content)

    logger.info(f"✅ Đã lưu file chuẩn đẹp tại: {file_path}")
    return f"Đã lưu báo cáo thành công: {file_path}"
