import asyncio

from app.config import UPLOAD_DIR
from app.database import get_connection

RETENTION_DAYS = 30


def delete_old_photos() -> int:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, filename FROM photos WHERE uploaded_at < datetime('now', ?)",
            (f"-{RETENTION_DAYS} days",),
        ).fetchall()
        for r in rows:
            conn.execute("DELETE FROM photos WHERE id = ?", (r["id"],))
        conn.commit()
    finally:
        conn.close()
    for r in rows:
        (UPLOAD_DIR / r["filename"]).unlink(missing_ok=True)
    return len(rows)


async def cleanup_loop():
    while True:
        await asyncio.to_thread(delete_old_photos)
        await asyncio.sleep(6 * 60 * 60)  # har 6 ghante