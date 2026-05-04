import streamlit as st 

# 1. Initialize session state flag
if "has_agreed" not in st.session_state: 
    st.session_state.has_agreed = False 

# 2. Agreement text
AGREEMENT_TEXT = """
BURBIO SCHOOL OPENING TRACKER – TERMS OF USE
---------------------------------------------
The Burbio School Opening Tracker ("Data") is made available by Burbio, Inc.
("Burbio") to support academic research, journalism, and public policy analysis.

By accessing or using the Data, you agree to the following terms:

1. PERMITTED USE:
You may use the Data for non-commercial purposes, including academic research,
journalism and reporting, public policy analysis, and other non-commercial,
informational uses.

2. PROHIBITED USE:
You may not use the Data for any commercial purpose, including incorporation
into products, services, or paid reports. You may not sell, license, sublicense,
or redistribute the Data as a standalone dataset. You may not use the Data to
train, fine-tune, or enhance any commercial artificial intelligence or machine
learning models. You may not systematically extract or replicate the Data to
create a competing database or service.

3. ATTRIBUTION:
Any public use of the Data must include clear attribution to Burbio, for example:
"Source: Burbio School Opening Tracker". For digital uses, attribution should
include a link to Burbio where reasonably possible.

4. DERIVATIVE WORKS:
You may create analyses, reports, or other derivative works using the Data,
provided that such use remains non-commercial and proper attribution to Burbio
is included.

5. NO MISREPRESENTATION:
You may not represent the Data as your own, or use or modify the Data in a way
that is misleading or misrepresents Burbio's work.

6. NO WARRANTY:
The Data is provided "as is" without warranty of any kind, express or implied,
including accuracy or completeness. Burbio disclaims all liability for any
decisions or actions taken based on the Data.

7. RIGHT TO REVOKE:
Burbio reserves the right to revoke or restrict access to the Data at any time
for violation of these terms.

8. COMMERCIAL USE & LICENSING:
For commercial use, licensing, or partnership opportunities, please contact
Burbio at: [insert email]
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





