import asyncio

# Har connected display (TV) ki ek queue hoti hai
subscribers: set = set()


def subscribe() -> asyncio.Queue:
    q = asyncio.Queue()
    subscribers.add(q)
    return q


def unsubscribe(q: asyncio.Queue) -> None:
    subscribers.discard(q)


def publish(event: dict) -> None:
    """Sabhi connected displays ko event bhejta hai."""
    for q in list(subscribers):
        q.put_nowait(event)