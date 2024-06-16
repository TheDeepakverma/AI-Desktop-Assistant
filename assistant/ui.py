from tkinter import ttk
import threading
import queue
from ttkthemes import ThemedTk
from assistant.core import listen, handle_command, alarm_time
from PIL import Image, ImageTk

class AssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Desktop Assistant")
        self.root.geometry("500x500")

        self.label = ttk.Label(root, text="Press the button and speak", font=("Helvetica", 16))
        self.label.pack(pady=20)

        # Load and resize icon image
        self.mic_icon = Image.open("assets/mic_icon.png")  # Replace with your icon path
        self.mic_icon = self.mic_icon.resize((25, 25), Image.LANCZOS)  # Resize the icon using LANCZOS filter
        self.mic_icon = ImageTk.PhotoImage(self.mic_icon)

        self.listen_button = ttk.Button(root, text=" Listen", command=self.start_listening, style='TButton', image=self.mic_icon, compound="left")
        self.listen_button.pack(pady=20)

        self.response_label = ttk.Label(root, text="", font=("Helvetica", 14), wraplength=400, justify="center")
        self.response_label.pack(pady=20)

        self.queue = queue.Queue()
        self.check_queue()

        self.status_label = ttk.Label(root, text="", font=("Helvetica", 10), foreground="gray")
        self.status_label.pack(pady=10)

        self.check_alarm_button = ttk.Button(root, text="Check Alarm", command=self.check_alarm_status)
        self.check_alarm_button.pack(pady=20)

    def start_listening(self):
        self.status_label.config(text="Listening...")
        threading.Thread(target=self.listen).start()

    def listen(self):
        query = listen()
        if query != "None":
            self.queue.put(f"You said: {query}")
            handle_command(query)
        else:
            self.queue.put("Sorry, I did not catch that. Please try again.")
        self.status_label.config(text="")

    def check_queue(self):
        try:
            while True:
                message = self.queue.get_nowait()
                self.response_label.config(text=message)
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)

    def check_alarm_status(self):
        if alarm_time:
            alarm_time_str = alarm_time.strftime("%H:%M")
            self.status_label.config(text=f"Alarm set for {alarm_time_str}")
        else:
            self.status_label.config(text="No alarm set.")

if __name__ == "__main__":
    root = ThemedTk(theme="arc")  # Initialize ThemedTk with the desired theme
    app = AssistantApp(root)
    root.mainloop()
