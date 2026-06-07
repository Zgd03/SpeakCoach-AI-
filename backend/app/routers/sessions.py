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
from app.services.summary_service import generate_summary

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
def list_sessions(db: Session = Depends(get_db)):
    sessions = (
        db.query(Session)
        .order_by(Session.created_at.desc())
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
    return SessionList(sessions=items)


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


@router.get("/sessions/{session_id}/summary", response_model=SummaryOut)
async def get_summary(session_id: str, db: Session = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    scenario = db.query(Scenario).filter(Scenario.id == session.scenario_id).first()
    messages = (
        db.query(Message)
        .options(selectinload(Message.corrections))
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at)
        .all()
    )

    # Build conversation transcript (corrections eager-loaded)
    conversation_lines = []
    for msg in messages:
        conversation_lines.append(f"{msg.role}: {msg.content}")
        for c in msg.corrections:
            conversation_lines.append(f"  [correction] {c.original} → {c.corrected} ({c.explanation})")

    conversation_text = "\n".join(conversation_lines)

    # Generate summary via LLM
    result = await generate_summary(conversation_text)

    # Calculate average scores if we have per-message scores
    grammar_scores = [m.grammar_score for m in messages if m.grammar_score is not None]
    fluency_scores = [m.fluency_score for m in messages if m.fluency_score is not None]
    vocab_scores = [m.vocabulary_score for m in messages if m.vocabulary_score is not None]

    def avg(lst):
        return round(sum(lst) / len(lst), 1) if lst else 0

    dimensions = DimensionScores(
        grammar=result.get("dimensions", {}).get("grammar", avg(grammar_scores)),
        fluency=result.get("dimensions", {}).get("fluency", avg(fluency_scores)),
        vocabulary=result.get("dimensions", {}).get("vocabulary", avg(vocab_scores)),
        pronunciation=result.get("dimensions", {}).get("pronunciation", 80),
    )

    overall = result.get("overall_score", 0)
    if not overall:
        overall = round(
            (dimensions.grammar + dimensions.fluency + dimensions.vocabulary + dimensions.pronunciation) / 4, 1
        )

    return SummaryOut(
        session_id=session_id,
        scenario_name=scenario.name if scenario else "对话练习",
        overall_score=overall,
        dimensions=dimensions,
        strengths=result.get("strengths", []),
        weaknesses=result.get("weaknesses", []),
        tips=result.get("tips", []),
        corrected_dialogue=[
            CorrectedDialogue(**d) for d in result.get("corrected_dialogue", [])
        ],
    )
