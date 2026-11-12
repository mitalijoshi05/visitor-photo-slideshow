# AI Log
## Entry 1: Understanding the assignment
Prompt: Asked AI to explain the assignment in simple language and give a step-by-step plan.
Result: It suggested Node + Express + SQLite.
My decision: I changed the stack to Python + FastAPI + SQLite because I am more comfortable with Python.

## Entry 3: Swagger UI could not upload files
Prompt: Asked AI for a POST /upload endpoint and was told to test it in /docs.
Problem: In /docs the "photos" field showed as a text box, not a file picker.
Server returned 422 "Expected UploadFile, received str".
How I noticed: The error message and the screenshot showed a text input.
Fix: Built a real HTML upload form (Part B) and tested through it instead.
Lesson: Do not trust a testing tool blindly; confirm with a real browser form.

## Entry 4: Orphan files on failed upload
Prompt: Asked AI for the upload endpoint with validation and PIN check.
Problem: AI saved photos to disk first and checked the PIN afterwards. A wrong PIN left unused files in uploads/.
How I noticed: Counted files in uploads/ before and after a wrong-PIN upload.
Fix: Added cleanup (delete saved files) on wrong PIN and on a failed validation.

## Entry 5: Photos appeared late (polling gap)
Prompt: Asked AI to build the display page.
Problem: AI used polling every 5 seconds, so a new photo took up to 10 seconds to appear. The assignment says "as soon as an upload completes".
How I noticed: Uploaded a photo while watching /display and timed the delay.
Fix: Added Server-Sent Events (/events). The server publishes an event after each upload and the display reloads the list immediately. Kept a 60 second refresh as a backup.

## Entry 6: No limit on PIN guessing
Problem: AI's upload and delete endpoints accept unlimited wrong PINs. A 4-digit PIN has only 10,000 combinations, so it can be brute forced.
How I noticed: Reviewed the delete feature while thinking about who could misuse it.
Fix: Planned rate limiting per IP and per name.