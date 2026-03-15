import streamlit as st
import pandas as pd
import smtplib
from email.message import EmailMessage
import urllib.parse

st.set_page_config(page_title="Burbio Verification", page_icon="🔐")

st.title("Burbio Product Access Verification")
st.markdown("Please fill out this form to request access to Burbio products. We will review your request and get back to you shortly.")

# --- Email Configuration ---
SENDER_EMAIL = "grahamwierzbicki@gmail.com"
APP_PASSWORD = "iwzgpzwcqscarfhs"

# 1. Create the form with the required input fields
with st.form("verification_form"):
    name = st.text_input("Name", placeholder="Jane Doe")
    email = st.text_input("Email", placeholder="jane@university.edu")
    org = st.text_input("Organization/University", placeholder="Georgetown University")
    submit = st.form_submit_button("Submit Request")

# 2. Handle submission and validation
if submit:
    if not name or not email or not org:
        st.warning("All fields (Name, Email, Organization) are required to submit.")
    else:
        # 3. Email sending logic
        try:
            msg = EmailMessage()
            # Add approve/deny links as HTML buttons
            approve_link = f"http://localhost:8501/?approve=1&email={urllib.parse.quote(email)}&name={urllib.parse.quote(name)}"
            deny_link = f"http://localhost:8501/?deny=1&email={urllib.parse.quote(email)}&name={urllib.parse.quote(name)}"
            
            html_content = f"""
            <html>
                <body>
                    <h2>New Burbio Product Access Verification Request</h2>
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Organization:</strong> {org}</p>
                    <br>
                    <p>Please review this request:</p>
                    <a href="{approve_link}" style="display: inline-block; padding: 10px 20px; font-size: 16px; color: white; background-color: #28a745; text-decoration: none; border-radius: 5px; margin-right: 10px;">Approve</a>
                    <a href="{deny_link}" style="display: inline-block; padding: 10px 20px; font-size: 16px; color: white; background-color: #dc3545; text-decoration: none; border-radius: 5px;">Deny</a>
                </body>
            </html>
            """
            
            msg.set_content("Please enable HTML to view this message.")
            msg.add_alternative(html_content, subtype='html')
            msg['Subject'] = f'[Burbio Request] New Access Verification from {name}'
            target_email = "grahamwierzbicki@gmail.com"
            msg['From'] = SENDER_EMAIL
            msg['To'] = target_email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(SENDER_EMAIL, APP_PASSWORD)
                server.send_message(msg)
            st.success("Verification request sent successfully!")
        except Exception as e:
            st.error(f"Error sending email. Please check configuration.")
            st.info(f"Details: {e}")

# --- Simulate admin approval/denial via query params ---
query_params = st.query_params
if 'approve' in query_params and 'email' in query_params and 'name' in query_params:
    # Send approval email to requester
    try:
        requester_email = query_params['email']
        requester_name = query_params['name']
        approval_msg = EmailMessage()
        approval_msg.set_content(f"Hi {requester_name},\n\nYour request to access Burbio files has been approved! Click here to access: [ACCESS LINK]\n\nThank you.")
        approval_msg['Subject'] = 'Burbio Access Approved'
        approval_msg['From'] = SENDER_EMAIL
        approval_msg['To'] = requester_email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(approval_msg)
        st.success(f"Approval notice sent to {requester_email}.")
        st.write(f"You have approved access for **{requester_name}** ({requester_email}). They have been sent an email with the access link.")
    except Exception as e:
        st.error(f"Error sending approval email: {e}")
elif 'deny' in query_params and 'email' in query_params and 'name' in query_params:
    # Send denial email to requester
    try:
        requester_email = query_params['email']
        requester_name = query_params['name']
        denial_msg = EmailMessage()
        denial_msg.set_content(f"Hi {requester_name},\n\nUnfortunately, your request to access Burbio files has been denied. If you have questions, please contact us.\n\nThank you.")
        denial_msg['Subject'] = 'Burbio Access Denied'
        denial_msg['From'] = SENDER_EMAIL
        denial_msg['To'] = requester_email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(denial_msg)
        st.success(f"Denial notice sent to {requester_email}.")
        st.write(f"You have denied access for **{requester_name}** ({requester_email}). They have been sent an email notifying them.")
    except Exception as e:
        st.error(f"Error sending denial email: {e}")
