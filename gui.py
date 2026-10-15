"""Warm paper-style Tkinter interface for the offline English quiz."""

from __future__ import annotations

from collections.abc import Callable
import tkinter as tk
from tkinter import ttk

from data_loader import LEVELS, load_questions
from quiz_engine import QUESTION_COUNT, QuizSession

PAPER = "#FBF9F1"
PAPER_DARK = "#F0EBDD"
INK = "#28271F"
MUTED = "#777367"
ACCENT = "#7B382F"
ACCENT_DARK = "#612820"
GREEN = "#3E6A50"
RED = "#A13E36"
WHITE = "#FFFDF8"
LINE = "#DED8C8"
HOVER = "#F3EDDC"
SELECTED = "#E9DFC6"
FONT_SERIF = ("Georgia", 12)
FONT_SANS = ("Malgun Gothic", 10)
FONT_SANS_BOLD = ("Malgun Gothic", 10, "bold")


class EnglishQuizApp:
    """Manage the level dashboard, quiz questions, feedback, and results."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("LazyEng English Test")
        self.root.configure(bg=PAPER)
        self.root.geometry("960x820")
        self.root.minsize(780, 680)
        self.session: QuizSession | None = None
        self.level = ""
        self.selected_choice: int | None = None
        self.option_buttons: list[tk.Button] = []
        self._style_ttk()
        self.show_level_screen()

    def _style_ttk(self) -> None:
        style = ttk.Style(self.root)
        style.configure("Paper.Horizontal.TProgressbar", troughcolor=LINE, background=ACCENT)

    def _clear(self) -> None:
        for child in self.root.winfo_children():
            child.destroy()
        self.option_buttons.clear()

    def _centered_content(self, *, width: int = 760) -> tk.Frame:
        """Create a centered column that grows with the app window."""
        outer = tk.Frame(self.root, bg=PAPER)
        outer.pack(fill="both", expand=True, padx=30, pady=24)
        content = tk.Frame(outer, bg=PAPER, width=width)
        content.pack(fill="both", expand=True)
        content.grid_columnconfigure(0, weight=1)
        outer.bind("<Configure>", lambda event: content.configure(width=max(600, event.width - 24)))
        return content

    def show_level_screen(self) -> None:
        self._clear()
        content = self._centered_content(width=700)
        tk.Label(
            content,
            text="LAZYENG  ·  ENGLISH TEST",
            bg=PAPER,
            fg=ACCENT,
            font=("Georgia", 12, "bold"),
        ).grid(row=0, column=0, pady=(75, 20))
        tk.Label(
            content,
            text="오늘의 영어 시험",
            bg=PAPER,
            fg=INK,
            font=("Malgun Gothic", 28, "bold"),
        ).grid(row=1, column=0, pady=(0, 8))
        tk.Label(
            content,
            text="A little practice, one question at a time.",
            bg=PAPER,
            fg=MUTED,
            font=("Georgia", 14, "italic"),
        ).grid(row=2, column=0, pady=(0, 34))
        tk.Frame(content, bg=LINE, height=1).grid(row=3, column=0, sticky="ew", padx=42, pady=(0, 24))
        tk.Label(
            content,
            text="공부할 수준을 선택해 주세요",
            bg=PAPER,
            fg=INK,
            font=("Malgun Gothic", 15, "bold"),
        ).grid(row=4, column=0, pady=(0, 6))
        tk.Label(
            content,
            text="Choose your level · Each test has 20 questions",
            bg=PAPER,
            fg=MUTED,
            font=FONT_SERIF,
        ).grid(row=5, column=0, pady=(0, 22))

        levels = (
            ("elementary", "초등", "Elementary", "Words & simple sentences"),
            ("middle", "중등", "Middle School", "Everyday grammar"),
            ("high", "고등", "High School", "Clauses & sentence patterns"),
        )
        for row, (key, korean, english, description) in enumerate(levels, 6):
            button = tk.Button(
                content,
                text=f"{korean}   ·   {english}\n{description}",
                command=lambda selected=key: self.start_quiz(selected),
                bg=WHITE,
                fg=INK,
                activebackground=HOVER,
                activeforeground=INK,
                relief="flat",
                bd=0,
                highlightthickness=1,
                highlightbackground=LINE,
                highlightcolor=ACCENT,
                font=("Malgun Gothic", 13, "bold"),
                justify="left",
                anchor="w",
                padx=24,
                pady=15,
                cursor="hand2",
            )
            button.grid(row=row, column=0, sticky="ew", padx=62, pady=6)
            self._bind_hover(button, WHITE, HOVER)

        tk.Label(
            content,
            text="총 20문제 · 답을 고른 뒤 자세한 해설을 확인해요",
            bg=PAPER,
            fg=MUTED,
            font=("Malgun Gothic", 9),
        ).grid(row=9, column=0, pady=(22, 0))

    @staticmethod
    def _bind_hover(widget: tk.Widget, normal: str, hover: str) -> None:
        widget.bind("<Enter>", lambda _event: widget.configure(bg=hover))
        widget.bind("<Leave>", lambda _event: widget.configure(bg=normal))

    def start_quiz(self, level: str) -> None:
        try:
            questions = load_questions(level)
            session = QuizSession(questions)
        except (OSError, ValueError) as error:
            self._show_error(str(error))
            return
        self.level = level
        self.session = session
        self.selected_choice = None
        self.show_question()

    def _show_error(self, message: str) -> None:
        from tkinter import messagebox

        messagebox.showerror("퀴즈를 열 수 없어요 / Unable to start", message, parent=self.root)

    def show_question(self) -> None:
        if self.session is None:
            self.show_level_screen()
            return
        self._clear()
        self.selected_choice = None
        session = self.session
        question = session.current_question
        content = self._centered_content(width=820)
        korean_level, english_level = LEVELS[self.level].split(" / ")

        header = tk.Frame(content, bg=PAPER)
        header.grid(row=0, column=0, sticky="ew", pady=(12, 16))
        header.grid_columnconfigure(0, weight=1)
        tk.Label(
            header,
            text=f"LAZYENG ENGLISH TEST  —  Level: {english_level} ({korean_level})",
            bg=PAPER,
            fg=ACCENT,
            font=("Georgia", 12, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            header,
            text=f"Question {session.index + 1:02d}/{QUESTION_COUNT}",
            bg=PAPER,
            fg=INK,
            font=("Georgia", 12),
            anchor="e",
        ).grid(row=0, column=1, sticky="e")
        progress = ttk.Progressbar(
            header,
            maximum=QUESTION_COUNT,
            value=session.index + 1,
            style="Paper.Horizontal.TProgressbar",
        )
        progress.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        card = tk.Frame(content, bg=WHITE, highlightthickness=1, highlightbackground=LINE)
        card.grid(row=1, column=0, sticky="ew", pady=(8, 18))
        tk.Label(
            card,
            text=f"QUESTION {session.index + 1:02d}",
            bg=WHITE,
            fg=MUTED,
            font=("Georgia", 10, "bold"),
        ).pack(anchor="w", padx=28, pady=(20, 8))
        tk.Label(
            card,
            text=question.prompt,
            bg=WHITE,
            fg=INK,
            font=("Georgia", 23, "bold"),
            wraplength=740,
            justify="left",
            anchor="w",
        ).pack(fill="x", padx=28, pady=(0, 24))

        tk.Label(
            content,
            text="정답을 선택하세요  /  Choose one answer",
            bg=PAPER,
            fg=INK,
            font=FONT_SANS_BOLD,
            anchor="w",
        ).grid(row=2, column=0, sticky="ew", pady=(0, 8))
        options = tk.Frame(content, bg=PAPER)
        options.grid(row=3, column=0, sticky="ew")
        for column in range(2):
            options.grid_columnconfigure(column, weight=1, uniform="option")
        for index, choice in enumerate(question.choices):
            button = tk.Button(
                options,
                text=f"{'ABCD'[index]}     {choice}",
                command=lambda selected=index: self.select_choice(selected),
                bg=WHITE,
                fg=INK,
                activebackground=HOVER,
                activeforeground=INK,
                relief="flat",
                bd=0,
                highlightthickness=1,
                highlightbackground=LINE,
                font=("Georgia", 14),
                anchor="w",
                padx=18,
                pady=13,
                cursor="hand2",
                state="normal" if not session.submitted else "disabled",
            )
            button.grid(row=index // 2, column=index % 2, sticky="ew", padx=5, pady=5)
            self.option_buttons.append(button)
            self._bind_hover(button, WHITE, HOVER)
        self._refresh_option_colors()

        controls = tk.Frame(content, bg=PAPER)
        controls.grid(row=4, column=0, sticky="ew", pady=(10, 10))
        self.submit_button = tk.Button(
            controls,
            text="정답 확인  /  Check Answer",
            command=self.submit_answer,
            bg=ACCENT,
            fg=WHITE,
            activebackground=ACCENT_DARK,
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            font=FONT_SANS_BOLD,
            padx=20,
            pady=11,
            cursor="hand2",
            state="disabled" if session.submitted else "normal",
        )
        self.submit_button.pack(side="left")
        self.next_button = tk.Button(
            controls,
            text="결과 보기  /  See Results" if session.index == QUESTION_COUNT - 1 else "다음 문제  /  Next Question  →",
            command=self.next_question,
            bg=PAPER_DARK,
            fg=INK,
            activebackground=HOVER,
            relief="flat",
            bd=0,
            font=FONT_SANS_BOLD,
            padx=20,
            pady=11,
            cursor="hand2",
            state="normal" if session.submitted else "disabled",
        )
        self.next_button.pack(side="right")

        self.feedback_box = tk.Frame(content, bg=PAPER_DARK, highlightthickness=1, highlightbackground=LINE)
        self.feedback_box.grid(row=5, column=0, sticky="nsew", pady=(4, 0))
        content.grid_rowconfigure(5, weight=1)
        feedback_header = tk.Label(
            self.feedback_box,
            text="해설  /  Explanation",
            bg=PAPER_DARK,
            fg=ACCENT,
            font=FONT_SANS_BOLD,
            anchor="w",
        )
        feedback_header.pack(fill="x", padx=16, pady=(12, 4))
        self.feedback_text = tk.Text(
            self.feedback_box,
            height=8,
            wrap="word",
            bg=PAPER_DARK,
            fg=INK,
            font=FONT_SANS,
            relief="flat",
            padx=16,
            pady=4,
            state="disabled",
            cursor="arrow",
        )
        scrollbar = ttk.Scrollbar(self.feedback_box, orient="vertical", command=self.feedback_text.yview)
        self.feedback_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 6), pady=(0, 8))
        self.feedback_text.pack(fill="both", expand=True, padx=(0, 2), pady=(0, 8))
        self.feedback_text.tag_configure("status_correct", foreground=GREEN, font=("Malgun Gothic", 11, "bold"))
        self.feedback_text.tag_configure("status_incorrect", foreground=RED, font=("Malgun Gothic", 11, "bold"))
        self.feedback_text.tag_configure("section", foreground=ACCENT, font=FONT_SANS_BOLD)
        self._set_feedback_placeholder()
        if session.submitted:
            self._display_feedback()

    def _set_feedback_placeholder(self) -> None:
        self.feedback_text.configure(state="normal")
        self.feedback_text.delete("1.0", "end")
        self.feedback_text.insert("end", "답을 선택하고 확인 버튼을 누르면 자세한 해설이 여기에 나와요.\n")
        self.feedback_text.insert("end", "Detailed feedback appears here after you check your answer.")
        self.feedback_text.configure(state="disabled")

    def _refresh_option_colors(self) -> None:
        for index, button in enumerate(self.option_buttons):
            if self.session and self.session.submitted:
                if index == self.session.current_question.correct_index:
                    background, foreground = "#E3EFE5", GREEN
                elif index == self.session.selected_index:
                    background, foreground = "#F5E5E1", RED
                else:
                    background, foreground = WHITE, INK
            elif index == self.selected_choice:
                background, foreground = SELECTED, INK
            else:
                background, foreground = WHITE, INK
            button.configure(bg=background, fg=foreground, highlightbackground=ACCENT if index == self.selected_choice else LINE)
            self._bind_hover(button, background, HOVER if not (self.session and self.session.submitted) else background)

    def select_choice(self, index: int) -> None:
        if self.session is None or self.session.submitted:
            return
        self.selected_choice = index
        self.submit_button.configure(state="normal")
        self._refresh_option_colors()

    def submit_answer(self) -> None:
        if self.session is None or self.selected_choice is None or self.session.submitted:
            return
        self.session.submit(self.selected_choice)
        self._refresh_option_colors()
        self.submit_button.configure(state="disabled")
        self.next_button.configure(state="normal")
        self._display_feedback()

    def _display_feedback(self) -> None:
        if self.session is None or self.session.selected_index is None:
            return
        question = self.session.current_question
        correct = self.session.selected_index == question.correct_index
        self.feedback_text.configure(state="normal")
        self.feedback_text.delete("1.0", "end")
        status = "정답이에요! 잘했어요!  /  Correct! Well done!\n" if correct else "괜찮아요, 같이 배워 봐요!  /  Let's learn it together!\n"
        self.feedback_text.insert("end", status, "status_correct" if correct else "status_incorrect")
        self.feedback_text.insert("end", f"정답  /  Correct answer: {'ABCD'[question.correct_index]}. {question.choices[question.correct_index]}\n\n")

        self.feedback_text.insert("end", "단어 뜻 · 품사 · 한글 발음  /  Words\n", "section")
        for note in question.word_notes:
            self.feedback_text.insert(
                "end",
                f"• {note.word} [{note.pronunciation}] — {note.meaning_ko} ({note.part_of_speech})\n",
            )

        self.feedback_text.insert("end", "\n문법과 어순  /  Grammar & word order\n", "section")
        self.feedback_text.insert("end", question.grammar_ko + "\n")
        self.feedback_text.insert("end", "\n선택지별 설명  /  Why each answer\n", "section")
        for index, choice in enumerate(question.choices):
            verdict = "정답" if index == question.correct_index else "오답"
            reason = question.why_correct_ko if index == question.correct_index else question.why_wrong_ko[index]
            self.feedback_text.insert("end", f"{'ABCD'[index]}. {choice} — {verdict}: {reason}\n")
        self.feedback_text.configure(state="disabled")
        self.feedback_text.see("1.0")

    def next_question(self) -> None:
        if self.session is None or not self.session.submitted:
            return
        if self.session.advance():
            self.show_question()
        else:
            self.show_results()

    def show_results(self) -> None:
        if self.session is None:
            self.show_level_screen()
            return
        score = self.session.score
        self._clear()
        content = self._centered_content(width=700)
        tk.Label(
            content,
            text="TEST COMPLETE",
            bg=PAPER,
            fg=ACCENT,
            font=("Georgia", 12, "bold"),
        ).grid(row=0, column=0, pady=(120, 16))
        tk.Label(
            content,
            text=f"{score} / {QUESTION_COUNT}",
            bg=PAPER,
            fg=INK,
            font=("Georgia", 52, "bold"),
        ).grid(row=1, column=0, pady=8)
        tk.Label(
            content,
            text="수고했어요! 한 문제씩 해낸 것이 정말 멋져요.",
            bg=PAPER,
            fg=INK,
            font=("Malgun Gothic", 16, "bold"),
        ).grid(row=2, column=0, pady=(12, 4))
        tk.Label(
            content,
            text="Great work showing up and practicing, one question at a time.",
            bg=PAPER,
            fg=MUTED,
            font=("Georgia", 12, "italic"),
            wraplength=560,
        ).grid(row=3, column=0, pady=(4, 30))
        self._action_button(content, "같은 수준으로 다시 풀기  /  Try Again", lambda: self.start_quiz(self.level), 4)
        self._action_button(content, "수준 선택으로 돌아가기  /  Choose Another Level", self.show_level_screen, 5, secondary=True)

    def _action_button(
        self,
        parent: tk.Frame,
        text: str,
        command: Callable[[], object],
        row: int,
        *,
        secondary: bool = False,
    ) -> None:
        background = PAPER_DARK if secondary else ACCENT
        foreground = INK if secondary else WHITE
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=background,
            fg=foreground,
            activebackground=HOVER if secondary else ACCENT_DARK,
            activeforeground=foreground,
            relief="flat",
            bd=0,
            font=FONT_SANS_BOLD,
            padx=20,
            pady=12,
            cursor="hand2",
        )
        button.grid(row=row, column=0, pady=6)
        self._bind_hover(button, background, HOVER if secondary else ACCENT_DARK)


def run_app() -> None:
    root = tk.Tk()
    EnglishQuizApp(root)
    root.mainloop()
