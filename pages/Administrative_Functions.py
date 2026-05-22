import uuid
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone, timedelta

import requests
import streamlit as st

st.set_page_config(page_title="Burbio Admin", page_icon="🔐")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SENDER_EMAIL  = st.secrets["email"]["sender_email"]#jadenbobb03@gmail.com
APP_PASSWORD  = st.secrets["email"]["app_password"]
PUBLIC_URL    = "http://localhost:8599" # MUST REPLACE

SUPABASE_URL  = st.secrets["supabase"]["project_url"]
SUPABASE_KEY  = st.secrets["supabase"]["anon_key"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def create_download_token(requester_email: str) -> str | None:
    """Insert a row into download_links and return the token UUID."""
    token = str(uuid.uuid4())

    payload = {
        "id":         token,
        "file_id":    "all",           # placeholder until per-file logic is added
        "user_id":    requester_email,
        "used":       False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/download_links",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json=payload,
        timeout=10,
    )

    if resp.status_code in (200, 201):
        return token
    else:
        st.error(f"Failed to create download token: {resp.status_code} {resp.text}")
        return None


# ---------------------------------------------------------------------------
# Admin action handler
# ---------------------------------------------------------------------------

params = st.query_params

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
            token = create_download_token(requester_email)

            if token:
                download_link = f"{PUBLIC_URL}/Download_Files?token={token}"

                subject = "Burbio COVID School Opening Data Access Approved"
                plain   = (
                    f"Hi {requester_name},\n\n"
                    f"Your request to access Burbio has been approved!\n"
                    f"Click the link below to download your files:\n{download_link}\n\n"
                    "Thank you."
                )
                html = f"""
                <html><body>
                  <h2>Access Approved ✅</h2>
                  <p>Hi {requester_name},</p>
                  <p>Your request to access Burbio has been approved!</p>
                  <p>
                    <a href="{download_link}"
                       style="display:inline-block;padding:10px 20px;font-size:16px;
                              color:white;background:#28a745;text-decoration:none;
                              border-radius:5px;">
                      Download Your Files
                    </a>
                  </p>
                  <p>Thank you.</p>
                </body></html>
                """
                admin_msg = (
                    f"✅ You have **approved** access for **{requester_name}** "
                    f"({requester_email}). They have been emailed with the download link."
                )

                try:
                    send_email(requester_email, subject, html, plain)
                    st.success(admin_msg)
                except Exception as e:
                    st.error(f"Error sending approval email: {e}")
                    st.exception(e)

        else:  # deny
            default_denial = (
                f"Hi {requester_name},\n\n"
                "Unfortunately your request to access Burbio has been denied.\n"
                "If you have questions, please reply to this email.\n\n"
                "Thank you."
            )

            st.warning(f"You are about to deny access for **{requester_name}** ({requester_email}).")
            st.markdown("**Customize the denial email (optional):**")

            custom_message = st.text_area(
                "Email body",
                value=default_denial,
                height=200,
                key="denial_message"
            )

            if st.button("Send Denial Email", type="primary"):
                html = f"""
                <html><body>
                <h2>Access Denied</h2>
                <pre style="font-family:sans-serif;white-space:pre-wrap;">{custom_message}</pre>
                </body></html>
                """
                admin_msg = (
                    f"❌ You have **denied** access for **{requester_name}** "
                    f"({requester_email}). They have been notified."
                )

                try:
                    send_email(requester_email, "Burbio COVID School Opening Data Access Denied", html, custom_message)
                    st.success(admin_msg)
                    st.session_state.action_handled = True
                    st.query_params.clear()
                except Exception as e:
                    st.error(f"Error sending denial email: {e}")
                    st.exception(e)

            st.stop()

        st.session_state.action_handled = True
        st.query_params.clear()

    elif not action:
        st.warning("No action found. This page is for admin approve/deny actions only.")