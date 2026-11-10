# Assumptions

## Slideshow
- Each photo is shown for 5 seconds (configurable via SLIDE_DURATION_SECONDS).
- A new upload plays immediately, then the slideshow goes back to the normal loop.
- The display screen is just a web page opened in a browser on the TV or computer, in fullscreen.

## Returning visitors
- A visitor is identified by name + a 4-digit PIN chosen at first visit.
- Name alone is not enough, because two people can share a name.
- PIN is stored hashed, never as plain text.
- No email or phone number is collected.

## Privacy and consent
- Visitor must tick a consent checkbox before uploading: "I agree my photos will be shown on a public screen."
- A visitor can delete all their photos using name + PIN.
- Photos are automatically deleted after 30 days.

## File validation and limits
- Allowed formats: JPG, PNG, WebP.
- Maximum 5 MB per photo, maximum 5 photos per upload.
- File type is checked from the real file content, not only the extension.
- Images are resized to a maximum of 1920px so the TV loads them fast.

## Concurrent uploads
- Many people can upload at the same time.
- New photos go into a queue and play in the order they were uploaded.

## Scope
- No admin panel in the first version.
- The app runs on a local network or one deployed server, with SQLite as the database.