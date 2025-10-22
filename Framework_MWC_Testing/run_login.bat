@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title CHẠY TEST: ĐĂNG NHẬP (LOGIN)
set /p MODE="Nhập loại dữ liệu (excel / csv / json): "
if "%MODE%"=="" set MODE=excel

if /i "%MODE%"=="excel" (
    set "FILE=data\TestData.xlsx"
) else if /i "%MODE%"=="csv" (
    set "FILE=data\LoginData.csv"
) else if /i "%MODE%"=="json" (
    set "FILE=data\LoginData.json"
) else (
    echo Loại dữ liệu không hợp lệ.
    pause
    exit /b
)
pytest -s -v tests\test_login_ddt.py --data-mode=%MODE% --data-file=%FILE% --alluredir=reports/allure-results/login

allure generate reports/allure-results/login -o reports/allure-report/login --clean
start "" reports/allure-report/login/index.html
pause
