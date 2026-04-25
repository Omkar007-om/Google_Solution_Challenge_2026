"""
NEXUS 2.0 — Amazon Bedrock LLM Client
Thin wrapper around boto3 for Claude 3.5 Sonnet calls via Bedrock.
"""

import os
import json
import boto3
from dotenv import load_dotenv

load_dotenv()

# ── Configuration ──
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
MAX_TOKENS = int(os.getenv("BEDROCK_MAX_TOKENS", "4096"))

# Lazy-initialised client (created on first call)
_client = None


def _get_client():
    """Lazy-init the Bedrock Runtime client."""
    global _client
    if _client is None:
        _client = boto3.client(
            "bedrock-runtime",
            region_name=AWS_REGION,
        )
    return _client


def invoke_claude(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.3,
    max_tokens: int | None = None,
) -> str:
    """
    Send a single-turn message to Claude via Bedrock and return the text response.

    Args:
        system_prompt: The system-level instruction.
        user_message: The user-turn content.
        temperature: Sampling temperature (lower = more deterministic).
        max_tokens: Max response tokens (defaults to env config).

    Returns:
        The assistant's text response.
    """
    client = _get_client()

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens or MAX_TOKENS,
        "temperature": temperature,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_message},
        ],
    }

    response = client.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body),
    )

    result = json.loads(response["body"].read())

    # Claude returns content as a list of blocks
    text_blocks = [
        block["text"]
        for block in result.get("content", [])
        if block.get("type") == "text"
    ]
    return "\n".join(text_blocks)
