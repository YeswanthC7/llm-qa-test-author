# LLM-QA-Test-Author 🚀

[![CI](https://github.com/YeswanthC7/llm-qa-test-author/actions/workflows/qa.yml/badge.svg)](https://github.com/YeswanthC7/llm-qa-test-author/actions/workflows/qa.yml)

Turn plain-English user stories ➜ PyTest + Playwright E2E tests, on every push.

## 📁 Repo Structure

llm-qa-test-author/
├── stories/ # Markdown user stories (.md)
├── tests/ # Generated test files (.py)
├── scripts/
│ └── generate_all_tests.py
├── requirements.txt
└── README.md


## 🚀 Setup (using Hugging Face Inference API)

1. **Clone & enter directory**  
   ```bash
   git clone <your-repo-url>
   cd llm-qa-test-author

```

2. **Create a virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install requirements**
```bash
pip install -r requirements.txt
```

4. **Run tests**
```bash
pytest
```

5. **Installation & Run locally**
```bash
git clone https://github.com/YeswanthC7/llm-qa-test-author
cd llm-qa-test-author
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt ; playwright install
export HF_TOKEN="hf_…"  # your token
python scripts/generate_all_tests.py && pytest -q

##➡️ See [model_card.md](model_card.md) for prompt design, guard rails, and limitations.

