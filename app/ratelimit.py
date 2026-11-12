import time

MAX_FAILURES = 5          # itni galat tries allowed
WINDOW_SECONDS = 15 * 60  # 15 minute ka window

# key -> galat tries ke timestamps ki list
_failures: dict = {}


def _recent(key: str) -> list:
    now = time.time()
    recent = [t for t in _failures.get(key, []) if now - t < WINDOW_SECONDS]
    _failures[key] = recent
    return recent


def is_blocked(key: str) -> bool:
    return len(_recent(key)) >= MAX_FAILURES


def record_failure(key: str) -> None:
    _recent(key).append(time.time())


def clear(key: str) -> None:
    _failures.pop(key, None)