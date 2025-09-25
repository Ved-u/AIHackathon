import streamlit as st
import pyttsx3
import speech_recognition as sr
import os
import threading
import pdfplumber
import re
import spacy
import json
import query_data
import shutil
import Send_Email
import populate_database

# ---------------------- NLP Model ----------------------
nlp = spacy.load("en_core_web_sm")

# ---------------------- Feature Extraction ----------------------
def extract_features_from_pdf(pdf_file):
    features = {}
    text = ""

    # Extract text from PDF
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    text = text.strip()
    features['raw_text'] = text

    # Handle empty PDF
    if not text:
        features.update({
            "dates": [],
            "start_date": None,
            "end_date": None,
            "parties": [],
            "contract_value": None,
            "clauses": [],
            "organizations": [],
            "money": []
        })
        return features

    # Clean text
    clean_text = re.sub(r'\s+', ' ', text)

    # Extract dates
    date_pattern = r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|(?:\d{1,2}\s+[A-Za-z]+\s+\d{4})|(?:[A-Za-z]+\s+\d{1,2},\s*\d{4}))\b'
    features['dates'] = re.findall(date_pattern, text, flags=re.IGNORECASE)

    # Start / End date
    start_match = re.search(r'Contract Start Date[:\-]?\s*([^\n]+)', text, re.IGNORECASE)
    end_match = re.search(r'Contract End Date[:\-]?\s*([^\n]+)', text, re.IGNORECASE)
    features['start_date'] = start_match.group(1).strip() if start_match else None
    features['end_date'] = end_match.group(1).strip() if end_match else None

    # Parties
    parties = []
    party_match = re.search(r'between\s+(.+?)\s+and\s+(.+?)[,\.]', text, flags=re.IGNORECASE)
    if party_match:
        parties.extend([party_match.group(1).strip(), party_match.group(2).strip()])
    features['parties'] = list(set(parties))

    # Contract value
    money_pattern = r'(?:INR|USD|Rs\.?)\s?[0-9,]+'
    contract_value = re.search(money_pattern, text)
    features['contract_value'] = contract_value.group(0) if contract_value else None

    # Clauses
    clause_pattern = r'(Section\s+\d+:\s+[^\n]+)'
    clauses = re.findall(clause_pattern, text, flags=re.IGNORECASE)
    features['clauses'] = clauses[:5]

    # NLP entities
    doc = nlp(text)  # Ensure doc is always defined
    features['organizations'] = list(set(ent.text for ent in doc.ents if ent.label_ == "ORG"))
    features['money'] = list(set(ent.text for ent in doc.ents if ent.label_ == "MONEY"))

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

def handle_message(message: str):
    if not message.strip():
        return

    save_user_input(message)
    st.session_state.chat_history.append(("user", message))

    # Bot response logic
    # if "contract" in message.lower() and st.session_state.extracted_features:
    #     bot_reply = f"Here are the extracted contract details:\n{json.dumps(st.session_state.extracted_features, indent=2)}"
    # else:
    #     bot_reply = f"Bot response to: {message}"
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
        dest_folder = r"C:\Vedant\CS\Projects\GitHub\AI-Hackathon\AIHackathon\rag-tutorial-v2-main\data"
        os.makedirs(dest_folder, exist_ok=True)

        # Save uploaded file
        file_name = uploaded_pdf.name
        dest_path = os.path.join(dest_folder, file_name)
        
        # Save uploaded file to dest_path
        with open(dest_path, "wb") as f:
            f.write(uploaded_pdf.read())

        st.success(f"Uploaded: {file_name}")
        populate_database.load()

        # Extract features
        st.session_state.extracted_features = extract_features_from_pdf(dest_path)

        # Display key features
        st.subheader("📝 Extracted Features")
        features = st.session_state.extracted_features
        st.markdown(f"*Start Date:* {features.get('start_date')}")
        st.markdown(f"*End Date:* {features.get('end_date')}")
        st.markdown(f"*Parties:* {', '.join(features.get('parties', []))}")
        st.markdown(f"*Contract Value:* {features.get('contract_value')}")
        st.markdown("*Clauses:*")
        for clause in features.get('clauses', []):
            st.markdown(f"- {clause}")

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
        st.rerun()
