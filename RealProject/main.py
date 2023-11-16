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
            # Run the email processing logic
            for i in range(1, 101):
                self.update_progress(i, "Executing Command")
                time.sleep(0.1) # Simulate work
            # Set the flag to indicate that the first run is complete
            self.is_first_run = False
            
            # Call the read_email() function here
            readMail.read_email()
            
            self.update_progress(0, "Command Complete")
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
