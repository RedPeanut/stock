@echo off

if not exist marcap (
    git clone https://github.com/FinanceData/marcap.git
) else (
    cd marcap
    git pull
)