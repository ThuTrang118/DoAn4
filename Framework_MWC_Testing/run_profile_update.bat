@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title CHẠY TEST: CẬP NHẬT HỒ SƠ (PROFILE UPDATE)
set /p MODE="Nhập loại dữ liệu (excel / csv / json): "
if "%MODE%"=="" set MODE=excel

if /i "%MODE%"=="excel" (
    set "FILE=data\TestData.xlsx"
) else if /i "%MODE%"=="csv" (
    set "FILE=data\ProfileData.csv"
) else if /i "%MODE%"=="json" (
    set "FILE=data\ProfileData.json"
) else (
    echo Loại dữ liệu không hợp lệ.
    pause
    exit /b
)
pytest -s -v tests\test_profile_update_ddt.py --data-mode=%MODE% --data-file=%FILE% --alluredir=reports/allure-results/profile_update

allure generate reports/allure-results/profile_update -o reports/allure-report/profile_update --clean
start "" reports/allure-report/profile_update/index.html
pause
