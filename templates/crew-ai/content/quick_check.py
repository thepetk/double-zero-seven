# quick_check.py
import os
from openai import OpenAI

os.environ["OPENAI_BASE_URL"] = os.getenv("LLM_BASE_URL", "")
os.environ["OPENAI_API_KEY"] = os.getenv("LLM_API_KEY", "")

client = OpenAI()
resp = client.chat.completions.create(
    model="llama-31-8b-version1",
    messages=[{"role": "user", "content": "Say hello"}],
)
print(resp.choices[0].message.content)
