from api import upbit

def buy_market(ticker, amount):
    return upbit.buy_market_order(ticker, amount)

def sell_market(ticker, volume):
    return upbit.sell_market_order(ticker, volume)

