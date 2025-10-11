from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver, timeout: int = 12):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # --- Common actions ---
    def open(self, url: str):
        self.driver.get(url)

    def find(self, locator):
        """Tìm phần tử (chờ tối đa timeout)."""
        return self.wait.until(EC.presence_of_element_located(locator))

    def click(self, locator):
        """Click phần tử."""
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator, text: str):
        """Nhập dữ liệu vào ô input."""
        el = self.find(locator)
        el.clear()
        el.send_keys(text)

    # --- HTML5 validation ---
    def get_validation_message(self, locator) -> str:
        """Trả về thông báo HTML5 validation (nếu có)."""
        try:
            el = self.find(locator)
            return (el.get_attribute("validationMessage") or "").strip()
        except Exception:
            return ""

    def value_missing(self, locator) -> bool:
        """Kiểm tra xem field có bị bỏ trống theo validity API không."""
        try:
            el = self.find(locator)
            return bool(self.driver.execute_script(
                "return arguments[0].validity ? arguments[0].validity.valueMissing : false;", el
            ))
        except Exception:
            return False
