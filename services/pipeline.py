"""
Processing pipeline module for orchestrating the full file processing workflow.

Coordinates the extraction, translation, and PDF generation stages for batch
processing of English PDF files to Sinhala.
"""

import os
from typing import Callable, List, Optional
from services.pdf_extractor import extract_text_from_pdf
from services.translator import translate_text
from services.pdf_writer import create_pdf


def process_files(
    files: List[str],
    output_dir: str,
    progress_callback: Optional[Callable[[int, int, Optional[str]], None]] = None,
    chunk_callback: Optional[Callable[[int, int], None]] = None,
) -> None:
    """
    Process multiple PDF files through the full pipeline: extract, translate, write.

    Orchestrates the extraction of text from English PDFs, translation to Sinhala,
    and generation of translated PDFs. Handles errors gracefully, continuing to
    process remaining files if one fails.

    Args:
        files: List of file paths to PDF files for processing
        output_dir: Directory where translated PDFs will be written
        progress_callback: Optional callback function that receives (current_file_index, total_files, error)
                          Called after each file completes (whether success or error).
                          error is None on success, or a string error message on failure.

    Returns:
        None

    Raises:
        ValueError: If output_dir is invalid or files list is empty
    """
    if not files:
        raise ValueError("files list cannot be empty")

    if not output_dir or not isinstance(output_dir, str):
        raise ValueError("output_dir must be a non-empty string")

    # Create output directory if it doesn't exist
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to create output directory '{output_dir}': {exc}"
        ) from exc

    total_files = len(files)

    for current_index, file_path in enumerate(files, start=1):
        error: Optional[str] = None
        try:
            # Stage 1: Extract text from PDF
            text = extract_text_from_pdf(file_path)

            # Stage 2: Translate text to Sinhala
            translated = translate_text(text, on_chunk=chunk_callback)

            # Stage 3: Write translated text to PDF (collision-safe name)
            stem, ext = os.path.splitext(os.path.basename(file_path))
            candidate = os.path.join(output_dir, f"{stem}_sinhala{ext}")
            counter = 1
            while os.path.exists(candidate):
                candidate = os.path.join(output_dir, f"{stem}_sinhala_{counter}{ext}")
                counter += 1
            output_path = candidate
            create_pdf(translated, output_path)

        except Exception as exc:
            error = str(exc)

        finally:
            # Always call progress callback if provided
            if progress_callback is not None:
                progress_callback(current_index, total_files, error)
