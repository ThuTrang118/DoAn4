import os
import pytest
from datetime import datetime
from pages.search_page import MWCSearchPage
from utils.excel_utils import load_data
from utils.logger_utils import create_logger
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
    """Kiểm thử tự động chức năng Tìm kiếm sản phẩm."""
    logger.info(f"\n=== BẮT ĐẦU TESTCASE {tc} ===")
    logger.info(f"Input | Keyword='{keyword}' | Expected='{expected_raw}'")

    page = MWCSearchPage(driver)
    page.open()
    page.search(keyword)

    status, actual = "FAIL", ""
    try:
        # --- Kiểm tra kết quả tìm kiếm ---
        found, message = page.check_keyword(keyword)
        actual = message.strip()

        # --- Đánh giá kết quả ---
        expected_low = expected_raw.lower().strip()
        actual_low = actual.lower().strip()

        if found and keyword.lower() in actual_low:
            status = "PASS"
        elif not found and "không tìm thấy" in expected_low and "không tìm thấy" in actual_low:
            status = "PASS"
        elif not keyword and ("vui lòng nhập" in expected_low or "trống" in expected_low):
            actual = "Từ khóa trống"
            status = "PASS"
        else:
            status = "FAIL"

        if not actual:
            actual = "Không tìm thấy kết quả phù hợp."

    except Exception as e:
        actual = f"Lỗi khi chạy testcase: {e}"
        logger.error(actual)

    # --- Ghi kết quả ra Excel ---
    result_writer.add_row(SHEET, {
        "Testcase": tc,
        "Keyword": keyword,
        "Expected": expected_raw,
        "Actual": actual,
        "Status": status,
        "Time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    })

    if status == "FAIL":
        pytest.fail(f"Testcase {tc} thất bại.\nKeyword: '{keyword}'\nExpected: '{expected_raw}'\nActual: '{actual}'",pytrace=False)
