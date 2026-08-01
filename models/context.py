class AgentContext:

    def __init__(self):

        self.news = []

        self.market = []

        self.decisions = []

        self.calendar = []

        self.errors = []
        
        self.news_sentiment={}

    def add_news(self, news):

        self.news = news

    def add_market(self, market):

        self.market = market

    def add_decisions(self, decisions):

        self.decisions = decisions

    def add_calendar(self, calendar):

        self.calendar = calendar

    def add_error(self, error):

        self.errors.append(error)

    def add_news_sentiment(self,data):

    self.news_sentiment=data
