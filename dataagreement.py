import streamlit as st 

# 1. Initialize session state flag
if "has_agreed" not in st.session_state: 
    st.session_state.has_agreed = False 

# 2. Agreement text
AGREEMENT_TEXT = """ 
DATA USE AND PRIVACY AGREEMENT
-------------------------------
1. SCOPE OF USE:
The data provided through this portal is for internal research purposes only. 

2. CONFIDENTIALITY:
The user agrees to maintain the confidentiality of all sensitive information.

3. SECURITY:
The user is responsible for ensuring the data is stored on secure systems.

[Insert additional agreement text here...]
""".strip()

st.title("Data Request Form")

# 3. The Agreement Box 
# st.text_area creates a scrollable box by default. 
# Setting 'disabled=True' makes it read-only.
st.text_area(
    label="Please review the terms below:",
    value=AGREEMENT_TEXT,
    height=250,
    disabled=True
)

# 4. Checkmark Logic
# Always visible and enabled.
agreed = st.checkbox( 
    "I have read and agree to the Data Agreement.",
    key="agreement_checkbox" 
)

# 5. Submit button 
# Only becomes clickable once the checkbox above is checked.
submitted = st.button ( 
    "Submit and Request File",
    disabled=not agreed, 
    type="primary"
)

# 6. Handling the submission
if submitted: 
    st.session_state.has_agreed = True 

# 7. Confirmation after submission
if st.session_state.has_agreed: 
    st.success("✅ Agreement accepted. Your request has been recorded.")
    # Optional: Add a download button or next steps here





