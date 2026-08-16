import streamlit as st
from google import genai
from PIL import Image
import os

# --- Configuration ---
# The API key is now read from an environment variable, never hardcoded.
# Set it before running:
#   macOS/Linux:  export GEMINI_API_KEY="your-new-key-here"
#   Windows CMD:  set GEMINI_API_KEY=your-new-key-here
#   Windows PS :  $env:GEMINI_API_KEY="your-new-key-here"
API_KEY = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

st.set_page_config(
    page_title="forensicAI - Crime Scene Analysis",
    page_icon="🔎",
    layout="centered",
)

# --- Simple dark "case file" styling ---
st.markdown(
    """
    <style>
    .stApp { background-color: #1a1a1a; color: white; }
    h1 { color: #ff4444 !important; font-family: 'Courier New', monospace; }
    .stTextArea textarea { background-color: #2b2b2b; color: white; }
    .stButton button {
        background-color: #b30000; color: white; font-weight: bold;
        width: 100%; height: 3em;
    }
    /* Force readable text color on labels, headers, and body text everywhere */
    label, p, span, div, h2, h3, h4,
    .stMarkdown, .stMarkdown p,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploaderDropzoneInstructions"] {
        color: white !important;
    }
    /* File uploader "Browse files" button needs its own contrast fix */
    [data-testid="stFileUploaderDropzone"] button {
        background-color: #444 !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("CRIME CASE ANALYSER")

if not API_KEY:
    st.error(
        "No API key found. Set the GEMINI_API_KEY environment variable before "
        "running this app (see the comment at the top of app.py)."
    )
    st.stop()

client = genai.Client(api_key=API_KEY)

case_data = st.text_area(
    "Enter case details, clues, and alibis:",
    height=250,
    placeholder="e.g. Victim found at 9pm in the study. Suspect A claims to have been at a restaurant...",
)

uploaded_image = st.file_uploader(
    "Attach scene photo (optional)", type=["jpg", "jpeg", "png"]
)

image = None
if uploaded_image is not None:
    image = Image.open(uploaded_image)
    st.image(image, caption="Attached scene photo", use_container_width=True)

analyze_clicked = st.button("RUN FORENSIC ANALYSIS")

PROMPT = """analyze the crime scene data.
1. List key physical evidence.
2. Evaluate suspect alibis for logic gaps.
3. Rank suspect by probability of guilt(%).
4. Identify the most likely culprit and the motive.
Format the output clearly with headers.
"""

if analyze_clicked:
    if not case_data.strip() and image is None:
        st.warning("Please provide text details or an image of the crime scene.")
    else:
        content = [PROMPT]
        if case_data.strip():
            content.append(f"case file.\n{case_data.strip()}")
        if image is not None:
            content.append(image)

        with st.spinner("AI is examining evidence..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=content,
                )
                st.subheader("AI Findings")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
