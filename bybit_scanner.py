import os
from pybit.unified_trading import HTTP
from dotenv import load_dotenv
import pandas as pd
import talib

# 載入 API 金鑰
load_dotenv()
api_key = os.getenv("BYBIT_API_KEY")
api_secret = os.getenv("BYBIT_API_SECRET")

# 初始化 Bybit API
session = HTTP(
    testnet=False,
    api_key=api_key,
    api_secret=api_secret
)

# 取得所有 USDT 合約代號
def get_contract_symbols():
    result = session.get_instruments_info(category="linear")
    return [item["symbol"] for item in result["result"]["list"]]

# 取得歷史 K 線資料（1 小時）
def get_ohlcv(symbol):
    result = session.get_kline(
        category="linear",
        symbol=symbol,
        interval=60,
        limit=100
    )
    df = pd.DataFrame(result['result']['list'], columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
    ])
    df['close'] = df['close'].astype(float)
    return df

# 計算 RSI 和 MACD
def analyze_technicals(df):
    close = df['close']
    rsi = talib.RSI(close, timeperiod=14)
    macd, signal, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    return rsi.iloc[-1], macd.iloc[-1], signal.iloc[-1]

# 主程式
if __name__ == "__main__":
    symbols = get_contract_symbols()
    print("✅ 找到合約數量:", len(symbols))

    for symbol in symbols[:5]:  # 測試前5個
        df = get_ohlcv(symbol)
        rsi, macd, signal = analyze_technicals(df)
        print(f"📊 {symbol} | RSI: {rsi:.2f}, MACD: {macd:.2f}, Signal: {signal:.2f}")

