# pages/profile_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ProfilePage:
    """Điều hướng tới trang profile và đọc #UserName."""

    ACCOUNT_ICON = (By.CSS_SELECTOR,
        "div[class='no-padding col-xs-12 hidden-sm hidden-xs col-md-1 right-cus d-none d-lg-block'] a[class='account-handle-icon']"
    )
    PROFILE_USERNAME = (By.CSS_SELECTOR, "#UserName")

    def __init__(self, driver, timeout: int = 12):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open_profile(self):
        self.wait.until(EC.element_to_be_clickable(self.ACCOUNT_ICON)).click()
        self.wait.until(EC.presence_of_element_located(self.PROFILE_USERNAME))

    def profile_username_present(self) -> bool:
        try:
            self.wait.until(EC.presence_of_element_located(self.PROFILE_USERNAME))
            return True
        except Exception:
            return False

    def read_profile_username(self) -> str:
        el = self.driver.find_element(*self.PROFILE_USERNAME)
        return (el.get_attribute("value") or el.text or "").strip()
