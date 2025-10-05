from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver, timeout: int = 12):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def open(self, url: str):
        self.driver.get(url)

    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator, text: str):
        el = self.find(locator)
        el.clear()
        el.send_keys(text)
        return el

    def validation_message(self, locator) -> str:
        el = self.find(locator)
        return (el.get_attribute("validationMessage") or "").strip()

    def value_missing(self, locator) -> bool:
        """Check required-field theo HTML5 Validity API (không phụ thuộc ngôn ngữ)."""
        el = self.find(locator)
        try:
            return bool(self.driver.execute_script(
                "return arguments[0].validity ? arguments[0].validity.valueMissing : false;", el
            ))
        except Exception:
            # fallback
            required = el.get_attribute("required")
            value = el.get_attribute("value") or ""
            return (required is not None) and (value.strip() == "")
