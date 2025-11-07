from prometheus_client import Counter, Histogram

SCRAPER_REQUESTS = Counter(
    "scraper_requests_total",
    "Total scraper requests",
    ["scraper", "op"]  # op: headlines/article
)

SCRAPER_ERRORS = Counter(
    "scraper_errors_total",
    "Total scraper errors",
    ["scraper", "op"]
)

SCRAPER_LATENCY = Histogram(
    "scraper_request_duration_seconds",
    "Scraper request latency seconds",
    ["scraper", "op"]
)