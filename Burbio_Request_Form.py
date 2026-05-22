import re
import urllib.parse
import smtplib
from email.message import EmailMessage

import streamlit as st

st.set_page_config(page_title="Burbio Verification", page_icon="🔐")

# ---------------------------------------------------------------------------
# Configuration — update these values before deploying
# ---------------------------------------------------------------------------

SENDER_EMAIL  = st.secrets["email"]["sender_email"]
APP_PASSWORD  = st.secrets["email"]["app_password"]
RECIPIENT     = st.secrets["email"]["sender_email"]
#ACCESS_LINK   = "https://your-real-access-link.com"   # <-- replace with real link
PUBLIC_URL    = st.secrets["email"]["public_url"]               # <-- replace with deployed app URL


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
    return f"{PUBLIC_URL}/Administrative_Functions?{action}=1&{params}"




# ---------------------------------------------------------------------------
# Request form
# ---------------------------------------------------------------------------

st.title("Burbio COVID School Opening Data Access Request")
st.markdown(
    "Please fill out this form to request access to Burbio datasets. "
    "We will review your request and get back to you within the next five business days."
)

agreed = st.checkbox("I have read and agree to the Data Agreement.", key="external_agree")
# 1. Create the form with the required input fields
with st.form("verification_form"):
    name = st.text_input("Name", placeholder="Jane Doe")
    email = st.text_input("Email", placeholder="jane@university.edu")
    org = st.text_input("Organization/University", placeholder="Georgetown University")

    reason = st.text_area(
    "Reason for Request",
    placeholder="Briefly describe how you plan to use the data...",
    max_chars=1200,
    help="Maximum 200 words."
)
    
    st.markdown(
    """
    <div style="
        border: 1px solid #ccc;
        padding: 10px;
        height: 130px;
        overflow-y: scroll;
        margin-bottom: 10px;
    ">
        <strong>Burbio School Opening Tracker – Terms of Use</strong>
        <p style="font-size: 14px;">
        The Burbio School Opening Tracker ("Data") is made available by Burbio, Inc. ("Burbio") to support academic research, journalism, and public policy analysis. By accessing or using the Data, you agree to the following terms:
        <br><br>
        <strong>1. Permitted Use:</strong> You may use the Data for non-commercial purposes, including academic research, journalism and reporting, public policy analysis, and other non-commercial, informational uses.
        <br><br>
        <strong>2. Prohibited Use:</strong> You may not use the Data for any commercial purpose, including incorporation into products, services, or paid reports. You may not sell, license, sublicense, or redistribute the Data as a standalone dataset. You may not use the Data to train, fine-tune, or enhance any commercial artificial intelligence or machine learning models. You may not systematically extract or replicate the Data to create a competing database or service.
        <br><br>
        <strong>3. Attribution:</strong> Any public use of the Data must include clear attribution to Burbio, for example: "Source: Burbio School Opening Tracker". For digital uses, attribution should include a link to Burbio where reasonably possible.
        <br><br>
        <strong>4. Derivative Works:</strong> You may create analyses, reports, or other derivative works using the Data, provided that such use remains non-commercial and proper attribution to Burbio is included.
        <br><br>
        <strong>5. No Misrepresentation:</strong> You may not represent the Data as your own, or use or modify the Data in a way that is misleading or misrepresents Burbio's work.
        <br><br>
        <strong>6. No Warranty:</strong> The Data is provided "as is" without warranty of any kind, express or implied, including accuracy or completeness. Burbio disclaims all liability for any decisions or actions taken based on the Data.
        <br><br>
        <strong>7. Right to Revoke:</strong> Burbio reserves the right to revoke or restrict access to the Data at any time for violation of these terms.
        <br><br>
        <strong>8. Commercial Use &amp; Licensing:</strong> For commercial use, licensing, or partnership opportunities, please contact Burbio at: [insert email]
        </p>
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

    if not reason.strip():
        errors.append("Please provide a reason for your request.")
    elif len(reason.split()) > 200:
        errors.append("Reason must be 200 words or fewer.")
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
          <p><strong>Reason:</strong> {reason}</p>
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
            f"  Reason: {reason}\n\n"
            f"Approve: {approve_link}\n"
            f"Deny:    {deny_link}"
        )

        try:
            send_email(
                to      = RECIPIENT,
                subject = f"ACCESS Request: COVID School Opening Data from {name}",
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
