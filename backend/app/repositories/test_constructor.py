import re
import typing as tp
import logging

import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_asyncio
import sqlalchemy.orm as sqla_orm

from app.models import test_constructor as tc_models
from app.repositories import base as base_repo

LOGGER = logging.getLogger(__name__)


class TestRepository(base_repo.BaseRepository[tc_models.Test]):
    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(tc_models.Test, db)

    async def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> list[tc_models.Test]:
        stmt = (
            sa.select(tc_models.Test)
            .where(tc_models.Test.author_id == author_id)
            .options(
                sqla_orm.selectinload(tc_models.Test.questions),
                sqla_orm.selectinload(tc_models.Test.test_tags).selectinload(tc_models.TestTag.tag),
            )
            .offset(skip)
            .limit(limit)
            .order_by(tc_models.Test.created_at.desc())
        )
        return tp.cast(list[tc_models.Test], await self._scalars_all(stmt))

    async def count_by_author(self, author_id: int) -> int:
        stmt = sa.select(sa.func.count()).select_from(tc_models.Test).where(tc_models.Test.author_id == author_id)
        result = await self.db.execute(stmt)
        return tp.cast(int, result.scalar_one())

    async def get_public(
        self,
        skip: int = 0,
        limit: int = 20,
        query: str | None = None,
        tag_slugs: list[str] | None = None,
        author_id: int | None = None,
    ) -> list[tc_models.Test]:
        stmt = (
            sa.select(tc_models.Test)
            .where(tc_models.Test.is_public.is_(True))
            .options(
                sqla_orm.selectinload(tc_models.Test.questions),
                sqla_orm.selectinload(tc_models.Test.test_tags).selectinload(tc_models.TestTag.tag),
            )
        )
        if author_id is not None:
            stmt = stmt.where(tc_models.Test.author_id == author_id)
        if query:
            stmt = stmt.where(
                sa.or_(tc_models.Test.title.ilike(f"%{query}%"), tc_models.Test.description.ilike(f"%{query}%"))
            )
        if tag_slugs:
            stmt = (
                stmt.join(tc_models.TestTag, tc_models.Test.id == tc_models.TestTag.test_id)
                .join(tc_models.Tag, tc_models.TestTag.tag_id == tc_models.Tag.id)
                .where(tc_models.Tag.slug.in_(tag_slugs))
            )
        stmt = stmt.offset(skip).limit(limit).order_by(tc_models.Test.created_at.desc())

        LOGGER.info(f"Executing get_public query: skip={skip}, limit={limit}, query={query}, tag_slugs={tag_slugs}")

        result = await self._scalars_all(stmt)

        LOGGER.info(f"get_public returned {len(result)} tests")

        return tp.cast(list[tc_models.Test], result)

    async def count_public(
        self, query: str | None = None, tag_slugs: list[str] | None = None, author_id: int | None = None
    ) -> int:
        stmt = sa.select(sa.func.count()).select_from(tc_models.Test).where(tc_models.Test.is_public.is_(True))
        if author_id is not None:
            stmt = stmt.where(tc_models.Test.author_id == author_id)
        if query:
            stmt = stmt.where(
                sa.or_(tc_models.Test.title.ilike(f"%{query}%"), tc_models.Test.description.ilike(f"%{query}%"))
            )
        if tag_slugs:
            stmt = (
                stmt.join(tc_models.TestTag, tc_models.Test.id == tc_models.TestTag.test_id)
                .join(tc_models.Tag, tc_models.TestTag.tag_id == tc_models.Tag.id)
                .where(tc_models.Tag.slug.in_(tag_slugs))
            )
        result = await self.db.execute(stmt)
        return tp.cast(int, result.scalar_one())

    async def get_by_id_with_questions(self, test_id: int) -> tc_models.Test | None:
        stmt = (
            sa.select(tc_models.Test)
            .where(tc_models.Test.id == test_id)
            .options(
                sqla_orm.selectinload(tc_models.Test.questions).selectinload(tc_models.Question.options),
                sqla_orm.selectinload(tc_models.Test.test_tags).selectinload(tc_models.TestTag.tag),
            )
            .execution_options(populate_existing=True)
        )
        return tp.cast(tc_models.Test | None, await self._scalar_one_or_none(stmt))

    async def add_tags(self, test_id: int, tag_ids: list[int]) -> None:
        for tag_id in tag_ids:
            self.db.add(tc_models.TestTag(test_id=test_id, tag_id=tag_id))
        await self.db.commit()

    async def remove_tags(self, test_id: int) -> None:
        stmt = sa.delete(tc_models.TestTag).where(tc_models.TestTag.test_id == test_id)
        await self.db.execute(stmt)
        await self.db.commit()


