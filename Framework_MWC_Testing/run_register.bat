@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title CHẠY TEST: ĐĂNG KÝ (REGISTER)
set /p MODE="Nhập loại dữ liệu (excel / csv / json): "
if "%MODE%"=="" set MODE=excel

if /i "%MODE%"=="excel" (
    set "FILE=data\TestData.xlsx"
) else if /i "%MODE%"=="csv" (
    set "FILE=data\RegisterData.csv"
) else if /i "%MODE%"=="json" (
    set "FILE=data\RegisterData.json"
) else (
    echo Loại dữ liệu không hợp lệ.
    pause
    exit /b
)
pytest -s -v tests\test_register_ddt.py --data-mode=%MODE% --data-file=%FILE% --alluredir=reports/allure-results/register

allure generate reports/allure-results/register -o reports/allure-report/register --clean
start "" reports/allure-report/register/index.html
pause
