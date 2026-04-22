import pyupbit
from dotenv import load_dotenv
import os

load_dotenv()

access = os.getenv("ACCESS")
secret = os.getenv("SECRET")

# upbit API 연결
upbit = pyupbit.Upbit(access, secret)


# 비트코인 가격 조회
def get_price(ticker):
  return pyupbit.get_current_price(ticker)

# 내 상태 조회
def get_balance(current):
  return upbit.get_balance(current)

#가격 보기좋게 설정
def get_simple_pay(price):
  return f"{price:,.}원"
