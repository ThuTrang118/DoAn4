import os
import pytest
from datetime import datetime
from pages.login_page import MWCLoginPage
from pages.profile_page import ProfilePage
from utils.excel_utils import load_data
from utils.logger_utils import create_logger, log_data_source_from_pytest  

logger = create_logger("LoginTest")

# Ghi tự động loại dữ liệu đầu vào
@pytest.fixture(scope="session", autouse=True)
def _auto_log_data_source(pytestconfig):
    log_data_source_from_pytest(logger, pytestconfig)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHEET = "Login"

DATA_EXCEL = os.path.join(BASE_DIR, "data", "TestData.xlsx")
DATA_CSV   = os.path.join(BASE_DIR, "data", "LoginData.csv")
DATA_JSON  = os.path.join(BASE_DIR, "data", "LoginData.json")

def pytest_addoption(parser):
    parser.addoption("--data-mode", action="store", default="excel", help="excel | csv | json")

def get_test_data(data_mode: str):
    if data_mode == "excel":
        return load_data(DATA_EXCEL, sheet_name=SHEET)
    elif data_mode == "csv":
        return load_data(DATA_CSV)
    elif data_mode == "json":
        return load_data(DATA_JSON)
    else:
        raise ValueError("data-mode không hợp lệ")

def pytest_generate_tests(metafunc):
    if {"tc", "username", "password", "expected_raw"}.issubset(metafunc.fixturenames):
        mode = metafunc.config.getoption("--data-mode")
        data = get_test_data(mode)
        seen, params = set(), []
        for r in data:
            tc = str(r.get("testcase", "")).strip()
            if tc and tc not in seen:
                params.append(pytest.param(
                    r.get("testcase", ""),
                    r.get("username", ""),
                    r.get("password", ""),
                    r.get("expected", ""),
                    id=tc
                ))
                seen.add(tc)
        metafunc.parametrize("tc,username,password,expected_raw", params)

def test_login_ddt(driver, result_writer, tc, username, password, expected_raw):
    logger.info(f"\n=== BẮT ĐẦU TESTCASE {tc} ===")
    page = MWCLoginPage(driver)
    page.open()
    page.clear_input(page.USERNAME)
    page.clear_input(page.PASSWORD)
    page.login(username, password)

    status, actual = "FAIL", ""
    try:
        html5_msgs = []
        for locator in [page.USERNAME, page.PASSWORD]:
            msg = page.get_validation_message(locator)
            if msg:
                html5_msgs.append(msg)
        if html5_msgs:
            actual = " | ".join(html5_msgs)
            if "vui lòng điền" in actual.lower() and "vui lòng điền" in expected_raw.lower():
                status = "PASS"
        elif not html5_msgs:
            alert_text = (page.get_alert_text() or "").strip()
            if alert_text:
                actual = alert_text
                if "Tên đăng nhập hoặc mật khẩu không đúng" in alert_text.lower() and \
                   "Tên đăng nhập hoặc mật khẩu không đúng" in expected_raw.lower():
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
            actual = "Đăng nhập không thành công."
    except Exception as e:
        actual = f"Lỗi khi chạy testcase: {e}"
        logger.error(actual)
    result_writer.add_row(SHEET, {
        "Testcase": tc, "Username": username, "Password": password,
        "Expected": expected_raw, "Actual": actual, "Status": status,
        "Time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    })
    if status == "FAIL":
        pytest.fail(f"Testcase {tc} thất bại.\nExpected: '{expected_raw}'\nActual: '{actual}'", pytrace=False)
