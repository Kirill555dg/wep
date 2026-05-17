"""
Tests for TestService (CRUD, access control, question management)
"""

import pytest

from app.models.test_constructor import QuestionType
from app.schemas.test_constructor import QuestionCreate, TestCreate, TestUpdate
from app.schemas.users import UserCreate
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


async def test_create_test(db_session):
    uid = await _make_user(db_session)
    svc = TestService(db_session)
    test = await svc.create_test(author_id=uid, data=TestCreate(title="My Test", is_public=False))
    assert test.id is not None
    assert test.title == "My Test"
    assert test.author_id == uid
    assert test.is_public is False


async def test_create_test_with_tags(db_session):
    uid = await _make_user(db_session)
    svc = TestService(db_session)
    test = await svc.create_test(uid, TestCreate(title="Tagged", tag_names=["math", "algebra"]))
    fetched = await svc.get_test(test.id, user_id=uid)
    tag_slugs = [tt.tag.slug for tt in fetched.test_tags]
    assert "math" in tag_slugs
    assert "algebra" in tag_slugs


async def test_get_test_public(db_session):
    uid = await _make_user(db_session, "a@t.com")
    other = await _make_user(db_session, "b@t.com")
    svc = TestService(db_session)
    test = await svc.create_test(uid, TestCreate(title="Public", is_public=True))
    fetched = await svc.get_test(test.id, user_id=other)
    assert fetched.id == test.id


async def test_get_test_private_by_author(db_session):
    uid = await _make_user(db_session)
    svc = TestService(db_session)
    test = await svc.create_test(uid, TestCreate(title="Private", is_public=False))
    fetched = await svc.get_test(test.id, user_id=uid)
    assert fetched.id == test.id


async def test_get_test_private_access_denied(db_session):
    uid = await _make_user(db_session, "a@t.com")
    other = await _make_user(db_session, "b@t.com")
    svc = TestService(db_session)
    test = await svc.create_test(uid, TestCreate(title="Private", is_public=False))
    with pytest.raises(ServiceError) as exc:
        await svc.get_test(test.id, user_id=other)
    assert exc.value.code == "test_access_denied"


async def test_get_test_not_found(db_session):
    svc = TestService(db_session)
    with pytest.raises(ServiceError) as exc:
        await svc.get_test(9999, user_id=1)
    assert exc.value.code == "test_not_found"


async def test_update_test(db_session):
    uid = await _make_user(db_session)
    svc = TestService(db_session)
    test = await svc.create_test(uid, TestCreate(title="Old Title"))
    updated = await svc.update_test(test.id, user_id=uid, data=TestUpdate(title="New Title", is_public=True))
    assert updated.title == "New Title"
    assert updated.is_public is True


async def test_update_test_not_author(db_session):
    uid = await _make_user(db_session, "a@t.com")
    other = await _make_user(db_session, "b@t.com")
    svc = TestService(db_session)
    test = await svc.create_test(uid, TestCreate(title="Test"))
    with pytest.raises(ServiceError) as exc:
        await svc.update_test(test.id, user_id=other, data=TestUpdate(title="Hack"))
    assert exc.value.code == "not_author"


async def test_delete_test(db_session):
    uid = await _make_user(db_session)
    svc = TestService(db_session)
    test = await svc.create_test(uid, TestCreate(title="Del"))
    await svc.delete_test(test.id, user_id=uid)
    with pytest.raises(ServiceError):
        await svc.get_test(test.id, user_id=uid)


async def test_list_author_tests(db_session):
    uid1 = await _make_user(db_session, "a@t.com")
    uid2 = await _make_user(db_session, "b@t.com")
    svc = TestService(db_session)
    await svc.create_test(uid1, TestCreate(title="T1"))
    await svc.create_test(uid1, TestCreate(title="T2"))
    await svc.create_test(uid2, TestCreate(title="Other"))
    tests, total = await svc.list_author_tests(author_id=uid1)
    assert total == 2
    assert all(t.author_id == uid1 for t in tests)



async def test_add_question_with_options(db_session):
    from app.schemas.test_constructor import OptionCreate
    uid = await _make_user(db_session)
    svc = TestService(db_session)
    test = await svc.create_test(uid, TestCreate(title="T"))
    q = await svc.add_question(test.id, user_id=uid, data=QuestionCreate(
        question_type=QuestionType.SINGLE_CHOICE,
        text="Capital of France?",
        points=1,
        options=[
            OptionCreate(text="Berlin", is_correct=False, order_number=0),
            OptionCreate(text="Paris", is_correct=True, order_number=1),
        ],
    ))
    assert q.id is not None
    assert len(q.options) == 2
    correct = [o for o in q.options if o.is_correct]
    assert len(correct) == 1
    assert correct[0].text == "Paris"


async def test_add_question_not_author(db_session):
    uid = await _make_user(db_session, "a@t.com")
    other = await _make_user(db_session, "b@t.com")
    svc = TestService(db_session)
    test = await svc.create_test(uid, TestCreate(title="T"))
    with pytest.raises(ServiceError) as exc:
        await svc.add_question(test.id, user_id=other, data=QuestionCreate(
            question_type=QuestionType.TEXT, text="Q", points=1,
        ))
    assert exc.value.code == "not_author"


async def test_delete_question(db_session):
    uid = await _make_user(db_session)
    svc = TestService(db_session)
    test = await svc.create_test(uid, TestCreate(title="T"))
    q = await svc.add_question(test.id, user_id=uid, data=QuestionCreate(
        question_type=QuestionType.TEXT, text="Q", points=1,
    ))
    await svc.delete_question(q.id, user_id=uid)
    fetched = await svc.get_test(test.id, user_id=uid)
    assert len(fetched.questions) == 0
