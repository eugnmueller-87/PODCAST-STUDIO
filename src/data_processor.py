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


def process_pdf(file_path: str) -> PodcastInput:
    text_parts = []
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    text = " ".join(text_parts).strip()
    text = re.sub(r"\s+", " ", text)

    if not text:
        raise ValueError("Could not extract text from PDF.")

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
