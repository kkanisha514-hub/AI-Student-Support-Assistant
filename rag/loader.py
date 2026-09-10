"""
Loads college documents from the documents directory and extracts
(source_name, page_number, text) segments ready for chunking.

Supported formats:
- .txt  : plain text. If the file contains markers of the form
          "[SOURCE: <name>, PAGE: <n>]" at the start of a block, that
          metadata is used. Otherwise the whole file is treated as page 1.
- .pdf  : real PDF page extraction via pypdf.
"""
import os
import re
from dataclasses import dataclass
from typing import List

from config import settings
from logging_config import get_logger

logger = get_logger(__name__)

MARKER_RE = re.compile(r"\[SOURCE:\s*(.*?),\s*PAGE:\s*(\d+)\]")


@dataclass
class DocSegment:
    source: str
    page: int
    text: str


def _load_txt(path: str) -> List[DocSegment]:
    filename = os.path.basename(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    matches = list(MARKER_RE.finditer(content))
    segments: List[DocSegment] = []

    if matches:
        for i, m in enumerate(matches):
            source = m.group(1).strip()
            page = int(m.group(2))
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            text = content[start:end].strip()
            if text:
                segments.append(DocSegment(source=source, page=page, text=text))
    else:
        # No markers -> whole file is page 1
        segments.append(DocSegment(source=filename, page=1, text=content.strip()))

    return segments


def _load_pdf(path: str) -> List[DocSegment]:
    from pypdf import PdfReader

    filename = os.path.basename(path)
    reader = PdfReader(path)
    segments: List[DocSegment] = []
    for i, page in enumerate(reader.pages):
        text = (page.extract_text() or "").strip()
        if text:
            segments.append(DocSegment(source=filename, page=i + 1, text=text))
    return segments


def load_all_documents(documents_dir: str = None) -> List[DocSegment]:
    """Scan the documents directory and return all extracted segments."""
    documents_dir = documents_dir or settings.DOCUMENTS_DIR
    all_segments: List[DocSegment] = []

    if not os.path.isdir(documents_dir):
        logger.warning(f"Documents directory not found: {documents_dir}")
        return all_segments

    for filename in sorted(os.listdir(documents_dir)):
        full_path = os.path.join(documents_dir, filename)
        if not os.path.isfile(full_path):
            continue
        try:
            if filename.lower().endswith(".txt"):
                all_segments.extend(_load_txt(full_path))
            elif filename.lower().endswith(".pdf"):
                all_segments.extend(_load_pdf(full_path))
            else:
                logger.info(f"Skipping unsupported file type: {filename}")
        except Exception as e:
            logger.error(f"Failed to load {filename}: {e}")

    logger.info(f"Loaded {len(all_segments)} document segments from {documents_dir}")
    return all_segments
