import asyncio
import json
import re
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from app import events, ratelimit
from app.cleanup import cleanup_loop
from app.config import MAX_FILE_SIZE_BYTES, MAX_FILES_PER_UPLOAD, UPLOAD_DIR
from app.database import get_connection, init_db
from app.images import ImageError, validate_and_save
from app.security import hash_pin, verify_pin


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    task = asyncio.create_task(cleanup_loop())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)

UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


def client_keys(request: Request, name: str):
    ip = request.client.host if request.client else "unknown"
    return f"ip:{ip}", f"name:{name.lower()}"


@app.get("/")
def home():
    return FileResponse("app/static/index.html")


@app.get("/display")
def display_page():
    return FileResponse("app/static/display.html")


@app.post("/upload")
async def upload(
    request: Request,
    name: str = Form(...),
    pin: str = Form(...),
    consent: bool = Form(False),
    photos: List[UploadFile] = File(...),
):
    name = name.strip()

    ip_key, name_key = client_keys(request, name)
    if ratelimit.is_blocked(ip_key) or ratelimit.is_blocked(name_key):
        raise HTTPException(429, "Too many wrong attempts. Try again in 15 minutes.")

    # 1. Basic checks
    if not (1 <= len(name) <= 50):
        raise HTTPException(400, "Name must be 1 to 50 characters.")
    if not re.fullmatch(r"\d{4}", pin):
        raise HTTPException(400, "PIN must be exactly 4 digits.")
    if not consent:
        raise HTTPException(400, "You must agree to show your photos publicly.")
    if len(photos) > MAX_FILES_PER_UPLOAD:
        raise HTTPException(400, f"Maximum {MAX_FILES_PER_UPLOAD} photos at a time.")

    # 2. Saari photos validate karo
    saved = []
    try:
        for photo in photos:
            data = await photo.read(MAX_FILE_SIZE_BYTES + 1)
            saved.append(validate_and_save(data))
    except ImageError as e:
        for f in saved:
            (UPLOAD_DIR / f).unlink(missing_ok=True)
        raise HTTPException(400, f"{photo.filename}: {e}")

    # 3. Visitor dhoondo ya naya banao
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, pin_hash FROM visitors WHERE name = ?", (name,)
        ).fetchone()

        if row is None:
            cur = conn.execute(
                "INSERT INTO visitors (name, pin_hash) VALUES (?, ?)",
                (name, hash_pin(pin)),
            )
            visitor_id = cur.lastrowid
            returning = False
        else:
            if not verify_pin(pin, row["pin_hash"]):
                ratelimit.record_failure(ip_key)
                ratelimit.record_failure(name_key)
                for f in saved:
                    (UPLOAD_DIR / f).unlink(missing_ok=True)
                raise HTTPException(
                    401, "This name is already taken. Wrong PIN or pick another name."
                )
            visitor_id = row["id"]
            ratelimit.clear(name_key)
            returning = True

        for filename in saved:
            conn.execute(
                "INSERT INTO photos (visitor_id, filename, consent) VALUES (?, ?, 1)",
                (visitor_id, filename),
            )
        conn.commit()
    finally:
        conn.close()

    events.publish({"type": "new_photos", "visitor": name, "count": len(saved)})
    return {"ok": True, "returning_visitor": returning, "photos_saved": len(saved)}


@app.post("/delete-my-photos")
def delete_my_photos(request: Request, name: str = Form(...), pin: str = Form(...)):
    name = name.strip()

    ip_key, name_key = client_keys(request, name)
    if ratelimit.is_blocked(ip_key) or ratelimit.is_blocked(name_key):
        raise HTTPException(429, "Too many wrong attempts. Try again in 15 minutes.")

    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, pin_hash FROM visitors WHERE name = ?", (name,)
        ).fetchone()

        # Same message dono cases me, taaki koi guess na kar sake ki naam exist karta hai
        if row is None or not verify_pin(pin, row["pin_hash"]):
            ratelimit.record_failure(ip_key)
            ratelimit.record_failure(name_key)
            raise HTTPException(401, "Name or PIN is incorrect.")

        ratelimit.clear(name_key)

        files = conn.execute(
            "SELECT filename FROM photos WHERE visitor_id = ?", (row["id"],)
        ).fetchall()

        # Pehle DB se hatao (CASCADE se photo rows bhi hat jayengi)
        conn.execute("DELETE FROM visitors WHERE id = ?", (row["id"],))
        conn.commit()
    finally:
        conn.close()

    # Phir disk se files hatao
    for f in files:
        (UPLOAD_DIR / f["filename"]).unlink(missing_ok=True)

    events.publish({"type": "photos_deleted", "visitor": name})
    return {"ok": True, "photos_deleted": len(files)}


@app.get("/api/photos")
def list_photos():
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT p.id, p.filename, v.name
            FROM photos p
            JOIN visitors v ON v.id = p.visitor_id
            WHERE p.consent = 1
            ORDER BY p.id ASC
            """
        ).fetchall()
    finally:
        conn.close()
    return [
        {"id": r["id"], "url": f"/uploads/{r['filename']}", "name": r["name"]}
        for r in rows
    ]


@app.get("/events")
async def stream_events():
    q = events.subscribe()

    async def gen():
        try:
            while True:
                try:
                    event = await asyncio.wait_for(q.get(), timeout=15)
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"  # connection zinda rakhne ke liye
        finally:
            events.unsubscribe(q)

    return StreamingResponse(gen(), media_type="text/event-stream")