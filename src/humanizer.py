import random
import re

from models import DialogueLine, PodcastScript

TURN_OPENERS = [
    "You know,", "I mean,", "Honestly,", "Actually,", "Look —",
    "Here's the thing —", "And this is key —", "Right, so",
    "The thing is,", "What's wild is,",
]

REACTIONS_TO_QUESTION = [
    "Hmm.", "Right.", "Okay.", "Wait —", "Yeah, exactly.",
    "Huh, interesting.", "Sure, but —", "Fair point.",
    "Good question.", "Okay, so —",
]

REACTIONS_TO_STATEMENT = [
    "Right.", "Okay.", "Hmm.", "Yeah.", "Sure.",
    "Interesting.", "Huh.", "Wait.", "And —", "So —",
]

SELF_CORRECTIONS = [
    " — or, actually, ", " — well, more precisely, ",
    " — no wait, ", " — scratch that — ",
]


def _maybe_add_opener(text: str, chance: float = 0.25) -> str:
    if random.random() < chance:
        opener = random.choice(TURN_OPENERS)
        first_char = text[0].lower()
        return f"{opener} {first_char}{text[1:]}"
    return text


def _maybe_add_reaction(text: str, prev: DialogueLine | None, chance: float = 0.45) -> str:
    if prev is None or random.random() > chance:
        return text
    pool = REACTIONS_TO_QUESTION if prev.text.rstrip().endswith("?") else REACTIONS_TO_STATEMENT
    reaction = random.choice(pool)
    return f"{reaction} {text}"


def _maybe_add_self_correction(text: str, chance: float = 0.15) -> str:
    if random.random() > chance:
        return text
    sentences = re.split(r"(?<=[.!?])\s+", text)
    if len(sentences) < 2:
        return text
    # Insert a self-correction mid-first-sentence
    words = sentences[0].split()
    if len(words) < 6:
        return text
    split_at = len(words) // 2
    correction = random.choice(SELF_CORRECTIONS)
    sentences[0] = " ".join(words[:split_at]) + correction + " ".join(words[split_at:])
    return " ".join(sentences)


def humanize_script(script: PodcastScript) -> PodcastScript:
    random.seed()
    humanized = []
    for i, line in enumerate(script.lines):
        prev = script.lines[i - 1] if i > 0 else None
        text = line.text
        text = _maybe_add_reaction(text, prev)
        text = _maybe_add_opener(text)
        text = _maybe_add_self_correction(text)
        humanized.append(DialogueLine(host_name=line.host_name, text=text))
    return PodcastScript(lines=humanized, metadata=script.metadata)
