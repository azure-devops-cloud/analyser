import yfinance as yf

from services.logger import get_logger


logger = get_logger(__name__)


class MarketService:

    SYMBOLS = {
        "GOLD": "GC=F",
        "BITCOIN": "BTC-USD",
        "S&P500": "^GSPC",
        "NASDAQ": "^IXIC",
        "USD_INR": "INR=X",
        "CRUDE_OIL": "CL=F"
    }

    def get_market_data(self):

        results = []

        for name, symbol in self.SYMBOLS.items():

            try:

                ticker = yf.Ticker(symbol)

                data = ticker.history(
                    period="5d",
                    auto_adjust=False
                )

                if data.empty:

                    logger.warning(f"{name}: No data returned")

                    continue

                latest = data.iloc[-1]

                price = round(float(latest["Close"]), 2)

                if len(data) >= 2:

                    previous = float(data.iloc[-2]["Close"])

                    if previous != 0:

                        change = round(
                            ((price - previous) / previous) * 100,
                            2
                        )

                    else:

                        change = 0.0

                else:

                    change = 0.0

                results.append(
                    {
                        "name": name,
                        "symbol": symbol,
                        "price": price,
                        "change": change
                    }
                )

            except Exception as error:

                logger.error(f"{name}: {error}")

        return results
