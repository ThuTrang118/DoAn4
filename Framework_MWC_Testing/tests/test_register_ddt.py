import os
import pytest
from datetime import datetime
from pages.register_page import MWCRegisterPage
from pages.profile_page import ProfilePage
from utils.excel_utils import load_sheet

DATA_PATH = "data/TestData.xlsx"
SHEET = "Register"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SS_DIR = os.path.join(BASE_DIR, "reports", "screenshots")
os.makedirs(SS_DIR, exist_ok=True)


def rows():
    """Đọc dữ liệu từ Excel."""
    data = load_sheet(DATA_PATH, SHEET)
    return [
        pytest.param(
            r.get("testcase"),
            r.get("username", ""),
            r.get("phone", ""),
            r.get("password", ""),
            r.get("passwordconfirm", ""),
            r.get("expected", ""),
            id=str(r.get("testcase"))
        )
        for r in data if r.get("testcase")
    ]


@pytest.mark.parametrize("tc,username,phone,password,repass,expected_raw", rows())
def test_register_ddt(driver, result_writer, tc, username, phone, password, repass, expected_raw):
    page = MWCRegisterPage(driver)
    page.open()
    page.fill_form(username, phone, password, repass)
    page.click_register()

    actual, status = "", "FAIL"

    try:
        # 1 HTML5 VALIDATION — nếu có, form chưa submit
        html5_messages = []
        for locator in [page.USERNAME, page.PHONE, page.PASSWORD, page.REPASS]:
            try:
                el = driver.find_element(*locator)
                msg = (el.get_attribute("validationMessage") or "").strip()
                if msg:
                    html5_messages.append(msg)
            except Exception:
                continue

        if html5_messages:
            actual = " | ".join(html5_messages)
            if "vui lòng điền" in actual.lower() and "vui lòng điền" in expected_raw.lower():
                status = "PASS"
            else:
                status = "FAIL"
        # 2 ALERT THÔNG BÁO LỖI — nếu không có HTML5
        elif True:  # chỉ kiểm tra khi không có HTML5
            alert_text = (page.get_alert_text() or "").strip().lower()
            if alert_text:
                actual = alert_text
                possible_errors = [
                    "số điện thoại không đúng định dạng",
                    "mật khẩu không giống nhau",
                    "mật khẩu phải lớn hơn 8 ký tự",
                    "tài khoản đã tồn tại trong hệ thống",
                ]
                if expected_raw.lower() in alert_text:
                    status = "PASS"
                elif any(err in alert_text for err in possible_errors):
                    status = "FAIL"
                else:
                    actual = f"Thông báo không khớp mong đợi ({alert_text})"
                    status = "FAIL"
            # 3 THÀNH CÔNG — nếu không alert & không HTML5
            elif page.at_home():
                profile = ProfilePage(driver)
                profile.open_profile()
                if profile.profile_username_present():
                    actual = profile.read_profile_username()
                    if username.lower() in (actual or "").lower():
                        status = "PASS"
                    else:
                        actual = f"Không có thông báo"
                        status = "FAIL"
                else:
                    actual = "Không có thông báo"
                    status = "FAIL"
            # 4 FALLBACK — nếu không rơi vào TH nào
            else:
                actual = "Đăng ký tài khoản không thành công"
                status = "FAIL"

    except Exception as e:
        actual = f"Lỗi khi chạy testcase: {e}"
        status = "FAIL"

    finally:
        # Ghi kết quả ra Excel
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

    # Nếu FAIL thì fail thật để chụp ảnh màn hình
    if status == "FAIL":
        pytest.fail(
            f"Testcase {tc} thất bại.\nExpected: '{expected_raw}'\nActual: '{actual}'",
            pytrace=False
        )
