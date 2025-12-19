import os
import pytest
from datetime import datetime
import unicodedata

from pages.login_page import MWCLoginPage
from pages.profile_update_page import MWCProfileUpdatePage
from utils.excel_utils import load_data
from utils.logger_utils import create_logger, log_data_source_from_pytest

# =========================================================
# LOGGER
# =========================================================
logger = create_logger("ProfileUpdateTest")

@pytest.fixture(scope="session", autouse=True)
def _auto_log_data_source(pytestconfig):
    log_data_source_from_pytest(logger, pytestconfig)

# =========================================================
# DATA CONFIG (GIỐNG LOGIN / REGISTER)
# =========================================================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHEET = "Profile"

DATA_EXCEL = os.path.join(BASE_DIR, "data", "TestData.xlsx")
DATA_CSV   = os.path.join(BASE_DIR, "data", "ProfileData.csv")
DATA_JSON  = os.path.join(BASE_DIR, "data", "ProfileData.json")

SS_DIR = os.path.join(BASE_DIR, "reports", "screenshots")
os.makedirs(SS_DIR, exist_ok=True)

# =========================================================
# PYTEST OPTION (GIỐNG LOGIN / REGISTER)
# =========================================================
def pytest_addoption(parser):
    parser.addoption(
        "--data-mode",
        action="store",
        default="excel",
        help="Chọn loại dữ liệu: excel | csv | json"
    )

# =========================================================
# LOAD DATA THEO MODE (GIỐNG LOGIN / REGISTER)
# =========================================================
def get_test_data(mode: str):
    mode = (mode or "excel").lower()

    if mode == "excel":
        return load_data(DATA_EXCEL, sheet_name=SHEET)
    elif mode == "csv":
        return load_data(DATA_CSV)
    elif mode == "json":
        return load_data(DATA_JSON)
    else:
        raise ValueError(f"data-mode không hợp lệ: {mode}")

# =========================================================
# DDT GENERATOR (GIỐNG LOGIN / REGISTER)
# =========================================================
def pytest_generate_tests(metafunc):
    required = {
        "tc", "fullname", "email", "phone", "gender",
        "day", "month", "year",
        "province", "district", "ward", "address",
        "expected_raw"
    }

    if not required.issubset(metafunc.fixturenames):
        return

    mode = metafunc.config.getoption("--data-mode")
    data = get_test_data(mode)

    params = []
    seen = set()

    for r in data:
        tc = str(r.get("testcase", "")).strip()
        if not tc or tc in seen:
            continue

        params.append(pytest.param(
            tc,
            r.get("fullname", ""),
            r.get("email", ""),
            r.get("phone", ""),
            r.get("gender", ""),
            r.get("day", ""),
            r.get("month", ""),
            r.get("year", ""),
            r.get("province", ""),
            r.get("district", ""),
            r.get("ward", ""),
            r.get("address", ""),
            r.get("expected", ""),
            id=tc
        ))
        seen.add(tc)

    metafunc.parametrize(
        "tc,fullname,email,phone,gender,day,month,year,"
        "province,district,ward,address,expected_raw",
        params
    )

# =========================================================
# TESTCASE
# =========================================================
def test_profile_update(
    driver, result_writer,
    tc, fullname, email, phone, gender,
    day, month, year,
    province, district, ward, address,
    expected_raw
):
    logger.info("=" * 80)
    logger.info(f"BẮT ĐẦU TESTCASE {tc}")
    logger.info(f"Input → Email='{email}', Phone='{phone}', Expected='{expected_raw}'")

    # --- RESET SESSION ---
    try:
        driver.delete_all_cookies()
        driver.execute_script("window.localStorage && window.localStorage.clear();")
        driver.execute_script("window.sessionStorage && window.sessionStorage.clear();")
    except Exception:
        pass

    # --- LOGIN ---
    login = MWCLoginPage(driver)
    login.open()
    login.login("Ánh Dương Phạm", "anhduong@123")
    assert login.at_home(), "Không đăng nhập được!"
    logger.info("Đăng nhập thành công.")

    # --- PROFILE UPDATE ---
    page = MWCProfileUpdatePage(driver)
    page.open()
    page.fill_profile(
        fullname, email, phone,
        gender, day, month, year,
        province, district, ward, address
    )
    page.click_save()

    actual = ""
    status = "FAIL"

    def normalize(s):
        return unicodedata.normalize("NFD", (s or "").lower()) \
            .encode("ascii", "ignore").decode("utf-8")

    exp_norm = normalize(expected_raw)
    expect_success = ("thanh cong" in exp_norm) or ("success" in exp_norm)

    try:
        # 1. TOAST / ALERT
        toast_msg = page.get_toast_message()
        if toast_msg:
            actual = toast_msg

        if not actual:
            alert_msg = page.get_alert_text()
            if alert_msg:
                actual = alert_msg

        # 2. VALIDATION (CASE FAIL)
        if not actual and not expect_success:
            invalid_msg = page.get_first_invalid_validation()
            if invalid_msg:
                actual = invalid_msg

        # 3. VERIFY PERSIST (CASE SUCCESS)
        if not actual and expect_success:
            page.open()
            persisted = {
                "fullname": page.get_value(page.FULLNAME),
                "email": page.get_value(page.EMAIL),
                "phone": page.get_value(page.PHONE),
                "address": page.get_value(page.ADDRESS),
            }

            def ok(inp, got):
                if not inp:
                    return True
                return normalize(inp) in normalize(got)

            if (
                ok(fullname, persisted["fullname"]) and
                ok(email, persisted["email"]) and
                ok(phone, persisted["phone"]) and
                ok(address, persisted["address"])
            ):
                actual = "Cập nhập tài khoản thành công!"
            else:
                actual = f"Dữ liệu không lưu sau reload: {persisted}"

        if not actual:
            actual = "Không thấy thông báo sau khi lưu."

        if exp_norm and (exp_norm in normalize(actual) or normalize(actual) in exp_norm):
            status = "PASS"

    except Exception as e:
        actual = f"Lỗi khi chạy testcase: {e}"

    # --- GHI RESULT ---
    result_writer.add_row(SHEET, {
        "Testcase": tc,
        "FullName": fullname,
        "Email": email,
        "Phone": phone,
        "Gender": gender,
        "Day": day,
        "Month": month,
        "Year": year,
        "Province": province,
        "District": district,
        "Ward": ward,
        "Address": address,
        "Expected": expected_raw,
        "Actual": actual,
        "Status": status,
        "Time": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })

    if status == "FAIL":
        pytest.fail(f"Testcase {tc} thất bại.\nExpected: '{expected_raw}'\nActual: '{actual}'", pytrace=False)
        
    logger.info(f"Expected: {expected_raw}")
    logger.info(f"Actual:   {actual}")
    logger.info(f"Status:   {status}")

    logger.info(f"KẾT THÚC TESTCASE {tc}")
    logger.info("=" * 80 + "\n")
