"""
Paragraph-aware text chunking for PDF translation.

Chunks by paragraph boundaries first, falling back to sentence splitting
only for paragraphs that individually exceed max_chars.
"""

import re
from typing import List


def chunk_text(text: str, max_chars: int = 2500) -> List[str]:
    if max_chars < 1:
        raise ValueError(f"max_chars must be at least 1, got {max_chars}")
    if not text or not text.strip():
        return []

    paragraphs = re.split(r'\n{2,}', text)

    chunks: List[str] = []
    current_parts: List[str] = []
    current_len = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        sep = 2 if current_parts else 0  # "\n\n" separator cost
        if current_len + sep + len(para) <= max_chars:
            current_parts.append(para)
            current_len += sep + len(para)
        else:
            if current_parts:
                chunks.append("\n\n".join(current_parts))
                current_parts = []
                current_len = 0

            if len(para) <= max_chars:
                current_parts = [para]
                current_len = len(para)
            else:
                sub = _split_by_sentences(para, max_chars)
                chunks.extend(sub[:-1])
                current_parts = [sub[-1]] if sub else []
                current_len = len(current_parts[0]) if current_parts else 0

    if current_parts:
        chunks.append("\n\n".join(current_parts))

    return chunks


def _split_by_sentences(text: str, max_chars: int) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks: List[str] = []
    current: List[str] = []
    current_len = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        needed = len(sentence) + (1 if current else 0)
        if current_len + needed <= max_chars:
            current.append(sentence)
            current_len += needed
        else:
            if current:
                chunks.append(" ".join(current))
            current = [sentence]
            current_len = len(sentence)

    if current:
        chunks.append(" ".join(current))

    return chunks or [text[:max_chars]]
