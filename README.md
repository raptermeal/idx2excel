# 주요 국가 주가 및 환율 데이터 수집기

이 프로젝트는 `Yahoo Finance`와 `Naver 금융` 데이터를 활용하여 주요 국가의 주가 및 환율 정보를 수집하고, 이를 엑셀 파일로 저장하는 Python 스크립트입니다.

## 주요 기능
- meta_index.csv 파일에 정의된 항목을 기반으로 자동 수집
- yfinance (주가), naver (환율) 크롤링 지원
- 엑셀 템플릿을 기반으로 데이터 기록
- PyInstaller를 통해 .exe 파일로 패키징 가능

## 폴더 구조
- get_idx.py : 메인 스크립트
- data/meta_index.csv : 수집 대상 목록
- data/idx_temp_*.xlsx : 엑셀 템플릿
- result/ : 수집 결과 저장 폴더

## 실행 방법
1. 패키지 설치
`pip install -r requirements.txt`
2. 스크립트 실행
`python get_idx.py`

## .exe 파일 생성 방법
1. PyInstaller 설치
`pip install pyinstaller`
2. 실행 파일 만들기
`pyinstaller --onefile --distpath . --workpath ./build --specpath . get_idx.py`

생성된 실행 파일은 dist/ 폴더에 저장됩니다.

## 참고사항
- meta_index.csv의 출처는 yfinance 또는 naver로 설정
- 결과는 result/keyidx_YYMMDD.xlsx로 저장됨