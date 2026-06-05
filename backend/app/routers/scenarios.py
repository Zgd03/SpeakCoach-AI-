from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Scenario
from app.schemas.schemas import ScenarioList, ScenarioOut

router = APIRouter()


@router.get("/scenarios", response_model=ScenarioList)
def list_scenarios(db: Session = Depends(get_db)):
    scenarios = db.query(Scenario).all()
    return ScenarioList(scenarios=scenarios)


@router.get("/scenarios/{scenario_id}", response_model=ScenarioOut)
def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    return scenario
