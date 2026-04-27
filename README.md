# PodcastIQ — AI Startup & Future Intelligence Podcast Studio

> Drop any article, PDF, or link about AI startups and the future of AI — get a publish-ready two-host podcast episode in under 60 seconds.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Gradio](https://img.shields.io/badge/UI-Gradio-orange.svg)](https://gradio.app/)
[![OpenAI](https://img.shields.io/badge/LLM-OpenAI-412991.svg)](https://openai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

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
- **Voice-per-host TTS** — Each host is rendered with a separate OpenAI TTS voice; segments are stitched into a single seamless MP3
- **Episode metadata** — Title, one-sentence summary, topical tags, and estimated listen time generated automatically

### Interface
- **Gradio UI** with three tabs: Input, Settings, Output
- Real-time progress bar through each pipeline stage
- Full script preview alongside the audio player
- One-click MP3 download with ID3 tags embedded
- API cost estimate displayed after each run

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
│   ├── llm_processor.py    # OpenAI/Anthropic script generation
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
# Open .env and fill in your keys
```

Required keys:

| Variable | Where to get it |
|---|---|
| `OPENAI_API_KEY` | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |

Optional keys (for enhanced features):

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Use Claude instead of GPT-4o for scripting |
| `ELEVENLABS_API_KEY` | Higher-quality voice synthesis |

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
| Script generation | GPT-4o (8k tokens) | ~$0.04 |
| Text-to-speech | OpenAI TTS-1 (1,500 chars) | ~$0.02 |
| **Total** | | **~$0.06 per episode** |

Costs are displayed live in the UI after each generation.

---

## Architecture Deep Dive

### Data flow

```
DataProcessor.process(source)
    └── returns PodcastInput(text, title, source_type, word_count)

LLMProcessor.generate_script(podcast_input, style, settings)
    └── returns PodcastScript(segments=[DialogueLine(host, text), ...], metadata)

TTSGenerator.synthesise(script)
    └── returns AudioOutput(file_path, duration_seconds, cost_usd)
```

### Why two-host dialogue?

Single-voice monologues are harder to follow aurally. A back-and-forth format:
- Creates natural "chapter breaks" at speaker switches
- Allows one host to ask questions the listener would ask
- Enables coverage of multiple perspectives
- Sounds dramatically more professional with minimal extra complexity

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+ |
| UI | Gradio 4.x |
| LLM | OpenAI GPT-4o (default) / Claude 3.5 Sonnet |
| TTS | OpenAI TTS-1 / ElevenLabs |
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
