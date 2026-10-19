# Space Fractions — Desktop Game

A playable sixth-grade fractions game based on `Architecture_View.md` and
`Architecture_Documentation.md`. It opens as its own window. No browser,
Node.js, JavaScript setup, DeepSeek API, account, or paid service is required.

## Run on Windows

1. Extract the entire ZIP. Keep all `.py` files in the same folder.
2. Install Python 3 from python.org if it is not already installed. In the
   installer, select **Add python.exe to PATH**. The standard Tkinter GUI
   library must be included (it is part of the normal Windows Python install).
3. Double-click **run_game.bat**. A Space Fractions window opens.

In VS Code, open this folder and run `py -3 main.py` in the terminal. On a
system using `python` rather than `py`, run `python main.py`.

If `python -m tkinter` does not open a small window, reinstall Python with the
Tkinter/Tcl option enabled. This is a source project: the ZIP does not contain
a prebuilt `.exe`.

## Make a double-click EXE for a Windows computer without Python

Build **once on a Windows computer that has Python 3**:

1. Extract the ZIP and open the `space_fractions_desktop` folder.
2. Double-click `build_windows.bat` while connected to the Internet. It creates
   `.venv`, installs PyInstaller, runs five tests, and builds the game.
3. Find **`dist\SpaceFractions.exe`**. Double-click it to play, or copy that
   single `.exe` to another Windows computer. The other computer does not need
   Python, Docker, Node.js, or an API key.

The first build can take a few minutes. The executable opens its own game
window; saved scores and custom questions go into the player's Windows user
folder. This ZIP contains the source and build script, **not a prebuilt EXE**.
PyInstaller must build a Windows EXE on Windows; a Linux build cannot produce
the requested Windows binary.

## Play

Click **PLAY THE GAME**. Click one of the four gates or answer buttons, or
press A–D. Your spaceship flies to the gate. Read the explanation, then click
**Next gate** (or press Enter). Every game has ten questions, including when you
answer incorrectly. Correct answers earn points and streak bonuses. The score
updates immediately and is saved after each answer. Press Escape to pause or resume.
The main menu includes Help, Scores, and Update Questions. In Update Questions,
you can add, edit, or remove local questions. Scores and
custom questions are kept in `.space_fractions_game.json` in your Windows user
folder. Open **View scores** from the main menu to see finished and in-progress
missions. If your screen is small, use the mouse wheel or the right scroll bar
to reach the answer and Next buttons.

## Source files

| File | Purpose |
| --- | --- |
| `main.py` | Starts the desktop window |
| `gui.py` | Screens, controls, animations, and question editor |
| `game_logic.py` | Playing, Paused, GameOver, ten-question flow, and scoring |
| `questions.py` | Grade-six questions and custom-question validation |
| `storage.py` | Local JSON score and question storage |
| `tests/test_game.py` | Tests of the game rules |

Run tests with `python -m unittest discover -s tests -v` from this folder.

## Scope of the supplied documents

Both documents outline the scenario and proposed production architecture;
they do not supply exact game artwork, question bank, or rules. This local
desktop implementation covers the listed play, score, help, question update,
pause/resume, and ending-feedback behavior. The documents also propose a
web-based cloud system with microservices, OAuth, PostgreSQL, backups, and
availability goals. Those server and deployment features are not part of this
offline desktop source code. The question editor is local and has no admin
authentication.
