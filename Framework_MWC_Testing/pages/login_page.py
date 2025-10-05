# pages/login_page.py
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

    def set_username(self, username: str):
        el = self.wait.until(EC.presence_of_element_located(self.USERNAME))
        el.clear(); el.send_keys(username)

    def set_password(self, password: str):
        el = self.wait.until(EC.presence_of_element_located(self.PASSWORD))
        el.clear(); el.send_keys(password)

    def click_login(self):
        self.wait.until(EC.element_to_be_clickable(self.LOGIN_BTN)).click()

    # --- required checks (ngôn ngữ-agnostic) ---
    def _value_missing(self, locator) -> bool:
        el = self.driver.find_element(*locator)
        try:
            return bool(self.driver.execute_script(
                "return arguments[0].validity ? arguments[0].validity.valueMissing : false;", el
            ))
        except Exception:
            required = el.get_attribute("required")
            value = el.get_attribute("value") or ""
            return (required is not None) and (value.strip() == "")

    def username_value_missing(self) -> bool:
        return self._value_missing(self.USERNAME)

    def password_value_missing(self) -> bool:
        return self._value_missing(self.PASSWORD)
    # -------------------------------------------

    def get_username_validation(self) -> str:
        el = self.driver.find_element(*self.USERNAME)
        return (el.get_attribute("validationMessage") or "").strip()

    def get_password_validation(self) -> str:
        el = self.driver.find_element(*self.PASSWORD)
        return (el.get_attribute("validationMessage") or "").strip()

    def get_alert_text(self) -> str:
        try:
            alert = self.wait.until(EC.visibility_of_element_located(self.ALERT_DANGER))
            return alert.text.strip()
        except Exception:
            return ""

    def at_home(self) -> bool:
        return self.driver.current_url.startswith(self.HOME_URL)
