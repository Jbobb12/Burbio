import streamlit as st
import boto3
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Burbio Data Access", page_icon="📊", layout="centered")

# ─────────────────────────────────────────────
# AWS S3 CONFIGURATION
# Credentials are loaded securely from .streamlit/secrets.toml
# Never hardcode keys in this file!
# ─────────────────────────────────────────────
AWS_ACCESS_KEY_ID     = st.secrets["aws"]["access_key_id"]
AWS_SECRET_ACCESS_KEY = st.secrets["aws"]["secret_access_key"]
AWS_REGION            = st.secrets["aws"]["region"]
S3_BUCKET_NAME        = st.secrets["aws"]["bucket_name"]

# The exact filename as it appears in the S3 bucket
DATA_FILES = {
    "Combined School Data": "combined_data.csv",
}
# ─────────────────────────────────────────────


@st.cache_resource
def get_s3_client():
    """Create and cache the S3 client so we don't reconnect on every interaction."""
    return boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def load_csv_from_s3(bucket: str, key: str) -> pd.DataFrame:
    """Fetch a CSV file from S3 and return it as a DataFrame."""
    s3 = get_s3_client()
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8")
    return pd.read_csv(StringIO(content))


# ─────────────────────────────────────────────
# PAGE UI
# ─────────────────────────────────────────────

# Logo (same pattern as landingpage.py)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("burbio_logo.png", use_container_width=True)

st.divider()
st.header("📊 Burbio Dataset Access")
st.markdown(
    "Select a dataset below to preview its contents and download it. "
    "Access to these files is provided for approved researchers only."
)

# Dataset selector
selected_label = st.selectbox("Choose a dataset", list(DATA_FILES.keys()))
selected_file  = DATA_FILES[selected_label]

# Load & display button
if st.button("Load Dataset"):
    with st.spinner(f"Fetching **{selected_label}** from S3..."):
        try:
            df = load_csv_from_s3(S3_BUCKET_NAME, selected_file)

            st.success(f"Loaded {len(df):,} rows and {len(df.columns)} columns.")
            st.subheader("Preview (first 100 rows)")
            st.dataframe(df.head(100), use_container_width=True)

            # Download button — lets user save the full CSV locally
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download full CSV",
                data=csv_bytes,
                file_name=selected_file,
                mime="text/csv",
            )

        except Exception as e:
            st.error("Could not load the dataset. Check your AWS credentials and bucket configuration.")
            st.info(f"Details: {e}")