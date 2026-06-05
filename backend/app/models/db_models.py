import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    icon = Column(String(50), default="🎙️")
    difficulty = Column(String(20), default="中级")  # 初级 / 中级 / 高级
    system_prompt = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("Session", back_populates="scenario")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    overall_score = Column(Float, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    scenario = relationship("Scenario", back_populates="sessions")
    messages = relationship(
        "Message", back_populates="session", order_by="Message.created_at"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    audio_path = Column(String(255), nullable=True)
    grammar_score = Column(Float, nullable=True)
    fluency_score = Column(Float, nullable=True)
    vocabulary_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")
    corrections = relationship("Correction", back_populates="message")


class Correction(Base):
    __tablename__ = "corrections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    original_text = Column(String(500), nullable=False)
    corrected_text = Column(String(500), nullable=False)
    error_type = Column(String(50), nullable=False)  # grammar, pronunciation, expression, word_choice
    explanation = Column(Text, default="")
    severity = Column(String(20), default="minor")  # minor, major

    message = relationship("Message", back_populates="corrections")
