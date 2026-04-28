# QUALITY: 8/10
# Strengths: clean prompt templating, solid regex parser, safety checks at both ends, dual-API support
# Improve: handle API rate limit / retry, stream response for long scripts, add token count logging
import os
import re
from pathlib import Path

import anthropic
from openai import OpenAI

from models import DialogueLine, EpisodeMetadata, LLMProvider, PodcastInput, PodcastScript, PodcastSettings
from humanizer import humanize_script
from content_guard import check as safety_check

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
WORDS_PER_MINUTE = 150


def _load_prompt(style: str) -> str:
    path = PROMPTS_DIR / f"{style}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path}")
    return path.read_text(encoding="utf-8")


def _build_prompt(podcast_input: PodcastInput, settings: PodcastSettings) -> str:
    template = _load_prompt(settings.style.value)
    word_count_target = settings.target_minutes * WORDS_PER_MINUTE
    return template.format(
        source_text=podcast_input.text[:8000],
        target_minutes=settings.target_minutes,
        word_count_target=word_count_target,
        host_a_name=settings.host_a_name,
        host_b_name=settings.host_b_name,
    )


def _parse_script(raw: str, settings: PodcastSettings) -> PodcastScript:
    dialogue_lines = []
    metadata = EpisodeMetadata(
        title="Episode",
        summary="",
        tags=[],
        estimated_duration_min=settings.target_minutes,
    )

    metadata_block = re.search(r"TITLE:\s*(.+)", raw)
    if metadata_block:
        metadata.title = metadata_block.group(1).strip()

    summary_match = re.search(r"SUMMARY:\s*(.+)", raw)
    if summary_match:
        metadata.summary = summary_match.group(1).strip()

    tags_match = re.search(r"TAGS:\s*(.+)", raw)
    if tags_match:
        metadata.tags = [t.strip() for t in tags_match.group(1).split(",")]

    duration_match = re.search(r"DURATION:\s*(\d+)", raw)
    if duration_match:
        metadata.estimated_duration_min = int(duration_match.group(1))

    host_names = [settings.host_a_name.upper(), settings.host_b_name.upper()]
    pattern = rf"({'|'.join(host_names)}):\s*(.+?)(?=(?:{'|'.join(host_names)}):|TITLE:|$)"
    matches = re.findall(pattern, raw, re.DOTALL)

    for host, text in matches:
        cleaned = text.strip().replace("\n", " ")
        cleaned = re.sub(r"\s+", " ", cleaned)
        if cleaned:
            dialogue_lines.append(DialogueLine(host_name=host.capitalize(), text=cleaned))

    if not dialogue_lines:
        raise ValueError("Could not parse any dialogue lines from the LLM response.")

    return PodcastScript(lines=dialogue_lines, metadata=metadata)


ANTHROPIC_DEFAULT_TEMP = 1.0   # max allowed by Anthropic API
OPENAI_DEFAULT_TEMP = 0.7      # GPT-4o stays on-format at 0.7


def _call_anthropic(prompt: str, temperature: float) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        temperature=min(temperature, 1.0),  # clamp — Anthropic max is 1.0
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def _call_openai(prompt: str, temperature: float) -> str:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=4096,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def generate_script(podcast_input: PodcastInput, settings: PodcastSettings, temperature: float | None = None) -> PodcastScript:
    # Guard — check source content before sending to LLM
    safety_check(podcast_input.text, context="source input")

    prompt = _build_prompt(podcast_input, settings)

    if settings.llm_provider == LLMProvider.OPENAI:
        temp = temperature if temperature is not None else OPENAI_DEFAULT_TEMP
        raw = _call_openai(prompt, temp)
    else:
        temp = temperature if temperature is not None else ANTHROPIC_DEFAULT_TEMP
        raw = _call_anthropic(prompt, temp)

    script = _parse_script(raw, settings)
    humanized = humanize_script(script)

    # Guard — verify the generated script is also clean
    full_script_text = " ".join(line.text for line in humanized.lines)
    safety_check(full_script_text, context="generated script")

    return humanized
