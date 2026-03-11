import streamlit as st

st.set_page_config(
    page_title="Burbio",
    layout="centered",
)
#Button
if st.button("Form"):
    st.switch_page("pages/formpage.py")

# Logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("burbio_logo.png", use_container_width=True)

st.divider()

st.header("About Burbio")
st.markdown("""
Burbio is a data service that measures K-12 spending and policies and provides insights that drive results. Burbio's data is used by suppliers, policy makers, investors, researchers and advocacy groups to better understand the K-12 market.

**Burbio's specialty** is gathering hard-to-find information and turning it into actionable insights for industry stakeholders. Datasets include school board meeting minutes, strategic plans, state grants, checkbook registers, ESSER III plans, CapEx budgets, Superintendent staffing levels, and more. The information is delivered through a district profile that presents relevant information at the district level as well as through market-level reporting highlighting important trends. Burbio utilizes keyword searching and categorization of spending activity and provides the data in a format that can be easily integrated into client CRMs.

**Burbio's clients** include curriculum providers, equipment manufacturers, technology and software suppliers, furniture suppliers, staffing companies, consulting firms, and more.

**Our origin:** Burbio entered the K-12 market in July 2020, launching the Burbio School Opening Tracker, which became the authority on K-12 learning modalities—measuring whether schools were open for in-person learning every day, only a few days a week (hybrid), or not at all (virtual) during COVID-19. Burbio's nationwide survey of local school activity was cited thousands of times in the press, as well as by government officials and academic researchers. During 2020–22, Burbio provided data to the CDC, as well as to K-12 suppliers and consumer packaged goods companies whose operations were impacted by pandemic-era educational policies.

For more information on Burbio, you can [request sample data](mailto:info@burbio.com) here or [set up a short call](mailto:info@burbio.com).
""")
