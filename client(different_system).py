import socket
import pyaudio
import threading
from tkinter import *

# Audio Stream (PyAudio) Initialization
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 10240

# Server connection settings
HOST = '192.168.43.86'  # Server IP address
PORT = 1234

print("Connected to server:- ",HOST,PORT)
class AudioClient:
    def __init__(self, master):
        self.master = master
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
                                  frames_per_buffer=CHUNK, output=True)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))

        self.is_muted = True  # Start with muted microphone
        self.create_widgets()

        # Start the thread for receiving and playing audio
        self.receive_thread = threading.Thread(target=self.receive_audio)
        self.receive_thread.start()

    def create_widgets(self):
        self.speak_button = Button(self.master, text="Hold to Speak", command=self.toggle_mute)
        self.speak_button.pack()

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        if not self.is_muted:
            # Start speaking (sending audio)
            self.send_audio_thread = threading.Thread(target=self.send_audio)
            self.send_audio_thread.start()
        # If muted, the send_audio thread will automatically stop because is_muted becomes True

    def send_audio(self):
        while not self.is_muted:
            try:
                data = self.stream.read(CHUNK, exception_on_overflow=False)
                self.socket.sendall(data)
            except IOError as e:
                print(e)

    def receive_audio(self):
        while True:
            try:
                data = self.socket.recv(CHUNK)
                if data:
                    # Check if the data is a control message (simple example)
                    try:
                        message = data.decode()
                        if message == "No other clients connected.":
                            print(message)  # Or update the GUI accordingly
                    except UnicodeDecodeError:
                        # Data is not a text message, so play it as audio
                        self.stream.write(data)
            except IOError as e:
                print(e)


    def on_closing(self):
        self.socket.close()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.master.destroy()

if __name__ == "__main__":
    root = Tk()
    root.title("Client")
    client = AudioClient(master=root)
    root.protocol("WM_DELETE_WINDOW", client.on_closing)
    root.mainloop()
