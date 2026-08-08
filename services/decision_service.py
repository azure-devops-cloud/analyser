class DecisionService:
    """Deterministic decision engine with auditable evidence references."""

    def analyze(self, market, sentiment=None, calendar_events=None, evidence=None):
        score = 50
        reasons = []
        sentiment = sentiment or {}
        calendar_events = calendar_events or []
        evidence = evidence or []

        trend = market.get("trend", "SIDEWAYS")
        if trend == "BULLISH":
            score += 20
            reasons.append("Trading above SMA20")
        elif trend == "BEARISH":
            score -= 20
            reasons.append("Trading below SMA20")

        rsi = market.get("rsi", 50)
        if rsi < 30:
            score += 15
            reasons.append("Oversold (RSI)")
        elif rsi > 70:
            score -= 15
            reasons.append("Overbought (RSI)")
        else:
            reasons.append("RSI is neutral")

        # Preserve the pre-evidence legacy scoring contract.
        daily = market.get("daily_change", 0)
        if daily > 1:
            score += 10
            reasons.append("Positive daily momentum")
        elif daily < -1:
            score -= 10
            reasons.append("Negative daily momentum")

        volatility = market.get("volatility", 20)
        if volatility > 40:
            score -= 5
            reasons.append("High volatility")

        positive = sentiment.get("positive", 0)
        negative = sentiment.get("negative", 0)
        if positive > negative:
            score += 5
            reasons.append("Positive market sentiment")
        elif negative > positive:
            score -= 5
            reasons.append("Negative market sentiment")

        if calendar_events:
            score -= 3
            reasons.append("Major economic events ahead")

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

        evidence_for_asset = [
            item.as_dict() if hasattr(item, "as_dict") else item
            for item in evidence
            if not isinstance(item, dict) or item.get("metadata", {}).get("asset") == market.get("name")
        ]

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
            "reasons": reasons,
            "evidence": {
                "count": len(evidence_for_asset),
                "items": evidence_for_asset,
            },
        }
