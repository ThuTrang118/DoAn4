import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from utils.logger_utils import create_logger
from pages.base_page import BasePage

logger = create_logger("ProfileUpdatePage")


class MWCProfileUpdatePage(BasePage):
    """Trang cập nhật thông tin cá nhân — MWC."""

    PROFILE_URL = "https://mwc.com.vn/profile"

    # --- Locators ---
    USERNAME = (By.ID, "UserName")
    FULLNAME = (By.ID, "FullName")
    EMAIL = (By.ID, "Email")
    PHONE = (By.ID, "Phone")

    GENDER_MALE = (By.XPATH, "(//div[@class='stardust-radio-button__outer-circle'])[1]")
    GENDER_FEMALE = (By.XPATH, "(//div[contains(@class,'stardust-radio-button')])[4]")
    GENDER_OTHER = (By.XPATH, "(//div[@class='stardust-radio-button__outer-circle'])[3]")

    DAY = (By.ID, "Day")
    MONTH = (By.ID, "Month")
    YEAR = (By.ID, "Year")

    PROVINCE = (By.ID, "provinceOptions")
    DISTRICT = (By.ID, "districtSelect")
    WARD = (By.ID, "wardSelect")
    ADDRESS = (By.ID, "Address")

    SAVE_BTN = (By.XPATH, "(//button[contains(text(),'Lưu')])[1]")
    ALERT = (By.XPATH, "//div[contains(@class,'alert') or contains(text(),'thành công')]")
    TOAST_SUCCESS = (By.CSS_SELECTOR, ".jq-toast-single.jq-icon-success")

    def __init__(self, driver, timeout=15):
        super().__init__(driver, timeout)

    def open(self):
        super().open(self.PROFILE_URL)
        logger.info("Mở trang hồ sơ cá nhân.")

    # ---------------------- FORM XỬ LÝ ----------------------
    def clear_field(self, locator):
        try:
            el = self.wait.until(EC.presence_of_element_located(locator))
            el.clear()
        except Exception:
            logger.warning(f"Không thể xóa {locator}")

    def safe_type(self, locator, value):
        try:
            el = self.wait.until(EC.presence_of_element_located(locator))
            el.clear()
            if value:
                el.send_keys(value)
                logger.info(f"Nhập vào {locator}: {value}")
        except Exception:
            logger.warning(f"Không thể nhập {locator}")

    def fill_profile(self, username, fullname, email, phone,
                     gender, day, month, year,
                     province, district, ward, address):
        """Điền form cập nhật thông tin cá nhân"""
        logger.info("Bắt đầu điền thông tin hồ sơ...")

        for loc in [self.USERNAME, self.FULLNAME, self.EMAIL, self.PHONE, self.ADDRESS]:
            self.clear_field(loc)

        self.safe_type(self.USERNAME, username)
        self.safe_type(self.FULLNAME, fullname)
        self.safe_type(self.EMAIL, email)
        self.safe_type(self.PHONE, phone)

        # Giới tính
        try:
            g = (gender or "").strip().lower()
            if g == "nam":
                self.click(self.GENDER_MALE)
            elif g == "nữ":
                self.click(self.GENDER_FEMALE)
            elif g == "khác":
                self.click(self.GENDER_OTHER)
            logger.info(f"Đã chọn giới tính: {gender}")
        except Exception:
            logger.warning("Không thể chọn giới tính.")

        # Ngày sinh
        try:
            if day:
                Select(self.driver.find_element(*self.DAY)).select_by_value(str(day))
            if month:
                Select(self.driver.find_element(*self.MONTH)).select_by_value(str(month))
            if year:
                Select(self.driver.find_element(*self.YEAR)).select_by_value(str(year))
            logger.info(f"Chọn ngày sinh: {day}-{month}-{year}")
        except Exception:
            logger.warning("Không thể chọn ngày/tháng/năm sinh.")

        # Địa chỉ (tăng ổn định)
        try:
            if province:
                WebDriverWait(self.driver, 15).until(
                    lambda d: len(Select(d.find_element(*self.PROVINCE)).options) > 1
                )
                Select(self.driver.find_element(*self.PROVINCE)).select_by_visible_text(province)
                logger.info(f"Đã chọn Tỉnh/TP: {province}")

            if district:
                WebDriverWait(self.driver, 15).until(
                    lambda d: len(Select(d.find_element(*self.DISTRICT)).options) > 1
                )
                Select(self.driver.find_element(*self.DISTRICT)).select_by_visible_text(district)
                logger.info(f"Đã chọn Quận/Huyện: {district}")

            if ward:
                WebDriverWait(self.driver, 15).until(
                    lambda d: len(Select(d.find_element(*self.WARD)).options) > 1
                )
                Select(self.driver.find_element(*self.WARD)).select_by_visible_text(ward)
                logger.info(f"Đã chọn Phường/Xã: {ward}")
        except Exception:
            logger.warning("Không chọn được địa chỉ hành chính (bỏ qua).")

        self.safe_type(self.ADDRESS, address)

    # ---------------------- HÀNH ĐỘNG ----------------------
    def click_save(self):
        try:
            self.click(self.SAVE_BTN)
            logger.info("Click nút Lưu thông tin.")
        except Exception:
            logger.warning("Không thể click nút Lưu.")

    def get_toast_message(self):
        """Bắt thông báo toast thành công (ổn định hơn)"""
        try:
            end_time = time.time() + 15
            while time.time() < end_time:
                elements = self.driver.find_elements(*self.TOAST_SUCCESS)
                for e in elements:
                    inner = (e.get_attribute("innerText") or "").lower()
                    if "cập nhập tài khoản thành công" in inner:
                        logger.info("Phát hiện toast thành công.")
                        return "Cập nhập tài khoản thành công!"
                time.sleep(0.5)
            return ""
        except Exception:
            return ""

    def get_alert_text(self):
        try:
            el = self.wait.until(EC.visibility_of_element_located(self.ALERT))
            msg = (el.text or "").strip()
            if msg:
                logger.info(f"Alert DOM: {msg}")
            return msg
        except Exception:
            return ""

    def get_html5_validation(self, locator):
        """Lấy thông báo HTML5 validation tiếng Việt hoặc Anh"""
        try:
            el = self.driver.find_element(*locator)
            msg = self.driver.execute_script("return arguments[0].validationMessage;", el) or ""
            msg = msg.strip().lower()
            if msg:
                logger.info(f"HTML5 validation: {msg}")
            if "@" in msg and "bao gồm" in msg:
                return "Vui lòng bao gồm '@' trong địa chỉ email."
            elif "vui lòng điền" in msg or "please fill" in msg:
                return "Vui lòng điền vào trường này."
            elif "email" in msg:
                return "Vui lòng nhập địa chỉ email hợp lệ."
            elif "số" in msg or "number" in msg:
                return "Vui lòng nhập số hợp lệ."
            return msg
        except Exception:
            return ""
