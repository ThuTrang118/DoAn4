# pages/login_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utils.logger_utils import create_logger

logger = create_logger("login_page")

class MWCLoginPage:
    """Trang đăng nhập MWC."""

    URL = "https://mwc.com.vn/login"
    HOME_URL = "https://mwc.com.vn/"

    # --- Locators ---
    USERNAME = (By.XPATH, "(//input[@id='UserName'])[1]")
    PASSWORD = (By.XPATH, "(//input[@id='Password'])[1]")
    LOGIN_BTN = (By.CSS_SELECTOR, "input[value='Đăng nhập']")
    ALERT_DANGER = (By.CSS_SELECTOR, ".alert.alert-danger")

    def __init__(self, driver, timeout: int = 12):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # ---------------- HÀNH ĐỘNG CHÍNH ----------------
    def open(self):
        """Mở trang đăng nhập."""
        try:
            self.driver.get(self.URL)
            logger.info("Mở trang đăng nhập MWC thành công.")
        except Exception as e:
            logger.error(f"Không thể mở trang login: {e}")

    def login(self, username: str, password: str):
        """Thực hiện đăng nhập."""
        logger.info(f"Đăng nhập với Username='{username}' | Password='{password}'")
        self.set_username(username)
        self.set_password(password)
        self.click_login()

    def set_username(self, val: str):
        """Nhập tên đăng nhập."""
        try:
            el = self.wait.until(EC.presence_of_element_located(self.USERNAME))
            el.clear()
            el.send_keys(val)
            logger.info(f"Nhập Username: {val}")
        except Exception as e:
            logger.error(f"Không thể nhập Username: {e}")

    def set_password(self, val: str):
        """Nhập mật khẩu."""
        try:
            el = self.wait.until(EC.presence_of_element_located(self.PASSWORD))
            el.clear()
            el.send_keys(val)
            logger.info("Nhập Password (đã ẩn).")
        except Exception as e:
            logger.error(f"Không thể nhập Password: {e}")

    def click_login(self):
        """Click nút đăng nhập."""
        try:
            self.wait.until(EC.element_to_be_clickable(self.LOGIN_BTN)).click()
            logger.info("Click nút 'Đăng nhập'.")
        except Exception as e:
            logger.error(f"Không thể click nút đăng nhập: {e}")

    # ---------------- KIỂM TRA / THÔNG BÁO ----------------
    def get_validation_message(self, locator) -> str:
        """Lấy thông báo HTML5 validationMessage."""
        try:
            el = self.driver.find_element(*locator)
            msg = (el.get_attribute("validationMessage") or "").strip()
            if msg:
                logger.info(f"HTML5 message: {msg}")
            return msg
        except Exception as e:
            logger.warning(f"[WARN] Không lấy được validationMessage: {e}")
            return ""

    def get_alert_text(self) -> str:
        """Lấy thông báo lỗi alert-danger."""
        try:
            alert = self.wait.until(EC.visibility_of_element_located(self.ALERT_DANGER))
            msg = alert.text.strip()
            logger.info(f"Alert hiển thị: {msg}")
            return msg
        except Exception:
            return ""

    def at_home(self) -> bool:
        """Kiểm tra đã về trang chủ chưa."""
        ok = self.driver.current_url.startswith(self.HOME_URL)
        logger.info(f"Trang chủ sau đăng nhập: {ok}")
        return ok
