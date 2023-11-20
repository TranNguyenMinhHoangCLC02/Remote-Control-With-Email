import imaplib
import email
from email.header import decode_header
from threading import Timer
import time 
import keyLog
import sendMail
import re
import powerController
from bs4 import BeautifulSoup

def extract_email_information(raw_email):
    # Parse the email message
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
    return sender_email, body

def key_log(sender_email, body, start, end):
    duration_start = body.find("Duration:", start, end)
    if duration_start != -1:
        duration_start += len("Duration:")  # Move the start index to the character after "Duration:"
        duration_end = body.find("\n", duration_start, end)  # Find the end of the number, which is a newline character
        if duration_end != -1:
            duration_str = body[duration_start:duration_end]  # Extract the substring containing the duration as a string
            # Remove unwanted characters
            duration_str = ''.join(filter(str.isdigit, duration_str))
            duration = int(duration_str)
            sendMail.send_keyLog_email(sender_email, duration)

def get_name_app_or_process(body, stringstart):
    start_index = body.find(stringstart)
    Name = ""
    if start_index != -1:
        name_start = start_index + len(stringstart)
        name_end = body.find("\n", name_start)

        if name_end != -1:
            Name = body[name_start:name_end].strip()
            Name = BeautifulSoup(Name, "html.parser").text      # Remove HTML tags
            Name = Name.strip()
    return Name

def start_process(sender_email, body):
    procName = get_name_app_or_process(body, "StartProcess Name =")
    if procName != "":
        sendMail.send_startProc_status(sender_email, procName)

def end_process(sender_email, body):
    procName = get_name_app_or_process(body, "EndProcess Name =")
    if procName != "":
        sendMail.send_endProc_status(sender_email, procName)

def start_app(sender_email, body):
    appName = get_name_app_or_process(body, "StartApp Name =")
    if appName != "":
        sendMail.send_startApp(sender_email, appName)

def end_app(sender_email, body):
    appName = get_name_app_or_process(body, "EndApp Name =")
    if appName != "":
        sendMail.send_EndApp(sender_email, appName)

def process_email(sender_email, body):
    start = 0  # Define the start position in the string
    end = len(body)  # Define the end position in the string

    if body.find("KeyLog", start, end) != -1:
        key_log(sender_email, body, start, end)
        return "KeyLog"

    if body.find("ListApp", start, end) != -1:
        sendMail.send_process_email(sender_email)
        return "ListApp"

    if body.find("Screenshot", start, end) != -1:
        sendMail.send_screenshot_email(sender_email)
        return "Screenshot"

    if body.find("Shut Down", start, end) != -1:
        power_controller = powerController.powerController()
        power_controller.shutdown()

    if body.find("Log out", start, end) != -1:
        power_controller = powerController.powerController()
        power_controller.logout()

    if body.find("ListProcess", start, end) != -1:
        sendMail.send_bgProcess_email(sender_email)
        return "ListProcess"

    if body.find("StartProcess", start, end) != -1:
        start_process(sender_email, body)
        return "StartProcess"

    if body.find("EndProcess", start, end) != -1:
        end_process(sender_email, body)
        return "EndProcess"

    if body.find("StartApp", start, end) != -1:
        start_app(sender_email, body)
        return "StartApp"

    if body.find("EndApp", start, end) != -1:
        end_app(sender_email, body)
        return "EndApp"

    if body.find("Die", start, end) != -1:
        return "Die"
    
    else: 
        return "Invalid"

def read_email():
    # Gmail account credentials
    username = "2d2h.computernetwork.clc.fitus@gmail.com"
    password = "jvys wjpg mmmx belp"

    # Create an IMAP4 class with SSL
    imap = imaplib.IMAP4_SSL("imap.gmail.com")

    # Authenticate
    imap.login(username, password)

    # Select the mailbox (inbox in this case)
    imap.select("inbox")

    # Search for all unread emails and retrieve the latest one, if none found then exit
    status, email_ids = imap.search(None, 'UNSEEN')
    if not email_ids[0]:
        print("No unread emails found.")
        return "Error"
    latest_email_id = email_ids[0].split()[-1]

    # Fetch the email message by ID
    status, email_data = imap.fetch(latest_email_id, "(RFC822)")

    # Extract email information
    sender_email, body = extract_email_information(email_data[0][1])

    # Process email
    command = process_email(sender_email, body)

    # Close the connection
    imap.logout()
    return command

if __name__ == "__main__":
    # Process the 1st unread email
    read_email()