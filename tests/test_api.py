
import io
import sqlite3
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

from app import cleanup, database


# Helper function to create test images
def make_image(fmt="JPEG", size=(100, 100)):
    buf = io.BytesIO()
    Image.new("RGB", size, "orange").save(buf, fmt)
    buf.seek(0)
    return buf.read()


# Helper function to upload photos
def post_upload(
    client,
    name="Mitali",
    pin="1234",
    consent="true",
    files=None
):
    if files is None:
        files = [
            ("photos", ("a.jpg", make_image(), "image/jpeg"))
        ]

    return client.post(
        "/upload",
        data={
            "name": name,
            "pin": pin,
            "consent": consent
        },
        files=files
    )


# TEST 1: Valid upload
def test_valid_upload(client):
    r = post_upload(client)

    assert r.status_code == 200
    assert r.json()["returning_visitor"] is False
    assert len(list(client.uploads.iterdir())) == 1


# TEST 2: Returning visitor
def test_returning_visitor(client):
    post_upload(client)

    r = post_upload(client)

    assert r.status_code == 200
    assert r.json()["returning_visitor"] is True


# TEST 3: Wrong PIN rejected
def test_wrong_pin_rejected_and_no_orphan_file(client):
    post_upload(client)

    before = len(list(client.uploads.iterdir()))

    r = post_upload(client, pin="9999")

    assert r.status_code == 401
    assert len(list(client.uploads.iterdir())) == before


# TEST 4: Missing consent
def test_missing_consent_rejected(client):
    r = post_upload(client, consent="false")

    assert r.status_code == 400


# TEST 5: Invalid image
def test_non_image_rejected(client):
    files = [
        ("photos", ("fake.jpg", b"not an image", "image/jpeg"))
    ]

    r = post_upload(client, files=files)

    assert r.status_code == 400
    assert len(list(client.uploads.iterdir())) == 0


# TEST 6: GIF rejected
def test_gif_format_rejected(client):
    files = [
        ("photos", ("a.gif", make_image("GIF"), "image/gif"))
    ]

    r = post_upload(client, files=files)

    assert r.status_code == 400


# TEST 7: Oversized image
def test_too_large_rejected(client, monkeypatch):
    from app import images

    monkeypatch.setattr(
        images,
        "MAX_FILE_SIZE_BYTES",
        1000
    )

    files = [
        ("photos", ("big.jpg", make_image(size=(500, 500)), "image/jpeg"))
    ]

    r = post_upload(client, files=files)

    assert r.status_code == 400


# TEST 8: More than five photos
def test_too_many_files_rejected(client):
    files = [
        ("photos", (f"{i}.jpg", make_image(), "image/jpeg"))
        for i in range(6)
    ]

    r = post_upload(client, files=files)

    assert r.status_code == 400


# TEST 9: Invalid PIN format
def test_bad_pin_format_rejected(client):
    r = post_upload(client, pin="12ab")

    assert r.status_code == 400


# TEST 10: PIN hash must not be exposed
def test_photos_api_hides_pin_hash(client):
    post_upload(client)

    r = client.get("/api/photos")

    assert r.status_code == 200

    data = r.json()

    assert len(data) == 1
    assert "pin_hash" not in data[0]
    assert data[0]["name"] == "Mitali"


# TEST 11: Delete visitor photos
def test_delete_my_photos(client):
    post_upload(client)

    r = client.post(
        "/delete-my-photos",
        data={"name": "Mitali", "pin": "1234"}
    )

    assert r.status_code == 200
    assert r.json()["photos_deleted"] == 1
    assert len(list(client.uploads.iterdir())) == 0
    assert client.get("/api/photos").json() == []


# TEST 12: Wrong PIN during deletion
def test_delete_with_wrong_pin(client):
    post_upload(client)

    r = client.post(
        "/delete-my-photos",
        data={"name": "Mitali", "pin": "0000"}
    )

    assert r.status_code == 401
    assert len(list(client.uploads.iterdir())) == 1


# TEST 13: Rate limiting
def test_rate_limit_blocks_after_5_failures(client):
    post_upload(client)

    for _ in range(5):
        client.post(
            "/delete-my-photos",
            data={"name": "Mitali", "pin": "0000"}
        )

    r = client.post(
        "/delete-my-photos",
        data={"name": "Mitali", "pin": "1234"}
    )

    assert r.status_code == 429


# TEST 14: Simultaneous uploads
def test_concurrent_uploads_all_saved(client):

    def go(i):
        return post_upload(
            client,
            name=f"User{i}",
            pin="1111"
        )

    with ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(go, range(5)))

    assert all(r.status_code == 200 for r in results)
    assert len(client.get("/api/photos").json()) == 5


# TEST 15: Automatic deletion after 30 days
def test_old_photos_are_deleted(client):
    post_upload(client)

    conn = sqlite3.connect(database.DB_PATH)

    conn.execute(
        "UPDATE photos SET uploaded_at = datetime('now', '-31 days')"
    )

    conn.commit()
    conn.close()

    deleted = cleanup.delete_old_photos()

    assert deleted == 1
    assert len(list(client.uploads.iterdir())) == 0