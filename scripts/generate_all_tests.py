#!/usr/bin/env python3
"""
Generate PyTest + sync-Playwright tests from Markdown user stories
via Hugging Face (Mistral-7B Instruct).  Retries until code is
AST-parseable *and* free of placeholders, async/await, prose and
runtime-red-flag selectors.
"""

from __future__ import annotations
import os, re, ast, textwrap
from pathlib import Path
from huggingface_hub import InferenceClient

# ── Config ──────────────────────────────────────────────────────────────
HF_TOKEN    = os.getenv("HF_TOKEN")            # set in GH secrets
MODEL_ID    = "mistralai/Mistral-7B-Instruct-v0.2"
STORIES_DIR = Path("stories")
OUTPUT_DIR  = Path("tests"); OUTPUT_DIR.mkdir(exist_ok=True)
MAX_RETRIES = 3

PROMPT = (
    "You are a senior QA engineer.\n"
    "Return ONLY valid **sync-Playwright** Python for ONE PyTest file.\n"
    "Rules:\n"
    "• Base URLs on https://www.ebay.com/ (never placeholder domains).\n"
    "• Use stable text locators, avoid dummy CSS paths.\n"
    "• No markdown, comments, async/await, or plain English paragraphs.\n"
    "• Must not contain inner_text(), #buy-it-now-button, paypal selectors, etc.\n\n"
    "USER STORY:\n{story}\n"
)

# ── Regex validators ────────────────────────────────────────────────────
ASYNC_RX       = re.compile(r"\bawait\b|\basync\b", re.I)

PLACEHOLDER_RX = re.compile(
    r"your-website\.com|example\.com|todo_selector|#buy-it-now-button|#placeholder|TODO",
    re.I,
)

# lines starting with >30 letters that aren't code-ish
PROSE_LINE_RX  = re.compile(r"[A-Za-z]{30,}")

# Runtime killers we saw: async fixtures, inner_text(), paypal button, stray await
BAD_RUNTIME_RX = re.compile(
    r"""
    \basync\s+def\b        |   # async fixtures
    inner_text\s*\(        |   # method only in async API
    \#paypal-button        |   # placeholder selector
    \bawait\b                  # stray await missed earlier
    """,
    re.I | re.X,
)

# ── Helpers ─────────────────────────────────────────────────────────────
def clean(raw: str) -> str:
    raw = re.sub(r"```.*?```", "", raw, flags=re.S)
    m = re.search(r"(?:^|\n)(from|import|def)\s+\w+", raw)
    raw = raw[m.start():] if m else raw
    fixed = []
    for ln in raw.splitlines():
        if ASYNC_RX.match(ln.lstrip()):
            ln = "    " + ln.lstrip()           # indent stray await
        fixed.append(ln.rstrip())
    return "\n".join(fixed).rstrip()

def wrap_if_needed(code: str, slug: str) -> str:
    if "def test_" in code:
        return code
    body = ["    " + ln if ln.strip() else "" for ln in code.splitlines()]
    if not any(ln.strip() for ln in body):
        body = ["    pass"]
    header = (
        "from playwright.sync_api import sync_playwright, expect\n\n"
        f"def test_{slug}(page):\n"
    )
    return header + "\n".join(body)

def validate(code: str) -> bool:
    try:
        ast.parse(textwrap.dedent(code))
    except SyntaxError:
        return False
    prose = any(
        PROSE_LINE_RX.search(ln) and not ln.lstrip().startswith(("import", "from", "def"))
        for ln in code.splitlines()
    )
    bad = (
        PLACEHOLDER_RX.search(code)
        or ASYNC_RX.search(code)
        or BAD_RUNTIME_RX.search(code)
        or prose
    )
    return not bad

def auto_skip(code: str, reason: str) -> str:
    return f'import pytest\npytest.skip("{reason}", allow_module_level=True)\n\n' + code

# ── Hugging Face client ────────────────────────────────────────────────
if not HF_TOKEN:
    raise RuntimeError("Set HF_TOKEN  →  export HF_TOKEN='hf_...'")

client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

def generate_once(story: str, slug: str) -> str:
    raw = client.chat_completion(
        messages=[
            {"role": "system", "content": "You are a senior QA engineer."},
            {"role": "user",   "content": PROMPT.format(story=story)},
        ],
        max_tokens=350,
        temperature=0.2,
    ).choices[0].message.content
    return wrap_if_needed(clean(raw), slug)

def generate_valid(story: str, slug: str) -> str:
    for attempt in range(1, MAX_RETRIES + 1):
        code = generate_once(story, slug)
        if validate(code):
            if attempt > 1:
                print(f"  ↻  {slug}: fixed on retry {attempt}")
            return code
        print(f"  ✖  attempt {attempt} invalid ({slug})")
    return auto_skip(code, "still contained placeholders/async/prose after retries")

# ── Main ───────────────────────────────────────────────────────────────
def main() -> None:
    for md in STORIES_DIR.glob("*.md"):
        slug  = md.stem
        code  = generate_valid(md.read_text(), slug)
        (OUTPUT_DIR / f"test_{slug}.py").write_text(code)
        print(f"✔ Wrote test_{slug}.py")

if __name__ == "__main__":
    main()
