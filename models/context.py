class AgentContext:

    def __init__(self):

        self.news = []

        self.market = []

        self.decisions = []

        self.calendar = []

        self.errors = []
        
        self.news_sentiment={}

        self.fact_validation = {}

        self.source_trust_map = {}

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

    def add_fact_validation(self, data):

        self.fact_validation = data

    def add_source_trust_map(self, data):

        self.source_trust_map = data
