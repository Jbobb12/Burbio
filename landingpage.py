import streamlit as st

st.set_page_config(
    page_title="Burbio",
    layout="centered",
)

# Logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("burbio_logo.png", use_container_width=True)

st.divider()
