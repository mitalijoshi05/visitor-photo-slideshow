# Assumptions

## Slideshow
- Each photo is shown for 5 seconds by default. The duration can be changed using the SLIDE_DURATION_SECONDS environment variable.
- A new upload plays immediately, then the slideshow goes back to the normal loop.
- The display screen is a web page opened in a browser on the TV or computer, in fullscreen.

## Returning visitors
- A visitor is identified by their name and a 4-digit PIN chosen on their first visit.
- Names are unique. If a name is already taken, the visitor must enter the correct PIN to continue as that person, or choose a different name.
- Name alone is not enough because two people can share a name.
- The PIN is stored as a salted hash, never as plain text.
- No email or phone number is collected.

## Privacy and consent
- Visitors must tick a consent checkbox before uploading: "I agree my photos will be shown on a public screen."
- A visitor can delete all their photos using their name and PIN.
- Photos are automatically deleted after 30 days.

## File validation and limits
- Allowed formats: JPG, PNG, WebP.
- Maximum 5 MB per photo, maximum 5 photos per upload.
- File type is checked from the actual file content, not only the extension.
- Images are resized to a maximum of 1920px so the TV loads them quickly.
- Photos are re-saved as JPEG, which removes EXIF data such as GPS location.

## Concurrent uploads
- Multiple visitors can upload at the same time.
- New photos are added to a priority queue and played in the order they are received by the display.

## Scope
- No admin panel is included in the first version.
- The app runs on a local network or one deployed server, with SQLite as the database.
- Deleting a visitor's photos also deletes their visitor record, making that name available again.
- Wrong PIN attempts are limited to 5 failures in 15 minutes per IP address and per name.
- Rate-limit counters are stored in memory and reset when the server restarts.
- Rate-limit keys use lowercase names, while the database treats names with different capitalization as different names.
- The display shows the visitor's name as a caption.
- Photos older than 30 days are deleted automatically; the cleanup task checks every 6 hours.