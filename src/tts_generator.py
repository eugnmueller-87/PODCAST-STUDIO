import asyncio
import os
import random
import re
import tempfile
import time
from pathlib import Path

import static_ffmpeg
static_ffmpeg.add_paths()

import edge_tts
from pydub import AudioSegment

from models import AudioOutput, DialogueLine, PodcastScript, PodcastSettings

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

HOST_A_VOICE = "en-GB-SoniaNeural"   # Alex — British female
HOST_B_VOICE = "en-US-GuyNeural"     # Sam — American male


def _prosody_params(text: str) -> dict:
    """Pick rate and pitch based on emotional content of the line."""
    t = text.lower().strip()
    if text.strip().endswith("?"):
        # Questions — higher pitch, slightly slower
        return {"rate": "-8%", "pitch": "+10Hz"}
    if any(w in t for w in ["wow", "wild", "incredible", "seriously", "no way",
                              "come on", "exactly", "that's it", "brilliant"]):
        # Excited / emphatic
        return {"rate": "+10%", "pitch": "+8Hz"}
    if any(w in t for w in ["honestly", "genuinely", "actually", "i don't know",
                              "i'm not sure", "i'll be honest", "hard to say"]):
        # Thoughtful / uncertain — slower and lower
        return {"rate": "-12%", "pitch": "-6Hz"}
    if any(w in t for w in ["never", "always", "critical", "fundamental",
                              "the real question", "here's the thing"]):
        # Emphatic statement
        return {"rate": "-5%", "pitch": "+4Hz"}
    # Default — slightly slower than neutral for warmth
    return {"rate": "-5%", "pitch": "+0Hz"}


def _pause_ms(prev: DialogueLine | None, current: DialogueLine, idx: int) -> int:
    if prev is None:
        return 500
    prev_text = prev.text.rstrip()
    if prev_text.endswith("?"):
        return random.randint(300, 500)       # quick response to a question
    if len(current.text.split()) < 8:
        return random.randint(350, 600)       # short reaction jumped in
    if idx > 0 and idx % 5 == 0:
        return random.randint(1000, 1600)     # topic breath
    if len(prev_text.split()) > 35:
        return random.randint(700, 1000)      # long statement needs a beat
    return random.randint(500, 850)           # default natural gap


async def _synthesise_segment(text: str, voice: str, params: dict) -> AudioSegment:
    """Generate one TTS segment from a chunk of text."""
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


async def _synthesise_one(line: DialogueLine, voice: str) -> AudioSegment:
    """
    Split a dialogue line at em-dashes and ellipses so those markers
    become real silence in the audio, then stitch the sub-segments.
    """
    params = _prosody_params(line.text)

    # Split at em-dashes (400ms pause) and ellipses (700ms pause)
    parts = re.split(r"(\s*—\s*|\.\.\.)", line.text)

    tasks = []
    structure = []   # list of ("audio"|"pause", value)
    for part in parts:
        stripped = part.strip()
        if stripped in ("—", "...") or re.fullmatch(r"\s*—\s*", part):
            ms = 700 if "..." in part else 420
            structure.append(("pause", ms))
        elif stripped:
            structure.append(("audio", len(tasks)))
            tasks.append(_synthesise_segment(stripped, voice, params))

    segments = await asyncio.gather(*tasks)

    combined = AudioSegment.empty()
    for kind, value in structure:
        if kind == "pause":
            combined += AudioSegment.silent(duration=value)
        else:
            combined += segments[value]

    return combined


async def _synthesise_all(lines: list[DialogueLine], host_a: str) -> list[AudioSegment]:
    tasks = [
        _synthesise_one(
            line,
            HOST_A_VOICE if line.host_name.capitalize() == host_a else HOST_B_VOICE,
        )
        for line in lines
    ]
    return await asyncio.gather(*tasks)


def synthesise_script(script: PodcastScript, settings: PodcastSettings) -> AudioOutput:
    host_a = settings.host_a_name.capitalize()

    loop = asyncio.new_event_loop()
    try:
        segments = loop.run_until_complete(_synthesise_all(script.lines, host_a))
    finally:
        loop.close()

    combined = AudioSegment.empty()
    for idx, (line, segment) in enumerate(zip(script.lines, segments)):
        prev = script.lines[idx - 1] if idx > 0 else None
        pause = AudioSegment.silent(duration=_pause_ms(prev, line, idx))
        combined += pause + segment

    timestamp = int(time.time())
    output_path = OUTPUTS_DIR / f"episode_{timestamp}.mp3"
    combined.export(str(output_path), format="mp3")

    return AudioOutput(
        file_path=str(output_path),
        duration_seconds=len(combined) / 1000.0,
    )
