class DecisionService:

    def analyze(self, market):

        score = 50

        reasons = []

        # Trend
        trend = market.get("trend", "SIDEWAYS")

        if trend == "BULLISH":
            score += 20
            reasons.append("Trading above SMA20")

        elif trend == "BEARISH":
            score -= 20
            reasons.append("Trading below SMA20")

        # RSI
        rsi = market.get("rsi", 50)

        if rsi < 30:
            score += 15
            reasons.append("Oversold (RSI)")

        elif rsi > 70:
            score -= 15
            reasons.append("Overbought (RSI)")

        else:
            reasons.append("RSI is neutral")

        # Daily Change
        daily = market.get("daily_change", 0)

        if daily > 1:
            score += 10
            reasons.append("Positive daily momentum")

        elif daily < -1:
            score -= 10
            reasons.append("Negative daily momentum")

        # Volatility
        volatility = market.get("volatility", 20)

        if volatility > 40:
            score -= 5
            reasons.append("High volatility")

        score = max(0, min(score, 100))

        if score >= 70:
            bias = "BULLISH"

        elif score <= 35:
            bias = "BEARISH"

        else:
            bias = "NEUTRAL"

        if score >= 80:
            confidence = "HIGH"

        elif score >= 60:
            confidence = "MEDIUM"

        else:
            confidence = "LOW"

        return {

            "name": market["name"],

            "price": market["price"],

            "bias": bias,

            "confidence": confidence,

            "score": score,

            "trend": trend,

            "signal": market["signal"],

            "daily_change": daily,

            "rsi": rsi,

            "reasons": reasons

        }
