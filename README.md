# PodcastIQ — Automated Two-Host Podcast Studio

> Drop any article, PDF, YouTube link, or plain text — get a publish-ready two-host podcast episode in under 60 seconds.

📋 [Post-Project Review & Stakeholder Report](Report/post_project_review_podcastiq.md)

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Gradio](https://img.shields.io/badge/UI-Gradio%206-orange.svg)](https://gradio.app/)
[![Claude](https://img.shields.io/badge/LLM-Claude%20Sonnet-blueviolet.svg)](https://anthropic.com/)
[![GPT-4o](https://img.shields.io/badge/LLM-GPT--4o-412991.svg)](https://openai.com/)
[![ElevenLabs](https://img.shields.io/badge/TTS-ElevenLabs-black.svg)](https://elevenlabs.io/)
[![edge-tts](https://img.shields.io/badge/TTS-edge--tts-brightgreen.svg)](https://github.com/rany2/edge-tts)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

![PodcastIQ Studio](assets/studio.svg)

---

## What It Does

PodcastIQ is an automated podcast studio that turns any content into a two-host podcast episode. Feed it any source — a news article, a research PDF, a YouTube talk, or raw notes — and it returns a fully produced audio episode with two distinct hosts, a downloadable MP3, and auto-generated episode metadata. The tool adapts to whatever topic the content covers — no subject-matter restrictions.

The show features two recurring hosts: **Alex** (ElevenLabs premium voice — the expert deep-diver) and **Sam** (Microsoft Neural edge-tts, American male — the curious generalist with dry wit). Their contrasting voices and perspectives make every episode feel like a genuine conversation.

```
   INPUT                  PROCESS                        OUTPUT
┌──────────┐    ┌──────────────────────────────┐    ┌────────────────┐
│ PDF      │    │  1. Extract & clean source   │    │ 🎙 MP3 audio   │
│ URL      │───▶│  2. Claude writes the script │───▶│ 📄 Full script │
│ YouTube  │    │  3. Humanizer adds realism   │    │ 🏷 Metadata    │
│ Text     │    │  4. edge-tts voice per host  │    │ ⭐ Rating log  │
└──────────┘    │  5. Stitch & export MP3      │    │ 📋 Run log     │
                └──────────────────────────────┘    └────────────────┘
```

---

## Features

### Core Pipeline
- **Multi-source ingestion** — PDF upload, article URL scraping, YouTube transcript extraction, raw text paste
- **Four podcast styles** — Educational, Debate, News Brief, Deep Dive (each with its own prompt)
- **Dual LLM provider** — Claude Sonnet (temp 1.2) or GPT-4o (temp 0.7), selectable in the UI
- **3-layer humanizer** — script-level reactions, openers, self-corrections + Sam's dry humour injections
- **Premium voices per host** — Alex: ElevenLabs `eleven_v3` (falls back to `en-GB-SoniaNeural`), Sam: `en-US-GuyNeural`
- **Emotional prosody** — pitch and rate adapt per line (questions rise, excitement speeds up, reflection slows)
- **Mid-sentence silences** — em-dashes (420ms) and ellipses (700ms) become real pauses in the audio
- **Topic-agnostic** — all four prompt styles follow the source content; no hardcoded subject area
- **Voice status feedback** — UI shows which voice was used for Alex and why (ElevenLabs, edge-tts fallback, or no key)
- **Content safety guard** — 2-layer check (regex + Claude Haiku) blocks harmful content at input and output
- **Episode metadata** — title, one-sentence summary, tags, and estimated listen time

### Output & Logging
- **`test_audio/`** — all MP3 files land here, named `episode_<timestamp>.mp3`
- **`test_audio/run_log.jsonl`** — one JSON line per run: inputs, settings, timing, script, metadata, errors
- **`test_audio/ratings.csv`** — in-app 1–5 star ratings for transcript and audio quality with notes

### Interface
- Dark studio-themed Gradio UI with illustrated hosts
- Real-time progress bar through each pipeline stage
- Audio player + one-click MP3 download
- Expandable script and metadata panels
- Rating accordion to score each episode and leave notes

### Podcast Styles

| Style | Format |
|---|---|
| `educational` | Alex teaches, Sam asks — structured knowledge transfer |
| `debate` | Hosts argue opposing sides and reach a conclusion |
| `news_brief` | Crisp co-anchor format, headline-first, punchy |
| `deep_dive` | Long-form exploration with tangents, analogies, second-order effects |

---

## Project Structure

```
podcast-studio/
├── src/
│   ├── models.py           # Dataclasses for the pipeline
│   ├── data_processor.py   # Input handlers: PDF, URL, YouTube, text
│   ├── llm_processor.py    # Claude script generation (Anthropic API)
│   ├── humanizer.py        # Post-generation realism layer (reactions, humour)
│   ├── content_guard.py    # Safety guard — blocks hate speech, racism, foul language
│   ├── tts_generator.py    # edge-tts + prosody + pydub audio stitching
│   └── main.py             # Gradio UI, run logger, rating saver
├── prompts/
│   ├── educational.txt
│   ├── debate.txt
│   ├── news_brief.txt
│   └── deep_dive.txt
├── test_audio/             # Generated MP3s, run_log.jsonl, ratings.csv (gitignored)
├── assets/
│   └── studio.svg          # Illustrated header for README
├── PODCAST.ipynb           # One-click launcher (Run All → Gradio opens)
├── .env.example
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/eugnmueller-87/PODCAST-STUDIO.git
cd PODCAST-STUDIO
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API key

```bash
cp .env.example .env
# Open .env and paste your Anthropic API key
```

| Variable | Required | Where to get it |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | [console.anthropic.com](https://console.anthropic.com) |
| `ELEVENLABS_API_KEY` | Optional | [elevenlabs.io](https://elevenlabs.io) — premium voice for Alex (falls back to edge-tts if missing) |
| `OPENAI_API_KEY` | Optional | [platform.openai.com](https://platform.openai.com/api-keys) — enables GPT-4o as alternative LLM |

### 5. Launch

**Option A — Jupyter notebook (recommended)**

Open `PODCAST.ipynb` and click **Run All**.

**Option B — terminal**

```bash
python src/main.py
```

Open `http://localhost:7860` in your browser.

---

## Usage

1. **Choose source type** — Text, URL, YouTube, or PDF
2. **Paste / upload your content**
3. **Pick a podcast style** and set host names + target length
4. Click **Generate Episode**
5. Listen, read the script, download the MP3
6. **Rate the episode** (1–5 stars for transcript and audio) — saved to `test_audio/ratings.csv`

### Example inputs that work well

- A TechCrunch or Wired article URL
- A research paper or slide deck PDF
- A YouTube talk or interview (transcript extracted automatically)
- A block of raw notes or bullet points

---

## Architecture

### Full pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                        Gradio UI (main.py)                      │
│  Source input → Settings → [Generate Episode] → Audio + Script  │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────▼──────────────┐
              │   Step 1 — data_processor.py │
              │   Ingest & normalise source  │
              └──────────────┬──────────────┘
                             │ PodcastInput(text, title, word_count)
              ┌──────────────▼──────────────┐
              │   Step 2 — llm_processor.py  │
              │   Claude generates dialogue  │
              │   temperature=1.2            │
              └──────────────┬──────────────┘
                             │ PodcastScript(lines, metadata)
              ┌──────────────▼──────────────┐
              │   Step 3 — humanizer.py      │
              │   Reactions, openers,        │
              │   self-corrections, humour   │
              └──────────────┬──────────────┘
                             │ PodcastScript (humanized)
              ┌──────────────▼──────────────┐
              │   Step 4 — tts_generator.py  │
              │   edge-tts + prosody params  │
              │   asyncio.gather (parallel)  │
              │   pydub → MP3               │
              └──────────────┬──────────────┘
                             │ AudioOutput(file_path, duration_seconds)
                             ▼
              test_audio/episode_<timestamp>.mp3
              test_audio/run_log.jsonl  ← logged here
```

---

### Step 1 — Data Ingestion (`src/data_processor.py`)

| Source | How it works |
|---|---|
| **Text** | Strips whitespace, counts words, passes through |
| **URL** | `requests` fetches the page; `BeautifulSoup` extracts `<p>` tags > 40 chars |
| **PDF** | **Primary:** Claude Haiku native PDF understanding (tables, columns, scanned pages via vision). **Fallback:** `PyPDF2` if no `ANTHROPIC_API_KEY` or if the Haiku call fails |
| **YouTube** | `youtube-transcript-api` fetches transcript by video ID; falls back to any available language |

---

### Step 2 — Script Generation (`src/llm_processor.py`)

- Model: **Claude Sonnet (`claude-sonnet-4-6`)**, temperature **1.2**
- Style-specific prompt loaded from `prompts/{style}.txt`
- Template variables: `source_text`, `target_minutes`, `word_count_target`, `host_a_name`, `host_b_name`
- Target word count: `target_minutes × 150 words/min`

**Claude returns:**
```
ALEX: Did you see Anthropic just raised $2.75 billion?
SAM: That's massive. And somewhere a VC is nodding very seriously right now.
...
TITLE: The AI Funding Race Nobody Saw Coming
SUMMARY: Alex and Sam unpack what Anthropic's raise means for the safety-first bet.
TAGS: Anthropic, funding, AI safety, LLM
DURATION: 5
```

**Prompt styles:**

| Style | Alex | Sam |
|---|---|---|
| `educational` | Expert teacher | Curious student |
| `debate` | Optimist / advocate | Sceptic / critic |
| `news_brief` | Lead anchor — facts | Colour anchor — so what |
| `deep_dive` | Technical researcher | Market strategist |

---

### Step 3 — Humanizer (`src/humanizer.py`)

Post-processes Claude's script before audio generation:

| Layer | What it adds | Probability |
|---|---|---|
| Reaction | `"Hmm."` / `"Right."` / `"Wait —"` prepended based on previous line | 45% |
| Opener | `"You know,"` / `"Here's the thing —"` etc. | 25% |
| Self-correction | Mid-sentence `" — or, actually, "` / `" — scratch that —"` | 15% |
| Sam quip | Dry humour appended: `"Classic Silicon Valley — disrupt first, apologise later."` | 30% |
| Sam self-deprecation | `"— don't fact-check me on that, I'm going from memory."` | 15% |

---

### Step 4 — Audio Generation (`src/tts_generator.py`)

**Voices:**
- Alex → ElevenLabs REST API, `eleven_v3`, voice ID `DEZHhPbmb8LVZmWufkCh` (falls back to `en-GB-SoniaNeural` if no ElevenLabs key)
- Sam → `en-US-GuyNeural` via edge-tts (free, always available)

**Prosody per line** (rate + pitch):

| Trigger | Rate | Pitch |
|---|---|---|
| Line ends with `?` | −8% | +10 Hz |
| Excited words (`wow`, `incredible`, `exactly`…) | +10% | +8 Hz |
| Thoughtful words (`honestly`, `I'm not sure`…) | −12% | −6 Hz |
| Emphatic words (`never`, `here's the thing`…) | −5% | +4 Hz |
| Default | −5% | 0 Hz |

**Mid-sentence silence:**
- Em-dash `—` → 420 ms silence
- Ellipsis `...` → 700 ms silence

**Between-turn pauses:**
- After a question: 300–500 ms
- Short reaction: 350–600 ms
- Topic breath (every 5 lines): 1000–1600 ms
- After long statement: 700–1000 ms
- Default: 500–850 ms

All lines are synthesised **in parallel** via `asyncio.gather()` — a 20-line episode takes ~4s instead of ~30s.

---

### Security — Content Safety Guard (`src/content_guard.py`)

All content passes through a two-layer safety check **before** reaching Claude and **after** the script is generated.

**Layer 1 — Keyword regex** (instant, no API call)
Compiled regex patterns catch obvious slurs, hate phrases, and calls for violence immediately.

**Layer 2 — Claude Haiku classifier** (`temperature=0`, ~60 tokens)
Detects subtle and contextual violations that a keyword list would miss — coded language, implied discrimination, targeted abuse.

**What is blocked:**
- Racism and racial slurs
- Hate speech targeting any group (religion, gender, sexuality, ethnicity, nationality, disability)
- Calls for violence or discrimination
- Severe foul or abusive language intended to demean

**Two checkpoints:**
1. Source input — checked before anything is sent to Claude
2. Generated script — checked after humanization, before audio is made

**On violation**, the UI shows:
```
🚫 Content Blocked

Content blocked in source input: Contains a racial slur targeting [group].

PodcastIQ does not process content that contains racism, hate speech,
foul language, or discrimination of any kind.
```

Blocked attempts are logged to `run_log.jsonl` with `"status": "blocked"`.

---

### Logging (`test_audio/`)

**`run_log.jsonl`** — appended on every run:
```json
{
  "timestamp": "2026-04-27 14:32:01",
  "status": "success",
  "elapsed_seconds": 22.4,
  "source_type": "URL",
  "style": "Deep Dive",
  "host_a": "Alex",
  "host_b": "Sam",
  "target_minutes": 5,
  "source_words": 842,
  "dialogue_lines": 18,
  "audio_duration_min": 4.7,
  "audio_file": "episode_1234567890.mp3",
  "title": "...",
  "summary": "...",
  "tags": ["..."],
  "script": "ALEX: ...\n\nSAM: ..."
}
```

**`ratings.csv`** — one row per user rating submission:
```
timestamp, audio_file, transcript_rating, audio_rating, notes
2026-04-27 14:35:00, episode_1234567890.mp3, 4, 5, "Sam's humour landed well"
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+ |
| UI | Gradio 6.x |
| LLM (default) | Claude Sonnet 4.6 (Anthropic) — temperature 1.2 |
| LLM (alternative) | GPT-4o (OpenAI) — temperature 0.7, selectable in UI |
| TTS — Alex | ElevenLabs REST API, `eleven_v3` (falls back to edge-tts) |
| TTS — Sam | Microsoft edge-tts `en-US-GuyNeural` — free |
| Audio processing | pydub + static-ffmpeg (bundled, no system install) |
| PDF parsing | PyPDF2 |
| Web scraping | requests + BeautifulSoup4 |
| YouTube transcripts | youtube-transcript-api v2 |
| Config | python-dotenv |

---

## API Costs

| Component | Model / Service | Typical cost per episode |
|---|---|---|
| Script generation | Claude Sonnet (~8k tokens) | ~$0.03 |
| Script generation | GPT-4o (~8k tokens) | ~$0.04 |
| TTS — Alex | ElevenLabs eleven_v3 (~1,500 chars) | ~$0.02 |
| TTS — Sam | edge-tts (free) | $0.00 |
| **Total (Claude + ElevenLabs)** | | **~$0.05 per episode** |
| **Total (Claude + edge-tts fallback)** | | **~$0.03 per episode** |

---

## Roadmap

- [x] Multi-source ingestion (PDF, URL, YouTube, text)
- [x] Two-host LLM dialogue — 4 podcast styles
- [x] Distinct male/female neural voices (edge-tts)
- [x] Emotional prosody — pitch and rate per line
- [x] 3-layer humanizer + Sam humour
- [x] Parallel TTS generation (asyncio)
- [x] Episode rating UI (1–5 stars, notes)
- [x] Run log (JSONL) + ratings log (CSV)
- [x] Content safety guard (racism, hate speech, foul language blocked)
- [x] Dual LLM provider — Claude Sonnet + GPT-4o selectable in UI
- [x] ElevenLabs premium voice for Alex (with edge-tts fallback)
- [x] Topic-agnostic prompt templates — any subject, not just AI
- [x] Voice status feedback in Stats panel (which voice, why)
- [x] Claude Haiku PDF extraction (with PyPDF2 fallback)
- [ ] Background music mixer (intro/outro jingle)
- [ ] RSS feed export for podcast platforms
- [ ] Multi-language support
- [ ] Batch generation mode

---

## Contributing

Pull requests are welcome. For major changes, open an issue first.

---

## License

MIT — see [LICENSE](LICENSE)

---

*Built at Ironhack — Week 2 Group Project, April 2026*
