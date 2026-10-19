"""Pure game rules; does not depend on the window toolkit."""

import random
from dataclasses import dataclass, field
from uuid import uuid4

from questions import BUILT_IN, Question


@dataclass
class Game:
    name: str
    questions: list[Question]
    index: int = 0
    score: int = 0
    streak: int = 0
    correct_count: int = 0
    answered_count: int = 0
    session_id: str = field(default_factory=lambda: uuid4().hex)
    state: str = "Playing"
    answered: bool = False
    last_result: dict = field(default_factory=dict)

    @classmethod
    def new(cls, name, custom=(), rng=None):
        pool = list(BUILT_IN) + list(custom)
        (rng or random).shuffle(pool)
        return cls(name=(name.strip()[:24] or "Explorer"), questions=pool[:10])

    @property
    def question(self):
        return self.questions[self.index]

    def submit(self, choice):
        if self.state != "Playing" or self.answered:
            return None
        if type(choice) is not int or choice not in range(4):
            raise ValueError("Choose A, B, C, or D.")
        right = choice == self.question.correct
        self.answered = True
        self.answered_count += 1
        if right:
            self.streak += 1
            self.correct_count += 1
            self.score += 100 + 10 * (self.streak - 1)
        else:
            self.streak = 0
        self.last_result = {"right": right, "answer": self.question.choices[self.question.correct],
                            "explanation": self.question.explanation, "choice": choice}
        return self.last_result

    def next_question(self):
        if self.state != "Playing" or not self.answered:
            return False
        if self.index + 1 >= len(self.questions):
            self.state = "GameOver"
            return False
        self.index += 1
        self.answered = False
        self.last_result = {}
        return True

    def pause(self):
        if self.state == "Playing":
            self.state = "Paused"

    def resume(self):
        if self.state == "Paused":
            self.state = "Playing"

    @property
    def sector(self):
        return "Lunar Outpost" if self.index < 3 else "Asteroid Belt" if self.index < 7 else "Crystal Core"
