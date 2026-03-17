import streamlit as st
import pandas as pd
import requests
from io import StringIO
from urllib.parse import quote

st.set_page_config(page_title="Burbio Data Access", page_icon="📊", layout="centered")

# ─────────────────────────────────────────────
# SUPABASE CONFIGURATION
# Credentials are loaded securely from .streamlit/secrets.toml
# Never hardcode keys in this file!
# ─────────────────────────────────────────────
SUPABASE_URL = st.secrets["supabase"]["project_url"]
SUPABASE_KEY = st.secrets["supabase"]["anon_key"]
BUCKET_NAME  = st.secrets["supabase"]["bucket_name"]

# The exact filenames as they appear in the Supabase Storage bucket
DATA_FILES = {
    "Combined School Data": "combined_data.csv",
}
# ─────────────────────────────────────────────


@st.cache_data(ttl=600)
def load_csv_from_supabase(file_name: str) -> pd.DataFrame:
    """Fetch a CSV file from Supabase Storage (private bucket) and return it as a DataFrame."""

    encoded_bucket = quote(BUCKET_NAME)
    encoded_file = quote(file_name)

    url = f"{SUPABASE_URL}/storage/v1/object/authenticated/{encoded_bucket}/{encoded_file}"

    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apikey": SUPABASE_KEY,
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Supabase returned status {response.status_code}: {response.text}")

    return pd.read_csv(StringIO(response.text))


# ─────────────────────────────────────────────
# PAGE UI
# ─────────────────────────────────────────────

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("burbio_logo.png", use_container_width=True)

st.divider()
st.header("📊 Burbio Dataset Access")
st.markdown(
    "Select a dataset below to preview its contents and download it. "
    "Access to these files is provided for approved researchers only."
)

selected_label = st.selectbox("Choose a dataset", list(DATA_FILES.keys()))
selected_file  = DATA_FILES[selected_label]

if st.button("Load Dataset"):
    with st.spinner(f"Fetching **{selected_label}** from Supabase..."):
        try:
            df = load_csv_from_supabase(selected_file)

            st.success(f"Loaded {len(df):,} rows and {len(df.columns)} columns.")
            st.subheader("Preview (first 100 rows)")
            st.dataframe(df.head(100), use_container_width=True)

            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download full CSV",
                data=csv_bytes,
                file_name=selected_file,
                mime="text/csv",
            )

        except Exception as e:
            st.error("Could not load the dataset. Check your Supabase credentials and bucket configuration.")
            st.info(f"Details: {e}")