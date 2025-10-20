import os, pytest
from datetime import datetime
from pages.login_page import MWCLoginPage
from pages.profile_page import ProfilePage
from utils.excel_utils import load_sheet
from utils.logger_utils import create_logger

# --- Cấu hình logger ---
logger = create_logger("LoginTest")

# --- Dữ liệu đầu vào ---
DATA_PATH = "data/TestData.xlsx"
SHEET = "Login"

# --- Thư mục lưu ảnh ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SS_DIR = os.path.join(BASE_DIR, "reports", "screenshots")
os.makedirs(SS_DIR, exist_ok=True)

# --- Đọc dữ liệu từ Excel ---
def rows():
    """Đọc dữ liệu test từ sheet Login (lọc trùng testcase nếu có)."""
    data = load_sheet(DATA_PATH, SHEET)
    seen, rows_ = set(), []
    for r in data:
        tc = str(r.get("testcase", "")).strip()
        if tc and tc not in seen:
            rows_.append(r)
            seen.add(tc)
    return [
        pytest.param(
            r.get("testcase"),
            r.get("username", ""),
            r.get("password", ""),
            r.get("expected", ""),
            id=str(r.get("testcase"))
        )
        for r in rows_
    ]

# --- Test chính ---
@pytest.mark.parametrize("tc,username,password,expected_raw", rows())
def test_login_ddt(driver, result_writer, tc, username, password, expected_raw):
    """Kiểm thử chức năng Đăng nhập MWC."""
    logger.info(f"\n=== Bắt đầu Testcase {tc} ===")
    logger.info(f"Input | Username='{username}' | Password='{password}' | Expected='{expected_raw}'")

    page = MWCLoginPage(driver)
    page.open()
    page.login(username, password)

    status, actual = "FAIL", ""

    try:
        # --- 1 HTML5 VALIDATION ---
        html5_msgs = []
        for locator in [page.USERNAME, page.PASSWORD]:
            msg = page.get_validation_message(locator)
            if msg:
                html5_msgs.append(msg)

        if html5_msgs:
            actual = " | ".join(html5_msgs)
            if "vui lòng điền" in actual.lower() and "vui lòng điền" in expected_raw.lower():
                status = "PASS"

        # --- 2 ALERT LỖI ĐĂNG NHẬP SAI ---
        if not html5_msgs:
            alert_text = (page.get_alert_text() or "").strip()
            if alert_text:
                actual = alert_text
                if "tên đăng nhập hoặc mật khẩu không đúng" in alert_text.lower() and \
                   "tên đăng nhập hoặc mật khẩu không đúng" in expected_raw.lower():
                    status = "PASS"

        # --- 3 ĐĂNG NHẬP THÀNH CÔNG ---
        if not html5_msgs and not actual:
            if page.at_home():
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
            else:
                actual = "Không chuyển hướng về trang chủ sau đăng nhập."

    except Exception as e:
        actual = f"Lỗi khi chạy testcase: {e}"
        logger.error(actual)

    # --- Ghi log ---
    logger.info(f"Expected: {expected_raw}")
    logger.info(f"Actual:   {actual}")
    logger.info(f"Status:   {status}")
    logger.info(f"=== Kết thúc testcase {tc} ===")

    # --- Ghi kết quả Excel ---
    result_writer.add_row(SHEET, {
        "Testcase": tc,
        "Username": username,
        "Password": password,
        "Expected": expected_raw,
        "Actual": actual,
        "Status": status,
        "Time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    })

    # --- Thông báo Fail để kích hoạt screenshot ---
    if status == "FAIL":
        pytest.fail(
            f"Testcase {tc} thất bại.\nExpected: '{expected_raw}'\nActual: '{actual}'",
            pytrace=False
        )
