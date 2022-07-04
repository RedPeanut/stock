#!/bin sh
if ! [ -d marcap ]; then
  git clone https://github.com/FinanceData/marcap.git
else
  cd marcap
  git pull
fi
