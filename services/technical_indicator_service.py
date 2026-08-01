import pandas as pd


class TechnicalIndicatorService:

    @staticmethod
    def calculate(data: pd.DataFrame):

        if data.empty:
            return None

        df = data.copy()

        close = df["Close"]

        # Moving averages
        df["SMA5"] = close.rolling(window=5).mean()
        df["SMA20"] = close.rolling(window=20).mean()
        df["SMA50"] = close.rolling(window=50).mean()

        # Exponential Moving Average
        df["EMA20"] = close.ewm(span=20, adjust=False).mean()

        # Daily return
        df["Return"] = close.pct_change()

        # Volatility (annualized)
        volatility = (
            df["Return"].std() * (252 ** 0.5) * 100
        )

        # RSI (14)
        delta = close.diff()

        gain = delta.where(delta > 0, 0)

        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(14).mean()

        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss

        rsi = 100 - (100 / (1 + rs))

        latest = df.iloc[-1]

        latest_price = float(latest["Close"])

        sma5 = latest["SMA5"]
        sma20 = latest["SMA20"]
        sma50 = latest["SMA50"]
        ema20 = latest["EMA20"]

        latest_rsi = rsi.iloc[-1]

        if pd.isna(sma5):
            sma5 = latest_price

        if pd.isna(sma20):
            sma20 = latest_price

        if pd.isna(sma50):
            sma50 = latest_price

        if pd.isna(ema20):
            ema20 = latest_price

        if pd.isna(latest_rsi):
            latest_rsi = 50

        trend = "SIDEWAYS"

        if latest_price > sma20:
            trend = "BULLISH"

        elif latest_price < sma20:
            trend = "BEARISH"

        signal = "HOLD"

        if trend == "BULLISH" and latest_rsi < 70:
            signal = "BUY WATCH"

        elif trend == "BEARISH" and latest_rsi > 30:
            signal = "SELL WATCH"

        return {

            "price": round(latest_price, 2),

            "sma5": round(float(sma5), 2),

            "sma20": round(float(sma20), 2),

            "sma50": round(float(sma50), 2),

            "ema20": round(float(ema20), 2),

            "rsi": round(float(latest_rsi), 2),

            "volatility": round(float(volatility), 2),

            "trend": trend,

            "signal": signal

        }
