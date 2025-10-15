import pytest
from datetime import datetime
from pages.login_page import MWCLoginPage
from pages.profile_update_page import MWCProfileUpdatePage
from utils.excel_utils import load_sheet

DATA_PATH = "data/TestData.xlsx"
SHEET = "Profile"

def rows():
    data = load_sheet(DATA_PATH, SHEET)
    return [
        pytest.param(
            r.get("testcase"), r.get("username", ""), r.get("fullname", ""),
            r.get("email", ""), r.get("phone", ""), r.get("gender", ""),
            r.get("day", ""), r.get("month", ""), r.get("year", ""),
            r.get("province", ""), r.get("district", ""), r.get("ward", ""),
            r.get("address", ""), r.get("expected", ""),
            id=str(r.get("testcase"))
        )
        for r in data if r.get("testcase")
    ]


@pytest.mark.parametrize(
    "tc,username,fullname,email,phone,gender,day,month,year,province,district,ward,address,expected_raw", rows()
)
def test_profile_update(driver, result_writer, tc, username, fullname, email, phone,
                        gender, day, month, year, province, district, ward, address, expected_raw):
    """Kiểm thử cập nhật hồ sơ người dùng (tài khoản cố định Ánh Dương Phạm)."""

    login = MWCLoginPage(driver)
    login.open()
    login.login("Ánh Dương Phạm", "anhduong@123")
    assert login.at_home(), "Không đăng nhập được!"

    page = MWCProfileUpdatePage(driver)
    page.open()

    page.fill_profile(username, fullname, email, phone, gender, day, month, year, province, district, ward, address)
    try:
        page.click_save()
    except Exception:
        pass

    actual = ""
    status = "FAIL"

    # 1 Toast thành công
    toast_msg = page.get_toast_message()
    if toast_msg:
        actual = toast_msg

    # 2 HTML5 Validation
    if not actual:
        for locator in [page.FULLNAME, page.EMAIL, page.PHONE]:
            msg = page.get_html5_validation(locator)
            if msg:
                actual = msg
                break

    # 3 Alert nếu có
    if not actual:
        alert_msg = page.get_alert_text()
        if alert_msg:
            actual = alert_msg
        else:
            actual = "Không thấy thông báo sau khi lưu."

    # 4 So sánh Expected vs Actual 
    exp = (expected_raw or "").strip().lower()
    act = (actual or "").strip().lower()
    if exp and (exp in act or act in exp):
        status = "PASS"
    else:
        status = "FAIL"

    # 5 Ghi kết quả Excel 
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
        "Time": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })

    if status == "FAIL":
        pytest.fail(f"Testcase {tc} thất bại.\nExpected: '{expected_raw}'\nActual: '{actual}'", pytrace=False)
