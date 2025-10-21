import os
import pytest
from datetime import datetime
from pages.register_page import MWCRegisterPage
from pages.profile_page import ProfilePage
from utils.excel_utils import load_data
from utils.logger_utils import create_logger

logger = create_logger("RegisterTest")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHEET = "Register"

# --- Đường dẫn dữ liệu ---
DATA_EXCEL = os.path.join(BASE_DIR, "data", "TestData.xlsx")
DATA_CSV   = os.path.join(BASE_DIR, "data", "RegisterData.csv")
DATA_JSON  = os.path.join(BASE_DIR, "data", "RegisterData.json")


# --- Lấy dữ liệu theo mode từ conftest.py ---
def get_test_data(data_mode: str):
    """Đọc dữ liệu test từ Excel / CSV / JSON."""
    logger.info(f"Đang đọc dữ liệu test ({data_mode})...")
    if data_mode == "excel":
        return load_data(DATA_EXCEL, sheet_name=SHEET)
    elif data_mode == "csv":
        return load_data(DATA_CSV)
    elif data_mode == "json":
        return load_data(DATA_JSON)
    else:
        raise ValueError("data-mode không hợp lệ (excel | csv | json)")


# --- Tự động truyền dữ liệu test ---
def pytest_generate_tests(metafunc):
    """Lấy --data-mode từ conftest.py và truyền dữ liệu vào test."""
    if {"tc", "username", "phone", "password", "repass", "expected_raw"}.issubset(metafunc.fixturenames):
        mode = metafunc.config.getoption("--data-mode")
        data = get_test_data(mode)
        params = [
            pytest.param(
                r.get("testcase", ""),
                r.get("username", ""),
                r.get("phone", ""),
                r.get("password", ""),
                r.get("passwordconfirm", ""),
                r.get("expected", ""),
                id=str(r.get("testcase"))
            )
            for r in data if r.get("testcase")
        ]
        metafunc.parametrize("tc,username,phone,password,repass,expected_raw", params)


# --- HÀM TEST CHÍNH ---
def test_register_ddt(driver, result_writer, tc, username, phone, password, repass, expected_raw):
    logger.info(f"\n=== BẮT ĐẦU TESTCASE {tc} ===")

    page = MWCRegisterPage(driver)
    page.open()
    page.fill_form(username, phone, password, repass)
    page.click_register()

    # --- Lấy thông tin thực tế ---
    actual = ""
    html5_msgs = [page.get_validation_message(x) for x in [page.USERNAME, page.PHONE, page.PASSWORD, page.REPASS] if page.get_validation_message(x)]
    alert_text = page.get_alert_text().strip().lower()
    success = page.at_home()

    # --- Ưu tiên 1: HTML5 validation ---
    if html5_msgs:
        actual = " | ".join(html5_msgs)
        logger.info(f"HTML5 validation: {actual}")
        assert "vui lòng điền" in actual.lower(), f"Expected HTML5 validation nhưng nhận được: {actual}"

    # --- Ưu tiên 2: Alert lỗi ---
    elif alert_text:
        actual = alert_text
        logger.info(f"Alert hiển thị: {actual}")
        assert expected_raw.lower() in alert_text, f"Expected: {expected_raw}, Actual: {actual}"

    # --- Ưu tiên 3: Thành công (về trang chủ) ---
    elif success:
        profile = ProfilePage(driver)
        profile.open_profile()
        assert profile.profile_username_present(), "Không tìm thấy tên người dùng trong hồ sơ."
        actual = profile.read_profile_username()
        assert username.lower() in (actual or "").lower(), f"Tên người dùng khác mong đợi: {actual}"

    # --- Nếu không thuộc các trường hợp trên ---
    else:
        actual = "Đăng ký không thành công."
        pytest.fail(f"Không xác định được kết quả. Expected: {expected_raw}, Actual: {actual}")

    # --- Ghi kết quả ra Excel ---
    result_writer.add_row(SHEET, {
        "Testcase": tc,
        "Username": username,
        "Phone": phone,
        "Password": password,
        "PasswordConfirm": repass,
        "Expected": expected_raw,
        "Actual": actual,
        "Status": "PASS",
        "Time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    })

    logger.info(f"TESTCASE {tc} HOÀN THÀNH THÀNH CÔNG.\n")
