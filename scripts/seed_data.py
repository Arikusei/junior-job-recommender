"""Seed synthetic junior IT vacancies and user profiles."""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.models import Job, SessionLocal, UserProfile, init_db

JOBS = [
    {
        "title": "Junior Python Developer",
        "company": "FinTech Start",
        "description": "Разработка REST API на FastAPI, работа с PostgreSQL, code review.",
        "skills": "Python, FastAPI, SQL, Git",
        "city": "Москва",
        "salary_min": 90000,
        "salary_max": 130000,
    },
    {
        "title": "Junior Data Analyst",
        "company": "Retail Analytics",
        "description": "Подготовка отчётов, A/B-тесты, визуализация метрик удержания.",
        "skills": "SQL, Python, pandas, Tableau",
        "city": "Санкт-Петербург",
        "salary_min": 80000,
        "salary_max": 110000,
    },
    {
        "title": "Junior ML Engineer",
        "company": "AI Lab",
        "description": "Обучение baseline-моделей, feature engineering, деплой в Docker.",
        "skills": "Python, scikit-learn, PyTorch, Docker",
        "city": "Удалённо",
        "salary_min": 120000,
        "salary_max": 170000,
    },
    {
        "title": "Junior Backend Developer",
        "company": "Marketplace",
        "description": "Микросервисы, интеграции, оптимизация SQL-запросов.",
        "skills": "Python, Django, PostgreSQL, Redis",
        "city": "Казань",
        "salary_min": 85000,
        "salary_max": 120000,
    },
    {
        "title": "Junior Frontend Developer",
        "company": "EdTech",
        "description": "React-компоненты, интеграция с API, accessibility.",
        "skills": "JavaScript, React, TypeScript, CSS",
        "city": "Новосибирск",
        "salary_min": 90000,
        "salary_max": 125000,
    },
    {
        "title": "Junior NLP Engineer",
        "company": "Search Team",
        "description": "Векторизация текстов, semantic search, оценка качества ранжирования.",
        "skills": "Python, BERT, FAISS, FastAPI",
        "city": "Москва",
        "salary_min": 130000,
        "salary_max": 180000,
    },
    {
        "title": "Junior QA Engineer",
        "company": "SaaS Platform",
        "description": "Автотесты API, регрессионное тестирование, CI/CD.",
        "skills": "Python, pytest, Postman, GitLab CI",
        "city": "Екатеринбург",
        "salary_min": 70000,
        "salary_max": 100000,
    },
    {
        "title": "Junior DevOps Engineer",
        "company": "Cloud Ops",
        "description": "Docker, Kubernetes basics, мониторинг, алерты.",
        "skills": "Linux, Docker, Kubernetes, Prometheus",
        "city": "Удалённо",
        "salary_min": 100000,
        "salary_max": 140000,
    },
    {
        "title": "Junior iOS Developer",
        "company": "Mobile Studio",
        "description": "SwiftUI экраны, работа с REST API, unit-тесты.",
        "skills": "Swift, SwiftUI, Git",
        "city": "Москва",
        "salary_min": 95000,
        "salary_max": 135000,
    },
    {
        "title": "Junior Product Analyst",
        "company": "Growth Team",
        "description": "Воронки, DAU/MAU, когортный анализ, гипотезы роста.",
        "skills": "SQL, Python, Amplitude, A/B testing",
        "city": "Санкт-Петербург",
        "salary_min": 90000,
        "salary_max": 120000,
    },
    {
        "title": "Junior Go Developer",
        "company": "Infra Team",
        "description": "Высоконагруженные сервисы, gRPC, observability.",
        "skills": "Go, PostgreSQL, gRPC, Docker",
        "city": "Москва",
        "salary_min": 110000,
        "salary_max": 150000,
    },
    {
        "title": "Junior Data Engineer",
        "company": "Data Platform",
        "description": "ETL-пайплайны, Airflow DAGs, подготовка витрин.",
        "skills": "Python, SQL, Airflow, Spark",
        "city": "Удалённо",
        "salary_min": 115000,
        "salary_max": 160000,
    },
]

USERS = [
    {
        "name": "Анна",
        "resume_text": "Студентка МФТИ, pet-проекты на Python и FastAPI, интерес к NLP.",
        "skills": "Python, FastAPI, SQL, pandas",
    },
    {
        "name": "Илья",
        "resume_text": "Стажёр в аналитике, строил дашборды и считал конверсию в продукте.",
        "skills": "SQL, Python, Tableau, A/B testing",
    },
    {
        "name": "Мария",
        "resume_text": "Хочу в ML: baseline-модели, sklearn, небольшие эксперименты в PyTorch.",
        "skills": "Python, scikit-learn, PyTorch, Docker",
    },
    {
        "name": "Денис",
        "resume_text": "Junior backend: Django, REST, оптимизация запросов в PostgreSQL.",
        "skills": "Python, Django, PostgreSQL, Redis",
    },
    {
        "name": "София",
        "resume_text": "Frontend-стажёр, делала лендинги и SPA на React.",
        "skills": "JavaScript, React, TypeScript, CSS",
    },
]


def seed() -> None:
    Path("data").mkdir(exist_ok=True)
    init_db()
    db = SessionLocal()
    try:
        if db.query(Job).count() > 0:
            print("Database already seeded, skipping.")
            return

        for payload in JOBS:
            job = Job(
                **payload,
                views=random.randint(10, 200),
                applications=random.randint(0, 40),
            )
            db.add(job)

        for idx, payload in enumerate(USERS, start=1):
            db.add(UserProfile(id=idx, **payload))

        db.commit()
        print(f"Seeded {len(JOBS)} jobs and {len(USERS)} users.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
