# PodcastIQ — TODO & Progress Tracker

> Status as of April 2026. ✅ = done, 🔄 = in progress, ⬜ = not started.

---

## Core Pipeline — ✅ COMPLETE

- ✅ `models.py` — dataclasses: PodcastInput, PodcastScript, DialogueLine, EpisodeMetadata, AudioOutput, PodcastSettings, LLMProvider enum
- ✅ `data_processor.py` — Text / PDF / URL / YouTube → unified `process()`
- ✅ `llm_processor.py` — Claude Sonnet (temp 1.2) + GPT-4o (temp 0.7), selectable per run
- ✅ `humanizer.py` — 3-layer post-processor: reactions (45%), openers (25%), self-corrections (15%), Sam humour (30%)
- ✅ `content_guard.py` — regex blocklist + Claude Haiku classifier, two checkpoints
- ✅ `tts_generator.py` — ElevenLabs (Alex) + edge-tts (Sam), parallel asyncio, prosody, mid-sentence silence
- ✅ `main.py` — Gradio UI, LLM provider toggle, progress bar, run logger, rating UI

---

## Prompt Templates — ✅ COMPLETE

- ✅ `educational.txt` — Alex teaches, Sam questions; Sam humour rule added
- ✅ `debate.txt` — Alex optimist vs Sam sceptic; Sam humour rule added
- ✅ `news_brief.txt` — co-anchor NPR style; Sam dry wit rule added
- ✅ `deep_dive.txt` — long-form exploratory; Sam humour rule added
- ✅ All templates: HUMANISATION RULES section with contractions, trailing dashes, interruptions

---

## Infrastructure — ✅ COMPLETE

- ✅ Virtual environment (`.venv/`)
- ✅ `requirements.txt` — all packages pinned
- ✅ `.env` — ANTHROPIC_API_KEY, OPENAI_API_KEY, ELEVENLABS_API_KEY
- ✅ `.gitignore` — protects .env, test_audio logs, .venv, gradio log files
- ✅ `PODCAST.ipynb` — 3 cells, Run All → Gradio launches
- ✅ GitHub: https://github.com/eugnmueller-87/PODCAST-STUDIO
- ✅ Branch strategy: `main` (production) + `develop` (team)
- ✅ `share=True` — public gradio.live URL on every launch

---

## Logging & Quality — ✅ COMPLETE

- ✅ `test_audio/run_log.jsonl` — every run logged (inputs, settings, script, timing, status)
- ✅ `test_audio/ratings.csv` — 1-5 star ratings for transcript + audio quality
- ✅ `QUALITY.md` — code quality ratings 1-10 per file with improvement notes
- ✅ Quality header comment in every `src/` file
- ✅ Output files named by provider: `episode_anthropic_*.mp3` / `episode_openai_*.mp3`

---

## Security — ✅ COMPLETE

- ✅ Content guard blocks racism, hate speech, foul language
- ✅ Two checkpoints: source input + generated script
- ✅ Graceful fallback if Anthropic key not set (keyword layer still runs)
- ✅ User-facing message: "🚫 Blocked for Harmful Content"
- ✅ Blocked attempts logged with `status: "blocked"`

---

## Open Items — ⬜ REMAINING

### Demo prep
- ⬜ Generate 3 example episodes (educational / debate / deep_dive) and save to `test_audio/`
- ⬜ Test with live URL (TechCrunch / Wired AI article)
- ⬜ Test with YouTube AI talk
- ⬜ Test with PDF research paper
- ⬜ Prepare 5-slide deck (see HANDOVER.md for structure)
- ⬜ Dry run full demo end-to-end (target < 60s generation)

### Nice to have (stretch)
- ⬜ Background music — mix low-volume ambient track under voices with pydub
- ⬜ RSS feed export — valid `feed.xml` for podcast app import
- ⬜ Multi-language support — detect source language, generate in same language
- ⬜ Batch mode — queue multiple URLs, generate asynchronously
- ⬜ Deploy to Hugging Face Spaces — permanent public URL (no 72h expiry)
- ⬜ ElevenLabs voice cloning — custom voice trained on sample audio

---

## Quick Commands

```bash
# Launch (from notebook)
PODCAST.ipynb → Run All

# Launch (from terminal)
.venv/Scripts/python.exe src/main.py

# Install new package
.venv/Scripts/pip.exe install <package>

# Lint
.venv/Scripts/ruff.exe check src/

# Git team flow
git checkout develop && git pull origin develop
git checkout -b feature/your-name-task
git push origin feature/your-name-task
# → open PR into develop on GitHub
```

---

*Updated April 2026*
