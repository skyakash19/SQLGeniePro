#from database import list_columns, list_databases, list_tables

import os
import streamlit as st # type: ignore
import requests # type: ignore
import pandas as pd # type: ignore
import time
import random
from PIL import Image # type: ignore
import logging
logging.getLogger("tornado.application").setLevel(logging.ERROR)

from pathlib import Path
import base64
import random

import time
import streamlit as st # type: ignore

import time
import json
import plotly.express as px # type: ignore
import plotly.graph_objects as go # type: ignore
import re

# -------------------- 1. PAGE CONFIGURATION & CSS (Unified) --------------------
st.set_page_config(
    page_title="🔮 SQLGenie Pro — Whisper to the Oracle",
    page_icon="🧞‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Consolidated CSS from all pages ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Uncial+Antiqua&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&family=UnifrakturCook:wght@700&display=swap');
    
    /* Main App Body */
    .stApp {
        background: linear-gradient(135deg, #2b0057, #4e1a8a);
        background-attachment: fixed;
        font-family: 'Segoe UI', sans-serif;
        color: #f5f5f5;
    }
    
    /* Headers & Titles */
    .header-container {
        background: linear-gradient(145deg, #05000c, #1a0f2e);
        padding: 3.2rem 1.5rem; text-align: center;
        border-bottom: 2px solid #d4af37;
        box-shadow: inset 0 0 60px #d4af3777;
        border-radius: 0 0 30px 30px;
        font-family: 'Uncial Antiqua', serif;
    }
    .header-title {
        font-size: 3.4rem; font-weight: 700; color: #d4af37;
        letter-spacing: 2px; text-shadow: 0 0 25px #b8860b, 0 0 40px #ffd700;
        margin-bottom: 1.4rem;
    }
    .header-subtitle {
        font-size: 1.4rem; font-weight: 600; color: #e6c200;
        margin-top: -0.5rem; margin-bottom: 1rem; text-shadow: 0 0 12px #daa520aa;
    }
    h1, h2, h3 { color: #d8b4fe; text-shadow: 0 0 12px #c084fc, 0 0 20px #a855f7; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(-45deg, #1a0033, #32014f, #180028, #2a0059);
        background-size: 600% 600%;
        animation: glowingBackground 25s ease infinite;
        font-family: 'Cinzel Decorative', cursive;
        border-right: 3px solid #9a45ff;
        box-shadow: inset 0 0 40px #000000cc;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label {
        font-family: 'UnifrakturCook', cursive; color: #f5d9ff;
        text-shadow: 0 0 12px #bf80ff; letter-spacing: 1px;
    }
    [data-testid="stSidebar"] button {
        background-color: #2a004d; color: #fff; border: 2px solid #c280ff;
        border-radius: 12px; padding: 8px 16px; font-size: 15px; font-weight: bold;
        box-shadow: 0 0 15px #a84be4; transition: all 0.4s ease-in-out;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: #4b007a; color: #ffeaff; transform: scale(1.07);
        box-shadow: 0 0 30px #dfbfff, 0 0 15px #bf80ff inset;
    }

    /* Main Content Buttons & Containers */
    .stButton>button {
        background-color: #a855f7; color: #ffffff; border-radius: 12px;
        border: 1px solid #c084fc; padding: 0.7em 1.4em; font-weight: bold;
        box-shadow: 0 0 15px rgba(168, 85, 247, 0.6); transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #7e22ce; box-shadow: 0 0 20px rgba(126, 34, 206, 0.7);
    }
    
    /* Background Animation */
    @keyframes glowingBackground {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    /* --- Welcome Page Styling --- */
    .stApp {{
        background: #0B0B1E;
        background-image: linear-gradient(rgba(11,11,30,0.35), rgba(11,11,30,0.35)), url("data:image/jpeg;base64,{bg_img_base64 if 'bg_img_base64' in st.session_state else ''}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #FFD700;
        text-align: center;
    }}
    .welcome-title {{
        font-family: 'Cinzel', serif; font-size: 3rem; margin-top: 3rem;
        text-shadow: 0 0 12px rgba(255, 215, 0, 0.4);
    }}
    .welcome-text {{
        font-family: 'Playfair Display', serif; font-size: 1.3rem;
        line-height: 1.8; color: #f0e6d2; max-width: 800px;
        margin: 1.5rem auto;
    }}
    .welcome-quote {{
        color: #ffec8b; font-style: italic; font-size: 1.2rem;
        text-shadow: 0 0 8px rgba(255, 236, 139, 0.5);
    }}
    .button-container {{
        display: flex; justify-content: center; gap: 20px;
        margin-top: 2rem;
    }}
    .genie-box {{
        font-family: 'Cormorant Garamond', serif;
        color: #F0E6D2; background: rgba(20, 20, 40, 0.85);
        border-radius: 15px; padding: 3rem;
        border: 1px solid #C0A880; box-shadow: 0 0 20px rgba(192, 168, 128, 0.2);
        backdrop-filter: none; max-width: 700px;
        margin: auto; text-align: center;
        transition: all 0.5s ease;
    }}
    
    /* --- About Page Styling --- */
    .about-container {{
        background: rgba(15, 12, 41, 0.8);
        border-radius: 15px; padding: 3rem;
        border: 2px solid #a855f7; margin-top: 2rem;
        box-shadow: 0 0 20px rgba(168, 85, 247, 0.5);
    }}
    .tech-list li {{
        font-size: 1.1rem; margin-bottom: 0.5rem;
    }}
    .tech-title {{
        color: #c084fc; font-weight: bold; font-size: 1.2rem;
    }}
</style>
""", unsafe_allow_html=True)


# -------------------- 2. UNIFIED CSS STYLING --------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Uncial+Antiqua&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&family=UnifrakturCook:wght@700&display=swap');

    /* --- Main App Body --- */
    .stApp {
        background: linear-gradient(135deg, #2b0057, #4e1a8a);
        background-attachment: fixed;
        font-family: 'Segoe UI', sans-serif;
        color: #f5f5f5;
    }

    /* --- Headers & Titles --- */
    .header-container {
        background: linear-gradient(145deg, #05000c, #1a0f2e);
        padding: 3.2rem 1.5rem; text-align: center;
        border-bottom: 2px solid #d4af37;
        box-shadow: inset 0 0 60px #d4af3777;
        border-radius: 0 0 30px 30px;
        font-family: 'Uncial Antiqua', serif;
    }
    .header-title {
        font-size: 3.4rem; font-weight: 700; color: #d4af37;
        letter-spacing: 2px; text-shadow: 0 0 25px #b8860b, 0 0 40px #ffd700;
        margin-bottom: 1.4rem;
    }
    .header-subtitle {
        font-size: 1.4rem; font-weight: 600; color: #e6c200;
        margin-top: -0.5rem; margin-bottom: 1rem; text-shadow: 0 0 12px #daa520aa;
    }
    h1, h2, h3 { color: #d8b4fe; text-shadow: 0 0 12px #c084fc, 0 0 20px #a855f7; }

    /* --- Sidebar --- */
    [data-testid="stSidebar"] {
        background: linear-gradient(-45deg, #1a0033, #32014f, #180028, #2a0059);
        background-size: 600% 600%;
        animation: glowingBackground 25s ease infinite;
        font-family: 'Cinzel Decorative', cursive;
        border-right: 3px solid #9a45ff;
        box-shadow: inset 0 0 40px #000000cc;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label {
        font-family: 'UnifrakturCook', cursive; color: #f5d9ff;
        text-shadow: 0 0 12px #bf80ff; letter-spacing: 1px;
    }
    [data-testid="stSidebar"] button {
        background-color: #2a004d; color: #fff; border: 2px solid #c280ff;
        border-radius: 12px; padding: 8px 16px; font-size: 15px; font-weight: bold;
        box-shadow: 0 0 15px #a84be4; transition: all 0.4s ease-in-out;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: #4b007a; color: #ffeaff; transform: scale(1.07);
        box-shadow: 0 0 30px #dfbfff, 0 0 15px #bf80ff inset;
    }

    /* --- Main Content Buttons & Containers --- */
    .stButton>button {
        background-color: #a855f7; color: #ffffff; border-radius: 12px;
        border: 1px solid #c084fc; padding: 0.7em 1.4em; font-weight: bold;
        box-shadow: 0 0 15px rgba(168, 85, 247, 0.6); transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #7e22ce; box-shadow: 0 0 20px rgba(126, 34, 206, 0.7);
    }
    
    /* Background Animation */
    @keyframes glowingBackground {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
</style>
""", unsafe_allow_html=True)

# -------------------- 3. API & SESSION STATE SETUP --------------------
API_URL = "http://127.0.0.1:8000"

# Initialize session state keys
if 'page' not in st.session_state:
    st.session_state['page'] = 'welcome'  # CORRECTED: Start at the welcome page
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'auth_token' not in st.session_state:
    st.session_state['auth_token'] = ""
if 'generated_sql' not in st.session_state:
    st.session_state['generated_sql'] = ""
if 'manual_sql_query' not in st.session_state:
    st.session_state['manual_sql_query'] = ""
if 'query_results' not in st.session_state:
    st.session_state['query_results'] = None
if 'execution_error' not in st.session_state:
    st.session_state['execution_error'] = ""
if 'query_history' not in st.session_state:
    st.session_state['query_history'] = []
if 'columns' not in st.session_state:
    st.session_state['columns'] = []

# -------------------- 4. API HELPER FUNCTIONS --------------------
def register_user(username, password):
    return requests.post(f"{API_URL}/register", json={"username": username, "password": password})

def login_user(username, password):
    return requests.post(f"{API_URL}/token", data={"username": username, "password": password})

import google.generativeai as genai  # type: ignore # ✅ Correct Gemini import
from dotenv import load_dotenv # type: ignore
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # ✅ Set your Gemini API key
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

def call_gemini_chat(prompt):
    response = gemini_model.generate_content(prompt)
    return response.text


def execute_sql_query(query):
    if query.strip():
        with st.spinner("🔄 Casting your SQL spell..."):
            start = time.time()
            # --- CORRECTED CODE ---
            response = requests.post(
                f"{API_URL}/execute_sql/",
                json={ # ✅ CORRECT: This sends a JSON body
                    "query": query, # ✅ CORRECT: Matches Pydantic model
                    "db_name": st.session_state.get("selected_db", "default")
                },
                headers=get_auth_header()
            )
            duration = time.time() - start

            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data.get("results", []))
                st.session_state['query_results'] = {
                    "data": df,
                    "execution_time": duration,
                    "optimization_tips": data.get("optimization_tips", "No tips available.")
                }
                st.success(f"⚡ Spell casted in {duration:.2f} seconds!")
            else:
                error_detail = response.json().get("detail", f"Code {response.status_code}")
                st.error(f"❌ Execution Error: {error_detail}")
                st.session_state['query_results'] = None
    else:
        st.warning("📝 Please enter a SQL query.")


def rerun_with_suggestion(suggestion):
    original_query = st.session_state.get("manual_sql_query_input", "")
    corrected_query = re.sub(r"'[^']+'", f"'{suggestion}'", original_query)

    response = execute_sql_query(corrected_query)
    st.session_state['execution_result'] = response
    st.session_state['manual_sql_query_input'] = corrected_query

import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Load and encode your background image
bg_img_base64 = get_base64_image("bodugenie.png")  # Change file name to your actual image


def get_auth_header():
    token = st.session_state.get('auth_token')
    if not token:
        st.error("Authentication token not found. Please log in again.")
        st.session_state['logged_in'] = False
        st.rerun()
    return {"Authorization": f"Bearer {token}"}

# --- ADD THIS NEW HELPER FUNCTION ---
def authenticated_get(endpoint):
    """A wrapper to make authenticated GET requests to the backend."""
    return requests.get(f"{API_URL}/{endpoint}", headers=get_auth_header())

def render_hero_section(image_file, title, quote):
    """Renders a cinematic hero section with text overlaid on a background image, ensuring full visibility."""
    import base64

    # --- Encode the image to Base64 ---
    def get_image_as_base64(file_path):
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except FileNotFoundError:
            st.error(f"Error: Image file '{file_path}' not found.")
            return None

    img_base64 = get_image_as_base64(image_file)

    if img_base64:
        image_url = f"data:image/png;base64,{img_base64}" # Assuming PNG
    else:
        image_url = ""

    # --- Hero Section Styling with 'contain' and fallback ---
    st.markdown(f"""
    <style>
        .hero-container {{
            position: relative;
            color: white;
            text-align: center;
            border-radius: 20px;
            overflow: hidden;
            min-height: 400px; /* Ensure a minimum height */
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 2rem;
            box-shadow: inset 0 0 150px rgba(0,0,0,0.7);
            background-image: url("{image_url}");
            background-size: contain; /* Show the whole image */
            background-repeat: no-repeat;
            background-position: center;
            /* Fallback background color/gradient if the image doesn't cover the whole area */
            background-color: #0B0B0B; /* Dark background */
        }}
        .hero-title {{
            font-family: 'Cinzel Decorative', serif;
            font-size: 3.5rem;
            font-weight: 700;
            color: #ffd700;
            text-shadow: 0 0 25px #b8860b, 0 0 40px #ffd700;
            margin-bottom: 1rem;
        }}
        .hero-quote {{
            font-size: 1.5rem;
            font-style: italic;
            color: #e0e0e0;
            text-shadow: 2px 2px 4px #000;
            max-width: 80%;
        }}
    </style>

    <div class="hero-container">
        <div class="hero-title">I AM THE GENIE OF THE QUERY</div>
        <p class="hero-quote">"{quote}"</p>
    </div>
    """, unsafe_allow_html=True)

# -------------------- 5. PAGE RENDERING LOGIC --------------------
import streamlit as st # type: ignore
from pathlib import Path
import base64
import random


def get_image_as_base64(file_path: Path) -> str:
    """Read image and return base64 string."""
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.warning(f"⚠️ Image '{file_path.name}' not found in {file_path.parent}")
        return ""


def render_welcome_page():
    

    # Path to assets
    assets_dir = Path(__file__).parent
    bg_img_base64 = get_image_as_base64(assets_dir / "bodugenie.png")

    # Persistent random quote selection
    if "chosen_quote" not in st.session_state:
        quotes = [
            "✨ The universe is made of stories, not of atoms.",
            "🌌 The greatest secrets are always hidden in the most unlikely places.",
            "💫 Logic will get you from A to B. Imagination will take you everywhere."
        ]
        st.session_state.chosen_quote = random.choice(quotes)

    # --- Styling (No Box) ---
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Cinzel:wght@500;700&display=swap');

    .stApp {{
        background: #0B0B1E;
        background-image: linear-gradient(rgba(11,11,30,0.35), rgba(11,11,30,0.35)), 
                          url("data:image/jpeg;base64,{bg_img_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #FFD700;
        text-align: center;
    }}

    .welcome-title {{
        font-family: 'Cinzel', serif;
        font-size: 3rem;
        margin-top: 3rem;
        text-shadow: 0 0 12px rgba(255, 215, 0, 0.4);
    }}

    .welcome-text {{
        font-family: 'Playfair Display', serif;
        font-size: 1.3rem;
        line-height: 1.8;
        color: #f0e6d2;
        max-width: 800px;
        margin: 1.5rem auto;
    }}

    .welcome-quote {{
        color: #ffec8b;
        font-style: italic;
        font-size: 1.2rem;
        text-shadow: 0 0 8px rgba(255, 236, 139, 0.5);
    }}

    .button-container {{
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 2rem;
    }}

    .stButton > button {{
        background-color: #FFD700;
        color: #0B0B1E;
        font-family: 'Playfair Display', serif;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
        transition: all 0.3s ease;
    }}

    .stButton > button:hover {{
        transform: scale(1.05);
        background-color: #e6c200;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.7);
    }}
    </style>
    """, unsafe_allow_html=True)
    #st.markdown("<p style='text-align:center; font-style:italic;'>Where ancient elegance meets AI-powered prophecy.</p>", unsafe_allow_html=True)
    # --- Text Content ---
    st.markdown(f"""
    <h2 class="welcome-title">⚜ Welcome, Seeker ⚜</h2>
    <p style='text-align:center; font-style:italic;'>Where ancient elegance meets AI-powered prophecy.</p>
    <p class="welcome-text">
        Beyond the veil of numbers lies a world unseen — a realm where data breathes, whispers, 
        and reveals the fate of those bold enough to ask.  
    </p>
    
    <p class="welcome-text">
        Dare to seek, and the currents of insight shall bend to your will.
    </p>
    <p class="welcome-quote">{st.session_state.chosen_quote}</p>
    """, unsafe_allow_html=True)


    # --- Buttons ---
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🗝️ Login, Rub the Lamp", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()
    with col2:
        if st.button("📜 Sign Up", use_container_width=True):
            st.session_state.page = 'signup'
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def render_login_page():
    import streamlit as st # type: ignore
    import time
    import random
    import base64
    import os

    # --- Utility function to encode the background image to Base64 ---
    # --- Utility function to encode image to Base64 ---
    def get_image_as_base64(file_path):
        """Encodes a local image file into a Base64 string, with error handling."""
        import base64
        import os
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except FileNotFoundError:
            st.warning(f"Background image '{file_path}' not found. Displaying fallback gradient.")
            return None

    # --- Encode your background image ---
    # NOTE: Replace "genlamp.jpg" with the path to your desired background image
    img_base64 = get_image_as_base64("smooth-gradient-light-blur-wallpaper-with-a-simple-purple-plain-background-texture_9980781.jpg!sw800")

    # --- Create the background CSS with a beautiful fallback gradient ---
    if img_base64:
        background_css = f"""
            background-image: url("data:image/jpeg;base64,{img_base64}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        """
    else:
        # This is the beautiful gradient that will be shown if the image fails to load
        background_css = """
            background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1e1e1e);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
        """

    # ===== Random Genie Quote =====
    quotes = [
        "✨ *Seek, and the Genie shall answer.*",
        "🌌 *The stars whisper your destiny.*",
        "💫 *Your wish is but a breath away.*",
        "🔥 *Power beyond imagination awaits you.*"
    ]
    chosen_quote = random.choice(quotes)

    # ================= Cinematic Genie Login Page =================
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&display=swap');

        /* --- Full-screen background image and overlay --- */
        .stApp {{
            {background_css}
        }}
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(-45deg, rgba(15, 12, 41, 0.8), rgba(48, 43, 99, 0.8), rgba(36, 36, 62, 0.9), rgba(30, 30, 30, 0.9));
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            z-index: -1;
        }}
        @keyframes gradientShift {{
            0% {{background-position: 0% 50%;}} 50% {{background-position: 100% 50%;}} 100% {{background-position: 0% 50%;}}
        }}

        /* --- Animations for Glow and Shimmer --- */
        @keyframes glowing-border {{
            0% {{ box-shadow: 0 0 20px rgba(212, 175, 55, 0.6); }}
            50% {{ box-shadow: 0 0 40px rgba(255, 215, 0, 1); }}
            100% {{ box-shadow: 0 0 20px rgba(212, 175, 55, 0.6); }}
        }}
        @keyframes text-shimmer {{
            0% {{ text-shadow: 0 0 15px #daa520; }} 50% {{ text-shadow: 0 0 30px #ffd700; }} 100% {{ text-shadow: 0 0 15px #daa520; }}
        }}

        /* --- Glassmorphism Login Box --- */
        .login-container {{
            background: rgba(15, 12, 41, 0.8);
            border-radius: 20px;
            padding: 2.5rem;
            border: 2px solid #b8860b;
            backdrop-filter: blur(8px);
            animation: glowing-border 5s ease-in-out infinite;
        }}

        input:focus {{
        border: 2px solid #ffd700 !important;
        box-shadow: 0 0 10px #ffd700;
        }}


        /* --- Themed Text --- */
        .genie-greeting {{
            font-family: 'Cinzel Decorative', serif; color: #ffd700;
            text-align: center; font-size: 3rem;
            animation: text-shimmer 4s ease-in-out infinite;
        }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    .genie-icon {
        width: 60px;
        cursor: pointer;
        transition: transform 0.3s ease;
    }
    .genie-icon:hover {
        transform: scale(1.2);
    }
    </style>

    
    """, unsafe_allow_html=True)



    # Page config for cinematic feel
    #st.set_page_config(page_title="SQLGenie Pro", layout="wide")

    # Custom fonts and styling
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Cormorant+Garamond&display=swap');

        .mythic-text {
            font-family: 'Cinzel', serif;
            font-size: 32px;
            color: gold;
            margin-bottom: 10px;
        }

        .mythic-subtext {
            font-family: 'Cormorant Garamond', serif;
            font-size: 18px;
            color: #ddd;
            line-height: 1.6;
        }

        .login-box input {
            border: 2px solid gold;
            border-radius: 8px;
            padding: 10px;
            background-color: #111;
            color: white;
            width: 100%;
        }

        .login-box label {
            color: gold;
            font-family: 'Cinzel', serif;
        }
        </style>
    """, unsafe_allow_html=True)

    # Layout: Two columns
    left, right = st.columns([2, 1])

    with left:
        #st.markdown("<div class='mythic-text'>✨ Welcome, Seeker of Queries</div>", unsafe_allow_html=True)
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Cormorant+Garamond&display=swap');

            .mythic-container {
                background: url('asd.jpg') no-repeat center center;
                background-size: cover;
                padding: 40px;
                border-radius: 12px;
                animation: fadeIn 2s ease-in;
                box-shadow: 0 0 30px rgba(255, 215, 0, 0.3);
            }

            .mythic-subtext {
                font-family: 'Cormorant Garamond', serif;
                font-size: 18px;
                color: #f0e6d2;
                line-height: 1.8;
                text-shadow: 0 0 5px #000;
            }

            .mythic-title {
                font-family: 'Cinzel', serif;
                font-size: 32px;
                color: gold;
                margin-bottom: 20px;
                text-shadow: 0 0 10px #ffd700;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            </style>

            <div class="mythic-container">
                <div class="mythic-title">✨ Welcome, Seeker of Queries</div>
                <div class="mythic-subtext">
                    Before you step into the chamber of SQLGenie, know this:<br><br>
                    The Genie awaits not just your credentials, but your intent.<br><br>
                    Summon wisely. Ask boldly. And let your data dreams unfold in gold and shadow.<br><br>
                    Within these walls, queries are not merely executed—they are conjured.<br><br>
                    Each keystroke is a whisper to the unseen, each result a revelation from the depths.<br><br>
                    You do not log in—you awaken the ancient engine of insight.<br><br>
                    So steady your mind, align your purpose, and prepare to wield the power of precision.<br><br>
                    The scrolls are ready. The runes are aligned. The Genie listens.
                </div>
            </div>

        """, unsafe_allow_html=True)

        

    with right:
        st.markdown("### 🧞 Summon the Genie")
        st.image("genie-entrance1.gif", width=300)


    # ================= Layout =================
    st.write("") # Margin top
    left_col, right_col = st.columns([0.6, 0.4], gap="large")

    with left_col:
        # Define the content for your hero section
        hero_title = "I AM THE GENIE OF THE QUERY"
        hero_quote = chosen_quote # Assumes 'chosen_quote' is defined earlier
        hero_image = "genlamp.jpg" # Use the filename of your uploaded image

        # Render the hero section with the genie image
        render_hero_section(hero_image, hero_title, hero_quote)

    with right_col:
        # 🧞 Genie Icon + Button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("genie-entrance.gif", width=60)
            if st.button("🧞 Summon the Genie", help="Click to awaken the magic"):
                st.success("✨ The Genie has been summoned! Your wish is my command.")
                st.markdown("""
                <div style='text-align:center; font-size:24px; color:#ffd700; animation: shimmer 2s infinite;'>
                Your wish is granted!
                </div>

                <style>
                @keyframes shimmer {
                0% { text-shadow: 0 0 10px #daa520; }
                50% { text-shadow: 0 0 20px #ffd700; }
                100% { text-shadow: 0 0 10px #daa520; }
                }
                \</style>
                """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("<h3 style='text-align:center;'>🗝️ The Portal of Truth</h3>", unsafe_allow_html=True)
            st.write("")  # Adds vertical space

            # 🧞 Pre-fill username if remembered
            if 'remembered_user' in st.session_state:
                username = st.text_input("📜 **Name**", value=st.session_state['remembered_user'], placeholder="e.g., Aladdin")
            else:
                username = st.text_input("📜 **Name**", placeholder="e.g., Aladdin")

            # 🔐 Password input with reveal toggle
            show_password = st.checkbox("Reveal Passphrase")
            password = st.text_input("🔮 **Passphrase**", type="default" if show_password else "password", placeholder="e.g., open sesame")

            # 🧠 Remember Me checkbox
            remember_me = st.checkbox("🧠 Remember Me")

            st.write("")  # Adds vertical space

            # --- Centering the button using columns ---
            _, btn_col, _ = st.columns([1, 2, 1])
            with btn_col:
                submitted = st.form_submit_button("✨ Enter the Cave", use_container_width=True)

            if submitted:
                if not username or not password:
                    st.warning("⚠️ You must fill in both fields!")
                else:
                    with st.spinner("Verifying your worthiness..."):
                        response = login_user(username, password)
                        if response.status_code == 200:
                            # ✅ Save token and login state
                            st.session_state.update({
                                'auth_token': response.json()['access_token'],
                                'logged_in': True,
                                'page': 'main_app'
                            })

                            # 🧠 Save remembered user if checkbox is ticked
                            if remember_me:
                                st.session_state['remembered_user'] = username
                            else:
                                st.session_state.pop('remembered_user', None)  # Clear if unchecked

                            st.success("✅ Access Granted! The lamp has spoken — welcome back, Master. The code awaits your command.")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Access Denied! The lamp remains silent. Only the worthy may pass. Incorrect credentials.")

        st.markdown("<hr style='border-color: #b8860b;'>", unsafe_allow_html=True)


        # --- Centering the second button using columns ---
        _, btn_col2, _ = st.columns([0.5, 2, 0.5])
        with btn_col2:
            if st.button("🌟 New Seeker? Begin your legend here!", use_container_width=True):
                st.session_state['page'] = 'signup'
                st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

def render_signup_page():
    import streamlit as st # type: ignore
    import time
    import re

    # --- Utility function for password strength ---
    def check_password_strength(password):
        if len(password) < 8:
            return "weak", "A true sigil requires at least 8 characters."
        if not re.search("[a-z]", password) or not re.search("[A-Z]", password) or not re.search("[0-9]", password):
            return "medium", "A powerful sigil combines uppercase, lowercase, and numbers."
        return "strong", "A sigil of immense power!"

    # --- Page Styling with Centering Adjustments ---
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&display=swap');

        /* --- Main App Body --- */
        .stApp {
            background-color: #0B0B1E; /* Deep navy blue background */
            font-family: 'Montserrat', sans-serif;
        }

        /* --- Right Column Form Container --- */
        .signup-container {
            padding: 2.5rem;
            height: 100%;
            text-align: center; /* Horizontally center all text content */
        }

        /* --- Custom Title & Subtitle --- */
        .signup-title {
            font-family: 'Cinzel Decorative', serif;
            font-size: 2.5rem;
            font-weight: 700;
            color: #FFFFFF;
            margin-bottom: 0.5rem;
        }
        .signup-subtitle {
            font-size: 1rem;
            font-style: italic;
            color: #A0A0B5; /* Muted text color */
            margin-bottom: 2rem;
        }

        /* --- Custom Labeled Inputs --- */
        .input-label {
            color: #D0D0E0;
            font-weight: 600;
            margin-bottom: 5px;
            text-align: left; /* Keep labels left-aligned for readability */
        }
    </style>
    """, unsafe_allow_html=True)

    # ================= Layout =================
    
    left_col, right_col = st.columns([0.6, 0.4], gap="large")

    with left_col:
        # --- Left Column: Cinematic Image ---
        # NOTE: Your hero section from the screenshot looks great. This is a placeholder.
        try:
            st.image("poster.jpg", use_container_width=True)
        except FileNotFoundError:
            st.warning("Image 'signup_hero.jpg' not found. Please add it to your project folder.")

    with right_col:
        st.markdown('<div class="signup-container">', unsafe_allow_html=True)
        
        # --- Right Column: Header ---
        st.markdown('<div class="signup-title">The Rite of Summoning</div>', unsafe_allow_html=True)
        st.markdown('<div class="signup-subtitle">Forge a pact to command the Genie of the Lamp.</div>', unsafe_allow_html=True)
        
        # --- The Signup Form ---
        with st.form("signup_form"):
            st.markdown('<div class="input-label">Inscribe Thy Name</div>', unsafe_allow_html=True)
            username = st.text_input("Username", label_visibility="collapsed", placeholder="The name you shall be known by")
            
            st.markdown('<div class="input-label">Conjure Thy Secret Sigil</div>', unsafe_allow_html=True)
            password = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Your secret word of power")

            st.markdown('<div class="input-label">Recast the Sigil</div>', unsafe_allow_html=True)
            confirm_password = st.text_input("Confirm Password", type="password", label_visibility="collapsed", placeholder="Confirm your word of power")
            
            # Password Strength Check
            if password:
                strength, message = check_password_strength(password)
                if strength == "weak": st.warning(message)
                elif strength == "medium": st.info(message)
                else: st.success(message)
            
            st.write("") # Spacer

            # --- Centering the button using columns ---
            _, btn_col, _ = st.columns([1, 2, 1])
            with btn_col:
                submitted = st.form_submit_button("Seal the Pact", use_container_width=True)

            if submitted:
                if not username or not password:
                    st.warning("The Genie requires both a name and a sigil.")
                elif password != confirm_password:
                    st.error("The sigils do not match! The magic falters.")
                elif check_password_strength(password)[0] == "weak":
                    st.error("Your sigil is too fragile. Forge a stronger one!")
                else:
                    with st.spinner("The cosmos witnesses your oath..."):
                        response = register_user(username, password)
                        if response.status_code == 201:
                            st.success("The pact is sealed! Proceed to the Gate of Awakening, Master.")
                            st.session_state['page'] = 'login'
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(f"The ancient magic resists! {response.json().get('detail')}")
                            
        st.markdown("<hr style='border-color: #4A3F6B;'>", unsafe_allow_html=True)
        
        # --- Centering the second button using columns ---
        _, btn_col2, _ = st.columns([0.5, 2, 0.5])
        with btn_col2:
            if st.button("Already have a pact? Enter the Cave", use_container_width=True):
                st.session_state['page'] = 'login'
                st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------------------------------------------------------

def render_main_app():
    import streamlit as st # type: ignore
    import pandas as pd # type: ignore
    import requests # type: ignore
    import time
    import json
    import plotly.express as px # type: ignore
    import plotly.graph_objects as go # type: ignore
    from io import StringIO

    # --- API CONFIGURATION ---
    API_URL = "http://127.0.0.1:8000"
    def get_auth_header():
        # NOTE: Assumes JWT token is placed in session_state upon login
        token = st.session_state.get('auth_token')
        return {"Authorization": f"Bearer {token}"} if token else {}

    # --- API Helper Functions (Placeholders for Backend Calls) ---
    def authenticated_get(endpoint):
        return requests.get(f"{API_URL}/{endpoint}", headers=get_auth_header())

    def list_databases():
        try:
            # NOTE: Assuming backend returns JSON like: {"databases": ["db1", "db2"]}
            response = authenticated_get("list_databases/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"databases": []}

    def list_tables(db):
        try:
            response = authenticated_get(f"list_tables/{db}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"tables": []}

    def list_columns(db, table):
        try:
            response = authenticated_get(f"list_columns/{db}/{table}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"columns": []}

    # --- UI Styling (Cinematic Sidebar) ---
    with st.sidebar:
        st.markdown("""
        <style>
            /* Animated Gradient Background for the Sidebar */
            [data-testid="stSidebar"] {
                background: linear-gradient(-45deg, #1a0033, #32014f, #180028, #2a0059);
                background-size: 400% 400%;
                animation: gradientShift 15s ease infinite;
                border-right: 2px solid #9a45ff;
            }
            @keyframes gradientShift {
                0% {background-position: 0% 50%;} 50% {background-position: 100% 50%;} 100% {background-position: 0% 50%;}
            }
            /* Glowing Image Portal Animation */
            @keyframes glowing-portal {
                0% { box-shadow: 0 0 20px rgba(154, 69, 255, 0.6); }
                50% { box-shadow: 0 0 40px rgba(192, 132, 252, 1); }
                100% { box-shadow: 0 0 20px rgba(154, 69, 255, 0.6); }
            }
            .sidebar-image-container {
                border-radius: 15px; overflow: hidden;
                border: 2px solid #c084fc;
                animation: glowing-portal 6s ease-in-out infinite;
                margin-bottom: 1.5rem;
            }
            /* Ancient, Thematic Typography */
            .sidebar-title {
                font-family: 'Cinzel Decorative', serif; font-size: 1.8rem;
                text-align: center; color: #f5d9ff;
                text-shadow: 0 0 12px #bf80ff; margin-top: 1rem;
            }
            .sidebar-tagline {
                font-family: 'Montserrat', sans-serif; font-style: italic;
                text-align: center; color: #C3B8E1;
                margin-top: -1rem; margin-bottom: 1.5rem;
            }
            .custom-divider { border: 1px solid #4A3F6B; margin: 1rem 0; }
            .stButton>button { color: #d8b4fe; border-color: #d8b4fe; }
        </style>
        """, unsafe_allow_html=True)

        # --- Sidebar Content ---
        st.markdown('<div class="sidebar-image-container">', unsafe_allow_html=True)
        try:
            st.image("bodugenie.png", use_container_width=True)
        except FileNotFoundError:
            st.warning("Image 'bodugenie.png' not found.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<h2 class="sidebar-title">SQLGenie</h2>', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-tagline">Scroll of Secrets</p>', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-tagline">Voice input Coming soon</p>', unsafe_allow_html=True)
        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
        
        # --- NEW FEATURE: Tome of Spells (Saved Queries) ---
        st.header("🗂️ Tome of Spells")
        if 'saved_queries' not in st.session_state:
            st.session_state['saved_queries'] = {}
        
        if st.session_state['saved_queries']:
            for name, query in st.session_state['saved_queries'].items():
                if st.button(f"🔮 {name}", key=f"tome_{name}", help=query):
                    st.session_state['manual_sql_query'] = query
                    st.session_state['generated_sql'] = query
                    st.rerun()
        else:
            st.info("Your saved spells will appear here.")
        
        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

        # --- Query History ---
        st.header("📜 Query History")
        if not st.session_state.get('query_history'):
            st.info("Your recent queries will appear here.")
        else:
            for i, query in enumerate(reversed(st.session_state['query_history'][-5:])):
                if st.button(f"📜 {query[:40]}...", key=f"hist_{i}", help=query):
                    st.session_state['manual_sql_query'] = query
                    st.session_state['generated_sql'] = query
                    st.rerun()

        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
        
        # --- Logout Button ---
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
            
    # --- MAIN CONTENT ---
    # Hero Section
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">SQLGenie Pro: The Oracle of Intelligent Queries</h1>
        <p class="header-subtitle">AI-Powered Insight Engine for E-Commerce & Retail Analytics</p>
    </div>""", unsafe_allow_html=True)

    # --- NEW FEATURE: Database Schema Explorer (improved) ---
    with st.expander("🗃️ Explore Database Schema"):
        db_col, table_col, col_col = st.columns(3)
        with db_col:
            # Current database selection logic
            db_list = list_databases().get("databases", [])
            if "selected_db" not in st.session_state: st.session_state['selected_db'] = None
            # Default to the first found database if none is selected
            if not st.session_state['selected_db'] and db_list:
                 st.session_state['selected_db'] = db_list[0]
            st.session_state['selected_db'] = st.selectbox("Select Database", db_list, index=db_list.index(st.session_state['selected_db']) if st.session_state['selected_db'] in db_list else 0)
        
        with table_col:
            selected_db = st.session_state['selected_db']
            table_list = list_tables(selected_db).get("tables", []) if selected_db else []
            if "selected_table" not in st.session_state: st.session_state['selected_table'] = None
            if not st.session_state['selected_table'] and table_list:
                 st.session_state['selected_table'] = table_list[0]
            st.session_state['selected_table'] = st.selectbox("Select Table", table_list, index=table_list.index(st.session_state['selected_table']) if st.session_state['selected_table'] in table_list else 0)
        
        with col_col:
            selected_table = st.session_state['selected_table']
            st.write(f"Columns in `{selected_table}`:")
            columns = list_columns(selected_db, selected_table).get("columns", []) if selected_table and selected_db else []
            st.dataframe(columns, use_container_width=True)

    # --- Step 1: Generate SQL from Natural Language ---
    st.markdown("## 🪄 Step 1: Generate SQL from Natural Language")
    nl_query = st.text_area("Describe what you want to know 👇", st.session_state.get('nl_query_input', "Top 5 most expensive products and their categories"), height=100, key='nl_query_input')
    st.write(f"🔍 You entered: '{nl_query}'")

    col_nl_gen, col_nl_save, col_nl_space = st.columns([0.5, 0.5, 2])
    
    with col_nl_gen:
        if st.button("✨ Summon SQL Spell", type="primary", use_container_width=True):
            nl_query = st.session_state.get("nl_query_input", "").strip()
            selected_db = st.session_state.get("selected_db")

            if nl_query and selected_db:
                with st.spinner("🔮 Asking the Genie to craft your SQL spell..."):
                    try:
                        # 🚩 FIX 1: Send data as JSON payload to match FastAPI's Pydantic Model (QueryRequest)
                        # --- CORRECTED CODE ---
                        response = requests.post(
                            f"{API_URL}/generate_sql/",
                            json={ # ✅ CORRECT: This sends a JSON body
                                "query": nl_query, # ✅ CORRECT: Matches Pydantic model
                                "db_name": selected_db
                            },
                            headers=get_auth_header()
                        )

                        if response.status_code == 200:
                            response_data = response.json()
                            sql_result = response_data.get("sql_query", "")
                            query_type = response_data.get("query_type", "").lower()

                            # Save both SQL and its type
                            st.session_state['generated_sql'] = sql_result
                            st.session_state['query_type'] = query_type

                            # Save to query history
                            if 'query_history' not in st.session_state:
                                st.session_state['query_history'] = []
                            st.session_state['query_history'].append(sql_result)

                            st.success("✅ Your SQL spell has been summoned!")
                            st.markdown("### 🧠 Generated SQL Query")
                            st.code(sql_result, language="sql")


                        else:
                            # Handle FastAPI exceptions (HTTPException detail)
                            error_detail = response.json().get("detail", f"Code {response.status_code}")
                            st.error(f"❌ Genie Error: {error_detail}")

                    except requests.exceptions.RequestException as e:
                        st.error(f"❌ Connection to Genie's realm failed: {e}")
            else: 
                st.warning("🧞‍♂️ The Genie awaits your question and selected database.")


    # --- Save Spell Section ---
    with col_nl_save:
        if st.session_state.get('generated_sql'):
            st.markdown("### 💾 Save Your Spell")
            save_name = st.text_input(
                "Give this spell a name:",
                key='save_name_input',
                placeholder="e.g., 'Top Customers by Region'"
            )
            # Logic to save the query
            if st.button("💾 Save to Tome", use_container_width=True) and save_name:
                st.session_state['saved_queries'][save_name] = st.session_state['generated_sql']
                st.success(f"✨ Spell **'{save_name}'** has been inscribed into your Tome!")

    # --- Generated SQL and Execution (Advanced Layout) ---
    if st.session_state.get('generated_sql'):
        sql_result = st.session_state['generated_sql']

        # Animated Success Banner
        st.markdown("""
        <div style="
            padding: 15px;
            background: linear-gradient(90deg, #4CAF50, #2E7D32);
            color: white;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            font-size: 18px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            animation: glow 2s infinite alternate;
        ">
            ✅ Your SQL spell has been summoned successfully!
        </div>
        <style>
            @keyframes glow {
                from { box-shadow: 0 0 10px #4CAF50; }
                to   { box-shadow: 0 0 25px #2E7D32; }
            }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("### 🎯 AI-Generated SQL Query")

        if sql_result.strip():
            # Show SQL in code block
            st.code(sql_result, language="sql")

            # Copy to Clipboard button (using download button as a copy utility)
            st.download_button(
                "📋 Copy SQL to Clipboard",
                sql_result,
                file_name="generated_query.sql",
                mime="text/sql",
                use_container_width=True
            )

            # Auto-save to query history (check ensures no duplicates are logged)
            if 'query_history' not in st.session_state:
                st.session_state['query_history'] = []
            if sql_result not in st.session_state['query_history']:
                st.session_state['query_history'].append(sql_result)

        else:
            st.error("⚠️ Genie returned an empty scroll. Check backend response.")

        st.markdown("### ✍️ Refine or Edit")
        manual_sql_query = st.text_area(
            "🧾 Edit your SQL incantation below:",
            sql_result,
            height=180,
            key="manual_sql_query_input"
        )

        dangerous = ["delete", "drop", "truncate"]
        query_type = st.session_state.get("query_type", "").lower()

        if query_type in dangerous:
            st.warning(f"⚠️ This is a powerful `{query_type.upper()}` query. Execution may alter or erase data.")

            # Explanation for each type
            if query_type == "drop":
                st.markdown("🧠 **DROP** will permanently remove a table or database. This cannot be undone.")
            elif query_type == "truncate":
                st.markdown("🧠 **TRUNCATE** deletes all rows instantly, without logging individual deletions.")
            elif query_type == "delete":
                st.markdown("🧠 **DELETE** removes rows based on conditions. Use with caution.")

            # Permission checkbox
            if st.checkbox(f"✅ I understand and wish to execute this `{query_type.upper()}` query"):
                if st.button("✨ Execute SQL Query"):
                    execute_sql_query(manual_sql_query)
            else:
                st.info("🧞 Execution paused. The Genie awaits your permission.")
        else:
            if st.button("✨ Execute SQL Query"):
                execute_sql_query(manual_sql_query)
            if 'execution_result' in st.session_state:
                result = st.session_state['execution_result']

                # ✅ Show message if present
                if result.get("message"):
                    st.info(result["message"])
                    st.info("🧞 If in case - 'No results found' then The Our Genie suggests checking your spell or trying a nearby variation.")

                # ✅ Show results if present
                if result.get("results"):
                    st.markdown("### 📊 Query Results")
                    st.dataframe(result["results"])

                # ✅ Show suggestions if present
                if result.get("suggestions"):
                    st.markdown("### 🔍 Suggested Alternatives")
                    for suggestion in result["suggestions"]:
                        if st.button(f"Try: {suggestion}", key=f"suggestion_{suggestion}"):
                            rerun_with_suggestion(suggestion)

    

    st.markdown("## 💬 Chat with SQLGenie")

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    user_input = st.text_input("Ask SQLGenie anything about your query, schema, or results:", key="chat_input")

    if user_input:
        # Call Gemini or your backend model here
        response = call_gemini_chat(user_input)  # You define this function
        st.session_state['chat_history'].append(("You", user_input))
        st.session_state['chat_history'].append(("SQLGenie", response))

    # Display chat history
    for speaker, message in st.session_state['chat_history']:
        st.markdown(f"**{speaker}:** {message}")


    # --- NEW FEATURE: Advanced Visualization Tabbed Layout ---
    if st.session_state.get('query_results'):
        results = st.session_state['query_results']
        st.subheader("📊 Query Insights")
        
        # --- Display Execution Time, Optimization Tips, and Suggestions ---
        col_time, col_opt_tip = st.columns([1, 2])

        with col_time:
            st.metric(label="⚡ Spell Cast Time", value=f"{results.get('execution_time', 0.0):.4f} seconds")

        with col_opt_tip:
            st.info(f"💡 Optimization Tip: {results.get('optimization_tips', 'No tips available')}")

            # 🔍 Show suggestions if present
            if results.get("suggestions"):
                st.markdown("### 🔍 Suggested Alternatives")
                for suggestion in results["suggestions"]:
                    if st.button(f"Try: {suggestion}", key=f"suggestion_{suggestion}"):
                        rerun_with_suggestion(suggestion)



        tab1, tab2 = st.tabs(["📄 Data Table", "📈 Visualization"])

        with tab1:
            st.dataframe(results["data"], use_container_width=True)
            st.download_button("Download Results as CSV", results["data"].to_csv(index=False).encode('utf-8'), 'query_results.csv', 'text/csv')

        with tab2:
            st.subheader("Visual Explorer")
            if not results["data"].empty:
                # --- AI-Powered Chart Suggestions (Logic kept) ---
                chart_options = {}
                df = results["data"]
                num_cols = df.select_dtypes(include=['int64', 'float64']).columns
                cat_cols = df.select_dtypes(include=['object', 'category']).columns
                date_cols = df.select_dtypes(include=['datetime64']).columns
                
                # Logic to suggest chart types based on data availability (kept as-is)
                if len(date_cols) >= 1 and len(num_cols) >= 1: chart_options['Time-Series Line Chart'] = 'line'
                if len(num_cols) >= 2: chart_options['Scatter Plot'] = 'scatter'
                if len(cat_cols) >= 1 and len(num_cols) >= 1: 
                    chart_options['Bar Chart'] = 'bar'
                    chart_options['Pie Chart'] = 'pie'
                
                selected_chart_type = st.selectbox("Select a visualization type:", list(chart_options.keys()) if chart_options else ["No Charts Available"])
                
                # --- Chart Rendering Logic (Simplified & Corrected for Plotly) ---
                if selected_chart_type == 'Bar Chart' and len(cat_cols) >= 1 and len(num_cols) >= 1:
                    x_axis = st.selectbox('X-axis (Categorical)', cat_cols)
                    y_axis = st.selectbox('Y-axis (Numerical)', num_cols)
                    fig = px.bar(df, x=x_axis, y=y_axis, title=f"Bar Chart of {y_axis} by {x_axis}")
                    st.plotly_chart(fig, use_container_width=True)
                elif selected_chart_type == 'Time-Series Line Chart' and len(date_cols) >= 1 and len(num_cols) >= 1:
                    x_axis = st.selectbox('X-axis (Date)', date_cols)
                    y_axis = st.selectbox('Y-axis (Numerical)', num_cols)
                    fig = px.line(df, x=x_axis, y=y_axis, title=f"Line Chart of {y_axis} over {x_axis}")
                    st.plotly_chart(fig, use_container_width=True)
                elif selected_chart_type == 'Scatter Plot' and len(num_cols) >= 2:
                    x_axis = st.selectbox('X-axis', num_cols)
                    y_axis = st.selectbox('Y-axis', [col for col in num_cols if col != x_axis])
                    fig = px.scatter(df, x=x_axis, y=y_axis, title=f"Scatter Plot of {y_axis} vs {x_axis}")
                    st.plotly_chart(fig, use_container_width=True)
                elif selected_chart_type == 'Pie Chart' and len(cat_cols) >= 1 and len(num_cols) >= 1:
                    names_col = st.selectbox('Labels', cat_cols)
                    values_col = st.selectbox('Values', num_cols)
                    fig = px.pie(df, names=names_col, values=values_col, title=f"Pie Chart of {names_col} Distribution")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Select a visualization type and valid columns above to generate a chart.")
            else:
                st.info("No data available to visualize.")

    st.markdown("""
    <div class="genie-footer">
    Final Year Project by Akash — Summoned from the depths of code and curiosity
    </div>
    <style>
    @keyframes shimmer {
    0% { background-position: -500px 0; }
    100% { background-position: 500px 0; }
    }

    </style>
    """, unsafe_allow_html=True)


    # --- Buttons ---
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    col1, _ = st.columns([1, 1]) # Unpack the list into two variables
    with col1: # Use a single column object as a context manager
        if st.button("About", use_container_width=True):
            st.session_state.page = 'about'
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Cinematic Genie Footer ---
    st.markdown("""
    <style>
    .footer-genie {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: linear-gradient(to right, #3e1e68, #8e44ad);
        color: #f8e9d2;
        text-align: center;
        padding: 14px;
        font-size: 17px;
        font-family: 'Papyrus', 'Georgia', serif;
        font-weight: bold;
        border-top: 3px solid #f5cba7;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.4);
        z-index: 999;
        animation: genieGlow 3s infinite alternate;
    }

    @keyframes genieGlow {
        from { box-shadow: 0 -4px 20px #f5cba7; }
        to   { box-shadow: 0 -4px 30px #f8e9d2; }
    }
    </style>

    <div class="footer-genie">
    🧞‍♂️ <em>The Genie whispers from the lamp...</em><br>
    “If no scrolls are found, revisit your spell or seek a nearby incantation.”
    </div>
    """, unsafe_allow_html=True)


from pathlib import Path
import base64
import random

def render_about_page():
    # 🚩 FIX: Imports moved to the top of the main file
    # (Ensure Path, base64, random, and st are imported globally)
    
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&family=Playfair+Display:wght@400;700&display=swap');
        
        @keyframes glowing-border {{
            0% {{ box-shadow: 0 0 10px rgba(168, 85, 247, 0.4), inset 0 0 10px rgba(168, 85, 247, 0.2); }}
            50% {{ box-shadow: 0 0 25px rgba(168, 85, 247, 0.8), inset 0 0 25px rgba(168, 85, 247, 0.4); }}
            100% {{ box-shadow: 0 0 10px rgba(168, 85, 247, 0.4), inset 0 0 10px rgba(168, 85, 247, 0.2); }}
        }}
        
        .about-container {{
            background: rgba(15, 12, 41, 0.8);
            border-radius: 25px;
            padding: 3rem;
            margin-top: 3rem;
            border: 3px solid #a855f7;
            animation: glowing-border 5s ease-in-out infinite;
            backdrop-filter: blur(8px);
            color: #f0e6d2;
            font-family: 'Playfair Display', serif;
            text-align: center;
        }}

        .about-header {{
            font-family: 'Cinzel Decorative', serif;
            font-size: 3rem;
            color: #d8b4fe;
            text-shadow: 0 0 15px #c084fc;
            margin-bottom: 2rem;
            text-transform: uppercase;
        }}
        
        .tech-list-stunning {{
            list-style: none;
            padding-left: 0;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        
        .tech-list-stunning li {{
            font-family: 'Playfair Display', serif;
            font-size: 1.15rem;
            padding: 1rem;
            background: linear-gradient(to right, rgba(30, 15, 60, 0.7), rgba(45, 20, 85, 0.5));
            border-radius: 15px;
            border-left: 4px solid #d8b4fe;
            transition: all 0.3s ease;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            text-align: left;
        }}
        
        .tech-list-stunning li:hover {{
            background: linear-gradient(to right, #452085, #6030a0);
            border-left: 4px solid #f5d9ff;
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 8px 20px rgba(168, 85, 247, 0.4);
        }}
        
        .tech-title-stunning {{
            font-weight: bold;
            color: #f5d9ff;
            text-transform: uppercase;
            letter-spacing: 1px;
            text-shadow: 0 0 5px #c084fc;
        }}
        
        .tech-description {{
            font-size: 0.95rem;
            color: #e0d0ff;
            display: block;
            margin-top: 0.5rem;
        }}
        
        .back-button {{
            margin-top: 3rem;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # 🚩 FIX 2: Re-activated the main container
    st.markdown('<div class="about-container">', unsafe_allow_html=True)
    
    st.markdown("<h2 class='about-header'>⚙️ The Oracle's Architecture</h2>", unsafe_allow_html=True)

    st.markdown("""
        <p class='about-description' style='text-align: center; color: #f0e6d2; font-size: 1.1rem;'>
            Within the digital fortress of <strong>SQLGenie Pro</strong>, a fusion of ancient elegance and cutting-edge AI transforms your commands into a cascade of data insights.
        </p>
    """, unsafe_allow_html=True)

    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 class'tech-title'>The Genie's Spellbook</h3>", unsafe_allow_html=True)
        st.markdown("""
        <ul class="tech-list-stunning">
            <li>
                <span class='tech-title-stunning'>🔮 The Scrying Mirror: Streamlit</span>
                <span class='tech-description'>
                    The enchanted interface that reflects the Genie's realm onto your screen. It channels user intent into visual spells, allowing mortals to interact with ancient data magic.
                </span>
            </li>
            <li>
                <span class='tech-title-stunning'>✨ The Genie's Gate: FastAPI</span>
                <span class='tech-description'>
                    A shimmering portal guarded by swift incantations. It listens to your summons and delivers them to the Oracle with speed and precision, ensuring secure passage through the backend ether.
                </span>
            </li>
            <li>
                <span class='tech-title-stunning'>🧠 The Oracle's Mind: Gemini 2.5 Pro (API)</span>
                <span class='tech-description'>
                    A boundless intellect, summoned from the cloud. This Transformer model interprets your whispers and crafts intelligent SQL spells with world-class accuracy.
                </span>
            </li>
            <li>
                <span class='tech-title-stunning'>🗄️ The Ancient Tome: MySQL</span>
                <span class='tech-description'>
                    A timeless vault inscribed with the knowledge of a thousand queries. It stores the sacred texts of data, ready to be summoned by the Genie’s will.
                </span>
            </li>
            <li>
                <span class='tech-title-stunning'>📜 The Binding Scroll: SQLAlchemy</span>
                <span class='tech-description'>
                    A mystical parchment that binds Python’s arcane language to the database’s ancient runes. It ensures harmony between realms, translating commands into powerful actions.
                </span>
            </li>
        </ul>
        """, unsafe_allow_html=True)

        # 🚩 FIX 3: Removed stray (and incorrect) st.markdown('</div>', ...)
    
    with col2:
        st.markdown("<h3><span class='tech-title'>Visual Spell</span></h3>", unsafe_allow_html=True)
        try:
            st.image("about.jpg", width=350)
        except FileNotFoundError:
            st.warning("Image 'about.jpg' not found.")

    # 🚩 FIX 2 (Continued): Close the main container
    st.markdown('</div>', unsafe_allow_html=True) 

    st.markdown("""
        <style>
        .back-button {
            margin-top: 20px;
            text-align: left;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="back-button">', unsafe_allow_html=True)

    if st.button("⬅️ Back to the Oracle"):
        st.session_state['page'] = 'main_app'
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# --- Router to navigate between pages ---
if st.session_state.get('logged_in'):
    # If logged in, check for specific pages first
    if st.session_state.get('page') == 'about':
        render_about_page()
    else:
        # Default to main app if logged in and not on a specific page
        render_main_app()
elif st.session_state.get('page') == 'login':
    render_login_page()
elif st.session_state.get('page') == 'signup':
    render_signup_page()
else:
    # Default to welcome page if not logged in
    render_welcome_page()
