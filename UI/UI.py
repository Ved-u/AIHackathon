import streamlit as st
import os
import sys
import shutil

# Add project root BEFORE importing RAG
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
# Import RAG
from RAG import query_data
from RAG import populate_database
import Send_Email

# Global Variable for path to data folder for storing PDFs
PATH = r"D:\OneDrive - SoftDEL Systems Pvt. Ltd\GAP\Demo\AIHackathon\UI\data"

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
    st.session_state.chat_history.append(("Bot:", bot_reply))
   
def fetch_docs():
    # Root folder containing all subfolders
    source_folder = r"D:\OneDrive - SoftDEL Systems Pvt. Ltd\Softdel Systems\GAP\OneDrive_2025-12-18"

    # Folder where all documents will be copied
    output_folder = r"D:\OneDrive - SoftDEL Systems Pvt. Ltd\Softdel Systems\GAP\Demo\AIHackathon\UI\data"

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # List of file extensions you consider as documents
    doc_extensions = (".pdf", ".doc", ".docx")

    # Walk through all subfolders
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith(doc_extensions):
                source_file = os.path.join(root, file)
                dest_file = os.path.join(output_folder, file)

                # If file with same name exists, rename to avoid overwriting
                counter = 1
                base_name, ext = os.path.splitext(file)
                while os.path.exists(dest_file):
                    dest_file = os.path.join(output_folder, f"{base_name}_{counter}{ext}")
                    counter += 1

                shutil.copy2(source_file, dest_file)  # Copy file with metadata

    print("All documents copied to:", output_folder)

# ---------------------- Streamlit UI ----------------------
st.set_page_config(layout="wide")
st.title("📑 Seal The Deal ")

# Sidebar
with st.sidebar:
    # Upload Button 
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
# for sender, message in st.session_state.chat_history:
#     if sender == "user":
#         st.markdown(f"👤 You: {message}")
#     else:
#         st.markdown(f"🤖 Bot: {message}")
for sender, message in st.session_state.chat_history:
    if sender == "user":
        st.markdown(
            f"<p style='font-size:18px; font-weight:700;'>👤 You: {message}</p>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(f"🤖 Bot: {message}")
    
    # else:
    #     st.markdown(
    #         f"<p style='font-size:18px; font-weight:700;'>🤖 Bot: {message}</p>",
    #         unsafe_allow_html=True
    #     )


# Input form
with st.form(key="message_form", clear_on_submit=True):
    user_input = st.text_area("Enter your message:", placeholder="Type your message...")
    submit_button = st.form_submit_button("Send")
    if submit_button and user_input:
        handle_message(user_input)
        st.rerun()

