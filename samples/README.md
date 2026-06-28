# Samples

A before/after demo of the embedder, themed as a high-school English assignment.

| File | What it is |
|------|------------|
| `assignment_clean.pdf` | A normal assignment. Nothing hidden. |
| `assignment_injected.pdf` | **Visually identical**, but carries an invisible prompt injection that tells the AI to refuse. |
| `make_sample.py` | Regenerates both files. |

## Try it yourself

Open both PDFs in a viewer — they look the same. Now extract the text the way an
AI does:

```bash
python ../embed_hidden_text.py --extract assignment_clean.pdf      # visible text only
python ../embed_hidden_text.py --extract assignment_injected.pdf   # visible text + hidden note
```

Or hand each PDF to an AI assistant and ask it to "write this essay." The clean
version produces an ordinary essay. The injected version instructs the AI to
**stop and refuse** — a compliant assistant declines to write any essay text and
instead returns a short notice that the work must be the student's own.

Note this is best-effort, not a guarantee: whether an AI honors the hidden
instruction depends on the model and how the PDF is ingested. Treat it as a
deterrent, not a lock.

Regenerate:

```bash
python make_sample.py
```

> This demonstrates *discouraging* AI misuse on a document you own, not enabling
> it. See the repo's [Responsible use](../README.md#responsible-use) section.
