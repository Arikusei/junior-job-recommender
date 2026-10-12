# junior-job-recommender

Пет-проект: REST API рекомендаций вакансий для джуниор-специалистов с семантическим поиском на базе эмбеддингов и векторного индекса FAISS.

Проект создавался для отработки бэкенд-навыков (FastAPI, SQLAlchemy, SQLite, Pydantic) и знакомства с векторным поиском (Sentence-BERT + FAISS).

## Что умеет сервис

- **Семантический поиск**: поиск вакансий по текстовому запросу на базе векторного сходства (косинусное расстояние / `IndexFlatIP`).
- **Персональные рекомендации**: ранжирование вакансий по степени соответствия резюме кандидата.
- **A/B сплитование**: разделение пользователей на когорты `control` (популярные вакансии) и `treatment` (семантические рекомендации) для оценки CTR.
- **REST API на FastAPI**: валидация входных данных, автоматическая Swagger-документация.
- **Логирование событий**: запись просмотров и кликов в SQLite для аналитики.

## Быстрый старт

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Наполнение базы тестовыми данными и сборка индекса FAISS
python scripts/seed_data.py
python scripts/build_index.py

# Запуск API
uvicorn app.main:app --reload --port 8000
```

- Swagger UI: http://127.0.0.1:8000/docs
- Healthcheck: http://127.0.0.1:8000/health

### Примеры запросов

- `GET /users/1/recommendations?top_k=5` — получить персональные рекомендации для соискателя.
- `POST /search` с телом `{"query": "python fastapi junior backend", "top_k": 5}` — семантический поиск по описаниям вакансий.
- `GET /ab/stats` — метрики распределения групп и конверсии в отклики.

## Стек технологий

- **Бэкенд**: Python 3, FastAPI, Pydantic, SQLAlchemy, SQLite.
- **Векторный поиск**: Sentence-Transformers (`all-MiniLM-L6-v2`), FAISS, NumPy.
- **Тестирование**: PyTest.
- **Контейнеризация**: Docker.

## Тесты

```powershell
pytest
```
