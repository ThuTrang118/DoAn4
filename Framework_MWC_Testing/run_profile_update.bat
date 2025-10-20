@echo off
chcp 65001 >nul
echo CHẠY TEST: CẬP NHẬT HỒ SƠ (PROFILE UPDATE)
pytest tests/test_profile_update_ddt.py --alluredir=reports/allure-results/profile_update
echo TẠO BÁO CÁO ALLURE (PROFILE UPDATE)
allure generate reports/allure-results/profile_update -o reports/allure-report/profile_update --clean
allure serve reports/allure-report/profile_update
pause
