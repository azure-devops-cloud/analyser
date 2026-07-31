from agents.news_agent import NewsAgent


class ManagerAgent:


    def __init__(self):

        self.agents = [
            NewsAgent()
        ]


    def run(self):

        results = []

        for agent in self.agents:

            result = agent.run()

            results.append(result)


        return results
