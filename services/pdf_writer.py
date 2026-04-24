import os
import sys
import re
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4


def _base_path(*rel_parts: str) -> str:
    """Return absolute path that works for both dev and PyInstaller bundle."""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *rel_parts)

# Matches one or more consecutive characters in the Sinhala Unicode block,
# including ZWJ/ZWNJ which are used to form Sinhala conjunct characters.
_SINHALA = re.compile(r'([඀-෿‌‍]+)')

_font_registered = False


def _register_sinhala_font() -> None:
    global _font_registered
    if _font_registered:
        return
    font_path = _base_path('fonts', 'NotoSansSinhala-Regular.ttf')
    pdfmetrics.registerFont(TTFont('NotoSinhala', font_path))
    _font_registered = True


def _mf(text: str) -> str:
    """
    Wrap Sinhala character runs in NotoSinhala font tags.

    All other characters (Latin, digits, punctuation) are left untagged and
    render in the paragraph's base Helvetica font, which has full Latin coverage.
    NotoSansSinhala has no Latin glyphs — using it as the sole font causes every
    English technical term to render as blank space.
    """
    parts = _SINHALA.split(text)
    out = []
    for part in parts:
        if not part:
            continue
        if _SINHALA.fullmatch(part):
            out.append(f'<font name="NotoSinhala">{part}</font>')
        else:
            out.append(part)
    return ''.join(out)


def _split_paragraphs(text: str):
    return [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]


def _make_styles() -> dict:
    # Helvetica is a built-in ReportLab font with full Latin/ASCII coverage.
    # Sinhala runs are tagged inline via _mf(), so the base font only needs
    # to cover Latin characters reliably.
    return {
        'h1': ParagraphStyle(
            'H1',
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=22,
            spaceBefore=16,
            spaceAfter=10,
            alignment=TA_LEFT,
        ),
        'h2': ParagraphStyle(
            'H2',
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=18,
            spaceBefore=12,
            spaceAfter=8,
            alignment=TA_LEFT,
        ),
        'body': ParagraphStyle(
            'Body',
            fontName='Helvetica',
            fontSize=11,
            leading=18,
            spaceBefore=4,
            spaceAfter=6,
            alignment=TA_LEFT,
        ),
    }


def create_pdf(text: str, output_path: str) -> None:
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    _register_sinhala_font()
    styles = _make_styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=50, rightMargin=50,
        topMargin=50, bottomMargin=50,
    )

    story = []
    paragraphs = _split_paragraphs(text)

    for para in paragraphs:
        if para.startswith("[H1]"):
            story.append(Paragraph(_mf(para[4:].strip()), styles['h1']))
            continue

        if para.startswith("[H2]"):
            story.append(Paragraph(_mf(para[4:].strip()), styles['h2']))
            continue

        if para.startswith("▸") or para.startswith("-"):
            bullet_text = para.replace("▸", "•").strip()
            story.append(Paragraph(_mf(bullet_text), styles['body']))
            story.append(Spacer(1, 6))
            continue

        # Normal paragraph (IMPORTANT: keep as one block)
        story.append(Paragraph(_mf(para), styles['body']))
        story.append(Spacer(1, 10))

    doc.build(story)