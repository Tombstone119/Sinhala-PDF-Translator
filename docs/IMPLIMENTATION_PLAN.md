# 📄 English → Sinhala PDF Translator (Desktop App)

## 🎯 Objective
Build a **PyQt6 desktop application** that:
- Accepts **multiple English PDFs**
- Translates them into **Sinhala using local Gemma (gemma4:e4b via Ollama)**
- Outputs **complete, accurate Sinhala PDFs**
- Ensures **no loss of critical information**

---

## ⚠️ CRITICAL REQUIREMENTS

1. **DO NOT skip or summarize content**
2. **DO NOT omit numbers, names, or technical terms**
3. **Preserve meaning exactly**
4. **Translate EVERYTHING**
5. Maintain:
   - Paragraph structure
   - Lists
   - Headings (as plain text)

---

## 🧱 Architecture


[PyQt UI]
↓
[PDF Extractor (PyMuPDF)]
↓
[Smart Chunker]
↓
[Translator (Ollama - gemma4:e4b)]
↓
[PDF Generator (ReportLab with Sinhala font)]
↓
[Output Files]


---

## 📦 Dependencies

```bash
pip install PyQt6 pymupdf reportlab requests
📂 Folder Structure
project/
│
├── main.py
├── ui/
├── services/
│   ├── pdf_extractor.py
│   ├── translator.py
│   ├── chunker.py
│   └── pdf_writer.py
│
├── fonts/
│   └── NotoSansSinhala-Regular.ttf
│
└── output/
1️⃣ PDF TEXT EXTRACTION (High Accuracy)

Use PyMuPDF:

import fitz

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    full_text = []

    for page in doc:
        text = page.get_text("text")
        full_text.append(text)

    return "\n\n".join(full_text)
2️⃣ SMART CHUNKING (IMPORTANT FOR ACCURACY)

❗ Do NOT break sentences randomly.

def chunk_text(text, max_chars=1200):
    import re

    sentences = re.split(r'(?<=[.!?]) +', text)
    
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) < max_chars:
            current += sentence + " "
        else:
            chunks.append(current.strip())
            current = sentence + " "

    if current:
        chunks.append(current.strip())

    return chunks
3️⃣ TRANSLATION (STRICT ACCURACY MODE)

Use Ollama API (gemma4:e4b)

🔴 VERY IMPORTANT PROMPT DESIGN
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def translate_chunk(chunk):
    prompt = f"""
You are a professional translator.

Translate the following English text into Sinhala.

STRICT RULES:
- Do NOT summarize
- Do NOT omit any detail
- Preserve numbers, names, dates, and technical terms exactly
- Maintain full meaning and context
- Output ONLY Sinhala text
- If a word should remain in English (like technical terms), keep it unchanged

TEXT:
{chunk}
"""

    response = requests.post(OLLAMA_URL, json={
        "model": "gemma4:e4b",
        "prompt": prompt,
        "stream": False
    })

    return response.json()["response"]
4️⃣ FULL TEXT TRANSLATION
def translate_text(text):
    chunks = chunk_text(text)
    translated_chunks = []

    for chunk in chunks:
        translated = translate_chunk(chunk)
        translated_chunks.append(translated)

    return "\n\n".join(translated_chunks)
5️⃣ SINHALA PDF GENERATION (FONT SUPPORT REQUIRED)
⚠️ MUST USE SINHALA FONT
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('Sinhala', 'fonts/NotoSansSinhala-Regular.ttf'))

def create_pdf(text, output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    y = height - 40

    for line in text.split("\n"):
        c.setFont("Sinhala", 11)
        c.drawString(40, y, line)
        y -= 16

        if y < 40:
            c.showPage()
            y = height - 40

    c.save()
6️⃣ FILE PROCESSING PIPELINE
import os

def process_files(files, output_dir):
    for file in files:
        text = extract_text_from_pdf(file)
        translated = translate_text(text)

        filename = os.path.basename(file)
        output_path = os.path.join(output_dir, filename)

        create_pdf(translated, output_path)
7️⃣ PYQT UI (MINIMAL + FUNCTIONAL)
Features:
Multi-file selection
Output folder selection
Start button
Progress bar
UI Layout
[ Select PDFs ]
[ Select Output Folder ]

[ Start Translation ]

[ Progress Bar ]
8️⃣ PERFORMANCE SETTINGS (FOR GTX 1650)
Chunk size: 1000–1200 chars
No parallel GPU calls
Sequential processing
Keep Ollama running
9️⃣ PACKAGING
pip install pyinstaller
pyinstaller --onefile --windowed main.py
🔟 FINAL QUALITY GUARANTEES

To ensure no critical detail is lost:

Sentence-aware chunking ✅
Strict translation prompt ✅
No summarization ✅
Full text reconstruction ✅
🚫 DO NOT DO
Do not summarize text
Do not skip long paragraphs
Do not attempt layout recreation
Do not use cloud APIs
✅ RESULT

A fully offline desktop app that:

Translates PDFs → Sinhala
Keeps all critical content
Works efficiently on GTX 1650
Supports batch processing

---

If you want next step, I can:
- Generate the **complete working code (all files ready)**
- Or upgrade this to **preserve tables + formatting (advanced version)**