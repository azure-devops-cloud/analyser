from services.database_service import DatabaseService
from services.telegram_service import send_message
from services.logger import get_logger

from agents.manager_agent import ManagerAgent


logger = get_logger()


def main():

    logger.info(
        "Starting MarketMind AI"
    )


    db = DatabaseService()

    db.initialize()


    tables = db.health_check()


    manager = ManagerAgent()

    results = manager.run()



    message = [
        "🚀 MarketMind AI",
        "",
        "News Update",
        ""
    ]


    for result in results:

        if result.status == "success":
    
            checked = result.data["total_checked"]
    
            message.append(
                f"✅ {result.agent}"
            )
    
            message.append(
                f"Checked: {checked}"
            )
    
            message.append(
                f"New: {result.count}"
            )
    
        else:
    
            message.append(
                f"❌ {result.agent} failed"
            )



    message.extend(
        [
            "",
            f"Database tables: {len(tables)}",
            "",
            "Status: Healthy ✅"
        ]
    )


    send_message(
        "\n".join(message)
    )


    db.close()


    logger.info(
        "Completed"
    )



if __name__ == "__main__":
    main()
