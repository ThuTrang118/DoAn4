@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title CHẠY TEST: ĐÁNH GIÁ SẢN PHẨM (PRODUCT REVIEW)
set /p MODE="Nhập loại dữ liệu (excel / csv / json): "
if "%MODE%"=="" set MODE=excel

if /i "%MODE%"=="excel" (
    set "FILE=data\TestData.xlsx"
) else if /i "%MODE%"=="csv" (
    set "FILE=data\ProductReviewData.csv"
) else if /i "%MODE%"=="json" (
    set "FILE=data\ProductReviewData.json"
) else (
    echo Loại dữ liệu không hợp lệ.
    pause
    exit /b
)
if exist reports\allure-results\product_review (
    echo Đang xóa thư mục cũ: reports\allure-results\product_review ...
    rmdir /s /q reports\allure-results\product_review
)
if exist reports\allure-report\product_review (
    echo Đang xóa thư mục cũ: reports\allure-report\product_review ...
    rmdir /s /q reports\allure-report\product_review
)
mkdir reports\allure-results\product_review >nul 2>&1
pytest -s -v tests\test_product_review_ddt.py --data-mode=%MODE% --data-file=%FILE% --alluredir=reports/allure-results/product_review
allure generate reports/allure-results/product_review -o reports/allure-report/product_review --clean
start "" reports/allure-report/product_review\index.html
pause
