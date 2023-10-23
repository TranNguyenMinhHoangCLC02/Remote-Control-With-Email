from smtplib import SMTP_SSL, SMTP_SSL_PORT
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from PIL import ImageGrab  # Import ImageGrab for local screenshot capture
from appController import AppController  # Import the AppController class

SMTP_HOST = 'smtp.gmail.com'
SMTP_USER = 'tnmhoang.lop93@gmail.com'
SMTP_PASS = 'ijjm pypm pmly hmqm'
FROM_EMAIL = 'tnmhoang.lop93@gmail.com'  # Update the from email address

def send_email(subject, body, recipient_email, attachment_path=None):
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Attach text content
    text = MIMEText(body, 'plain')
    msg.attach(text)

    # Attach the screenshot or any other attachment
    if attachment_path:
        with open(attachment_path, 'rb') as attachment_file:
            attachment = MIMEImage(attachment_file.read(), name='screenshot.png')
            msg.attach(attachment)

    # Connect, authenticate, and send mail
    smtp_server = SMTP_SSL(SMTP_HOST, port=SMTP_SSL_PORT)
    smtp_server.set_debuglevel(1)  # Show SMTP server interactions
    smtp_server.login(SMTP_USER, SMTP_PASS)
    smtp_server.sendmail(FROM_EMAIL, recipient_email, msg.as_string())

    # Disconnect
    smtp_server.quit()

def send_screenshot_email(recipient_email):
    screenshot_path = 'Assets/screenshot.png'
    screenshot = ImageGrab.grab()
    screenshot.save(screenshot_path)

    subject = "SCREENSHOT"
    body = "This is the screenshot!"

    send_email(subject, body, recipient_email, screenshot_path)

def send_process_email(recipient_email):
    app_controller = AppController()
    formatted_table = app_controller.viewList()

    subject = "LIST OF APPLICATIONS"
    body = formatted_table  # Use the formatted table as the email body

    send_email(subject, body, recipient_email)