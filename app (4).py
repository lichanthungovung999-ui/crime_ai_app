import streamlit as st
from google import genai
from PIL import Image
import os

# --- Configuration ---
# The API key is read from an environment variable locally, or from
# Streamlit Cloud's Secrets when deployed. Never hardcode it here.
#   macOS/Linux:  export GEMINI_API_KEY="your-new-key-here"
#   Windows CMD:  set GEMINI_API_KEY=your-new-key-here
#   Windows PS :  $env:GEMINI_API_KEY="your-new-key-here"
API_KEY = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

st.set_page_config(
    page_title="forensicAI - Crime Scene Analysis",
    page_icon="🔎",
    layout="centered",
)

# --- Advanced "case file" styling ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&family=Oswald:wght@500;600&display=swap');

    .stApp {
        background: radial-gradient(circle at 20% 0%, #241414 0%, #141414 45%, #0d0d0d 100%);
        color: #e8e8e8;
    }

    /* Remove default top padding so the title sits nicer */
    .block-container { padding-top: 2.5rem; padding-bottom: 3rem; }

    h1 {
        color: #ff4b4b !important;
        font-family: 'Oswald', sans-serif;
        letter-spacing: 3px;
        text-shadow: 0 0 18px rgba(255, 60, 60, 0.35);
        border-bottom: 2px solid #4a1414;
        padding-bottom: 14px;
        margin-bottom: 6px !important;
    }

    /* subtitle under the title */
    .case-subtitle {
        color: #999;
        font-family: 'Courier Prime', monospace;
        font-size: 0.85rem;
        letter-spacing: 2px;
        margin-bottom: 28px;
    }

    /* Card-style bordered containers (st.container(border=True)) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(180deg, #1c1c1c 0%, #171717 100%);
        border: 1px solid #3a2020 !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255,255,255,0.02);
        padding: 6px 4px;
        margin-bottom: 22px;
    }

    /* Section labels styled like case-file tags */
    .section-label {
        color: #ff8080;
        font-family: 'Oswald', sans-serif;
        font-size: 0.78rem;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        margin: 4px 0 10px 2px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-label::before {
        content: "";
        width: 8px; height: 8px;
        background: #ff4b4b;
        border-radius: 50%;
        box-shadow: 0 0 8px #ff4b4b;
        display: inline-block;
    }

    .stTextArea textarea {
        background-color: #101010 !important;
        color: #e8e8e8 !important;
        border: 1px solid #333 !important;
        border-radius: 10px !important;
        font-family: 'Courier Prime', monospace;
    }
    .stTextArea textarea:focus {
        border: 1px solid #ff4b4b !important;
        box-shadow: 0 0 0 1px #ff4b4b33 !important;
    }

    .stButton button {
        background: linear-gradient(180deg, #d61f1f 0%, #9c0f0f 100%);
        color: white; font-weight: 700; letter-spacing: 1.5px;
        font-family: 'Oswald', sans-serif;
        width: 100%; height: 3.2em;
        border: 1px solid #ff6b6b55 !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(180, 20, 20, 0.35);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(255, 60, 60, 0.5);
        border: 1px solid #ff4b4b !important;
        color: white !important;
    }

    /* Results terminal look */
    .terminal-box {
        background: #0a0e0a;
        border: 1px solid #1f3d1f;
        border-radius: 10px;
        padding: 18px 20px;
        font-family: 'Courier Prime', monospace;
        color: #4dff4d;
        box-shadow: inset 0 0 24px rgba(0, 255, 0, 0.05), 0 0 16px rgba(0,255,0,0.08);
        white-space: pre-wrap;
        line-height: 1.55;
    }

    /* Force readable text color on labels and body text everywhere */
    label, p, span,
    .stMarkdown, .stMarkdown p,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploaderDropzoneInstructions"] {
        color: #dcdcdc !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        background-color: #101010 !important;
        border: 1px dashed #3a2020 !important;
        border-radius: 10px !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        background-color: #2b2b2b !important;
        color: white !important;
        border-radius: 8px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("CRIME CASE ANALYSER")
st.markdown('<div class="case-subtitle">CASE FILE // AI FORENSIC REVIEW UNIT</div>', unsafe_allow_html=True)

if not API_KEY:
    st.error(
        "No API key found. Set the GEMINI_API_KEY environment variable before "
        "running this app (see the comment at the top of app.py)."
    )
    st.stop()

client = genai.Client(api_key=API_KEY)

with st.container(border=True):
    st.markdown('<div class="section-label">Case Details</div>', unsafe_allow_html=True)
    case_data = st.text_area(
        "Enter case details, clues, and alibis:",
        height=220,
        placeholder="e.g. Victim found at 9pm in the study. Suspect A claims to have been at a restaurant...",
        label_visibility="collapsed",
    )

with st.container(border=True):
    st.markdown('<div class="section-label">Scene Evidence</div>', unsafe_allow_html=True)
    uploaded_image = st.file_uploader(
        "Attach scene photo (optional)", type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
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

Write the whole answer in simple, plain, everyday language — as if
explaining it to someone with no legal or forensic background. Avoid
technical jargon and complicated words; use short sentences instead.
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
                st.markdown('<div class="section-label">AI Findings</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="terminal-box">{response.text}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred: {e}")
