from prometheus_client import Counter, Histogram

RECOMMENDATION_REQUESTS = Counter(
    "recommendation_requests_total",
    "Total recommendation requests",
    ["variant"],
)

SEARCH_REQUESTS = Counter("search_requests_total", "Total semantic search requests")

EVENTS_TOTAL = Counter(
    "user_events_total",
    "Tracked user events",
    ["event_type", "variant"],
)

RECOMMENDATION_LATENCY = Histogram(
    "recommendation_latency_seconds",
    "Recommendation endpoint latency",
    ["variant"],
)

SEARCH_LATENCY = Histogram("search_latency_seconds", "Search endpoint latency")

EMBEDDING_ERRORS = Counter("embedding_errors_total", "Embedding pipeline errors")
