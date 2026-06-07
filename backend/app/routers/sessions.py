import asyncio
import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.db_models import Session, Scenario, Message, Correction
from app.schemas.schemas import (
    SessionCreate,
    SessionOut,
    SessionList,
    SessionListItem,
    SummaryOut,
    DimensionScores,
    CorrectedDialogue,
)
from app.services.summary_service import generate_summary, _fallback_summary

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/sessions", response_model=SessionOut, status_code=201)
def create_session(body: SessionCreate, db: Session = Depends(get_db)):
    scenario = db.query(Scenario).filter(Scenario.id == body.scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    session = Session(scenario_id=body.scenario_id, start_time=datetime.utcnow())
    db.add(session)
    db.commit()
    db.refresh(session)

    return SessionOut(
        id=session.id,
        scenario_id=session.scenario_id,
        scenario_name=scenario.name,
        start_time=session.start_time,
        end_time=session.end_time,
        overall_score=session.overall_score,
        summary=session.summary,
        created_at=session.created_at,
        messages=[],
    )


@router.get("/sessions", response_model=SessionList)
def list_sessions(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    total = db.query(Session).count()
    sessions = (
        db.query(Session)
        .order_by(Session.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    items = []
    for s in sessions:
        scenario = db.query(Scenario).filter(Scenario.id == s.scenario_id).first()
        items.append(
            SessionListItem(
                id=s.id,
                scenario_name=scenario.name if scenario else None,
                start_time=s.start_time,
                end_time=s.end_time,
                overall_score=s.overall_score,
            )
        )
    return SessionList(sessions=items, total=total)


@router.get("/sessions/{session_id}", response_model=SessionOut)
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    scenario = db.query(Scenario).filter(Scenario.id == session.scenario_id).first()
    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at)
        .all()
    )

    return SessionOut(
        id=session.id,
        scenario_id=session.scenario_id,
        scenario_name=scenario.name if scenario else None,
        start_time=session.start_time,
        end_time=session.end_time,
        overall_score=session.overall_score,
        summary=session.summary,
        created_at=session.created_at,
        messages=messages,
    )


@router.post("/sessions/{session_id}/end")
def end_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.end_time = datetime.utcnow()
    db.commit()
    return {"status": "ended", "session_id": session_id}


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Cascade delete: corrections → messages → session
    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .all()
    )
    for msg in messages:
        db.query(Correction).filter(Correction.message_id == msg.id).delete()
    db.query(Message).filter(Message.session_id == session_id).delete()
    db.delete(session)
    db.commit()

    return {"status": "deleted", "session_id": session_id}


@router.get("/sessions/{session_id}/summary", response_model=SummaryOut)
async def get_summary(session_id: str, db: Session = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    scenario = db.query(Scenario).filter(Scenario.id == session.scenario_id).first()

    # Return cached summary if already generated
    if session.summary:
        try:
            result = json.loads(session.summary)
            return _summary_out(session_id, scenario, result, db)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Cached summary corrupted, regenerating: {e}")
            session.summary = None  # reset for regeneration

    try:
        messages = (
            db.query(Message)
            .options(selectinload(Message.corrections))
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at)
            .all()
        )

        # Build conversation transcript
        conversation_lines = []
        for msg in messages:
            conversation_lines.append(f"{msg.role}: {msg.content}")
            for c in msg.corrections:
                conversation_lines.append(f"  [correction] {c.original} → {c.corrected} ({c.explanation})")

        conversation_text = "\n".join(conversation_lines)

        # Generate summary via LLM and cache it
        result = await generate_summary(conversation_text)
        session.summary = json.dumps(result, ensure_ascii=False)
        session.overall_score = _compute_overall(result, messages)
        db.commit()

        return _summary_out(session_id, scenario, result, db)

    except (Exception, asyncio.CancelledError) as e:
        logger.error(f"Summary generation failed for {session_id}: {e}")
        # Return fallback so frontend never gets 500
        fallback = _fallback_summary()
        return _summary_out(session_id, scenario, fallback, db)


def _compute_overall(result: dict, messages: list[Message]) -> float:
    """Compute overall_score from LLM result and per-message scores."""
    def avg(lst):
        return round(sum(lst) / len(lst), 1) if lst else 0

    grammar_scores = [m.grammar_score for m in messages if m.grammar_score is not None]
    fluency_scores = [m.fluency_score for m in messages if m.fluency_score is not None]
    vocab_scores = [m.vocabulary_score for m in messages if m.vocabulary_score is not None]

    pronunciation_val = result.get("dimensions", {}).get("pronunciation", 0)
    if not pronunciation_val:
        avg_others = avg(
            [s for s in [avg(grammar_scores), avg(fluency_scores), avg(vocab_scores)] if s]
        )
        pronunciation_val = max(avg_others or 0, 0)

    d = result.get("dimensions", {})
    grammar = d.get("grammar", avg(grammar_scores))
    fluency = d.get("fluency", avg(fluency_scores))
    vocabulary = d.get("vocabulary", avg(vocab_scores))

    overall = result.get("overall_score", 0)
    if not overall:
        overall = round((grammar + fluency + vocabulary + pronunciation_val) / 4, 1)
    return overall


def _compute_dimensions(result: dict, messages: list[Message]) -> DimensionScores:
    """Compute DimensionScores from LLM result and per-message scores."""
    def avg(lst):
        return round(sum(lst) / len(lst), 1) if lst else 0

    grammar_scores = [m.grammar_score for m in messages if m.grammar_score is not None]
    fluency_scores = [m.fluency_score for m in messages if m.fluency_score is not None]
    vocab_scores = [m.vocabulary_score for m in messages if m.vocabulary_score is not None]

    pronunciation_val = result.get("dimensions", {}).get("pronunciation", 0)
    if not pronunciation_val:
        avg_others = avg(
            [s for s in [avg(grammar_scores), avg(fluency_scores), avg(vocab_scores)] if s]
        )
        pronunciation_val = max(avg_others or 0, 0)

    d = result.get("dimensions", {})
    return DimensionScores(
        grammar=d.get("grammar", avg(grammar_scores)),
        fluency=d.get("fluency", avg(fluency_scores)),
        vocabulary=d.get("vocabulary", avg(vocab_scores)),
        pronunciation=pronunciation_val,
    )


def _summary_out(session_id: str, scenario, result: dict, db: Session) -> SummaryOut:
    """Build SummaryOut from result dict, computing scores from messages."""
    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .all()
    )
    return SummaryOut(
        session_id=session_id,
        scenario_name=scenario.name if scenario else "对话练习",
        overall_score=result.get("overall_score", _compute_overall(result, messages)),
        dimensions=_compute_dimensions(result, messages),
        strengths=result.get("strengths", []),
        weaknesses=result.get("weaknesses", []),
        tips=result.get("tips", []),
        corrected_dialogue=[
            CorrectedDialogue(**d) for d in result.get("corrected_dialogue", [])
        ],
    )
