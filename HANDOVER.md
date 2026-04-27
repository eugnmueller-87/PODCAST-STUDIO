# PodcastIQ — Agent Handover

## Project Summary
Ironhack Week 2 Module 1 group project. Automated two-host podcast generator focused on **AI startups and how AI knowledge is reshaping the future**. Target grade: exceed expectations.

GitHub: https://github.com/eugnmueller-87/WEEK-2

---

## Tech Stack (decisions already made — do not change)
| Layer | Choice | Reason |
|---|---|---|
| LLM | Claude Sonnet (`claude-sonnet-4-6`) via Anthropic API | User has Anthropic key, no OpenAI key |
| TTS | gTTS (free, no key) | No second API key needed |
| Audio stitching | pydub | Joins per-host segments into one MP3 |
| UI | Gradio (`gr.Blocks`) | Project requirement |
| Input sources | Text, PDF, URL scraping, YouTube transcript | All implemented |

---

## Project Structure
```
podcast-studio/
├── PODCAST.ipynb          ← entry point — 3 cells, Run All launches Gradio
├── src/
│   ├── models.py          ← dataclasses: PodcastInput, PodcastScript, DialogueLine, AudioOutput, PodcastSettings
│   ├── data_processor.py  ← process_text / process_pdf / process_url / process_youtube → unified process()
│   ├── llm_processor.py   ← loads prompt template, calls Claude, parses ALEX:/SAM: dialogue + METADATA block
│   ├── tts_generator.py   ← gTTS per line (US accent = Alex, UK accent = Sam), pydub stitch → MP3
│   └── main.py            ← Gradio Blocks UI — source type tabs, settings, audio player, script preview
├── prompts/
│   ├── educational.txt    ← Alex teaches, Sam asks questions
│   ├── debate.txt         ← Alex (optimist) vs Sam (sceptic)
│   ├── news_brief.txt     ← co-anchor NPR style
│   └── deep_dive.txt      ← long-form, second-order effects
├── outputs/               ← generated MP3s saved here (gitignored)
├── .env                   ← ANTHROPIC_API_KEY is set (user added it)
├── .env.example
├── requirements.txt
├── README.md
├── TODO.md
└── HANDOVER.md            ← this file
```

---

## How to Run
1. Open `PODCAST.ipynb` from `podcast-studio/` folder (NOT from LAB 1/)
2. Select the `.venv` kernel (Python 3.14.4)
3. Press **Run All**
4. Gradio opens at http://localhost:7860

---

## Current Blockers

### ffmpeg not installed (CRITICAL)
pydub needs ffmpeg to export stitched audio as MP3. Without it, Step 3 (audio generation) will fail.

**Fix:**
```powershell
winget install ffmpeg
```
Then restart VS Code so PATH updates take effect.

---

## What Works Right Now
- [x] Full pipeline code written and structured
- [x] All 4 prompt templates written (educational, debate, news_brief, deep_dive)
- [x] Gradio UI with source type toggle, settings, audio player, script preview, download
- [x] `.env` has the Anthropic API key
- [x] Notebook is 3 cells — Run All goes straight to Gradio
- [x] Committed and pushed to GitHub

## What Has NOT Been Tested Yet
- [ ] Full end-to-end run (blocked by ffmpeg)
- [ ] PDF input handler (needs a real PDF to test)
- [ ] YouTube transcript extraction (needs a real URL to test)
- [ ] URL scraper (needs a real article URL to test)

---

## Next Steps After ffmpeg is Installed
1. Run All in the notebook — verify Gradio opens
2. Paste this test text into the UI and hit Generate:
   > "Anthropic has raised $2.75 billion in its latest funding round, valuing the AI startup at $18.4 billion. The company develops Claude — a family of large language models focused on safety. Investors include Google and Spark Capital."
3. Confirm script appears and MP3 plays
4. Test URL input with a TechCrunch or Wired AI article
5. Test YouTube input with an AI founder talk
6. Commit working demo + example MP3 to GitHub

---

## Key Code Locations
| What | File | Notes |
|---|---|---|
| Claude API call | `src/llm_processor.py:generate_script()` | Model: `claude-sonnet-4-6`, max_tokens: 4096 |
| Prompt loading | `src/llm_processor.py:_load_prompt()` | Reads from `prompts/{style}.txt` |
| Dialogue parsing | `src/llm_processor.py:_parse_script()` | Regex on `ALEX:` / `SAM:` lines |
| Audio stitching | `src/tts_generator.py:synthesise_script()` | 400ms silence between turns |
| Gradio pipeline | `src/main.py:run_pipeline()` | Calls process → generate_script → synthesise_script |
| Voice accents | `src/tts_generator.py` | Alex = `tld="com"` (US), Sam = `tld="co.uk"` (UK) |

---

## Presentation Format (5–7 min)
1. **Introduction** — who we are, what PodcastIQ does
2. **Problem** — information overload; AI moves fast; people don't have time to read
3. **Demo** — live: paste AI article → Generate → audio plays (use test text above as backup)
4. **Takeaways** — what we learned, what we'd add next (ElevenLabs voices, RSS export, multi-language)

---

*Last updated by Claude — April 2026*
