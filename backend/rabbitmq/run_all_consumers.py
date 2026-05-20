"""
Точка входа: запуск всех RabbitMQ-консьюмеров сообщений.

Пример:
  python -m backend.rabbitmq.run_all_consumers
"""

from __future__ import annotations

import asyncio
import logging

from backend.project_config import configure_logging
from backend.rabbitmq.consumers.messages.create_message import run_consumer as run_create

configure_logging()
logger = logging.getLogger(__name__)


async def run_all_message_consumers() -> None:
    await asyncio.gather(
        run_create(),
    )


def main() -> None:
    try:
        asyncio.run(run_all_message_consumers())
    except KeyboardInterrupt:
        logger.info("Остановка консьюмеров.")


if __name__ == "__main__":
    main()
