import io
import json
import os
import csv
from datetime import datetime, timezone
import requests
import pandas as pd
import streamlit as st
from urllib.parse import quote

# ── Config ────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH    = os.path.join(SCRIPT_DIR, "burbio_logo.png")
SUPABASE_URL = st.secrets["supabase"]["project_url"]
SUPABASE_KEY = st.secrets["supabase"]["anon_key"]
BUCKET_NAME  = st.secrets["supabase"]["bucket_name"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

FORMATS = {
    "CSV":   {"ext": ".csv",   "mime": "text/csv"},
    "JSON":  {"ext": ".json",  "mime": "application/json"},
    "Excel": {"ext": ".xlsx",  "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    "TSV":   {"ext": ".tsv",   "mime": "text/tab-separated-values"},
}

def rows_to_bytes(rows: list[dict], fmt: str) -> bytes:
    if fmt == "CSV":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=rows[0].keys() if rows else [], extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
        return buf.getvalue().encode("utf-8")
    if fmt == "JSON":
        return json.dumps(rows, indent=2).encode("utf-8")
    if fmt == "Excel":
        buf = io.BytesIO()
        pd.DataFrame(rows).to_excel(buf, index=False, engine="openpyxl")
        return buf.getvalue()
    if fmt == "TSV":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=rows[0].keys() if rows else [], delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
        return buf.getvalue().encode("utf-8")
    raise ValueError(f"Unknown format: {fmt}")

st.set_page_config(page_title="Burbio – Download", page_icon="📊", layout="centered")

# ── Logo ──────────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.subheader("Burbio")

st.divider()

# ── Session state init ────────────────────────────────────────────────────────
if "dl_rows" not in st.session_state:
    st.session_state.dl_rows      = None
    st.session_state.dl_base_name = None
    st.session_state.dl_ready     = False

# ── Read token from email link (?token=UUID) ──────────────────────────────────
token = st.query_params.get("token")

if not token:
    st.error("This link is invalid or expired. Please check your email for the correct download link.")
    st.stop()

# ── If file already fetched this session, skip re-lookup ─────────────────────
if not st.session_state.dl_ready:
    lookup = requests.get(
        f"{SUPABASE_URL}/rest/v1/download_links?id=eq.{token}&select=*",
        headers=HEADERS,
        timeout=10,
    )

    if lookup.status_code != 200 or not lookup.json():
        st.error("This link is invalid or expired. Please check your email for the correct download link.")
        st.stop()

    row = lookup.json()[0]

    if row["used"]:
        st.error("This download link has already been used. Each link can only be used once.")
        st.stop()

    expires_at = row.get("expires_at")
    if expires_at:
        expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        if datetime.now(timezone.utc) > expiry:
            st.error("This download link has expired. Please contact support if you need a new one.")
            st.stop()

    ALL_FILES = [
    "closures_cleaned_Final.csv",
    "combined_data.csv",
    "disruptions_cleaned_Final.csv",
    "v2_2020-2021_Burbio_Tracked_Districts_complete_SY.csv",
    "weekly_merged.csv",
]

st.header("Your files are ready to download")
st.warning("These files are for your authorized use only.")

selected_files = [f for f in ALL_FILES if st.checkbox(f, value=True, key=f"chk_{f}")]

fmt_choice = st.radio(
    "Choose your download format",
    list(FORMATS.keys()),
    horizontal=True,
)

if st.button("Download Selected Files", type="primary", use_container_width=True):
    import zipfile
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_id in selected_files:
            with st.spinner(f"Fetching {file_id}…"):
                try:
                    url = (
                        f"{SUPABASE_URL}/storage/v1/object/authenticated/"
                        f"{quote(BUCKET_NAME)}/{quote(file_id)}"
                    )
                    resp = requests.get(url, headers=HEADERS, timeout=60)
                    resp.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    st.error(f"Could not fetch {file_id} ({e.response.status_code}): {e.response.text}")
                    continue
                except Exception as e:
                    st.error(f"Error fetching {file_id}: {e}")
                    continue

            rows = list(csv.DictReader(io.StringIO(resp.text, newline='')))
            base_name = os.path.splitext(file_id)[0]
            filename = base_name + FORMATS[fmt_choice]["ext"]
            data = rows_to_bytes(rows, fmt_choice)
            zf.writestr(filename, data)

    zip_buffer.seek(0)
    st.download_button(
        label="Save All Files (.zip)",
        data=zip_buffer,
        file_name="burbio_files.zip",
        mime="application/zip",
        use_container_width=True,
    )


