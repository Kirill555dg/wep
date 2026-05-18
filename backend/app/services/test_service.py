import typing as tp

import sqlalchemy.ext.asyncio as sa_asyncio

from app.models import test_constructor as tc_models
from app.repositories import test_constructor as tc_repos
from app.schemas import test_constructor as tc_schemas
from app.services import exceptions as svc_exc


class TestService:
    def __init__(self, db: sa_asyncio.AsyncSession):
        self.db = db
        self.test_repo = tc_repos.TestRepository(db)
        self.question_repo = tc_repos.QuestionRepository(db)
        self.option_repo = tc_repos.OptionRepository(db)
        self.tag_repo = tc_repos.TagRepository(db)

    async def create_test(self, author_id: int, data: tc_schemas.TestCreate) -> tc_models.Test:
        test = await self.test_repo.create({
            "author_id": author_id,
            "title": data.title,
            "description": data.description,
            "is_public": data.is_public,
            "time_limit_minutes": data.time_limit_minutes,
            "attempt_limit": data.attempt_limit,
            "track_time": data.track_time,
            "completion_message": data.completion_message,
        })
        if data.tag_names:
            tag_ids = [(await self.tag_repo.get_or_create(name)).id for name in data.tag_names]
            await self.test_repo.add_tags(test.id, tag_ids)
        return await self.test_repo.get_by_id_with_questions(test.id)  # type: ignore[return-value]

    async def get_test(self, test_id: int, user_id: int | None) -> tc_models.Test:
        test = await self.test_repo.get_by_id_with_questions(test_id)
        if not test:
            raise svc_exc.ServiceError("Test not found", code="test_not_found")
        
        is_authorized = test.is_public
        if not test.is_public and user_id is not None and test.author_id == user_id:
            is_authorized = True
        
        if not is_authorized:
            raise svc_exc.ServiceError("Access denied", code="test_access_denied")
        
        return test

    async def update_test(self, test_id: int, user_id: int, data: tc_schemas.TestUpdate) -> tc_models.Test:
        test = await self.test_repo.get_by_id(test_id)
        if not test:
            raise svc_exc.ServiceError("Test not found", code="test_not_found")
        if test.author_id != user_id:
            raise svc_exc.ServiceError("Not the author", code="not_author")

        update_data: dict[str, tp.Any] = {
            k: v for k, v in data.model_dump(exclude_none=True).items() if k != "tag_names"
        }
        if update_data:
            await self.test_repo.update(test_id, update_data)

        if data.tag_names is not None:
            await self.test_repo.remove_tags(test_id)
            if data.tag_names:
                tag_ids = [(await self.tag_repo.get_or_create(name)).id for name in data.tag_names]
                await self.test_repo.add_tags(test_id, tag_ids)

        return await self.test_repo.get_by_id_with_questions(test_id)  # type: ignore[return-value]

    async def delete_test(self, test_id: int, user_id: int) -> None:
        test = await self.test_repo.get_by_id(test_id)
        if not test:
            raise svc_exc.ServiceError("Test not found", code="test_not_found")
        if test.author_id != user_id:
            raise svc_exc.ServiceError("Not the author", code="not_author")
        await self.test_repo.delete(test_id)

    async def list_author_tests(self, author_id: int, skip: int = 0, limit: int = 100) -> tuple[list[tc_models.Test], int]:
        tests = await self.test_repo.get_by_author(author_id, skip, limit)
        total = await self.test_repo.count_by_author(author_id)
        return tests, total

    async def add_question(self, test_id: int, user_id: int, data: tc_schemas.QuestionCreate) -> tc_models.Question:
        test = await self.test_repo.get_by_id(test_id)
        if not test:
            raise svc_exc.ServiceError("Test not found", code="test_not_found")
        if test.author_id != user_id:
            raise svc_exc.ServiceError("Not the author", code="not_author")

        max_order = await self.question_repo.get_max_order(test_id)
        order = data.order_number if data.order_number > 0 else max_order + 1

        create_data: dict[str, tp.Any] = {
            "test_id": test_id,
            "question_type": data.question_type,
            "text": data.text,
            "order_number": order,
            "points": data.points,
            "explanation": data.explanation,
            "correct_answer": data.correct_answer,
            "image_url": data.image_url,
        }
        if data.question_data is not None:
            create_data["question_data"] = data.question_data
        question = await self.question_repo.create(create_data)

        for opt in data.options:
            await self.option_repo.create({
                "question_id": question.id,
                "text": opt.text,
                "is_correct": opt.is_correct,
                "order_number": opt.order_number,
            })

        questions = await self.question_repo.get_by_test(test_id)
        return next(q for q in questions if q.id == question.id)

    async def update_question(self, question_id: int, user_id: int, data: tc_schemas.QuestionUpdate) -> tc_models.Question:
        question = await self.question_repo.get_by_id(question_id)
        if not question:
            raise svc_exc.ServiceError("Question not found", code="question_not_found")
        test = await self.test_repo.get_by_id(question.test_id)
        if not test or test.author_id != user_id:
            raise svc_exc.ServiceError("Not the author", code="not_author")

        update_data = {k: v for k, v in data.model_dump(exclude_none=True).items() if k != "options"}
        if "question_data" in update_data and update_data["question_data"] is None:
            del update_data["question_data"]
        if update_data:
            await self.question_repo.update(question_id, update_data)

        if data.options is not None:
            await self.option_repo.delete_by_question(question_id)
            for opt in data.options:
                await self.option_repo.create({
                    "question_id": question_id,
                    "text": opt.text,
                    "is_correct": opt.is_correct,
                    "order_number": opt.order_number,
                })

        questions = await self.question_repo.get_by_test(question.test_id)
        return next(q for q in questions if q.id == question_id)

    async def delete_question(self, question_id: int, user_id: int) -> None:
        question = await self.question_repo.get_by_id(question_id)
        if not question:
            raise svc_exc.ServiceError("Question not found", code="question_not_found")
        test = await self.test_repo.get_by_id(question.test_id)
        if not test or test.author_id != user_id:
            raise svc_exc.ServiceError("Not the author", code="not_author")
        await self.question_repo.delete(question_id)

    async def add_question_from_pool(
        self, test_id: int, user_id: int, source_question_id: int
    ) -> tc_models.Question:
        test = await self.test_repo.get_by_id(test_id)
        if not test:
            raise svc_exc.ServiceError("Test not found", code="test_not_found")
        if test.author_id != user_id:
            raise svc_exc.ServiceError("Not the author", code="not_author")

        source_question = await self.question_repo.get_by_id(source_question_id)
        if not source_question:
            raise svc_exc.ServiceError("Source question not found", code="question_not_found")

        source_test = await self.test_repo.get_by_id(source_question.test_id)
        if not source_test or source_test.author_id != user_id:
            raise svc_exc.ServiceError("Cannot add question from another author's test", code="access_denied")

        max_order = await self.question_repo.get_max_order(test_id)
        create_data: dict[str, tp.Any] = {
            "test_id": test_id,
            "question_type": source_question.question_type,
            "text": source_question.text,
            "order_number": max_order + 1,
            "points": source_question.points,
            "explanation": source_question.explanation,
            "correct_answer": source_question.correct_answer,
            "image_url": source_question.image_url,
            "question_data": source_question.question_data,
        }
        question = await self.question_repo.create(create_data)

        source_options = await self.option_repo.get_by_question(source_question_id)
        for opt in source_options:
            await self.option_repo.create({
                "question_id": question.id,
                "text": opt.text,
                "is_correct": opt.is_correct,
                "order_number": opt.order_number,
            })

        questions = await self.question_repo.get_by_test(test_id)
        return next(q for q in questions if q.id == question.id)
