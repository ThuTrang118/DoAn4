import os
import pytest
from datetime import datetime
from pages.register_page import MWCRegisterPage
from pages.profile_page import ProfilePage
from utils.excel_utils import load_data
from utils.logger_utils import create_logger, log_data_source_from_pytest

logger = create_logger("RegisterTest")

@pytest.fixture(scope="session", autouse=True)
def _auto_log_data_source(pytestconfig):
    log_data_source_from_pytest(logger, pytestconfig)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHEET = "Register"

DATA_EXCEL = os.path.join(BASE_DIR, "data", "TestData.xlsx")
DATA_CSV   = os.path.join(BASE_DIR, "data", "RegisterData.csv")
DATA_JSON  = os.path.join(BASE_DIR, "data", "RegisterData.json")

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
    if {"tc", "username", "phone", "password", "repass", "expected_raw"}.issubset(metafunc.fixturenames):
        data = get_test_data(metafunc.config)
        seen, params = set(), []
        for r in data:
            tc = str(r.get("testcase", "")).strip()
            if tc and tc not in seen:
                params.append(pytest.param(
                    r.get("testcase", ""),
                    r.get("username", ""),
                    r.get("phone", ""),
                    r.get("password", ""),
                    r.get("passwordconfirm", ""),
                    r.get("expected", ""),
                    id=tc
                ))
                seen.add(tc)
        metafunc.parametrize("tc,username,phone,password,repass,expected_raw", params)

def test_register_ddt(driver, result_writer, tc, username, phone, password, repass, expected_raw):
    logger.info(f"\n=== BẮT ĐẦU TESTCASE {tc} ===")
    logger.info(f"Input | Username='{username}' | Phone='{phone}' | Password='***' | Expected='{expected_raw}'")

    page = MWCRegisterPage(driver)
    page.open()
    page.fill_form(username, phone, password, repass)
    page.click_register()

    status, actual = "FAIL", ""
    try:
        html5_msgs = []
        for locator in [page.USERNAME, page.PHONE, page.PASSWORD, page.REPASS]:
            msg = page.get_validation_message(locator)
            if msg:
                html5_msgs.append(msg)

        if html5_msgs:
            actual = " | ".join(html5_msgs)
            if "vui lòng điền" in actual.lower() and "vui lòng điền" in (expected_raw or "").lower():
                status = "PASS"

        elif not html5_msgs:
            alert_text = (page.get_alert_text() or "").strip().lower()
            if alert_text:
                actual = alert_text
                if (expected_raw or "").lower() in alert_text:
                    status = "PASS"

        if status == "FAIL" and page.at_home():
            profile = ProfilePage(driver)
            profile.open_profile()
            if profile.profile_username_present():
                actual = profile.read_profile_username()
                if username.lower() in (actual or "").lower():
                    status = "PASS"
                else:
                    actual = f"Tên người dùng khác mong đợi: {actual}"
            else:
                actual = "Không hiển thị tên người dùng trong hồ sơ."

        if status == "FAIL" and not actual:
            actual = "Đăng ký không thành công."

    except Exception as e:
        actual = f"Lỗi khi chạy testcase: {e}"
        logger.error(actual)

    result_writer.add_row(SHEET, {
        "Testcase": tc,
        "Username": username,
        "Phone": phone,
        "Password": password,
        "PasswordConfirm": repass,
        "Expected": expected_raw,
        "Actual": actual,
        "Status": status,
        "Time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    })

    if status == "FAIL":
        pytest.fail(f"Testcase {tc} thất bại.\nExpected: '{expected_raw}'\nActual: '{actual}'", pytrace=False)

    logger.info(f"Expected: {expected_raw}")
    logger.info(f"Actual:   {actual}")
    logger.info(f"Status:   {status}")
    logger.info(f"KẾT THÚC TESTCASE {tc}")
    logger.info("=" * 80 + "\n")
