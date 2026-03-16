import imaplib
import email
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL_SENDER")
PASSWORD = os.getenv("EMAIL_PASSWORD")

def fetch_resumes():
    if not EMAIL or not PASSWORD:
        return [], "Missing EMAIL_SENDER or EMAIL_PASSWORD in .env"

    try:
        if os.path.exists("resumes") and not os.path.isdir("resumes"):
            return [], "'resumes' exists as a file. Delete or rename it, then create a folder named resumes."

        os.makedirs("resumes", exist_ok=True)

        print("Connecting to Gmail IMAP...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL, PASSWORD)
        print("Login successful")

        status, count = mail.select("inbox")
        print("Inbox select status:", status, "Message count:", count)

        status, messages = mail.search(None, "UNSEEN")
        print("Search status:", status)
        print("Messages raw:", messages)

        if status != "OK":
            mail.logout()
            return [], "Failed to search inbox"

        email_ids = messages[0].split()
        print("Email IDs found:", email_ids)

        resumes = []

        for e_id in email_ids:
            print("Fetching email ID:", e_id)
            status, msg_data = mail.fetch(e_id, "(RFC822)")
            print("Fetch status:", status)

            if status != "OK":
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    print("Processing message subject:", msg.get("Subject"))

                    for part in msg.walk():
                        if part.get_content_disposition() == "attachment":
                            filename = part.get_filename()
                            print("Attachment found:", filename)

                            if filename and filename.lower().endswith(".pdf"):
                                filepath = os.path.join("resumes", filename)
                                with open(filepath, "wb") as f:
                                    f.write(part.get_payload(decode=True))
                                resumes.append(filepath)
                                print("Saved resume:", filepath)

        mail.logout()
        return resumes, None

    except Exception as e:
        return [], str(e)
