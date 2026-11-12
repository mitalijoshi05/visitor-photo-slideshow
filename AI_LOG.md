# AI Log

## Entry 1: Understanding the assignment
Prompt: Asked AI to explain the assignment in simple language and give a step-by-step plan.
Result: It suggested Node + Express + SQLite.
My decision: Changed to Python + FastAPI + SQLite because I am more comfortable with Python.

## Entry 2: Database design
Prompt: Asked AI to design the database for visitors and photos.
Result: Two tables, visitors and photos, linked by visitor_id with ON DELETE CASCADE.
My decision: Kept UNIQUE(name) and documented it in ASSUMPTIONS.md.

## Entry 3 (AI mistake): Swagger could not upload files
Prompt: Asked AI for a POST /upload endpoint and was told to test it in /docs.
Problem: In /docs the "photos" field showed as a text box, not a file picker. Server returned 422 "Expected UploadFile, received str".
How I noticed: The error message and my screenshot.
Fix: Built a real HTML upload form and tested through it.

## Entry 4 (AI mistake): Orphan files on failed upload
Prompt: Asked AI for the upload endpoint with validation and PIN check.
Problem: AI saved photos to disk first and checked the PIN afterwards. A wrong PIN left unused files in uploads/.
How I noticed: AI warned about it, and I confirmed by counting files in uploads/ before and after a wrong-PIN upload.
Fix: Added cleanup that deletes saved files on wrong PIN and on failed validation. Added a test for it.

## Entry 5 (AI mistake): Photos appeared late
Prompt: Asked AI to build the display page.
Problem: It used polling every 5 seconds, so a new photo took up to 10 seconds. The assignment says "as soon as an upload completes".
How I noticed: Uploaded a photo while watching /display.
Fix: Added Server-Sent Events (/events). Kept a 60 second refresh as backup.

## Entry 6 (AI gap): No limit on PIN guessing
Problem: Upload and delete accepted unlimited wrong PINs. A 4-digit PIN has only 10,000 combinations.
How I noticed: Reviewed the delete feature and asked who could misuse it.
Fix: Added in-memory rate limiting (5 failures in 15 minutes, per IP and per name).

## Entry 7 (AI gap): Promise with no code
Problem: ASSUMPTIONS.md said photos are deleted after 30 days but nothing did it.
How I noticed: Compared my assumptions with the code.
Fix: Added a background cleanup task and a test that fakes an old photo.

## Entry 8 (AI mistake): Wrong Python environment
Problem: pytest said "collected 0 items" and used Anaconda's Python instead of my venv.
How I noticed: The test output showed /opt/anaconda3/bin/python and (base) in the prompt.
Fix: Ran conda deactivate, activated venv, and used python -m pytest.