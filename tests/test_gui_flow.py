"""Exercise screen callbacks without requiring a graphical display."""

import sys
import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import gui
import storage


class Widget:
    def __init__(self, parent=None, **options):
        self.parent = parent
        self.children = []
        if parent is not None:
            parent.children.append(self)
        self.options = options
        self.bg = options.get("bg", "#10162f")
        self.command = options.get("command")
        self.value = options.get("text", "")
        self.exists = True
        self.next_id = 0

    def __getattr__(self, name):
        if name in ("pack", "grid", "columnconfigure", "rowconfigure", "bind", "bind_all", "tag_bind",
                    "configure", "config", "itemconfigure", "move", "title", "geometry",
                    "minsize", "resizable", "transient", "grab_set", "protocol",
                    "set", "yview", "yview_scroll", "focus_set"):
            return lambda *args, **kwargs: self.options.update(kwargs)
        if name.startswith("create_"):
            def create(*args, **kwargs):
                self.next_id += 1
                return self.next_id
            return create
        raise AttributeError(name)

    def cget(self, key):
        return self.bg if key == "bg" else self.options.get(key)

    def bbox(self, key):
        return (0, 0, 1000, 800)

    def winfo_children(self):
        return list(self.children)

    def winfo_exists(self):
        return self.exists

    def destroy(self):
        self.exists = False
        if self.parent is not None and self in self.parent.children:
            self.parent.children.remove(self)

    def get(self):
        return self.value

    def set(self, value):
        self.value = value

    def delete(self, first, last):
        self.value = ""

    def insert(self, first, value):
        self.value = value

    def after(self, delay, callback):
        # Leave animation callbacks queued: screen transitions are synchronous.
        return None


class GuiFlowTests(unittest.TestCase):
    def walk(self, node):
        yield node
        for child in node.children:
            yield from self.walk(child)

    def click(self, root, text):
        matches = [widget for widget in self.walk(root)
                   if widget.options.get("text") == text and widget.command is not None]
        self.assertEqual(len(matches), 1, text)
        matches[0].command()

    def test_all_ten_questions_and_other_screens(self):
        replacements = [patch.object(gui.tk, key, Widget) for key in
                        ("Frame", "Label", "Button", "Canvas", "Scrollbar", "Entry", "Toplevel", "StringVar")]
        replacements.append(patch.object(gui.ttk, "Combobox", Widget))
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(storage, "SAVE_FILE", Path(folder) / "scores.json"):
                for replacement in replacements:
                    replacement.start()
                try:
                    app = gui.SpaceFractionsApp(Widget())
                    self.assertEqual(app.screen, "menu")
                    app.help()
                    self.assertEqual(app.screen, "help")
                    app.menu()
                    app.editor()
                    self.assertEqual(app.screen, "editor")
                    form_fields = [w for w in self.walk(app.root) if w.options.get("width") == 65]
                    self.assertEqual(len(form_fields), 7)
                    for field, value in zip(form_fields, ("1/2 + 1/2?", "Addition", "1", "2", "1/2", "1/4", "Two halves make one.")):
                        field.value = value
                    self.click(app.root, "Add question")
                    self.assertEqual(len(app.custom), 1)
                    self.assertEqual(len(storage.load()[0]), 1)
                    self.click(app.root, "Edit")
                    form_fields = [w for w in self.walk(app.root) if w.options.get("width") == 65]
                    form_fields[0].value = "2/2 = ?"
                    self.click(app.root, "Save changes")
                    self.assertEqual(app.custom[0].prompt, "2/2 = ?")
                    self.assertEqual(storage.load()[0][0].prompt, "2/2 = ?")
                    self.click(app.root, "Remove")
                    self.assertEqual(len(app.custom), 0)
                    app.menu()
                    app.start()
                    self.assertEqual(app.screen, "game")
                    app.pause()
                    self.assertEqual(app.game.state, "Paused")
                    self.click(app.root, "Resume")
                    self.assertEqual(app.game.state, "Playing")
                    for step in range(10):
                        wrong = (app.game.question.correct + 1) % 4
                        if step == 0:
                            app.on_key(SimpleNamespace(keysym="", char="ABCD"[wrong].lower()))
                        else:
                            app.answer(wrong)
                        self.assertEqual(app.game.answered_count, step + 1)
                        self.assertEqual(storage.load()[1][0]["answered"], step + 1)
                        if step < 9:
                            app.advance()
                            self.assertEqual(app.screen, "game")
                    app.advance()
                    self.assertEqual(app.screen, "results")
                    self.assertEqual(app.game.state, "GameOver")
                    app.show_scores()
                    self.assertEqual(app.screen, "scores")
                    self.assertTrue(storage.load()[1][0]["completed"])
                finally:
                    for replacement in reversed(replacements):
                        replacement.stop()
