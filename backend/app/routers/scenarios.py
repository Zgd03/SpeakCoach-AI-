from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Scenario, Session, Message, Correction
from app.schemas.schemas import ScenarioList, ScenarioOut, ScenarioCreate

router = APIRouter()


@router.get("/scenarios", response_model=ScenarioList)
def list_scenarios(db: Session = Depends(get_db)):
    scenarios = db.query(Scenario).order_by(Scenario.id).all()
    return ScenarioList(scenarios=scenarios)


@router.get("/scenarios/{scenario_id}", response_model=ScenarioOut)
def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@router.post("/scenarios", response_model=ScenarioOut, status_code=201)
def create_scenario(body: ScenarioCreate, db: Session = Depends(get_db)):
    scenario = Scenario(**body.model_dump())
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return scenario


@router.delete("/scenarios/{scenario_id}")
def delete_scenario(scenario_id: int, db: Session = Depends(get_db)):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Cascade delete: sessions → messages → corrections
    sessions = db.query(Session).filter(Session.scenario_id == scenario_id).all()
    for s in sessions:
        messages = db.query(Message).filter(Message.session_id == s.id).all()
        for msg in messages:
            db.query(Correction).filter(Correction.message_id == msg.id).delete()
        db.query(Message).filter(Message.session_id == s.id).delete()
        db.delete(s)
    db.delete(scenario)
    db.commit()

    return {"status": "deleted", "scenario_id": scenario_id}
