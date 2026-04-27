# QUALITY: 9/10
# Strengths: clean dataclasses, clear separation of concerns, enum for type safety
# Improve: add field validation (e.g. word_count > 0), consider Pydantic for auto-validation
from dataclasses import dataclass, field
from enum import Enum


class SourceType(str, Enum):
    TEXT = "text"
    PDF = "pdf"
    URL = "url"
    YOUTUBE = "youtube"


class PodcastStyle(str, Enum):
    EDUCATIONAL = "educational"
    DEBATE = "debate"
    NEWS_BRIEF = "news_brief"
    DEEP_DIVE = "deep_dive"


class LLMProvider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


@dataclass
class PodcastInput:
    text: str
    title: str
    source_type: SourceType
    word_count: int


@dataclass
class DialogueLine:
    host_name: str
    text: str


@dataclass
class EpisodeMetadata:
    title: str
    summary: str
    tags: list[str]
    estimated_duration_min: int


@dataclass
class PodcastScript:
    lines: list[DialogueLine]
    metadata: EpisodeMetadata


@dataclass
class PodcastSettings:
    style: PodcastStyle = PodcastStyle.EDUCATIONAL
    host_a_name: str = "Alex"
    host_b_name: str = "Sam"
    target_minutes: int = 5
    llm_provider: LLMProvider = LLMProvider.ANTHROPIC


@dataclass
class AudioOutput:
    file_path: str
    duration_seconds: float
