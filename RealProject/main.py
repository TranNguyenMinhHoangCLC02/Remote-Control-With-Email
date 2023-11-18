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
import readMail

class EmailProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Processing App")
        self.is_running = False
        self.is_first_run = True  # Flag to indicate the first run
        self.progress_value = 0

        # Create GUI elements
        self.start_stop_button = tk.Button(root, text="Start", command=self.process_emails)
        self.start_stop_button.pack(pady=20)

        self.progress_label = tk.Label(root, text="Command Progress:")
        self.progress_label.pack()

        self.progress_bar = ttk.Progressbar(root, length=200, mode="determinate")
        self.progress_bar.pack()

        self.command_label = tk.Label(root, text="Command: ")
        self.command_label.pack()

    def process_emails(self):
        if not self.is_running:
            self.is_running = True
            self.start_stop_button.config(text="Processing...", state=tk.DISABLED)  # Disable the button
            # Start a new thread to run the email processing in the background
            thread = Thread(target=self.process_emails_thread)
            thread.start()

    def process_emails_thread(self):
        # Run the email processing logic
        for i in range(1, 101):
            self.update_progress(i, "Executing Command")
            time.sleep(0.1) # Simulate work

        # Call the read_email() function here
        readMail.read_email()

        self.update_progress(0, "Command Complete")
        self.stop_processing()

    def stop_processing(self):
        self.is_running = False
        self.progress_value = 0
        self.progress_bar["value"] = 0
        self.command_label.config(text="Command: ")
        self.start_stop_button.config(text="Start", state=tk.NORMAL)  # Enable the button

    def update_progress(self, value, command):
        self.progress_value = value
        self.progress_bar["value"] = self.progress_value
        self.command_label.config(text="Command: " + command)


if __name__ == "__main__":
    root = tk.Tk()
    app = EmailProcessingApp(root)
    root.mainloop()
