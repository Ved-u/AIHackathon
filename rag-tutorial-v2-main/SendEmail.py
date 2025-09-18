import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -----------------------------
# CONFIGURATION (Gmail SMTP)
# -----------------------------
SMTP_SERVER = "smtp.gmail.com"  # Gmail SMTP server
SMTP_PORT = 587
EMAIL_ADDRESS = "utpatvedant96@gmail.com"  # Your email
EMAIL_PASSWORD = "iauy nfth uzey xbec"  # ⚠️ App password (not normal password)

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
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email sent successfully to {to_email}")
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed! Please check credentials or app password.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# -----------------------------
# CHECK CONTRACT DATES
# -----------------------------
def check_contracts():
    today = datetime.date.today()
    for contract in contracts:
        end_date = datetime.datetime.strptime(contract["end_date"], "%Y-%m-%d").date()
        days_left = (end_date - today).days

        if days_left == 7:
            subject = f"Reminder: Contract ending in 7 days ({contract['user']})"
            body = (
                f"Hello {contract['user']},\n\n"
                f"This is a reminder that your contract will end in 7 days "
                f"on {end_date}.\n\n"
                f"Regards,\nContract Analyzer Team"
            )
            send_email(contract["email"], subject, body)

        elif days_left == 1:
            subject = f"Urgent: Contract ending tomorrow ({contract['user']})"
            body = (
                f"Hello {contract['user']},\n\n"
                f"This is an urgent reminder that your contract ends tomorrow "
                f"on {end_date}.\n\n"
                f"Regards,\nContract Analyzer Team"
            )
            send_email(contract["email"], subject, body)

        elif days_left == 0:
            subject = f"Final Notice: Contract Ending Today ({contract['user']})"
            body = (
                f"Hello {contract['user']},\n\n"
                f"This is the final reminder that your contract is ending today "
                f"({end_date}).\n\n"
                f"Regards,\nContract Analyzer Team"
            )
            send_email(contract["email"], subject, body)

        else:
            print(f"ℹ️ No reminders for {contract['user']} today (contract ends in {days_left} days).")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    check_contracts()
