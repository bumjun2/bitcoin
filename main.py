import time
import pyupbit
import os
from datetime import datetime, timedelta

from api import get_balance, get_price, upbit
from trade import buy_market, sell_market


# =========================
# 🔧 설정
# =========================
TAKE_PROFIT_RATE = 1.02
STOP_LOSS_RATE = 0.98

last_buy_price = None
last_coin = None


# =========================
# 📝 로그 저장
# =========================
def write_log(msg, strategy="A"):
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    os.makedirs("logs", exist_ok=True)

    with open(f"logs/{today}.log", "a", encoding="utf-8") as f:
        f.write(f"[{now}] {msg} | strategy:{strategy}\n")


# =========================
# 📊 로그 로딩 (N일)
# =========================
def load_logs(days):

    logs = []

    for i in range(days):

        day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        path = f"logs/{day}.log"

        if not os.path.exists(path):
            continue

        with open(path, "r", encoding="utf-8") as f:
            logs += f.readlines()

    return logs


# =========================
# 📊 로그 분석
# =========================
def analyze(lines):

    pnl = {"A": 0, "B": 0, "C": 0}

    for line in lines:

        if "strategy:A" in line:
            pnl["A"] += 1
        elif "strategy:B" in line:
            pnl["B"] += 1
        elif "strategy:C" in line:
            pnl["C"] += 1

    return pnl


# =========================
# 🧠 전략 선택 (핵심 개선)
# =========================
def pick_best_strategy():

    logs30 = load_logs(30)
    count = len(logs30)

    print(f"📊 총 로그 수: {count}")

    # 🔥 1단계: 초기 (거래 거의 없음)
    if count < 5:
        print("⚠️ 초기 단계 → 전략 B")
        return "B"

    # 🔥 2단계: 중간 (누적 기준)
    elif count < 20:
        pnl = analyze(logs30)
        print("📊 누적 전략 성과:", pnl)
        return max(pnl, key=pnl.get)

    # 🔥 3단계: 안정 (최근 7일)
    else:
        logs7 = load_logs(7)
        pnl = analyze(logs7)
        print("📊 최근 7일 전략 성과:", pnl)
        return max(pnl, key=pnl.get)


# =========================
# 📊 RSI
# =========================
def get_rsi(df):

    delta = df['close'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)

    rs = up.rolling(14).mean() / down.rolling(14).mean()
    rsi = 100 - (100 / (1 + rs))

    val = rsi.iloc[-1]

    if val != val:
        return None

    return float(val)


# =========================
# 📈 추세
# =========================
def is_uptrend(df):
    return df['close'].rolling(5).mean().iloc[-1] > df['close'].rolling(20).mean().iloc[-1]


# =========================
# 📊 거래량
# =========================
def volume_ok(df):
    return df['volume'].iloc[-1] > df['volume'].mean() * 1.5


# =========================
# 🟣 전략 A (RSI)
# =========================
def strategy_a(df):
    rsi = get_rsi(df)
    return rsi is not None and rsi < 30


# =========================
# 🟡 전략 B (Momentum)
# =========================
def strategy_b(df):

    rsi = get_rsi(df)

    price_now = df['close'].iloc[-1]
    price_prev = df['close'].iloc[-3]

    momentum = price_now > price_prev

    return rsi is not None and rsi < 60 and momentum


# =========================
# 🟢 전략 C (Breakout)
# =========================
def strategy_c(df):

    rsi = get_rsi(df)

    high_20 = df['high'].rolling(20).max().iloc[-2]
    price = df['close'].iloc[-1]

    return (
        rsi is not None and
        rsi < 70 and
        price > high_20 and
        volume_ok(df)
    )


# =========================
# 📊 거래량 TOP20
# =========================
def get_top_coins():

    coins = pyupbit.get_tickers(fiat="KRW")
    result = []

    for c in coins:
        try:
            df = pyupbit.get_ohlcv(c, "minute1", 1)
            if df is None:
                continue

            result.append((c, df['volume'].iloc[-1]))

        except:
            continue

    result.sort(key=lambda x: x[1], reverse=True)

    return [x[0] for x in result[:20]]


# =========================
# 🧠 코인 선택
# =========================
def select_coin(strategy):

    coins = get_top_coins()

    for coin in coins:

        df = pyupbit.get_ohlcv(coin, "minute1", 50)

        if df is None:
            continue

        if strategy == "A" and strategy_a(df):
            return coin

        if strategy == "B" and strategy_b(df):
            return coin

        if strategy == "C" and strategy_c(df):
            return coin

    return None


# =========================
# 🚀 MAIN
# =========================
def main():

    global last_buy_price, last_coin

    krw = get_balance("KRW")

    best_strategy = pick_best_strategy()
    print(f"🔥 BEST 전략: {best_strategy}")

    coin = select_coin(best_strategy)
    print(f"🔥 선택 코인: {coin}")

    # =========================
    # 📌 매수
    # =========================
    if last_coin is None:

        if coin and krw > 5000:

            price = get_price(coin)

            buy_market(coin, krw * 0.999)

            last_buy_price = price
            last_coin = coin

            write_log(f"매수 | {coin} | {price}", best_strategy)

    # =========================
    # 📌 매도
    # =========================
    else:

        price = get_price(last_coin)
        profit_rate = price / last_buy_price

        if profit_rate >= TAKE_PROFIT_RATE:
            sell_market(last_coin, krw)
            write_log(f"익절 | {last_coin} | {profit_rate:.3f}", best_strategy)
            last_coin = None

        elif profit_rate <= STOP_LOSS_RATE:
            sell_market(last_coin, krw)
            write_log(f"손절 | {last_coin} | {profit_rate:.3f}", best_strategy)
            last_coin = None


# =========================
# 🔁 실행
# =========================
if __name__ == "__main__":
    while True:
        main()
        time.sleep(60)