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
import random

class TimerApp:
    def __init__(self, root, email_app):
        self.root = root
        self.email_app = email_app
        self.root.title("Timer App")
        self.timer_value = tk.StringVar()
        self.timer_value.set("00:00:00")

        self.timer_label = tk.Label(root, text="Set Timer:")
        self.timer_label.pack()

        self.timer_entry = tk.Entry(root, textvariable=self.timer_value)
        self.timer_entry.pack()

    def start_timer(self):
        timer_value = self.timer_value.get()
        hours, minutes, seconds = map(int, timer_value.split(':'))
        total_seconds = hours * 3600 + minutes * 60 + seconds

        self.timer_entry.config(state=tk.DISABLED)
        self.email_app.process_emails()
        self.update_timer(total_seconds)

    def update_timer(self, remaining_seconds):
        if remaining_seconds >= 0:
            hours = remaining_seconds // 3600
            minutes = (remaining_seconds % 3600) // 60
            seconds = remaining_seconds % 60
            timer_value = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.timer_value.set(timer_value)

            self.root.after(1000, self.update_timer, remaining_seconds - 1)
        else:
            self.timer_entry.config(state=tk.NORMAL)


class EmailProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Processing App")
        self.is_running = False
        self.is_first_run = True  # Flag to indicate the first run
        self.progress_value = 0

        # Create GUI elements
        self.start_stop_button = tk.Button(root, text="Start", command=self.start_timer)
        self.start_stop_button.pack(pady=20)

        self.progress_label = tk.Label(root, text="Command Progress:")
        self.progress_label.pack()

        self.progress_bar = ttk.Progressbar(root, length=200, mode="determinate")
        self.progress_bar.pack()

        self.command_label = tk.Label(root, text="Command: ")
        self.command_label.pack()

        # Create TimerApp instance
        self.timer_app = TimerApp(root, self)

    def start_timer(self):
        self.timer_app.start_timer()

    def process_emails(self):
        if not self.is_running:
            self.is_running = True
            self.start_stop_button.config(text="Processing...", state=tk.DISABLED)  # Disable the button
            # Start a new thread to run the email processing in the background
            thread = Thread(target=self.process_emails_thread)
            thread.start()


    def process_emails_thread(self):
        # Start the timer
        self.start_timer()
        while self.timer_app.timer_value.get() != "00:00:00":
            # Call the read_email() function here
            command = readMail.read_email()
            if command == "Invalid":
                self.update_progress(0, "Invalid")
                continue
            # Run the email processing logic
            for i in range(1, 101):
                self.update_progress(i, "Executing " + command)
                time.sleep(random.uniform(0.01, 0.1))  # Random sleep time between 0.01 and 0.1 seconds

            self.update_progress(0, "Command Complete")
            if command == "Die":
                self.stop_processing()

        self.stop_processing()

    def stop_processing(self):
        self.is_running = False
        self.progress_value = 0
        self.progress_bar["value"] = 0
        self.command_label.config(text="Command: ")
        self.start_stop_button.config(text="Start", state=tk.NORMAL)  # Enable the button
        self.timer_app.timer_value.set("00:00:00")

    def update_progress(self, value, command):
        self.progress_value = value
        self.progress_bar["value"] = self.progress_value
        self.command_label.config(text="Command: " + command)


if __name__ == "__main__":
    root = tk.Tk()
    app = EmailProcessingApp(root)
    root.mainloop()
