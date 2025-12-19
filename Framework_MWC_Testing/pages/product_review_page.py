from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MWCProductReviewPage:
    PRODUCT_URL = "https://mwc.com.vn/products/giay-cao-got-mwc-nucg--g299?&c=bac"

    # Step 2: tab "BÌNH LUẬN" (li role=presentation thứ 2)
    TAB_COMMENT = (By.XPATH, "(//li[@role='presentation'])[2]")

    # Step 3: input fields
    FULLNAME = (By.ID, "FullName")
    PHONE    = (By.ID, "Phone")
    EMAIL    = (By.ID, "Email")
    TITLE    = (By.ID, "Title")
    CONTENT  = (By.ID, "Content")

    # Step 5: button "Gửi"
    BTN_SEND = (By.XPATH, "(//button[contains(text(),'Gửi')])[1]")

    # Step check errors (ưu tiên 1)
    ERR_FULLNAME = (By.ID, "FullName-error")
    ERR_PHONE    = (By.ID, "Phone-error")
    ERR_EMAIL    = (By.ID, "Email-error")
    ERR_TITLE    = (By.ID, "Title-error")
    ERR_CONTENT  = (By.ID, "Content-error")

    # Step check success (ưu tiên 2)
    SWAL_ACTIONS = (By.XPATH, "(//div[@class='swal2-actions'])[1]")
    SWAL_TITLE_OK = (By.XPATH, "(//h2[contains(text(),'Gửi bình luận thành công!')])[1]")

    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self):
        self.driver.get(self.PRODUCT_URL)

    def _scroll_into_view(self, locator):
        el = self.wait.until(EC.presence_of_element_located(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        return el

    def open_comment_tab(self):
        el = self._scroll_into_view(self.TAB_COMMENT)
        self.wait.until(EC.element_to_be_clickable(self.TAB_COMMENT)).click()

    def fill_form(self, full_name: str, phone: str, email: str, title: str, content: str):
        # Có thể dùng clear + send_keys để chắc chắn
        for locator, value in [
            (self.FULLNAME, full_name),
            (self.PHONE, phone),
            (self.EMAIL, email),
            (self.TITLE, title),
            (self.CONTENT, content),
        ]:
            el = self.wait.until(EC.presence_of_element_located(locator))
            el.clear()
            el.send_keys(value or "")

    def select_star(self, star: int):
        """
        star: 1..5
        Bạn đưa 1 xpath tuyệt đối cho input; để chọn 1..5 ổn định hơn,
        ta dùng xpath theo index label/input trong khối đánh giá.
        """
        if star < 1 or star > 5:
            raise ValueError("star must be in range 1..5")

        # Cố gắng chọn theo cấu trúc thường gặp: div[5] là khu vực rating có nhiều label/input
        # Index [star] là số sao (1..5)
        star_locator = (
            By.XPATH,
            f"(//form//div[contains(@class,'rating') or contains(@class,'rate') or .//label/input])[1]//label/input[{star}]"
        )

        # Nếu website không có class rating/rate, dùng fallback theo label/input trong div[5]
        fallback_locator = (
            By.XPATH,
            f"(/html/body/div[1]/div/section[1]/div/section/div[1]/div/div[2]/div/div/div[2]/form/div[5]//label/input)[{star}]"
        )

        try:
            self._scroll_into_view(star_locator)
            self.wait.until(EC.element_to_be_clickable(star_locator)).click()
        except Exception:
            self._scroll_into_view(fallback_locator)
            self.wait.until(EC.element_to_be_clickable(fallback_locator)).click()

    def click_send(self):
        self._scroll_into_view(self.BTN_SEND)
        self.wait.until(EC.element_to_be_clickable(self.BTN_SEND)).click()

    def _is_any_visible(self, locators, short_timeout=2) -> bool:
        w = WebDriverWait(self.driver, short_timeout)
        for loc in locators:
            try:
                el = w.until(EC.visibility_of_element_located(loc))
                if el:
                    return True
            except Exception:
                pass
        return False

    def get_actual_result(self) -> str:
        """
        Kết quả theo rule bạn yêu cầu:
        1) Nếu có bất kỳ *-error hiển thị -> "Vui lòng nhập!"
        2) Nếu xuất hiện swal2-actions hoặc h2 'Gửi bình luận thành công!' -> "Gửi bình luận thành công!"
        3) Còn lại -> "Kết quả không hợp lệ"
        """
        # Ưu tiên 1: error
        error_locators = [
            self.ERR_FULLNAME, self.ERR_PHONE, self.ERR_EMAIL, self.ERR_TITLE, self.ERR_CONTENT
        ]
        if self._is_any_visible(error_locators, short_timeout=2):
            return "Vui lòng nhập!"

        # Ưu tiên 2: success popup
        success_locators = [self.SWAL_ACTIONS, self.SWAL_TITLE_OK]
        if self._is_any_visible(success_locators, short_timeout=4):
            return "Gửi bình luận thành công!"

        return "Kết quả không hợp lệ"
