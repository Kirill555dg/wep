import re
import typing as tp

from app.models import test_constructor as tc_models


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


class GradingService:
    def check_answer(
        self,
        question: tc_models.Question,
        selected_option_ids: list[int] | None,
        text_answer: str | None,
        matching_answer: dict[str, int] | None = None,
        file_answer: str | None = None,
    ) -> tuple[bool | None, int]:
        if question.question_type == tc_models.QuestionType.SINGLE_CHOICE:
            return self._check_single_choice(question, selected_option_ids)
        if question.question_type == tc_models.QuestionType.MULTIPLE_CHOICE:
            return self._check_multiple_choice(question, selected_option_ids)
        if question.question_type == tc_models.QuestionType.TEXT:
            return self._check_text(question, text_answer)
        if question.question_type == tc_models.QuestionType.MATCHING:
            return self._check_matching(question, matching_answer)
        if question.question_type == tc_models.QuestionType.FILE_UPLOAD:
            return self._check_file_upload(question, file_answer)
        return None, 0

    def grade_attempt(
        self,
        questions: list[tc_models.Question],
        answers: list[tc_models.Answer],
    ) -> tuple[int, int]:
        answers_by_question = {a.question_id: a for a in answers}
        total_score = 0
        max_score = sum(q.points for q in questions)
        for q in questions:
            answer = answers_by_question.get(q.id)
            if not answer:
                continue
            _, pts = self.check_answer(
                q, answer.selected_option_ids, answer.text_answer,
                matching_answer=answer.matching_answer,
                file_answer=answer.file_answer,
            )
            total_score += pts
        return total_score, max_score

    def _check_single_choice(
        self, question: tc_models.Question, selected_option_ids: list[int] | None
    ) -> tuple[bool, int]:
        if not selected_option_ids:
            return False, 0
        correct_ids = {o.id for o in question.options if o.is_correct}
        if set(selected_option_ids) == correct_ids:
            return True, question.points
        return False, 0

    def _check_multiple_choice(
        self, question: tc_models.Question, selected_option_ids: list[int] | None
    ) -> tuple[bool, int]:
        if not selected_option_ids:
            return False, 0
        correct_ids = {o.id for o in question.options if o.is_correct}
        if set(selected_option_ids) == correct_ids:
            return True, question.points
        return False, 0

    def _check_text(self, question: tc_models.Question, text_answer: str | None) -> tuple[bool | None, int]:
        expected = question.correct_answer or question.explanation
        if not expected:
            return None, 0
        if not text_answer:
            return False, 0
        if _normalize_text(text_answer) == _normalize_text(expected):
            return True, question.points
        return False, 0

    def _check_matching(
        self, question: tc_models.Question, matching_answer: dict[str, int] | None
    ) -> tuple[bool, int]:
        if not matching_answer:
            return False, 0
        question_data = question.question_data or {}
        pairs = question_data.get("matching_pairs", [])
        if not pairs:
            return False, 0
        correct_count = 0
        for term_id_str, def_id in matching_answer.items():
            term_id = int(term_id_str)
            if term_id == def_id:
                correct_count += 1
        if correct_count == len(pairs):
            return True, question.points
        return False, 0

    def _check_file_upload(self, question: tc_models.Question, file_answer: str | None) -> tuple[None, int]:
        return None, 0
