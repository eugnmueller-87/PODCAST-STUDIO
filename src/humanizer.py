# QUALITY: 7/10
# Strengths: probability-based layering, Sam humour is distinct and context-aware
# Improve: avoid stacking multiple injections on one line, add unit tests for each layer
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

# Sam-only dry humour injections — appended or prepended to his lines
SAM_QUIPS = [
    " Which, honestly, is a sentence I never expected to say on a podcast.",
    " And yes, I did just compare a startup to a confused golden retriever.",
    " I mean, no pressure, but the entire industry is watching.",
    " Which is either genius or completely insane — possibly both.",
    " And I say that as someone who has read way too many pitch decks.",
    " Classic Silicon Valley — disrupt first, apologise later.",
    " Not to be dramatic, but this changes everything. Okay, maybe a little dramatic.",
    " Which is, of course, the technical term for 'we have no idea either'.",
    " At this point I just assume every AI startup has a hockey-stick slide.",
    " And somewhere a VC is nodding very seriously right now.",
]

SAM_SELF_DEPRECATING = [
    " — which, full disclosure, I only half understood until about ten minutes ago.",
    " — and I'm speaking as someone who once called transformers 'fancy autocomplete'.",
    " — don't fact-check me on that, I'm going from memory.",
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
    words = sentences[0].split()
    if len(words) < 6:
        return text
    split_at = len(words) // 2
    correction = random.choice(SELF_CORRECTIONS)
    sentences[0] = " ".join(words[:split_at]) + correction + " ".join(words[split_at:])
    return " ".join(sentences)


def _maybe_add_sam_humor(line: DialogueLine, chance: float = 0.30) -> str:
    """30% chance Sam drops a dry quip; 15% chance he's self-deprecating."""
    if line.host_name.lower() != "sam":
        return line.text
    roll = random.random()
    if roll < chance:
        return line.text + random.choice(SAM_QUIPS)
    if roll < chance + 0.15:
        # Insert self-deprecating aside before the last sentence
        sentences = re.split(r"(?<=[.!?])\s+", line.text)
        if len(sentences) >= 2:
            aside = random.choice(SAM_SELF_DEPRECATING)
            sentences[-2] = sentences[-2].rstrip(".!?") + aside + "."
            return " ".join(sentences)
    return line.text


def humanize_script(script: PodcastScript) -> PodcastScript:
    random.seed()
    humanized = []
    for i, line in enumerate(script.lines):
        prev = script.lines[i - 1] if i > 0 else None
        text = line.text
        text = _maybe_add_reaction(text, prev)
        text = _maybe_add_opener(text)
        text = _maybe_add_self_correction(text)
        # Build a temporary line so _maybe_add_sam_humor sees the host name
        tmp = DialogueLine(host_name=line.host_name, text=text)
        text = _maybe_add_sam_humor(tmp)
        humanized.append(DialogueLine(host_name=line.host_name, text=text))
    return PodcastScript(lines=humanized, metadata=script.metadata)
