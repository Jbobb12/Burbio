import smtplib
from email.message import EmailMessage

import streamlit as st

st.set_page_config(page_title="Burbio Admin", page_icon="🔐")

# ---------------------------------------------------------------------------
# Configuration — keep in sync with formpage.py
# ---------------------------------------------------------------------------

SENDER_EMAIL = "jadenbobb03@gmail.com"
APP_PASSWORD = "emym pzaj pvyi oldi"

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


def get_download_link(requester_email: str, requester_name: str) -> str:
    """
    TODO: Replace this placeholder with real Supabase logic.
    This function should:
      1. Fetch the relevant file(s) from Supabase storage
      2. Apply a watermark based on the current timestamp and user identity
      3. Return a temporary signed download URL
    """
    return "https://your-supabase-download-link.com"  # <-- replace with real logic


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
            # --- Get download link (swap placeholder for real Supabase logic later) ---
            download_link = get_download_link(requester_email, requester_name)

            subject = "Burbio Access Approved ✅"
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
            admin_msg = (
                f"❌ You have **denied** access for **{requester_name}** "
                f"({requester_email}). They have been notified."
            )

        try:
            send_email(requester_email, subject, html, plain)
            st.success(admin_msg)
        except Exception as e:
            st.error(f"Error sending notification email: {e}")
            st.exception(e)

        st.session_state.action_handled = True
        st.query_params.clear()

    elif not action:
        # Someone navigated to this page directly with no query params
        st.warning("No action found. This page is for admin approve/deny actions only.")