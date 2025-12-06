import os
import pytest
from datetime import datetime

import allure

from pages.order_page import MWCOrderPage
from utils.excel_utils import load_data
from utils.logger_utils import create_logger, log_data_source_from_pytest

logger = create_logger("OrderTest")

# Ghi tự động loại dữ liệu đầu vào (giống file test_login_ddt)
@pytest.fixture(scope="session", autouse=True)
def _auto_log_data_source(pytestconfig):
    log_data_source_from_pytest(logger, pytestconfig)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHEET = "Order"

DATA_EXCEL = os.path.join(BASE_DIR, "data", "TestData.xlsx")
DATA_CSV = os.path.join(BASE_DIR, "data", "OrderData.csv")
DATA_JSON = os.path.join(BASE_DIR, "data", "OrderData.json")


# =======================
# Cho phép chọn dữ liệu đầu vào (giống login)
# =======================
def pytest_addoption(parser):
    parser.addoption("--data-mode", action="store", default="excel", help="excel | csv | json")


def get_test_data(data_mode: str):
    logger.info(f"Đọc dữ liệu ORDER (mode={data_mode})")
    if data_mode == "excel":
        return load_data(DATA_EXCEL, sheet_name=SHEET)
    elif data_mode == "csv":
        return load_data(DATA_CSV)
    elif data_mode == "json":
        return load_data(DATA_JSON)
    else:
        raise ValueError("data-mode không hợp lệ")


# =======================
# Data Driven
# =======================
def pytest_generate_tests(metafunc):
    needed = {
        "tc", "keyword", "color", "size",
        "fullname", "phone", "address",
        "province", "district", "ward", "expected_raw"
    }

    if needed.issubset(metafunc.fixturenames):
        mode = metafunc.config.getoption("--data-mode")
        data = get_test_data(mode)

        params = []
        seen = set()

        for r in data:
            tc = str(r.get("testcase", "")).strip()
            if tc and tc not in seen:
                params.append(
                    pytest.param(
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
                    )
                )
                seen.add(tc)

        metafunc.parametrize(
            "tc,keyword,color,size,fullname,phone,address,province,district,ward,expected_raw",
            params,
        )


# =======================
# Test ORDER
# =======================
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
        # 1. Mở trang
        page.open()

        # 2. Tìm kiếm sản phẩm
        page.search_product(keyword)

        # 3. Mở sản phẩm đầu tiên
        page.click_first_product()
        assert page.verify_product_page(), "Không vào đúng trang chi tiết sản phẩm."

        # 4. Chọn màu + size + Mua ngay
        page.select_color_and_size(color, size)
        page.click_buy_now()
        page.verify_cart_info()

        # 5–6. Nhập thông tin khách + chọn Tỉnh/Huyện/Xã
        page.fill_customer_info(fullname, phone, address, province, district, ward)

        # 7. Click Đặt hàng
        page.click_order()

        # 8. Lấy kết quả (thành công hoặc thông báo lỗi)
        success_msg = page.get_success_message()
        alert_msg = "" if success_msg else page.get_alert_message()

        # ===== ƯU TIÊN XÁC ĐỊNH KẾT QUẢ THỰC TẾ =====
        # ƯU TIÊN 1: Đặt hàng thành công (trang /cart/success, text "Đặt hàng thành công!")
        if success_msg and "đặt hàng thành công" in success_msg.lower():
            actual = "Đặt hàng thành công!"

        # ƯU TIÊN 2: Popup "Bạn chưa nhập thông tin nhận hàng!"
        elif alert_msg and "bạn chưa nhập thông tin nhận hàng" in alert_msg.lower():
            actual = "Bạn chưa nhập thông tin nhận hàng!"

        # Các lỗi khác: dùng nguyên nội dung alert
        elif alert_msg:
            actual = alert_msg.strip()

        # Không có gì hiển thị
        else:
            actual = "Không có thông báo hiển thị."

        # So sánh Expected vs Actual (chuẩn hóa giống login)
        expected_norm = (expected_raw or "").strip().lower()
        actual_norm = (actual or "").strip().lower()
        status = "PASS" if expected_norm and expected_norm in actual_norm else "FAIL"

    except Exception as e:
        actual = f"Lỗi testcase: {e}"
        status = "FAIL"
        logger.error(actual)

    # Ghi kết quả ra file (sheet Order) – format giống Login
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

    logger.info(f"ORDER {tc} | Expected='{expected_raw}' | Actual='{actual}' | Status={status}")
    logger.info("===== END ORDER %s =====\n", tc)

    if status == "FAIL":
        pytest.fail(
            f"TC {tc} FAIL\nExpected='{expected_raw}'\nActual='{actual}'",
            pytrace=False,
        )
