# PodcastIQ — Agent Handover

## Project Summary
Ironhack Week 2 group project. Automated two-host podcast generator focused on **AI startups and how AI knowledge is reshaping the future of business, work, and society**.

**GitHub:** https://github.com/eugnmueller-87/PODCAST-STUDIO
**Branch strategy:** `main` = production, `develop` = team integration branch
**Launch:** Open `PODCAST.ipynb` → Run All → Gradio opens at localhost:7860 + public share URL

---

## Current Status — FULLY WORKING ✓

All blockers resolved. Full end-to-end pipeline confirmed working:
- Text → Claude/GPT-4o → Humanizer → ElevenLabs (Alex) + edge-tts (Sam) → MP3

---

## Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| LLM | Claude Sonnet `claude-sonnet-4-6` (Anthropic) | Default, temp=1.2 |
| LLM alt | GPT-4o (OpenAI) | Selectable in UI, temp=0.7 |
| TTS — Alex (host A) | ElevenLabs REST API, voice `DEZHhPbmb8LVZmWufkCh`, `eleven_v3` | Falls back to `en-GB-SoniaNeural` if no key |
| TTS — Sam (host B) | edge-tts `en-US-GuyNeural` | Free, no key needed |
| Audio | pydub + static-ffmpeg (bundled, no system install) | |
| UI | Gradio `gr.Blocks`, `share=True` for public URL | |
| Safety | 2-layer content guard: regex + Claude Haiku classifier | |
| Logging | `test_audio/run_log.jsonl` + `test_audio/ratings.csv` | |

---

## Project Structure

```
podcast-studio/
├── PODCAST.ipynb              ← entry point — Run All launches Gradio
├── src/
│   ├── models.py              ← dataclasses + LLMProvider/PodcastStyle enums
│   ├── data_processor.py      ← PDF / URL / YouTube / Text → PodcastInput
│   ├── llm_processor.py       ← Anthropic + OpenAI API calls, prompt builder, parser
│   ├── humanizer.py           ← 3-layer post-processor: reactions, openers, Sam humour
│   ├── content_guard.py       ← regex blocklist + Claude Haiku safety classifier
│   ├── tts_generator.py       ← ElevenLabs (Alex) + edge-tts (Sam), prosody, async
│   └── main.py                ← Gradio UI, run logger, rating saver
├── prompts/
│   ├── educational.txt        ← Alex teaches, Sam questions
│   ├── debate.txt             ← Alex (optimist) vs Sam (sceptic)
│   ├── news_brief.txt         ← co-anchor NPR style, punchy
│   └── deep_dive.txt          ← long-form, tangents, second-order effects
├── test_audio/                ← MP3 outputs + run_log.jsonl + ratings.csv (gitignored)
├── assets/studio.svg          ← illustrated header for README
├── .env                       ← ANTHROPIC_API_KEY, OPENAI_API_KEY, ELEVENLABS_API_KEY
├── .env.example               ← template (safe to commit)
├── requirements.txt
├── QUALITY.md                 ← code quality ratings 1-10 per file
├── README.md
├── TODO.md
└── HANDOVER.md                ← this file
```

---

## How to Run

1. Open `PODCAST.ipynb` from the `podcast-studio/` folder
2. Select the `.venv` kernel (Python 3.14+)
3. Press **Run All**
4. Gradio opens at `http://localhost:7860` + prints a public `gradio.live` URL (valid 72h)

---

## API Keys Required

All keys go in `.env` (never committed):

```
ANTHROPIC_API_KEY=sk-ant-...     # Claude script generation (default provider)
OPENAI_API_KEY=sk-...            # GPT-4o script generation (optional, selectable in UI)
ELEVENLABS_API_KEY=...           # Alex's voice — falls back to SoniaNeural if missing
```

---

## Pipeline Flow

```
User input (Text / URL / PDF / YouTube)
    │
    ▼ data_processor.py
PodcastInput(text, title, word_count)
    │
    ▼ content_guard.py  ← LAYER 1: blocks harmful input
    │
    ▼ llm_processor.py  ← Claude or GPT-4o generates dialogue at temp 1.2 / 0.7
PodcastScript(lines, metadata)
    │
    ▼ humanizer.py      ← adds reactions, openers, Sam humour (30% chance per line)
    │
    ▼ content_guard.py  ← LAYER 2: blocks harmful generated content
    │
    ▼ tts_generator.py  ← asyncio.gather parallel synthesis
        Alex lines → ElevenLabs REST API (eleven_v3)
        Sam lines  → edge-tts en-US-GuyNeural
        Prosody: pitch/rate per emotional context
        Mid-sentence silences: — = 420ms, ... = 700ms
        Between-turn pauses: 300ms – 1600ms dynamic
    │
    ▼ test_audio/episode_{provider}_{timestamp}.mp3
    │
    ▼ run_log.jsonl  ← every run logged (success / error / blocked)
```

