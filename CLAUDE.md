# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A PyQt6 desktop application that batch-translates English PDFs into Sinhala using a local Ollama instance. All processing is offline; no content is summarized or omitted.

**Required external service:** Ollama running on `http://localhost:11434` with model `gemma4:e4b` pulled.

## Running the App

```bash
python main.py
```

No build step. Dependencies must be installed manually (no requirements.txt exists):

```bash
pip install PyQt6 pymupdf reportlab requests
```

## Architecture

Processing pipeline triggered per-file in a background `QThread` worker:

```
PDF file
  → services/pdf_extractor.py   # PyMuPDF: extract text blocks, tag headings as [H1]/[H2]
  → services/chunker.py         # Paragraph-aware split (max 2500 chars)
  → services/translator.py      # POST to Ollama 2 chunks at a time; strict prompt forbids summarization
  → services/pdf_writer.py      # ReportLab: reconstruct styled A4 PDF with mixed fonts
```

`services/pipeline.py` (`process_files()`) orchestrates the above and reports progress via two callbacks: `progress_callback(file_index, total_files, error)` fires once per completed file; `chunk_callback(chunks_done, chunks_total)` fires after every chunk and is threaded through to the UI status label.

`main.py` owns the UI (`MainWindow`) and the worker thread (`TranslationWorker`). It emits two signals: `progress` (per-file) and `chunk_progress` (per-chunk). `_on_finished` only overwrites the status label on full success — errors stay visible.

## Key Implementation Details

**Mixed-script font rendering** (`pdf_writer.py`): ReportLab uses Helvetica as the base font. Runs of Sinhala characters (`[඀-෿‌‍]+`) are wrapped in font-switch tags via regex because NotoSansSinhala contains no Latin glyphs.

**Heading detection** (`pdf_extractor.py`): Blocks with max font size ≥ 16 pt → `[H1]`; ≥ 12 pt → `[H2]`. These tags survive through translation and drive styling in the writer.

**Parallel Ollama calls** (`translator.py`): Two chunks are sent concurrently via `ThreadPoolExecutor(max_workers=2)`. Chunk order in the final output is preserved via index-keyed futures regardless of completion order. Timeout is 600 s per request (accounts for Ollama queue time + inference). Hardcoded constants:
- URL: `http://localhost:11434/api/generate`
- Model: `gemma4:e4b`

**Ollama must be started with `OLLAMA_NUM_PARALLEL=2`** (set as a User environment variable on Windows, then restart Ollama) — without it the second concurrent request queues behind the first, which can cause the Python-side timeout to fire while the chunk is still waiting in Ollama's queue.

**Output naming** (`pipeline.py`): Collision-safe — appends `_1`, `_2`, … if a file with the same name already exists in the output directory.

**Fonts**: `NotoSansSinhala-Regular.ttf` lives in `fonts/`. Two additional Sinhala serif fonts (`NotoSerifSinhala-Regular.ttf`, `NotoSerifSinhala-Bold.ttf`) sit at the project root.

## Separate Utility

`generate_sinhala_pdf.py` is a standalone script (unrelated to the main app) that generates a styled CareerCraft AI Proposal PDF with mixed Sinhala/English content using ReportLab directly.
