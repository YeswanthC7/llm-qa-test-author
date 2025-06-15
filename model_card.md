
### 2.  Model card

Add **`model_card.md`**

```markdown
# Prompt design & safety

**System prompt**  
> You are a senior QA engineer. Return ONLY valid sync-Playwright code …

**Guard rails**

* Retries until AST-parseable.
* Rejects placeholders, async, prose; final auto-skip if still present.
* Captcha / login-flows are auto-skipped without credentials.

**Limitations**

* Assumes public selectors on ebay.com.  
* No captcha solving.  
* Free-tier HF quota (~30 k tokens/month).

Feel free to adapt the prompt or selector strategy for your own app.
