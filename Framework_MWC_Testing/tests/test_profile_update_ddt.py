import os
import pytest
from datetime import datetime
from pages.login_page import MWCLoginPage
from pages.profile_update_page import MWCProfileUpdatePage
from utils.excel_utils import load_sheet
from utils.logger_utils import create_logger, log_data_source_from_pytest  # ✅ tự động log mode

# --- LOGGER ---
logger = create_logger("ProfileUpdateTest")

# Ghi loại dữ liệu đầu vào tự động (excel / csv / json)
@pytest.fixture(scope="session", autouse=True)
def _auto_log_data_source(pytestconfig):
    log_data_source_from_pytest(logger, pytestconfig)

# --- DATA ---
DATA_PATH = "data/TestData.xlsx"
SHEET = "Profile"

# --- SCREENSHOT DIR ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SS_DIR = os.path.join(BASE_DIR, "reports", "screenshots")
os.makedirs(SS_DIR, exist_ok=True)


# --- LOAD DỮ LIỆU TỪ EXCEL ---
def rows():
    data = load_sheet(DATA_PATH, SHEET)
    return [
        pytest.param(
            r.get("testcase"), r.get("username", ""), r.get("fullname", ""),
            r.get("email", ""), r.get("phone", ""), r.get("gender", ""),
            r.get("day", ""), r.get("month", ""), r.get("year", ""),
            r.get("province", ""), r.get("district", ""), r.get("ward", ""),
            r.get("address", ""), r.get("expected", ""),
            id=str(r.get("testcase")).strip()
        )
        for r in data if r.get("testcase")
    ]


# --- TESTCASE CHÍNH ---
@pytest.mark.parametrize(
    "tc,username,fullname,email,phone,gender,day,month,year,province,district,ward,address,expected_raw", rows()
)
def test_profile_update(driver, result_writer, tc, username, fullname, email, phone,
                        gender, day, month, year, province, district, ward, address, expected_raw):

    logger.info("=" * 80)
    logger.info(f"BẮT ĐẦU TESTCASE {tc}")
    logger.info(f"Input → Username='{username}', Email='{email}', Phone='{phone}', Expected='{expected_raw}'")

    # --- Đăng nhập bằng tài khoản cố định ---
    login = MWCLoginPage(driver)
    login.open()
    login.login("Ánh Dương Phạm", "anhduong@123")
    assert login.at_home(), "Không đăng nhập được!"
    logger.info("Đăng nhập thành công bằng tài khoản cố định.")

    # --- Mở trang hồ sơ cá nhân ---
    page = MWCProfileUpdatePage(driver)
    page.open()

    # --- Điền form & lưu ---
    page.fill_profile(username, fullname, email, phone, gender, day, month, year, province, district, ward, address)
    page.click_save()

    # --- BẮT ĐẦU XỬ LÝ KẾT QUẢ ---
    actual = ""
    status = "FAIL"

    try:
        # TOAST THÀNH CÔNG
        toast_msg = page.get_toast_message()
        if toast_msg:
            actual = toast_msg
            logger.info(f"Thông báo TOAST: {actual}")

        # HTML5 VALIDATION (Email, Phone, Fullname)
        if not actual:
            for locator in [page.FULLNAME, page.EMAIL, page.PHONE]:
                msg = page.get_html5_validation(locator)
                if msg:
                    actual = msg
                    logger.info(f"HTML5 validation: {actual}")
                    break

        # ALERT DOM (nếu có cảnh báo DOM)
        if not actual:
            alert_msg = page.get_alert_text()
            if alert_msg:
                actual = alert_msg
                logger.info(f"Thông báo ALERT: {actual}")
            else:
                actual = "Không thấy thông báo sau khi lưu."
                logger.warning(actual)

        # SO SÁNH EXPECTED - ACTUAL
        exp = (expected_raw or "").strip().lower()
        act = (actual or "").strip().lower()

        if exp and (exp in act or act in exp):
            status = "PASS"
        else:
            status = "FAIL"

    except Exception as e:
        actual = f"Lỗi khi chạy testcase: {e}"
        logger.error(actual)
        status = "FAIL"

    # --- GHI KẾT QUẢ RA EXCEL ---
    result_writer.add_row(SHEET, {
        "Testcase": tc,
        "Username": username,
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
        "Time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    })

    # --- GHI LOG CUỐI ---
    logger.info(f"Expected: {expected_raw}")
    logger.info(f"Actual:   {actual}")
    logger.info(f"Status:   {status}")

    # --- NẾU FAIL → CHỤP ẢNH ---
    if status == "FAIL":
        ss_path = os.path.join(SS_DIR, f"profile_update_{tc}.png")
        try:
            driver.save_screenshot(ss_path)
            logger.error(f"Đã chụp ảnh lỗi: {ss_path}")
        except Exception as e:
            logger.error(f"Không thể chụp ảnh lỗi: {e}")

        pytest.fail(
            f"Testcase {tc} thất bại.\nExpected: '{expected_raw}'\nActual: '{actual}'",
            pytrace=False
        )

    logger.info(f"KẾT THÚC TESTCASE {tc}")
    logger.info("=" * 80 + "\n")
