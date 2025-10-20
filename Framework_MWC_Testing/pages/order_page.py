from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time


class MWCOrderPage:
    HOME_URL = "https://mwc.com.vn/"

    # --- B1–B3: Tìm kiếm và mở sản phẩm ---
    SEARCH_BOX = (By.XPATH, "(//input[@placeholder='Tìm kiếm'])[1]")
    FIRST_PRODUCT = (By.XPATH, "(//a[@class='product-grid-info pl-id-3893'])[1]")
    PRODUCT_TITLE = (By.XPATH, "(//h1[contains(text(),'Giày Cao Gót MWC 4444')])[1]")

    # --- B4–B5: Màu và size ---
    COLOR_SILVER = (By.ID, "bac")
    COLOR_BLACK = (By.ID, "den")
    SIZE_IDS = ["35", "36", "37", "38", "39"]

    # --- B6: Button mua ngay ---
    BTN_BUY_NOW = (By.ID, "btnBuyNow")

    # --- B7: Giỏ hàng ---
    CART_PRODUCT_NAME = (By.XPATH, "(//a[contains(text(),'Giày Cao Gót MWC 4444')])[1]")
    CART_PRODUCT_OPTIONS = (By.XPATH, "(//div[@class='cart-item-body-item-product-options-name d-none d-lg-block'])[1]")

    # --- B8–B9: Form nhận hàng ---
    FULLNAME = (By.ID, "FullName")
    PHONE = (By.ID, "Phone")
    ADDRESS = (By.ID, "Address")
    PROVINCE = (By.XPATH, "(//select[@id='provinceOptions'])[1]")
    DISTRICT = (By.XPATH, "(//select[@id='districtSelect'])[1]")
    WARD = (By.XPATH, "(//select[@id='wardSelect'])[1]")

    # --- B10: Đặt hàng ---
    BTN_ORDER = (By.ID, "btnDatHang")

    # --- Thông báo kết quả ---
    ALERT_ERROR = (By.ID, "swal2-html-container")
    SUCCESS_TEXT = (By.XPATH, "(//h1[contains(text(),'Đặt hàng thành công!')])[1]")

    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # ------------------ B1–B3 ------------------
    def open_home(self):
        self.driver.get(self.HOME_URL)

    def search_product(self, keyword):
        box = self.wait.until(EC.presence_of_element_located(self.SEARCH_BOX))
        box.clear()
        box.send_keys(keyword)
        box.submit()
        time.sleep(2)

    def click_first_product(self):
        el = self.wait.until(EC.element_to_be_clickable(self.FIRST_PRODUCT))
        el.click()
        print("[INFO] Đã click sản phẩm đầu tiên trong kết quả tìm kiếm.")

    def verify_product_page(self):
        try:
            title_el = self.wait.until(EC.visibility_of_element_located(self.PRODUCT_TITLE))
            return "Giày Cao Gót MWC 4444" in (title_el.text or "")
        except:
            return False

    # ------------------ B4–B6 ------------------
    def select_color_and_size(self, color, size):
        try:
            if color.lower() == "bạc":
                self.driver.find_element(*self.COLOR_SILVER).click()
            elif color.lower() == "đen":
                self.driver.find_element(*self.COLOR_BLACK).click()
            time.sleep(0.3)
            if str(size) in self.SIZE_IDS:
                self.driver.find_element(By.ID, str(size)).click()
        except Exception as e:
            print(f"[WARN] Không chọn được màu/size: {e}")

    def click_buy_now(self):
        try:
            btn = self.wait.until(EC.element_to_be_clickable(self.BTN_BUY_NOW))
            btn.click()
            print("[INFO] Đã click Mua Ngay.")
        except Exception as e:
            print(f"[WARN] Không thể click Mua Ngay: {e}")

    def verify_cart_info(self):
        try:
            name = self.wait.until(EC.visibility_of_element_located(self.CART_PRODUCT_NAME)).text.strip()
            options = self.wait.until(EC.visibility_of_element_located(self.CART_PRODUCT_OPTIONS)).text.strip()
            print(f"[INFO] Trong giỏ hàng có: {name} | {options}")
            return name, options
        except Exception as e:
            print(f"[WARN] Không đọc được thông tin giỏ hàng: {e}")
            return "", ""

    # ------------------ B8–B9 ------------------
    def _normalize_text(self, text):
        return (text or "").lower().replace("tp.", "").replace("thành phố", "").replace("tỉnh", "").strip()

    def _wait_for_dropdown(self, locator):
        """Đợi dropdown load xong (phải có ít nhất 2 options)."""
        self.wait.until(lambda d: len(Select(d.find_element(*locator)).options) > 1)

    def _select_option_approx(self, locator, text):
        """Chọn option gần đúng (dễ chịu với chữ hoa/thường)."""
        text_norm = self._normalize_text(text)
        sel = Select(self.driver.find_element(*locator))
        for opt in sel.options:
            if text_norm in self._normalize_text(opt.text):
                opt.click()
                print(f"[INFO] Đã chọn: {opt.text}")
                return True
        print(f"[WARN] Không tìm thấy option khớp với '{text}'")
        return False

    def fill_customer_info(self, fullname, phone, address, province, district, ward):
        """Nhập thông tin người nhận + chọn địa chỉ."""
        try:
            # Nhập dữ liệu
            for locator, val in [(self.FULLNAME, fullname), (self.PHONE, phone), (self.ADDRESS, address)]:
                el = self.driver.find_element(*locator)
                el.clear()
                if val:
                    el.send_keys(val)

            # Chọn tỉnh
            if province:
                self._wait_for_dropdown(self.PROVINCE)
                self._select_option_approx(self.PROVINCE, province)
                time.sleep(1.5)
            # Chọn huyện
            if district:
                self._wait_for_dropdown(self.DISTRICT)
                self._select_option_approx(self.DISTRICT, district)
                time.sleep(1.5)
            # Chọn xã
            if ward:
                self._wait_for_dropdown(self.WARD)
                self._select_option_approx(self.WARD, ward)
        except Exception as e:
            print(f"[WARN] Không nhập được thông tin người nhận: {e}")

    # ------------------ B10 ------------------
    def click_order(self):
        try:
            btn = self.wait.until(EC.presence_of_element_located(self.BTN_ORDER))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            time.sleep(0.8)
            self.wait.until(EC.element_to_be_clickable(self.BTN_ORDER)).click()
            print("[INFO] Đã click Đặt hàng.")
        except Exception as e:
            print(f"[WARN] Không thể click Đặt hàng: {e}")

    # ------------------ THÔNG BÁO ------------------
    def get_alert_message(self):
        try:
            el = self.wait.until(EC.visibility_of_element_located(self.ALERT_ERROR))
            return el.text.strip()
        except:
            return self.driver.execute_script(
                "return document.querySelector(':invalid')?.validationMessage || '';"
            ) or "Không có thông báo hiển thị."

    def get_success_message(self):
        """Kiểm tra trang /cart/success và dòng chữ 'Đặt hàng thành công!'."""
        try:
            self.wait.until(EC.url_contains("/cart/success"))
            if "/cart/success" in self.driver.current_url:
                el = self.wait.until(EC.visibility_of_element_located(self.SUCCESS_TEXT))
                msg = (el.text or "").strip()
                if "đặt hàng thành công" in msg.lower():
                    print("[INFO] Trang /cart/success — Đặt hàng thành công!")
                    return msg
            return ""
        except Exception:
            return ""
