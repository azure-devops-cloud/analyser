from services.database_service import DatabaseService
from services.telegram_service import send_message
from services.logger import get_logger

from agents.manager_agent import ManagerAgent


logger = get_logger()


def main():

    logger.info("Starting MarketMind AI")


    # Initialize Database
    db = DatabaseService()

    db.initialize()

    tables = db.health_check()


    logger.info(
        f"Database ready. Tables available: {len(tables)}"
    )


    # Run Agents
    manager = ManagerAgent()

    results = manager.run()


    message_lines = [
        "🚀 MarketMind AI",
        "",
        "Agent Status",
        ""
    ]


    for result in results:

        logger.info(
            f"{result.agent} - {result.status}"
        )


        if result.status == "success":

            message_lines.append(
                f"✅ {result.agent}: {result.count} items"
            )

        else:

            message_lines.append(
                f"❌ {result.agent}: Failed"
            )

            logger.error(
                result.errors
            )


    message_lines.extend(
        [
            "",
            "Database:",
            f"Tables: {len(tables)}",
            "",
            "Status: Healthy ✅"
        ]
    )


    message = "\n".join(message_lines)


    send_message(message)


    db.close()


    logger.info(
        "MarketMind AI execution completed."
    )


if __name__ == "__main__":
    main()
