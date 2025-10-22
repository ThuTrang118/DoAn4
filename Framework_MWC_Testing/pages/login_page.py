from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger_utils import create_logger

logger = create_logger("LoginPage")

class MWCLoginPage:
    """Trang Đăng nhập MWC."""

    URL = "https://mwc.com.vn/login"
    HOME_URL = "https://mwc.com.vn/"
    USERNAME = (By.XPATH, "(//input[@id='UserName'])[1]")
    PASSWORD = (By.XPATH, "(//input[@id='Password'])[1]")
    LOGIN_BTN = (By.CSS_SELECTOR, "input[value='Đăng nhập']")
    ALERT = (By.XPATH, "//div[contains(@class,'alert') or contains(text(),'mật khẩu không đúng')]")

    def __init__(self, driver, timeout: int = 12):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self):
        self.driver.get(self.URL)
        logger.info("Mở trang đăng nhập MWC thành công.")

    def clear_input(self, locator):
        """Xóa nội dung trong ô input."""
        try:
            el = self.wait.until(EC.presence_of_element_located(locator))
            el.clear()
            logger.info(f"Đã xóa dữ liệu cũ trong {locator}.")
        except Exception as e:
            logger.warning(f"Không thể xóa nội dung: {e}")

    def login(self, username, password):
        """Thực hiện đăng nhập (đã dọn sạch input)."""
        logger.info("Bắt đầu thao tác đăng nhập...")

        user_el = self.wait.until(EC.presence_of_element_located(self.USERNAME))
        user_el.send_keys(username)
        logger.info(f"Nhập Username: {username}")

        pass_el = self.wait.until(EC.presence_of_element_located(self.PASSWORD))
        pass_el.send_keys(password)
        logger.info("Nhập Password (đã ẩn).")

        self.wait.until(EC.element_to_be_clickable(self.LOGIN_BTN)).click()
        logger.info("Click nút 'Đăng nhập'.")

    def get_alert_text(self):
        """Lấy nội dung alert (nếu có)."""
        try:
            el = self.wait.until(EC.visibility_of_element_located(self.ALERT))
            return el.text.strip()
        except Exception:
            return ""

    def at_home(self):
        """Kiểm tra đã về trang chủ chưa."""
        return self.driver.current_url.startswith(self.HOME_URL)

    def get_validation_message(self, locator):
        """Lấy thông báo HTML5 validation."""
        try:
            el = self.driver.find_element(*locator)
            return (el.get_attribute("validationMessage") or "").strip()
        except Exception:
            return ""