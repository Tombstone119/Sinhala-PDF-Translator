#!/usr/bin/env python3
"""
Regenerate CareerCraft AI Proposal in Sinhala with correct mixed-script rendering.

Root-cause: NotoSerifSinhala contains zero Latin glyphs, so all English technical
terms rendered as blank space. Fix: use Helvetica (built-in, full Latin) as the
paragraph base font, and auto-wrap only Sinhala character runs in NotoSinhala
font tags via mf(). Latin text passes through untouched.
"""
import os, re, urllib.request

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Sinhala font (download if absent) ─────────────────────────────────────────
HERE  = os.path.dirname(os.path.abspath(__file__))
_FMAP = {
    "NotoSinhala":      "NotoSerifSinhala-Regular.ttf",
    "NotoSinhala-Bold": "NotoSerifSinhala-Bold.ttf",
}
_BASE = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSerifSinhala/"

for alias, fname in _FMAP.items():
    fpath = os.path.join(HERE, fname)
    if not os.path.exists(fpath):
        print(f"Downloading {fname}...")
        urllib.request.urlretrieve(_BASE + fname, fpath)
    pdfmetrics.registerFont(TTFont(alias, fpath))

# Helvetica is a built-in Type1 font in reportlab — covers full ASCII + Latin-1.

# ── Font-switching helper ──────────────────────────────────────────────────────
_SI = re.compile(r'([඀-෿‌‍]+)')

def mf(text, bold=False):
    """
    Wrap Sinhala character runs in NotoSinhala font tags.
    Everything else (Latin, digits, punctuation) stays in base Helvetica.
    Safe to call on all-Latin strings — returns them unchanged.
    """
    sf = "NotoSinhala-Bold" if bold else "NotoSinhala"
    out = []
    for part in _SI.split(text):
        if not part:
            continue
        out.append(f'<font name="{sf}">{part}</font>' if _SI.fullmatch(part) else part)
    return "".join(out)

# ── Palette ────────────────────────────────────────────────────────────────────
NAVY    = colors.HexColor("#1a2744")
TEAL    = colors.HexColor("#2e86ab")
ROW_A   = colors.HexColor("#e8edf5")
RULE    = colors.HexColor("#b0bcd0")
FOOT_BG = colors.HexColor("#f0f4fa")

# ── Styles — Helvetica base gives guaranteed Latin rendering ───────────────────
def _ps(name, font="Helvetica", size=9, leading=15, color=NAVY, align=TA_LEFT, **kw):
    return ParagraphStyle(name, fontName=font, fontSize=size, leading=leading,
                          textColor=color, alignment=align, **kw)

ST = {
    "title":  _ps("title",  "Helvetica-Bold", 22, 28, colors.white),
    "sub":    _ps("sub",    "Helvetica",       11, 16, TEAL),
    "cap":    _ps("cap",    "Helvetica",        9, 13, colors.HexColor("#8899bb")),
    "stat":   _ps("stat",   "Helvetica-Bold",  12, 18, TEAL, TA_CENTER),
    "h2":     _ps("h2",     "Helvetica-Bold",   8, 13, NAVY, spaceAfter=2),
    "body":   _ps("body",   "Helvetica",        9, 16, NAVY, TA_JUSTIFY, spaceAfter=4),
    "th":     _ps("th",     "Helvetica-Bold",   9, 13, colors.white),
    "tk":     _ps("tk",     "Helvetica-Bold",  8.5,14, NAVY),
    "tv":     _ps("tv",     "Helvetica",       8.5,14, NAVY),
    "bul":    _ps("bul",    "Helvetica",       8.5,14, NAVY, leftIndent=8),
    "foot":   _ps("foot",   "Helvetica-Bold",  10, 16, NAVY, TA_CENTER),
    "footi":  _ps("footi",  "Helvetica",       8.5,15, NAVY, TA_CENTER),
}

def P(text, s="body"):
    return Paragraph(text, ST[s])

def sh(text):
    """Section heading: bold line + hairline rule. Runs mf() on text."""
    return [P(mf(text), "h2"), HRFlowable(width="100%", thickness=0.5, color=NAVY, spaceAfter=6)]


# ── Header ─────────────────────────────────────────────────────────────────────
def build_header():
    left = Table([
        [P("CareerCraft AI", "title")],
        [P("Multi-Agent Career Acceleration System", "sub")],
        [P("Veracity AI - 3rd Iteration Hackathon Proposal", "cap")],
    ], colWidths=[113*mm])
    left.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), NAVY),
        ("TOPPADDING",    (0,0),(-1, 0), 10),
        ("BOTTOMPADDING", (0,0),(-1, 0),  2),
        ("BOTTOMPADDING", (0,1),(-1, 1),  2),
        ("BOTTOMPADDING", (0,2),(-1, 2), 12),
        ("LEFTPADDING",   (0,0),(-1,-1), 14),
        ("RIGHTPADDING",  (0,0),(-1,-1),  8),
    ]))

    right = Table(
        [[P(s, "stat")] for s in ("8 Agents","3 External APIs","Vector Memory","Deployed on AWS")],
        colWidths=[57*mm]
    )
    right.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), NAVY),
        ("TOPPADDING",    (0,0),(-1,-1),  7),
        ("BOTTOMPADDING", (0,0),(-1,-1),  6),
    ]))

    outer = Table([[left, right]], colWidths=[113*mm, 57*mm])
    outer.setStyle(TableStyle([
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
    ]))
    return outer


