# Run Reading Buddy on your own computer

About 10 minutes, start to finish. Works on macOS, Windows and Linux.

## 1. What you need

- **Python 3.10 or newer.**
  - Check with `python3 --version` (macOS/Linux) or `py --version` (Windows).
  - If it's missing, get it from https://www.python.org/downloads/. On Windows, tick **"Add python.exe to PATH"** in the installer.
- **Git.**
  - Check with `git --version`.
  - If it's missing, get it from https://git-scm.com/downloads.
- **Chrome, Edge or Safari**, and a microphone. A headset is best, so Buddy's voice doesn't feed back into the mic.
- **The team's Gnani API key.** Ask the teammate who registered for the challenge. It is **never** in GitHub: share it privately (in person or a private message), never in a public post or a commit.

## 2. Get the code

```bash
git clone https://github.com/Rishiii57/reading-buddy.git
```

```bash
cd reading-buddy
```

## 3. Install

**macOS / Linux**

```bash
python3 -m venv .venv
```

```bash
.venv/bin/pip install -r requirements-dev.txt
```

**Windows (PowerShell)**

```powershell
py -m venv .venv
```

```powershell
.venv\Scripts\pip install -r requirements-dev.txt
```

## 4. Add the API key

Copy the example settings file and put the key in it.

**macOS / Linux**

```bash
cp .env.example .env
```

**Windows**

```powershell
copy .env.example .env
```

Open `.env` in any text editor and fill in the key after the `=`, with no spaces or quotes:

```text
GNANI_API_KEY=vach_xxxxxxxxxxxxxxxx
```

`.env` is listed in `.gitignore`, so git will never upload it. Don't rename it, and never paste the key into any other file.

## 5. Check everything works (no API calls, no credits)

**macOS / Linux**

```bash
.venv/bin/python -m pytest -q
```

**Windows**

```powershell
.venv\Scripts\python -m pytest -q
```

You should see `42 passed`.

## 6. Start the app

**macOS / Linux**

```bash
.venv/bin/uvicorn backend.main:app --port 8765
```

**Windows**

```powershell
.venv\Scripts\uvicorn backend.main:app --port 8765
```

Leave that window open, then open **http://localhost:8765** in Chrome, Edge or Safari. To stop the app, press `Ctrl+C` in that window.

## 7. Try it

1. Pick a language, then a poem.
2. **Without a microphone:** press **Demo reader**. A synthetic child voice (a Gnani Timbre voice, not a real child) reads the poem with one wrong word and one pause, and answers Buddy. You'll see the whole teaching loop:
   - Buddy greets and reads the first line.
   - Word practice ("Let's practise this word together").
   - The whole line again.
   - A stall prompt ("Listen…").
   - The finish, and the summary.
3. **With the microphone:** press the big microphone.
   - The first time, the browser asks for mic permission. Click **Allow**.
   - Wait for Buddy's greeting, then read aloud. Some things to try:
     - Read a word wrong (Buddy practises it with you).
     - Stop mid-line (Buddy gives the next words).
     - Say "I'm tired" (Buddy offers a break).
4. **Listen first** has Buddy read the whole poem aloud before you start.

The microphone only works on `localhost` or an `https://` address. Opening the app as `http://<some-ip>:8765` from another device will block the mic.

## 8. Recording test sessions (optional, consenting team members only)

To keep a log of what the speech model heard and what Buddy decided, which is useful for test rounds, start the app with session saving on.

**macOS / Linux**

```bash
SAVE_SESSIONS=1 .venv/bin/uvicorn backend.main:app --port 8765
```

**Windows (PowerShell)**

```powershell
$env:SAVE_SESSIONS="1"; .venv\Scripts\uvicorn backend.main:app --port 8765
```

Logs go to `cache/sessions/` (never committed). Only record team members who agree. The challenge rules forbid recording other children.

## 9. Re-score the tutor (optional, no credits)

```bash
.venv/bin/python -m eval.replay
```

(Windows: `.venv\Scripts\python -m eval.replay`.) This replays the recorded synthetic readings through the tutor and rewrites `eval/RESULTS.md`. Only `python -m eval.run_stt` and `python -m eval.make_testset` call the API. You don't need them unless you change the test set.

## Troubleshooting

| Problem | Fix |
|---|---|
| `Address already in use` | Something else uses port 8765. Use `--port 8766` and open http://localhost:8766 |
| `GNANI_API_KEY is not set` | `.env` is missing or misspelled, or isn't in the project folder |
| "Could not reach the speech service" | Check the key and your internet connection. A `401` in the terminal means the key is wrong |
| Buddy is slow the first time it says something new | It's creating that clip with Timbre (about 1 s). After that it's cached in `cache/tts/` |
| `429 Too Many Requests` in the terminal | The API rate limit; the app retries by itself. Avoid opening many sessions at once |
| No sound from Buddy | Unmute the tab, and click on the page once (browsers block sound until you interact) |
| The microphone doesn't work | Allow the mic in the browser's address-bar settings; on macOS also check System Settings → Privacy & Security → Microphone for your browser |
| `pip` or `python` not found on Windows | Re-install Python with "Add python.exe to PATH" ticked, or use `py` instead of `python` |

## Credits

Every session streams audio to Gnani Prisma and may create new Timbre clips. Both come out of the team's 5,000 challenge credits. Common phrases and lines are already cached in the repo. Check the balance at https://app.gnani.ai/voice now and then.
