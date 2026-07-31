from collections import Counter


class NewsAnalysisService:


    def analyze(self, articles):

        category_count = Counter()

        impact_count = Counter()


        for article in articles:

            category = article.get(
                "category",
                "GENERAL"
            )

            impact = article.get(
                "impact",
                "LOW"
            )


            category_count[category] += 1

            impact_count[impact] += 1



        return {

            "categories": dict(category_count),

            "impact": dict(impact_count)

        }
