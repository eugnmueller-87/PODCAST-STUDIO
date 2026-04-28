# QUALITY: 8/10
# Strengths: clean handler dispatch, covers all 4 source types, Haiku PDF with PyPDF2 fallback
# Improve: add URL timeout retry, cap extracted text length
import base64
import os
import re
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
import PyPDF2

from models import PodcastInput, SourceType


def process_text(text: str) -> PodcastInput:
    text = text.strip()
    if not text:
        raise ValueError("Text input is empty.")
    return PodcastInput(
        text=text,
        title="Custom Text Input",
        source_type=SourceType.TEXT,
        word_count=len(text.split()),
    )


def _pdf_via_haiku(file_path: str) -> str | None:
    """Extract PDF text using Claude Haiku's native PDF understanding.
    Returns None if no API key or if the call fails — caller falls back to PyPDF2."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    try:
        import anthropic
        with open(file_path, "rb") as f:
            pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_data},
                    },
                    {
                        "type": "text",
                        "text": "Extract all text from this PDF. Return only the extracted text, preserving paragraph structure. No commentary.",
                    },
                ],
            }],
        )
        text = message.content[0].text.strip()
        return text if text else None
    except Exception:
        return None


def _pdf_via_pypdf2(file_path: str) -> str | None:
    """Fallback PDF extraction using PyPDF2."""
    try:
        text_parts = []
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        text = " ".join(text_parts).strip()
        return re.sub(r"\s+", " ", text) if text else None
    except Exception:
        return None


def process_pdf(file_path: str) -> PodcastInput:
    text = _pdf_via_haiku(file_path) or _pdf_via_pypdf2(file_path)

    if not text:
        raise ValueError("Could not extract text from PDF.")

    text = re.sub(r"\s+", " ", text).strip()
    title = file_path.split("/")[-1].replace(".pdf", "")
    return PodcastInput(
        text=text,
        title=title,
        source_type=SourceType.PDF,
        word_count=len(text.split()),
    )


def process_url(url: str) -> PodcastInput:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title else url

    paragraphs = soup.find_all("p")
    text = " ".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 40)
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        raise ValueError("Could not extract article text from URL.")

    return PodcastInput(
        text=text,
        title=title,
        source_type=SourceType.URL,
        word_count=len(text.split()),
    )


def _extract_youtube_id(url: str) -> str:
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11})",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Could not extract YouTube video ID from URL.")


def process_youtube(url: str) -> PodcastInput:
    video_id = _extract_youtube_id(url)
    api = YouTubeTranscriptApi()
    try:
        transcript = api.fetch(video_id)
    except Exception:
        # fall back to any available language
        listings = api.list(video_id)
        first = next(iter(listings))
        transcript = first.fetch()
    text = " ".join(snippet.text for snippet in transcript)
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        raise ValueError("YouTube video has no transcript available.")

    return PodcastInput(
        text=text,
        title=f"YouTube: {video_id}",
        source_type=SourceType.YOUTUBE,
        word_count=len(text.split()),
    )


def process(source: str, source_type: SourceType) -> PodcastInput:
    handlers = {
        SourceType.TEXT: process_text,
        SourceType.PDF: process_pdf,
        SourceType.URL: process_url,
        SourceType.YOUTUBE: process_youtube,
    }
    return handlers[source_type](source)
