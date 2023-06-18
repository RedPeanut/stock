# stock 

# Features

# Install

```bash
$ git clone https://github.com/RedPeanut/stock.git
$ cd stock
$ git clone https://github.com/FinanceData/FinanceDataReader.git # 
$ git clone https://github.com/FinanceData/marcap.git #
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

# Usage

```bash
$ python -m my.crawling_v2 --quarter=2022/03 # yyyy/mm
... 대략 5분 소요 ...
$ python -m my.rating --name={결과엑셀파일} # my/download 폴더
```
소형주 엑셀파일 상위20종목에 투자(금융사, 지주사 제외)

# License
This project is licensed under the MIT License