class QuestionRepository(base_repo.BaseRepository[tc_models.Question]):
    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(tc_models.Question, db)

    async def get_by_test(self, test_id: int) -> list[tc_models.Question]:
        stmt = (
            sa.select(tc_models.Question)
            .where(tc_models.Question.test_id == test_id)
            .options(sqla_orm.selectinload(tc_models.Question.options))
            .order_by(tc_models.Question.order_number)
        )
        return tp.cast(list[tc_models.Question], await self._scalars_all(stmt))

    async def get_max_order(self, test_id: int) -> int:
        stmt = sa.select(sa.func.coalesce(sa.func.max(tc_models.Question.order_number), -1)).where(
            tc_models.Question.test_id == test_id
        )
        result = await self.db.execute(stmt)
        return tp.cast(int, result.scalar_one())


class OptionRepository(base_repo.BaseRepository[tc_models.Option]):
    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(tc_models.Option, db)

    async def get_by_question(self, question_id: int) -> list[tc_models.Option]:
        stmt = (
            sa.select(tc_models.Option)
            .where(tc_models.Option.question_id == question_id)
            .order_by(tc_models.Option.order_number)
        )
        return tp.cast(list[tc_models.Option], await self._scalars_all(stmt))

    async def delete_by_question(self, question_id: int) -> None:
        stmt = sa.delete(tc_models.Option).where(tc_models.Option.question_id == question_id)
        await self.db.execute(stmt)
        await self.db.commit()


class TagRepository(base_repo.BaseRepository[tc_models.Tag]):
    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(tc_models.Tag, db)

    async def get_by_slug(self, slug: str) -> tc_models.Tag | None:
        stmt = sa.select(tc_models.Tag).where(tc_models.Tag.slug == slug)
        return tp.cast(tc_models.Tag | None, await self._scalar_one_or_none(stmt))

    async def get_by_slugs(self, slugs: list[str]) -> list[tc_models.Tag]:
        stmt = sa.select(tc_models.Tag).where(tc_models.Tag.slug.in_(slugs))
        return tp.cast(list[tc_models.Tag], await self._scalars_all(stmt))

    async def get_or_create(self, name: str) -> tc_models.Tag:
        slug = re.sub(r"[^\w]+", "-", name.lower()).strip("-")
        tag = await self.get_by_slug(slug)
        if tag:
            return tag
        return await self.create({"name": name, "slug": slug})


