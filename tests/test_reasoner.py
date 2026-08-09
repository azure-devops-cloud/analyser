from models.evidence import Evidence
from services.reasoner_service import ReasonerService

def test_reasoner_explains_decision_from_relevant_evidence():
    decision={"name":"GOLD","bias":"BULLISH","score":100,"confidence":"HIGH"}
    evidence=[Evidence("ev-trend","market_data","technical","Trend is BULLISH","BULLISH",0.85,metadata={"asset":"GOLD"}),Evidence("ev-rsi","market_data","technical","RSI is 28",28,0.85,metadata={"asset":"GOLD"}),Evidence("ev-momentum","market_data","momentum","Daily change is 1.8%",1.8,0.8,metadata={"asset":"GOLD"}),Evidence("ev-sentiment","news_sentiment","sentiment","News sentiment",{"positive":8,"negative":2},0.6,metadata={"asset":"GOLD"}),Evidence("ev-other","market_data","technical","Trend is BEARISH","BEARISH",0.85,metadata={"asset":"BTC"})]
    result=ReasonerService().analyze(decision,evidence)
    assert result["asset"]=="GOLD"; assert result["bias"]=="BULLISH"; assert result["score"]==100; assert result["evidence_count"]==4; assert result["stance"]=="supporting"; assert len(result["supporting"])==4; assert not result["opposing"]

def test_reasoner_never_changes_decision_contract():
    decision={"name":"GOLD","bias":"BULLISH","score":100,"confidence":"HIGH"}
    result=ReasonerService().analyze(decision,[])
    assert result["score"]==decision["score"]; assert result["bias"]==decision["bias"]; assert result["confidence"]==decision["confidence"]; assert result["evidence_count"]==0; assert result["stance"]=="weak"
