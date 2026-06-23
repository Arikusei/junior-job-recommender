# job-recommender

Небольшой пет-проект: рекомендации вакансий для джунов + семантический поиск.

Делал для практики перед собесами на ml-позиции. Данные фейковые, вакансии набросал руками.

## что умеет

- рекомендации: либо по популярности, либо по сходству резюме с вакансией (sentence-bert + faiss)
- поиск по тексту запроса
- простой a/b тест (control vs treatment), смотрю ctr
- api на fastapi, бд sqlite

## запуск

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

python scripts/seed_data.py
python scripts/build_index.py   # первый раз качает модель, подождать

uvicorn app.main:app --reload
```

доки: http://127.0.0.1:8000/docs

примеры:

```
GET /users/1/recommendations?top_k=5
POST /search  {"query": "python fastapi junior", "top_k": 5}
GET /ab/stats
```

## стек

python, fastapi, sqlalchemy, sqlite, sentence-transformers, faiss, sklearn (пока почти не трогал, хочу добавить baseline)

## todo

- [ ] нормальный парсер вакансий вместо seed_data
- [ ] mlflow для экспериментов
- [ ] docker нормально проверить на linux
- [ ] тесты побольше

## тесты

```
pytest
```

## docker (черновик)

```
docker build -t job-rec .
docker run -p 8000:8000 job-rec
```
