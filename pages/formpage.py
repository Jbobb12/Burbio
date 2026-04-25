import re
import urllib.parse
import smtplib
from email.message import EmailMessage

import streamlit as st

st.set_page_config(page_title="Burbio Verification", page_icon="🔐")

# ---------------------------------------------------------------------------
# Configuration — update these values before deploying
# ---------------------------------------------------------------------------

SENDER_EMAIL  = "jadenbobb03@gmail.com"
APP_PASSWORD  = "emym pzaj pvyi oldi"
RECIPIENT     = "jadenbobb03@gmail.com"
ACCESS_LINK   = "https://your-real-access-link.com"   # <-- replace with real link
PUBLIC_URL    = "http://localhost:8599"                # <-- replace with deployed app URL


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_valid_email(addr: str) -> bool:
    """Basic RFC-5322-ish email validation."""
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, addr) is not None


def send_email(to: str, subject: str, html: str, plain: str) -> None:
    """Send an HTML email via Gmail SMTP-SSL."""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = to
    msg.set_content(plain)
    msg.add_alternative(html, subtype="html")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)


def make_action_link(action: str, email: str, name: str) -> str:
    """Build an approve/deny URL pointing to the *public* deployed app."""
    params = urllib.parse.urlencode({"email": email, "name": name})
    return f"{PUBLIC_URL}/adminaction?{action}=1&{params}"




# ---------------------------------------------------------------------------
# Request form
# ---------------------------------------------------------------------------

st.title("Burbio Product Access Verification")
st.markdown(
    "Please fill out this form to request access to Burbio products. "
    "We will review your request and get back to you shortly."
)

agreed = st.checkbox("I have read and agree to the Data Agreement.", key="external_agree")
# 1. Create the form with the required input fields
with st.form("verification_form"):
    name = st.text_input("Name", placeholder="Jane Doe")
    email = st.text_input("Email", placeholder="jane@university.edu")
    org = st.text_input("Organization/University", placeholder="Georgetown University")
    
    st.markdown(
        """
        <div style="
            border: 1px solid #ccc;
            padding: 10px;
            height: 130px;
            overflow-y: scroll;
            margin-bottom: 10px;
        ">
            <strong>User Agreement</strong>
            <p style="font-size: 14px;">
            This Data Use Agreement (“Agreement”) is entered into as of [Date] by and between [Data Provider Name] (“Provider”) and [Data Recipient Name] (“Recipient”). The Provider agrees to provide certain data (“Data”) to the Recipient solely for the purpose of [describe purpose, such as research, analytics, or internal business use]. The Data includes [describe the dataset, such as customer records, anonymized logs, or survey data]. The Recipient agrees to use the Data only for the stated purpose and not for any unauthorized use, and to comply with all applicable laws and regulations.

The Recipient shall implement appropriate administrative, technical, and physical safeguards to protect the Data from unauthorized access, disclosure, or misuse, and shall promptly notify the Provider of any known or suspected data breach. The Data shall be treated as confidential, and the Recipient shall not disclose it to any third party without the prior written consent of the Provider.

The Recipient agrees to comply with all applicable data protection and privacy laws relevant to the handling of the Data. This Agreement shall commence on [Start Date] and remain in effect until [End Date], unless terminated earlier by either party upon [X days] written notice. Upon termination of this Agreement, the Recipient agrees to return or securely destroy all copies of the Data and certify such destruction if requested.
        </div>
        """,
        unsafe_allow_html=True
    )


    submit = st.form_submit_button(
        "Submit Request", 
        disabled=not agreed, 
        type="primary"
    )

if submit:
    # --- Validation ---
    errors = []
    if not name.strip():
        errors.append("Name is required.")
    if not email.strip():
        errors.append("Email is required.")
    elif not is_valid_email(email.strip()):
        errors.append("Please enter a valid email address (e.g. jane@university.edu).")
    if not org.strip():
        errors.append("Organization is required.")

    if errors:
        for err in errors:
            st.warning(err)
    else:
        name  = name.strip()
        email = email.strip()
        org   = org.strip()

        approve_link = make_action_link("approve", email, name)
        deny_link    = make_action_link("deny",    email, name)

        html_body = f"""
        <html><body>
          <h2>New Burbio Access Verification Request</h2>
          <p><strong>Name:</strong> {name}</p>
          <p><strong>Email:</strong> {email}</p>
          <p><strong>Organization:</strong> {org}</p>
          <br>
          <p>Please review this request:</p>
          <a href="{approve_link}"
             style="display:inline-block;padding:10px 20px;font-size:16px;
                    color:white;background:#28a745;text-decoration:none;
                    border-radius:5px;margin-right:10px;">
            Approve
          </a>
          <a href="{deny_link}"
             style="display:inline-block;padding:10px 20px;font-size:16px;
                    color:white;background:#dc3545;text-decoration:none;
                    border-radius:5px;">
            Deny
          </a>
        </body></html>
        """
        plain_body = (
            f"New Burbio access request:\n"
            f"  Name: {name}\n  Email: {email}\n  Org: {org}\n\n"
            f"Approve: {approve_link}\n"
            f"Deny:    {deny_link}"
        )

        try:
            send_email(
                to      = RECIPIENT,
                subject = f"[Burbio Request] New Access Verification from {name}",
                html    = html_body,
                plain   = plain_body,
            )
            st.success(
                "✅ Your verification request has been submitted! "
                "You'll receive an email once it has been reviewed."
            )
        except Exception as e:
            st.error("Error sending request. Please check the app configuration.")
            st.info(f"Details: {e}")
