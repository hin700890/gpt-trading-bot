import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from bybit.unified_trading import HTTP
import pandas as pd
import talib

# 1️⃣ 環境變數
load_dotenv()
api_key = os.getenv("BYBIT_API_KEY")
api_secret = os.getenv("BYBIT_API_SECRET")

# 2️⃣ Bybit 初始化
session = HTTP(
    testnet=False,
    api_key=api_key,
    api_secret=api_secret
)

# 3️⃣ 獲取所有 USDT 合約幣種
def get_contract_symbols():
    result = session.get_instruments_info(category="linear")
    return [item["symbol"] for item in result["result"]["list"]]

# 4️⃣ 取得歷史 K 線（1 小時）
def get_ohlcv(symbol):
    result = session.get_kline(
        category="linear",
        symbol=symbol,
        interval="60",
        limit=100
    )
    df = pd.DataFrame(result["result"]["list"])
    df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
    df = df.astype(float)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df.sort_values("timestamp")
    return df

# 5️⃣ 技術分析邏輯（RSI、MACD、MA20、Volume）
def analyze(df):
    close = df["close"]
    volume = df["volume"]

    rsi = talib.RSI(close, timeperiod=14)
    macd, signal, _ = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    ma20 = talib.MA(close, timeperiod=20)

    latest_rsi = rsi.iloc[-1]
    latest_macd = macd.iloc[-1]
    latest_signal = signal.iloc[-1]
    latest_price = close.iloc[-1]
    latest_ma20 = ma20.iloc[-1]
    latest_vol = volume.iloc[-1]
    avg_vol = volume.mean()

    signal_met = (
        latest_rsi < 30 and
        latest_macd > latest_signal and
        latest_price > latest_ma20 and
        latest_vol > avg_vol
    )

    return signal_met, {
        "price": round(latest_price, 4),
        "rsi": round(latest_rsi, 2),
        "macd": round(latest_macd, 4),
        "signal": round(latest_signal, 4),
        "ma20": round(latest_ma20, 4),
        "volume": round(latest_vol, 0)
    }

# 6️⃣ Flask API 建立
app = Flask(__name__)

@app.route("/signal", methods=["GET"])
def get_signal():
    matches = []
    symbols = get_contract_symbols()

    for symbol in symbols[:10]:  # ⚠️ 測試階段先掃前10個
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
