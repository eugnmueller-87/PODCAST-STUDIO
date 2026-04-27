# PodcastIQ — Project TODO

> Work through this top to bottom. Check off each item as it's done.
> Phases 0–2 = MVP (meets requirements). Phase 3+ = exceeds expectations.

---

## Phase 0 — Environment Setup

- [ ] Create virtual environment (`python -m venv venv`)
- [ ] Activate venv and confirm Python version ≥ 3.10
- [ ] Create `.env` from `.env.example` and add API keys
  - [ ] `OPENAI_API_KEY`
  - [ ] `ANTHROPIC_API_KEY` (optional — for Claude fallback)
  - [ ] `ELEVENLABS_API_KEY` (optional — for premium voices)
- [ ] Run `pip install -r requirements.txt`
- [ ] Verify installs: `python -c "import openai, gradio, pydub; print('OK')`
- [ ] Install ffmpeg (required by pydub for MP3 export)
  - Windows: `winget install ffmpeg` or download from ffmpeg.org
- [ ] Initialize git repo and make first commit (`git init && git add . && git commit -m "init: project scaffold"`)
- [ ] Add `outputs/`, `.env`, `venv/` to `.gitignore`

---

## Phase 1 — Core Pipeline (MVP)

### 1.1 Data Models (`src/models.py`)
- [ ] Define `SourceType` enum: `TEXT`, `PDF`, `URL`, `YOUTUBE`
- [ ] Define `PodcastInput` dataclass: `text`, `title`, `source_type`, `word_count`
- [ ] Define `DialogueLine` dataclass: `host_name`, `text`
- [ ] Define `PodcastScript` dataclass: `lines: list[DialogueLine]`, `metadata: EpisodeMetadata`
- [ ] Define `EpisodeMetadata` dataclass: `title`, `summary`, `tags`, `estimated_duration_min`
- [ ] Define `AudioOutput` dataclass: `file_path`, `duration_seconds`, `cost_usd`
- [ ] Define `PodcastSettings` dataclass: `style`, `host_a_name`, `host_b_name`, `host_a_voice`, `host_b_voice`, `target_minutes`

### 1.2 Data Processor (`src/data_processor.py`)
- [ ] `process_text(text: str) -> PodcastInput` — wrap raw text
- [ ] `process_pdf(file_path: str) -> PodcastInput` — extract text with PyPDF2, clean whitespace
- [ ] `process_url(url: str) -> PodcastInput` — scrape article with requests + BeautifulSoup4, strip nav/ads
- [ ] `process_youtube(url: str) -> PodcastInput` — extract transcript with youtube-transcript-api
- [ ] `process(source: str | bytes, source_type: SourceType) -> PodcastInput` — unified dispatcher
- [ ] Add error handling: empty content, blocked sites, missing transcript
- [ ] Test each handler independently (use print statements initially)

### 1.3 LLM Processor (`src/llm_processor.py`)
- [ ] Load prompt templates from `prompts/` directory
- [ ] `generate_script(input: PodcastInput, settings: PodcastSettings) -> PodcastScript`
  - [ ] Build system prompt from style template
  - [ ] Build user prompt with source text + settings (host names, target length)
  - [ ] Call OpenAI Chat Completions (GPT-4o)
  - [ ] Parse response into list of `DialogueLine` objects
  - [ ] Extract episode metadata from response
  - [ ] Return `PodcastScript`
- [ ] Add fallback to Anthropic Claude if `ANTHROPIC_API_KEY` set
- [ ] Log token usage and calculate cost
- [ ] Add retry logic (max 2 retries on rate limit)
- [ ] Test with a short text input, print the script

### 1.4 Prompt Templates (`prompts/`)
- [x] `educational.txt` — Alex teaches, Sam asks clarifying questions (AI startups focus)
- [x] `debate.txt` — Alex (optimist) vs Sam (sceptic) on AI startup claims
- [x] `news_brief.txt` — co-anchor format, headline-first, punchy AI news briefing
- [x] `deep_dive.txt` — exploratory long-form, tangents welcome, second-order effects
- [x] All templates output structured dialogue: `ALEX:` / `SAM:` lines
- [x] All templates output METADATA block: TITLE / SUMMARY / TAGS / DURATION

### 1.5 TTS Generator (`src/tts_generator.py`)
- [ ] `synthesise_line(text: str, voice: str) -> bytes` — call OpenAI TTS-1, return audio bytes
- [ ] `synthesise_script(script: PodcastScript, settings: PodcastSettings) -> AudioOutput`
  - [ ] Loop through `DialogueLine` list
  - [ ] Route each line to correct voice (host A voice / host B voice)
  - [ ] Collect audio bytes per segment
  - [ ] Stitch segments with pydub (`AudioSegment`)
  - [ ] Add short silence (300ms) between speaker turns
  - [ ] Export final MP3 to `outputs/` with timestamped filename
  - [ ] Return `AudioOutput` with path, duration, and estimated cost
- [ ] Test with a 3-line dummy script, verify MP3 plays

### 1.6 Basic Gradio App (`src/main.py`)
- [ ] Create `gr.Blocks()` layout
- [ ] Add text input area
- [ ] Add "Generate Episode" button
- [ ] Call pipeline: `process → generate_script → synthesise_script`
- [ ] Display audio player
- [ ] Show status messages (loading / done / error)
- [ ] Confirm end-to-end flow works before moving to Phase 2

