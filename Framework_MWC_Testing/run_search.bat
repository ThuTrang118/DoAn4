@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title CHẠY TEST: TÌM KIẾM (SEARCH)
set /p MODE="Nhập loại dữ liệu (excel / csv / json): "
if "%MODE%"=="" set MODE=excel

if /i "%MODE%"=="excel" (
    set "FILE=data\TestData.xlsx"
) else if /i "%MODE%"=="csv" (
    set "FILE=data\SearchData.csv"
) else if /i "%MODE%"=="json" (
    set "FILE=data\SearchData.json"
) else (
    echo Loại dữ liệu không hợp lệ.
    pause
    exit /b
)
pytest -s -v tests\test_search_ddt.py --data-mode=%MODE% --data-file=%FILE% --alluredir=reports/allure-results/search

allure generate reports/allure-results/search -o reports/allure-report/search --clean
start "" reports/allure-report/search/index.html
pause
