import os, time, pytest, subprocess, datetime, shutil, webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils.excel_utils import ResultBook, ensure_dir
import allure

# ---------------- ĐƯỜNG DẪN CỐ ĐỊNH ----------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
SS_DIR = os.path.join(REPORTS_DIR, "screenshots")
RES_DIR = os.path.join(REPORTS_DIR, "results")
ALLURE_RESULTS = os.path.join(REPORTS_DIR, "allure-results")
ALLURE_REPORT = os.path.join(REPORTS_DIR, "allure-report")

for d in [SS_DIR, RES_DIR, ALLURE_RESULTS, ALLURE_REPORT]:
    ensure_dir(d)

# ---------------- KHAI BÁO TÙY CHỌN TOÀN CỤC ----------------
def pytest_addoption(parser):
    """Thêm option để chọn loại và file dữ liệu đầu vào."""
    parser.addoption(
        "--data-mode",
        action="store",
        default="excel",
        help="Chọn loại dữ liệu: excel | csv | json"
    )
    parser.addoption(
        "--data-file",
        action="store",
        default="data/TestData.xlsx",
        help="Đường dẫn đến file dữ liệu test (mặc định: data/TestData.xlsx)"
    )

# ---------------- GHI KẾT QUẢ ----------------
@pytest.fixture(scope="session")
def result_writer(request):
    writer = ResultBook(out_dir=RES_DIR, file_name="ResultsData.xlsx")

    def finalize():
        path = writer.save()
        print(f"\n[RESULT FILE SAVED]: {path}")

    request.addfinalizer(finalize)
    return writer

# ---------------- FIXTURE: KHỞI TẠO WEBDRIVER ----------------
@pytest.fixture
def driver():
    opts = Options()
    opts.add_argument("--lang=vi")
    opts.add_experimental_option("prefs", {"intl.accept_languages": "vi,vi_VN"})
    opts.add_argument("--start-maximized")
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument("--ignore-ssl-errors=yes")

    driver = webdriver.Chrome(options=opts)
    yield driver
    driver.quit()

# ---------------- CHỤP ẢNH KHI FAIL + GẮN VÀO ALLURE ----------------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Chụp ảnh khi testcase FAIL và attach vào Allure."""
    outcome = yield
    rep = outcome.get_result()
    driver = item.funcargs.get("driver", None)
    if not driver:
        return

    base_name = item.name.replace("[", "_").replace("]", "_")
    img_path = os.path.join(SS_DIR, f"{base_name}.png")

    # Khi testcase FAIL
    if rep.when == "call" and rep.failed:
        try:
            if os.path.exists(img_path):
                os.remove(img_path)
            driver.save_screenshot(img_path)
            print(f"\n[SCREENSHOT SAVED]: {img_path}")
            with open(img_path, "rb") as f:
                allure.attach(
                    f.read(),
                    name=os.path.basename(img_path),
                    attachment_type=allure.attachment_type.PNG
                )
        except Exception as e:
            print(f"[WARN] Không thể chụp ảnh: {e}")

    # Khi testcase PASS: xóa ảnh cũ (nếu có)
    elif rep.when == "call" and rep.passed:
        if os.path.exists(img_path):
            try:
                os.remove(img_path)
                print(f"[CLEANUP] Xóa ảnh cũ sau khi PASS: {img_path}")
            except Exception:
                pass

# ---------------- TỰ ĐỘNG SINH ALLURE REPORT SAU KHI TEST ----------------
def pytest_sessionfinish(session, exitstatus):
    """
    Sau khi chạy xong 1 module test:
      - Xác định đúng thư mục chức năng (login, register, search, order,...)
      - Giữ lại dữ liệu Allure do pytest ghi
      - Sinh báo cáo Allure mới
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # --- Lấy file test đang chạy ---
    try:
        test_file = session.config.invocation_params.args[0]
    except Exception:
        test_file = "all_tests"

    # --- Rút gọn tên chức năng từ file test ---
    base_name = os.path.basename(test_file)
    func_name = os.path.splitext(base_name)[0].replace("test_", "")
    for suffix in ["_ddt", "_bai1", "_bai2"]:
        if func_name.endswith(suffix):
            func_name = func_name.replace(suffix, "")

    # --- Đường dẫn đến thư mục Allure ---
    allure_results = os.path.join(ALLURE_RESULTS, func_name)
    allure_report = os.path.join(ALLURE_REPORT, func_name)

    # ⚠️ KHÔNG xóa dữ liệu cũ ở đây nữa, để pytest giữ file .json
    ensure_dir(allure_results)

    print(f"\n[ALLURE] Tạo báo cáo cho chức năng: {func_name}")
    try:
        subprocess.run(
            ["allure", "generate", allure_results, "-o", allure_report, "--clean"],
            check=True
        )
        print(f"[ALLURE] Báo cáo HTML đã tạo tại: {allure_report}\\index.html\n")

        index_path = os.path.abspath(os.path.join(allure_report, "index.html"))
        if os.path.exists(index_path):
            webbrowser.open_new_tab(index_path)
            print(f"[OPEN] Mở báo cáo Allure trên Chrome: {index_path}")

    except Exception as e:
        print(f"[ALLURE] Lỗi khi tạo báo cáo: {e}")
