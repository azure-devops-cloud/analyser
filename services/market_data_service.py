import yfinance as yf

from services.logger import get_logger
from services.technical_indicator_service import TechnicalIndicatorService


logger = get_logger(__name__)


class MarketService:

    SYMBOLS = {
        "GOLD": "GC=F",
        "BITCOIN": "BTC-USD",
        "ETHEREUM": "ETH-USD",
        "S&P500": "^GSPC",
        "NASDAQ": "^IXIC",
        "USD_INR": "INR=X",
        "CRUDE_OIL": "CL=F"
    }

    def get_market_data(self):

        results = []

        for name, symbol in self.SYMBOLS.items():

            try:

                logger.info(f"Fetching {name}")

                ticker = yf.Ticker(symbol)

                data = ticker.history(
                    period="3mo",
                    interval="1d",
                    auto_adjust=False
                )

                if data.empty:

                    logger.warning(f"{name}: No data")

                    continue

                indicators = TechnicalIndicatorService.calculate(data)

                if indicators is None:
                    continue

                latest = data.iloc[-1]
                previous = data.iloc[-2]

                daily_change = round(
                    (
                        (latest["Close"] - previous["Close"])
                        / previous["Close"]
                    ) * 100,
                    2
                )

                indicators["name"] = name
                indicators["symbol"] = symbol
                indicators["daily_change"] = daily_change

                results.append(indicators)

                logger.info(
                    f"{name} | "
                    f"{indicators['price']} | "
                    f"{indicators['trend']}"
                )

            except Exception as ex:

                logger.exception(
                    f"{name}: {str(ex)}"
                )

        logger.info(
            f"Collected {len(results)} market instruments"
        )

        return results
