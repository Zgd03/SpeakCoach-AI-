import json
import base64
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.models.db_models import Session, Scenario, Message, Correction
from app.services.llm_service import call_deepseek
from app.services.tts_service import text_to_speech

logger = logging.getLogger(__name__)
router = APIRouter()

# Pre-defined opening lines per scenario keyword
_OPENING_LINES = {
    "interview": "Hello! Thank you for coming in today. Could you start by telling me a little about yourself and your background?",
    "restaurant": "Welcome to our restaurant! Here's a menu for you. Would you like to start with some drinks, or shall I tell you about today's specials?",
    "meeting": "Good morning, everyone. Thanks for joining today's meeting. Let's start by going over the agenda. Who would like to begin with their project update?",
}


def _get_opening_line(system_prompt: str) -> str:
    """Look up a pre-defined opening line based on scenario keywords."""
    s = system_prompt.lower()
    if "interview" in s:
        return _OPENING_LINES["interview"]
    if "restaurant" in s:
        return _OPENING_LINES["restaurant"]
    if "meeting" in s:
        return _OPENING_LINES["meeting"]
    return _OPENING_LINES["interview"]


@router.websocket("/ws/{session_id}")
async def conversation_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()

    # We cannot use Depends(get_db) directly with WebSocket, so create a session manually
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        db_session = db.query(Session).filter(Session.id == session_id).first()
        if not db_session:
            await websocket.send_json({"type": "error", "message": "Session not found"})
            await websocket.close()
            return

        scenario = db.query(Scenario).filter(Scenario.id == db_session.scenario_id).first()
        system_prompt = scenario.system_prompt if scenario else "You are an English speaking coach."

        conversation_history = []

        # Look up pre-defined opening line for the scenario
        opening_text = _get_opening_line(system_prompt)
        if opening_text:
            # Save assistant message
            assistant_msg = Message(
                session_id=session_id,
                role="assistant",
                content=opening_text,
            )
            db.add(assistant_msg)
            db.commit()
            db.refresh(assistant_msg)

            conversation_history.append({"role": "assistant", "content": opening_text})

            # Synthesize and send opening line
            audio_b64 = ""
            if opening_text:
                audio_bytes = await text_to_speech(opening_text)
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

            await websocket.send_json({
                "type": "ai_reply",
                "audio": audio_b64,
                "text": opening_text,
            })

        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "user_message" and msg.get("text"):
                user_text = msg["text"].strip()
                if not user_text:
                    continue

                # Save user message to DB
                user_msg = Message(
                    session_id=session_id,
                    role="user",
                    content=user_text,
                )
                db.add(user_msg)
                db.commit()
                db.refresh(user_msg)

                # Build conversation history for LLM
                conversation_history.append({"role": "user", "content": user_text})

                # Call DeepSeek for reply + corrections + score
                llm_result = await call_deepseek(system_prompt, conversation_history)

                reply_text = llm_result.get("reply", "")
                corrections_data = llm_result.get("corrections", [])
                score_data = llm_result.get("score", {})

                # Save assistant message
                assistant_msg = Message(
                    session_id=session_id,
                    role="assistant",
                    content=reply_text,
                    grammar_score=score_data.get("grammar"),
                    fluency_score=score_data.get("fluency"),
                    vocabulary_score=score_data.get("vocabulary"),
                )
                db.add(assistant_msg)
                db.commit()
                db.refresh(assistant_msg)

                # Save corrections
                for c in corrections_data:
                    correction = Correction(
                        message_id=user_msg.id,
                        original_text=c.get("original", ""),
                        corrected_text=c.get("corrected", ""),
                        error_type=c.get("error_type", "grammar"),
                        explanation=c.get("explanation", ""),
                        severity=c.get("severity", "minor"),
                    )
                    db.add(correction)
                db.commit()

                conversation_history.append({"role": "assistant", "content": reply_text})

                # Synthesize speech (only if there's actual content)
                audio_b64 = ""
                if reply_text:
                    audio_bytes = await text_to_speech(reply_text)
                    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

                # Send response back
                await websocket.send_json({
                    "type": "ai_reply",
                    "audio": audio_b64,
                    "text": reply_text,
                })

                if corrections_data:
                    await websocket.send_json({
                        "type": "correction",
                        "data": corrections_data,
                    })

                if score_data:
                    await websocket.send_json({
                        "type": "score_update",
                        "data": score_data,
                    })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        db.close()
