import io
import os
import random
import time
from pathlib import Path

import static_ffmpeg
static_ffmpeg.add_paths()

from gtts import gTTS
from pydub import AudioSegment

from models import AudioOutput, DialogueLine, PodcastScript, PodcastSettings

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

HOST_A_TLD = "com"      # US accent — Alex
HOST_B_TLD = "co.uk"    # UK accent — Sam


def _pause(prev: DialogueLine | None, current: DialogueLine, idx: int) -> AudioSegment:
    """Return a silence segment whose length reflects the conversational context."""
    if prev is None:
        return AudioSegment.silent(duration=300)

    prev_text = prev.text.rstrip()

    # Quick snappy response to a question
    if prev_text.endswith("?"):
        ms = random.randint(120, 220)

    # Short reaction line — feels like the host jumped in
    elif len(current.text.split()) < 8:
        ms = random.randint(150, 280)

    # Topic breath every ~5 turns
    elif idx > 0 and idx % 5 == 0:
        ms = random.randint(600, 900)

    # Longer statement — needs a beat before the reply
    elif len(prev_text.split()) > 35:
        ms = random.randint(450, 650)

    # Default natural conversational gap
    else:
        ms = random.randint(280, 480)

    return AudioSegment.silent(duration=ms)


def _synthesise_line(text: str, tld: str) -> AudioSegment:
    tts = gTTS(text=text, lang="en", tld=tld)
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return AudioSegment.from_mp3(buffer)


def synthesise_script(script: PodcastScript, settings: PodcastSettings) -> AudioOutput:
    host_a = settings.host_a_name.capitalize()
    combined = AudioSegment.empty()

    for idx, line in enumerate(script.lines):
        prev = script.lines[idx - 1] if idx > 0 else None
        tld = HOST_A_TLD if line.host_name.capitalize() == host_a else HOST_B_TLD
        pause = _pause(prev, line, idx)
        segment = _synthesise_line(line.text, tld)
        combined += pause + segment

    timestamp = int(time.time())
    output_path = OUTPUTS_DIR / f"episode_{timestamp}.mp3"
    combined.export(str(output_path), format="mp3")

    return AudioOutput(
        file_path=str(output_path),
        duration_seconds=len(combined) / 1000.0,
    )
