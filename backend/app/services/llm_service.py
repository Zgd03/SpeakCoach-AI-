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
                f"{settings.deepseek_base_url}/chat/completions",
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

    except Exception as e:
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


# ---- Opening line generation ----

OPENING_TEMPLATE = """You are an English speaking coach for the scenario: {scenario}

Your task is to start the conversation with a natural opening line in English.
Speak as the conversation partner (e.g. waiter, interviewer, colleague) to begin the role-play.

Return ONLY the opening line — no JSON, no extra text, no markdown.
The line should be natural, friendly, and appropriate for the scenario.
"""


async def generate_opening(system_prompt: str) -> str:
    """Generate an opening line for the given scenario."""
    if not settings.deepseek_api_key:
        logger.warning("DEEPSEEK_API_KEY not set, using fallback opening")
        return _fallback_opening(system_prompt)

    try:
        messages = [
            {"role": "system", "content": OPENING_TEMPLATE.format(scenario=system_prompt)},
        ]

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{settings.deepseek_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.deepseek_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.deepseek_model,
                    "messages": messages,
                    "temperature": 0.8,
                    "max_tokens": 128,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return content.strip().strip('"').strip("'")

    except Exception as e:
        logger.error(f"Opening generation failed: {e}")
        return _fallback_opening(system_prompt)


def _fallback_opening(scenario_prompt: str) -> str:
    """Fallback opening lines based on scenario keywords."""
    s = scenario_prompt.lower()
    if "interview" in s or "面试" in s:
        return "Hello! Thank you for coming in today. Could you start by telling me a little about yourself and your background?"
    if "restaurant" in s or "餐厅" in s or "点餐" in s:
        return "Welcome to our restaurant! Here's a menu for you. Would you like to start with some drinks, or shall I tell you about today's specials?"
    if "meeting" in s or "会议" in s or "商务" in s:
        return "Good morning, everyone. Thanks for joining today's meeting. Let's start by going over the agenda. Who would like to begin with their project update?"
    return "Hello! Welcome to today's practice session. How are you doing today?"
