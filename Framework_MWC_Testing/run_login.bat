@echo off
chcp 65001 >nul
title CHẠY TEST: ĐĂNG NHẬP (LOGIN)
set /p MODE="Nhập loại dữ liệu (excel / csv / json): "
if "%MODE%"=="" set MODE=excel
echo -------------------------------------
echo Sử dụng dữ liệu đầu vào: %MODE%
echo -------------------------------------
rmdir /s /q reports\allure-results\login >nul 2>&1
rmdir /s /q reports\allure-report\login >nul 2>&1
echo =====================================================
echo ĐANG CHẠY TEST CHỨC NĂNG: ĐĂNG NHẬP (%MODE%)
echo =====================================================
pytest -s -v tests/test_login_ddt.py --data-mode=%MODE% --alluredir=reports/allure-results/login
echo =====================================================
echo TẠO BÁO CÁO ALLURE (LOGIN)
echo =====================================================
allure generate reports/allure-results/login -o reports/allure-report/login --clean
echo =====================================================
echo MỞ BÁO CÁO TRÊN CHROME
echo =====================================================
start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" "reports/allure-report/login/index.html"
pause
