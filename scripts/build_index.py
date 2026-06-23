# считаем эмбеддинги и строим faiss индекс
# первый запуск долгий — качает модель с huggingface

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal, init_db
from app.recommender import build_and_save_index


def main():
    init_db()
    db = SessionLocal()
    n = build_and_save_index(db)
    db.close()
    print(f"индекс готов, вакансий: {n}")


if __name__ == "__main__":
    main()
