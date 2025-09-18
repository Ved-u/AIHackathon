import tkinter as tk
from tkinter import filedialog, ttk
import threading
import speech_recognition as sr
from datetime import datetime

# ---------- Global Variables ----------
recognizer = sr.Recognizer()
mic = sr.Microphone()
recording = False
stop_thread = False
last_recognized_text = ""  # Store last recognized speech
typing_label = None
mic_animation_job = None


# ---------- Helper: Save logs ----------
def save_to_file(sender, message, filename="chat_log.txt"):
    """Save a message to a file."""
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{sender.upper()} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}): {message}\n")


# ---------- Functions ----------
def upload_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        add_message(f"📄 PDF Uploaded:\n{file_path}", sender="bot")
        save_to_file("bot", f"📄 PDF Uploaded: {file_path}")


def send_message(event=None):
    """Handle user message and display bot response from output.txt"""
    user_input = message_entry.get()
    if user_input.strip():
        # Save user input (overwrite previous content)
        with open("input.txt", "w", encoding="utf-8") as f:
            f.write(user_input)

        # Display user input in chat
        add_message(user_input, sender="user")
        save_to_file("user", user_input)
        message_entry.delete(0, tk.END)

        # Read bot response from output.txt
        try:
            with open("output.txt", "r", encoding="utf-8") as f:
                bot_response = f.read().strip()
                if not bot_response:
                    bot_response = "🤖 No response found in output.txt"
        except FileNotFoundError:
            bot_response = "🤖 output.txt not found."

        # Display bot response
        add_message(bot_response, sender="bot")
        save_to_file("bot", bot_response)


def process_button_action():
    if last_recognized_text:
        bot_message = f"⚡ Processing: {last_recognized_text}"
        add_message(bot_message, sender="bot")
        save_to_file("bot", bot_message)
    else:
        bot_message = "⚠ No speech recognized yet."
        add_message(bot_message, sender="bot")
        save_to_file("bot", bot_message)


def add_message(message, sender="user"):
    """Add a message bubble to the chat"""
    bubble_color = "#D0F0FD" if sender == "user" else "#F0F0F0"
    text_color = "#000000"
    anchor_side = "e" if sender == "user" else "w"

    bubble_frame = tk.Frame(chat_inner_frame, bg="#E8EEF1")
    bubble_frame.pack(fill="x", pady=6, padx=12, anchor=anchor_side)

    timestamp = datetime.now().strftime("%H:%M")
    msg_label = tk.Label(
        bubble_frame,
        text=f"{message}\n{timestamp}",
        bg=bubble_color,
        fg=text_color,
        wraplength=450,
        justify="left",
        anchor=anchor_side,
        padx=12,
        pady=8,
        font=("Segoe UI", 11),
        bd=0,
        relief="solid"
    )
    msg_label.pack(anchor=anchor_side, fill="x")

    chat_canvas.update_idletasks()
    chat_canvas.yview_moveto(1.0)
    return msg_label


# ---------- Speech Recognition Functions ----------
def toggle_recording():
    global recording, stop_thread, mic_animation_job
    if not recording:
        recording = True
        stop_thread = False
        mic_button.config(text="⏹ Stop")
        animate_mic()
        add_message("🎙 Recording... Speak now.", sender="bot")
        save_to_file("bot", "🎙 Recording... Speak now.")
        threading.Thread(target=real_time_listen, daemon=True).start()
    else:
        stop_thread = True
        recording = False
        mic_button.config(text="🎤 Start", bg="#4CAF50")
        if mic_animation_job:
            root.after_cancel(mic_animation_job)
        add_message("🎙 Recording stopped.", sender="bot")
        save_to_file("bot", "🎙 Recording stopped.")


def animate_mic(step=0):
    global mic_animation_job
    colors = ["#FF5252", "#FF1744", "#F44336"]
    mic_button.config(bg=colors[step % len(colors)])
    mic_animation_job = root.after(300, animate_mic, step + 1)


