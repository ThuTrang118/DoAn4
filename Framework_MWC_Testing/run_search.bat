@echo off
chcp 65001 >nul
echo CHẠY TEST: TÌM KIẾM SẢN PHẨM (SEARCH)
pytest tests/test_search_ddt.py --alluredir=reports/allure-results/search
echo TẠO BÁO CÁO ALLURE (SEARCH)
allure generate reports/allure-results/search -o reports/allure-report/search --clean
allure serve reports/allure-results/search
pause
