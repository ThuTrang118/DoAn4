import os, pytest
from datetime import datetime
from pages.order_page import MWCOrderPage
from utils.excel_utils import load_sheet

DATA_PATH = "data/TestData.xlsx"
SHEET = "Order"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SS_DIR = os.path.join(BASE_DIR, "reports", "screenshots")
os.makedirs(SS_DIR, exist_ok=True)


def rows():
    """Đọc dữ liệu từ Excel."""
    data = load_sheet(DATA_PATH, SHEET)
    return [
        pytest.param(
            r.get("testcase"), r.get("keyword", ""), r.get("color", ""), r.get("size", ""),
            r.get("fullname", ""), r.get("phone", ""), r.get("address", ""),
            r.get("province", ""), r.get("district", ""), r.get("ward", ""),
            r.get("expected", ""), id=str(r.get("testcase"))
        )
        for r in data if r.get("testcase")
    ]


@pytest.mark.parametrize(
    "tc,keyword,color,size,fullname,phone,address,province,district,ward,expected_raw",
    rows()
)
def test_order_product(driver, result_writer, tc, keyword, color, size, fullname, phone,
                       address, province, district, ward, expected_raw):
    """Kiểm thử chức năng Đặt hàng (Buy Now)."""

    page = MWCOrderPage(driver)
    page.open_home()
    page.search_product(keyword)
    page.click_first_product()

    assert page.verify_product_page(), "Không mở đúng trang sản phẩm."

    page.select_color_and_size(color, size)
    page.click_buy_now()
    page.verify_cart_info()
    page.fill_customer_info(fullname, phone, address, province, district, ward)
    page.click_order()

    # --- Lấy kết quả ---
    actual = page.get_success_message() or page.get_alert_message()
    status = "PASS" if expected_raw.lower().strip() in actual.lower().strip() else "FAIL"

    # --- Ghi file Excel đầy đủ dữ liệu ---
    result_writer.add_row(SHEET, {
        "Testcase": tc,
        "Keyword": keyword,
        "Color": color,
        "Size": size,
        "FullName": fullname,
        "Phone": phone,
        "Address": address,
        "Province": province,
        "District": district,
        "Ward": ward,
        "Expected": expected_raw,
        "Actual": actual,
        "Status": status,
        "Time": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })

    if status == "FAIL":
        pytest.fail(
            f"Testcase {tc} thất bại.\nExpected: '{expected_raw}'\nActual: '{actual}'",
            pytrace=False
        )
