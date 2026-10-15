"""Question models, answer checking, and one-question-at-a-time quiz flow."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

QUESTION_COUNT = 20
LETTERS = ("A", "B", "C", "D")


@dataclass(frozen=True)
class WordNote:
    word: str
    pronunciation: str
    part_of_speech: str
    meaning_ko: str


@dataclass(frozen=True)
class Question:
    prompt: str
    choices: tuple[str, str, str, str]
    correct_index: int
    focus: str
    grammar_ko: str
    why_correct_ko: str
    why_wrong_ko: tuple[str, str, str, str]
    word_notes: tuple[WordNote, ...]


class QuizSession:
    """Track a single fixed-length quiz independently of its user interface."""

    def __init__(self, questions: list[Question]) -> None:
        if len(questions) != QUESTION_COUNT:
            raise ValueError(f"A quiz session must contain exactly {QUESTION_COUNT} questions.")
        self.questions = tuple(questions)
        self.index = 0
        self.score = 0
        self.selected_index: int | None = None
        self.submitted = False

    @property
    def current_question(self) -> Question:
        return self.questions[self.index]

    @property
    def is_complete(self) -> bool:
        return self.index == QUESTION_COUNT - 1 and self.submitted

    def submit(self, choice_index: int) -> bool:
        """Submit one selected choice, update score, and return whether it is right."""
        if self.submitted:
            raise ValueError("This question has already been submitted.")
        if not 0 <= choice_index < len(LETTERS):
            raise ValueError("Choose one of the four available answers.")
        self.selected_index = choice_index
        self.submitted = True
        correct = choice_index == self.current_question.correct_index
        if correct:
            self.score += 1
        return correct

    def advance(self) -> bool:
        """Move to the next question; return False after the final answer."""
        if not self.submitted:
            raise ValueError("Submit an answer before moving to the next question.")
        if self.is_complete:
            return False
        self.index += 1
        self.selected_index = None
        self.submitted = False
        return True


def check_answer(question: Question, answer: str) -> bool:
    """Check a letter or a choice's exact text, ignoring case and whitespace."""
    normalized = answer.strip().casefold()
    if normalized.upper() in LETTERS:
        return LETTERS.index(normalized.upper()) == question.correct_index
    return normalized == question.choices[question.correct_index].casefold()


def format_feedback(question: Question, answer: str) -> str:
    """Explain vocabulary, sentence structure, and every answer option in Korean."""
    correct = check_answer(question, answer)
    lines = [
        "정답이에요! 잘했어요! / Correct! Well done!"
        if correct
        else "괜찮아요, 하나씩 배워 봐요! / That's okay; let's learn it step by step!",
        f"정답 / Correct answer: {LETTERS[question.correct_index]}. "
        f"{question.choices[question.correct_index]}",
        "",
        "단어 뜻과 품사, 한글 발음 / Words: meaning, part of speech & Korean pronunciation",
    ]
    lines.extend(
        f"  - {note.word} [{note.pronunciation}] - {note.meaning_ko} ({note.part_of_speech})"
        for note in question.word_notes
    )
    lines.extend(
        [
            "",
            f"문법·어순 / Grammar & word order: {question.grammar_ko}",
            "",
            "선택지 하나씩 살펴보기 / Let's review every choice:",
        ]
    )
    for index, choice in enumerate(question.choices):
        verdict = "정답" if index == question.correct_index else "오답"
        reason = question.why_correct_ko if index == question.correct_index else question.why_wrong_ko[index]
        lines.append(f"  {LETTERS[index]}. {choice} - {verdict}: {reason}")
    return "\n".join(lines)


def run_quiz(
    questions: list[Question],
    level: str,
    *,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], object] = print,
) -> int:
    """Run exactly 20 answered multiple-choice questions and return the score."""
    if len(questions) != QUESTION_COUNT:
        raise ValueError(f"A quiz session must contain exactly {QUESTION_COUNT} questions.")

    output_fn(f"\n시작해 볼까요? 총 20문제예요. / Let's begin! There are exactly 20 questions. ({level})")
    score = 0
    for number, question in enumerate(questions, 1):
        output_fn(f"\n{'=' * 58}\n문제 {number}/20 / Question {number}/20")
        output_fn(question.prompt)
        for index, choice in enumerate(question.choices):
            output_fn(f"  {LETTERS[index]}. {choice}")

        while True:
            answer = input_fn("정답을 골라 주세요 (A/B/C/D) / Your answer (A/B/C/D): ").strip().upper()
            if answer in LETTERS:
                break
            output_fn("A, B, C, D 중에서 골라 주세요. / Please enter A, B, C, or D.")
        if check_answer(question, answer):
            score += 1
        output_fn(format_feedback(question, answer))

    output_fn(f"\n{'=' * 58}")
    output_fn(f"퀴즈 완료! 점수: {score}/20 / Quiz complete! Score: {score}/20")
    if score == QUESTION_COUNT:
        output_fn("완벽해요! 정말 대단해요! / Perfect score! Amazing work!")
    elif score >= 15:
        output_fn("정말 잘했어요! 계속 연습해 봐요. / Great job! Keep practicing.")
    elif score >= 10:
        output_fn("좋은 시작이에요. 다시 풀면 더 잘할 거예요! / Good start. You'll do even better next time!")
    else:
        output_fn("천천히 다시 공부하면 괜찮아요. 포기하지 마세요! / Take it slowly and keep going. Don't give up!")
    return score
