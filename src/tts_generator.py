import io
import os
import time
from pathlib import Path

import static_ffmpeg
static_ffmpeg.add_paths()

from gtts import gTTS
from pydub import AudioSegment

from models import AudioOutput, PodcastScript, PodcastSettings

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

# Different TLDs give slightly different accents in gTTS
HOST_A_TLD = "com"      # US accent
HOST_B_TLD = "co.uk"    # UK accent

PAUSE_BETWEEN_TURNS = AudioSegment.silent(duration=400)


def _synthesise_line(text: str, tld: str) -> AudioSegment:
    tts = gTTS(text=text, lang="en", tld=tld)
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return AudioSegment.from_mp3(buffer)


def synthesise_script(script: PodcastScript, settings: PodcastSettings) -> AudioOutput:
    host_a = settings.host_a_name.capitalize()
    combined = AudioSegment.empty()

    for line in script.lines:
        tld = HOST_A_TLD if line.host_name.capitalize() == host_a else HOST_B_TLD
        segment = _synthesise_line(line.text, tld)
        combined += segment + PAUSE_BETWEEN_TURNS

    timestamp = int(time.time())
    output_path = OUTPUTS_DIR / f"episode_{timestamp}.mp3"
    combined.export(str(output_path), format="mp3")

    duration_seconds = len(combined) / 1000.0

    return AudioOutput(
        file_path=str(output_path),
        duration_seconds=duration_seconds,
    )
