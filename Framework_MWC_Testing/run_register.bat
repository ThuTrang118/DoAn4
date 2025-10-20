@echo off
chcp 65001 >nul
echo CHẠY TEST: ĐĂNG KÝ TÀI KHOẢN (REGISTER)
pytest tests/test_register_ddt.py --alluredir=reports/allure-results/register
echo TẠO BÁO CÁO ALLURE (REGISTER)
allure generate reports/allure-results/register -o reports/allure-report/register --clean
allure serve reports/allure-results/register
pause
