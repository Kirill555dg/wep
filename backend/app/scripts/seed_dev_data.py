"""
Seed development data into the database.

Creates:
- demo users with tests

Run:
  python -m app.scripts.seed_dev_data
"""

import asyncio
import logging

import sqlalchemy as sa
from sqlalchemy.ext import asyncio as sa_asyncio

from app.core import logging_config as logging_config
from app.db import session as db_session
from app.models import users as user_models
from app.schemas import users as user_schemas
from app.services import auth as auth_service_module


logger = logging.getLogger("app.seed")


async def _exists_any_user(session: sa_asyncio.AsyncSession) -> bool:
    stmt = sa.select(sa.func.count()).select_from(user_models.User)
    count_value = (await session.execute(stmt)).scalar_one()
    return int(count_value) > 0


async def seed_dev_data() -> None:
    logging_config.setup_logging()

    async with db_session.AsyncSessionLocal() as session:
        if await _exists_any_user(session):
            logger.warning("seed_skipped_db_not_empty")
            return

        auth_service = auth_service_module.AuthService(session)

        user = await auth_service.register_user(
            user_schemas.UserCreate(
                email="demo@wep.dev",
                password="DemoPass123!",
                first_name="Demo",
                last_name="User",
            )
        )

        logger.info(
            "seed_done",
            extra={
                "user_id": user.id,
                "email": user.email,
            },
        )


def main() -> None:
    asyncio.run(seed_dev_data())


if __name__ == "__main__":
    main()

