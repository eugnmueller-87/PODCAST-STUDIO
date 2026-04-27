# PodcastIQ — AI Startup & Future Intelligence Podcast Studio

> Drop any article, PDF, or link about AI startups and the future of AI — get a publish-ready two-host podcast episode in under 60 seconds.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Gradio](https://img.shields.io/badge/UI-Gradio-orange.svg)](https://gradio.app/)
[![Claude](https://img.shields.io/badge/LLM-Claude-blueviolet.svg)](https://anthropic.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

![PodcastIQ Studio](assets/studio.svg)

---

## What It Does

PodcastIQ is a domain-focused automated podcast studio built around one question: **how is AI knowledge reshaping startups and the future of work, business, and society?** Feed it any content — a TechCrunch article, a Y Combinator blog post, an AI research PDF, a YouTube talk — and it returns a fully produced audio episode with two distinct expert hosts, a downloadable MP3, and auto-generated episode metadata.

The show format features two recurring hosts: **Alex** (the technical founder perspective) and **Sam** (the business and market perspective). Their contrasting lenses make every episode feel like a genuine conversation rather than a summary read aloud.

```
   INPUT                 PROCESS                   OUTPUT
┌──────────┐    ┌─────────────────────────┐    ┌──────────────┐
│ PDF      │    │  1. Extract & clean     │    │ 🎙 MP3 file  │
│ URL      │───▶│  2. LLM dialogue script │───▶│ 📄 Script    │
│ YouTube  │    │  3. Voice-per-host TTS  │    │ 🏷 Metadata  │
│ Text     │    │  4. Stitch & export     │    │ 💰 Cost log  │
└──────────┘    └─────────────────────────┘    └──────────────┘
```

---

## Features

### Core Pipeline
- **Multi-source ingestion** — PDF upload, article URL scraping, YouTube transcript extraction, raw text paste
- **Two-host dialogue** — LLM generates a scripted conversation between named hosts with distinct personalities and natural transitions
- **Voice-per-host TTS** — Each host is rendered with a distinct accent via gTTS; segments are stitched into a single seamless MP3
- **Episode metadata** — Title, one-sentence summary, topical tags, and estimated listen time generated automatically

### Interface
- **Gradio UI** with three tabs: Input, Settings, Output
- Real-time progress bar through each pipeline stage
- Full script preview alongside the audio player
- One-click MP3 download
- Script preview alongside the audio player

### Podcast Styles
| Style | Format |
|---|---|
| `educational` | One host teaches, the other asks clarifying questions |
| `debate` | Hosts argue opposing sides, reach a conclusion |
| `news_brief` | Crisp co-anchor format, headline-first |
| `deep_dive` | Long-form exploration with tangents and analogies |

---

## Project Structure

```
podcast-studio/
├── src/
│   ├── models.py           # Pydantic dataclasses for the pipeline
│   ├── data_processor.py   # Input handlers: PDF, URL, YouTube, text
│   ├── llm_processor.py    # Claude script generation via Anthropic API
│   ├── tts_generator.py    # TTS + audio stitching
│   └── main.py             # Gradio application entry point
├── prompts/
│   ├── educational.txt     # Prompt template — educational style
│   ├── debate.txt          # Prompt template — debate style
│   ├── news_brief.txt      # Prompt template — news brief style
│   └── deep_dive.txt       # Prompt template — deep dive style
├── outputs/                # Generated audio files and scripts (gitignored)
├── .env.example            # API key template
├── requirements.txt
├── TODO.md
└── README.md
```

---

## Quick Start

### 1. Clone and enter the project

```bash
git clone <your-repo-url>
cd podcast-studio
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

### 4. Configure API keys

```bash
cp .env.example .env
# Open .env and add your Anthropic key
```

Required keys:

| Variable | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |

No other keys needed — audio is generated using gTTS (free, no account required).

### 5. Launch

```bash
python src/main.py
```

Open the URL printed in the terminal (usually `http://localhost:7860`).

---

## Usage

### Basic flow

1. **Input tab** — paste text, upload a PDF, or enter a URL / YouTube link
2. **Settings tab** — choose podcast style, host names, voices, target duration
3. Click **Generate Episode**
4. **Output tab** — listen, read the script, download the MP3

### Example inputs that work well

- A Wikipedia article URL about any topic
- A lecture PDF or slide deck
- A YouTube video URL (transcript is extracted automatically)
- A block of raw notes or bullet points

---

## API Costs (Approximate)

| Component | Model / Service | Typical cost per episode |
|---|---|---|
| Script generation | Claude Sonnet (8k tokens) | ~$0.03 |
| Text-to-speech | gTTS (free) | $0.00 |
| **Total** | | **~$0.03 per episode** |

---

## Architecture Deep Dive

### Full pipeline overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Gradio UI (main.py)                      │
│  Source input → Settings → [Generate Episode] → Audio + Script  │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────▼──────────────┐
              │   Step 1 — data_processor.py │
              │   Ingest & clean the source  │
              └──────────────┬──────────────┘
                             │ PodcastInput(text, title, word_count)
              ┌──────────────▼──────────────┐
              │   Step 2 — llm_processor.py  │
              │   Claude generates dialogue  │
              └──────────────┬──────────────┘
                             │ PodcastScript(lines, metadata)
              ┌──────────────▼──────────────┐
              │   Step 3 — tts_generator.py  │
              │   gTTS + pydub → MP3 file    │
              └──────────────┬──────────────┘
                             │ AudioOutput(file_path, duration_seconds)
                             ▼
                  outputs/episode_<timestamp>.mp3
```

---

### Step 1 — Data Ingestion (`src/data_processor.py`)

Accepts four source types and normalises them all into a single `PodcastInput` object:

| Source | How it works |
|---|---|
| **Text** | Strips whitespace, counts words, passes straight through |
| **URL** | `requests` fetches the page, `BeautifulSoup` strips nav/footer/scripts, extracts `<p>` tags longer than 40 chars |
| **PDF** | `PyPDF2` reads each page, joins extracted text, collapses whitespace |
| **YouTube** | `youtube-transcript-api` fetches the auto-generated transcript by video ID; falls back to any available language if English isn't found |

All four paths return the same dataclass:

```python
@dataclass
class PodcastInput:
    text: str         # cleaned source content (capped at 8000 chars for the prompt)
    title: str        # article title, filename, or video ID
    source_type: SourceType
    word_count: int
```

---

### Step 2 — Script Generation (`src/llm_processor.py`)

Sends the cleaned text to **Claude Sonnet (`claude-sonnet-4-6`)** via the Anthropic API.

**How the prompt is built:**
1. A style-specific template is loaded from `prompts/{style}.txt`
2. The template is filled with `source_text`, `target_minutes`, `word_count_target`, and both host names
3. Target word count is calculated as `target_minutes × 150 words/min`

**What Claude returns:**
```
ALEX: Did you see Anthropic just raised $2.75 billion?
SAM: That's massive. What does that mean for the safety-first approach?
...
TITLE: The AI Funding Race
SUMMARY: Alex and Sam debate what Anthropic's latest raise means for AI safety.
TAGS: Anthropic, funding, AI safety, LLM
DURATION: 5
```

**How the response is parsed:**
- Regex extracts every `ALEX:` / `SAM:` line into a list of `DialogueLine` objects
- A separate regex pass pulls `TITLE`, `SUMMARY`, `TAGS`, and `DURATION` into `EpisodeMetadata`
- The result is a `PodcastScript` containing both

```python
@dataclass
class PodcastScript:
    lines: list[DialogueLine]      # ordered dialogue turns
    metadata: EpisodeMetadata      # title, summary, tags, duration
```

**The 4 prompt styles** each give Claude a different persona:

| Style | Alex | Sam | Format |
|---|---|---|---|
| `educational` | Expert teacher | Curious student | Q&A — Sam asks, Alex explains |
| `debate` | Optimist / advocate | Sceptic / critic | Structured argument with a conclusion |
| `news_brief` | Co-anchor | Co-anchor | Fast-paced, headline-first |
| `deep_dive` | Analyst | Analyst | Long-form with second-order effects and tangents |

---

### Step 3 — Audio Generation (`src/tts_generator.py`)

Converts each `DialogueLine` to speech using **gTTS (Google Text-to-Speech)** — free, no API key needed.

**Voice differentiation:**
- Alex → `tld="com"` (US English accent)
- Sam → `tld="co.uk"` (British English accent)

**Stitching process:**
1. Each line is synthesised individually into an `AudioSegment` (via an in-memory buffer, no temp files)
2. A 400 ms silence pause is inserted between every turn
3. All segments are concatenated with pydub
4. The final track is exported as MP3 to `outputs/episode_<timestamp>.mp3`
5. ffmpeg (bundled via `static-ffmpeg`) handles the MP3 encoding — no system install required

```python
@dataclass
class AudioOutput:
    file_path: str           # absolute path to the MP3
    duration_seconds: float  # total runtime
```

---

### Step 4 — Gradio UI (`src/main.py`)

`gr.Blocks` wires everything together. When **Generate Episode** is clicked:

1. `run_pipeline()` is called with all form values
2. Progress bar updates at 10% (ingestion), 35% (Claude), 65% (audio), 100% (done)
3. The MP3 path is returned to the audio player and download button
4. Script text and episode metadata are displayed in expandable accordions

---

### Data models (`src/models.py`)

All objects passed between pipeline stages are plain Python dataclasses — no ORM, no serialisation overhead:

```
PodcastSettings ──► llm_processor, tts_generator
PodcastInput    ──► llm_processor
PodcastScript   ──► tts_generator
  ├── list[DialogueLine]
  └── EpisodeMetadata
AudioOutput     ──► Gradio UI
```

---

### Why two-host dialogue?

Single-voice monologues are harder to follow aurally. A back-and-forth format:
- Creates natural "chapter breaks" at every speaker switch
- Lets one host ask questions the listener is thinking
- Covers multiple perspectives without sounding like a listicle
- Sounds dramatically more professional with almost no added complexity

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+ |
| UI | Gradio 4.x |
| LLM | Claude Sonnet (Anthropic) |
| TTS | gTTS (Google Text-to-Speech, free) |
| Audio processing | pydub + ffmpeg |
| PDF parsing | PyPDF2 |
| Web scraping | requests + BeautifulSoup4 |
| YouTube transcripts | youtube-transcript-api |
| Data validation | Pydantic v2 |
| Config | python-dotenv |

---

## Development Roadmap

- [x] Multi-source ingestion pipeline
- [x] Two-host LLM dialogue generation
- [x] Voice-per-host TTS + audio stitching
- [x] Gradio UI with tabs and progress
- [x] Episode metadata generation
- [ ] Background music mixer (intro/outro jingle)
- [ ] RSS feed export (publish directly to podcast platforms)
- [ ] Multi-language support
- [ ] Voice cloning via ElevenLabs
- [ ] Batch generation mode

---

## Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

---

## License

MIT — see [LICENSE](LICENSE)

---

*Built at Ironhack — Module 1 Group Project, April 2026*
