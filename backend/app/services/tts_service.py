import logging

import edge_tts

logger = logging.getLogger(__name__)

# Default voice: en-US-JennyNeural (natural female American English)
DEFAULT_VOICE = "en-US-JennyNeural"


async def text_to_speech(text: str, voice: str = DEFAULT_VOICE) -> bytes:
    """Convert text to speech using edge-tts. Returns MP3 audio bytes."""
    try:
        communicate = edge_tts.Communicate(text=text, voice=voice)
        audio_chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])

        return b"".join(audio_chunks)
    except Exception as e:
        logger.error(f"TTS failed: {e}")
        # Return empty bytes on failure
        return b""
