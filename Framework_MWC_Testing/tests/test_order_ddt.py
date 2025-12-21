import os
import pytest
from datetime import datetime
import allure

from pages.order_page import MWCOrderPage
from utils.excel_utils import load_data
from utils.logger_utils import create_logger, log_data_source_from_pytest

logger = create_logger("OrderTest")

@pytest.fixture(scope="session", autouse=True)
def _auto_log_data_source(pytestconfig):
    log_data_source_from_pytest(logger, pytestconfig)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHEET = "Order"

DATA_EXCEL = os.path.join(BASE_DIR, "data", "TestData.xlsx")
DATA_CSV = os.path.join(BASE_DIR, "data", "OrderData.csv")
DATA_JSON = os.path.join(BASE_DIR, "data", "OrderData.json")

def get_test_data(pytestconfig):
    mode = (pytestconfig.getoption("--data-mode") or "excel").lower()
    data_file = (pytestconfig.getoption("--data-file") or "").strip()

    if data_file:
        ext = os.path.splitext(data_file)[1].lower()
        if ext in [".xlsx", ".xls"]:
            return load_data(data_file, sheet_name=SHEET)
        return load_data(data_file)

    if mode == "excel":
        return load_data(DATA_EXCEL, sheet_name=SHEET)
    elif mode == "csv":
        return load_data(DATA_CSV)
    elif mode == "json":
        return load_data(DATA_JSON)
    else:
        raise ValueError("data-mode không hợp lệ")

def pytest_generate_tests(metafunc):
    needed = {
        "tc", "keyword", "color", "size",
        "fullname", "phone", "address",
        "province", "district", "ward", "expected_raw"
    }
    if needed.issubset(metafunc.fixturenames):
        data = get_test_data(metafunc.config)
        params = []
        seen = set()

        for r in data:
            tc = str(r.get("testcase", "")).strip()
            if tc and tc not in seen:
                params.append(pytest.param(
                    r.get("testcase", ""),
                    r.get("keyword", ""),
                    r.get("color", ""),
                    r.get("size", ""),
                    r.get("fullname", ""),
                    r.get("phone", ""),
                    r.get("address", ""),
                    r.get("province", ""),
                    r.get("district", ""),
                    r.get("ward", ""),
                    r.get("expected", ""),
                    id=tc,
                ))
                seen.add(tc)

        metafunc.parametrize(
            "tc,keyword,color,size,fullname,phone,address,province,district,ward,expected_raw",
            params,
        )

@allure.feature("Order")
@allure.story("Đặt hàng sản phẩm (Buy Now) - DDT")
def test_order_ddt(
    driver,
    result_writer,
    tc,
    keyword,
    color,
    size,
    fullname,
    phone,
    address,
    province,
    district,
    ward,
    expected_raw,
):
    logger.info(f"\n===== START ORDER {tc} =====")
    logger.info(
        f"Input | keyword='{keyword}', color='{color}', size='{size}', "
        f"fullname='{fullname}', phone='{phone}', address='{address}', "
        f"province='{province}', district='{district}', ward='{ward}', "
        f"expected='{expected_raw}'"
    )

    page = MWCOrderPage(driver)

    try:
        page.open()
        page.search_product(keyword)
        page.click_first_product()
        assert page.verify_product_page(), "Không vào đúng trang chi tiết sản phẩm."

        page.select_color_and_size(color, size)
        page.click_buy_now()
        page.verify_cart_info()

        page.fill_customer_info(fullname, phone, address, province, district, ward)
        page.click_order()

        success_msg = page.get_success_message()
        alert_msg = "" if success_msg else page.get_alert_message()

        if success_msg and "đặt hàng thành công" in success_msg.lower():
            actual = "Đặt hàng thành công!"
        elif alert_msg and "bạn chưa nhập thông tin nhận hàng" in alert_msg.lower():
            actual = "Bạn chưa nhập thông tin nhận hàng!"
        elif alert_msg:
            actual = alert_msg.strip()
        else:
            actual = "Không có thông báo hiển thị."

        expected_norm = (expected_raw or "").strip().lower()
        actual_norm = (actual or "").strip().lower()
        status = "PASS" if expected_norm and expected_norm in actual_norm else "FAIL"

    except Exception as e:
        actual = f"Lỗi testcase: {e}"
        status = "FAIL"
        logger.error(actual)

    result_writer.add_row(
        SHEET,
        {
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
            "Time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        },
    )

    if status == "FAIL":
        pytest.fail(f"Testcase {tc} thất bại.\nExpected: '{expected_raw}'\nActual: '{actual}'", pytrace=False)

    logger.info(f"Expected: {expected_raw}")
    logger.info(f"Actual:   {actual}")
    logger.info(f"Status:   {status}")
    logger.info(f"KẾT THÚC TESTCASE {tc}")
    logger.info("=" * 80 + "\n")