# ── Agents table ───────────────────────────────────────────────────────────────
def build_agents():
    rows = [
        ("1. Orchestrator Agent",
         "රැකියා ලැයිස්තු ආදානයන් ලබා ගනී; "
         "කාර්යය විසුරුවා හරින අතර උප කාර්යයන් මාර්ගගත කරයි"),
        ("2. JD Analyzer Agent",
         "රැකියා විස්තර විශ්ලේෂණය කරයි: "
         "අවශ්‍ය කුසලතා, ස්වරය සහ සන්දර්භය හඳුනා ගනී"),
        ("3. Resume Parser Agent",
         "අයදුම්කරුවන්ගේ CV "
         "වෙතින් ව්‍යුහගත දත්ත වෙන් කරයි (කුසලතා, අත්දැකීම්, හිඩැස්)"),
        ("4. Profile Matcher Agent",
         "Vector similarity "
         "භාවිතයෙන් ගැලපීම මැනීම; JD ට අනුව අපේක්ෂකයින් ශ්‍රේණිගත කරයි"),
        ("5. CV Rewriter Agent",
         "JD "
         "එකට අනුව සකස් කරන ලද CV අන්තර්ගතය ජනනය කරයි"),
        ("6. Cover Letter Agent",
         "Company + JD "
         "සන්දර්භය භාවිතා කර පුද්ගලික Cover Letters කෙටුම්පත් කරයි"),
        ("7. Memory & State Agent",
         "Session "
         "සන්දර්භය, පරිශීලක මනාපයන් සහ අතීත අයදුම්පත් සුරකියි"),
        ("8. Output Formatter Agent",
         "අවසාන DOCX/PDF "
         "සම්පාදනය කරයි; Email හෝ Dashboard හරහා අපනයනය කරයි"),
    ]

    data = (
        [[P("Agent Node", "th"), P(mf("භූමිකාව සහ වගකීම"), "th")]]
        + [[P(a, "tk"), P(mf(d), "tv")] for a, d in rows]
    )
    t = Table(data, colWidths=[60*mm, 110*mm], repeatRows=1)
    style = [
        ("BACKGROUND", (0,0),(-1, 0), NAVY),
        ("BOX",        (0,0),(-1,-1), 0.5, RULE),
        ("INNERGRID",  (0,0),(-1,-1), 0.3, RULE),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]
    for i in range(1, len(data)):
        style.append(("BACKGROUND", (0,i),(-1,i), ROW_A if i%2==1 else colors.white))
    t.setStyle(TableStyle(style))
    return t


# ── Two-column: External APIs + Memory Layer ───────────────────────────────────
def build_two_col():
    apis = [
        ("OpenAI GPT-4o",
         "CV නැවත ලිවීම, Cover Letter ජනනය, කුසලතා හිඩැස් විශ්ලේෂණය"),
        ("LinkedIn Jobs API",
         "Live Job Data සහ JD සන්දර්භය සඳහා"),
        ("SendGrid API",
         "Application Package ස්වයංක්‍රීය Email බෙදාහැරීම"),
    ]
    mems = [
        ("Pinecone Vector DB",
         "Semantic matching සඳහා CV Profile Embeddings ගබඩා කරයි"),
        ("PostgreSQL",
         "Session State, පරිශීලක මනාපයන් සහ Application History සුරකියි"),
        ("Redis Cache",
         "Session Agents අතර Short-term Context හුවමාරු කරයි"),
    ]

    def bul(k, v):
        return P(f"&gt;  <b>{k}</b> - {mf(v)}", "bul")

    lh = P(mf("බාහිර API ඒකාබද්ධකරණ"), "h2")
    rh = P("Memory Layer", "h2")
    lr = HRFlowable(width=75*mm, thickness=0.5, color=NAVY, spaceAfter=4)
    rr = HRFlowable(width=79*mm, thickness=0.5, color=NAVY, spaceAfter=4)

    rows = (
        [[lh, rh], [lr, rr]]
        + [[bul(k, v), bul(km, vm)] for (k,v),(km,vm) in zip(apis, mems)]
    )
    t = Table(rows, colWidths=[83*mm, 87*mm])
    t.setStyle(TableStyle([
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("TOPPADDING",    (0,0),(-1,-1), 3),
        ("BOTTOMPADDING", (0,0),(-1,-1), 3),
        ("LEFTPADDING",   (0,0),(-1,-1), 4),
        ("RIGHTPADDING",  (0,0),(0, -1), 8),
        ("LEFTPADDING",   (1,0),(1, -1), 10),
        ("RIGHTPADDING",  (1,0),(1, -1), 4),
        ("LINEAFTER",     (0,0),(0, -1), 0.5, RULE),
    ]))
    return t


