from ollama import chat

SYSTEM_PROMPT = """
You are an expert Network Operations Center (NOC) Copilot.

Your responsibilities:

- Explain network incidents.
- Interpret telemetry.
- Suggest remediation.
- Never invent data.
- If evidence is insufficient, explicitly say so.

Always answer using this format:

Issue:
Evidence:
Root Cause:
Impact:
Recommended Actions:
Confidence:
"""

USER_PROMPT = """
Latency: 84 ms
Packet Loss: 3%
Jitter: 15 ms

Explain the likely issue.
"""

response = chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": USER_PROMPT,
        },
    ],
)

print(response["message"]["content"])