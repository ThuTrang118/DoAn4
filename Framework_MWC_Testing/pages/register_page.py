from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger_utils import create_logger

logger = create_logger("RegisterPage")

class MWCRegisterPage(BasePage):
    URL = "https://mwc.com.vn/login"
    HOME_URL = "https://mwc.com.vn/"

    USERNAME = (By.XPATH, "(//input[@id='UserName'])[2]")
    PHONE = (By.XPATH, "(//input[@id='Phone'])[1]")
    PASSWORD = (By.XPATH, "(//input[@id='Password'])[2]")
    REPASS = (By.XPATH, "(//input[@id='PasswordConfirm'])[1]")
    REGISTER_BTN = (By.CSS_SELECTOR, "input[value='Đăng ký']")
    ALERT_DANGER = (By.XPATH, "//div[@class='alert alert-danger']")

    def open(self):
        self.driver.get(self.URL)
        logger.info("Mở trang đăng ký tài khoản MWC.")

    def fill_form(self, username, phone, password, repass):
        """Điền form đăng ký"""
        logger.info(f"Điền thông tin: Username='{username}', Phone='{phone}', Password='***', RePass='***'")
        if username: self.type(self.USERNAME, username)
        if phone: self.type(self.PHONE, phone)
        if password: self.type(self.PASSWORD, password)
        if repass: self.type(self.REPASS, repass)

    def click_register(self):
        """Click nút Đăng ký"""
        self.click(self.REGISTER_BTN)
        logger.info("Click nút 'Đăng ký'.")

    def get_alert_text(self) -> str:
        """Gom toàn bộ thông báo lỗi alert-danger."""
        try:
            alerts = self.driver.find_elements(*self.ALERT_DANGER)
            texts = [a.text.strip() for a in alerts if a.text.strip()]
            combined = " | ".join(dict.fromkeys(texts))
            if combined:
                logger.info(f"Thông báo lỗi hiển thị: {combined}")
            return combined
        except Exception as e:
            logger.warning(f"Lỗi khi lấy alert: {e}")
            return ""

    def at_home(self) -> bool:
        ok = self.driver.current_url.startswith(self.HOME_URL)
        logger.info(f"Kiểm tra về trang chủ sau đăng ký: {ok}")
        return ok
