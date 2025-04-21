# Troubleshooting

Common issues when running **PDF‑OCR‑Pipeline** and how to fix them.

## “pdftoppm: write failed broken pipe” or no text extracted

Poppler version 25 changed the behaviour of `pdftoppm` so that the command no
longer streams PPM data to *stdout* when the output prefix is "-".  Newer
versions silently create `-.ppm` files on disk which results in *empty* input
for Tesseract.

**Fix** – Upgrade to the latest version (>25) *or* install the backported
package for your OS.  The pipeline includes an automatic runtime detector and
will fall back to a safe temp‑file path, but very old releases (<0.4.0) need
the manual workaround.

## “Error opening data file … eng.traineddata”

Tesseract cannot find the requested language pack.

```bash
sudo apt-get install tesseract-ocr-eng     # Debian / Ubuntu
brew install tesseract-lang                # Homebrew (installs all langs)
```

Then re‑run the command with `--lang <code>` or set `PDF_OCR_LANG`.

## OPENAI_API_KEY not set / placeholder key

An actual API key is required for the summarisation step.  Get one from
https://platform.openai.com/account/api-keys and export it:

```bash
export OPENAI_API_KEY="sk-…"
```

Placeholders like `YOUR_API_KEY` are detected at startup and produce a helpful
error.

## “Rate limit exceeded” or timeouts

Large PDFs can exceed the token limit of GPT‑4o.  Consider:

* Increasing the segmentation granularity so each chunk is smaller.
* Switching to a model with larger context (e.g. `gpt-4o-2024-05-13-long`).
* Using the pipeline offline and re‑running only failed chunks.

If you repeatedly hit *rate limits* enable exponential back‑off or request a
higher quota from OpenAI.
