# QUALITY: 8/10
# Strengths: parallel asyncio, emotional prosody, mid-sentence silences, ElevenLabs + edge-tts hybrid
# Improve: add ElevenLabs retry on 429, extract Sam synthesis into its own function, add audio normalisation
import asyncio
import io
import os
import random
import re
import tempfile
import time
from pathlib import Path

import requests
import static_ffmpeg
static_ffmpeg.add_paths()

import edge_tts
from pydub import AudioSegment

from models import AudioOutput, DialogueLine, PodcastScript, PodcastSettings

OUTPUTS_DIR = Path(__file__).parent.parent / "test_audio"
OUTPUTS_DIR.mkdir(exist_ok=True)

HOST_A_VOICE_ID = "DEZHhPbmb8LVZmWufkCh"  # Alex — ElevenLabs custom voice
HOST_A_FALLBACK = "en-GB-SoniaNeural"      # fallback if no ElevenLabs key
HOST_B_VOICE = "en-US-GuyNeural"           # Sam — American male (edge-tts)

ELEVENLABS_API_BASE = "https://api.elevenlabs.io/v1"
ELEVENLABS_MODEL = "eleven_v3"


# ── ElevenLabs helper ─────────────────────────────────────────────────────────

def _elevenlabs_synthesise(text: str, voice_id: str, api_key: str) -> AudioSegment:
    resp = requests.post(
        f"{ELEVENLABS_API_BASE}/text-to-speech/{voice_id}",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        json={
            "text": text,
            "model_id": ELEVENLABS_MODEL,
            "language_code": "en",
            "voice_settings": {"stability": 0.75, "similarity_boost": 0.90, "style": 0.2},
        },
        timeout=30,
    )
    resp.raise_for_status()
    return AudioSegment.from_mp3(io.BytesIO(resp.content))


# ── Prosody & pause helpers (edge-tts only) ───────────────────────────────────

def _prosody_params(text: str) -> dict:
    t = text.lower().strip()
    if text.strip().endswith("?"):
        return {"rate": "-8%", "pitch": "+10Hz"}
    if any(w in t for w in ["wow", "wild", "incredible", "seriously", "no way",
                              "come on", "exactly", "that's it", "brilliant"]):
        return {"rate": "+10%", "pitch": "+8Hz"}
    if any(w in t for w in ["honestly", "genuinely", "actually", "i don't know",
                              "i'm not sure", "i'll be honest", "hard to say"]):
        return {"rate": "-12%", "pitch": "-6Hz"}
    if any(w in t for w in ["never", "always", "critical", "fundamental",
                              "the real question", "here's the thing"]):
        return {"rate": "-5%", "pitch": "+4Hz"}
    return {"rate": "-5%", "pitch": "+0Hz"}


def _pause_ms(prev: DialogueLine | None, current: DialogueLine, idx: int) -> int:
    if prev is None:
        return 500
    prev_text = prev.text.rstrip()
    if prev_text.endswith("?"):
        return random.randint(300, 500)
    if len(current.text.split()) < 8:
        return random.randint(350, 600)
    if idx > 0 and idx % 5 == 0:
        return random.randint(1000, 1600)
    if len(prev_text.split()) > 35:
        return random.randint(700, 1000)
    return random.randint(500, 850)


# ── Segment synthesis ─────────────────────────────────────────────────────────

async def _edge_segment(text: str, voice: str, params: dict) -> AudioSegment:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        communicate = edge_tts.Communicate(
            text, voice,
            rate=params.get("rate", "+0%"),
            pitch=params.get("pitch", "+0Hz"),
        )
        await communicate.save(tmp_path)
        return AudioSegment.from_mp3(tmp_path)
    finally:
        os.unlink(tmp_path)


def _eleven_segment(text: str, voice_id: str, api_key: str) -> AudioSegment:
    return _elevenlabs_synthesise(text, voice_id, api_key)


_elevenlabs_fallback_triggered = False  # module-level flag, reset per run


