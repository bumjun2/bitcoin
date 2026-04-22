from api import upbit

def buy_market(ticker, amount):
    print("===매수 실행~!===")
    return upbit.buy_market_order(ticker, amount)

def sell_market(ticker, volume):
    print("===매수실패~!!===")
    return upbit.sell_market_order(ticker, volume)

