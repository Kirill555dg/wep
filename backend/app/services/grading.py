"""
GradingService: pure logic for auto-checking answers.
"""

from app.models.test_constructor import Answer, Question, QuestionType


class GradingService:
    def check_answer(
        self,
        question: Question,
        selected_option_ids: list[int] | None,
        text_answer: str | None,
    ) -> tuple[bool | None, int]:
        if question.question_type == QuestionType.SINGLE_CHOICE:
            return self._check_single_choice(question, selected_option_ids)
        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            return self._check_multiple_choice(question, selected_option_ids)
        if question.question_type == QuestionType.TEXT:
            return self._check_text(question, text_answer)
        # essay — manual grading
        return None, 0

    def grade_attempt(
        self,
        questions: list[Question],
        answers: list[Answer],
    ) -> tuple[int, int]:
        answers_by_question = {a.question_id: a for a in answers}
        total_score = 0
        max_score = sum(q.points for q in questions)
        for q in questions:
            answer = answers_by_question.get(q.id)
            if not answer:
                continue
            _, pts = self.check_answer(q, answer.selected_option_ids, answer.text_answer)
            total_score += pts
        return total_score, max_score

    def _check_single_choice(self, question: Question, selected_option_ids: list[int] | None) -> tuple[bool, int]:
        if not selected_option_ids:
            return False, 0
        correct_ids = {o.id for o in question.options if o.is_correct}
        if set(selected_option_ids) == correct_ids:
            return True, question.points
        return False, 0

    def _check_multiple_choice(self, question: Question, selected_option_ids: list[int] | None) -> tuple[bool, int]:
        if not selected_option_ids:
            return False, 0
        correct_ids = {o.id for o in question.options if o.is_correct}
        if set(selected_option_ids) == correct_ids:
            return True, question.points
        return False, 0

    def _check_text(self, question: Question, text_answer: str | None) -> tuple[bool | None, int]:
        if not question.explanation:
            return None, 0
        if not text_answer:
            return False, 0
        if text_answer.strip().lower() == question.explanation.strip().lower():
            return True, question.points
        return False, 0
