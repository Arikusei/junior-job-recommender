import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/jobs.db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
ARTIFACTS_DIR = os.getenv("ARTIFACTS_DIR", "./artifacts")
