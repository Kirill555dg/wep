"""
Tests for AttemptService (start, submit, finish, result)
"""

import pytest

from app.models.test_constructor import AttemptStatus, QuestionType
from app.repositories import test_constructor as tc_repos
from app.schemas.test_constructor import AnswerSubmitRequest, OptionCreate, QuestionCreate, TestCreate
from app.schemas.users import UserCreate
from app.services.attempt_service import AttemptService
from app.services.auth import AuthService
from app.services.exceptions import ServiceError
from app.services.test_service import TestService

pytestmark = pytest.mark.anyio


async def _make_user(db, email: str = "u@test.com") -> int:
    svc = AuthService(db)
    user = await svc.register_user(UserCreate(
        email=email, password="Pass123!", first_name="T", last_name="U",
    ))
    return user.id


async def _make_test_with_questions(db, author_id: int, is_public: bool = True):
    svc = TestService(db)
    test = await svc.create_test(author_id, TestCreate(title="Quiz", is_public=is_public))
    await svc.add_question(test.id, author_id, QuestionCreate(
        question_type=QuestionType.SINGLE_CHOICE,
        text="2+2?",
        points=2,
        options=[
            OptionCreate(text="3", is_correct=False, order_number=0),
            OptionCreate(text="4", is_correct=True, order_number=1),
        ],
    ))
    await svc.add_question(test.id, author_id, QuestionCreate(
        question_type=QuestionType.TEXT,
        text="Capital of France?",
        points=3,
        explanation="Paris",
    ))
    return await svc.get_test(test.id, user_id=author_id)


async def test_start_attempt(db_session):
    uid = await _make_user(db_session)
    test = await _make_test_with_questions(db_session, uid)
    svc = AttemptService(db_session)
    attempt = await svc.start_attempt(test.id, user_id=uid)
    assert attempt.id is not None
    assert attempt.status == AttemptStatus.IN_PROGRESS
    assert attempt.test_id == test.id


async def test_start_attempt_test_not_found(db_session):
    uid = await _make_user(db_session)
    svc = AttemptService(db_session)
    with pytest.raises(ServiceError) as exc:
        await svc.start_attempt(9999, user_id=uid)
    assert exc.value.code == "test_not_found"


async def test_start_attempt_already_active(db_session):
    uid = await _make_user(db_session)
    test = await _make_test_with_questions(db_session, uid)
    svc = AttemptService(db_session)
    await svc.start_attempt(test.id, user_id=uid)
    with pytest.raises(ServiceError) as exc:
        await svc.start_attempt(test.id, user_id=uid)
    assert exc.value.code == "attempt_already_active"


async def test_submit_answer(db_session):
    uid = await _make_user(db_session)
    test = await _make_test_with_questions(db_session, uid)
    svc = AttemptService(db_session)
    attempt = await svc.start_attempt(test.id, user_id=uid)
    question = test.questions[0]
    correct_opt_id = next(o.id for o in question.options if o.is_correct)
    answer = await svc.submit_answer(attempt.id, uid, AnswerSubmitRequest(
        question_id=question.id,
        selected_option_ids=[correct_opt_id],
    ))
    assert answer.question_id == question.id
    assert answer.is_correct is True


async def test_submit_answer_wrong_attempt(db_session):
    uid = await _make_user(db_session)
    svc = AttemptService(db_session)
    with pytest.raises(ServiceError) as exc:
        await svc.submit_answer(9999, uid, AnswerSubmitRequest(question_id=1))
    assert exc.value.code == "attempt_not_found"


async def test_finish_attempt(db_session):
    uid = await _make_user(db_session)
    test = await _make_test_with_questions(db_session, uid)
    svc = AttemptService(db_session)
    attempt = await svc.start_attempt(test.id, user_id=uid)

    question = test.questions[0]
    correct_opt = next(o.id for o in question.options if o.is_correct)
    await svc.submit_answer(attempt.id, uid, AnswerSubmitRequest(
        question_id=question.id,
        selected_option_ids=[correct_opt],
    ))

    result = await svc.finish_attempt(attempt.id, user_id=uid)
    assert result.status == AttemptStatus.COMPLETED
    assert result.score == 2
    assert result.max_score == 5


