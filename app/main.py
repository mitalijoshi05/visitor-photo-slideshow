import re
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.config import MAX_FILE_SIZE_BYTES, MAX_FILES_PER_UPLOAD
from app.database import get_connection, init_db
from app.images import ImageError, validate_and_save
from app.security import hash_pin, verify_pin
from fastapi.responses import FileResponse
from app.config import UPLOAD_DIR
from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def home():
    return FileResponse("app/static/index.html")

@app.post("/upload")
async def upload(
    name: str = Form(...),
    pin: str = Form(...),
    consent: bool = Form(False),
    photos: List[UploadFile] = File(...),
):
    name = name.strip()

    # 1. Basic checks
    if not (1 <= len(name) <= 50):
        raise HTTPException(400, "Name must be 1 to 50 characters.")
    if not re.fullmatch(r"\d{4}", pin):
        raise HTTPException(400, "PIN must be exactly 4 digits.")
    if not consent:
        raise HTTPException(400, "You must agree to show your photos publicly.")
    if len(photos) > MAX_FILES_PER_UPLOAD:
        raise HTTPException(400, f"Maximum {MAX_FILES_PER_UPLOAD} photos at a time.")

    # 2. Pehle saari photos validate karo, phir visitor ko touch karo
    saved = []
    try:
        for photo in photos:
            data = await photo.read(MAX_FILE_SIZE_BYTES + 1)
            saved.append(validate_and_save(data))
    except ImageError as e:
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
                raise HTTPException(
                    401, "This name is already taken. Wrong PIN or pick another name."
                )
            visitor_id = row["id"]
            returning = True

        for filename in saved:
            conn.execute(
                "INSERT INTO photos (visitor_id, filename, consent) VALUES (?, ?, 1)",
                (visitor_id, filename),
            )
        conn.commit()
    finally:
        conn.close()

    return {"ok": True, "returning_visitor": returning, "photos_saved": len(saved)}

@app.get("/display")
def display_page():
    return FileResponse("app/static/display.html")


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