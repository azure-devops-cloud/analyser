class AgentContext:
    """Shared run state and auditable evidence ledger."""

    def __init__(self):
        self.news = []
        self.market = []
        self.decisions = []
        self.calendar = []
        self.errors = []
        self.news_sentiment = {}
        self.fact_validation = {}
        self.source_trust_map = {}
        self.alerts = []
        self.history = {}
        self.execution = {}
        self.technical_analysis = []
        self.confidence = {}
        self.risk = {}
        self.evidence = []

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

    def add_news_sentiment(self, data):
        self.news_sentiment = data

    def add_fact_validation(self, data):
        self.fact_validation = data

    def add_source_trust_map(self, data):
        self.source_trust_map = data

    def add_alerts(self, alerts):
        self.alerts = alerts

    def add_history(self, history):
        self.history = history

    def add_execution(self, execution):
        self.execution = execution

    def add_technical_analysis(self, analysis):
        self.technical_analysis = analysis

    def add_confidence(self, confidence):
        self.confidence = confidence

    def add_risk(self, risk):
        self.risk = risk

    def add_evidence(self, evidence):
        """Append auditable evidence records to the current run."""
        if not evidence:
            return
        self.evidence.extend(evidence)
