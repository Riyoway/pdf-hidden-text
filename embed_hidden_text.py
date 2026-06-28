#!/usr/bin/env python3
"""Embed text into a PDF that is invisible to humans but readable by text
extraction (i.e. by the way LLMs read PDFs).

It uses PDF text rendering mode 3 (invisible) -- the same mechanism as the
text layer of an OCR'd, searchable PDF. The text never appears on screen or in
print, yet pdftotext / pypdf / pdfminer extract it normally.

Usage:
  # Embed into an existing PDF (first page)
  python embed_hidden_text.py input.pdf -t "message for the AI" -o output.pdf

  # Embed into every page
  python embed_hidden_text.py input.pdf -t "..." --all-pages -o output.pdf

  # Embed the contents of a text file
  python embed_hidden_text.py input.pdf -f message.txt -o output.pdf

  # No input PDF -> generate a blank-looking PDF carrying the hidden text
  python embed_hidden_text.py -t "hidden text" -o output.pdf

  # Extract embedded text (what an AI would read)
  python embed_hidden_text.py --extract output.pdf
"""

import argparse
import io
import sys

# Keep Japanese/Unicode prints from crashing on Windows consoles (cp932/cp1252).
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas

# Bundled CID font (no external file needed); covers most scripts. Because the
# text is invisible, glyph coverage is irrelevant -- only the Unicode mapping
# used for extraction matters.
JP_FONT = "HeiseiKakuGo-W5"
_jp_registered = False


def _ensure_jp_font():
    global _jp_registered
    if not _jp_registered:
        pdfmetrics.registerFont(UnicodeCIDFont(JP_FONT))
        _jp_registered = True


def make_invisible_overlay(text, pagesize, font_size=8):
    """Return a single-page PDF overlay (BytesIO) containing invisible text."""
    _ensure_jp_font()
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=pagesize)
    _, height = pagesize

    text_obj = c.beginText()
    text_obj.setFont(JP_FONT, font_size)
    text_obj.setTextRenderMode(3)  # 3 = invisible

    x = 20
    y = height - 30
    leading = font_size + 2
    for line in text.splitlines() or [text]:
        text_obj.setTextOrigin(x, y)
        text_obj.textLine(line)
        y -= leading
        if y < 30:
            y = height - 30

    c.drawText(text_obj)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf


def embed_into_pdf(input_pdf, text, output_pdf, font_size=8, all_pages=False):
    """Overlay invisible text onto an existing PDF and write the result."""
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    pages_to_mark = range(len(reader.pages)) if all_pages else [0]

    for i, page in enumerate(reader.pages):
        if i in pages_to_mark:
            box = page.mediabox
            size = (float(box.width), float(box.height))
            overlay_page = PdfReader(make_invisible_overlay(text, size, font_size)).pages[0]
            page.merge_page(overlay_page)
        writer.add_page(page)

    with open(output_pdf, "wb") as f:
        writer.write(f)
    print(f"Embedded into {output_pdf} ({'all' if all_pages else '1'} page(s)).")


def create_new_pdf(text, output_pdf, font_size=8):
    """Generate a blank-looking PDF that only carries the invisible text."""
    reader = PdfReader(make_invisible_overlay(text, A4, font_size))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    with open(output_pdf, "wb") as f:
        writer.write(f)
    print(f"Created {output_pdf} (looks blank, carries invisible text).")


def extract_text(pdf_path):
    """Print embedded text -- the same thing an AI extracting the PDF sees."""
    reader = PdfReader(pdf_path)
    for i, page in enumerate(reader.pages):
        print(f"--- page {i + 1} ---")
        print(page.extract_text())


def main():
    p = argparse.ArgumentParser(
        description="Embed text into a PDF that is invisible to humans but readable by AI."
    )
    p.add_argument("input", nargs="?", help="Input PDF (omit to generate a new one)")
    p.add_argument("-t", "--text", help="Text to embed")
    p.add_argument("-f", "--file", help="Read text to embed from this file")
    p.add_argument("-o", "--output", default="output.pdf", help="Output PDF (default: output.pdf)")
    p.add_argument("-s", "--size", type=float, default=8, help="Font size (default: 8)")
    p.add_argument("--all-pages", action="store_true", help="Embed on every page (default: first page only)")
    p.add_argument("--extract", metavar="PDF", help="Extract and print embedded text from a PDF")
    args = p.parse_args()

    if args.extract:
        extract_text(args.extract)
        return

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        p.error("provide text with -t/--text or -f/--file")

    if args.input:
        embed_into_pdf(args.input, text, args.output, args.size, args.all_pages)
    else:
        create_new_pdf(text, args.output, args.size)


if __name__ == "__main__":
    main()
