import unicodedata
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger_utils import create_logger

logger = create_logger("SearchPage")

class MWCSearchPage:
    """Trang tìm kiếm sản phẩm trên website MWC."""

    URL = "https://mwc.com.vn/"
    SEARCH_BOX = (By.XPATH, "(//input[@placeholder='Tìm kiếm'])[1]")
    FIRST_RESULT = (By.XPATH, "(//div[@class='product-grid-item'])[1]")
    PRODUCT_TITLES = (By.CSS_SELECTOR, "a[class='product-grid-info pl-id-5370'] p[class='product-grid-title']")

    def __init__(self, driver, timeout: int = 12):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # ---------------- Tiện ích ----------------
    def normalize_text(self, text: str) -> str:
        """Chuẩn hóa tiếng Việt (bỏ dấu, viết thường) để so sánh."""
        if not text:
            return ""
        text = unicodedata.normalize("NFD", text)
        text = text.encode("ascii", "ignore").decode("utf-8")
        return text.lower().strip()

    # ---------------- Chức năng chính ----------------
    def open(self):
        self.driver.get(self.URL)
        logger.info("Mở trang chủ MWC.")

    def search(self, keyword: str):
        """Nhập từ khóa vào ô tìm kiếm và nhấn Enter."""
        box = self.wait.until(EC.presence_of_element_located(self.SEARCH_BOX))
        box.clear()
        box.send_keys(keyword)
        box.submit()
        logger.info(f"Thực hiện tìm kiếm với từ khóa: '{keyword}'")

    def get_first_result_text(self) -> str:
        """Lấy nội dung sản phẩm đầu tiên (nếu có)."""
        try:
            el = self.wait.until(EC.presence_of_element_located(self.FIRST_RESULT))
            text = (el.text or "").strip()
            logger.info(f"Sản phẩm đầu tiên: {text}")
            return text
        except Exception:
            # ⚠️ Giữ cảnh báo ngắn gọn – KHÔNG in stacktrace
            logger.warning("Không tìm thấy sản phẩm đầu tiên (bỏ qua).")
            return ""

    def get_all_titles(self):
        """Lấy danh sách toàn bộ tiêu đề sản phẩm hiển thị."""
        try:
            self.wait.until(EC.presence_of_all_elements_located(self.PRODUCT_TITLES))
            elements = self.driver.find_elements(*self.PRODUCT_TITLES)
            titles = [el.text.strip() for el in elements if el.text.strip()]
            logger.info(f"Đã lấy {len(titles)} sản phẩm hiển thị.")
            return titles
        except Exception:
            logger.warning("Không thể lấy danh sách tiêu đề sản phẩm (bỏ qua).")
            return []

    def check_keyword(self, keyword: str) -> tuple[bool, str]:
        """Kiểm tra từ khóa trong sản phẩm đầu tiên hoặc toàn trang."""
        keyword_norm = self.normalize_text(keyword)

        # --- Bước 1: Kiểm tra sản phẩm đầu tiên ---
        first_text = self.get_first_result_text()
        if first_text and keyword_norm in self.normalize_text(first_text):
            logger.info(f"Từ khóa '{keyword}' xuất hiện trong sản phẩm đầu tiên.")
            return True, first_text

        # --- Bước 2: Kiểm tra toàn trang ---
        all_titles = self.get_all_titles()
        for title in all_titles:
            if keyword_norm in self.normalize_text(title):
                logger.info(f"Từ khóa '{keyword}' tìm thấy trong sản phẩm: {title}")
                return True, title

        # --- Bước 3: Không tìm thấy ---
        logger.warning(f"Không tìm thấy sản phẩm nào chứa từ khóa '{keyword}'.")
        return False, "Không tìm thấy sản phẩm"
