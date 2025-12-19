import pytest
from pages.product_review_page import MWCProductReviewPage


@pytest.mark.review
@pytest.mark.parametrize(
    "full_name,phone,email,title,content,star,expected_actual",
    [
        # Case thiếu dữ liệu -> expect "Vui lòng nhập!"
        ("", "", "", "", "", 5, "Vui lòng nhập!"),

        # Case hợp lệ (ví dụ) -> expect "Gửi bình luận thành công!"
        ("Phạm Ánh", "0332115678987", "phamanh@gmail.com", "Sản phẩm tốt", "Mang êm, đúng size.", 5, "Gửi bình luận thành công!"),
    ]
)
def test_product_review_flow(driver, full_name, phone, email, title, content, star, expected_actual):
    page = MWCProductReviewPage(driver)

    # Step 1
    page.open()

    # Step 2
    page.open_comment_tab()

    # Step 3
    page.fill_form(
        full_name=full_name,
        phone=phone,
        email=email,
        title=title,
        content=content
    )

    # Step 4
    page.select_star(star)

    # Step 5
    page.click_send()

    # Verify (theo rule của bạn)
    actual = page.get_actual_result()

    assert actual == expected_actual, f"Expected: {expected_actual} | Actual: {actual}"
