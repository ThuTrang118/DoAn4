# tests/conftest.py
import os, time, pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils.excel_utils import ResultBook, ensure_dir

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SS_DIR = os.path.join(BASE_DIR, "reports", "screenshots")
RES_DIR = os.path.join(BASE_DIR, "reports", "results")
ensure_dir(SS_DIR); ensure_dir(RES_DIR)

@pytest.fixture(scope="session")
def result_writer(request):
    # Ghi cố định vào results_data.xlsx
    writer = ResultBook(out_dir=RES_DIR, file_name="results_data.xlsx")
    def finalize():
        path = writer.save()
        print(f"\n[RESULT FILE]: {path}")
    request.addfinalizer(finalize)
    return writer

@pytest.fixture
def driver():
    opts = Options()
    # Tuỳ chọn: ép ngôn ngữ VI (không bắt buộc vì ta dùng Validity API)
    opts.add_argument("--lang=vi")
    opts.add_experimental_option("prefs", {"intl.accept_languages": "vi,vi_VN"})
    opts.add_argument("--start-maximized")
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument("--ignore-ssl-errors=yes")
    d = webdriver.Chrome(options=opts)
    yield d
    d.quit()

# Chụp ảnh khi FAIL
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver")
        if driver:
            ts = time.strftime("%Y%m%d-%H%M%S")
            name = f"{item.name}-{ts}.png"
            path = os.path.join(SS_DIR, name)
            try:
                driver.save_screenshot(path)
                print(f"\n[SCREENSHOT SAVED]: {path}")
            except Exception as e:
                print(f"\n[WARN] Cannot save screenshot: {e}")
