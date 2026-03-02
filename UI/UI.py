import streamlit as st
import os
import sys
# Add project root BEFORE importing RAG
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
# Import RAG
from RAG import query_data
from RAG import populate_database

# Global Variable for path to data folder for storing DOCs
PATH = r"D:\EktaSonawane\Phase2\AIHackathon\UI\data"
# Root folder containing all subfolders to be fetched automatically
SOURCE_RECURSIVE = r"D:\EktaSonawane\Test Documents"
# Supported DOC extensions 
doc_extensions = (".pdf", ".doc", ".docx")

# ---------------------- Session State ----------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def handle_message(message: str):
    if not message.strip():
        return

    # For Keeping Chat History 
    st.session_state.chat_history.append(("user", message))

    # Generate Response through RAG & LLM
    with st.spinner("Generating response..."):
        bot_reply = query_data.query_rag(message)  # This might take time

    # For Keeping Chat History 
    st.session_state.chat_history.append(("Bot:", bot_reply))

# ---------------------- Streamlit UI ----------------------
st.set_page_config(layout="wide")
st.title("📑 Seal The Deal ")

# Sidebar
with st.sidebar:
    # Upload Button 
    st.header("📂 Upload Contract")
    uploaded_pdf = st.file_uploader("Upload PDF", type=doc_extensions)
    if uploaded_pdf:
        dest_folder = r""+PATH
        os.makedirs(dest_folder, exist_ok=True)
        # Save uploaded file
        file_name = uploaded_pdf.name
        dest_path = os.path.join(dest_folder, file_name)
        # Save uploaded file to dest_path
        with open(dest_path, "wb") as f:
            f.write(uploaded_pdf.read())
        # update the embedings
        populate_database.load()
        st.success(f"Uploaded: {file_name}")

    # Clear Database button
    if st.button("🧹 Clear DB"):
        # Clear Context by deleting PDFs and DB
        if os.path.exists(PATH):
            for file in os.listdir(PATH):
                if file.lower().endswith(doc_extensions):
                    try:
                        os.remove(os.path.join(PATH, file))
                    except Exception as e:
                        print(f"Could not delete {file}: {e}")
        # Clear DB
        populate_database.clear_database() 
        st.success("Database cleared successfully!")
     # ---------------------- Refresh Button (ADDED) ----------------------
    st.divider()
   
# Main chat area
st.subheader("💬 Conversation")
for sender, message in st.session_state.chat_history:
    if sender == "user":
        st.markdown(
            f"<p style='font-size:18px; font-weight:700;'>👤 You: {message}</p>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<p style='font-size:18px; font-weight:700;'>🤖 Bot: {message}</p>",
            unsafe_allow_html=True
        )

# Input form
with st.form(key="message_form", clear_on_submit=True):
    user_input = st.text_area("Enter your message:", placeholder="Type your message...")
    submit_button = st.form_submit_button("Send")
    if submit_button and user_input:
        handle_message(user_input)
        st.rerun()