async def test_finish_attempt_score_zero(db_session):
    uid = await _make_user(db_session)
    test = await _make_test_with_questions(db_session, uid)
    svc = AttemptService(db_session)
    attempt = await svc.start_attempt(test.id, user_id=uid)
    result = await svc.finish_attempt(attempt.id, user_id=uid)
    assert result.score == 0
    assert result.status == AttemptStatus.COMPLETED


async def test_get_result(db_session):
    uid = await _make_user(db_session)
    test = await _make_test_with_questions(db_session, uid)
    svc = AttemptService(db_session)
    attempt = await svc.start_attempt(test.id, user_id=uid)
    await svc.finish_attempt(attempt.id, user_id=uid)
    result = await svc.get_result(attempt.id, user_id=uid)
    assert result.attempt_id == attempt.id
    assert result.test_title == "Quiz"


async def test_start_attempt_sets_expires_at(db_session):
    uid = await _make_user(db_session)
    svc = TestService(db_session)
    test = await svc.create_test(uid, TestCreate(title="Timed", time_limit_minutes=30))
    attempt_svc = AttemptService(db_session)
    attempt = await attempt_svc.start_attempt(test.id, user_id=uid)
    assert attempt.expires_at is not None
    assert attempt.expires_at > attempt.started_at


async def test_start_attempt_no_time_limit(db_session):
    uid = await _make_user(db_session)
    test = await _make_test_with_questions(db_session, uid)
    attempt_svc = AttemptService(db_session)
    attempt = await attempt_svc.start_attempt(test.id, user_id=uid)
    assert attempt.expires_at is None


async def test_submit_answer_after_expiry_raises(db_session):
    from app.core import datetime_extensions as dte
    import datetime as dt
    uid = await _make_user(db_session)
    test = await _make_test_with_questions(db_session, uid)
    # Create a past-expired attempt via the repo
    attempt_repo = tc_repos.AttemptRepository(db_session)
    attempt = await attempt_repo.create({
        "test_id": test.id, "user_id": uid,
        "started_at": dte.utc_now() - dt.timedelta(hours=1),
        "expires_at": dte.utc_now() - dt.timedelta(minutes=1),
        "status": AttemptStatus.IN_PROGRESS,
    })
    attempt_svc = AttemptService(db_session)
    with pytest.raises(ServiceError) as exc:
        await attempt_svc.submit_answer(attempt.id, uid, AnswerSubmitRequest(question_id=1))
    assert exc.value.code == "attempt_expired"


async def test_finish_attempt_sets_expired_status(db_session):
    from app.core import datetime_extensions as dte
    import datetime as dt
    uid = await _make_user(db_session)
    test = await _make_test_with_questions(db_session, uid)
    attempt_repo = tc_repos.AttemptRepository(db_session)
    attempt = await attempt_repo.create({
        "test_id": test.id, "user_id": uid,
        "started_at": dte.utc_now() - dt.timedelta(hours=1),
        "expires_at": dte.utc_now() - dt.timedelta(minutes=1),
        "status": AttemptStatus.IN_PROGRESS,
    })
    attempt_svc = AttemptService(db_session)
    result = await attempt_svc.finish_attempt(attempt.id, uid)
    assert result.status == AttemptStatus.EXPIRED


async def test_text_grading_normalization(db_session):
    from app.services.grading import _normalize_text
    assert _normalize_text("  Hello   World  ") == "hello world"
    assert _normalize_text("Hello\tWorld\n") == "hello world"
    assert _normalize_text("  ") == ""
    assert _normalize_text("") == ""


async def test_expire_overdue_bulk(db_session):
    from app.core import datetime_extensions as dte
    import datetime as dt
    uid = await _make_user(db_session)
    test = await _make_test_with_questions(db_session, uid)
    attempt_repo = tc_repos.AttemptRepository(db_session)
    await attempt_repo.create({
        "test_id": test.id, "user_id": uid,
        "started_at": dte.utc_now() - dt.timedelta(hours=1),
        "expires_at": dte.utc_now() - dt.timedelta(minutes=1),
        "status": AttemptStatus.IN_PROGRESS,
    })
    attempt_svc = AttemptService(db_session)
    count = await attempt_svc.expire_overdue(test.id)
    assert count > 0
