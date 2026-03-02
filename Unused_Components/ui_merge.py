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
from docx2pdf import convert

# Global Variable for path to data folder for storing PDFs
PATH = r"D:\updated_GAP\AIHackathon\UI\data"

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

    # For Keeping Chat History 
    st.session_state.chat_history.append(("user", message))

    # Generate Response through RAG & LLM
    with st.spinner("Generating response..."):
        bot_reply = query_data.query_rag(message)  # This might take time

    # For Keeping Chat History 
    st.session_state.chat_history.append(("UniSoft:", bot_reply))
   

# ---------------------- Streamlit UI ----------------------
st.set_page_config(layout="wide")
st.title("📑 UniSoft - Contract Chatbot")

# Sidebar
with st.sidebar:
    st.header("📂 Upload Contract")

    uploaded_file = st.file_uploader("Upload DOC, DOCX, or PDF", type=["pdf", "docx", "doc"])

    if uploaded_file:
        dest_folder = PATH  
        os.makedirs(dest_folder, exist_ok=True)

        # Save uploaded file
        original_name = uploaded_file.name
        original_path = os.path.join(dest_folder, original_name)

        with open(original_path, "wb") as f:
            f.write(uploaded_file.read())

        # ------------------------
        # Convert DOC/DOCX → PDF
        # ------------------------
        if original_name.lower().endswith((".docx", ".doc")):
            pdf_name = os.path.splitext(original_name)[0] + ".pdf"
            pdf_path = os.path.join(dest_folder, pdf_name)

            try:
                convert(original_path, pdf_path)
                st.success(f"Converted to PDF: {pdf_name}")
                final_pdf_path = pdf_path
            except Exception as e:
                st.error(f"Conversion failed: {e}")
                st.stop()

        else:
            # Already PDF
            final_pdf_path = original_path
            st.success(f"Uploaded PDF: {original_name}")

        # ------------------------
        # Call your DB function
        # ------------------------
        try:
            populate_database.load(final_pdf_path)
            st.success("Database updated successfully!")
        except Exception as e:
            st.error(f"Database update failed: {e}")

    # Clear Database button
    if st.button("🧹 Clear DB"):
        # Clear Context by deleting PDFs and DB
        if os.path.exists(PATH):
            for file in os.listdir(PATH):
                if file.lower().endswith(".pdf"):
                    try:
                        os.remove(os.path.join(PATH, file))
                    except Exception as e:
                        print(f"Could not delete {file}: {e}")
        # Clear DB
        populate_database.clear_database_new() 
        st.success("Database cleared successfully!")

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
        st.markdown(f"*🤖 UniSoft:* {message}")

# Input form
with st.form(key="message_form", clear_on_submit=True):
    user_input = st.text_area("Enter your message:", placeholder="Type your message...")
    submit_button = st.form_submit_button("Send")
    if submit_button and user_input:
        handle_message(user_input)
        st.rerun()

