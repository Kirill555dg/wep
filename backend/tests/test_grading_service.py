"""
Tests for GradingService (pure logic, no DB)
"""

from app.models.test_constructor import Answer, Option, Question, QuestionType
from app.services.grading import GradingService

grading = GradingService()


def _question(qtype: QuestionType, points: int = 2, explanation: str | None = None) -> Question:
    q = Question()
    q.question_type = qtype
    q.points = points
    q.explanation = explanation
    q.options = []
    return q


def _option(id: int, is_correct: bool) -> Option:
    o = Option()
    o.id = id
    o.is_correct = is_correct
    return o


# --- single_choice ---

def test_single_choice_correct():
    q = _question(QuestionType.SINGLE_CHOICE, points=2)
    q.options = [_option(1, False), _option(2, True)]
    is_correct, pts = grading.check_answer(q, [2], None)
    assert is_correct is True
    assert pts == 2


def test_single_choice_wrong():
    q = _question(QuestionType.SINGLE_CHOICE, points=2)
    q.options = [_option(1, False), _option(2, True)]
    is_correct, pts = grading.check_answer(q, [1], None)
    assert is_correct is False
    assert pts == 0


def test_single_choice_no_answer():
    q = _question(QuestionType.SINGLE_CHOICE, points=2)
    q.options = [_option(1, True)]
    is_correct, pts = grading.check_answer(q, None, None)
    assert is_correct is False
    assert pts == 0


# --- multiple_choice ---

def test_multiple_choice_all_correct():
    q = _question(QuestionType.MULTIPLE_CHOICE, points=3)
    q.options = [_option(1, True), _option(2, True), _option(3, False)]
    is_correct, pts = grading.check_answer(q, [1, 2], None)
    assert is_correct is True
    assert pts == 3


def test_multiple_choice_partial():
    q = _question(QuestionType.MULTIPLE_CHOICE, points=3)
    q.options = [_option(1, True), _option(2, True), _option(3, False)]
    is_correct, pts = grading.check_answer(q, [1], None)
    assert is_correct is False
    assert pts == 0


def test_multiple_choice_extra_wrong():
    q = _question(QuestionType.MULTIPLE_CHOICE, points=3)
    q.options = [_option(1, True), _option(2, True), _option(3, False)]
    is_correct, pts = grading.check_answer(q, [1, 2, 3], None)
    assert is_correct is False
    assert pts == 0


# --- text ---

def test_text_exact_match():
    q = _question(QuestionType.TEXT, points=1, explanation="Paris")
    is_correct, pts = grading.check_answer(q, None, "Paris")
    assert is_correct is True
    assert pts == 1


def test_text_case_insensitive():
    q = _question(QuestionType.TEXT, points=1, explanation="Paris")
    is_correct, pts = grading.check_answer(q, None, "paris")
    assert is_correct is True


def test_text_wrong():
    q = _question(QuestionType.TEXT, points=1, explanation="Paris")
    is_correct, pts = grading.check_answer(q, None, "London")
    assert is_correct is False
    assert pts == 0


def test_text_no_explanation():
    q = _question(QuestionType.TEXT, points=1, explanation=None)
    is_correct, pts = grading.check_answer(q, None, "anything")
    assert is_correct is None
    assert pts == 0


# --- essay ---

def test_essay_always_none():
    q = _question(QuestionType.ESSAY, points=5)
    is_correct, pts = grading.check_answer(q, None, "some long answer")
    assert is_correct is None
    assert pts == 0


# --- grade_attempt ---

def test_grade_attempt():
    q1 = _question(QuestionType.SINGLE_CHOICE, points=2)
    q1.id = 1
    q1.options = [_option(10, True), _option(11, False)]

    q2 = _question(QuestionType.SINGLE_CHOICE, points=3)
    q2.id = 2
    q2.options = [_option(20, False), _option(21, True)]

    a1 = Answer()
    a1.question_id = 1
    a1.selected_option_ids = [10]
    a1.text_answer = None

    a2 = Answer()
    a2.question_id = 2
    a2.selected_option_ids = [20]
    a2.text_answer = None

    score, max_score = grading.grade_attempt([q1, q2], [a1, a2])
    assert max_score == 5
    assert score == 2
