
import pytest
from fastapi.testclient import TestClient

from app import database, images, main, cleanup, ratelimit


@pytest.fixture
def client(tmp_path, monkeypatch):

    # Create a separate temporary database for every test
    test_db = tmp_path / "test.db"
    test_uploads = tmp_path / "uploads"

    test_uploads.mkdir()

    # Redirect application files to temporary test locations
    monkeypatch.setattr(database, "DB_PATH", test_db)
    monkeypatch.setattr(images, "UPLOAD_DIR", test_uploads)
    monkeypatch.setattr(main, "UPLOAD_DIR", test_uploads)
    monkeypatch.setattr(cleanup, "UPLOAD_DIR", test_uploads)

    monkeypatch.setattr(
        main,
        "MAX_FILE_SIZE_BYTES",
        images.MAX_FILE_SIZE_BYTES
    )

    # Clear previous rate-limit attempts
    ratelimit._failures.clear()

    # Start the application and its lifespan
    with TestClient(main.app) as test_client:
        test_client.uploads = test_uploads
        yield test_client

    # Clean rate-limit state after testing
    ratelimit._failures.clear()
