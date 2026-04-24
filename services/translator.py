"""
Translation module for converting English text to Sinhala using Ollama.

Handles text translation via local Ollama API with gemma4:e4b model.
Includes chunking and sequential processing for GTX 1650 compatibility.
"""

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional
from services.chunker import chunk_text

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma4:e4b"
OLLAMA_TIMEOUT = 600  # 10 minutes — accounts for Ollama queue time + processing


def translate_chunk(chunk: str) -> str:
    """
    Translate a single text chunk to Sinhala using Ollama.

    Sends the chunk to the local Ollama API with a strict prompt that prevents
    summarization and preserves all details, numbers, names, and technical terms.

    Args:
        chunk: A text string to translate (typically 1200 chars or less)

    Returns:
        The translated Sinhala text

    Raises:
        RuntimeError: If Ollama is unreachable, returns an error, or times out
        ValueError: If chunk is empty
    """
    if not chunk or not chunk.strip():
        raise ValueError("Chunk cannot be empty")

    prompt = f"""You are a professional translator.

Translate the following English text into Sinhala.

STRICT RULES:
- Do NOT summarize or omit any content
- Preserve numbers, names, dates, and technical terms exactly
- Maintain full meaning and context
- Output ONLY the translated text — no explanations or commentary
- If a word should remain in English (technical terms, product names), keep it unchanged
- Preserve all [H1] and [H2] tags exactly as they appear at the start of lines — do not translate or remove them
- Preserve blank lines between paragraphs exactly as they appear

TEXT:
{chunk}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=OLLAMA_TIMEOUT
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            f"Cannot connect to Ollama at {OLLAMA_URL}. "
            f"Please ensure Ollama is running on port 11434. Error: {str(e)}"
        ) from e
    except requests.exceptions.Timeout as e:
        raise RuntimeError(
            f"Ollama request timed out after {OLLAMA_TIMEOUT} seconds. "
            f"The translation may be too long or Ollama is overwhelmed. Error: {str(e)}"
        ) from e
    except requests.exceptions.RequestException as e:
        raise RuntimeError(
            f"Error communicating with Ollama API: {str(e)}"
        ) from e

    try:
        result = response.json()
        if "response" not in result:
            raise RuntimeError(
                f"Ollama returned unexpected response format: {result}"
            )
        return result["response"]
    except ValueError as e:
        raise RuntimeError(
            f"Ollama returned invalid JSON: {str(e)}"
        ) from e


def translate_text(
    text: str,
    on_chunk: Optional[Callable[[int, int], None]] = None,
) -> str:
    """
    Translate English text to Sinhala using chunking and parallel processing.

    Args:
        text: The full English text to translate
        on_chunk: Optional callback invoked after each chunk completes,
                  receiving (chunks_done, total_chunks).

    Returns:
        The translated Sinhala text with chunks separated by double newlines

    Raises:
        RuntimeError: If translation fails at any point
        ValueError: If text is empty
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("Text produced no chunks after processing")

    translated_chunks = [None] * len(chunks)
    completed = 0

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(translate_chunk, chunk): i for i, chunk in enumerate(chunks)}
        for future in as_completed(futures):
            i = futures[future]
            try:
                translated_chunks[i] = future.result()
                completed += 1
                if on_chunk:
                    on_chunk(completed, len(chunks))
            except RuntimeError as e:
                raise RuntimeError(
                    f"Translation failed on chunk {i + 1} of {len(chunks)}: {str(e)}"
                ) from e

    return "\n\n".join(translated_chunks)
