"""Small JSON save file in the user's home directory."""

import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
import os

from questions import question_from_dict

SAVE_FILE = Path.home() / ".space_fractions_game.json"


def load():
    try:
        data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return [], []
    if not isinstance(data, dict):
        return [], []
    custom = []
    raw_questions = data.get("questions", [])
    if isinstance(raw_questions, list):
        for raw in raw_questions[:100]:
            try:
                custom.append(question_from_dict(raw))
            except (ValueError, TypeError):
                continue
    scores = data.get("scores", [])
    if not isinstance(scores, list):
        scores = []
    return custom, [x for x in scores[:10] if isinstance(x, dict)]


def save(custom, scores):
    content = {"questions": [q.to_dict() for q in custom], "scores": scores[:10]}
    # Write a complete replacement before swapping files, so a crash cannot
    # leave a half-written score file.
    temp_name = None
    try:
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=SAVE_FILE.parent,
                                prefix="space_fractions_", suffix=".tmp", delete=False) as temp:
            temp_name = temp.name
            json.dump(content, temp, indent=2, ensure_ascii=False)
        os.replace(temp_name, SAVE_FILE)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)


def record_score(scores, game):
    entry = {"id": game.session_id, "name": game.name, "score": game.score,
             "correct": game.correct_count, "answered": game.answered_count,
             "total": len(game.questions), "completed": game.state == "GameOver",
             "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")}
    return [entry, *(x for x in scores if x.get("id") != game.session_id)][:10]
