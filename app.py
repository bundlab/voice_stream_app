import pyttsx3
import threading
import time

# Initialize the speech engine
engine = pyttsx3.init()

# Text lines to print and speak
lines = [
    "Hello, this is a live speaking text printer.",
    "This app prints and speaks text continuously.",
    "You can modify the text list to include your own content.",
    "Python makes it easy to combine speech and printing.",
    "Thanks for using this demo!"
]

def speak_text():
    for line in lines:
        engine.say(line)
        engine.runAndWait()
        time.sleep(0.5)

def print_text():
    for line in lines:
        print(line)
        time.sleep(0.5)

# Create threads
speak_thread = threading.Thread(target=speak_text)
print_thread = threading.Thread(target=print_text)

# Start threads
speak_thread.start()
print_thread.start()

# Wait for both threads to complete
speak_thread.join()
print_thread.join()
