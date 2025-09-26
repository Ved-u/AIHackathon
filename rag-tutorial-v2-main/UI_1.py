import streamlit as st
import pyttsx3
import speech_recognition as sr
import os
import threading
import pdfplumber
import re
import spacy
import pytesseract
from pdf2image import convert_from_path
import json
import query_data
import shutil
import Send_Email
import populate_database

# ---------------------- NLP Model ----------------------
nlp = spacy.load("en_core_web_sm")

# ---------------------- Extract Features ----------------------
def extract_features_from_pdf(pdf_file):
    features = {
        "start_date": None,
        "end_date": None,
        "contract_value": None,
        "parties": []
    }

    # Extract text from PDF
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "

    # OCR fallback if no text (scanned PDF)
    if not text.strip():
        images = convert_from_path(pdf_file)
        for img in images:
            text += pytesseract.image_to_string(img)

    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return features

    # Dates
    start_match = re.search(
        r'(?:Start Date|Contract Start Date|Commencement Date|Effective Date)[:\-]?\s*([0-9]{1,2}[A-Za-z]*[ -/]\w+[ -/][0-9]{2,4})',
        text, re.IGNORECASE)
    end_match = re.search(
        r'(?:End Date|Contract End Date|Termination Date|Expiry Date)[:\-]?\s*([0-9]{1,2}[A-Za-z]*[ -/]\w+[ -/][0-9]{2,4})',
        text, re.IGNORECASE)

    if start_match:
        features["start_date"] = start_match.group(1).strip()
    if end_match:
        features["end_date"] = end_match.group(1).strip()

    # Contract Value
    money_match = re.search(r'(?:INR|Rs\.?|USD|EUR|GBP)\s?[0-9,]+(?:\.\d{1,2})?', text, re.IGNORECASE)
    if money_match:
        features["contract_value"] = money_match.group(0)

    # Parties
    party_match = re.findall(r'between\s+(.+?)\s+and\s+(.+?)(?:,|\.|\n)', text, re.IGNORECASE)
    if party_match:
        features["parties"] = list(party_match[0])

    return features

# ---------------------- Session State ----------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "recording" not in st.session_state:
    st.session_state.recording = False

if "bot_speech" not in st.session_state:
    st.session_state.bot_speech = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "email_set" not in st.session_state:
    st.session_state.email_set = False

if "extracted_features" not in st.session_state:
    st.session_state.extracted_features = {}

INPUT_FILE = "user_input.txt"
OUTPUT_FILE = "bot_output.txt"

for file in [INPUT_FILE, OUTPUT_FILE]:
    if not os.path.exists(file):
        open(file, "w").close()

# ---------------------- Helper Functions ----------------------
def save_user_input(text):
    with open(INPUT_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def save_bot_output(text):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def recognize_speech():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=3, phrase_time_limit=5)
        text = r.recognize_google(audio)
        return text
    except Exception:
        return None

def speak(text):
    def _speak():
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"TTS Error: {e}")

    if st.session_state.bot_speech:
        threading.Thread(target=_speak, daemon=True).start()

# ---------------------- Handle Message ----------------------
def handle_message(message: str):
    if not message.strip():
        return

    save_user_input(message)
    st.session_state.chat_history.append(("user", message))

    with st.spinner("🤖 Bot is generating response..."):
        # Bot response logic
        bot_reply = ""
        if "contract" in message.lower() and st.session_state.extracted_features:
            bot_reply = f"Here are the extracted contract details:\n{json.dumps(st.session_state.extracted_features, indent=2)}"
        else:
            # Use your RAG model query
            bot_reply = query_data.query_rag(message)

    save_bot_output(bot_reply)
    st.session_state.chat_history.append(("bot", bot_reply))
    speak(bot_reply)

# ---------------------- Streamlit UI ----------------------
st.set_page_config(layout="wide")
st.title("📑 Unity - Contract Chatbot")

# Sidebar
with st.sidebar:
    st.header("📂 Upload Contract")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_pdf:
        dest_folder = r"C:\Users\vedan\OneDrive\Desktop\Hackathon\AIHackathon\rag-tutorial-v2-main\data"
        os.makedirs(dest_folder, exist_ok=True)

        file_name = uploaded_pdf.name
        dest_path = os.path.join(dest_folder, file_name)

        with open(dest_path, "wb") as f:
            f.write(uploaded_pdf.read())

        st.success(f"Uploaded: {file_name}")

        # Extract features
        st.session_state.extracted_features = extract_features_from_pdf(dest_path)

        # # Display key features (only if available)
        # st.subheader("📝 Extracted Features")
        # features = st.session_state.extracted_features

        # if features.get("start_date"):
        #     st.markdown(f"*Start Date:* {features.get('start_date')}")
        # if features.get("end_date"):
        #     st.markdown(f"*End Date:* {features.get('end_date')}")
        # if features.get("contract_value"):
        #     st.markdown(f"*Contract Value:* {features.get('contract_value')}")
        # if features.get("parties"):
        #     st.markdown(f"*Parties:* {features.get('parties')}")

    # Email
    if not st.session_state.email_set:
        st.header("📧 Email")
        name_input = st.text_input("Enter your name (one time):")
        email_input = st.text_input("Enter your email (one time):")

        if st.button("Save Email"):
            if email_input:
                st.session_state.user_email = email_input
                st.session_state.email_set = True
                st.success("Email saved!")
                Send_Email.add_contract_and_notify(name_input, email_input)
                st.rerun()
    else:
        st.success(f"Email: {st.session_state.user_email}")

    # Voice input
    st.header("🎙️ Voice Input")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎤 Start Recording", disabled=st.session_state.recording):
            st.session_state.recording = True
            st.rerun()
    with col2:
        if st.button("🛑 Stop Recording", disabled=not st.session_state.recording):
            st.session_state.recording = False
            st.rerun()

    if st.session_state.recording:
        st.warning("🔴 Recording... Speak now!")
        speech_text = recognize_speech()
        if speech_text:
            st.session_state.recording = False
            handle_message(speech_text)
            st.rerun()
    else:
        st.info("⚫ Ready to record")

    # Bot voice
    st.header("🔊 Bot Voice Response")
    st.session_state.bot_speech = st.checkbox("Enable Bot Voice Output", value=st.session_state.bot_speech)

    # Display key features (only if available)
    st.subheader("📝 Extracted Features")
    features = st.session_state.extracted_features

    if features.get("start_date"):
        st.markdown(f"*Start Date:* {features.get('start_date')}")
    if features.get("end_date"):
        st.markdown(f"*End Date:* {features.get('end_date')}")
    if features.get("contract_value"):
        st.markdown(f"*Contract Value:* {features.get('contract_value')}")
    if features.get("parties"):
        st.markdown(f"*Parties:* {features.get('parties')}")
# Main chat area
st.subheader("💬 Conversation")
for sender, message in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"👤 You: *{message}*")
    else:
        st.markdown(f"*🤖 Bot:* {message}")

# Input form
with st.form(key="message_form", clear_on_submit=True):
    user_input = st.text_input("Enter your message:", placeholder="Type your message...")
    submit_button = st.form_submit_button("Send")
    if submit_button and user_input:
        handle_message(user_input)
        st.experimental_rerun()
