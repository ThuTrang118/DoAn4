import os, time, pytest, subprocess, datetime, shutil, webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils.excel_utils import ResultBook, ensure_dir
import allure

# --- Đường dẫn thư mục ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
SS_DIR = os.path.join(REPORTS_DIR, "screenshots")
RES_DIR = os.path.join(REPORTS_DIR, "results")
ALLURE_RESULTS = os.path.join(REPORTS_DIR, "allure-results")
ALLURE_REPORT = os.path.join(REPORTS_DIR, "allure-report")

for d in [SS_DIR, RES_DIR, ALLURE_RESULTS, ALLURE_REPORT]:
    ensure_dir(d)


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

    driver = webdriver.Chrome(options=opts)
    yield driver
    driver.quit()


# --- Hook Pytest: Quản lý ảnh chụp khi FAIL ---
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    1 Chụp ảnh khi testcase FAIL (và ghi đè ảnh cũ nếu có)
    2 Xóa ảnh cũ nếu testcase PASS
    3 Gắn screenshot vào Allure report nếu có.
    """
    outcome = yield
    rep = outcome.get_result()
    driver = item.funcargs.get("driver", None)
    if not driver:
        return

    base_name = item.name.replace("[", "_").replace("]", "_")
    img_path = os.path.join(SS_DIR, f"{base_name}.png")

    # --- Nếu FAIL ---
    if rep.when == "call" and rep.failed:
        try:
            if os.path.exists(img_path):
                os.remove(img_path)
            driver.save_screenshot(img_path)
            print(f"\n[SCREENSHOT SAVED]: {img_path}")
            print(f"[FAIL REASON]: {rep.longreprtext[:300]}...")
            with open(img_path, "rb") as f:
                allure.attach(
                    f.read(),
                    name=os.path.basename(img_path),
                    attachment_type=allure.attachment_type.PNG
                )
        except Exception as e:
            print(f"[WARN] Không thể chụp ảnh: {e}")

    # --- Nếu PASS ---
    elif rep.when == "call" and rep.passed:
        if os.path.exists(img_path):
            try:
                os.remove(img_path)
                print(f"[CLEANUP] Xóa ảnh cũ sau khi PASS: {img_path}")
            except Exception:
                pass


# --- TỰ ĐỘNG SINH + MỞ ALLURE REPORT ---
def pytest_sessionfinish(session, exitstatus):
    """
    Sau khi chạy xong 1 module test → tự động:
      - Dọn thư mục Allure cũ
      - Sinh Allure HTML mới cho từng chức năng
      - Mở báo cáo trên Chrome
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Lấy tên file test đang chạy
    test_file = session.config.invocation_params.args[0] if session.config.invocation_params.args else "all_tests"
    func_name = os.path.splitext(os.path.basename(test_file))[0].replace("test_", "")

    # Thư mục kết quả Allure
    allure_results = os.path.join(ALLURE_RESULTS, func_name)
    allure_report = os.path.join(ALLURE_REPORT, func_name)

    # Dọn dữ liệu cũ (tránh nhân đôi testcases)
    if os.path.exists(allure_results):
        shutil.rmtree(allure_results)
        print(f"[CLEANUP] Đã xóa dữ liệu cũ: {allure_results}")
    ensure_dir(allure_results)

    # Tạo báo cáo mới
    print(f"\n[ALLURE] Tạo báo cáo cho chức năng: {func_name}")
    try:
        subprocess.run(
            ["allure", "generate", allure_results, "-o", allure_report, "--clean"],
            check=True
        )
        print(f"[ALLURE] Báo cáo HTML đã tạo tại: {allure_report}/index.html\n")

        # Mở Chrome tự động
        index_path = os.path.abspath(os.path.join(allure_report, "index.html"))
        if os.path.exists(index_path):
            webbrowser.open_new_tab(index_path)
            print(f"[OPEN] Mở báo cáo Allure trên Chrome: {index_path}")

    except Exception as e:
        print(f"[ALLURE] Lỗi khi tạo báo cáo: {e}")
