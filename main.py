import time
import pyupbit
from api import get_balance, get_price, upbit
from trade import buy_market, sell_market

# =========================
# 🔥 전략 설정
# =========================
BUY_RSI = 30
SELL_RSI = 70

TAKE_PROFIT_RATE = 1.02   # ✅ 2% 익절
STOP_LOSS_RATE = 0.98     # 2% 손절

IGNORE_COINS = ["KRW-VTHO", "KRW-APENFT"]


# =========================
# 📊 RSI 계산 함수
# =========================
def get_rsi(ticker):
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute1", count=50)

        if df is None or len(df) < 14:
            return None

        delta = df['close'].diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)

        avg_up = up.rolling(14).mean()
        avg_down = down.rolling(14).mean()

        rs = avg_up / avg_down
        rsi = 100 - (100 / (1 + rs))

        value = rsi.iloc[-1]

        if value != value:  # NaN 체크
            return None

        return float(value)

    except:
        return None


# =========================
# 💰 수익 계산 함수
# =========================
def calculate_profit(buy_price, current_price, volume):
    profit = (current_price - buy_price) * volume
    rate = (current_price / buy_price - 1) * 100
    return profit, rate


# =========================
# 🖨️ 결과 출력 함수
# =========================
def print_trade_result(title, profit, rate):
    print(f"=== {title} === 수익: {profit:.2f}원 ({rate:.2f}%)")


# =========================
# 🧠 현재 보유 코인 (avg_buy_price 포함)
# =========================
def get_my_coin():
    balances = upbit.get_balances()

    for b in balances:
        coin = f"KRW-{b['currency']}"
        balance = float(b['balance'])

        if coin in IGNORE_COINS:
            continue

        if b['currency'] != 'KRW' and balance > 0:
            avg_price = float(b['avg_buy_price'])
            return coin, balance, avg_price

    return None, 0, 0


# =========================
# 🧠 가장 RSI 낮은 코인 선택
# =========================
def get_best_coin():
    coins = pyupbit.get_tickers(fiat="KRW")
    coins = coins[:10]  # 상위 10개만

    best_coin = None
    best_rsi = 100

    for coin in coins:
        rsi = get_rsi(coin)

        if rsi is None:
            continue

        print(f"{coin} RSI: {rsi:.2f}")

        if rsi < best_rsi:
            best_rsi = rsi
            best_coin = coin

        time.sleep(0.2)

    return best_coin, best_rsi


# =========================
# 🚀 메인 로직
# =========================
def main():
    try:
        krw = get_balance("KRW")
        my_coin, volume, avg_price = get_my_coin()

        best_coin, best_rsi = get_best_coin()

        print("\n==========================")

        # 🔥 상태 출력 (손익 포함)
        if my_coin:
            current_price = get_price(my_coin)
            profit, rate = calculate_profit(avg_price, current_price, volume)

            print(
                f"KRW: {krw:.0f} / 보유코인: {my_coin} / "
                f"현재가: {current_price:.0f} / "
                f"평가손익: {profit:.2f}원 ({rate:.2f}%)"
            )
        else:
            print(f"KRW: {krw:.0f} / 보유코인: 없음")

        print(f"🔥 선택 코인: {best_coin} / RSI: {best_rsi}")
        print("==========================\n")

        # =========================
        # 📌 매수
        # =========================
        if my_coin is None:
            if best_coin and best_rsi < BUY_RSI and krw >= 5000:
                print("=== 매수 실행 ===")
                buy_market(best_coin, krw * 0.999)

        # =========================
        # 📌 매도
        # =========================
        else:
            price = get_price(my_coin)
            rsi = get_rsi(my_coin)

            profit, rate = calculate_profit(avg_price, price, volume)

            # ✅ 익절 (2%)
            if price >= avg_price * TAKE_PROFIT_RATE:
                print_trade_result("익절", profit, rate)
                sell_market(my_coin, volume)

            # ✅ 손절 (-2%)
            elif price <= avg_price * STOP_LOSS_RATE:
                print_trade_result("손절", profit, rate)
                sell_market(my_coin, volume)

            # ✅ RSI 매도
            elif rsi is not None and rsi > SELL_RSI:
                print_trade_result("RSI 매도", profit, rate)
                sell_market(my_coin, volume)

    except Exception as e:
        print("에러:", e)


# =========================
# 🔁 자동 실행
# =========================
if __name__ == "__main__":
    while True:
        main()
        time.sleep(60)