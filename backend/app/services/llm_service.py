import asyncio
import json
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_TEMPLATE = """You are an English speaking coach. The user is practicing: {scenario}

Reply naturally as the conversation partner. Also analyze the user's latest message and provide corrections.

Return JSON only (no markdown, no code fences):
{{
  "reply": "<your natural conversation reply in English>",
  "corrections": [
    {{
      "original": "<incorrect phrase from user>",
      "corrected": "<corrected version>",
      "error_type": "grammar|pronunciation|expression|word_choice",
      "explanation": "<why it's wrong, in Chinese>",
      "severity": "minor|major"
    }}
  ],
  "score": {{
    "grammar": <0-100>,
    "fluency": <0-100>,
    "vocabulary": <0-100>
  }}
}}

Rules:
- Keep corrections concise, max 2 per turn.
- Use Chinese for explanations when helpful.
- If no correction needed, return empty corrections list.
- Always include all three score dimensions.
"""


def _build_messages(system_prompt: str, conversation_history: list[dict]) -> list[dict]:
    messages = [{"role": "system", "content": SYSTEM_TEMPLATE.format(scenario=system_prompt)}]

    # Only include last 10 messages for context window
    recent = conversation_history[-10:]
    for msg in recent:
        messages.append({"role": msg["role"], "content": msg["content"]})

    return messages


async def call_deepseek(system_prompt: str, conversation_history: list[dict]) -> dict:
    if not settings.deepseek_api_key:
        logger.warning("DEEPSEEK_API_KEY not set, using fallback response")
        return _fallback_response(conversation_history[-1]["content"] if conversation_history else "")

    try:
        messages = _build_messages(system_prompt, conversation_history)

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                settings.api_chat_url,
                headers={
                    "Authorization": f"Bearer {settings.deepseek_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.deepseek_model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1024,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]

        # Parse JSON from response
        # Sometimes the model wraps in markdown fences
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
            content = content.rsplit("```", 1)[0]
        content = content.strip()

        result = json.loads(content)
        return result

    except (Exception, asyncio.CancelledError) as e:
        logger.error(f"DeepSeek API call failed: {e}")
        return _fallback_response(
            conversation_history[-1]["content"] if conversation_history else ""
        )


def _fallback_response(user_text: str) -> dict:
    """Fallback when API is unavailable."""
    return {
        "reply": f"That's interesting! Could you tell me more about what you mean by '{user_text[:50]}'?",
        "corrections": [],
        "score": {"grammar": 80, "fluency": 75, "vocabulary": 78},
    }
