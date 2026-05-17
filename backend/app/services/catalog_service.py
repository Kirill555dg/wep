"""
CatalogService: public test search and preview.
AuthorStatsService: test and author statistics.
"""

from sqlalchemy.ext import asyncio as sa_asyncio

from app.repositories.test_constructor import AttemptRepository, TestRepository
from app.schemas.test_constructor import (
    AuthorStatsResponse,
    CatalogSearchParams,
    TestStatsResponse,
)
from app.models.test_constructor import Test
from app.services.exceptions import ServiceError


class CatalogService:
    def __init__(self, db: sa_asyncio.AsyncSession):
        self.test_repo = TestRepository(db)

    async def search_public_tests(self, params: CatalogSearchParams) -> tuple[list[Test], int]:
        tests = await self.test_repo.get_public(
            skip=params.skip,
            limit=params.limit,
            query=params.q,
            tag_slugs=params.tags or None,
        )
        total = await self.test_repo.count_public(query=params.q, tag_slugs=params.tags or None)
        return tests, total

    async def get_public_test_detail(self, test_id: int) -> Test:
        test = await self.test_repo.get_by_id_with_questions(test_id)
        if not test or not test.is_public:
            raise ServiceError("Test not found", code="test_not_found")
        return test


class AuthorStatsService:
    def __init__(self, db: sa_asyncio.AsyncSession):
        self.test_repo = TestRepository(db)
        self.attempt_repo = AttemptRepository(db)

    async def get_test_stats(self, test_id: int, user_id: int) -> TestStatsResponse:
        test = await self.test_repo.get_by_id(test_id)
        if not test:
            raise ServiceError("Test not found", code="test_not_found")
        if test.author_id != user_id:
            raise ServiceError("Not the author", code="not_author")

        total = await self.attempt_repo.count_by_test(test_id)
        completed = await self.attempt_repo.count_completed_by_test(test_id)
        avg = await self.attempt_repo.avg_score_by_test(test_id)
        max_score = sum(q.points for q in test.questions) if test.questions else 0
        avg_pct = round(avg / max_score * 100, 1) if avg is not None and max_score > 0 else None

        return TestStatsResponse(
            test_id=test.id,
            test_title=test.title,
            total_attempts=total,
            completed_attempts=completed,
            avg_score=round(avg, 2) if avg is not None else None,
            avg_score_percent=avg_pct,
        )

    async def get_author_stats(self, user_id: int) -> AuthorStatsResponse:
        tests, total = await self.test_repo.get_by_author(user_id), await self.test_repo.count_by_author(user_id)
        public = sum(1 for t in tests if t.is_public)
        total_attempts = 0
        completed_attempts = 0
        for t in tests:
            total_attempts += await self.attempt_repo.count_by_test(t.id)
            completed_attempts += await self.attempt_repo.count_completed_by_test(t.id)
        return AuthorStatsResponse(
            total_tests=total,
            public_tests=public,
            total_attempts_received=total_attempts,
            completed_attempts_received=completed_attempts,
        )
