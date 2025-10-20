@echo off
chcp 65001 >nul
echo CHẠY TEST: ĐẶT HÀNG (ORDER)
pytest tests/test_order_ddt.py --alluredir=reports/allure-results/order
echo TẠO BÁO CÁO ALLURE (ORDER)
allure generate reports/allure-results/order -o reports/allure-report/order --clean
allure serve reports/allure-report/order
pause
