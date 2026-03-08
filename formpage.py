import streamlit as st

st.set_page_config(
    page_title="Burbio Data Request Form",
    layout="centered",
)

st.title("Burbio Data Request Form")
st.write("Please complete all fields to request access to the data.")

with st.form("data_request_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    organization = st.text_input("Organization/University")

    submitted = st.form_submit_button("Submit")