---

## Output File Naming

Files are named by LLM provider so runs can be compared:
```
test_audio/episode_anthropic_1714234567.mp3
test_audio/episode_openai_1714234567.mp3
```

---

## Logging Files

### `test_audio/run_log.jsonl`
One JSON line per run. Fields: `timestamp`, `status` (success/error/blocked), `llm_provider`, `elapsed_seconds`, `source_type`, `style`, `host_a`, `host_b`, `target_minutes`, `source_words`, `dialogue_lines`, `audio_duration_min`, `audio_file`, `title`, `summary`, `tags`, `script`, `error`.

### `test_audio/ratings.csv`
One row per user rating submission. Fields: `timestamp`, `audio_file`, `transcript_rating` (1-5), `audio_rating` (1-5), `notes`.

---

## Key Code Locations

| What | File | Line |
|---|---|---|
| LLM provider switch | `src/llm_processor.py` | `generate_script()` |
| Claude API call | `src/llm_processor.py` | `_call_anthropic()` |
| OpenAI API call | `src/llm_processor.py` | `_call_openai()` |
| Prompt loading | `src/llm_processor.py` | `_load_prompt()` |
| Script parser | `src/llm_processor.py` | `_parse_script()` |
| Safety guard | `src/content_guard.py` | `check()` |
| Humanizer layers | `src/humanizer.py` | `humanize_script()` |
| ElevenLabs call | `src/tts_generator.py` | `_elevenlabs_synthesise()` |
| Voice ID (Alex) | `src/tts_generator.py` | `HOST_A_VOICE_ID` |
| Prosody logic | `src/tts_generator.py` | `_prosody_params()` |
| Pause logic | `src/tts_generator.py` | `_pause_ms()` |
| Gradio UI | `src/main.py` | `with gr.Blocks(...)` |
| Run logger | `src/main.py` | `_log_run()` |
| Rating saver | `src/main.py` | `save_rating()` |

---

## Resolved Issues (do not re-open)

| Issue | Fix |
|---|---|
| ffmpeg not in PATH | `static-ffmpeg` pip package — bundles ffmpeg, no system install |
| YouTube API changed | `api.fetch(video_id)` with language fallback |
| Gradio event loop conflict | `asyncio.new_event_loop()` in `synthesise_script()` |
| TTS too slow (26s sequential) | `asyncio.gather()` → parallel → ~4s for 20 lines |
| PDF input unusable | Changed from Textbox to `gr.File(file_types=[".pdf"])` |
| Content guard crashes on OpenAI-only | `_claude_check()` skips silently if no Anthropic key |
| OpenAI too erratic | Temperature lowered to 0.7 (Claude stays at 1.2) |
| ElevenLabs SDK Windows long-path error | Using REST API via `requests` directly — no SDK |

---

## Known Limitations

- Gradio public share URL expires after 72h — restart notebook to get a new one
- ElevenLabs free tier: 10,000 chars/month (~5-6 episodes)
- YouTube IP rate limiting — if blocked, wait 30-60 min and retry
- OpenAI key must be in `.env` to use GPT-4o provider

---

## Team Branch Workflow

```bash
git checkout develop          # always start from develop
git pull origin develop       # get latest
git checkout -b feature/name  # your own branch
# ... make changes ...
git push origin feature/name  # push your branch
# open Pull Request: feature/name → develop on GitHub
```

---

## Demo Script (5-7 min)

1. **Intro** — PodcastIQ turns any AI article into a two-host podcast in under 60 seconds
2. **Live demo** — paste URL → Deep Dive → Generate → audio plays
3. **Backup input** (if live fails):
   > "Anthropic has raised $2.75 billion in its latest funding round, valuing the AI startup at $18.4 billion. The company develops Claude — a family of large language models focused on safety and alignment. Investors include Google and Spark Capital."
4. **Show features** — switch to OpenAI provider, show run_log.jsonl, show rating UI
5. **Close** — what we'd add: ElevenLabs voice cloning, RSS export, multi-language

---

*Last updated: April 2026 — all systems operational*
