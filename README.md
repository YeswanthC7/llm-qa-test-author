# LLM-Powered QA Test Author

Convert plain-English user stories into runnable PyTest + Playwright E2E tests using OpenAI.

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
