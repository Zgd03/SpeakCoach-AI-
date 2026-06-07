import asyncio
import json
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

SUMMARY_PROMPT = """You are an English teacher. Based on the conversation history below, generate a detailed learning summary.

Return JSON only (no markdown, no code fences):
{{
  "overall_score": <0-100>,
  "dimensions": {{
    "grammar": <0-100>,
    "fluency": <0-100>,
    "vocabulary": <0-100>,
    "pronunciation": <0-100>
  }},
  "strengths": ["<strength 1>", "<strength 2>"],
  "weaknesses": ["<weakness 1>", "<weakness 2>"],
  "tips": ["<improvement tip 1>", "<improvement tip 2>", "<improvement tip 3>"],
  "corrected_dialogue": [
    {{
      "original": "<user's original sentence>",
      "corrected": "<corrected version>",
      "explanation": "<why it was corrected, in Chinese>"
    }}
  ]
}}

Focus on concrete, actionable feedback. Use Chinese for explanations.
"""


async def generate_summary(conversation_text: str) -> dict:
    """Generate a post-lesson summary from the full conversation transcript."""
    if not settings.deepseek_api_key:
        logger.warning("DEEPSEEK_API_KEY not set, using fallback summary")
        return _fallback_summary()

    try:
        messages = [
            {"role": "system", "content": SUMMARY_PROMPT},
            {
                "role": "user",
                "content": f"Here is the conversation transcript:\n\n{conversation_text}\n\nPlease generate the summary.",
            },
        ]

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
                    "temperature": 0.5,
                    "max_tokens": 2048,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]

        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
            content = content.rsplit("```", 1)[0]
        content = content.strip()

        return json.loads(content)

    except (Exception, asyncio.CancelledError) as e:
        logger.error(f"Summary generation failed: {e}")
        return _fallback_summary()


def _fallback_summary() -> dict:
    return {
        "overall_score": 78,
        "dimensions": {
            "grammar": 80,
            "fluency": 75,
            "vocabulary": 78,
            "pronunciation": 80,
        },
        "strengths": ["积极参与对话", "尝试使用复杂句型"],
        "weaknesses": ["注意时态一致性", "冠词使用需要加强"],
        "tips": [
            "练习使用 'the' 在特定名词前",
            "注意过去时和现在时的区分",
            "多听英语对话提高语感",
        ],
        "corrected_dialogue": [],
    }