async def _synthesise_one(
    line: DialogueLine,
    use_elevenlabs: bool,
    elevenlabs_voice_id: str | None,
    elevenlabs_api_key: str | None,
) -> AudioSegment:
    parts = re.split(r"(\s*—\s*|\.\.\.)", line.text)
    params = _prosody_params(line.text)

    structure = []
    audio_chunks = []

    for part in parts:
        stripped = part.strip()
        if stripped in ("—", "...") or re.fullmatch(r"\s*—\s*", part):
            ms = 700 if "..." in part else 420
            structure.append(("pause", ms))
        elif stripped:
            structure.append(("audio", len(audio_chunks)))
            audio_chunks.append(stripped)

    if use_elevenlabs and elevenlabs_voice_id and elevenlabs_api_key:
        # get_running_loop() is correct inside a coroutine (get_event_loop() is deprecated in 3.12+)
        loop = asyncio.get_running_loop()
        try:
            segments = await asyncio.gather(*[
                loop.run_in_executor(None, _eleven_segment, chunk, elevenlabs_voice_id, elevenlabs_api_key)
                for chunk in audio_chunks
            ])
        except Exception as e:
            # 401 invalid key, quota exceeded, network error — fall back silently
            global _elevenlabs_fallback_triggered
            _elevenlabs_fallback_triggered = True
            print(f"[tts] ElevenLabs failed ({e}) — falling back to {HOST_A_FALLBACK}")
            try:
                segments = await asyncio.gather(*[
                    _edge_segment(chunk, HOST_A_FALLBACK, params)
                    for chunk in audio_chunks
                ])
            except Exception as edge_e:
                print(f"[tts] edge-tts fallback also failed ({edge_e}) — returning silence")
                segments = [AudioSegment.silent(duration=1000)] * len(audio_chunks)
    else:
        try:
            segments = await asyncio.gather(*[
                _edge_segment(chunk, HOST_A_FALLBACK, params)
                for chunk in audio_chunks
            ])
        except Exception as e:
            print(f"[tts] edge-tts failed ({e}) — returning silence for chunk")
            segments = [AudioSegment.silent(duration=1000)] * len(audio_chunks)

    combined = AudioSegment.empty()
    for kind, value in structure:
        if kind == "pause":
            combined += AudioSegment.silent(duration=value)
        else:
            combined += segments[value]
    return combined


async def _synthesise_all(
    lines: list[DialogueLine],
    host_a: str,
    elevenlabs_voice_id: str | None,
    elevenlabs_api_key: str | None,
) -> list[AudioSegment]:
    tasks = []
    for line in lines:
        is_host_a = line.host_name.capitalize() == host_a
        if is_host_a:
            tasks.append(_synthesise_one(line, True, elevenlabs_voice_id, elevenlabs_api_key))
        else:
            # Sam — always edge-tts
            parts = re.split(r"(\s*—\s*|\.\.\.)", line.text)
            params = _prosody_params(line.text)
            structure, chunks = [], []
            for part in parts:
                s = part.strip()
                if s in ("—", "...") or re.fullmatch(r"\s*—\s*", part):
                    structure.append(("pause", 700 if "..." in part else 420))
                elif s:
                    structure.append(("audio", len(chunks)))
                    chunks.append(s)

            async def _sam_line(structure=structure, chunks=chunks, params=params):
                try:
                    segs = await asyncio.gather(*[_edge_segment(c, HOST_B_VOICE, params) for c in chunks])
                except Exception as e:
                    print(f"[tts] Sam edge-tts failed ({e}) — returning silence")
                    segs = [AudioSegment.silent(duration=1000)] * len(chunks)
                out = AudioSegment.empty()
                for kind, val in structure:
                    out += AudioSegment.silent(duration=val) if kind == "pause" else segs[val]
                return out

            tasks.append(_sam_line())

    return await asyncio.gather(*tasks)


# ── Public entry point ────────────────────────────────────────────────────────

def synthesise_script(script: PodcastScript, settings: PodcastSettings, provider: str = "anthropic") -> tuple["AudioOutput", str]:
    """Returns (AudioOutput, voice_status_message)."""
    global _elevenlabs_fallback_triggered
    _elevenlabs_fallback_triggered = False

    host_a = settings.host_a_name.capitalize()

    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    voice_id = HOST_A_VOICE_ID if api_key else None
    no_key = not api_key

    loop = asyncio.new_event_loop()
    try:
        segments = loop.run_until_complete(
            _synthesise_all(script.lines, host_a, voice_id, api_key or None)
        )
    finally:
        loop.close()

    combined = AudioSegment.empty()
    for idx, (line, segment) in enumerate(zip(script.lines, segments)):
        prev = script.lines[idx - 1] if idx > 0 else None
        pause = AudioSegment.silent(duration=_pause_ms(prev, line, idx))
        combined += pause + segment

    timestamp = int(time.time())
    output_path = OUTPUTS_DIR / f"episode_{provider}_{timestamp}.mp3"
    combined.export(str(output_path), format="mp3")

    if no_key:
        voice_status = f"⚠️ Alex voice: {HOST_A_FALLBACK} (no ElevenLabs key set)"
    elif _elevenlabs_fallback_triggered:
        voice_status = f"⚠️ Alex voice: {HOST_A_FALLBACK} (ElevenLabs key invalid or expired — update ELEVENLABS_API_KEY in .env)"
    else:
        voice_status = f"✅ Alex voice: ElevenLabs eleven_v3"

    return AudioOutput(file_path=str(output_path), duration_seconds=len(combined) / 1000.0), voice_status
