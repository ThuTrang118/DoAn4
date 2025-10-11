import os, time, pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils.excel_utils import ResultBook, ensure_dir

# --- Đường dẫn thư mục ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SS_DIR = os.path.join(BASE_DIR, "reports", "screenshots")
RES_DIR = os.path.join(BASE_DIR, "reports", "results")
ensure_dir(SS_DIR)
ensure_dir(RES_DIR)


# --- Fixture ghi kết quả ---
@pytest.fixture(scope="session")
def result_writer(request):
    writer = ResultBook(out_dir=RES_DIR, file_name="ResultsData.xlsx")

    def finalize():
        path = writer.save()
        print(f"\n[RESULT FILE SAVED]: {path}")

    request.addfinalizer(finalize)
    return writer


# --- Fixture khởi tạo WebDriver ---
@pytest.fixture
def driver():
    opts = Options()
    opts.add_argument("--lang=vi")
    opts.add_experimental_option("prefs", {"intl.accept_languages": "vi,vi_VN"})
    opts.add_argument("--start-maximized")
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument("--ignore-ssl-errors=yes")
    d = webdriver.Chrome(options=opts)
    yield d
    d.quit()


# --- Hook Pytest: Quản lý ảnh chụp khi FAIL ---
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook này:
    1️⃣ Chụp ảnh khi testcase FAIL (và ghi đè ảnh cũ nếu có)
    2️⃣ Xóa ảnh cũ nếu testcase PASS (từng FAIL trước đó)
    Ảnh luôn lưu ở reports/screenshots/
    """
    outcome = yield
    rep = outcome.get_result()

    driver = item.funcargs.get("driver", None)
    if not driver:
        return

    # Tên file ảnh: ví dụ test_register_ddt_RG3_.png
    base_name = item.name.replace("[", "_").replace("]", "_")
    img_path = os.path.join(SS_DIR, f"{base_name}.png")

    # --- 1. Nếu FAIL -> chụp ảnh (và ghi đè nếu đã có) ---
    if rep.when == "call" and rep.failed:
        # Nếu có ảnh cũ → xóa
        if os.path.exists(img_path):
            try:
                os.remove(img_path)
                print(f"[INFO] Đã xóa ảnh cũ: {img_path}")
            except Exception as e:
                print(f"[WARN] Không thể xóa ảnh cũ: {e}")

        # Chụp ảnh mới
        try:
            driver.save_screenshot(img_path)
            print(f"\n[SCREENSHOT SAVED]: {img_path}")
            print(f"[FAIL REASON]: {rep.longreprtext[:300]}...")
        except Exception as e:
            print(f"[WARN] Không thể chụp ảnh: {e}")

    # --- 2. Nếu PASS -> xóa ảnh cũ nếu còn tồn tại ---
    elif rep.when == "call" and rep.passed:
        if os.path.exists(img_path):
            try:
                os.remove(img_path)
                print(f"[CLEANUP] Testcase '{item.name}' đã PASS, xóa ảnh cũ: {img_path}")
            except Exception as e:
                print(f"[WARN] Không thể xóa ảnh cũ khi PASS: {e}")
