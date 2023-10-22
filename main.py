import imaplib
import email
from email.header import decode_header

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

# Print email details
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