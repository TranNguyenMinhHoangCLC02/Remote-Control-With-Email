import tkinter as tk
from tkinter import ttk
from threading import Thread
import time
import imaplib
import email
from email.header import decode_header
import re
from bs4 import BeautifulSoup
import sendMail
import powerController

class EmailProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Processing App")
        self.is_running = False
        self.is_first_run = True  # Flag to indicate the first run
        self.progress_value = 0

        # Create GUI elements
        self.start_stop_button = tk.Button(root, text="Start", command=self.toggle_processing)
        self.start_stop_button.pack(pady=20)

        self.progress_label = tk.Label(root, text="Command Progress:")
        self.progress_label.pack()

        self.progress_bar = ttk.Progressbar(root, length=200, mode="determinate")
        self.progress_bar.pack()

        self.command_label = tk.Label(root, text="Command: ")
        self.command_label.pack()

    def toggle_processing(self):
        if not self.is_running:
            self.start_processing()
        else:
            self.stop_processing()

    def start_processing(self):
        self.is_running = True
        self.start_stop_button.config(text="Stop")
        # Start a new thread to run the email processing in the background
        thread = Thread(target=self.process_emails)
        thread.start()

    def stop_processing(self):
        self.is_running = False
        self.progress_value = 0
        self.progress_bar["value"] = 0
        self.command_label.config(text="Command: ")
        self.start_stop_button.config(text="Start")

    def update_progress(self, value, command):
        self.progress_value = value
        self.progress_bar["value"] = self.progress_value
        self.command_label.config(text="Command: " + command)

    def process_emails(self):
        if self.is_first_run:
            # Set the flag to indicate that the first run is complete
            self.is_first_run = False
            # Run the email processing logic
            for i in range(1, 101):
                self.update_progress(i, "Executing Command")
                time.sleep(0.1)
            # Gmail account credentials
            username = "2d2h.computernetwork.clc.fitus@gmail.com"
            password = "jvys wjpg mmmx belp"

            # Create an IMAP4 class with SSL
            imap = imaplib.IMAP4_SSL("imap.gmail.com")

            # Authenticate
            imap.login(username, password)

            # Select the mailbox (inbox in this case)
            imap.select("inbox")

            # Search for all emails and retrieve the latest one
            status, email_ids = imap.search(None, "UNSEEN")
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
            for i in range(1, 101):
                self.update_progress(i, "Executing Command")
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

            if body.find("ListApp", start, end) != -1:
                sendMail.send_process_email(sender_email)

            if body.find("Screenshot", start, end) != -1:
                sendMail.send_screenshot_email(sender_email)

            if body.find("Shut Down", start, end) != -1:
                power_controller = powerController.powerController()
                power_controller.shutdown()

            if body.find("Log out", start, end) != -1:
                power_controller = powerController.powerController()
                power_controller.logout()
                
            if body.find("ListProcess", start, end) != -1:
                sendMail.send_bgProcess_email(sender_email)
                
            if body.find("StartProcess", start, end) != -1:
                start_process_string = "StartProcess Name="
                start_index = body.find(start_process_string)
                if start_index != -1:
                    procName_start = start_index + len(start_process_string)
                    procName_end = body.find("\n", procName_start)
                    
                    if procName_end != -1:
                        procName = body[procName_start:procName_end].strip()
                        procName = BeautifulSoup(procName, "html.parser").text      # Remove HTML tags
                        sendMail.send_startProc_status(sender_email, procName)
                        
            if body.find("EndProcess", start, end) != -1:
                end_process_string = "EndProcess Name="
                start_index = body.find(end_process_string)
                if start_index != -1:
                    procName_start = start_index + len(end_process_string)
                    procName_end = body.find("\n", procName_start)
                    
                    if procName_end != -1:
                        procName = body[procName_start:procName_end].strip()
                        procName = BeautifulSoup(procName, "html.parser").text      # Remove HTML tags
                        sendMail.send_endProc_status(sender_email, procName)

            if body.find("StartApp", start, end) != -1:
                appName_start = body.find("Name=", start, end)
                if appName_start != -1:
                    appName_start += len("Name=")
                    appName_end = body.find("\n", appName_start, end)

                    if appName_end != -1:
                        appName = body[appName_start:appName_end]
                        appName = BeautifulSoup(appName, "html.parser").text      # Remove HTML tags
                        appName = appName.strip()
                        sendMail.send_startApp(sender_email, appName) 

            if body.find("EndApp", start, end) != -1:
                appName_start = body.find("Name=", start, end)
                if appName_start != -1:
                    appName_start += len("Name=")
                    appName_end = body.find("\n", appName_start, end)

                    if appName_end != -1:
                        appName = body[appName_start:appName_end]
                        appName = BeautifulSoup(appName, "html.parser").text      # Remove HTML tags
                        appName = appName.strip()
                        sendMail.send_endApp(sender_email, appName) 
            imap.logout()
            self.stop_processing()
            self.progress_value = 0
            self.progress_bar["value"] = 0
            self.command_label.config(text="Command: ")
            time.sleep(5)  # Adjust the interval as needed
            self.progress_bar.start()
            self.start_stop_button.config(text="Start", state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = EmailProcessingApp(root)
    root.mainloop()
