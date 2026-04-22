import pyupbit
import api

# upbit API 연결
upbit = pyupbit.Upbit(api.access, api.secret)


# 비트코인 가격 조회
price = pyupbit.get_current_price("KRW-BTC")

# 내 잔고 조회
balance = upbit.get_balance("KRW")

#가격 보기좋게 설정
def get_price(price):
  return f"{price:,.0f}원"

print(get_price(balance))
print(get_price(price))


