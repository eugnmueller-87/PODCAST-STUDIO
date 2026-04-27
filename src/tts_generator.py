import asyncio
import os
import random
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


def _pause(prev: DialogueLine | None, current: DialogueLine, idx: int) -> AudioSegment:
    if prev is None:
        return AudioSegment.silent(duration=300)
    prev_text = prev.text.rstrip()
    if prev_text.endswith("?"):
        ms = random.randint(120, 220)
    elif len(current.text.split()) < 8:
        ms = random.randint(150, 280)
    elif idx > 0 and idx % 5 == 0:
        ms = random.randint(600, 900)
    elif len(prev_text.split()) > 35:
        ms = random.randint(450, 650)
    else:
        ms = random.randint(280, 480)
    return AudioSegment.silent(duration=ms)


async def _synthesise_async(text: str, voice: str) -> AudioSegment:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(tmp_path)
        return AudioSegment.from_mp3(tmp_path)
    finally:
        os.unlink(tmp_path)


def _synthesise_line(text: str, voice: str) -> AudioSegment:
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_synthesise_async(text, voice))
    finally:
        loop.close()


def synthesise_script(script: PodcastScript, settings: PodcastSettings) -> AudioOutput:
    host_a = settings.host_a_name.capitalize()
    combined = AudioSegment.empty()

    for idx, line in enumerate(script.lines):
        prev = script.lines[idx - 1] if idx > 0 else None
        voice = HOST_A_VOICE if line.host_name.capitalize() == host_a else HOST_B_VOICE
        pause = _pause(prev, line, idx)
        segment = _synthesise_line(line.text, voice)
        combined += pause + segment

    timestamp = int(time.time())
    output_path = OUTPUTS_DIR / f"episode_{timestamp}.mp3"
    combined.export(str(output_path), format="mp3")

    return AudioOutput(
        file_path=str(output_path),
        duration_seconds=len(combined) / 1000.0,
    )
