import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# 接收 TradingView 訊號文字
tv_message = """
RSI is 28, MACD shows a golden cross, volume is increasing. What should we do?
"""

# 交給 GPT 分析
response = client.chat.completions.create(
    model="gpt-4-1106-preview",
    messages=[
        {"role": "system", "content": "You are a crypto trading assistant who gives clear and short trade advice. Only say Buy, Sell, or Hold."},
        {"role": "user", "content": tv_message}
    ]
)

print("📡 TradingView Message:", tv_message)
print("🤖 GPT Advice:", response.choices[0].message.content.strip())
