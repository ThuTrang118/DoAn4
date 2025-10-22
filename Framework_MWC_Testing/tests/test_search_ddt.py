import os
import pytest
from datetime import datetime
from pages.search_page import MWCSearchPage
from utils.excel_utils import load_data
from utils.logger_utils import create_logger, log_data_source_from_pytest
import allure

logger = create_logger("SearchTest")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHEET = "Search"

DATA_EXCEL = os.path.join(BASE_DIR, "data", "TestData.xlsx")
DATA_CSV   = os.path.join(BASE_DIR, "data", "SearchData.csv")
DATA_JSON  = os.path.join(BASE_DIR, "data", "SearchData.json")

# --- TỰ THIẾT LẬP THƯ MỤC ALLURE (nếu .bat không có --alluredir) ---
@pytest.fixture(scope="session", autouse=True)
def _auto_allure_dir(pytestconfig):
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    default_dir = os.path.join(base, "reports", "allure-results", "search")
    # Nếu người dùng không truyền --alluredir, pytestconfig.option sẽ không có thuộc tính này
    if not getattr(pytestconfig.option, "allure_report_dir", None) and not getattr(pytestconfig.option, "allure_results_dir", None):
        os.makedirs(default_dir, exist_ok=True)
        pytestconfig.option.allure_report_dir = default_dir
        pytestconfig.option.allure_results_dir = default_dir
        print(f"[INFO] Đã tự tạo Allure results folder: {default_dir}")
    yield

# --- Cho phép chọn loại dữ liệu đầu vào ---
def pytest_addoption(parser):
    parser.addoption("--data-mode", action="store", default="excel", help="excel | csv | json")
    parser.addoption("--data-file", action="store", default=DATA_EXCEL, help="Đường dẫn file dữ liệu test")

def get_test_data(data_mode: str):
    """Đọc dữ liệu test theo loại file."""
    logger.info(f"Đang đọc dữ liệu test (mode={data_mode})...")
    if data_mode == "excel":
        return load_data(DATA_EXCEL, sheet_name=SHEET)
    elif data_mode == "csv":
        return load_data(DATA_CSV)
    elif data_mode == "json":
        return load_data(DATA_JSON)
    else:
        raise ValueError("data-mode không hợp lệ")

def pytest_generate_tests(metafunc):
    """Sinh dữ liệu test tự động (Data-Driven)."""
    if {"tc", "keyword", "expected_raw"}.issubset(metafunc.fixturenames):
        mode = metafunc.config.getoption("--data-mode")
        data = get_test_data(mode)
        seen, params = set(), []
        for r in data:
            tc = str(r.get("testcase", "")).strip()
            if tc and tc not in seen:
                params.append(pytest.param(
                    r.get("testcase", ""),
                    r.get("keyword", ""),
                    r.get("expected", ""),
                    id=tc
                ))
                seen.add(tc)
        metafunc.parametrize("tc,keyword,expected_raw", params)


# --- HÀM TEST CHÍNH ---
def test_search_ddt(driver, result_writer, tc, keyword, expected_raw):
    """Kiểm thử tự động chức năng Tìm kiếm sản phẩm (bỏ dấu, chỉ cần chứa từ khóa là PASS)."""
    logger.info(f"\n=== BẮT ĐẦU TESTCASE {tc} ===")
    logger.info(f"Input | Keyword='{keyword}' | Expected='{expected_raw}'")

    page = MWCSearchPage(driver)
    page.open()
    page.search(keyword)

    status, actual = "FAIL", ""
    try:
        # --- Lấy tên sản phẩm đầu tiên ---
        first_name = (page.get_first_result_text() or "").strip()
        actual = first_name if first_name else "Không tìm thấy sản phẩm"

        # --- Chuẩn hóa để so sánh KHÔNG DẤU ---
        keyword_norm  = page.normalize_text(keyword)
        actual_norm   = page.normalize_text(first_name)
        expected_norm = page.normalize_text(expected_raw)

        # --- Đánh giá kết quả ---
        if not keyword:  # từ khóa trống
            if "vui long nhap" in expected_norm or "trong" in expected_norm:
                actual = "Từ khóa trống"
                status = "PASS"
            else:
                status = "FAIL"

        elif not first_name:  # không có sản phẩm hiển thị
            if "khong tim thay" in expected_norm:
                status = "PASS"
            else:
                status = "FAIL"

        else:
            # chỉ cần từ khóa nằm TRONG tên sản phẩm đầu tiên (bỏ dấu)
            if keyword_norm in actual_norm:
                status = "PASS"
            else:
                logger.warning(f"Không tìm thấy sản phẩm nào chứa từ khóa '{keyword}'.")
                actual = "Không tìm thấy sản phẩm"
                status = "PASS" if "khong tim thay" in expected_norm else "FAIL"

        # --- Ghi lại Expected / Actual / Status ---
        logger.info(f"Expected: {expected_raw}")
        logger.info(f"Actual:   {actual}")
        logger.info(f"Status:   {status}")

    except Exception as e:
        actual = f"Lỗi khi chạy testcase: {e}"
        logger.error(actual)
        status = "FAIL"

    # --- Ghi kết quả ra Excel ---
    result_writer.add_row(SHEET, {
        "Testcase": tc,
        "Keyword": keyword,
        "Expected": expected_raw,
        "Actual": actual,
        "Status": status,
        "Time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    })

    logger.info(f"=== KẾT THÚC TESTCASE {tc} ===")

    # --- Nếu thất bại thì fail pytest ---
    if status == "FAIL":
        pytest.fail(
            f"Testcase {tc} thất bại.\n"
            f"Keyword: '{keyword}'\n"
            f"Expected: '{expected_raw}'\n"
            f"Actual: '{actual}'",
            pytrace=False
        )
