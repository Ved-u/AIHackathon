import streamlit as st
import pyttsx3
import speech_recognition as sr
import os
import threading

# ✅ Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# File paths
INPUT_FILE = "input.txt"
OUTPUT_FILE = "output.txt"

# Ensure files exist
for file in [INPUT_FILE, OUTPUT_FILE]:
    if not os.path.exists(file):
        open(file, "w").close()


# Save text to file
def save_to_file(file_path, text):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(text + "\n")


# Speech recognition
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Speak now")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "❌ Could not understand audio."
    except sr.RequestError:
        return "❌ Speech service unavailable."


# Text-to-speech (safe in Streamlit)
def speak(text):
    def _speak():
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"TTS Error: {e}")

    threading.Thread(target=_speak, daemon=True).start()


# ---------------------- UI ----------------------
st.set_page_config(layout="wide")
st.title("📑 Contract Analyzer Chatbot")

# Sidebar (Left side UI)
with st.sidebar:
    st.header("📂 Upload Contract")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_pdf:
        st.success(f"Uploaded: {uploaded_pdf.name}")

    st.header("🎙 Speech Input")
    if st.button("Start Recording"):
        speech_text = recognize_speech()
        if speech_text:
            save_to_file(INPUT_FILE, "USER: " + speech_text)
            st.session_state.chat_history.append(("user", speech_text))

            bot_reply = f"Bot understood: {speech_text}"
            save_to_file(OUTPUT_FILE, "BOT: " + bot_reply)
            st.session_state.chat_history.append(("bot", bot_reply))
            speak(bot_reply)

# Main content (Middle section)
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("💬 Conversation")

    for sender, message in st.session_state.chat_history:
        if sender == "user":
            st.markdown(
                f"<div style='background-color:#ffffff; color:#000000; padding:8px; "
                f"border-radius:8px; margin-bottom:5px'><b>You:</b> {message}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div style='background-color:#e6e6e6; color:#000000; padding:8px; "
                f"border-radius:8px; margin-bottom:5px'><b>Bot:</b> {message}</div>",
                unsafe_allow_html=True
            )

    # Input box at bottom
    user_input = st.text_input("✏️ Enter your message:")
    if st.button("Send"):
        if user_input:
            save_to_file(INPUT_FILE, "USER: " + user_input)
            st.session_state.chat_history.append(("user", user_input))

            bot_reply = f"Bot reply to: {user_input}"
            save_to_file(OUTPUT_FILE, "BOT: " + bot_reply)
            st.session_state.chat_history.append(("bot", bot_reply))
            speak(bot_reply)
