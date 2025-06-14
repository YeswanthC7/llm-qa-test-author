#!/usr/bin/env python3
"""
Generate PyTest + Playwright E2E tests from Markdown stories
via Hugging Face Inference API (Mistral-7B-Instruct, free tier).
"""

import os, glob, re, ast, textwrap
from huggingface_hub import InferenceClient

# ───────────────────────── Config ──────────────────────────
HF_TOKEN   = os.getenv("HF_TOKEN")               # export HF_TOKEN="hf_…"
MODEL_ID   = "mistralai/Mistral-7B-Instruct-v0.2"
STORIES_DIR = "stories"
OUTPUT_DIR  = "tests"
os.makedirs(OUTPUT_DIR, exist_ok=True)

PROMPT = (
    "You are a senior QA engineer.\n"
    "Return ONLY valid **sync Playwright** Python code for one PyTest file.\n"
    "Rules:\n"
    "• Use sync API (`from playwright.sync_api import sync_playwright, expect`).\n"
    "• Either start with `def test_…(page):` OR give raw statements—no markdown.\n"
    "• Absolutely NO async/await, comments, or natural-language sentences.\n\n"
    "USER STORY:\n{story}\n"
)

# ───────────────────────── Helpers ─────────────────────────
ASYNC_RX = re.compile(r"^\s*(await|async\s+with|async\s+for)\b", re.I)

def clean(code: str) -> str:
    """Drop markdown fences & indent stray async lines."""
    code = re.sub(r"```.*?```", "", code, flags=re.S)
    m = re.search(r"(?:^|\n)(from|import|def)\s+\w+", code)
    code = code[m.start():] if m else code
    fixed = []
    for ln in code.splitlines():
        if ASYNC_RX.match(ln):
            ln = "    " + ln.lstrip()
        fixed.append(ln.rstrip())
    return "\n".join(fixed).rstrip()

def wrap_if_needed(code: str, slug: str) -> str:
    """
    • If `def test_` already present → return unchanged.
    • Else → wrap the snippet under def test_<slug>(page): …
      ↳ If snippet is empty or only blanks, inject a `pass`.
    """
    if "def test_" in code:
        return code

    raw_lines = code.splitlines()
    # indent non-blank lines; keep blanks for spacing
    indented = [(("    " + ln) if ln.strip() else "") for ln in raw_lines]
    # ensure at least one real line of code
    if not any(ln.strip() for ln in indented):
        indented = ["    pass"]

    header = (
        "from playwright.sync_api import sync_playwright, expect\n\n"
        f"def test_{slug}(page):\n"
    )
    return header + "\n".join(indented)


def safe_write(path: str, code: str):
    """Write only if code compiles under ast.parse."""
    try:
        ast.parse(textwrap.dedent(code))
    except SyntaxError as err:
        print(f"✖ Skipped {os.path.basename(path)} – syntax error ({err.msg})")
        return
    with open(path, "w") as f:
        f.write(code)
    print(f"✔ Wrote {os.path.basename(path)}")

# ───────────────────────── HF client ───────────────────────
if not HF_TOKEN:
    raise RuntimeError("Set HF_TOKEN first ➜  export HF_TOKEN='hf_...'")

client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

def generate_test_code(story_text: str, slug: str) -> str:
    messages = [
        {"role": "system", "content": "You are a senior QA engineer."},
        {"role": "user",   "content": PROMPT.format(story=story_text)},
    ]
    resp = client.chat_completion(messages=messages,
                                  max_tokens=350,
                                  temperature=0.2)
    raw  = resp.choices[0].message.content
    code = clean(raw)
    return wrap_if_needed(code, slug)

# ───────────────────────── Main loop ───────────────────────
def main() -> None:
    for md_path in glob.glob(f"{STORIES_DIR}/*.md"):
        slug = os.path.splitext(os.path.basename(md_path))[0]
        with open(md_path) as f:
            story = f.read()
        code = generate_test_code(story, slug)
        out_file = os.path.join(OUTPUT_DIR, f"test_{slug}.py")
        safe_write(out_file, code)

if __name__ == "__main__":
    main()
