#!/usr/bin/env python3
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

prompt = (
    "You are a QA engineer. "
    "Write a PyTest + Playwright test for this user story: "
    "\"As a visitor, I can log in with valid credentials.\""
)

resp = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)

print(resp.choices[0].message.content)
