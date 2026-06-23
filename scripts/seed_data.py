# скрипт для заполнения бд тестовыми вакансиями
# TODO: потом подключить реальный парсер / csv

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import Job, SessionLocal, UserProfile, init_db

JOBS = [
    ("Junior Python Developer", "FinTech Start", "REST API на FastAPI, PostgreSQL", "Python, FastAPI, SQL", "Москва", 90000, 130000),
    ("Junior Data Analyst", "Retail Analytics", "отчёты, sql, немного python", "SQL, Python, pandas", "СПб", 80000, 110000),
    ("Junior ML Engineer", "AI Lab", "sklearn, pytorch, docker", "Python, scikit-learn, PyTorch", "удалёнка", 120000, 170000),
    ("Junior Backend Developer", "Marketplace", "django, postgres", "Python, Django, SQL", "Казань", 85000, 120000),
    ("Junior Frontend Developer", "EdTech", "react, typescript", "JavaScript, React, CSS", "Новосибирск", 90000, 125000),
    ("Junior NLP Engineer", "Search Team", "эмбеддинги, faiss, fastapi", "Python, BERT, FAISS", "Москва", 130000, 180000),
    ("Junior QA Engineer", "SaaS", "автотесты api", "Python, pytest, Postman", "Екатеринбург", 70000, 100000),
    ("Junior DevOps", "Cloud Ops", "docker, linux", "Linux, Docker, Git", "удалёнка", 100000, 140000),
    ("Junior iOS Developer", "Mobile Studio", "swift, swiftui", "Swift, Git", "Москва", 95000, 135000),
    ("Junior Product Analyst", "Growth", "воронки, ab тесты", "SQL, Python, Amplitude", "СПб", 90000, 120000),
    ("Junior Go Developer", "Infra", "микросервисы на go", "Go, PostgreSQL, Docker", "Москва", 110000, 150000),
    ("Junior Data Engineer", "Data Platform", "etl, airflow", "Python, SQL, Airflow", "удалёнка", 115000, 160000),
]

USERS = [
    (1, "Анна", "учусь на мфти, пишу на python, делала api на fastapi", "python, fastapi, sql"),
    (2, "Илья", "стажировался аналитиком, sql + tableau", "sql, python, pandas"),
    (3, "Мария", "интересен ml, курсы по sklearn и pytorch", "python, sklearn, pytorch"),
    (4, "Денис", "junior backend, django pet project", "python, django, postgres"),
    (5, "София", "фронт на react", "javascript, react, typescript"),
]


def main():
    Path("data").mkdir(exist_ok=True)
    init_db()
    db = SessionLocal()

    if db.query(Job).count() > 0:
        print("уже есть данные, выхожу")
        return

    for title, company, desc, skills, city, smin, smax in JOBS:
        db.add(
            Job(
                title=title,
                company=company,
                description=desc,
                skills=skills,
                city=city,
                salary_min=smin,
                salary_max=smax,
                views=random.randint(5, 150),
                applications=random.randint(0, 30),
            )
        )

    for uid, name, resume, skills in USERS:
        db.add(UserProfile(id=uid, name=name, resume_text=resume, skills=skills))

    db.commit()
    db.close()
    print("готово, залил вакансии и юзеров")


if __name__ == "__main__":
    main()
