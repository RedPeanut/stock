# AI 코파일럿 지시사항 - 한국 주식 분석 코드베이스

## 프로젝트 개요
KRX 시장 데이터, DART 공시 데이터, 재무지표를 결합한 한국 주식시장 분석 및 포트폴리오 관리 도구. 가치투자 전략에 기반한 멀티 워크스페이스 모노레포 구조로 3개의 통합 파이썬 패키지 포함.

## 아키텍처 & 데이터 흐름

### 핵심 모듈
- **`my/`** - 메인 분석 로직 (크롤링, 평가, 백테스트 진입점)
- **`pykrx/`** - 한국거래소 API 래퍼 (로컬 포크)
- **`dart-fss/`** - DART 공시 데이터 읽기 (로컬 포크)
- **`marcap/`** - 시가총액 데이터 제공 (로컬 포크)
- **`FinanceDataReader/`** - 주식 상장정보 & 재무데이터 (로컬 포크)

### 데이터 파이프라인
```
KRX 시장 데이터 (pykrx)
    ↓
시가총액 (marcap_data)
    ↓
크롤링 (my.crawling_v2.Crawling) → 다중 웹 스크래퍼
    ↓
평가 (my.rating) → 종목 필터링 & 점수 계산
    ↓
백테스트 (my.backtest) → 포트폴리오 성과 시뮬레이션
```

## 주요 워크플로우

### 분석 실행 (CLI 진입점)
모두 Python 모듈 `-m` 옵션으로 실행 가능:

```bash
# 주요 워크플로우 - 기업 재무데이터 크롤링 (~5분 소요)
$ python -m my.crawling_v2 --quarter=2022/03  # yyyy/mm 형식

# 종목 평가 & 필터링
$ python -m my.rating --name={결과엑셀파일}  # my/download/ 폴더에서 읽음

# 통합 테스트
$ python -m my.test_pykrx_n_marcap    # KRX + 시가총액
$ python -m my.test_fnguide           # FnGuide 스크래퍼  
$ python -m my.test_dart_fss          # DART 공시 읽기
```

## 핵심 패턴

### 데이터 조회
- **KRX 데이터**: `from pykrx import stock; stock.get_market_cap(date_string)` 사용
- **시가총액**: `from marcap import marcap_data; marcap_data('YYYY-MM-DD')`
- **영업일 처리**: `stock.get_nearest_business_day_in_a_week()`는 'YYYYMMDD' 문자열 반환
- **날짜 형식 통일**: KRX 'YYYYMMDD' 형식은 `datetime.strptime()`으로 파싱

### DataFrame 작업
- **컬럼명 변환** ([crawling_v2.py](my/crawling_v2.py#L47-L53) 참고):
  - KRX: '티커'→'Code', '종목명'→'Name', '시가총액'→'Marcap'
  - 항상 조회 시점에 변환하여 일관성 유지
- **Excel I/O**: .xlsx 파일은 `openpyxl` 사용 ([rating.py](my/rating.py#L23) 참고)
- **종목 코드**: `'{:06d}'.format(code)`로 6자리 문자열 포맷팅

### 스레딩 & 웹 스크래핑
- `my.worker.Worker` - 병렬 데이터 수집용 스레딩
- `my.naver.Naver` 클래스 - FnGuide HTML 스크래핑 (`urlopen`, `pd.read_html` 사용)
- `my.static.make_dataframe()` - GET 요청으로 재무표 파싱
- **속도 제한**: WAIT_TIME = 0.01 (서버 블로킹 방지)

### 필터 체인 (재무지표)
1. **섹터 필터링** ([rating.py](my/rating.py#L44) 참고):
   - 중국주, SPAC 제외: `~startswith('9')`, `~contains('SPAC')`
   - KRX 상장정보와 병합하여 섹터/산업 데이터 추가
2. **밸류에이션 필터**:
   - PER, PBR, 배당수익률 = FnGuide에서 계산
   - 극단값 처리 (PER<1, PBR<0.3은 부실기업 신호)

## 설정 패턴
- **Options 클래스** (optparse): `crawling_v2`, `rating`, `fnguide`에서 표준화
- **분기 형식**: "YYYY/MM" (예: "2022/03")
- **빈도 파라미터**: `frq`는 분기/연간 ('3', '4', '12')
- **기준 로직**: `base='target'`이면 분기 첫날부터 역으로, 아니면 오늘 기준

## 연동 지점
- **pykrx 임포트**: `pykrx.website.krx`에서 날짜 변환 유틸리티 사용
- **pandas merge**: KRX 데이터와 크롤링 데이터 결합시 `how='left'` 사용
- **FinanceDataReader**: 상장정보 조회 - `fdr.StockListing('KRX')`는 ['Code', 'Sector', 'Industry'] 반환
- **DART 파일**: `dart_fss.Open()` API로 공시 메타데이터 조회 ([test_dart_fss.py](my/test_dart_fss.py) 참고)

## 일반적인 문제 & 해결법
- **날짜 형식 충돌**: KRX는 'YYYYMMDD', pandas는 'YYYY-MM-DD' - 즉시 변환 필수
- **영업일 데이터 누락**: `len(result) > 0`까지 반복하며 역으로 조회 ([static.py](my/static.py#L32-L37) 참고)
- **인코딩 문제**: 파일 헤더에 `# -*- coding: utf-8 -*-` 필수 (한글 텍스트 사용)
- **모듈 임포트**: `my/` 내부에서 상대 임포트 사용 (예: crawling_v2에서 `import my.static`)

## 테스트 & 검증
- `my/test_*.py` 파일들은 빠른 통합 테스트 (단위 테스트 아님)
- `-m` 플래그로 실행하여 모듈 경로 올바르게 설정
- 결과 Excel 파일은 `my/download/` 폴더에 저장됨

## 더 이상 사용하지 않는 패턴
- **구버전 API**: `get_firm_data_v3()`은 `marcap_data()` 사용, 신규 코드는 `pykrx.stock.get_market_cap()` 사용 (README의 TODO 참고)
- `crawling.py`는 `crawling_v2.py`로 대체됨 (스레딩 개선)
- FnGuide 직접 HTML 스크래핑은 pykrx API로 전환 예정
