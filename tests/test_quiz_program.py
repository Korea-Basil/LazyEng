import unittest
import tkinter as tk

from data_loader import LEVELS, load_questions
from gui import EnglishQuizApp
from quiz_engine import Question, QuizSession, WordNote, check_answer, format_feedback, run_quiz


def sample_question():
    return Question(
        prompt="I ____ a student.",
        choices=("am", "is", "are", "be"),
        correct_index=0,
        focus="I와 be동사의 짝",
        grammar_ko="I와 함께 현재형 be동사 am을 써요.",
        why_correct_ko="I am은 '나는 ~이다'라는 뜻이에요.",
        why_wrong_ko=(
            "정답이에요.",
            "is는 he, she, it과 써요.",
            "are는 you, we, they와 써요.",
            "be는 이 문장의 현재형 형태가 아니에요.",
        ),
        word_notes=(WordNote("student", "스튜던트", "명사", "학생"),),
    )


class QuizEngineTests(unittest.TestCase):
    def test_each_level_has_exactly_twenty_four_choice_questions(self):
        self.assertEqual(set(LEVELS), {"elementary", "middle", "high"})
        for level in LEVELS:
            with self.subTest(level=level):
                questions = load_questions(level)
                self.assertEqual(len(questions), 20)
                self.assertTrue(all(len(question.choices) == 4 for question in questions))
                self.assertTrue(all(question.word_notes for question in questions))

    def test_all_choice_words_have_korean_pronunciation_and_meaning(self):
        for level in LEVELS:
            for question in load_questions(level):
                notes = {note.word.casefold(): note for note in question.word_notes}
                for word in question.prompt.split() + [
                    token for choice in question.choices for token in choice.split()
                ]:
                    cleaned = "".join(char for char in word if char.isalpha() or char == "'")
                    if cleaned:
                        self.assertIn(cleaned.casefold(), notes, (level, question.prompt, cleaned))
                self.assertTrue(all(note.pronunciation and note.meaning_ko and note.part_of_speech
                                    for note in question.word_notes))

    def test_answer_accepts_letter_or_choice_text(self):
        question = sample_question()
        self.assertTrue(check_answer(question, "a"))
        self.assertTrue(check_answer(question, " AM "))
        self.assertFalse(check_answer(question, "B"))

    def test_feedback_explains_vocabulary_grammar_and_every_option(self):
        feedback = format_feedback(sample_question(), "B")
        self.assertIn("스튜던트", feedback)
        self.assertIn("문법·어순", feedback)
        self.assertIn("A. am", feedback)
        self.assertIn("B. is", feedback)
        self.assertIn("C. are", feedback)
        self.assertIn("D. be", feedback)
        self.assertIn("is는 he, she, it과 써요.", feedback)

    def test_quiz_runs_exactly_twenty_questions_and_scores_answers(self):
        question = sample_question()
        prompts = []
        outputs = []
        answers = iter(["invalid"] + ["A", "B"] * 10)

        def input_fn(prompt):
            prompts.append(prompt)
            return next(answers)

        score = run_quiz(
            [question] * 20,
            "elementary",
            input_fn=input_fn,
            output_fn=outputs.append,
        )
        self.assertEqual(score, 10)
        self.assertEqual(sum("정답을 골라 주세요" in item for item in prompts), 21)
        self.assertTrue(any("20/20" in item for item in outputs))
        self.assertTrue(any("점수: 10/20" in item for item in outputs))

    def test_quiz_rejects_a_bank_that_is_not_twenty_questions(self):
        with self.assertRaises(ValueError):
            run_quiz([sample_question()], "elementary", input_fn=lambda _: "A", output_fn=lambda _: None)

    def test_session_tracks_score_and_prevents_double_submission(self):
        session = QuizSession([sample_question()] * 20)
        self.assertTrue(session.submit(0))
        self.assertEqual(session.score, 1)
        with self.assertRaises(ValueError):
            session.submit(0)
        self.assertTrue(session.advance())
        self.assertEqual(session.index, 1)
        self.assertIsNone(session.selected_index)

    def test_session_requires_an_answer_before_advancing(self):
        session = QuizSession([sample_question()] * 20)
        with self.assertRaises(ValueError):
            session.advance()

    def test_session_finishes_after_exactly_twenty_submissions(self):
        session = QuizSession([sample_question()] * 20)
        for index in range(20):
            self.assertTrue(session.submit(0))
            if index < 19:
                self.assertTrue(session.advance())
        self.assertTrue(session.is_complete)
        self.assertEqual(session.score, 20)
        self.assertFalse(session.advance())


class GuiStartupTests(unittest.TestCase):
    def test_level_selection_screen_renders_visible_controls(self):
        try:
            root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk display is not available: {error}")
        self.addCleanup(root.destroy)
        app = EnglishQuizApp(root)
        root.update_idletasks()
        root.update()

        outer = root.winfo_children()[0]
        content = outer.winfo_children()[0]
        self.assertGreater(content.winfo_width(), 300)
        self.assertGreater(content.winfo_height(), 300)
        buttons = [
            child for child in content.winfo_children()
            if isinstance(child, tk.Button)
        ]
        self.assertEqual(len(buttons), 3)
        self.assertTrue(all(button.winfo_ismapped() for button in buttons))
        self.assertTrue(all(button.winfo_width() > 100 for button in buttons))


if __name__ == "__main__":
    unittest.main()
