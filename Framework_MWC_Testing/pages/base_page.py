import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
)
from selenium.webdriver.common.action_chains import ActionChains


class BasePage:
    """
    BasePage dùng chung cho các PageObject:
    - Quản lý driver + WebDriverWait
    - Các thao tác cơ bản: open, find, click, type, clear, safe_type
    - Hỗ trợ đọc HTML5 validationMessage (raw & chuẩn hoá)
    """

    def __init__(self, driver, timeout: int = 12):
        self.driver = driver
        self.timeout = timeout              # Lưu timeout để dùng cho các wait cục bộ (ổn định với pytest)
        self.wait = WebDriverWait(driver, timeout)

    # =========================
    # Common actions
    # =========================
    def open(self, url: str):
        """Mở 1 URL bất kỳ."""
        self.driver.get(url)

    def find(self, locator):
        """Tìm phần tử (chờ tối đa timeout)."""
        return self.wait.until(EC.presence_of_element_located(locator))

    def click(self, locator):
        """
        Click phần tử (mặc định).
        Sửa cẩn thận để giảm flaky:
        - Scroll element vào giữa viewport (giảm bị che/ngoài màn hình)
        - Retry nhẹ khi Stale/Intercepted (DOM refresh/overlay)
        Không đổi contract (không return).
        """
        # Lấy element trước để scroll (presence là đủ cho scroll)
        el = self.wait.until(EC.presence_of_element_located(locator))
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            time.sleep(0.05)  # rất nhỏ, tránh ảnh hưởng tốc độ chung
        except Exception:
            pass

        try:
            self.wait.until(EC.element_to_be_clickable(locator)).click()
        except (StaleElementReferenceException, ElementClickInterceptedException):
            # Retry 1 lần (nhẹ, ít ảnh hưởng các trang khác)
            el = self.wait.until(EC.presence_of_element_located(locator))
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                time.sleep(0.05)
            except Exception:
                pass
            self.wait.until(EC.element_to_be_clickable(locator)).click()

    def click_robust(self, locator, timeout: int | None = None, js_fallback: bool = True):
        """
        Click "cứng" dành cho element hay bị chặn click (overlay/loading/toast).
        KHÔNG bắt buộc dùng cho tất cả page; chỉ gọi khi cần (VD: nút Lưu).
        Không đổi behavior click() mặc định.
        """
        wait = WebDriverWait(self.driver, timeout or self.timeout)

        # 1) presence + scroll
        el = wait.until(EC.presence_of_element_located(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        time.sleep(0.15)

        # 2) clickable + click, retry bằng ActionChains nếu bị intercept/stale
        try:
            el = wait.until(EC.element_to_be_clickable(locator))
            el.click()
            return
        except (StaleElementReferenceException, ElementClickInterceptedException):
            el = wait.until(EC.element_to_be_clickable(locator))
            try:
                ActionChains(self.driver).move_to_element(el).pause(0.05).click(el).perform()
                return
            except Exception:
                pass

        # 3) JS fallback (tùy chọn)
        if js_fallback:
            el = self.driver.find_element(*locator)
            self.driver.execute_script("arguments[0].click();", el)
            return

        raise TimeoutException(f"Robust click failed for locator: {locator}")

    def type(self, locator, text: str):
        """
        Nhập dữ liệu vào ô input:
        - Luôn clear trước
        - Dùng cho các field bắt buộc phải nhập giá trị
        """
        el = self.find(locator)
        el.clear()
        el.send_keys(text)

    def clear(self, locator):
        """
        Chỉ clear nội dung của 1 ô input.
        Trả về element để caller có thể dùng tiếp nếu cần.
        """
        el = self.find(locator)
        el.clear()
        return el

    def safe_type(self, locator, text: str | None):
        """
        Nhập dữ liệu "an toàn":
        - Luôn clear trước
        - Chỉ send_keys nếu text không rỗng
        Dùng cho các form update / order, nơi dữ liệu test có thể để trống 1 vài field.
        """
        el = self.clear(locator)
        if text:
            el.send_keys(text)
        return el

    # =========================
    # HTML5 validation (raw)
    # =========================
    def get_validation_message(self, locator) -> str:
        """
        Trả về thông báo HTML5 validation thô (theo ngôn ngữ của trình duyệt),
        đọc từ thuộc tính validationMessage của element.
        """
        try:
            el = self.find(locator)
            return (el.get_attribute("validationMessage") or "").strip()
        except Exception:
            return ""

    def value_missing(self, locator) -> bool:
        """Kiểm tra xem field có bị bỏ trống theo validity API không."""
        try:
            el = self.find(locator)
            return bool(
                self.driver.execute_script(
                    "return arguments[0].validity ? arguments[0].validity.valueMissing : false;",
                    el,
                )
            )
        except Exception:
            return False

    # =========================
    # HTML5 validation (chuẩn hoá)
    # =========================
    def _normalize_html5_message(self, raw: str) -> str:
        """
        Chuẩn hoá thông báo validation về tiếng Việt "chuẩn" để dễ so sánh trong test.
        Không phụ thuộc hoàn toàn vào wording của trình duyệt.
        """
        msg = (raw or "").strip()
        lower = msg.lower()

        if not msg:
            return ""

        # Một số pattern hay gặp (có thể mở rộng dần khi test thực tế)
        if "@" in lower and "bao gồm" in lower:
            return "Vui lòng bao gồm '@' trong địa chỉ email."
        if "vui lòng điền" in lower or "please fill" in lower:
            return "Vui lòng điền vào trường này."
        if "email" in lower:
            return "Vui lòng nhập địa chỉ email hợp lệ."
        if "số" in lower or "number" in lower:
            return "Vui lòng nhập số hợp lệ."

        return msg

    def get_html5_validation(self, locator) -> str:
        """
        Lấy thông báo HTML5 validation của 1 field và chuẩn hoá lại.
        Dùng chung cho các page muốn so sánh message trong testcase.
        """
        try:
            el = self.find(locator)
            raw = self.driver.execute_script(
                "return arguments[0].validationMessage || '';",
                el,
            )
            return self._normalize_html5_message(raw)
        except Exception:
            return ""

    def get_page_validation_message(self) -> str:
        """
        Lấy validationMessage của field đầu tiên bị :invalid trên toàn trang,
        rồi chuẩn hoá lại. Dùng cho các form không truyền locator cụ thể
        (ví dụ Order chỉ cần biết lý do lỗi chung).
        """
        try:
            raw = self.driver.execute_script(
                "return document.querySelector(':invalid')?.validationMessage || '';"
            )
            return self._normalize_html5_message(raw)
        except Exception:
            return ""
