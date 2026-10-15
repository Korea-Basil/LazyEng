# LazyEng — English Quiz Workbook | 초보자 영어 기초 퀴즈

A friendly, offline English-learning app for beginners, presented as a warm paper-style GUI instead of a command-line quiz. Choose **Elementary (초등)**, **Middle School (중등)**, or **High School (고등)** and practice with exactly 20 multiple-choice questions per session.

Each answer reveals Korean pronunciation guides, word meanings and parts of speech, a plain-language grammar explanation, and feedback for every answer choice. The question banks and quiz mechanics are unchanged; the interface uses Python's built-in Tkinter library.

## Features

- Warm parchment palette, readable workbook-style question cards, and progress header.
- Three curated levels with 20 questions in each level's bank.
- Four clickable answer tiles, answer feedback, and next-question navigation.
- Detailed Korean grammar and word explanations with Hangul pronunciation guides.
- Score screen with an invitation to retry or choose another level.
- Runs entirely offline. No analytics, telemetry, accounts, or network requests.
- Tkinter UI uses only Python's standard library; no UI package installation needed.

## Requirements

- Python 3.10 or newer with Tcl/Tk included (the standard Windows Python installer includes Tkinter).
- Windows, macOS, or Linux desktop environment.

## Run from source

Clone the repository and open a terminal in its directory:

```bash
git clone https://github.com/your-username/english-step-by-step-quiz.git
cd english-step-by-step-quiz
python main.py
```

The level-selection window opens. Choose Elementary, Middle School, or High School to begin.

## Build a standalone Windows GUI executable

The single-file executable runs without Python installed on the target PC. Build it on Windows with PowerShell:

```powershell
python -m pip install -r requirements-build.txt
.\build_windows.ps1
```

The windowed executable is created at `dist\EnglishQuiz.exe`. Double-click it to start; it opens the GUI without a console window. To rebuild it directly:

```powershell
python -m PyInstaller --noconfirm --clean --onefile --noconsole --name EnglishQuiz main.py
```

PyInstaller is needed only on the build machine and is not required to run the `.exe`. The build script uses `--noconsole` to create a single-window GUI app. Build Windows executables on Windows. Review and scan the resulting executable before distributing it; unsigned self-extracting applications may receive antivirus warnings.

## Project layout

```text
.
├── main.py                  # GUI entry point
├── gui.py                   # Tkinter screens and user interaction
├── quiz_engine.py           # Question model, answer checking, session state
├── data_loader.py           # Level validation and Korean word guides
├── questions/
│   ├── __init__.py
│   ├── elementary.py        # 초등 bank (20 questions)
│   ├── middle.py            # 중등 bank (20 questions)
│   └── high.py              # 고등 bank (20 questions)
├── tests/
│   └── test_quiz_program.py
├── build_windows.ps1        # Build the one-file, no-console .exe
├── requirements-build.txt   # Build-only PyInstaller dependency
├── .gitignore
├── LICENSE
└── README.md
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

The tests use Python's built-in `unittest` framework and do not need a network connection or extra packages.

## Security & Privacy Guarantee

- **Offline operation:** The app has no network client, analytics, telemetry, update checker, or online service integration. It does not make network requests.
- **No collection or logging:** Answers and quiz progress are held in memory for the current session. The app does not save, upload, or log responses or scores.
- **No user-file access:** The app reads its bundled/local question modules only. It does not prompt for paths, open user-selected files, or modify question banks.
- **Restricted inputs:** Learners select from fixed levels and four answer choices. Input is not interpreted as a command, evaluated as code, or used to construct a path.
- **No risky execution:** The application does not use `eval`, `exec`, shell commands, or subprocesses.
- **Executable transparency:** PyInstaller is a build-time tool. A one-file PyInstaller executable extracts bundled runtime components to a temporary directory while it runs; this is bootloader behavior, not storage of quiz data. The quiz itself creates no persistent user data. Build only from source you trust and scan distributed executables. Antivirus products may flag unsigned self-extracting files; no project can guarantee how every antivirus classifies an executable.

These statements describe the application's code and intended behavior, not an absolute guarantee that any software or third-party build environment is risk-free. Obtain build tools from trusted sources and verify release artifacts.

## Learning note

Hangul pronunciation is an approachable reading guide, not a perfect representation of English sounds. Use it alongside the original spelling and meaning. The questions cover selected grammar points and are a study aid, not a complete English course.

## License

Released under the [MIT License](LICENSE).
