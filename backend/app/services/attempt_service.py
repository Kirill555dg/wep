"""
AttemptService: start, submit answers, finish, get result.
"""

from app.core import datetime_extensions as dte
from app.models.test_constructor import AttemptStatus
from app.repositories.test_constructor import (
    AnswerRepository,
    AttemptRepository,
    QuestionRepository,
    TestRepository,
)
from app.schemas.test_constructor import AnswerSubmitRequest, AttemptResponse, AttemptResultResponse, AttemptAnswerDetail
from app.services.exceptions import ServiceError
from app.services.grading import GradingService
from sqlalchemy.ext import asyncio as sa_asyncio


class AttemptService:
    def __init__(self, db: sa_asyncio.AsyncSession):
        self.db = db
        self.test_repo = TestRepository(db)
        self.question_repo = QuestionRepository(db)
        self.attempt_repo = AttemptRepository(db)
        self.answer_repo = AnswerRepository(db)
        self.grading = GradingService()

    async def start_attempt(self, test_id: int, user_id: int) -> AttemptResponse:
        test = await self.test_repo.get_by_id(test_id)
        if not test:
            raise ServiceError("Test not found", code="test_not_found")

        active = await self.attempt_repo.get_active_for_user_test(user_id, test_id)
        if active:
            raise ServiceError("Already have an active attempt", code="attempt_already_active")

        attempt = await self.attempt_repo.create({
            "test_id": test_id,
            "user_id": user_id,
            "started_at": dte.utc_now(),
            "status": AttemptStatus.IN_PROGRESS,
        })
        return AttemptResponse.model_validate(attempt)

    async def submit_answer(self, attempt_id: int, user_id: int, data: AnswerSubmitRequest) -> AttemptResponse:
        attempt = await self.attempt_repo.get_by_id(attempt_id)
        if not attempt or attempt.user_id != user_id:
            raise ServiceError("Attempt not found", code="attempt_not_found")
        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise ServiceError("Attempt already finished", code="attempt_finished")

        test = await self.test_repo.get_by_id_with_questions(attempt.test_id)
        question = next((q for q in test.questions if q.id == data.question_id), None)  # type: ignore[union-attr]
        if not question:
            raise ServiceError("Question not found in test", code="question_not_found")

        is_correct, points = self.grading.check_answer(question, data.selected_option_ids, data.text_answer)
        answer = await self.answer_repo.upsert(attempt_id, data.question_id, {
            "selected_option_ids": data.selected_option_ids,
            "text_answer": data.text_answer,
            "is_correct": is_correct,
            "points_earned": points,
        })
        from app.schemas.test_constructor import AnswerResponse
        return AnswerResponse.model_validate(answer)  # type: ignore[return-value]

    async def finish_attempt(self, attempt_id: int, user_id: int) -> AttemptResultResponse:
        attempt = await self.attempt_repo.get_by_id(attempt_id)
        if not attempt or attempt.user_id != user_id:
            raise ServiceError("Attempt not found", code="attempt_not_found")

        test = await self.test_repo.get_by_id_with_questions(attempt.test_id)
        answers = await self.answer_repo.get_by_attempt(attempt_id)

        score, max_score = self.grading.grade_attempt(test.questions, answers)  # type: ignore[union-attr]

        await self.attempt_repo.update(attempt_id, {
            "status": AttemptStatus.COMPLETED,
            "finished_at": dte.utc_now(),
            "score": score,
            "max_score": max_score,
        })

        return await self.get_result(attempt_id, user_id)

    async def get_result(self, attempt_id: int, user_id: int) -> AttemptResultResponse:
        attempt = await self.attempt_repo.get_by_id_with_answers(attempt_id)
        if not attempt or attempt.user_id != user_id:
            raise ServiceError("Attempt not found", code="attempt_not_found")

        test = await self.test_repo.get_by_id_with_questions(attempt.test_id)
        questions_by_id = {q.id: q for q in test.questions}  # type: ignore[union-attr]
        answers_by_question = {a.question_id: a for a in attempt.answers}

        answer_details = []
        for q in test.questions:  # type: ignore[union-attr]
            ans = answers_by_question.get(q.id)
            correct_option_ids = [o.id for o in q.options if o.is_correct]
            answer_details.append(AttemptAnswerDetail(
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

        return AttemptResultResponse(
            attempt_id=attempt.id,
            test_id=attempt.test_id,
            test_title=test.title,  # type: ignore[union-attr]
            status=attempt.status,
            score=attempt.score or 0,
            max_score=attempt.max_score or 0,
            started_at=attempt.started_at,
            finished_at=attempt.finished_at,
            answers=answer_details,
        )