# ── Deployment table ───────────────────────────────────────────────────────────
def build_deployment():
    rows = [
        ("Infrastructure",
         "AWS EC2 (agent runners) + AWS Lambda (event-driven triggers) + S3 (document storage)"),
        ("Orchestration",
         "LangGraph multi-agent graph; Agents communicate via async message queue (SQS)"),
        ("Frontend",
         mf("CV upload, job URL input, සහ result download සඳහා React Dashboard")),
        ("Pre-Hack Scope",
         "End-to-end pipeline: JD input -> matched CV + Cover Letter -> Email delivery"),
        ("Deep Hack Goal",
         mf("Batch processing, ATS score feedback loop, multi-job comparison, සහ mobile UI")),
    ]
    data = [[P(k, "tk"), P(v, "tv")] for k, v in rows]
    t = Table(data, colWidths=[40*mm, 130*mm])
    style = [
        ("BOX",       (0,0),(-1,-1), 0.5, RULE),
        ("INNERGRID", (0,0),(-1,-1), 0.3, RULE),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]
    for i in range(len(data)):
        style.append(("BACKGROUND", (0,i),(0,i), ROW_A))
    t.setStyle(TableStyle(style))
    return t


# ── Footer callout ─────────────────────────────────────────────────────────────
def build_footer():
    t = Table([
        [P("CareerCraft AI " + mf("ජය ගන්නේ ඇයි?"), "foot")],
        [P(
            mf("සැබෑ බලපෑම") + " - " +
            mf("තාක්ෂණිකව ගැඹුරු") + " - Hackathon " +
            mf("කාල රාමුව තුළ සම්පූර්ණයෙන්ම ගොඩනගා ගත හැකි") + " - " +
            mf("ප්‍රවෘත්තියට පැහැදිලි මාර්ගයක් සහිත වාණිජීය වශයෙන් යෝග්‍ය නිෂ්පාදනයක්"),
            "footi"
        )],
    ], colWidths=[170*mm])
    t.setStyle(TableStyle([
        ("BOX",           (0,0),(-1,-1), 2, TEAL),
        ("BACKGROUND",    (0,0),(-1,-1), FOOT_BG),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1),  8),
        ("LEFTPADDING",   (0,0),(-1,-1), 15),
        ("RIGHTPADDING",  (0,0),(-1,-1), 15),
    ]))
    return t


# ── Assemble story and build ───────────────────────────────────────────────────
OUTPUT = r"C:\Users\kodag\Downloads\CareerCraft_AI_Proposal_sinhala_fixed.pdf"

doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=20*mm, rightMargin=20*mm,
    topMargin=15*mm,  bottomMargin=15*mm,
)

problem_body = mf(
    "CV සහ ආවරණ ලිපියක් සකස් කිරීමට රැකියා අයදුම්කරුවන්ට "
    "පැය 5 ත් 10 ත් අතර කාලයක් ගතවේ. "
    "කෙසේ වෙතත්, ඔවුන්ගේ අයදුම්පත සෑම රැකියාවකටම කොපමණ "
    "හොඳින් අනුවර්තනය කර ඇත්දැයි ඔවුන්ට තවමත් අදහසක් නැත. "
    "CareerCraft AI යනු අයදුම්කරුවෙකුට රැකියා විස්තරයක් ලබා "
    "ගැනීමට, අයදුම්කරුගේ CV එකක් තක්සේරු කිරීමට, "
    "අයදුම්කරුට අඩු වන කුසලතා ස්වයංක්‍රීයව තීරණය කිරීමට, "
    "එම හිඩැස් ආමන්ත්‍රණය කිරීම සඳහා CV හි කොටස් කිහිපයක් "
    "නැවත ලිවීමට, පුද්ගලීකරණය කරන ලද Cover Letter "
    "සකස් කිරීමට සහ රැකියා විස්තරය, CV, සහ Cover Letter "
    "මිනිත්තු 2 කට අඩු කාලයක් තුළ ස්වයංක්‍රීයව ඉදිරිපත් "
    "කිරීමට භාවිත කළ හැකි සම්පූර්ණයෙන්ම ස්වයංක්‍රීය "
    "පද්ධතියකි."
)

story = [build_header(), Spacer(1, 7*mm)]
story += sh("ගැටලු ප්‍රකාශය සහ දර්ශනය")
story += [P(problem_body), Spacer(1, 4*mm)]
story += sh("Multi-Agent Architecture  (8 Nodes - Hierarchical + Sequential)")
story += [build_agents(), Spacer(1, 6*mm)]
story += [build_two_col(), Spacer(1, 6*mm)]
story += sh("යෙදවීමේ සැලැස්ම")
story += [build_deployment(), Spacer(1, 8*mm), build_footer()]

doc.build(story)
print(f"Saved: {OUTPUT}")
