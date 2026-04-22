from trade import buy_market, sell_market
from dotenv import load_dotenv
import api
import os

def main():
  amount = int(os.getenv("BUY_AMOUNT"))
  ticker = os.getenv("TICKER")
  
  #내 잔고 조회
  krw = api.get_balance("KRW")

  if krw > amount:
    buy_market(ticker, amount)
  #내 코인 수량 조회
  btc = api.get_balance("BTC")
  print(btc)

  if btc > 0:
     sell_market("KRW-BTC", btc)


if __name__ == "__main__":
    main()
