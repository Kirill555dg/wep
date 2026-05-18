import sqlalchemy.ext.asyncio as sa_asyncio

from app.models import test_constructor as tc_models
from app.repositories import test_constructor as tc_repos
from app.schemas import test_constructor as tc_schemas
from app.services import exceptions as svc_exc


class CatalogService:
    def __init__(self, db: sa_asyncio.AsyncSession):
        self.test_repo = tc_repos.TestRepository(db)

    async def search_public_tests(
        self, params: tc_schemas.CatalogSearchParams
    ) -> tuple[list[tc_models.Test], int]:
        tests = await self.test_repo.get_public(
            skip=params.skip,
            limit=params.limit,
            query=params.q,
            tag_slugs=params.tags or None,
            author_id=params.author_id,
        )
        total = await self.test_repo.count_public(
            query=params.q, tag_slugs=params.tags or None, author_id=params.author_id
        )
        return tests, total

    async def get_public_test_detail(self, test_id: int) -> tc_models.Test:
        test = await self.test_repo.get_by_id_with_questions(test_id)
        if not test or not test.is_public:
            raise svc_exc.ServiceError("Test not found", code="test_not_found")
        return test


class AuthorStatsService:
    def __init__(self, db: sa_asyncio.AsyncSession):
        self.test_repo = tc_repos.TestRepository(db)
        self.attempt_repo = tc_repos.AttemptRepository(db)

    async def get_test_stats(self, test_id: int, user_id: int) -> tc_schemas.TestStatsResponse:
        test = await self.test_repo.get_by_id_with_questions(test_id)
        if not test:
            raise svc_exc.ServiceError("Test not found", code="test_not_found")
        if test.author_id != user_id:
            raise svc_exc.ServiceError("Not the author", code="not_author")

        total = await self.attempt_repo.count_by_test(test_id)
        completed = await self.attempt_repo.count_completed_by_test(test_id)
        avg = await self.attempt_repo.avg_score_by_test(test_id)
        max_score = sum(q.points for q in test.questions) if test.questions else 0
        avg_pct = round(avg / max_score * 100, 1) if avg is not None and max_score > 0 else None

        return tc_schemas.TestStatsResponse(
            test_id=test.id,
            test_title=test.title,
            total_attempts=total,
            completed_attempts=completed,
            avg_score=round(avg, 2) if avg is not None else None,
            avg_score_percent=avg_pct,
        )

    async def get_author_stats(self, user_id: int) -> tc_schemas.AuthorStatsResponse:
        tests = await self.test_repo.get_by_author(user_id)
        total = await self.test_repo.count_by_author(user_id)
        public = sum(1 for t in tests if t.is_public)

        test_ids = [t.id for t in tests]
        agg = await self.attempt_repo.aggregate_by_tests(test_ids)
        total_attempts = sum(v["total"] for v in agg.values())
        completed_attempts = sum(v["completed"] for v in agg.values())

        return tc_schemas.AuthorStatsResponse(
            total_tests=total,
            public_tests=public,
            total_attempts_received=total_attempts,
            completed_attempts_received=completed_attempts,
        )
