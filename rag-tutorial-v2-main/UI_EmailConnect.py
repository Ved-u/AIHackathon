import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -----------------------------
# CONFIGURATION (Gmail SMTP)
# -----------------------------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "utpatvedant96@gmail.com"   # Your email
EMAIL_PASSWORD = "iauy nfth uzey xbec"      # ⚠️ App password (not your normal password)

# -----------------------------
# CONTRACTS DATA
# -----------------------------
contracts = [
    {
        "user": "Vedant Utpat",
        "email": "vedantutpat084@gmail.com",
        "end_date": "2025-09-18"
    }
]

# -----------------------------
# FUNCTION TO SEND EMAIL
# -----------------------------
def send_email(to_email, subject, body):
    """Send email with subject & body to recipient."""
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"✅ Email sent successfully to {to_email}")
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed! Please check credentials or app password.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# -----------------------------
# CHECK CONTRACT DATES
# -----------------------------
def check_contracts():
    """Check contract dates and send email reminders."""
    today = datetime.date.today()

    for contract in contracts:
        end_date = datetime.datetime.strptime(contract["end_date"], "%Y-%m-%d").date()
        days_left = (end_date - today).days

        subject = f"Contract Status: {contract['user']} (Ends on {end_date})"
        body = (
            f"Hello {contract['user']},\n\n"
            f"This is an automated reminder about your contract.\n\n"
            f"📅 Contract End Date: {end_date}\n"
            f"⏳ Days Left: {days_left}\n\n"
            f"Regards,\nContract Analyzer Team"
        )

        send_email(contract["email"], subject, body)
        print(f"📩 Reminder sent to {contract['user']} ({days_left} days left)")

# -----------------------------
# EXTRA FUNCTION: ADD CONTRACT & SEND EMAIL
# -----------------------------
def add_contract_and_notify(user_name, user_email, end_date="2025-09-26"):
    """
    Add a new contract with user_name, user_email, and optional end_date.
    Then calls check_contracts() to send the reminder immediately.
    """
    contracts.clear()  # Clear old contracts if you want only the new one
    contracts.append({
        "user": user_name,
        "email": user_email,
        "end_date": end_date
    })
    print(f"📝 Added contract for {user_name} ({user_email}), checking now...")
    check_contracts()

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    # Normal: check predefined contracts
    check_contracts()

    # OR dynamically add a new one and send mail immediately
    # Example usage:
    # add_contract_and_notify("New User", "newuser@example.com", "2025-12-31")
