import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import os
import shutil
from openpyxl import load_workbook

# ✅ 날짜 설정
today = datetime.today()
start_date = today - timedelta(days=365)
period1 = int(start_date.timestamp())
period2 = int(today.timestamp())
date_str = today.strftime("%y%m%d")

# ✅ 경로 설정
meta_path = "./data/meta_index.csv"
template_path = "./data/idx_temp_250502.xlsx"
# template_path = "./data/test.xlsx"

result_dir = "./result"
output_path = f"{result_dir}/keyidx_{date_str}.xlsx"
sheet_name = "table"
os.makedirs(result_dir, exist_ok=True)

# ✅ 메타파일 로딩
index_list = []
with open(meta_path, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        index_list.append((row["국가"], row["구분"], row["단위"], row["티커"], row["출처"]))

# ✅ 결과 초기화
result_rows = [["인덱스", "국가", "구분", "단위", "날짜", "값", "출처"]]

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://finance.yahoo.com/"
}

# ✅ 데이터 수집
for country, gubun, name, ticker, source in index_list:
    try:
        if source == "yfinance":
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            params = {
                "symbol": ticker,
                "interval": "1d",
                "period1": period1,
                "period2": period2,
                "includeAdjustedClose": "true",
                "events": "capitalGain|div|split",
                "formatted": "true",
                "lang": "en-US",
                "region": "US"
            }
            res = requests.get(url, params=params, headers=headers)
            data = res.json()
            result = data["chart"]["result"][0]
            timestamps = result["timestamp"]
            closes = result["indicators"]["quote"][0]["close"]

            for ts, close in zip(timestamps, closes):
                if close is None:
                    continue
                date_fmt = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
                index_val = f"{name}_{date_fmt}"
                result_rows.append([index_val, country, gubun, name, date_fmt, close, source])
            print(f"📡 {name} URL: {res.url}")

        elif source == "naver":
            if country == "한국":
                url = f"https://finance.naver.com/marketindex/exchangeDailyQuote.naver?marketindexCd={ticker}&page=1&pageSize=500"
            else:
                url = f"https://finance.naver.com/marketindex/worldDailyQuote.naver?fdtc=4&marketindexCd={ticker}&page=1&pageSize=500"

            print(f"📡 {name} URL: {url}")
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            table = soup.select_one("table.tbl_exchange")
            if not table:
                continue

            for row in table.select("tbody > tr"):
                cols = row.select("td")
                if len(cols) < 2:
                    continue
                try:
                    date_fmt = datetime.strptime(cols[0].text.strip(), "%Y.%m.%d").strftime("%Y-%m-%d")
                    close_val = float(cols[1].text.strip().replace(",", ""))
                    index_val = f"{name}_{date_fmt}"
                    result_rows.append([index_val, country, gubun, name, date_fmt, close_val, source])
                except:
                    continue

    except Exception as e:
        print(f"❌ 오류 발생: {name} → {e}")


# ✅ 템플릿 복사 후 기록
shutil.copy(template_path, output_path)
wb = load_workbook(output_path)
if sheet_name not in wb.sheetnames:
    wb.create_sheet(sheet_name)
ws = wb[sheet_name]

# 기존 데이터 삭제
ws.delete_rows(1, ws.max_row)

# 새 데이터 작성 + 날짜 형식 지정
for row_idx, row in enumerate(result_rows, start=1):
    for col_idx, value in enumerate(row, start=1):
        cell = ws.cell(row=row_idx, column=col_idx, value=value)
        if row_idx > 1 and col_idx == 4:  # 날짜열
            cell.number_format = "yyyy-mm-dd"

# 저장
wb.save(output_path)
print(f"\n📄 최종 저장 완료: {output_path} → 시트 '{sheet_name}' ({len(result_rows) - 1}행)")
