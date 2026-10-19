"""Fraction questions and validation for Space Fractions."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Question:
    prompt: str
    choices: tuple[str, str, str, str]
    correct: int
    explanation: str
    topic: str = "Fractions"

    def to_dict(self):
        data = asdict(self)
        data["choices"] = list(self.choices)
        return data


def question_from_dict(data):
    if not isinstance(data, dict):
        raise ValueError("Question must be an object.")
    prompt = data.get("prompt")
    choices = data.get("choices")
    correct = data.get("correct")
    explanation = data.get("explanation")
    topic = data.get("topic", "Fractions")
    for value, name, limit in ((prompt, "question", 220), (explanation, "explanation", 350), (topic, "topic", 40)):
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            raise ValueError(f"Enter a valid {name}.")
    if not isinstance(choices, (list, tuple)) or len(choices) != 4:
        raise ValueError("There must be four answers.")
    if any(not isinstance(x, str) or not x.strip() or len(x) > 70 for x in choices):
        raise ValueError("All four answers must be filled in.")
    choices = tuple(x.strip() for x in choices)
    if len({x.casefold() for x in choices}) != 4:
        raise ValueError("The four answers must be different.")
    if type(correct) is not int or not 0 <= correct < 4:
        raise ValueError("Select the correct answer A, B, C, or D.")
    return Question(prompt.strip(), choices, correct, explanation.strip(), topic.strip())


def q(prompt, choices, correct, explanation, topic):
    return Question(prompt, tuple(choices), correct, explanation, topic)


BUILT_IN = (
    q("Which fraction is equivalent to 1/2?", ("2/4", "1/3", "2/5", "3/8"), 0, "Multiply the top and bottom of 1/2 by 2 to get 2/4.", "Equivalent fractions"),
    q("What is 1/4 + 2/4?", ("3/8", "3/4", "2/4", "1/2"), 1, "The bottoms match. Add the tops: 1 + 2 = 3, so 3/4.", "Addition"),
    q("Which is greater: 3/4 or 2/3?", ("2/3", "They are equal", "3/4", "Neither"), 2, "3/4 is 9/12, while 2/3 is 8/12.", "Comparison"),
    q("What is 5/6 - 1/6 in simplest form?", ("2/3", "4/12", "1/6", "5/5"), 0, "5/6 - 1/6 = 4/6 = 2/3.", "Subtraction"),
    q("Simplify 6/8.", ("6/4", "3/4", "2/3", "1/4"), 1, "Divide the top and bottom by 2: 6/8 = 3/4.", "Simplifying"),
    q("What is 1/2 + 1/4?", ("2/6", "1/6", "3/4", "4/4"), 2, "1/2 = 2/4, then 2/4 + 1/4 = 3/4.", "Addition"),
    q("What is 2/3 x 3/4?", ("6/7", "1/2", "5/12", "2/7"), 1, "Multiply: 6/12. Simplify to 1/2.", "Multiplication"),
    q("What is 3/4 of 20 crystals?", ("10", "12", "15", "16"), 2, "One quarter of 20 is 5. Three quarters is 15.", "Fraction of a whole"),
    q("Which fraction is the smallest?", ("1/2", "3/4", "2/3", "1/4"), 3, "A quarter is smaller than all the other choices.", "Comparison"),
    q("What is 2/3 + 1/6?", ("3/9", "5/6", "1/2", "4/6"), 1, "2/3 = 4/6, then 4/6 + 1/6 = 5/6.", "Addition"),
    q("What is 7/8 - 1/4?", ("6/4", "3/8", "5/8", "1/2"), 2, "1/4 is 2/8. Subtract to get 5/8.", "Subtraction"),
    q("Fill the blank: 2/5 = __/20", ("4", "6", "8", "10"), 2, "Multiply the top and bottom by 4: 8/20.", "Equivalent fractions"),
    q("Which mixed number equals 7/4?", ("1 1/4", "1 3/4", "2 1/4", "3 1/4"), 1, "7/4 = 4/4 + 3/4 = 1 3/4.", "Improper fractions"),
    q("A ship uses 2/5 of 30 fuel cells. How many?", ("6", "10", "12", "15"), 2, "30 divided by 5 is 6. Two groups of 6 make 12.", "Fraction of a whole"),
    q("What is 1/2 divided by 1/4?", ("1/8", "1/2", "2", "4"), 2, "There are two quarters in one half.", "Division"),
    q("Choose the sign: 5/8 __ 3/4", (">", "=", "<", "+"), 2, "3/4 is 6/8. Since 5/8 is less, use <.", "Comparison"),
    q("What is 3/10 + 4/10?", ("7/20", "1/10", "7/10", "3/5"), 2, "The bottoms match; add the tops to get 7/10.", "Addition"),
    q("What is 1/2 x 2/5?", ("1/5", "3/7", "2/7", "1/10"), 0, "2/10 simplifies to 1/5.", "Multiplication"),
    q("Simplify 9/12.", ("9/6", "3/4", "2/3", "4/5"), 1, "Divide the top and bottom by 3: 3/4.", "Simplifying"),
    q("12 of 16 stars glow. What fraction is that?", ("2/3", "3/4", "4/5", "1/4"), 1, "12/16 simplifies to 3/4.", "Simplifying"),
)
