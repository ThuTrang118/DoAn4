from selenium.webdriver.common.by import By
from pages.base_page import BasePage

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

    def fill_form(self, username, phone, password, repass):
        if username: self.type(self.USERNAME, username)
        if phone: self.type(self.PHONE, phone)
        if password: self.type(self.PASSWORD, password)
        if repass: self.type(self.REPASS, repass)

    def click_register(self):
        self.click(self.REGISTER_BTN)

    def get_alert_text(self) -> str:
        """Gom toàn bộ thông báo lỗi alert-danger."""
        try:
            alerts = self.driver.find_elements(*self.ALERT_DANGER)
            texts = [a.text.strip() for a in alerts if a.text.strip()]
            return " | ".join(dict.fromkeys(texts))  # loại trùng, giữ thứ tự
        except Exception:
            return ""

    def at_home(self) -> bool:
        return self.driver.current_url.startswith(self.HOME_URL)
