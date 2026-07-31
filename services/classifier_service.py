from services.logger import get_logger


logger = get_logger(__name__)


class ClassifierService:


    CATEGORIES = {

        "FED": [
            "fed",
            "fomc",
            "jerome powell",
            "interest rate",
            "inflation",
            "rate hike",
            "rate cut"
        ],


        "GOLD": [
            "gold",
            "bullion",
            "precious metal",
            "xau"
        ],


        "CRYPTO": [
            "bitcoin",
            "btc",
            "ethereum",
            "crypto",
            "blockchain"
        ],


        "INDIA_MARKET": [
            "rbi",
            "nifty",
            "sensex",
            "india stock",
            "indian market"
        ],


        "GLOBAL_MARKET": [
            "s&p",
            "nasdaq",
            "dow jones",
            "oil",
            "dollar",
            "forex"
        ]

    }


    HIGH_IMPACT_WORDS = [

        "rate decision",
        "interest rate",
        "fed meeting",
        "cpi",
        "inflation",
        "recession",
        "crisis",
        "war",
        "default"

    ]


    def classify(self, article):


        text = (

            article.get("title", "")
            + " "
            + article.get("summary", "")

        ).lower()


        category = "GENERAL"

        score = 20


        for name, keywords in self.CATEGORIES.items():

            for keyword in keywords:

                if keyword in text:

                    category = name

                    score += 10

                    break



        for word in self.HIGH_IMPACT_WORDS:

            if word in text:

                score += 15



        if score > 100:

            score = 100



        impact = "LOW"


        if score >= 70:

            impact = "HIGH"

        elif score >= 40:

            impact = "MEDIUM"



        article["category"] = category

        article["impact_score"] = score

        article["impact"] = impact



        return article
