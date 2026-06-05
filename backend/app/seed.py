"""Seed the database with default scenarios."""

from app.database import SessionLocal, engine, Base
from app.models.db_models import Scenario

SCENARIOS = [
    {
        "name": "面试 (Job Interview)",
        "description": "模拟面试场景，面试官会询问你的背景、经验和技术能力",
        "icon": "💼",
        "difficulty": "中级",
        "system_prompt": "job interview — You are a professional HR interviewer at a tech company. "
        "Ask the user about their work experience, skills, career goals, "
        "and why they want this job. Be professional but friendly. "
        "Give the user a chance to speak in full sentences.",
    },
    {
        "name": "餐厅点餐 (Restaurant Ordering)",
        "description": "模拟在餐厅点餐的场景，练习点菜、询问菜品信息等",
        "icon": "🍽️",
        "difficulty": "初级",
        "system_prompt": "restaurant ordering — You are a friendly waiter at an American restaurant. "
        "Greet the user, offer menus, describe today's specials, "
        "answer questions about the menu, and take their order. "
        "Be patient and encouraging.",
    },
    {
        "name": "商务会议 (Business Meeting)",
        "description": "模拟商务会议场景，练习发表意见、讨论方案等",
        "icon": "📊",
        "difficulty": "高级",
        "system_prompt": "business meeting — You are a colleague in a business meeting. "
        "Discuss project updates, budgets, timelines, and next steps. "
        "Use professional business English. Ask for the user's opinion "
        "on various topics and challenge their ideas constructively.",
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    existing = db.query(Scenario).count()
    if existing > 0:
        print(f"Database already has {existing} scenarios, skipping seed.")
        db.close()
        return

    for s in SCENARIOS:
        scenario = Scenario(**s)
        db.add(scenario)

    db.commit()
    db.close()
    print(f"Seeded {len(SCENARIOS)} scenarios successfully.")


if __name__ == "__main__":
    seed()
