import os, pytest
from datetime import datetime
from pages.register_page import MWCRegisterPage
from pages.profile_page import ProfilePage
from utils.excel_utils import load_sheet
from utils.logger_utils import create_logger

logger = create_logger("RegisterTest")

DATA_PATH = "data/TestData.xlsx"
SHEET = "Register"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SS_DIR = os.path.join(BASE_DIR, "reports", "screenshots")
os.makedirs(SS_DIR, exist_ok=True)

def rows():
    """Đọc dữ liệu từ Excel"""
    data = load_sheet(DATA_PATH, SHEET)
    return [
        pytest.param(
            r.get("testcase"), r.get("username", ""), r.get("phone", ""),
            r.get("password", ""), r.get("passwordconfirm", ""), r.get("expected", ""),
            id=str(r.get("testcase"))
        )
        for r in data if r.get("testcase")
    ]

@pytest.mark.parametrize("tc,username,phone,password,repass,expected_raw", rows())
def test_register_ddt(driver, result_writer, tc, username, phone, password, repass, expected_raw):
    """Kiểm thử chức năng Đăng ký tài khoản"""
    logger.info(f"\n=== Bắt đầu Testcase {tc} ===")
    logger.info(f"Dữ liệu: Username='{username}', Phone='{phone}', Expected='{expected_raw}'")

    page = MWCRegisterPage(driver)
    page.open()
    page.fill_form(username, phone, password, repass)
    page.click_register()

    actual, status = "", "FAIL"

    try:
        # --- 1 HTML5 VALIDATION ---
        html5_msgs = []
        for locator in [page.USERNAME, page.PHONE, page.PASSWORD, page.REPASS]:
            try:
                el = driver.find_element(*locator)
                msg = el.get_attribute("validationMessage") or ""
                if msg.strip():
                    html5_msgs.append(msg.strip())
            except Exception:
                pass

        if html5_msgs:
            actual = " | ".join(html5_msgs)
            logger.info(f"HTML5 validation: {actual}")
            status = "PASS" if "vui lòng điền" in actual.lower() else "FAIL"

        # --- 2 ALERT THÔNG BÁO LỖI ---
        elif not html5_msgs:
            alert_text = (page.get_alert_text() or "").strip().lower()
            if alert_text:
                actual = alert_text
                logger.info(f"Alert hiển thị: {alert_text}")
                if expected_raw.lower() in alert_text:
                    status = "PASS"
                else:
                    status = "FAIL"
            # --- 3 ĐĂNG KÝ THÀNH CÔNG ---
            elif page.at_home():
                profile = ProfilePage(driver)
                profile.open_profile()
                if profile.profile_username_present():
                    actual = profile.read_profile_username()
                    if username.lower() in (actual or "").lower():
                        status = "PASS"
                        logger.info("Đăng ký thành công, về trang profile.")
                    else:
                        actual = "Không có thông báo hiển thị."
                else:
                    actual = "Không có thông báo hiển thị."
            else:
                actual = "Không có thông báo hiển thị."
                status = "FAIL"

    except Exception as e:
        actual = f"Lỗi khi chạy testcase: {e}"
        logger.error(actual)

    finally:
        
        logger.info(f"Expected: {expected_raw}")
        logger.info(f"Actual:   {actual}")
        logger.info(f"Status:   {status}")
        logger.info(f"=== Kết thúc testcase {tc} ===\n")
        
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
        pytest.fail(
            f"Testcase {tc} thất bại.\nExpected: '{expected_raw}'\nActual: '{actual}'",
            pytrace=False
        )
