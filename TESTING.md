# Testing

## How to Run Tests

Run the following command in the terminal:

```bash
python -m pytest -v
```

## Automated Test Results

**Result: 15 passed, 1 warning in 1.18s**

All 15 automated tests passed successfully.

## What Was Tested

1. Valid photo upload.
2. Returning visitor identification.
3. Wrong PIN rejection.
4. Missing consent rejection.
5. Non-image file rejection.
6. GIF file rejection.
7. Oversized image rejection.
8. Uploading more than five photos.
9. Invalid PIN format.
10. PIN hash is not exposed.
11. Visitor can delete their own photos.
12. Wrong PIN deletion rejection.
13. Rate limiting after five failed attempts.
14. Multiple simultaneous uploads.
15. Automatic deletion of photos after 30 days.

## Manual Testing

| Test Case | Result |
|---|---|
| Returning visitor sees previous photos | PASS |
| Multiple visitors' photos appear in slideshow | PASS |
| Photos display for five seconds | PASS |
| Deleted photos disappear from slideshow | PASS |

## Additional Manual Testing

| Test Case | Expected Result | Actual Result |
|---|---|---|
| Upload without consent | Upload rejected | PASS |
| Upload PDF file | File rejected | PASS |
| Upload six photos | Upload rejected | PASS |