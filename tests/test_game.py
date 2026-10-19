import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from game_logic import Game
from questions import BUILT_IN, question_from_dict
import storage


class GameTests(unittest.TestCase):
    def test_questions_and_mission(self):
        self.assertEqual(len(BUILT_IN), 20)
        self.assertTrue(all(question_from_dict(q.to_dict()) == q for q in BUILT_IN))
        game = Game.new("Student")
        self.assertEqual(len(game.questions), 10)
        self.assertEqual(game.state, "Playing")
        self.assertEqual(game.sector, "Lunar Outpost")

    def test_answer_pause_and_ten_question_game_over(self):
        game = Game.new("Student")
        game.pause()
        self.assertIsNone(game.submit(0))
        game.resume()
        self.assertTrue(game.submit(game.question.correct)["right"])
        self.assertEqual(game.score, 100)
        self.assertIsNone(game.submit(0))
        self.assertTrue(game.next_question())
        for step in range(1, 10):
            wrong = (game.question.correct + 1) % 4
            self.assertFalse(game.submit(wrong)["right"])
            self.assertEqual(game.answered_count, step + 1)
            if step < 9:
                self.assertTrue(game.next_question())
                self.assertEqual(game.state, "Playing")
            else:
                self.assertFalse(game.next_question())
        self.assertEqual(game.state, "GameOver")
        self.assertEqual(game.correct_count, 1)
        self.assertEqual(game.score, 100)
        self.assertEqual(game.answered_count, 10)

    def test_score_is_saved_during_play_and_after_completion(self):
        game = Game.new("Student")
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(storage, "SAVE_FILE", Path(directory) / "scores.json"):
                scores = []
                for step in range(10):
                    game.submit(game.question.correct)
                    scores = storage.record_score(scores, game)
                    storage.save([], scores)
                    loaded_custom, loaded_scores = storage.load()
                    self.assertEqual(loaded_custom, [])
                    self.assertEqual(len(loaded_scores), 1)
                    self.assertEqual(loaded_scores[0]["answered"], step + 1)
                    self.assertEqual(loaded_scores[0]["score"], game.score)
                    if step < 9:
                        game.next_question()
                game.next_question()
                scores = storage.record_score(scores, game)
                storage.save([], scores)
                self.assertTrue(storage.load()[1][0]["completed"])
                self.assertEqual(game.score, 1450)

    def test_custom_validation(self):
        raw = {"prompt": "1/2 + 1/2?", "choices": ["1", "2", "1/2", "1/4"],
               "correct": 0, "explanation": "Two halves make a whole.", "topic": "Addition"}
        self.assertEqual(question_from_dict(raw).correct, 0)
        with self.assertRaises(ValueError):
            question_from_dict({**raw, "choices": ["1", "1", "2", "3"]})

    def test_game_new_trims_name_and_defaults_to_explorer(self):
        self.assertEqual(Game.new("  Ada  ").name, "Ada")
        self.assertEqual(Game.new("   ").name, "Explorer")

    def test_game_new_keeps_ten_questions_when_custom_pool_is_used(self):
        custom = [
            question_from_dict({"prompt": f"Custom {i}?", "choices": ["A", "B", "C", "D"],
                               "correct": 0, "explanation": "Example.", "topic": "Custom"})
            for i in range(3)
        ]
        game = Game.new("Student", custom=custom)
        self.assertEqual(len(game.questions), 10)
        self.assertTrue(all(isinstance(q, type(custom[0])) for q in game.questions))

    def test_submit_rejects_invalid_choices_and_paused_games(self):
        game = Game.new("Student")
        with self.assertRaises(ValueError):
            game.submit("A")
        with self.assertRaises(ValueError):
            game.submit(4)
        game.pause()
        self.assertIsNone(game.submit(game.question.correct))

    def test_score_and_streak_increase_for_correct_answers(self):
        game = Game.new("Student")
        result = game.submit(game.question.correct)
        self.assertTrue(result["right"])
        self.assertEqual(game.score, 100)
        self.assertEqual(game.streak, 1)
        self.assertEqual(game.correct_count, 1)
        self.assertEqual(game.answered_count, 1)
        self.assertEqual(game.last_result["answer"], game.question.choices[game.question.correct])

    def test_wrong_answer_resets_streak_and_keeps_wrong_count(self):
        game = Game.new("Student")
        wrong = (game.question.correct + 1) % 4
        result = game.submit(wrong)
        self.assertFalse(result["right"])
        self.assertEqual(game.score, 0)
        self.assertEqual(game.streak, 0)
        self.assertEqual(game.correct_count, 0)
        self.assertEqual(game.answered_count, 1)

    def test_next_question_moves_forward_and_requires_answer(self):
        game = Game.new("Student")
        self.assertTrue(game.submit(game.question.correct))
        self.assertTrue(game.next_question())
        self.assertEqual(game.index, 1)
        self.assertFalse(game.answered)
        self.assertEqual(game.last_result, {})
        self.assertFalse(game.next_question())

    def test_last_question_sets_game_over_after_advancing(self):
        game = Game.new("Student")
        game.index = len(game.questions) - 1
        self.assertTrue(game.submit(game.question.correct))
        self.assertFalse(game.next_question())
        self.assertEqual(game.state, "GameOver")
        self.assertEqual(game.index, len(game.questions) - 1)

    def test_sector_changes_at_question_boundaries(self):
        game = Game.new("Student")
        self.assertEqual(game.sector, "Lunar Outpost")
        game.index = 3
        self.assertEqual(game.sector, "Asteroid Belt")
        game.index = 7
        self.assertEqual(game.sector, "Crystal Core")

    def test_storage_save_and_load_round_trip_for_custom_questions(self):
        custom = [question_from_dict({
            "prompt": "1/3 + 1/3?",
            "choices": ["2/3", "1/3", "1/6", "2/6"],
            "correct": 0,
            "explanation": "Two thirds.",
            "topic": "Addition",
        })]
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(storage, "SAVE_FILE", Path(directory) / "scores.json"):
                storage.save(custom, [])
                loaded_custom, loaded_scores = storage.load()
                self.assertEqual(len(loaded_custom), 1)
                self.assertEqual(loaded_custom[0].prompt, "1/3 + 1/3?")
                self.assertEqual(loaded_scores, [])

    def test_record_score_replaces_same_session_id_and_keeps_latest_entry_first(self):
        game = Game.new("Student")
        game.session_id = "session-123"
        game.score = 850
        game.correct_count = 8
        game.answered_count = 9
        scores = [{"id": "session-123", "name": "Old", "score": 10, "correct": 1, "answered": 2,
                   "total": 10, "completed": False, "date": "2024-01-01"},
                  {"id": "other", "name": "Other", "score": 777, "correct": 7, "answered": 8,
                   "total": 10, "completed": True, "date": "2024-01-02"}]
        updated = storage.record_score(scores, game)
        self.assertEqual(updated[0]["id"], "session-123")
        self.assertEqual(updated[0]["score"], 850)
        self.assertEqual(len(updated), 2)
        self.assertEqual(updated[1]["id"], "other")


if __name__ == "__main__":
    unittest.main()
