from services.database_service import DatabaseService
from services.telegram_service import send_message
from services.logger import get_logger

from agents.manager_agent import ManagerAgent


logger = get_logger()


def main():

    logger.info(
        "Starting MarketMind AI"
    )


    # Database initialization
    db = DatabaseService()

    db.initialize()

    tables = db.health_check()


    # Run Agents
    manager = ManagerAgent()

    results, context = manager.run()



    message = [

        "🚀 MarketMind AI",

        "",

        "📊 Intelligence Report",

        ""

    ]



    for result in results:


        if result.status != "success":

            message.append(
                f"❌ {result.agent} failed"
            )

            continue



        # News Agent Report

        if result.agent == "news_agent":


            checked = result.data["total_checked"]

            analysis = result.data["analysis"]


            message.append(
                "📰 News Intelligence"
            )


            message.append(
                f"Checked: {checked}"
            )


            message.append(
                f"New: {result.count}"
            )


            message.append("")


            message.append(
                "📂 Categories:"
            )


            for category, count in analysis["categories"].items():

                message.append(
                    f"{category}: {count}"
                )


            message.append("")


            message.append(
                "🔥 Impact:"
            )


            for impact, count in analysis["impact"].items():

                message.append(
                    f"{impact}: {count}"
                )


            message.append("")



        # Market Agent Report

        elif result.agent == "market_agent":


            message.append(
                "📈 Market Data"
            )


            message.append("")


            for item in result.data:


                change = item.get(
                    "daily_change",
                    0
                )


                if change >= 0:

                    icon = "🟢"

                else:

                    icon = "🔴"

                message.append(f"{icon} {item['name']}")
                message.append(f"Price : {item['price']}")
                message.append(f"Daily : {change}%")
                message.append(f"Trend : {item['trend']}")
                message.append(f"Signal: {item['signal']}")
                message.append(f"RSI   : {item['rsi']}")
                message.append("")

                

            message.append("")
            
        # Calendar Agent Report

        elif result.agent == "calendar_agent":
        
            message.append("📅 Economic Calendar")
        
            message.append("")
        
            if len(result.data) == 0:
        
                message.append("No major events found.")
        
                message.append("")
        
            else:
        
                for event in result.data[:5]:    

    message.extend(

        [

            "💾 Database",

            f"Tables: {len(tables)}",

            "",

            "Status: Healthy ✅"

        ]

    )



    telegram_message = "\n".join(
        message
    )


    send_message(
        telegram_message
    )



    db.close()


    logger.info(
        "MarketMind AI completed"
    )



if __name__ == "__main__":

    main()
