import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from pybit import HTTP
import pandas as pd

# 1️⃣ 載入環境變數
load_dotenv()
api_key = os.getenv("BYBIT_API_KEY")
api_secret = os.getenv("BYBIT_API_SECRET")

# 2️⃣ 初始化 Bybit Session（live 環境）
session = HTTP(
    endpoint="https://api.bybit.com",
    api_key=api_key,
    api_secret=api_secret
)

# 3️⃣ 取得合約列表（線性合約）
def get_contract_symbols():
    result = session.query_symbol()
    return [item["name"] for item in result["result"]]

# 4️⃣ 取得歷史 K 線（1 小時）
def get_ohlcv(symbol):
    result = session.kline(symbol=symbol, interval="60", limit=100)
    df = pd.DataFrame(result["result"])
    df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df = df.astype(float)
    return df

# 5️⃣ 簡單分析邏輯：volume 大於平均 + 價格高於前一根
def analyze(df):
    volume = df["volume"]
    close = df["close"]

    latest_vol = volume.iloc[-1]
    avg_vol = volume.mean()
    latest_price = close.iloc[-1]
    prev_price = close.iloc[-2]

    met = latest_vol > avg_vol and latest_price > prev_price

    return met, {
        "price": round(latest_price, 4),
        "volume": round(latest_vol, 2),
        "avg_volume": round(avg_vol, 2)
    }

# 6️⃣ 建立 Flask API
app = Flask(__name__)

@app.route("/signal", methods=["GET"])
def get_signal():
    matches = []
    symbols = get_contract_symbols()

    for symbol in symbols[:10]:  # 測試階段先抓前10個
        try:
            df = get_ohlcv(symbol)
            met, details = analyze(df)
            if met:
                matches.append({
                    "symbol": symbol,
                    "details": details
                })
        except Exception as e:
            print(f"❌ {symbol} error: {e}")
    
    return jsonify({
        "matches": matches,
        "count": len(matches)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
