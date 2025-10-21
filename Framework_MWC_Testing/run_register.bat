@echo off
chcp 65001 >nul
title CHẠY TEST: ĐĂNG KÝ (REGISTER)
set /p MODE="Nhập loại dữ liệu (excel / csv / json): "
if "%MODE%"=="" set MODE=excel
echo -------------------------------------
echo Sử dụng dữ liệu đầu vào: %MODE%
echo -------------------------------------
rmdir /s /q reports\allure-results\register >nul 2>&1
rmdir /s /q reports\allure-report\register >nul 2>&1
echo =====================================================
echo ĐANG CHẠY TEST CHỨC NĂNG: ĐĂNG KÝ (%MODE%)
echo =====================================================
pytest -s -v tests/test_register_ddt.py --data-mode=%MODE% --alluredir=reports/allure-results/register
echo =====================================================
echo TẠO BÁO CÁO ALLURE (REGISTER)
echo =====================================================
allure generate reports/allure-results/register -o reports/allure-report/register --clean
echo =====================================================
echo MỞ BÁO CÁO TRÊN CHROME
echo =====================================================
start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" "reports/allure-report/register/index.html"
pause
