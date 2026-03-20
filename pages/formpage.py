import re
import urllib.parse
import smtplib
from email.message import EmailMessage

import streamlit as st

st.set_page_config(page_title="Burbio Verification", page_icon="🔐")

# ---------------------------------------------------------------------------
# Configuration — update these values before deploying
# ---------------------------------------------------------------------------

SENDER_EMAIL  = "grahamwierzbicki@gmail.com"
APP_PASSWORD  = "iwzgpzwcqscarfhs"
RECIPIENT     = "grahamwierzbicki@gmail.com"
ACCESS_LINK   = "https://your-real-access-link.com"   # <-- replace with real link
PUBLIC_URL    = "http://localhost:8501"                # <-- replace with deployed app URL


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
    return f"{PUBLIC_URL}/?{action}=1&{params}"


# ---------------------------------------------------------------------------
# Admin action handler  (runs before the form so the page renders cleanly)
# ---------------------------------------------------------------------------

params = st.query_params

# Guard: only process each action once per session
if "action_handled" not in st.session_state:
    st.session_state.action_handled = False

if not st.session_state.action_handled:
    action = None
    if "approve" in params:
        action = "approve"
    elif "deny" in params:
        action = "deny"

    if action and "email" in params and "name" in params:
        requester_email = params["email"]
        requester_name  = params["name"]

        if action == "approve":
            subject = "Burbio Access Approved ✅"
            plain   = (
                f"Hi {requester_name},\n\n"
                f"Your request to access Burbio has been approved!\n"
                f"Click the link below to get started:\n{ACCESS_LINK}\n\n"
                "Thank you."
            )
            html = f"""
            <html><body>
              <h2>Access Approved ✅</h2>
              <p>Hi {requester_name},</p>
              <p>Your request to access Burbio has been approved!</p>
              <p>
                <a href="{ACCESS_LINK}"
                   style="display:inline-block;padding:10px 20px;font-size:16px;
                          color:white;background:#28a745;text-decoration:none;
                          border-radius:5px;">
                  Access Burbio
                </a>
              </p>
              <p>Thank you.</p>
            </body></html>
            """
            admin_msg = f"✅ You have **approved** access for **{requester_name}** ({requester_email}). They have been emailed with the access link."

        else:  # deny
            subject = "Burbio Access Request Denied"
            plain   = (
                f"Hi {requester_name},\n\n"
                "Unfortunately your request to access Burbio has been denied.\n"
                "If you have questions, please reply to this email.\n\n"
                "Thank you."
            )
            html = f"""
            <html><body>
              <h2>Access Denied</h2>
              <p>Hi {requester_name},</p>
              <p>Unfortunately your request to access Burbio has been denied.</p>
              <p>If you have questions, please reply to this email.</p>
              <p>Thank you.</p>
            </body></html>
            """
            admin_msg = f"❌ You have **denied** access for **{requester_name}** ({requester_email}). They have been notified."

        try:
            send_email(requester_email, subject, html, plain)
            st.success(admin_msg)
        except Exception as e:
            st.error(f"Error sending notification email: {e}")

        # Mark handled so a page refresh doesn't resend
        st.session_state.action_handled = True
        # Clear query params so the URL looks clean
        st.query_params.clear()

# ---------------------------------------------------------------------------
# Request form
# ---------------------------------------------------------------------------

st.title("Burbio Product Access Verification")
st.markdown(
    "Please fill out this form to request access to Burbio products. "
    "We will review your request and get back to you shortly."
)

with st.form("verification_form"):
    name   = st.text_input("Name",                    placeholder="Jane Doe")
    email  = st.text_input("Email",                   placeholder="jane@university.edu")
    org    = st.text_input("Organization/University", placeholder="Georgetown University")
    submit = st.form_submit_button("Submit Request")

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
