import streamlit as st
import pandas as pd
import smtplib
from email.message import EmailMessage

st.set_page_config(page_title="Burbio Verification", page_icon="🔐")

st.title("Burbio Product Access Verification")
st.markdown("Please fill out this form to request access to Burbio products. We will review your request and get back to you shortly.")

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
            Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos. Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.
        </div>
        """,
        unsafe_allow_html=True
    )


    submit = st.form_submit_button(
        "Submit Request", 
        disabled=not agreed, 
        type="primary"
    )

# 2. Handle submission and validation
if submit:
    if not name or not email or not org:
        st.warning("All fields (Name, Email, Organization) are required to submit.")
    else:
        # 3. Email sending logic
        try:
            msg = EmailMessage()
            msg.set_content(f"New Burbio Product Access Verification Request:\n\nName: {name}\nEmail: {email}\nOrganization: {org}\n\nPlease review this request.")
            msg['Subject'] = f'[Burbio Request] New Access Verification from {name}'
            
            # Credentials for sending email
            # Note the following instructions. In place of grahamwierzbicki@gmail.com, place your email. In place of iwzgpzwcqscarfhs place your app password.
            # To generate an app password, go to https://myaccount.google.com/apppasswords
            sender_email = "grahamwierzbicki@gmail.com"
            app_password = "iwzgpzwcqscarfhs"
            target_email = "grahamwierzbicki@gmail.com"
            
            msg['From'] = sender_email
            msg['To'] = target_email
            
            # Connect to SMTP server (using Gmail's SSL port as standard)
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, app_password)
                server.send_message(msg)
                
            st.success("Verification request sent successfully!")
            
        except Exception as e:
            st.error(f"Error sending email. Please check configuration.")
            st.info(f"Details: {e}")
