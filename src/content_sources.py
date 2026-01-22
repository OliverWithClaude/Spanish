"""
Content Sources module for Spanish Learning App
Extracts Spanish text from various sources: YouTube, websites, files
"""

import re
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class ContentResult:
    """Result from content extraction."""
    text: str
    title: str
    source_type: str
    source_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    error: Optional[str] = None


# ============ YouTube Extraction ============

def extract_youtube_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def extract_youtube_transcript(url: str, language: str = 'es') -> ContentResult:
    """
    Extract transcript from a YouTube video.

    Args:
        url: YouTube video URL
        language: Language code (default 'es' for Spanish)

    Returns:
        ContentResult with transcript text or error
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api._errors import (
            TranscriptsDisabled,
            NoTranscriptFound,
            VideoUnavailable
        )
    except ImportError:
        return ContentResult(
            text="",
            title="",
            source_type="youtube",
            source_url=url,
            error="YouTube transcript API not installed. Run: pip install youtube-transcript-api"
        )

    video_id = extract_youtube_id(url)
    if not video_id:
        return ContentResult(
            text="",
            title="",
            source_type="youtube",
            source_url=url,
            error="Invalid YouTube URL. Please provide a valid YouTube video link."
        )

    try:
        # Create API instance (v1.x API)
        ytt_api = YouTubeTranscriptApi()

        # Try Spanish variants first, then fall back to English
        languages_to_try = ['es', 'es-ES', 'es-MX', 'es-419', 'en']

        transcript = ytt_api.fetch(video_id, languages=languages_to_try)

        # Convert to raw data format (list of dicts with 'text', 'start', 'duration')
        transcript_data = transcript.to_raw_data()

        # Combine all text segments
        full_text = ' '.join([entry['text'] for entry in transcript_data])

        # Clean up the text
        full_text = re.sub(r'\[.*?\]', '', full_text)  # Remove [Music], [Applause], etc.
        full_text = re.sub(r'\s+', ' ', full_text).strip()

        # Calculate duration
        duration = int(transcript_data[-1]['start'] + transcript_data[-1].get('duration', 0)) if transcript_data else 0

        return ContentResult(
            text=full_text,
            title=f"YouTube Video ({video_id})",
            source_type="youtube",
            source_url=url,
            duration_seconds=duration
        )

    except TranscriptsDisabled:
        return ContentResult(
            text="",
            title="",
            source_type="youtube",
            source_url=url,
            error="Transcripts are disabled for this video."
        )
    except NoTranscriptFound:
        return ContentResult(
            text="",
            title="",
            source_type="youtube",
            source_url=url,
            error="No transcript available for this video in Spanish or English."
        )
    except VideoUnavailable:
        return ContentResult(
            text="",
            title="",
            source_type="youtube",
            source_url=url,
            error="Video is unavailable or private."
        )
    except Exception as e:
        return ContentResult(
            text="",
            title="",
            source_type="youtube",
            source_url=url,
            error=f"Error extracting transcript: {str(e)}"
        )


# ============ Website Scraping ============

def fetch_website_content(url: str) -> ContentResult:
    """
    Fetch and extract text content from a website.

    Args:
        url: Website URL

    Returns:
        ContentResult with extracted text or error
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return ContentResult(
            text="",
            title="",
            source_type="website",
            source_url=url,
            error="BeautifulSoup not installed. Run: pip install beautifulsoup4"
        )

    try:
        import requests
    except ImportError:
        return ContentResult(
            text="",
            title="",
            source_type="website",
            source_url=url,
            error="Requests library not installed."
        )

    # Ensure URL has protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # Detect encoding
        response.encoding = response.apparent_encoding or 'utf-8'

        soup = BeautifulSoup(response.text, 'html.parser')

        # Get title
        title = soup.title.string if soup.title else url

        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer',
                           'aside', 'form', 'iframe', 'noscript']):
            element.decompose()

        # Try to find main content
        main_content = None
        for selector in ['article', 'main', '[role="main"]', '.content', '.post', '.entry']:
            main_content = soup.select_one(selector)
            if main_content:
                break

        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
        else:
            # Fall back to body
            body = soup.find('body')
            text = body.get_text(separator=' ', strip=True) if body else soup.get_text(separator=' ', strip=True)

        # Clean up text
        text = re.sub(r'\s+', ' ', text).strip()

        if len(text) < 50:
            return ContentResult(
                text="",
                title=title,
                source_type="website",
                source_url=url,
                error="Could not extract meaningful content from this page."
            )

        return ContentResult(
            text=text,
            title=title,
            source_type="website",
            source_url=url
        )

    except requests.exceptions.Timeout:
        return ContentResult(
            text="",
            title="",
            source_type="website",
            source_url=url,
            error="Request timed out. The website may be slow or unavailable."
        )
    except requests.exceptions.RequestException as e:
        return ContentResult(
            text="",
            title="",
            source_type="website",
            source_url=url,
            error=f"Error fetching website: {str(e)}"
        )
    except Exception as e:
        return ContentResult(
            text="",
            title="",
            source_type="website",
            source_url=url,
            error=f"Error processing website: {str(e)}"
        )


# ============ File Handling ============

