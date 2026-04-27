# PodcastIQ — Code Quality Assessment

> Ratings are on a **1–10 scale**. Each file has a header comment with the same rating.
> Use this as a guide for where to focus improvement efforts.

---

## Overview

| File | Rating | Priority to improve |
|---|---|---|
| `src/models.py` | 9/10 | Low |
| `src/content_guard.py` | 8/10 | Low |
| `src/llm_processor.py` | 8/10 | Medium |
| `src/tts_generator.py` | 8/10 | Medium |
| `src/data_processor.py` | 7/10 | Medium |
| `src/humanizer.py` | 7/10 | Medium |
| `src/main.py` | 7/10 | High |

**Overall project score: 7.7 / 10**

---

## File-by-file breakdown

### `src/models.py` — 9/10
**What it does:** Defines all data classes shared across the pipeline.

**Strengths:**
- Clean, minimal dataclasses with no business logic
- Enum for source type and podcast style — type-safe
- Every pipeline stage speaks the same data language

**What to improve:**
- Add field validation (e.g. `word_count > 0`, non-empty `text`)
- Consider migrating to Pydantic for automatic validation and serialisation

---

### `src/content_guard.py` — 8/10
**What it does:** Two-layer safety check — keyword regex + Claude Haiku classifier.

**Strengths:**
- Fast pre-filter catches obvious violations without an API call
- Claude classifier handles subtle/contextual hate speech
- Clean `ContentViolationError` exception, easy to catch upstream
- Blocked attempts logged to run_log

**What to improve:**
- Add patterns for non-English slurs (German, Spanish, French)
- Cache Claude classification result per content hash to avoid repeat API calls
- Add a test suite with known-bad and known-safe inputs

---

### `src/llm_processor.py` — 8/10
**What it does:** Builds the prompt and calls Claude to generate the podcast script.

**Strengths:**
- Clean prompt templating via external `.txt` files
- Solid regex parser handles all metadata fields
- Safety checks at both input and output
- Temperature 1.2 produces varied, natural dialogue

**What to improve:**
- Add API retry logic for rate limit errors (429)
- Log token usage per call to track costs
- Handle edge case where Claude returns no dialogue lines gracefully

---

### `src/tts_generator.py` — 8/10
**What it does:** Synthesises audio — ElevenLabs for Alex, edge-tts for Sam.

**Strengths:**
- Parallel async generation via `asyncio.gather()` — fast
- Emotional prosody (rate + pitch per line context)
- Mid-sentence silences from em-dashes and ellipses
- Graceful fallback to edge-tts if ElevenLabs key is missing

**What to improve:**
- Add retry on ElevenLabs 429 rate limit response
- Extract Sam's synthesis into its own dedicated function (currently duplicated logic)
- Add audio normalisation so both voices match in volume

---

### `src/data_processor.py` — 7/10
**What it does:** Ingests source content (text, URL, PDF, YouTube) into a `PodcastInput`.

**Strengths:**
- Clean handler dispatch with a single `process()` entry point
- Covers all 4 source types with appropriate error messages
- YouTube fallback to any available language

**What to improve:**
- Add retry logic for flaky URLs
- Cap extracted text length before returning (currently done in llm_processor)
- PDF: extract title from document metadata instead of filename
- URL: handle paywalled or JS-rendered pages

---

### `src/humanizer.py` — 7/10
**What it does:** Post-processes Claude's script with reactions, openers, self-corrections, and Sam humour.

**Strengths:**
- Probability-based layering feels natural
- Sam humour is distinct and context-aware
- Self-deprecating asides add personality

**What to improve:**
- Guard against stacking multiple injections on a single line (can sound odd)
- Add unit tests for each layer with fixed random seeds
- Tune probabilities based on user ratings from `ratings.csv`

---

### `src/main.py` — 7/10
**What it does:** Gradio UI, pipeline orchestration, run logging, and episode rating.

**Strengths:**
- Clean Gradio layout with dark studio theme
- Run logging (JSONL) and rating system (CSV) fully integrated
- Content guard surfaces clearly to the user

**What to improve:**
- Split UI code and pipeline logic into separate files (`ui.py` + `pipeline.py`)
- Add input validation before calling the pipeline (e.g. URL format check)
- Wrap audio player in error boundary — currently a failed run leaves it blank

---

## How to contribute improvements

1. Pick a file with a rating below 8
2. Create a feature branch: `git checkout -b feature/your-name-improve-main`
3. Make the improvement, update the `# QUALITY` comment at the top of the file
4. Open a Pull Request into `develop` with before/after reasoning

---

*Last reviewed: April 2026*
