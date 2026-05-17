import datetime as dt

import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_asyncio

from app.core import datetime_extensions as dte
from app.models import test_constructor as tc_models
from app.repositories import test_constructor as tc_repos
from app.schemas import test_constructor as tc_schemas
from app.services import exceptions as svc_exc
from app.services import grading as grading_mod


class AttemptService:
    def __init__(self, db: sa_asyncio.AsyncSession):
        self.db = db
        self.test_repo = tc_repos.TestRepository(db)
        self.question_repo = tc_repos.QuestionRepository(db)
        self.attempt_repo = tc_repos.AttemptRepository(db)
        self.answer_repo = tc_repos.AnswerRepository(db)
        self.grading = grading_mod.GradingService()

    async def _check_expired(self, attempt: tc_models.Attempt) -> bool:
        if attempt.expires_at and dte.utc_now() > attempt.expires_at:
            if attempt.status == tc_models.AttemptStatus.IN_PROGRESS:
                await self.attempt_repo.update(attempt.id, {
                    "status": tc_models.AttemptStatus.EXPIRED,
                    "finished_at": dte.utc_now(),
                })
            return True
        return False

    async def start_attempt(self, test_id: int, user_id: int) -> tc_schemas.AttemptResponse:
        test = await self.test_repo.get_by_id(test_id)
        if not test:
            raise svc_exc.ServiceError("Test not found", code="test_not_found")

        active = await self.attempt_repo.get_active_for_user_test(user_id, test_id)
        if active:
            raise svc_exc.ServiceError("Already have an active attempt", code="attempt_already_active")

        expires_at = None
        if test.time_limit_minutes:
            expires_at = dte.utc_now() + dt.timedelta(minutes=test.time_limit_minutes)

        attempt = await self.attempt_repo.create({
            "test_id": test_id,
            "user_id": user_id,
            "started_at": dte.utc_now(),
            "expires_at": expires_at,
            "status": tc_models.AttemptStatus.IN_PROGRESS,
        })
        return tc_schemas.AttemptResponse.model_validate(attempt)

    async def expire_overdue(self, test_id: int) -> int:
        now = dte.utc_now()
        stmt = (
            sa.update(tc_models.Attempt)
            .where(
                tc_models.Attempt.test_id == test_id,
                tc_models.Attempt.status == tc_models.AttemptStatus.IN_PROGRESS,
                tc_models.Attempt.expires_at.isnot(None),
                tc_models.Attempt.expires_at < now,
            )
            .values(status=tc_models.AttemptStatus.EXPIRED, finished_at=now)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    async def submit_answer(
        self, attempt_id: int, user_id: int, data: tc_schemas.AnswerSubmitRequest
    ) -> tc_schemas.AnswerResponse:
        attempt = await self.attempt_repo.get_by_id(attempt_id)
        if not attempt or attempt.user_id != user_id:
            raise svc_exc.ServiceError("Attempt not found", code="attempt_not_found")
        if attempt.status != tc_models.AttemptStatus.IN_PROGRESS:
            raise svc_exc.ServiceError("Attempt already finished", code="attempt_finished")

        if await self._check_expired(attempt):
            raise svc_exc.ServiceError("Attempt has expired", code="attempt_expired")

        test = await self.test_repo.get_by_id_with_questions(attempt.test_id)
        question = next((q for q in test.questions if q.id == data.question_id), None)  # type: ignore[union-attr]
        if not question:
            raise svc_exc.ServiceError("Question not found in test", code="question_not_found")

        is_correct, points = self.grading.check_answer(question, data.selected_option_ids, data.text_answer)
        answer = await self.answer_repo.upsert(attempt_id, data.question_id, {
            "selected_option_ids": data.selected_option_ids,
            "text_answer": data.text_answer,
            "is_correct": is_correct,
            "points_earned": points,
        })
        return tc_schemas.AnswerResponse.model_validate(answer)

    async def finish_attempt(self, attempt_id: int, user_id: int) -> tc_schemas.AttemptResultResponse:
        attempt = await self.attempt_repo.get_by_id(attempt_id)
        if not attempt or attempt.user_id != user_id:
            raise svc_exc.ServiceError("Attempt not found", code="attempt_not_found")

        is_expired = await self._check_expired(attempt)
        status = tc_models.AttemptStatus.EXPIRED if is_expired else tc_models.AttemptStatus.COMPLETED

        test = await self.test_repo.get_by_id_with_questions(attempt.test_id)
        answers = await self.answer_repo.get_by_attempt(attempt_id)

        score, max_score = self.grading.grade_attempt(test.questions, answers)  # type: ignore[union-attr]

        await self.attempt_repo.update(attempt_id, {
            "status": status,
            "finished_at": dte.utc_now(),
            "score": score,
            "max_score": max_score,
        })

        return await self.get_result(attempt_id, user_id)

    async def get_result(self, attempt_id: int, user_id: int) -> tc_schemas.AttemptResultResponse:
        attempt = await self.attempt_repo.get_by_id_with_answers(attempt_id)
        if not attempt or attempt.user_id != user_id:
            raise svc_exc.ServiceError("Attempt not found", code="attempt_not_found")

        test = await self.test_repo.get_by_id_with_questions(attempt.test_id)
        answers_by_question = {a.question_id: a for a in attempt.answers}

        answer_details = []
        for q in test.questions:  # type: ignore[union-attr]
            ans = answers_by_question.get(q.id)
            correct_option_ids = [o.id for o in q.options if o.is_correct]
            answer_details.append(tc_schemas.AttemptAnswerDetail(
                question_id=q.id,
                question_text=q.text,
                question_type=q.question_type,
                points=q.points,
                selected_option_ids=ans.selected_option_ids if ans else None,
                text_answer=ans.text_answer if ans else None,
                is_correct=ans.is_correct if ans else None,
                points_earned=ans.points_earned if ans else None,
                correct_option_ids=correct_option_ids,
                explanation=q.explanation,
            ))

        return tc_schemas.AttemptResultResponse(
            attempt_id=attempt.id,
            test_id=attempt.test_id,
            test_title=test.title,  # type: ignore[union-attr]
            status=attempt.status,
            score=attempt.score or 0,
            max_score=attempt.max_score or 0,
            started_at=attempt.started_at,
            finished_at=attempt.finished_at,
            expires_at=attempt.expires_at,
            answers=answer_details,
        )
