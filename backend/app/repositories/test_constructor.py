"""
Repositories for test constructor domain.
"""

import re
import typing as tp

import sqlalchemy as sa
from sqlalchemy import orm as orm

from app.db import session as db_session
from app.models.test_constructor import Answer, Attempt, AttemptStatus, Option, Question, Tag, Test, TestTag
from app.repositories.base import BaseRepository


class TestRepository(BaseRepository[Test]):
    def __init__(self, db: db_session.AsyncSessionLocal.__class__) -> None:  # type: ignore[name-defined]
        super().__init__(Test, db)

    async def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> list[Test]:
        stmt = sa.select(Test).where(Test.author_id == author_id).offset(skip).limit(limit).order_by(Test.created_at.desc())
        return tp.cast(list[Test], await self._scalars_all(stmt))

    async def count_by_author(self, author_id: int) -> int:
        stmt = sa.select(sa.func.count()).select_from(Test).where(Test.author_id == author_id)
        result = await self.db.execute(stmt)
        return tp.cast(int, result.scalar_one())

    async def get_public(
        self,
        skip: int = 0,
        limit: int = 20,
        query: str | None = None,
        tag_slugs: list[str] | None = None,
    ) -> list[Test]:
        stmt = sa.select(Test).where(Test.is_public.is_(True))
        if query:
            stmt = stmt.where(sa.or_(Test.title.ilike(f"%{query}%"), Test.description.ilike(f"%{query}%")))
        if tag_slugs:
            stmt = stmt.join(TestTag, Test.id == TestTag.test_id).join(Tag, TestTag.tag_id == Tag.id).where(Tag.slug.in_(tag_slugs))
        stmt = stmt.offset(skip).limit(limit).order_by(Test.created_at.desc())
        return tp.cast(list[Test], await self._scalars_all(stmt))

    async def count_public(self, query: str | None = None, tag_slugs: list[str] | None = None) -> int:
        stmt = sa.select(sa.func.count()).select_from(Test).where(Test.is_public.is_(True))
        if query:
            stmt = stmt.where(sa.or_(Test.title.ilike(f"%{query}%"), Test.description.ilike(f"%{query}%")))
        if tag_slugs:
            stmt = stmt.join(TestTag, Test.id == TestTag.test_id).join(Tag, TestTag.tag_id == Tag.id).where(Tag.slug.in_(tag_slugs))
        result = await self.db.execute(stmt)
        return tp.cast(int, result.scalar_one())

    async def get_by_id_with_questions(self, test_id: int) -> Test | None:
        stmt = (
            sa.select(Test)
            .where(Test.id == test_id)
            .options(
                orm.selectinload(Test.questions).selectinload(Question.options),
                orm.selectinload(Test.test_tags).selectinload(TestTag.tag),
            )
        )
        return tp.cast(Test | None, await self._scalar_one_or_none(stmt))

    async def add_tags(self, test_id: int, tag_ids: list[int]) -> None:
        for tag_id in tag_ids:
            self.db.add(TestTag(test_id=test_id, tag_id=tag_id))
        await self.db.commit()

    async def remove_tags(self, test_id: int) -> None:
        stmt = sa.delete(TestTag).where(TestTag.test_id == test_id)
        await self.db.execute(stmt)
        await self.db.commit()


class QuestionRepository(BaseRepository[Question]):
    def __init__(self, db: tp.Any) -> None:
        super().__init__(Question, db)

    async def get_by_test(self, test_id: int) -> list[Question]:
        stmt = (
            sa.select(Question)
            .where(Question.test_id == test_id)
            .options(orm.selectinload(Question.options))
            .order_by(Question.order_number)
        )
        return tp.cast(list[Question], await self._scalars_all(stmt))

    async def get_max_order(self, test_id: int) -> int:
        stmt = sa.select(sa.func.coalesce(sa.func.max(Question.order_number), -1)).where(Question.test_id == test_id)
        result = await self.db.execute(stmt)
        return tp.cast(int, result.scalar_one())


