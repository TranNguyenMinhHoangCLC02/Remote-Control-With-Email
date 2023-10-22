from smtplib import SMTP_SSL, SMTP_SSL_PORT
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from PIL import ImageGrab  # Import ImageGrab for local screenshot capture
import os, signal
import subprocess
import json

SMTP_HOST = 'smtp.gmail.com'
SMTP_USER = 'tnmhoang.lop93@gmail.com'
SMTP_PASS = 'ijjm pypm pmly hmqm'

choice = input("1. Screenshot, 2. List App")

# Craft the email by hand
#to_emails = input('Input email: ')
to_emails = 'dophantuandat@gmail.com'
subject = input('Input subject: ')
body = input('Input body: ')

from_email = 'Tran Nguyen Minh Hoang'  # or simply the email address

if choice == '1':
    # Take a local screenshot using Pillow's ImageGrab
    screenshot_path = './Images/screenshot.png'
    screenshot = ImageGrab.grab()
    screenshot.save(screenshot_path)

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_emails
    msg['Subject'] = subject

    # Attach text content
    text = MIMEText(body, 'plain')
    msg.attach(text)

    # Attach the screenshot as an image
    with open(screenshot_path, 'rb') as image_file:
        image = MIMEImage(image_file.read(), name='screenshot.png')
        msg.attach(image)

    # Connect, authenticate, and send mail
    smtp_server = SMTP_SSL(SMTP_HOST, port=SMTP_SSL_PORT)
    smtp_server.set_debuglevel(1)  # Show SMTP server interactions
    smtp_server.login(SMTP_USER, SMTP_PASS)
    smtp_server.sendmail(from_email, to_emails, msg.as_string())

    # Disconnect
    smtp_server.quit()  

class AppController():
    def process2List(self,processes):
        a = processes.decode().strip()
        b = a.split("\r\n")
        b = [" ".join(x.split()) for x in b]
        c = [x.split() for x in b][2:]
        return c

    def viewList(self):
        app = subprocess.check_output(
            "powershell gps | where {$_.MainWindowTitle} | \
            select Name,Id,@{Name='ThreadCount';Expression={$_.Threads.Count}}",
            stdin=subprocess.PIPE, stderr=subprocess.PIPE)

        self.appList = self.process2List(app)

        dataToSend = json.dumps(self.appList).encode('utf-8') 
        print(dataToSend)
        return dataToSend
if choice == '2':
    app_controller = AppController()
    data = str(app_controller.viewList())
    print(type(data))
    headers = f"From: {from_email}\r\n"
    headers += f"To: {to_emails}\r\n" 
    headers += f"Subject: Hello\r\n"
    body += data
    email_message = headers + "\r\n" + body + "\r\n" + data # Blank line needed between headers and body

    # Connect, authenticate, and send mail
    smtp_server = SMTP_SSL(SMTP_HOST, port=SMTP_SSL_PORT)
    smtp_server.set_debuglevel(1)  # Show SMTP server interactions
    smtp_server.login(SMTP_USER, SMTP_PASS)
    smtp_server.sendmail(from_email, to_emails, email_message)

    # Disconnect
    smtp_server.quit()



