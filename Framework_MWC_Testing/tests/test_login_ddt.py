# tests/test_login_ddt.py
import pytest
from datetime import datetime
from pages.login_page import MWCLoginPage
from pages.profile_page import ProfilePage
from utils.excel_utils import load_sheet
from utils.expected import Exp, normalize_expected

DATA_PATH = "data/TestData.xlsx"
SHEET = "Login" 

def rows():
    data = load_sheet(DATA_PATH, SHEET)
    out = []
    for r in data:
        tc = r.get("testcase")
        if not tc:
            continue
        u = r.get("username", "")
        p = r.get("password", "")
        expected_raw = r.get("expected", "")   # giữ nguyên
        exp_type, exp_value = normalize_expected(expected_raw, u, p)
        out.append(pytest.param(tc, u, p, expected_raw, exp_type, exp_value, id=str(tc)))
    return out

@pytest.mark.parametrize("tc,username,password,expected_raw,exp,exp_value", rows())
def test_login_ddt(driver, result_writer, tc, username, password, expected_raw, exp: Exp, exp_value: str):
    page = MWCLoginPage(driver)
    page.open()

    if username: page.set_username(username)
    if password: page.set_password(password)
    page.click_login()

    status = "FAIL"
    actual = ""

    try:
        if exp is Exp.SUCCESS:
            assert page.at_home(), "Không chuyển về trang chủ sau khi đăng nhập thành công."
            profile = ProfilePage(driver)
            profile.open_profile()
            assert profile.profile_username_present(), "Không thấy #UserName trên trang Profile."
            actual = profile.read_profile_username()
            if exp_value:
                assert exp_value.lower() in (actual or "").lower(), \
                    f"Tên hiển thị không khớp. Expect~ '{exp_value}', actual~ '{actual}'"
            status = "PASS"

        elif exp in {Exp.REQ_USER, Exp.REQ_PASS, Exp.REQ_BOTH}:
            need_user = exp in {Exp.REQ_USER, Exp.REQ_BOTH}
            need_pass = exp in {Exp.REQ_PASS, Exp.REQ_BOTH}
            ok = True
            if need_user: ok = ok and page.username_value_missing()
            if need_pass: ok = ok and page.password_value_missing()
            actual = page.get_username_validation() or page.get_password_validation()
            assert ok, f"Expected required; u='{page.get_username_validation()}', p='{page.get_password_validation()}'"
            status = "PASS"

        elif exp is Exp.INVALID:
            actual = page.get_alert_text()
            assert "Tên đăng nhập hoặc mật khẩu không đúng!" in actual, \
                f"Expect 'Tên đăng nhập hoặc mật khẩu không đúng!', got '{actual}'"
            status = "PASS"

        else:
            pytest.skip(f"Unknown expectation: {exp}")

    finally:
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        result_writer.add_row(SHEET, {
            "Testcase": tc,
            "Username": username,
            "Password": password,
            "Expected": expected_raw,     
            "Actual": actual,
            "Status": status,
            "Time": timestamp             
        })
