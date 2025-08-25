import streamlit as st
import os
import io
import pickle
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# ----------------------------
# App Config
# ----------------------------
st.set_page_config(page_title="📤 Google Drive Upload", page_icon="📁")
st.title("📁 Upload File to Google Drive")

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
TOKEN_FILE = "token.pickle"
FOLDER_ID = "1lVsJ3-CjtgKaAyBszmaDWEC6MaOVpZwV"  # ← अपनी Drive Folder ID

# ----------------------------
# Embedded credentials.json content
# ----------------------------
credentials_dict = {
    "installed": {
        "client_id": "876158418541-qb3no5vc0ri6fse3hdka6vfhpa8nnn64.apps.googleusercontent.com",
        "project_id": "my-project9-470014",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": ["http://localhost"]
    }
}

# ----------------------------
# Build Drive service only (no widgets)
# ----------------------------
@st.cache_resource
def build_drive_service(creds):
    return build("drive", "v3", credentials=creds)

# ----------------------------
# Load or request credentials
# ----------------------------
creds = None
if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "rb") as token:
        creds = pickle.load(token)

if not creds:
    flow = Flow.from_client_config(
        credentials_dict,
        scopes=SCOPES,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob"
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.markdown(f"🔐 [Click here to authorize Google Drive access]({auth_url})", unsafe_allow_html=True)

    auth_code = st.text_input("🔑 Paste the authorization code here:")

    if auth_code:
        try:
            flow.fetch_token(code=auth_code)
            creds = flow.credentials
            with open(TOKEN_FILE, "wb") as token:
                pickle.dump(creds, token)
            st.success("✅ Authorization successful! Please reload the app.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Authorization failed: {e}")
            st.stop()

# ----------------------------
# Use the drive service if creds are ready
# ----------------------------
if creds:
    drive_service = build_drive_service(creds)
else:
    st.warning("⚠️ App not authorized yet.")
    st.stop()

# ----------------------------
# File Upload Section
# ----------------------------
uploaded_file = st.file_uploader("📂 Upload any file to Google Drive")

if uploaded_file is not None:
    st.info(f"📤 Uploading `{uploaded_file.name}`...")

    file_metadata = {
        'name': uploaded_file.name,
        'parents': [FOLDER_ID]
    }

    media = MediaIoBaseUpload(io.BytesIO(uploaded_file.getvalue()), mimetype=uploaded_file.type)

    try:
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        st.success("✅ File uploaded successfully!")
        st.markdown(f"[🔗 Open File](https://drive.google.com/file/d/{file['id']})", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Upload failed: {e}")