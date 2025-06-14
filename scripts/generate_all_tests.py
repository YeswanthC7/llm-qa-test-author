#!/usr/bin/env python3
"""
Generate PyTest + sync-Playwright tests from Markdown user stories
via Hugging Face Inference API (Mistral-7B).  Retries until code
is syntactically valid *and* free of placeholders/async/prose.
"""

from __future__ import annotations
import os, re, ast, textwrap
from pathlib import Path
from typing import Optional
from huggingface_hub import InferenceClient

# ── Config ───────────────────────────────────────────────────────────
HF_TOKEN   = os.getenv("HF_TOKEN")          # export HF_TOKEN="hf_…"
MODEL_ID   = "mistralai/Mistral-7B-Instruct-v0.2"
STORIES_DIR = Path("stories")
OUTPUT_DIR  = Path("tests")
OUTPUT_DIR.mkdir(exist_ok=True)
MAX_RETRIES = 3

PROMPT = (
    "You are a senior QA engineer.\n"
    "Return ONLY valid **sync-Playwright** Python for ONE PyTest file.\n"
    "Rules:\n"
    "• Base URLs on https://www.ebay.com/ (never placeholder domains).\n"
    "• Use stable text locators, avoid dummy IDs.\n"
    "• NO comments, markdown, async/await, or plain-English paragraphs.\n\n"
    "USER STORY:\n{story}\n"
)

# ── Regexes for validation ───────────────────────────────────────────
ASYNC_RX       = re.compile(r"\bawait\b|\basync\b", re.I)
PLACEHOLDER_RX = re.compile(
    r"your-website\.com|example\.com|todo_selector|#buy-it-now-button|#placeholder|TODO",
    re.I,
)
PROSE_LINE_RX  = re.compile(r"[A-Za-z]{30,}")  # 30+ letters ⇒ likely prose

# ── Helper functions ────────────────────────────────────────────────
def clean(raw: str) -> str:
    raw = re.sub(r"```.*?```", "", raw, flags=re.S)
    first_code = re.search(r"(?:^|\n)(from|import|def)\s+\w+", raw)
    raw = raw[first_code.start():] if first_code else raw
    lines = []
    for ln in raw.splitlines():
        if ASYNC_RX.match(ln.lstrip()):
            ln = "    " + ln.lstrip()  # indent stray async to keep syntax
        lines.append(ln.rstrip())
    return "\n".join(lines).rstrip()

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
    bad = (
        PLACEHOLDER_RX.search(code)
        or ASYNC_RX.search(code)
        or any(
            PROSE_LINE_RX.search(ln) and not ln.lstrip().startswith(("import", "from", "def"))
            for ln in code.splitlines()
        )
    )
    return not bad

def auto_skip(code: str, reason: str) -> str:
    commented = "\n".join("# " + ln for ln in code.splitlines())
    return (
        'import pytest\n'
        f'pytest.skip("{reason}", allow_module_level=True)\n\n'
        f'{commented}\n'
    )

# ── HF client ───────────────────────────────────────────────────────
if not HF_TOKEN:
    raise RuntimeError("Set HF_TOKEN →  export HF_TOKEN='hf_...'")
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
    # After retries still bad → auto-skip
    return auto_skip(code, "Placeholders or async remained after retries")

# ── Main loop ───────────────────────────────────────────────────────
def main() -> None:
    for md in STORIES_DIR.glob("*.md"):
        slug  = md.stem
        story = md.read_text()
        code  = generate_valid(story, slug)
        (OUTPUT_DIR / f"test_{slug}.py").write_text(code)
        print(f"✔ Wrote test_{slug}.py")

if __name__ == "__main__":
    main()