def real_time_listen():
    global stop_thread
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        while not stop_thread:
            try:
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
                threading.Thread(target=process_audio, args=(audio,), daemon=True).start()
            except sr.WaitTimeoutError:
                continue


def process_audio(audio):
    global last_recognized_text
    try:
        text = recognizer.recognize_google(audio)
        last_recognized_text = text
        message_entry.delete(0, tk.END)
        message_entry.insert(0, text)
        add_message(f"📝 Recognized: {text}", sender="bot")
        save_to_file("bot", f"📝 Recognized: {text}")
        save_to_file("user", text)
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        add_message("⚠ Speech recognition service unavailable.", sender="bot")
        save_to_file("bot", "⚠ Speech recognition service unavailable.")


# ---------- UI Setup ----------
root = tk.Tk()
root.title("Chatbot UI with File-based Bot Response")
root.geometry("900x650")
root.minsize(700, 500)
root.configure(bg="#E8EEF1")

paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief="raised")
paned.pack(fill=tk.BOTH, expand=True)

# Sidebar
sidebar_frame = tk.Frame(paned, bg="#1E2A38", width=240)
sidebar_frame.pack_propagate(False)

tk.Label(
    sidebar_frame, text="≡", bg="#1E2A38", fg="white",
    font=("Segoe UI", 20, "bold")
).pack(pady=15, anchor="w", padx=15)

tk.Label(
    sidebar_frame, text="CHAT\nBOT", bg="#1E2A38", fg="white",
    font=("Segoe UI", 26, "bold"), justify="left"
).pack(pady=20, anchor="w", padx=15)

btn_style = {
    "font": ("Segoe UI", 12, "bold"),
    "relief": "flat",
    "bd": 0,
    "activebackground": "#303F9F",
    "fg": "white"
}

tk.Button(
    sidebar_frame, text="Upload PDF", bg="#4CAF50",
    command=upload_pdf, **btn_style
).pack(pady=15, padx=20, fill="x")

tk.Button(
    sidebar_frame, text="Process", bg="#3F51B5",
    command=process_button_action, **btn_style
).pack(pady=15, padx=20, fill="x")

paned.add(sidebar_frame, width=240)

# Chat Area
chat_frame = tk.Frame(paned, bg="#E8EEF1")

chat_canvas = tk.Canvas(chat_frame, bg="#E8EEF1", highlightthickness=0)
chat_scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=chat_canvas.yview)
chat_scrollbar.pack(side="right", fill="y")
chat_canvas.pack(side="top", fill="both", expand=True)
chat_canvas.configure(yscrollcommand=chat_scrollbar.set)

chat_inner_frame = tk.Frame(chat_canvas, bg="#E8EEF1")
chat_window = chat_canvas.create_window((0, 0), window=chat_inner_frame, anchor="nw")

chat_inner_frame.bind(
    "<Configure>",
    lambda e: chat_canvas.configure(scrollregion=chat_canvas.bbox("all"))
)

# Bottom Input
bottom_frame = tk.Frame(chat_frame, bg="#FFFFFF", bd=1, relief="solid")
bottom_frame.pack(side="bottom", fill="x", pady=5, padx=5)

message_entry = tk.Entry(
    bottom_frame, font=("Segoe UI", 12),
    relief="flat", bg="#F5F5F5", bd=0
)
message_entry.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=5)
message_entry.bind("<Return>", send_message)

mic_button = tk.Button(
    bottom_frame, text="🎤 Start", font=("Segoe UI", 12, "bold"),
    bg="#4CAF50", fg="white", relief="flat", command=toggle_recording
)
mic_button.pack(side="left", padx=5, pady=5)

send_button = tk.Button(
    bottom_frame, text="➤", font=("Segoe UI", 12, "bold"),
    bg="#2196F3", fg="white", relief="flat", command=send_message
)
send_button.pack(side="right", pady=5)

paned.add(chat_frame)

root.update_idletasks()
paned.sash_place(0, 240, 0)

root.mainloop()
