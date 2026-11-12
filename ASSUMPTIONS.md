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
- Names are unique. If a name is already taken, the visitor must enter their PIN to continue as that person, or choose a different name.

## Added during development
- Names are unique. If a name is taken, the visitor must enter the correct PIN, or choose another name.
- Deleting photos also deletes the visitor record. The name becomes free again.
- Wrong PIN attempts are limited: 5 failures in 15 minutes per IP and per name.
- Rate limit counters are in memory and reset on server restart.
- Photos older than 30 days are deleted automatically (checked every 6 hours).
- Rate limit keys use lowercase names, while the database treats "Mitali" and "mitali" as different names.
- Photos are re-saved as JPEG, which removes EXIF data such as GPS location.
- The display shows the visitor's name as a caption.s