def extract_text_from_file(file_path: str) -> ContentResult:
    """
    Extract text from uploaded file.

    Supports:
    - .txt files (plain text)
    - .srt files (subtitle files)
    - .pdf files (PDF documents)

    Args:
        file_path: Path to the uploaded file

    Returns:
        ContentResult with extracted text or error
    """
    import os

    if not os.path.exists(file_path):
        return ContentResult(
            text="",
            title="",
            source_type="file",
            error="File not found."
        )

    filename = os.path.basename(file_path)
    extension = os.path.splitext(filename)[1].lower()

    try:
        if extension == '.txt':
            return _extract_from_txt(file_path, filename)
        elif extension == '.srt':
            return _extract_from_srt(file_path, filename)
        elif extension == '.pdf':
            return _extract_from_pdf(file_path, filename)
        else:
            return ContentResult(
                text="",
                title=filename,
                source_type="file",
                error=f"Unsupported file type: {extension}. Supported: .txt, .srt, .pdf"
            )
    except Exception as e:
        return ContentResult(
            text="",
            title=filename,
            source_type="file",
            error=f"Error reading file: {str(e)}"
        )


def _extract_from_txt(file_path: str, filename: str) -> ContentResult:
    """Extract text from a plain text file."""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                text = f.read()
            return ContentResult(
                text=text.strip(),
                title=filename,
                source_type="file"
            )
        except UnicodeDecodeError:
            continue

    return ContentResult(
        text="",
        title=filename,
        source_type="file",
        error="Could not decode file. Please ensure it's a valid text file."
    )


def _extract_from_srt(file_path: str, filename: str) -> ContentResult:
    """Extract text from an SRT subtitle file."""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue
    else:
        return ContentResult(
            text="",
            title=filename,
            source_type="file",
            error="Could not decode subtitle file."
        )

    # Parse SRT format
    # SRT format: index, timestamp, text, blank line
    lines = content.split('\n')
    text_lines = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip index numbers
        if line.isdigit():
            i += 1
            continue

        # Skip timestamp lines (contain -->)
        if '-->' in line:
            i += 1
            continue

        # Skip empty lines
        if not line:
            i += 1
            continue

        # This is a text line
        # Remove HTML tags like <i>, </i>, etc.
        line = re.sub(r'<[^>]+>', '', line)
        text_lines.append(line)
        i += 1

    full_text = ' '.join(text_lines)
    full_text = re.sub(r'\s+', ' ', full_text).strip()

    return ContentResult(
        text=full_text,
        title=filename,
        source_type="file"
    )


def _extract_from_pdf(file_path: str, filename: str) -> ContentResult:
    """Extract text from a PDF file."""
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        return ContentResult(
            text="",
            title=filename,
            source_type="file",
            error="PyPDF2 not installed. Run: pip install PyPDF2"
        )

    try:
        reader = PdfReader(file_path)
        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        full_text = ' '.join(text_parts)
        full_text = re.sub(r'\s+', ' ', full_text).strip()

        if not full_text:
            return ContentResult(
                text="",
                title=filename,
                source_type="file",
                error="Could not extract text from PDF. It may be image-based or protected."
            )

        return ContentResult(
            text=full_text,
            title=filename,
            source_type="file"
        )

    except Exception as e:
        return ContentResult(
            text="",
            title=filename,
            source_type="file",
            error=f"Error reading PDF: {str(e)}"
        )


# ============ Helper Functions ============

def detect_source_type(input_text: str) -> str:
    """
    Detect the type of content source from user input.

    Args:
        input_text: URL or text provided by user

    Returns:
        'youtube', 'website', or 'text'
    """
    input_lower = input_text.lower().strip()

    if 'youtube.com' in input_lower or 'youtu.be' in input_lower:
        return 'youtube'
    elif input_lower.startswith(('http://', 'https://', 'www.')):
        return 'website'
    else:
        return 'text'


def extract_content(source: str, source_type: str = None, file_path: str = None) -> ContentResult:
    """
    Extract content from any source type.

    Args:
        source: URL or text content
        source_type: 'youtube', 'website', 'file', or 'text' (auto-detected if None)
        file_path: Path to file (required if source_type is 'file')

    Returns:
        ContentResult with extracted text
    """
    if source_type is None:
        source_type = detect_source_type(source)

    if source_type == 'youtube':
        return extract_youtube_transcript(source)
    elif source_type == 'website':
        return fetch_website_content(source)
    elif source_type == 'file' and file_path:
        return extract_text_from_file(file_path)
    elif source_type == 'text':
        return ContentResult(
            text=source,
            title="Pasted Text",
            source_type="text"
        )
    else:
        return ContentResult(
            text="",
            title="",
            source_type=source_type or "unknown",
            error="Invalid source type or missing file path."
        )


if __name__ == "__main__":
    # Test YouTube extraction
    print("Testing YouTube extraction...")
    result = extract_youtube_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print(f"  Source: {result.source_type}")
    print(f"  Error: {result.error}" if result.error else f"  Text length: {len(result.text)}")

    # Test website extraction
    print("\nTesting website extraction...")
    result = fetch_website_content("https://es.wikipedia.org/wiki/Espa%C3%B1ol")
    print(f"  Source: {result.source_type}")
    print(f"  Title: {result.title}")
    print(f"  Error: {result.error}" if result.error else f"  Text length: {len(result.text)}")