---

## Phase 2 — Exceed Expectations Features

### 2.1 Multi-Source Input
- [ ] Add Gradio `gr.Tab` for each input type: Text, PDF, URL, YouTube
- [ ] PDF: use `gr.File(file_types=[".pdf"])` component
- [ ] URL: validate URL format before processing (show inline error)
- [ ] YouTube: detect youtube.com or youtu.be URL, extract transcript
- [ ] Show detected word count and estimated read time after ingestion

### 2.2 Settings Tab
- [ ] Podcast style dropdown (Educational / Debate / News Brief / Deep Dive)
- [ ] Host A name input (default: "Alex")
- [ ] Host B name input (default: "Sam")
- [ ] Host A voice dropdown (alloy / echo / fable / onyx / nova / shimmer)
- [ ] Host B voice dropdown (same options, default different)
- [ ] Target duration slider (2 min – 15 min)

### 2.3 Enhanced Output Tab
- [ ] Audio player (`gr.Audio`)
- [ ] Script preview (`gr.Textbox`, read-only, scrollable)
- [ ] Episode metadata display (title, summary, tags)
- [ ] Downloadable MP3 (`gr.File`)
- [ ] API cost display (tokens used + USD estimate)
- [ ] Real-time progress using `gr.Progress`

### 2.4 Episode History
- [ ] Save each run's metadata to `outputs/history.json`
- [ ] Add history panel (`gr.Dataframe`) showing past episodes
- [ ] Allow re-downloading any past episode's audio

---

## Phase 3 — Polish & Delivery

### 3.1 Error Handling & UX
- [ ] Wrap entire pipeline in try/except, surface friendly errors in UI
- [ ] Validate all inputs before submitting (empty text, bad URL, no file)
- [ ] Show estimated generation time and cost before user hits generate
- [ ] Disable button while generation is running to prevent double-clicks

### 3.2 Code Quality
- [ ] Remove all debug print statements, use `logging` instead
- [ ] Add type hints to every function
- [ ] Ensure every module has a single-line docstring
- [ ] Run `ruff check src/` and fix any linting issues
- [ ] Confirm `requirements.txt` is complete and pinned

### 3.3 Documentation
- [ ] `README.md` complete (already drafted — verify all instructions work)
- [ ] `.env.example` has all keys and comments
- [ ] Commit messages are meaningful (not "wip" or "fix")
- [ ] At least 6 commits showing incremental progress

### 3.4 Demo Preparation

**Topic focus: AI startups and how AI knowledge is reshaping the future**

Curated demo inputs (test each one):
- [ ] URL: a TechCrunch or Wired article about an AI startup (e.g. recent OpenAI, Mistral, Perplexity news)
- [ ] URL: Y Combinator blog post on AI trends (blog.ycombinator.com)
- [ ] YouTube: a recent AI founder talk or VC panel (e.g. from a16z, SV Angel)
- [ ] PDF: an AI research paper abstract or startup pitch deck (find one relevant to AI economy)
- [ ] Text: paste a summary of a recent AI funding round manually

Delivery checklist:
- [ ] Generate at least 3 example audio files — one per style (educational, debate, news_brief)
- [ ] Save best example to `outputs/example_episode.mp3`
- [ ] Practice live demo: Input → Settings → Generate → Audio plays in < 5 min
- [ ] Prepare 5-slide deck:
  - Slide 1: Who we are + what we built (30 sec)
  - Slide 2: The problem / opportunity (45 sec)
  - Slide 3: Architecture diagram (1 min)
  - Slide 4: Live demo (2–3 min)
  - Slide 5: What we learned + what's next (1 min)

### 3.5 Final Submission
- [ ] GitHub repo is public (or shared with instructor)
- [ ] All required files present: README.md, requirements.txt, .env.example, src/
- [ ] `outputs/example_episode.mp3` is committed (or linked via release)
- [ ] Final end-to-end test on a clean clone confirms setup instructions work

---

## Stretch Goals (if time allows)

- [ ] Background music: mix a low-volume ambient track under the voices with pydub
- [ ] Intro/outro jingle: 3-second generated tone bookending each episode
- [ ] Multi-language output: detect language of source, generate in same language
- [ ] RSS feed: generate a valid `feed.xml` from episode history for podcast app import
- [ ] Batch mode: queue multiple URLs and generate episodes asynchronously

---

## Quick Reference — Useful Commands

```bash
# Activate venv (Windows)
venv\Scripts\activate

# Run the app
python src/main.py

# Install a new package and update requirements
pip install <package> && pip freeze > requirements.txt

# Run linter
ruff check src/

# Git snapshot
git add src/ prompts/ && git commit -m "feat: <what you did>"
```

---

## API Voice Reference (OpenAI TTS)

| Voice | Character |
|---|---|
| `alloy` | Neutral, clear — good anchor voice |
| `echo` | Measured, authoritative |
| `fable` | Warm, storytelling |
| `onyx` | Deep, confident |
| `nova` | Energetic, friendly |
| `shimmer` | Gentle, thoughtful |

**Recommended pairings:** Alex = `onyx`, Sam = `nova` (contrast makes dialogue easier to follow)
