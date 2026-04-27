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


def _pause_ms(prev: DialogueLine | None, current: DialogueLine, idx: int) -> int:
    if prev is None:
        return 300
    prev_text = prev.text.rstrip()
    if prev_text.endswith("?"):
        return random.randint(120, 220)
    if len(current.text.split()) < 8:
        return random.randint(150, 280)
    if idx > 0 and idx % 5 == 0:
        return random.randint(600, 900)
    if len(prev_text.split()) > 35:
        return random.randint(450, 650)
    return random.randint(280, 480)


async def _synthesise_one(text: str, voice: str) -> AudioSegment:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        await edge_tts.Communicate(text, voice).save(tmp_path)
        return AudioSegment.from_mp3(tmp_path)
    finally:
        os.unlink(tmp_path)


async def _synthesise_all(lines: list[DialogueLine], host_a: str) -> list[AudioSegment]:
    tasks = [
        _synthesise_one(
            line.text,
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
