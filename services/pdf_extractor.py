import fitz

_H1_MIN_SIZE = 16.0
_H2_MIN_SIZE = 12.0


def extract_text_from_pdf(file_path: str) -> str:
    try:
        with fitz.open(file_path) as doc:
            pages_text = []
            for page in doc:
                page_dict = page.get_text("dict")
                blocks = _page_blocks(page_dict)
                if blocks:
                    pages_text.append("\n\n".join(blocks))
            return "\n\n".join(pages_text)
    except Exception as exc:
        raise RuntimeError(f"Failed to extract text from '{file_path}': {exc}") from exc


def _block_max_font(block: dict) -> float:
    return max(
        (span.get("size", 0)
         for line in block.get("lines", [])
         for span in line.get("spans", [])),
        default=0.0,
    )


def _page_blocks(page_dict: dict) -> list:
    raw = []
    for block in page_dict.get("blocks", []):
        if block.get("type") != 0:
            continue

        lines = []
        for line in block.get("lines", []):
            # Join all spans in a line preserving their original spacing
            parts = [s["text"] for s in line.get("spans", [])]
            joined = "".join(parts).strip()
            if joined:
                lines.append(joined)

        if not lines:
            continue

        text = "\n".join(lines)
        fs = _block_max_font(block)

        if fs >= _H1_MIN_SIZE:
            text = f"[H1]{text}"
        elif fs >= _H2_MIN_SIZE:
            text = f"[H2]{text}"

        x0, y0 = block["bbox"][0], block["bbox"][1]
        raw.append((x0, y0, text))

    # Sort by reading order: y-band of 15pt for column tolerance, then left-to-right
    raw.sort(key=lambda b: (int(b[1] / 15), b[0]))
    return [b[2] for b in raw]
