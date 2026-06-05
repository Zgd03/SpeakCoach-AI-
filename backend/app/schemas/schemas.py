from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ---- Scenario ----
class ScenarioOut(BaseModel):
    id: int
    name: str
    description: str
    icon: str
    difficulty: str
    system_prompt: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ScenarioList(BaseModel):
    scenarios: list[ScenarioOut]


# ---- Correction ----
class CorrectionOut(BaseModel):
    id: int
    original_text: str
    corrected_text: str
    error_type: str
    explanation: str
    severity: str

    model_config = {"from_attributes": True}


# ---- Message ----
class MessageOut(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    grammar_score: Optional[float] = None
    fluency_score: Optional[float] = None
    vocabulary_score: Optional[float] = None
    created_at: datetime
    corrections: list[CorrectionOut] = []

    model_config = {"from_attributes": True}


# ---- Session ----
class SessionCreate(BaseModel):
    scenario_id: int


class SessionOut(BaseModel):
    id: str
    scenario_id: int
    scenario_name: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    overall_score: Optional[float] = None
    summary: Optional[str] = None
    created_at: datetime
    messages: list[MessageOut] = []

    model_config = {"from_attributes": True}


class SessionListItem(BaseModel):
    id: str
    scenario_name: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    overall_score: Optional[float] = None

    model_config = {"from_attributes": True}


class SessionList(BaseModel):
    sessions: list[SessionListItem]


# ---- Summary ----
class DimensionScores(BaseModel):
    grammar: float = 0
    fluency: float = 0
    vocabulary: float = 0
    pronunciation: float = 0


class CorrectedDialogue(BaseModel):
    original: str
    corrected: str
    explanation: str


class SummaryOut(BaseModel):
    session_id: str
    scenario_name: str
    overall_score: float
    dimensions: DimensionScores
    strengths: list[str] = []
    weaknesses: list[str] = []
    tips: list[str] = []
    corrected_dialogue: list[CorrectedDialogue] = []


# ---- WebSocket Messages ----
class WSUserMessage(BaseModel):
    type: str = "user_message"
    text: str


class WSCorrection(BaseModel):
    original: str
    corrected: str
    error_type: str
    explanation: str
    severity: str


class WSScoreUpdate(BaseModel):
    grammar: float
    fluency: float
    vocabulary: float
