# Testing

Run all tests:

    python -m pytest -v

## Result
(paste your pytest output here, for example "15 passed")

## What is tested
- Valid upload, returning visitor
- Wrong PIN rejected and no leftover file
- Missing consent, bad PIN format
- Non-image file, GIF, oversized file, too many files
- PIN hash never returned by /api/photos
- Delete-my-photos (right and wrong PIN)
- Rate limiting after 5 failures
- Five simultaneous uploads all saved
- 30-day auto-delete