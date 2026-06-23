# накидываем немного трафика чтобы ab/stats не был пустой

import random
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

BASE = "http://127.0.0.1:8000"


def main():
    with httpx.Client(base_url=BASE, timeout=30, trust_env=False) as c:
        for uid in range(1, 6):
            r = c.get(f"/users/{uid}/recommendations", params={"top_k": 5})
            r.raise_for_status()
            for item in r.json():
                if random.random() < 0.3:
                    c.post(
                        "/events",
                        json={
                            "user_id": uid,
                            "job_id": item["job"]["id"],
                            "event_type": "click",
                            "position": item["position"],
                        },
                    )

        print(c.get("/ab/stats").json())


if __name__ == "__main__":
    main()
