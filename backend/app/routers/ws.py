import json
import base64
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Session, Scenario, Message, Correction
from app.services.llm_service import call_deepseek
from app.services.tts_service import text_to_speech

logger = logging.getLogger(__name__)
router = APIRouter()


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

        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            # ── Start event: AI speaks first (opening line) ──
            if msg.get("type") == "start":
                opening_prompt = (
                    system_prompt
                    + "\n\nThe conversation is just starting. "
                    "Greet the user warmly and ask an opening question "
                    "to begin the conversation. "
                    "Your reply should be the first thing the user hears."
                )
                llm_result = await call_deepseek(opening_prompt, conversation_history)

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

                conversation_history.append({"role": "assistant", "content": reply_text})

                # Synthesize speech
                audio_bytes = await text_to_speech(reply_text)
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

                await websocket.send_json({
                    "type": "ai_reply",
                    "audio": audio_b64,
                    "text": reply_text,
                })
                continue

            # ── User message event ──
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

                # Synthesize speech
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
