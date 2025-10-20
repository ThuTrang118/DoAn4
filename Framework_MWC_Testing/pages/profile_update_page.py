import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.logger_utils import create_logger

logger = create_logger("ProfileUpdatePage")


class MWCProfileUpdatePage:
    """Trang cập nhật thông tin cá nhân — MWC."""

    PROFILE_URL = "https://mwc.com.vn/profile"

    # --- Locator ---
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
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # ------------------ HÀM CHÍNH ------------------
    def open(self):
        self.driver.get(self.PROFILE_URL)
        logger.info("Mở trang hồ sơ cá nhân.")

    def clear_text_field(self, locator):
        """Xóa nội dung trong text field."""
        try:
            el = self.wait.until(EC.presence_of_element_located(locator))
            if el.is_enabled() and el.get_attribute("readonly") not in ("true", "readonly"):
                el.clear()
        except Exception:
            logger.warning(f"Không thể clear {locator} (bỏ qua).")

    def safe_type(self, locator, value):
        """Nhập dữ liệu an toàn — luôn clear trước khi nhập."""
        try:
            el = self.wait.until(EC.presence_of_element_located(locator))
            if el.is_enabled() and el.get_attribute("readonly") not in ("true", "readonly"):
                el.clear()
                if value:
                    el.send_keys(value)
                    logger.info(f"Nhập vào {locator}: {value}")
            else:
                logger.info(f"Field {locator} bị khóa, bỏ qua.")
        except Exception:
            logger.warning(f"Không thể nhập {locator} (bỏ qua).")

    def reset_address_dropdowns(self):
        """Reset dropdown địa chỉ về mặc định (None)."""
        try:
            for loc in [self.PROVINCE, self.DISTRICT, self.WARD]:
                el = self.driver.find_element(*loc)
                Select(el).select_by_index(0)
            logger.info("Đã reset 3 dropdown địa chỉ.")
        except Exception:
            pass

    def fill_profile(self, username, fullname, email, phone,
                     gender, day, month, year,
                     province, district, ward, address):
        """Điền toàn bộ thông tin cá nhân."""
        logger.info("Bắt đầu điền form hồ sơ người dùng.")

        # Xóa dữ liệu cũ
        for field in [self.USERNAME, self.FULLNAME, self.EMAIL, self.PHONE, self.ADDRESS]:
            self.clear_text_field(field)
        self.reset_address_dropdowns()

        # Nhập dữ liệu
        self.safe_type(self.USERNAME, username)
        self.safe_type(self.FULLNAME, fullname)
        self.safe_type(self.EMAIL, email)
        self.safe_type(self.PHONE, phone)

        # Giới tính
        try:
            gender = (gender or "").strip().lower()
            if gender == "nam":
                self.driver.find_element(*self.GENDER_MALE).click()
            elif gender == "nữ":
                self.driver.find_element(*self.GENDER_FEMALE).click()
            elif gender == "khác":
                self.driver.find_element(*self.GENDER_OTHER).click()
            logger.info(f"Đã chọn giới tính: {gender}")
        except Exception:
            logger.warning("Không chọn được giới tính (bỏ qua).")

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
            logger.warning("Không chọn được ngày/tháng/năm sinh (bỏ qua).")

        # Địa chỉ
        try:
            if province:
                WebDriverWait(self.driver, 10).until(
                    lambda d: len(Select(d.find_element(*self.PROVINCE)).options) > 1
                )
                Select(self.driver.find_element(*self.PROVINCE)).select_by_visible_text(province)
                logger.info(f"Đã chọn Tỉnh/TP: {province}")
                time.sleep(1.2)

            if district:
                WebDriverWait(self.driver, 10).until(
                    lambda d: len(Select(d.find_element(*self.DISTRICT)).options) > 1
                )
                Select(self.driver.find_element(*self.DISTRICT)).select_by_visible_text(district)
                logger.info(f"Đã chọn Quận/Huyện: {district}")
                time.sleep(1.2)

            if ward:
                WebDriverWait(self.driver, 10).until(
                    lambda d: len(Select(d.find_element(*self.WARD)).options) > 1
                )
                Select(self.driver.find_element(*self.WARD)).select_by_visible_text(ward)
                logger.info(f"Đã chọn Phường/Xã: {ward}")
        except Exception:
            logger.warning("Không chọn được địa chỉ hành chính (bỏ qua).")

        # Địa chỉ cụ thể
        self.safe_type(self.ADDRESS, address)

    def click_save(self):
        try:
            self.wait.until(EC.element_to_be_clickable(self.SAVE_BTN)).click()
            logger.info("Click nút Lưu thông tin.")
        except Exception:
            logger.warning("Không thể click nút Lưu (bỏ qua).")

    def get_toast_message(self):
        """Bắt thông báo 'Cập nhập tài khoản thành công!'"""
        try:
            end_time = time.time() + 10
            while time.time() < end_time:
                elements = self.driver.find_elements(*self.TOAST_SUCCESS)
                for e in elements:
                    inner = (e.get_attribute("innerText") or "").lower()
                    if "cập nhập tài khoản thành công" in inner:
                        logger.info("Phát hiện thông báo toast thành công.")
                        return "Cập nhập tài khoản thành công!"
                time.sleep(0.3)
            return ""
        except Exception:
            logger.warning("Không bắt được toast message.")
            return ""

    def get_alert_text(self):
        try:
            alert = self.wait.until(EC.visibility_of_element_located(self.ALERT))
            msg = (alert.text or "").strip()
            if msg:
                logger.info(f"Alert DOM: {msg}")
            return msg
        except Exception:
            return ""

    def get_html5_validation(self, locator):
        """Lấy thông báo HTML5 tiếng Việt (ổn định, qua JS)."""
        try:
            el = self.driver.find_element(*locator)
            msg = self.driver.execute_script("return arguments[0].validationMessage;", el) or ""
            msg = msg.strip().lower()
            if msg:
                logger.info(f"HTML5 validation: {msg}")
            if "@" in msg and "bao gồm" in msg:
                return "Vui lòng bao gồm '@' trong địa chỉ email."
            elif "vui lòng điền" in msg:
                return "Vui lòng điền vào trường này."
            elif "email" in msg:
                return "Vui lòng nhập địa chỉ email hợp lệ."
            elif "số" in msg or "number" in msg:
                return "Vui lòng nhập số hợp lệ."
            return msg
        except Exception:
            return ""
