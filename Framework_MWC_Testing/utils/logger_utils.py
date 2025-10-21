import os
import logging
from datetime import datetime
import inspect

# Lưu cache logger để tránh tạo nhiều file
_LOGGER_CACHE = {}

def create_logger(name: str = None) -> logging.Logger:
    """
    Tạo logger duy nhất cho mỗi chức năng (login, search, order,...).
    Dù gọi ở nhiều nơi (page/test) cũng chỉ sinh 1 file log duy nhất.
    """
    global _LOGGER_CACHE

    # --- 1. Xác định tên module gọi ---
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

    # --- 4. Tên file log ---
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

        logger.info(f"=== Logger khởi tạo cho chức năng: {func_name.upper()} ===")
        logger.info(f"Ghi log tại: {log_path}")

    _LOGGER_CACHE[func_name] = logger
    return logger

# HÀM PHỤ: GHI NGUỒN DỮ LIỆU ĐẦU VÀO TRƯỚC MỖI TESTCASE
def log_data_source(logger: logging.Logger, data_mode: str):
    """
    Ghi dòng thông tin nguồn dữ liệu đầu vào (Excel / CSV / JSON)
    vào đầu mỗi testcase để dễ theo dõi log.
    """
    mode = str(data_mode).strip().upper()
    logger.info("=" * 60)
    logger.info(f"Nguồn dữ liệu đầu vào: {mode}")
    logger.info("=" * 60)
