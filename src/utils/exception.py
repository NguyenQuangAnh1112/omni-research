# AI code
import functools
from typing import Any, Callable, Optional

from langchain_core.messages import AIMessage

# Import cái logger Singleton mà chúng ta vừa tạo ở bài trước
# Để set làm mặc định, không cần truyền đi truyền lại
from src.utils.logger import logger as default_logger


# --- 1. CUSTOM EXCEPTIONS ---
class OmniError(Exception):
    """Lỗi gốc của dự án"""

    pass


class ToolExecutionError(OmniError):
    pass


class AgentReasoningError(OmniError):
    pass


# --- 2. DECORATOR FACTORY ---
def handle_errors(return_on_error: Optional[Any] = None, logger=default_logger):
    """
    Decorator Factory: Dùng để tạo ra decorator bắt lỗi.
    - logger: Mặc định lấy từ src.utils.logger (bạn không cần truyền nữa)
    - return_on_error: Giá trị trả về khi lỗi.
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)

            except ToolExecutionError as e:
                logger.error(f"🔧 Lỗi Tool [{func.__name__}]: {e}")
                if return_on_error is not None:
                    return return_on_error
                raise e

            except Exception as e:
                # Ghi log kèm số dòng code (nhờ logger mới)
                logger.critical(f"🔥 Lỗi tại [{func.__name__}]: {e}", exc_info=True)

                if return_on_error is not None:
                    return return_on_error

                # Trả về format chuẩn cho LangGraph nếu không có chỉ định khác
                return {"messages": [AIMessage(content=f"HỆ THỐNG GẶP LỖI: {str(e)}")]}

        return wrapper

    return decorator


# --- 3. BIẾN DÙNG NHANH (SHORTCUT) ---
# Đây chính là biến 'he' mà bạn muốn.
# Nó tương đương với việc gọi @handle_errors(logger=default_logger, return_on_error=None)
# Dùng cho các hàm Agent thông thường.
he = handle_errors()
