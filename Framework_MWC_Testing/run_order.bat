@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title CHẠY TEST: ĐẶT HÀNG (ORDER)
set /p MODE="Nhập loại dữ liệu (excel / csv / json): "
if "%MODE%"=="" set MODE=excel
if /i "%MODE%"=="excel" (
    set "FILE=data\TestData.xlsx"
) else if /i "%MODE%"=="csv" (
    set "FILE=data\OrderData.csv"
) else if /i "%MODE%"=="json" (
    set "FILE=data\OrderData.json"
) else (
    echo Loại dữ liệu không hợp lệ.
    pause
    exit /b
)
if exist reports\allure-results\order (
    echo Đang xóa thư mục cũ: reports\allure-results\order ...
    rmdir /s /q reports\allure-results\order
)
if exist reports\allure-report\order (
    echo Đang xóa thư mục cũ: reports\allure-report\order ...
    rmdir /s /q reports\allure-report\order
)
mkdir reports\allure-results\order >nul 2>&1
pytest -s -v tests\test_order_ddt.py --data-mode=%MODE% --data-file=%FILE% --alluredir=reports/allure-results/order
allure generate reports/allure-results/order -o reports/allure-report/order --clean
start "" reports/allure-report/order\index.html
pause
