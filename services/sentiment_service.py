class SentimentService:

    POSITIVE = [

        "rate cut",
        "cooling inflation",
        "bullish",
        "rally",
        "growth",
        "strong earnings",
        "recovery",
        "record high",
        "surge",
        "gain",
        "up",
        "positive"

    ]

    NEGATIVE = [

        "rate hike",
        "recession",
        "bearish",
        "war",
        "inflation",
        "selloff",
        "crash",
        "collapse",
        "decline",
        "down",
        "negative",
        "fear"

    ]

    def analyze(self, title):

        text = title.lower()

        positive = 0
        negative = 0

        for word in self.POSITIVE:

            if word in text:
                positive += 1

        for word in self.NEGATIVE:

            if word in text:
                negative += 1

        if positive > negative:

            return {

                "sentiment": "POSITIVE",

                "score": positive-negative

            }

        elif negative > positive:

            return {

                "sentiment": "NEGATIVE",

                "score": negative-positive

            }

        return {

            "sentiment": "NEUTRAL",

            "score":0

        }
