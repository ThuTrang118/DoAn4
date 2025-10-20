@echo off
chcp 65001 >nul
echo CHẠY TEST: ĐĂNG NHẬP (LOGIN)
pytest tests/test_login_ddt.py --alluredir=reports/allure-results/login
echo TẠO BÁO CÁO ALLURE (LOGIN)
allure generate reports/allure-results/login -o reports/allure-report/login --clean
allure serve reports/allure-report/login
pause
