# pdf-hidden-text

Embed text into a PDF that is **invisible to humans but readable by AI** (and any
text extractor like `pdftotext`, `pypdf`, or `pdfminer`).

It uses PDF **text rendering mode 3 (invisible)** — the exact mechanism behind
the text layer of an OCR'd, searchable PDF. The text never shows up on screen or
in print, but it is part of the document's text stream, so when a PDF is fed to
an LLM (which reads the extracted text), the hidden message comes through.

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
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
```

## Language support

Works for virtually all scripts and emoji (Latin, Japanese, Korean, Chinese,
Cyrillic, Thai, Devanagari, …). Because the text is invisible, font glyph
coverage is irrelevant — only the Unicode mapping used during extraction
matters, and that is embedded automatically.

**Caveat:** right-to-left scripts (Arabic, Hebrew) come out with character order
reversed on extraction. Write your message in a left-to-right language if this
matters.

## How it works

1. A transparent overlay page is generated with [`reportlab`](https://pypi.org/project/reportlab/),
   drawing the text with `setTextRenderMode(3)` so nothing is painted.
2. The overlay is merged onto your PDF (or saved standalone) with
   [`pypdf`](https://pypi.org/project/pypdf/).
3. The bytes still contain the text + a ToUnicode map, so extraction recovers it.

## Limitations

- Only survives if the consumer reads the **text layer**. Screenshotting, OCR, or
  retyping strips it. Scanned/image-only PDFs have no text layer to begin with.
- The text can be revealed by select-all, "extract text" tools, or this script's
  `--extract` mode — it is *hidden*, not *encrypted*.

## Responsible use

This technique is dual-use. Legitimate uses include watermarking, accessibility
text, AI-robustness testing, and provenance tagging. It can also be used for
**prompt injection** against AI systems (e.g. hiding instructions in a document
so an AI summarizer/grader behaves differently). Do not use it to deceive or
manipulate third-party AI systems you do not own. If you embed instructions
intended to detect AI use (e.g. in coursework), disclose that policy up front and
treat any signal as a prompt for a conversation, not as conclusive proof.

## License

MIT — see [LICENSE](LICENSE).
