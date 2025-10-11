from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class MWCLoginPage:
    URL = "https://mwc.com.vn/login"
    HOME_URL = "https://mwc.com.vn/"

    USERNAME = (By.ID, "UserName")
    PASSWORD = (By.ID, "Password")
    LOGIN_BTN = (By.CSS_SELECTOR, "input[value='Đăng nhập']")
    ALERT_DANGER = (By.CSS_SELECTOR, ".alert.alert-danger")

    def __init__(self, driver, timeout: int = 12):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self):
        self.driver.get(self.URL)

    def login(self, username: str, password: str):
        self.set_username(username)
        self.set_password(password)
        self.click_login()

    def set_username(self, val: str):
        el = self.wait.until(EC.presence_of_element_located(self.USERNAME))
        el.clear(); el.send_keys(val)

    def set_password(self, val: str):
        el = self.wait.until(EC.presence_of_element_located(self.PASSWORD))
        el.clear(); el.send_keys(val)

    def click_login(self):
        self.wait.until(EC.element_to_be_clickable(self.LOGIN_BTN)).click()

    def get_validation_message(self, locator) -> str:
        """Trả về thông báo HTML5 validationMessage."""
        try:
            el = self.driver.find_element(*locator)
            return (el.get_attribute("validationMessage") or "").strip()
        except Exception:
            return ""

    def get_alert_text(self) -> str:
        try:
            alert = self.wait.until(EC.visibility_of_element_located(self.ALERT_DANGER))
            return alert.text.strip()
        except Exception:
            return ""

    def at_home(self) -> bool:
        return self.driver.current_url.startswith(self.HOME_URL)
