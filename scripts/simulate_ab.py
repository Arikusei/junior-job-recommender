"""Simulate user traffic to populate A/B test metrics."""

from __future__ import annotations

import random

import httpx

BASE_URL = "http://127.0.0.1:8000"


def simulate(rounds: int = 3) -> None:
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        for user_id in range(1, 6):
            response = client.get(f"/users/{user_id}/recommendations", params={"top_k": 5})
            response.raise_for_status()
            recommendations = response.json()

            for item in recommendations:
                if random.random() < 0.25:
                    client.post(
                        "/events",
                        json={
                            "user_id": user_id,
                            "job_id": item["job"]["id"],
                            "event_type": "click",
                            "position": item["position"],
                            "score": item["score"],
                        },
                    )

        for _ in range(rounds):
            for user_id in range(1, 6):
                client.get(f"/users/{user_id}/recommendations", params={"top_k": 5})

        stats = client.get("/ab/stats")
        stats.raise_for_status()
        print("A/B stats:")
        for row in stats.json():
            print(
                f"  {row['variant']}: impressions={row['impressions']}, "
                f"clicks={row['clicks']}, ctr={row['ctr']:.2%}"
            )


if __name__ == "__main__":
    simulate()
