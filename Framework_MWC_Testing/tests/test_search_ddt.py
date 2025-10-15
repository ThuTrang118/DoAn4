# tests/test_search_ddt.py
import os, pytest
from datetime import datetime
from pages.search_page import MWCSearchPage
from utils.excel_utils import load_sheet

DATA_PATH = "data/TestData.xlsx"
SHEET = "Search"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SS_DIR = os.path.join(BASE_DIR, "reports", "screenshots")
os.makedirs(SS_DIR, exist_ok=True)


def rows():
    """Đọc dữ liệu từ Excel sheet Search (có cột Expected)."""
    data = load_sheet(DATA_PATH, SHEET)
    return [
        pytest.param(
            r.get("testcase"),
            r.get("keyword", ""),
            r.get("expected", ""),
            id=str(r.get("testcase"))
        )
        for r in data if r.get("testcase")
    ]


@pytest.mark.parametrize("tc,keyword,expected_raw", rows())
def test_search_ddt(driver, result_writer, tc, keyword, expected_raw):
    """Kiểm thử tự động chức năng Tìm kiếm sản phẩm (ưu tiên XPath, ghi Actual rõ)."""
    page = MWCSearchPage(driver)
    page.open()
    page.search(keyword)

    status, actual = "FAIL", ""

    try:
        # Kiểm tra sản phẩm
        found, message = page.check_keyword(keyword)
        actual = message.strip()

        # --- Quy tắc đánh giá kết quả ---
        expected_low = expected_raw.lower().strip()
        actual_low = actual.lower().strip()

        if found:
            # ✅ Tìm thấy sản phẩm có chứa từ khóa
            status = "PASS"
        elif not found and "không tìm thấy" in actual_low and "không tìm thấy" in expected_low:
            # ✅ Không tìm thấy sản phẩm – đúng như mong đợi
            status = "PASS"
        else:
            # ❌ Không đúng kỳ vọng
            status = "FAIL"

    finally:
        # 🧾 Ghi kết quả Excel
        result_writer.add_row(SHEET, {
            "Testcase": tc,
            "Keyword": keyword,
            "Expected": expected_raw,
            "Actual": actual,
            "Status": status,
            "Time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        })

    # 🔥 Nếu FAIL thật → Pytest fail để kích hoạt chụp ảnh (conftest.py)
    if status == "FAIL":
        pytest.fail(
            f"❌ Testcase {tc} thất bại.\nKeyword: '{keyword}'\nExpected: '{expected_raw}'\nActual: '{actual}'",
            pytrace=False
        )
