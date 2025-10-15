# pages/search_page.py
import unicodedata
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MWCSearchPage:
    """Trang tìm kiếm sản phẩm trên website MWC."""

    URL = "https://mwc.com.vn/"
    SEARCH_BOX = (By.XPATH, "(//input[@placeholder='Tìm kiếm'])[1]")
    FIRST_RESULT = (By.XPATH, "/html/body/div[1]/div/section[1]/div/section/div/div/div/div[1]/div[2]/div/div[7]/div/a/div/p[1]")
    PRODUCT_TITLES = (By.CLASS_NAME, "product-grid-title")

    def __init__(self, driver, timeout: int = 12):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # ==============================================================
    # 🔹 Hàm chuẩn hóa: chuyển tiếng Việt có dấu → không dấu
    # ==============================================================
    def normalize_text(self, text: str) -> str:
        """Xóa dấu tiếng Việt và viết thường để so sánh không phân biệt dấu."""
        if not text:
            return ""
        text = unicodedata.normalize('NFD', text)
        text = text.encode('ascii', 'ignore').decode('utf-8')
        return text.lower().strip()

    # ==============================================================
    # 🔹 Các hành động trang tìm kiếm
    # ==============================================================
    def open(self):
        """Mở trang chủ MWC."""
        self.driver.get(self.URL)

    def search(self, keyword: str):
        """Nhập từ khóa vào ô tìm kiếm và nhấn Enter."""
        box = self.wait.until(EC.presence_of_element_located(self.SEARCH_BOX))
        box.clear()
        box.send_keys(keyword)
        box.submit()

    def get_first_result_text(self) -> str:
        """Lấy nội dung sản phẩm đầu tiên (theo XPath cố định)."""
        try:
            el = self.wait.until(EC.presence_of_element_located(self.FIRST_RESULT))
            return (el.text or "").strip()
        except Exception:
            return ""

    def get_all_titles(self):
        """Lấy tất cả tiêu đề sản phẩm trên trang."""
        try:
            self.wait.until(EC.presence_of_all_elements_located(self.PRODUCT_TITLES))
            elements = self.driver.find_elements(*self.PRODUCT_TITLES)
            return [el.text.strip() for el in elements if el.text.strip()]
        except Exception:
            return []

    # ==============================================================
    # 🔹 Kiểm tra kết quả tìm kiếm (Actual = nội dung thực tế)
    # ==============================================================
    def check_keyword(self, keyword: str) -> tuple[bool, str]:
        """
        Kiểm tra tuần tự (có hỗ trợ so khớp không dấu):
        1️⃣ Kiểm tra sản phẩm đầu tiên (XPath).
        2️⃣ Nếu không có hoặc không chứa → kiểm tra toàn trang.
        3️⃣ Nếu không có sản phẩm nào → ghi rõ “Không tìm thấy sản phẩm.”
        Trả về (bool, actual_text)
        """
        keyword_norm = self.normalize_text(keyword)

        # --- Bước 1: Kiểm tra sản phẩm đầu tiên ---
        first_text = self.get_first_result_text()
        first_norm = self.normalize_text(first_text)

        if first_text and keyword_norm in first_norm:
            # ✅ Nếu sản phẩm đầu tiên chứa từ khóa
            return True, first_text  # Ghi nội dung thật làm Actual

        # --- Bước 2: Kiểm tra toàn trang ---
        all_titles = self.get_all_titles()
        if all_titles:
            for title in all_titles:
                if keyword_norm in self.normalize_text(title):
                    return True, title  # Ghi sản phẩm tìm thấy thật
            return False, "Không tìm thấy sản phẩm"

        # --- Bước 3: Không có sản phẩm nào ---
        return False, "Không tìm thấy sản phẩm"
