import os
import logging
from datetime import datetime
import inspect

# --- Cache để đảm bảo mỗi chức năng chỉ tạo 1 logger duy nhất ---
_LOGGER_CACHE = {}

def create_logger(name: str = None) -> logging.Logger:
    """
    Tạo logger duy nhất cho từng chức năng (login, search, register, profileupdate, ...).
    Dù gọi từ nhiều nơi (page/test) cũng chỉ sinh 1 file log duy nhất trong ngày.
    """
    global _LOGGER_CACHE

    # --- 1. Xác định tên module gọi (nếu không truyền) ---
    if not name:
        frame = inspect.stack()[1]
        caller_file = os.path.basename(frame.filename)
        base = os.path.splitext(caller_file)[0]
        name = base.replace("test_", "").replace("_page", "")
    else:
        name = name.lower().replace("test", "").replace("page", "").strip("_")

    func_name = name.lower()

    # --- 2. Nếu logger đã tồn tại, trả về luôn ---
    if func_name in _LOGGER_CACHE:
        return _LOGGER_CACHE[func_name]

    # --- 3. Tạo thư mục logs ---
    logs_dir = os.path.join(os.getcwd(), "reports", "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # --- 4. Tạo tên file log theo ngày ---
    timestamp = datetime.now().strftime("%Y%m%d")
    log_filename = f"mwc_{func_name}_{timestamp}.log"
    log_path = os.path.join(logs_dir, log_filename)

    # --- 5. Cấu hình logger ---
    logger = logging.getLogger(func_name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        console_handler = logging.StreamHandler()

        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%d/%m/%Y %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        # --- Header chung khi khởi tạo ---
        logger.info("=" * 60)
        logger.info(f"=== Logger khởi tạo cho chức năng: {func_name.upper()} ===")
        logger.info(f"Ghi log tại: {log_path}")
        logger.info("=" * 60)

    _LOGGER_CACHE[func_name] = logger
    return logger


# =====================================================================
# HÀM PHỤ: Tự động ghi loại dữ liệu (excel/csv/json) từ pytest option
# =====================================================================
def log_data_source_from_pytest(logger, pytestconfig):
    """
    Ghi tự động nguồn dữ liệu đầu vào (excel/csv/json)
    lấy từ tham số pytest: --data-mode
    """
    try:
        mode = pytestconfig.getoption("--data-mode") or "excel"
    except Exception:
        mode = "excel"

    mode = str(mode).strip().upper()
    logger.info("=" * 60)
    logger.info(f"Đang đọc dữ liệu test (mode={mode.lower()})...")
    logger.info("=" * 60)
    return mode
