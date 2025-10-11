import os
import pytest
from datetime import datetime
from pages.login_page import MWCLoginPage
from pages.profile_page import ProfilePage
from utils.excel_utils import load_sheet
from utils.expected import Exp, normalize_expected

DATA_PATH = "data/TestData.xlsx"
SHEET = "Login"
@pytest.mark.parametrize("tc,username,password,expected_raw,exp,exp_value", [
    pytest.param(
        r["testcase"],
        r.get("username", ""),
        r.get("password", ""),
        r.get("expected", ""),
        *normalize_expected(r.get("expected", ""), r.get("username", ""), r.get("password", "")),
        id=str(r["testcase"])
    )
    for r in load_sheet(DATA_PATH, SHEET) if r.get("testcase")
])
def test_login_ddt(driver, result_writer, tc, username, password, expected_raw, exp, exp_value):
    page = MWCLoginPage(driver)
    page.open()
    page.login(username, password)

    status, actual = "FAIL", ""

    try:
        # 1 HTML5 VALIDATION — form chưa gửi được
        html5_messages = []
        try:
            if not username:
                msg_u = page.get_validation_message(page.USERNAME)
                if msg_u:
                    html5_messages.append(msg_u)
            if not password:
                msg_p = page.get_validation_message(page.PASSWORD)
                if msg_p:
                    html5_messages.append(msg_p)
        except Exception:
            pass

        if html5_messages:
            actual = " | ".join(html5_messages)
            # Đánh giá theo expected
            if "vui lòng điền" in actual.lower() and "vui lòng điền" in expected_raw.lower():
                status = "PASS"
            else:
                status = "FAIL"
        # 2 ALERT LỖI ĐĂNG NHẬP SAI — chỉ kiểm tra nếu không có HTML5
        elif True:  # kiểm tra tiếp nếu không bị HTML5
            alert_text = (page.get_alert_text() or "").strip().lower()
            if alert_text:
                actual = alert_text
                if "tên đăng nhập hoặc mật khẩu không đúng" in alert_text:
                    if "tên đăng nhập hoặc mật khẩu không đúng" in expected_raw.lower():
                        status = "PASS"
                    else:
                        status = "FAIL"
                else:
                    # Nếu có alert khác
                    status = "FAIL"
            # 3 ĐĂNG NHẬP THÀNH CÔNG — chỉ kiểm tra khi không có alert
            elif page.at_home():
                profile = ProfilePage(driver)
                profile.open_profile()
                if profile.profile_username_present():
                    actual = profile.read_profile_username()
                    if username.lower() in (actual or "").lower():
                        status = "PASS"
                    else:
                        actual = f"Không tìm thấy thông báo."
                        status = "FAIL"
                else:
                    actual = "Không thấy #UserName trên trang Profile."
                    status = "FAIL"
            # 4 FALLBACK — nếu không rơi vào các trường hợp trên
            else:
                actual = "Đăng nhập không thành công"
                status = "FAIL"

    except Exception as e:
        actual = f"Lỗi khi chạy testcase: {e}"
        status = "FAIL"

    finally:
        # Ghi kết quả vào Excel
        result_writer.add_row(SHEET, {
            "Testcase": tc,
            "Username": username,
            "Password": password,
            "Expected": expected_raw,
            "Actual": actual,
            "Status": status,
            "Time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        })

    # Nếu FAIL thật → pytest fail để kích hoạt chụp ảnh trong conftest.py
    if status == "FAIL":
        pytest.fail(
            f"Testcase {tc} thất bại.\nExpected: '{expected_raw}'\nActual: '{actual}'",
            pytrace=False
        )