class OptionRepository(BaseRepository[Option]):
    def __init__(self, db: tp.Any) -> None:
        super().__init__(Option, db)

    async def get_by_question(self, question_id: int) -> list[Option]:
        stmt = sa.select(Option).where(Option.question_id == question_id).order_by(Option.order_number)
        return tp.cast(list[Option], await self._scalars_all(stmt))

    async def delete_by_question(self, question_id: int) -> None:
        stmt = sa.delete(Option).where(Option.question_id == question_id)
        await self.db.execute(stmt)
        await self.db.commit()


class TagRepository(BaseRepository[Tag]):
    def __init__(self, db: tp.Any) -> None:
        super().__init__(Tag, db)

    async def get_by_slug(self, slug: str) -> Tag | None:
        stmt = sa.select(Tag).where(Tag.slug == slug)
        return tp.cast(Tag | None, await self._scalar_one_or_none(stmt))

    async def get_by_slugs(self, slugs: list[str]) -> list[Tag]:
        stmt = sa.select(Tag).where(Tag.slug.in_(slugs))
        return tp.cast(list[Tag], await self._scalars_all(stmt))

    async def get_or_create(self, name: str) -> Tag:
        slug = re.sub(r"[^\w]+", "-", name.lower()).strip("-")
        tag = await self.get_by_slug(slug)
        if tag:
            return tag
        return await self.create({"name": name, "slug": slug})


class AttemptRepository(BaseRepository[Attempt]):
    def __init__(self, db: tp.Any) -> None:
        super().__init__(Attempt, db)

    async def get_active_for_user_test(self, user_id: int, test_id: int) -> Attempt | None:
        stmt = sa.select(Attempt).where(
            Attempt.user_id == user_id,
            Attempt.test_id == test_id,
            Attempt.status == AttemptStatus.IN_PROGRESS,
        )
        return tp.cast(Attempt | None, await self._scalar_one_or_none(stmt))

    async def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Attempt]:
        stmt = sa.select(Attempt).where(Attempt.user_id == user_id).order_by(Attempt.started_at.desc()).offset(skip).limit(limit)
        return tp.cast(list[Attempt], await self._scalars_all(stmt))

    async def get_by_id_with_answers(self, attempt_id: int) -> Attempt | None:
        stmt = (
            sa.select(Attempt)
            .where(Attempt.id == attempt_id)
            .options(orm.selectinload(Attempt.answers))
        )
        return tp.cast(Attempt | None, await self._scalar_one_or_none(stmt))

    async def count_by_test(self, test_id: int) -> int:
        stmt = sa.select(sa.func.count()).select_from(Attempt).where(Attempt.test_id == test_id)
        result = await self.db.execute(stmt)
        return tp.cast(int, result.scalar_one())

    async def count_completed_by_test(self, test_id: int) -> int:
        stmt = sa.select(sa.func.count()).select_from(Attempt).where(
            Attempt.test_id == test_id,
            Attempt.status == AttemptStatus.COMPLETED,
        )
        result = await self.db.execute(stmt)
        return tp.cast(int, result.scalar_one())

    async def avg_score_by_test(self, test_id: int) -> float | None:
        stmt = sa.select(sa.func.avg(Attempt.score)).where(
            Attempt.test_id == test_id,
            Attempt.status == AttemptStatus.COMPLETED,
        )
        result = await self.db.execute(stmt)
        val = result.scalar_one_or_none()
        return float(val) if val is not None else None


class AnswerRepository(BaseRepository[Answer]):
    def __init__(self, db: tp.Any) -> None:
        super().__init__(Answer, db)

    async def get_by_attempt(self, attempt_id: int) -> list[Answer]:
        stmt = sa.select(Answer).where(Answer.attempt_id == attempt_id)
        return tp.cast(list[Answer], await self._scalars_all(stmt))

    async def get_by_attempt_question(self, attempt_id: int, question_id: int) -> Answer | None:
        stmt = sa.select(Answer).where(Answer.attempt_id == attempt_id, Answer.question_id == question_id)
        return tp.cast(Answer | None, await self._scalar_one_or_none(stmt))

    async def upsert(self, attempt_id: int, question_id: int, data: dict[str, tp.Any]) -> Answer:
        existing = await self.get_by_attempt_question(attempt_id, question_id)
        if existing:
            for k, v in data.items():
                setattr(existing, k, v)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        return await self.create({"attempt_id": attempt_id, "question_id": question_id, **data})
