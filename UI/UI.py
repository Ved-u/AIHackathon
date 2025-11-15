import streamlit as st
import os
import sys
# Add project root BEFORE importing RAG
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
# Import RAG
from RAG import query_data
from RAG import populate_database
import Send_Email

# Global Variable for path to data folder for storing PDFs
PATH = r"C:\Vedant\CS\Projects\GAP\GAP\AIHackathon\\data"

# ---------------------- Session State ----------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "email_set" not in st.session_state:
    st.session_state.email_set = False

def handle_message(message: str):
    if not message.strip():
        return

    st.session_state.chat_history.append(("user", message))

    with st.spinner("Generating response..."):
        bot_reply = query_data.query_rag(message)  # This might take time

    st.session_state.chat_history.append(("Unity:", bot_reply))
   

# ---------------------- Streamlit UI ----------------------
st.set_page_config(layout="wide")
st.title("📑 Unity - Contract Chatbot")

# Sidebar
with st.sidebar:
    st.header("📂 Upload Contract")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_pdf:
        dest_folder = r""+PATH

        os.makedirs(dest_folder, exist_ok=True)

        # Save uploaded file
        file_name = uploaded_pdf.name
        dest_path = os.path.join(dest_folder, file_name)
        
        # Save uploaded file to dest_path
        with open(dest_path, "wb") as f:
            f.write(uploaded_pdf.read())

        populate_database.load()
        st.success(f"Uploaded: {file_name}")

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

   
# Main chat area
st.subheader("💬 Conversation")
for sender, message in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"👤 You: *{message}*")
    else:
        st.markdown(f"*🤖 Unity:* {message}")

# Input form
with st.form(key="message_form", clear_on_submit=True):
    user_input = st.text_area("Enter your message:", placeholder="Type your message...")
    submit_button = st.form_submit_button("Send")
    if submit_button and user_input:
        handle_message(user_input)
        st.rerun()

