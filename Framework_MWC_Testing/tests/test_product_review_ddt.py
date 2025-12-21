import os
import pytest
from datetime import datetime

from pages.product_review_page import MWCProductReviewPage
from utils.excel_utils import load_data
from utils.logger_utils import create_logger, log_data_source_from_pytest

logger = create_logger("ProductReviewTest")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SHEET = "Product_Review"

DATA_EXCEL = os.path.join(BASE_DIR, "data", "TestData.xlsx")
DATA_CSV   = os.path.join(BASE_DIR, "data", "ProductReviewData.csv")
DATA_JSON  = os.path.join(BASE_DIR, "data", "ProductReviewData.json")


@pytest.fixture(scope="session", autouse=True)
def _auto_log_data_source(pytestconfig):
    log_data_source_from_pytest(logger, pytestconfig)


def get_test_data(data_mode: str):
    if data_mode == "excel":
        return load_data(DATA_EXCEL, sheet_name=SHEET)
    elif data_mode == "csv":
        return load_data(DATA_CSV)
    elif data_mode == "json":
        return load_data(DATA_JSON)
    else:
        raise ValueError("data-mode không hợp lệ")


def pytest_generate_tests(metafunc):
    required = {"tc", "fullname", "phone", "email", "title", "content", "rating", "expected_raw"}
    if required.issubset(metafunc.fixturenames):
        mode = metafunc.config.getoption("--data-mode")
        data = get_test_data(mode)

        seen, params = set(), []
        for r in data:
            tc = str(r.get("testcase", "")).strip()
            if tc and tc not in seen:
                params.append(
                    pytest.param(
                        r.get("testcase", ""),
                        r.get("fullname", ""),
                        r.get("phone", ""),
                        r.get("email", ""),
                        r.get("title", ""),
                        r.get("content", ""),
                        r.get("rating", ""),
                        r.get("expected", ""),
                        id=tc
                    )
                )
                seen.add(tc)

        metafunc.parametrize("tc,fullname,phone,email,title,content,rating,expected_raw", params)


def test_product_review_ddt(driver, result_writer, tc, fullname, phone, email, title, content, rating, expected_raw):
    logger.info(f"\n=== BẮT ĐẦU TESTCASE {tc} ===")

    page = MWCProductReviewPage(driver)

    status, actual = "FAIL", ""
    try:
        page.login_search_open_comment_tab()

        page.fill_form(fullname=fullname, phone=phone, email=email, title=title, content=content)

        # Rating range: set 1..5
        page.select_rating(int(rating) if str(rating).strip() else 0)

        page.click_send()
        actual = page.get_actual_result()

        if (actual or "").strip().lower() == (expected_raw or "").strip().lower():
            status = "PASS"

    except Exception as e:
        actual = f"Lỗi khi chạy testcase: {e}"
        logger.error(actual)

    result_writer.add_row(SHEET, {
        "Testcase": tc,
        "FullName": fullname,
        "Phone": phone,
        "Email": email,
        "Title": title,
        "Content": content,
        "Rating": rating,
        "Expected": expected_raw,
        "Actual": actual,
        "Status": status,
        "Time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    })

    logger.info(f"Expected: {expected_raw}")
    logger.info(f"Actual:   {actual}")
    logger.info(f"Status:   {status}")
    logger.info(f"KẾT THÚC TESTCASE {tc}")
    logger.info("=" * 80 + "\n")

    if status == "FAIL":
        pytest.fail(
            f"Testcase {tc} thất bại.\nExpected: '{expected_raw}'\nActual: '{actual}'",
            pytrace=False
        )
