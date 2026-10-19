"""Tkinter windows, artwork, controls, and question editor."""

import random
import tkinter as tk
from tkinter import messagebox, ttk

from game_logic import Game
from questions import question_from_dict
from storage import load, record_score, save

BG = "#10162f"
CARD = "#1d2947"
INK = "#f5f6fa"
MUTED = "#a9b8d1"
LIME = "#ccf17d"
CORAL = "#ff9a8e"
PURPLE = "#aa9cf4"


class SpaceFractionsApp:
    def __init__(self, root):
        self.root = root
        root.title("Space Fractions - Play the Game")
        root.geometry("1050x720")
        root.minsize(780, 600)
        root.configure(bg=BG)
        self.custom, self.scores = load()
        self.player_name = tk.StringVar(value="Explorer")
        self.game = None
        self.screen = None
        self.sequence = 0
        self.root.bind("<Key>", self.on_key)
        self.menu()

    def clear(self, name):
        self.sequence += 1
        for child in self.root.winfo_children():
            child.destroy()
        self.screen = name
        shell = tk.Frame(self.root, bg=BG)
        shell.pack(fill="both", expand=True)
        scroll = tk.Canvas(shell, bg=BG, bd=0, highlightthickness=0)
        bar = tk.Scrollbar(shell, orient="vertical", command=scroll.yview)
        scroll.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        scroll.pack(side="left", fill="both", expand=True)
        outer = tk.Frame(scroll, bg=BG, padx=30, pady=20)
        window = scroll.create_window((0, 0), window=outer, anchor="nw")
        outer.bind("<Configure>", lambda event: scroll.configure(scrollregion=scroll.bbox("all")))
        scroll.bind("<Configure>", lambda event: scroll.itemconfigure(window, width=event.width))
        self.root.bind_all("<MouseWheel>", lambda event: scroll.yview_scroll(int(-event.delta / 120), "units"))
        self.root.bind_all("<Button-4>", lambda event: scroll.yview_scroll(-1, "units"))
        self.root.bind_all("<Button-5>", lambda event: scroll.yview_scroll(1, "units"))
        self.scroll = scroll
        return outer

    def label(self, parent, text, size=14, color=INK, bold=False, **options):
        return tk.Label(parent, text=text, font=("Segoe UI", size, "bold" if bold else "normal"),
                        fg=color, bg=parent.cget("bg"), **options)

    def button(self, parent, text, command, primary=False, **options):
        return tk.Button(parent, text=text, command=command, relief="flat", bd=0,
                         font=("Segoe UI", 12, "bold"), cursor="hand2", padx=18, pady=12,
                         bg=LIME if primary else CARD, fg=BG if primary else INK,
                         activebackground="#e0ffad" if primary else "#354368",
                         activeforeground=BG if primary else INK, **options)

    def heading(self, parent, title, subtitle=None):
        self.label(parent, "✦  SPACE FRACTIONS", 12, LIME, True).pack(anchor="w")
        self.label(parent, title, 30, INK, True).pack(anchor="w", pady=(8, 0))
        if subtitle:
            self.label(parent, subtitle, 12, MUTED).pack(anchor="w", pady=(2, 12))

    def starfield(self, canvas, count=70, seed=12):
        randomizer = random.Random(seed)
        for _ in range(count):
            x, y = randomizer.randint(0, 960), randomizer.randint(0, 340)
            r = randomizer.choice((1, 1, 1, 2))
            canvas.create_oval(x-r, y-r, x+r, y+r, fill=randomizer.choice(("#90a4cd", "#dbe9ff", "#788bb5")), outline="")

    def menu(self):
        outer = self.clear("menu")
        self.heading(outer, "A fraction adventure in space", "Choose a mission and fly through ten fraction gates.")
        canvas = tk.Canvas(outer, width=960, height=315, bg="#131d3d", bd=0, highlightthickness=0)
        canvas.pack(fill="x", pady=(8, 14))
        self.starfield(canvas, seed=37)
        canvas.create_oval(570, 14, 915, 358, fill="#7f71ba", outline="#bcafe4", width=5)
        canvas.create_oval(543, 130, 933, 221, outline="#e9d6ff", width=15)
        canvas.create_polygon(190, 190, 242, 235, 180, 280, fill="#e9f3ff", outline="#b1c9ea", width=3, tags=("introship",))
        canvas.create_oval(188, 221, 207, 240, fill="#83b8e5", outline="", tags=("introship",))
        canvas.create_polygon(175, 274, 197, 303, 205, 266, fill=CORAL, outline="", tags=("introship",))
        canvas.create_text(32, 38, anchor="nw", text="MISSION: FRACTION FRONTIER", font=("Segoe UI", 15, "bold"), fill=LIME)
        canvas.create_text(32, 75, anchor="nw", text="Answer ten questions.\nWatch your ship fly to each gate.",
                           font=("Segoe UI", 15), fill=INK)
        entry_row = tk.Frame(outer, bg=BG)
        entry_row.pack(fill="x", pady=(2, 8))
        self.label(entry_row, "Explorer name: ", 12, MUTED).pack(side="left")
        tk.Entry(entry_row, textvariable=self.player_name, font=("Segoe UI", 13), width=26,
                 bg=CARD, fg=INK, insertbackground=INK, relief="flat").pack(side="left", ipady=7)
        actions = tk.Frame(outer, bg=BG)
        actions.pack(fill="x", pady=9)
        self.button(actions, "▶  PLAY THE GAME", self.start, True).pack(side="left", padx=(0, 10))
        self.button(actions, "How to play", self.help).pack(side="left", padx=5)
        self.button(actions, "View scores", self.show_scores).pack(side="left", padx=5)
        self.button(actions, "Update questions", self.editor).pack(side="left", padx=5)
        self.label(outer, "All ten questions are played. Choose A–D; read feedback; click Next gate. Escape pauses.", 11, MUTED).pack(anchor="w", pady=10)
        marker = self.sequence
        self.animate_intro(canvas, marker, 0)

    def animate_intro(self, canvas, marker, frame):
        if marker != self.sequence or self.screen != "menu":
            return
        canvas.move("introship", 0, 2 if frame % 24 < 12 else -2)
        self.root.after(75, lambda: self.animate_intro(canvas, marker, frame + 1))

    def start(self):
        self.game = Game.new(self.player_name.get(), self.custom)
        self.show_game()

    def show_game(self):
        game = self.game
        outer = self.clear("game")
        header = tk.Frame(outer, bg=BG)
        header.pack(fill="x")
        self.label(header, f"GATE {game.index + 1}/10   •   {game.sector}", 15, LIME, True).pack(side="left")
        self.button(header, "Ⅱ Pause", self.pause).pack(side="right")
        self.status_label = self.label(outer, self.status_text(), 13, MUTED, True)
        self.status_label.pack(anchor="w", pady=(12, 7))
        self.canvas = tk.Canvas(outer, width=960, height=310, bg="#131d3d", bd=0, highlightthickness=0)
        self.canvas.pack(fill="x", pady=5)
        self.starfield(self.canvas, seed=game.index + 29)
        self.canvas.create_oval(760, -35, 1040, 245, fill="#514a8a", outline="#877abe", width=4)
        self.canvas.create_oval(35, 284, 82, 331, fill="#76799b", outline="")
        self.canvas.create_oval(680, 279, 724, 323, fill="#76799b", outline="")
        self.canvas.create_text(480, 23, text="CLICK A GATE OR CHOOSE AN ANSWER BELOW", fill=MUTED,
                                font=("Segoe UI", 12, "bold"))
        self.gate_positions = []
        self.gate_shapes = []
        q = game.question
        for i in range(4):
            x = 155 + 215 * i
            self.gate_positions.append((x, 135))
            tag = f"gate-{i}"
            shape = self.canvas.create_rectangle(x-74, 75, x+74, 186, fill="#2a395d", outline=PURPLE, width=4, tags=(tag,))
            self.gate_shapes.append(shape)
            self.canvas.create_text(x, 103, text=f"GATE {'ABCD'[i]}", fill=LIME,
                                    font=("Segoe UI", 13, "bold"), tags=(tag,))
            self.canvas.create_text(x, 142, text=q.choices[i], fill=INK, width=130,
                                    font=("Segoe UI", 14, "bold"), tags=(tag,))
            self.canvas.tag_bind(tag, "<Button-1>", lambda event, choice=i: self.answer(choice))
        self.ship = self.canvas.create_polygon(70, 235, 120, 260, 69, 285, 80, 260,
                                               fill="#e9f4ff", outline="#94b7d4", width=3, tags=("ship",))
        self.canvas.create_polygon(76, 252, 42, 260, 77, 270, fill=CORAL, outline="", tags=("ship",))
        self.ship_x, self.ship_y = 95, 260
        self.label(outer, q.topic.upper(), 10, PURPLE, True).pack(anchor="w", pady=(10, 0))
        self.label(outer, q.prompt, 22, INK, True, wraplength=900, justify="left").pack(anchor="w", pady=(2, 13))
        self.answers = tk.Frame(outer, bg=BG)
        self.answers.pack(fill="x")
        self.answer_buttons = []
        for i, choice in enumerate(q.choices):
            b = self.button(self.answers, f"{'ABCD'[i]}   {choice}", lambda idx=i: self.answer(idx))
            b.grid(row=i//2, column=i%2, sticky="ew", padx=5, pady=4)
            self.answer_buttons.append(b)
        self.answers.columnconfigure(0, weight=1)
        self.answers.columnconfigure(1, weight=1)
        self.feedback_frame = tk.Frame(outer, bg=BG)
        self.feedback_frame.pack(fill="x", pady=8)

    def answer(self, choice):
        if self.screen != "game" or self.game.state != "Playing":
            return
        result = self.game.submit(choice)
        if result is None:
            return
        self.status_label.config(text=self.status_text())
        self.scores = record_score(self.scores, self.game)
        self.persist()
        for i, b in enumerate(self.answer_buttons):
            b.config(state="disabled", disabledforeground=INK,
                     bg="#27523d" if i == self.game.question.correct else "#633a46" if i == choice else CARD)
        for i, shape in enumerate(self.gate_shapes):
            self.canvas.itemconfigure(shape, outline=LIME if i == self.game.question.correct else CORAL if i == choice else PURPLE)
        self.label(self.feedback_frame, ("✓  Correct!" if result["right"] else f"✗  The answer is {result['answer']}.")
                   + "  " + result["explanation"], 12, LIME if result["right"] else CORAL,
                   True, wraplength=870, justify="left").pack(anchor="w", pady=(0, 8))
        self.button(self.feedback_frame, "See results →" if self.game.index == len(self.game.questions)-1 else "Next gate →",
                    self.advance, True).pack(anchor="w")
        target_x, target_y = self.gate_positions[choice]
        marker = self.sequence
        self.fly(target_x, target_y, 14, marker)

    def fly(self, target_x, target_y, frames, marker):
        if marker != self.sequence or self.screen != "game" or frames <= 0:
            return
        dx = (target_x - self.ship_x) / frames
        dy = (target_y - self.ship_y) / frames
        self.canvas.move("ship", dx, dy)
        self.ship_x += dx
        self.ship_y += dy
        self.root.after(25, lambda: self.fly(target_x, target_y, frames-1, marker))

    def advance(self):
        if self.screen != "game" or self.game.state != "Playing":
            return
        if self.game.next_question():
            self.show_game()
        else:
            self.scores = record_score(self.scores, self.game)
            self.persist()
            self.results()

    def status_text(self):
        game = self.game
        return (f"SCORE  {game.score}          CORRECT  {game.correct_count}/{game.answered_count}"
                f"          COMPLETED  {game.answered_count}/{len(game.questions)}          STREAK  {game.streak}")

    def pause(self):
        if self.screen != "game" or self.game.state != "Playing":
            return
        self.game.pause()
        modal = tk.Toplevel(self.root)
        modal.title("Mission paused")
        modal.configure(bg=BG)
        modal.geometry("360x240")
        modal.resizable(False, False)
        modal.transient(self.root)
        modal.grab_set()
        self.label(modal, "Ⅱ  Mission paused", 20, LIME, True).pack(pady=(25, 13))
        self.label(modal, "The spaceship is waiting for you.", 12, MUTED).pack(pady=6)

        def resume():
            self.game.resume()
            modal.destroy()

        def quit_game():
            self.game.resume()
            modal.destroy()
            self.menu()

        self.button(modal, "Resume", resume, True).pack(pady=(10, 5))
        self.button(modal, "Leave mission", quit_game).pack()
        modal.bind("<Escape>", lambda event: resume())
        modal.protocol("WM_DELETE_WINDOW", resume)
        self.pause_window = modal

    def results(self):
        game = self.game
        outer = self.clear("results")
        self.heading(outer, "Mission complete!", "You finished all ten fraction gates.")
        canvas = tk.Canvas(outer, height=280, bg="#131d3d", highlightthickness=0)
        canvas.pack(fill="x", pady=20)
        self.starfield(canvas, seed=49)
        canvas.create_text(480, 95, text="✦  FRACTION FRONTIER  ✦", fill=LIME, font=("Segoe UI", 24, "bold"))
        canvas.create_text(480, 175, text=f"{game.name}  •  {game.score} POINTS", fill=INK, font=("Segoe UI", 20, "bold"))
        self.label(outer, f"Correct answers: {game.correct_count}/{len(game.questions)}     Best score: {max(x.get('score', 0) for x in self.scores)}",
                   16, INK, True).pack(anchor="w", pady=18)
        self.label(outer, "Every question you answer helps your fraction skills grow.", 13, MUTED).pack(anchor="w")
        row = tk.Frame(outer, bg=BG)
        row.pack(anchor="w", pady=30)
        self.button(row, "Play again", self.start, True).pack(side="left", padx=(0, 10))
        self.button(row, "Main menu", self.menu).pack(side="left")
        self.button(row, "View scores", self.show_scores).pack(side="left", padx=10)

    def help(self):
        outer = self.clear("help")
        self.heading(outer, "How to play", "A grade-six fraction learning adventure.")
        lines = (
            "1. Type your explorer name, then click PLAY THE GAME.",
            "2. Read the fraction question and click one of four gates or answer buttons.",
            "3. You can also press A, B, C, or D on your keyboard.",
            "4. Your ship flies to the selected gate. Correct answers earn 100 points and a streak bonus.",
            "5. Wrong answers do not end the game. Every mission has all ten questions.",
            "6. Read the explanation after each choice, then click Next gate.",
            "7. Press Escape or click Pause to stop; choose Resume to continue.",
            "8. Scores and your own questions are stored on this computer.",
        )
        for line in lines:
            self.label(outer, line, 13, INK, wraplength=850, justify="left").pack(anchor="w", pady=12)
        self.button(outer, "← Main menu", self.menu).pack(anchor="w", pady=22)

    def show_scores(self):
        outer = self.clear("scores")
        self.heading(outer, "Flight log", "Recent missions saved on this computer.")
        if not self.scores:
            self.label(outer, "No scores yet. Play your first game!", 14, MUTED).pack(anchor="w", pady=20)
        for i, entry in enumerate(self.scores):
            row = tk.Frame(outer, bg=CARD)
            row.pack(fill="x", pady=5, ipady=9)
            self.label(row, f"{i+1:02d}    {entry.get('name', 'Explorer')}", 14, INK, True).pack(side="left", padx=18)
            self.label(row, f"{entry.get('score', 0)} points     {entry.get('correct', 0)}/{entry.get('answered', entry.get('total', 10))} correct"
                       f"     {'Finished' if entry.get('completed') else 'In progress'}     {entry.get('date', '')}",
                       12, MUTED).pack(side="right", padx=18)
        self.button(outer, "← Main menu", self.menu).pack(anchor="w", pady=22)

    def persist(self):
        try:
            save(self.custom, self.scores)
        except OSError as exc:
            messagebox.showwarning("Cannot save", f"The game works, but scores could not be saved:\n{exc}")

    def editor(self):
        outer = self.clear("editor")
        self.heading(outer, "Update questions", "Local question editor for the person managing this game.")
        form = tk.Frame(outer, bg=CARD)
        form.pack(fill="x", pady=8, ipadx=12, ipady=10)
        fields = {}
        for row, (key, title) in enumerate((("prompt", "Fraction question"), ("topic", "Topic"),
                                            ("A", "Answer A"), ("B", "Answer B"),
                                            ("C", "Answer C"), ("D", "Answer D"),
                                            ("explanation", "Explanation"))):
            self.label(form, title, 11, MUTED).grid(row=row, column=0, sticky="w", padx=14, pady=4)
            field = tk.Entry(form, font=("Segoe UI", 11), bg=BG, fg=INK, insertbackground=INK,
                             relief="flat", width=65)
            field.grid(row=row, column=1, sticky="ew", padx=14, pady=4, ipady=5)
            fields[key] = field
        form.columnconfigure(1, weight=1)
        self.label(form, "Correct answer", 11, MUTED).grid(row=7, column=0, sticky="w", padx=14, pady=4)
        correct = ttk.Combobox(form, values=("A", "B", "C", "D"), state="readonly", width=8)
        correct.set("A")
        correct.grid(row=7, column=1, sticky="w", padx=14, pady=4)
        editing_index = [None]

        def add_question():
            if editing_index[0] is None and len(self.custom) >= 100:
                messagebox.showerror("Question limit", "The limit is 100 custom questions.")
                return
            try:
                question = question_from_dict({"prompt": fields["prompt"].get(), "topic": fields["topic"].get(),
                    "choices": [fields[c].get() for c in "ABCD"], "correct": "ABCD".index(correct.get()),
                    "explanation": fields["explanation"].get()})
            except ValueError as exc:
                messagebox.showerror("Check the question", str(exc))
                return
            if editing_index[0] is None:
                self.custom.append(question)
            else:
                self.custom[editing_index[0]] = question
            self.persist()
            self.editor()

        action_button = self.button(form, "Add question", add_question, True)
        action_button.grid(row=8, column=1, sticky="w", padx=14, pady=10)

        def edit_question(index):
            question = self.custom[index]
            editing_index[0] = index
            for field, value in (("prompt", question.prompt), ("topic", question.topic),
                                 ("explanation", question.explanation),
                                 *((letter, question.choices[i]) for i, letter in enumerate("ABCD"))):
                fields[field].delete(0, "end")
                fields[field].insert(0, value)
            correct.set("ABCD"[question.correct])
            action_button.config(text="Save changes")
            fields["prompt"].focus_set()
        self.label(outer, f"MY QUESTIONS: {len(self.custom)}", 12, LIME, True).pack(anchor="w", pady=(12, 2))
        list_frame = tk.Frame(outer, bg=BG)
        list_frame.pack(fill="x")
        for index, question in enumerate(self.custom[-4:]):
            real_index = len(self.custom) - min(4, len(self.custom)) + index
            row = tk.Frame(list_frame, bg=CARD)
            row.pack(fill="x", pady=3)
            self.label(row, question.prompt[:90], 11, INK).pack(side="left", padx=12, pady=8)
            self.button(row, "Remove", lambda i=real_index: self.remove_question(i)).pack(side="right", padx=8, pady=4)
            self.button(row, "Edit", lambda i=real_index: edit_question(i)).pack(side="right", padx=8, pady=4)
        if len(self.custom) > 4:
            self.label(outer, "Showing the four newest questions; all are included in the game.", 10, MUTED).pack(anchor="w")
        self.button(outer, "← Main menu", self.menu).pack(anchor="w", pady=12)

    def remove_question(self, index):
        self.custom.pop(index)
        self.persist()
        self.editor()

    def on_key(self, event):
        if self.screen != "game" or not self.game:
            return
        if event.keysym == "Escape":
            if self.game.state == "Paused" and hasattr(self, "pause_window") and self.pause_window.winfo_exists():
                self.game.resume()
                self.pause_window.destroy()
            elif self.game.state == "Playing":
                self.pause()
            return
        if self.game.state != "Playing":
            return
        if event.keysym in ("Return", "KP_Enter") and self.game.answered:
            self.advance()
        elif not self.game.answered and event.char.upper() in "ABCD" and len(event.char) == 1:
            self.answer("ABCD".index(event.char.upper()))
