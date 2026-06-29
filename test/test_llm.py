# from ollama import chat

# SYSTEM_PROMPT = """
# You are an expert Network Operations Center (NOC) Copilot.

# Your responsibilities:

# - Explain network incidents.
# - Interpret telemetry.
# - Suggest remediation.
# - Never invent data.
# - If evidence is insufficient, explicitly say so.

# Always answer using this format:

# Issue:
# Evidence:
# Root Cause:
# Impact:
# Recommended Actions:
# Confidence:
# """

# USER_PROMPT = """
# Latency: 84 ms
# Packet Loss: 3%
# Jitter: 15 ms

# Explain the likely issue.
# """

# response = chat(
#     model="qwen3:8b",
#     messages=[
#         {
#             "role": "system",
#             "content": SYSTEM_PROMPT,
#         },
#         {
#             "role": "user",
#             "content": USER_PROMPT,
#         },
#     ],
# )

# print(response["message"]["content"])

"""
Manual smoke test (not a pytest test).

This file is kept for developer convenience but should not fail CI/pytest when
Ollama isn't running. Run it manually:

  python test/test_llm.py
"""

import json
import requests

OLLAMA_URL = "http://localhost:11434/v1/chat/completions"


def main():
    payload = {
        "model": "local-model",
        "messages": [
            {"role": "system", "content": "Return strict JSON only."},
            {"role": "user", "content": "tell me any past network incidents."},
        ],
        "temperature": 0.1,
        "max_tokens": 200,
    }

    r = requests.post(OLLAMA_URL, json=payload, timeout=180)
    r.raise_for_status()
    print(r.json()["choices"][0]["message"]["content"])


if __name__ == "__main__":
    main()