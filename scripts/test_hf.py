# scripts/test_hf.py
import os
from huggingface_hub import InferenceClient

client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    token=os.getenv("HF_TOKEN"),
)

messages = [
    {"role": "system", "content": "You are a QA engineer."},
    {
        "role": "user",
        "content": (
            "Generate a PyTest + Playwright test for this user story:\n"
            '"As a visitor, I can log in with valid credentials."'
        ),
    },
]

resp = client.chat_completion(
    messages=messages,
    max_tokens=350,
    temperature=0.2
)

# The text is inside choices[0].message.content
generated_text = resp.choices[0].message.content
print(generated_text)
