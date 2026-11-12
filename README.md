# Visitor Photo Slideshow

A web app for events (for example a Diwali party). Visitors scan a QR code,
enter their name, a 4-digit PIN and photos, and agree to public display.
Their photos appear on a big screen (TV or computer) within a second.
Returning visitors can upload again with the same name and PIN, and all
their earlier photos keep playing in the slideshow.

## Features
- Upload page with name, PIN, photos and a consent checkbox
- Slideshow page for the TV with live updates (Server-Sent Events)
- Returning visitor identified by name + PIN
- File validation: real image check, JPG/PNG/WebP only, 5 MB limit, max 5 photos
- Delete-my-photos with PIN check
- Rate limiting on wrong PINs
- Automatic deletion of photos after 30 days

## Tech stack
Python 3, FastAPI, SQLite, Pillow, plain HTML/CSS/JS, pytest.

## Setup
    git clone https://github.com/mitalijoshi05/visitor-photo-slideshow.git
    cd visitor-photo-slideshow
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env

## Run
    uvicorn app.main:app --reload

- Upload page: http://127.0.0.1:8000
- TV slideshow: http://127.0.0.1:8000/display

To use it with phones, run with `--host 0.0.0.0` and open
`http://<your-laptop-ip>:8000` on the phones (same Wi-Fi).

## Tests
    python -m pytest -v

## Documentation
- [ASSUMPTIONS.md](ASSUMPTIONS.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [AI_LOG.md](AI_LOG.md)

## Deployed link
Not deployed yet.