class AttemptRepository(base_repo.BaseRepository[tc_models.Attempt]):
    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(tc_models.Attempt, db)

    async def get_active_for_user_test(self, user_id: int, test_id: int) -> tc_models.Attempt | None:
        stmt = sa.select(tc_models.Attempt).where(
            tc_models.Attempt.user_id == user_id,
            tc_models.Attempt.test_id == test_id,
            tc_models.Attempt.status == tc_models.AttemptStatus.IN_PROGRESS,
        )
        return tp.cast(tc_models.Attempt | None, await self._scalar_one_or_none(stmt))

    async def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100, test_id: int | None = None, status: str | None = None
    ) -> list[tc_models.Attempt]:
        stmt = (
            sa.select(tc_models.Attempt)
            .where(tc_models.Attempt.user_id == user_id)
            .order_by(tc_models.Attempt.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        if test_id is not None:
            stmt = stmt.where(tc_models.Attempt.test_id == test_id)
        if status is not None:
            stmt = stmt.where(tc_models.Attempt.status == status)
        return tp.cast(list[tc_models.Attempt], await self._scalars_all(stmt))

    async def count_by_user(self, user_id: int, test_id: int | None = None, status: str | None = None) -> int:
        stmt = sa.select(sa.func.count()).select_from(tc_models.Attempt).where(tc_models.Attempt.user_id == user_id)
        if test_id is not None:
            stmt = stmt.where(tc_models.Attempt.test_id == test_id)
        if status is not None:
            stmt = stmt.where(tc_models.Attempt.status == status)
        result = await self.db.execute(stmt)
        return tp.cast(int, result.scalar_one())

    async def get_calendar(self, user_id: int, year: int, month: int) -> dict[str, int]:
        from calendar import monthrange
        _, last_day = monthrange(year, month)
        start = dt.datetime(year, month, 1, tzinfo=dt.timezone.utc)
        end = dt.datetime(year, month, last_day, 23, 59, 59, tzinfo=dt.timezone.utc)

        stmt = (
            sa.select(
                sa.func.date(tc_models.Attempt.started_at).label("day"),
                sa.func.count().label("cnt"),
            )
            .where(
                tc_models.Attempt.user_id == user_id,
                tc_models.Attempt.started_at >= start,
                tc_models.Attempt.started_at <= end,
            )
            .group_by(sa.func.date(tc_models.Attempt.started_at))
        )
        result = await self.db.execute(stmt)
        return {str(row.day): row.cnt for row in result}

    async def get_by_id_with_answers(self, attempt_id: int) -> tc_models.Attempt | None:
        stmt = (
            sa.select(tc_models.Attempt)
            .where(tc_models.Attempt.id == attempt_id)
            .options(sqla_orm.selectinload(tc_models.Attempt.answers))
        )
        return tp.cast(tc_models.Attempt | None, await self._scalar_one_or_none(stmt))

    async def count_by_test(self, test_id: int) -> int:
        stmt = sa.select(sa.func.count()).select_from(tc_models.Attempt).where(tc_models.Attempt.test_id == test_id)
        result = await self.db.execute(stmt)
        return tp.cast(int, result.scalar_one())

    async def count_completed_by_test(self, test_id: int) -> int:
        stmt = sa.select(sa.func.count()).select_from(tc_models.Attempt).where(
            tc_models.Attempt.test_id == test_id,
            tc_models.Attempt.status == tc_models.AttemptStatus.COMPLETED,
        )
        result = await self.db.execute(stmt)
        return tp.cast(int, result.scalar_one())

    async def avg_score_by_test(self, test_id: int) -> float | None:
        stmt = sa.select(sa.func.avg(tc_models.Attempt.score)).where(
            tc_models.Attempt.test_id == test_id,
            tc_models.Attempt.status == tc_models.AttemptStatus.COMPLETED,
        )
        result = await self.db.execute(stmt)
        val = result.scalar_one_or_none()
        return float(val) if val is not None else None

    async def aggregate_by_tests(self, test_ids: list[int]) -> dict[int, dict[str, int]]:
        """Return {test_id: {total, completed}} in a single query."""
        if not test_ids:
            return {}
        stmt = (
            sa.select(
                tc_models.Attempt.test_id,
                sa.func.count().label("total"),
                sa.func.sum(
                    sa.case((tc_models.Attempt.status == tc_models.AttemptStatus.COMPLETED, 1), else_=0)
                ).label("completed"),
            )
            .where(tc_models.Attempt.test_id.in_(test_ids))
            .group_by(tc_models.Attempt.test_id)
        )
        result = await self.db.execute(stmt)
        return {row.test_id: {"total": row.total, "completed": row.completed} for row in result}


class AnswerRepository(base_repo.BaseRepository[tc_models.Answer]):
    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(tc_models.Answer, db)

    async def get_by_attempt(self, attempt_id: int) -> list[tc_models.Answer]:
        stmt = sa.select(tc_models.Answer).where(tc_models.Answer.attempt_id == attempt_id)
        return tp.cast(list[tc_models.Answer], await self._scalars_all(stmt))

    async def get_by_attempt_question(self, attempt_id: int, question_id: int) -> tc_models.Answer | None:
        stmt = sa.select(tc_models.Answer).where(
            tc_models.Answer.attempt_id == attempt_id, tc_models.Answer.question_id == question_id
        )
        return tp.cast(tc_models.Answer | None, await self._scalar_one_or_none(stmt))

    async def upsert(self, attempt_id: int, question_id: int, data: dict[str, tp.Any]) -> tc_models.Answer:
        existing = await self.get_by_attempt_question(attempt_id, question_id)
        if existing:
            for k, v in data.items():
                setattr(existing, k, v)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        return await self.create({"attempt_id": attempt_id, "question_id": question_id, **data})
