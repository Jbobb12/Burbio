import io
import json
import os
import csv
import random
import string
import zipfile
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

ALL_FILES = [
    "2020_2021_DistrictLevel_LearningModes.csv",
    "2020_2022_CountyLevel_LearningModes.csv",
    "2021_2022_DistrictLevel_Closures.csv",
    "2021_DistrictLevel_Closures.csv",
    "2021_DistrictLevel_LearningModes.csv",
]

FORMATS = {
    "CSV":   {"ext": ".csv",   "mime": "text/csv"},
    "JSON":  {"ext": ".json",  "mime": "application/json"},
    "Excel": {"ext": ".xlsx",  "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def generate_watermark_id() -> str:
    """Generate a random 8-character lowercase alphanumeric watermark ID."""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=8))


def fetch_file(file_id: str) -> str:
    """Fetch a file from Supabase storage and return as text."""
    url = (
        f"{SUPABASE_URL}/storage/v1/object/authenticated/"
        f"{quote(BUCKET_NAME)}/{quote(file_id)}"
    )
    resp = requests.get(url, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    return resp.content.decode("utf-8", errors="replace")


def rows_to_bytes(rows: list[dict], fmt: str) -> bytes:
    """Convert rows to bytes in the requested format, no watermark in data."""
    if fmt == "CSV":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=rows[0].keys() if rows else [], extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
        return buf.getvalue().encode("utf-8")


    if fmt == "JSON":
        return json.dumps(rows, indent=2).encode("utf-8")

    if fmt == "Excel":
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        if rows:
            ws.append(list(rows[0].keys()))
            for row in rows:
                ws.append(list(row.values()))
        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()

    raise ValueError(f"Unknown format: {fmt}")


def make_watermark_txt(watermark_id: str, downloaded_at: str, user_id: str, selected_files: list[str]) -> bytes:
    """Generate a watermark.txt to include in the zip."""
    lines = [
        "Burbio Data Download Receipt",
        "=" * 30,
        f"ID Code:         {watermark_id}",
        f"Date Downloaded: {downloaded_at}",
        f"User:            {user_id}",
        "",
        "Files included:",
    ] + [f"  - {f}" for f in selected_files] + [
        "",
        "This data is licensed for authorized use only.",
        "Redistribution without permission is prohibited.",
    ]
    return "\n".join(lines).encode("utf-8")


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Burbio – Download", page_icon="📊", layout="centered")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.subheader("Burbio")

st.divider()

# ── Session state init ────────────────────────────────────────────────────────
if "dl_ready" not in st.session_state:
    st.session_state.dl_ready = False
    st.session_state.dl_zip   = None

# ── Read token from URL ───────────────────────────────────────────────────────
token = st.query_params.get("token")

if not token:
    st.error("This link is invalid or expired. Please check your email for the correct download link.")
    st.stop()

# ── Validate token ────────────────────────────────────────────────────────────
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

    user_id = row.get("user_id", "unknown")

    # ── File selection UI ─────────────────────────────────────────────────────
    st.header("Your files are ready to download")
    st.warning("These files are for your authorized use only.")

    selected_files = [f for f in ALL_FILES if st.checkbox(f, value=True, key=f"chk_{f}")]

    fmt_choice = st.radio(
        "Choose your download format",
        list(FORMATS.keys()),
        horizontal=True,
    )

    if st.button("Download Selected Files", type="primary", use_container_width=True):
        if not selected_files:
            st.warning("Please select at least one file.")
            st.stop()

        watermark_id  = generate_watermark_id()
        downloaded_at = datetime.now(timezone.utc).isoformat()

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add watermark.txt
            zf.writestr("watermark.txt", make_watermark_txt(watermark_id, downloaded_at, user_id, selected_files))

            # Add each selected file, clean with no watermark in data
            for file_id in selected_files:
                with st.spinner(f"Fetching {file_id}…"):
                    try:
                        text = fetch_file(file_id)
                    except requests.exceptions.HTTPError as e:
                        st.error(f"Could not fetch {file_id} ({e.response.status_code}): {e.response.text}")
                        continue
                    except Exception as e:
                        st.error(f"Error fetching {file_id}: {e}")
                        continue

                rows = list(csv.DictReader(io.StringIO(text, newline='')))
                base_name = os.path.splitext(file_id)[0]
                filename  = base_name + FORMATS[fmt_choice]["ext"]
                data      = rows_to_bytes(rows, fmt_choice)
                zf.writestr(filename, data)

        # Write watermark ID to Supabase and mark token as used
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/download_links?id=eq.{token}",
            headers=HEADERS,
            json={"used": True, "watermark_id": watermark_id},
            timeout=10,
        )

        zip_buffer.seek(0)
        st.session_state.dl_ready = True
        st.session_state.dl_zip   = zip_buffer.getvalue()
        st.rerun()

# ── Download ready ────────────────────────────────────────────────────────────
if st.session_state.dl_ready:
    st.success("Your files are ready — click below to save them.")
    st.download_button(
        label="Save All Files (.zip)",
        data=st.session_state.dl_zip,
        file_name="burbio_files.zip",
        mime="application/zip",
        use_container_width=True,
    )