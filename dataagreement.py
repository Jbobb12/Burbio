#data areement form 
#checkmark logic 

import streamlit as st 
import streamlit.components.v1 as components 


#two flags (scroll + checkbox)
if "has_scrolled" not in st.session_state: 
    st.session_state.has_scrolled = False #true oncde user scrolls to bottom 

if "has_agreed" not in st.session_state: 
    st.session_state.has_agreed = False #true once checkbox checked off and submitted 

#agreement text // need to add once we get this  
AGREEMENT_TEXT = """ 
[insert agreement text]

""".strip() #for clean formatting 

#Note: Remove this section and its dependent conditionals if incompatible with pop-up box
#scroll-track component 
#using html + js
scroll_component_html = f"""
<div id="agreement-box" style="
    height: 220px;
    overflow-y: scroll;
    border: 1px solid #ccc;
    border-radius: 6px;
    padding: 1rem 1.2rem;
    font-size: 0.85rem;
    line-height: 1.7;
    background: #f9f9f9;
    color: #333;
    white-space: pre-wrap;
    font-family: monospace;
">
{AGREEMENT_TEXT}
</div>
 
<p id="scroll-hint" style="color: #e07b00; font-size:0.8rem; margin-top:0.4rem;">
  ↕ Scroll to the bottom to continue.
</p>
 
<script>
  const box  = document.getElementById("agreement-box");
  const hint = document.getElementById("scroll-hint");
 
  box.addEventListener("scroll", function () {{
    // Check if user has reached the bottom (within 5px tolerance)
    const atBottom = box.scrollTop + box.clientHeight >= box.scrollHeight - 5;
 
    if (atBottom) {{
      hint.textContent = "✔ Agreement fully read.";
      hint.style.color = "#2a7a2a";
 
      // Send a message to the Streamlit parent frame
      window.parent.postMessage({{
        type: "streamlit:setComponentValue",
        value: true
      }}, "*");
    }}
  }});
</script>
"""
scrolled = components.html(scroll_component_html, height=290)

#scrolled stays true once scrolled
if scrolled:
    st.session_state.has_scrolled = True


#checkmark box 
agreed = st.checkbox( 
    "I have read and agree to the Data Agreement.",
    disabled = not st.session_state.has_scrolled, 
    keys= "Agreement Checkbox"
)

#submit button 
submitted = st.button ( 
    "Submit and Request File"
    disabled=not agreed, 
    type = "primary"
)

if submitted and agreed: 
    st.session_state.has_agreed = True 

#confirmation after
if st.session_state.has_agreed: 
    st.success("Agreement accepted")





