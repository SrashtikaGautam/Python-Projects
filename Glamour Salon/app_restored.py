import streamlit as st
import pandas as pd
import sqlite3
from textwrap import dedent
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import hashlib
import os
import base64
import plotly.express as px
import plotly.graph_objects as go
import urllib.parse

# Page configuration
st.set_page_config(
    page_title="Glamour Salon - Beauty Redefined",
    page_icon="💅",
    layout="wide"
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'phone_number' not in st.session_state:
    st.session_state.phone_number = ""
if 'loyalty_points' not in st.session_state:
    st.session_state.loyalty_points = 0
if 'show_confetti' not in st.session_state:
    st.session_state.show_confetti = False
if 'navigate_to' not in st.session_state:
    st.session_state.navigate_to = None
if 'preselected_service' not in st.session_state:
    st.session_state.preselected_service = None
if 'flash_message' not in st.session_state:
    st.session_state.flash_message = None

# Create directory for gallery images if it doesn't exist
if not os.path.exists("gallery"):
    os.makedirs("gallery")

# Helper for database connection
def get_db_connection():
    """Create a database connection with timeout and proper configuration."""
    try:
        conn = sqlite3.connect('salon.db', timeout=30, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

# Initialize database
def init_db():
    conn = get_db_connection()
    if not conn:
        return
        
    try:
        c = conn.cursor()
        
        # Enable WAL mode for better concurrency
        try:
            c.execute('PRAGMA journal_mode=WAL;')
        except:
            pass
            
        # Create users table
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      phone TEXT NOT NULL UNIQUE,
                      loyalty_points INTEGER DEFAULT 0,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Check if loyalty_points column exists (migration for existing dbs)
        try:
            c.execute("SELECT loyalty_points FROM users LIMIT 1")
        except sqlite3.OperationalError:
            try:
                c.execute("ALTER TABLE users ADD COLUMN loyalty_points INTEGER DEFAULT 0")
            except:
                pass
        
        # Create appointments table
        c.execute('''CREATE TABLE IF NOT EXISTS appointments
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      service TEXT NOT NULL,
                      date TEXT NOT NULL,
                      time TEXT NOT NULL,
                      status TEXT DEFAULT 'booked',
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (user_id) REFERENCES users (id))''')
        
        # Create services table
        c.execute('''CREATE TABLE IF NOT EXISTS services
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      price REAL NOT NULL,
                      duration INTEGER NOT NULL,
                      description TEXT,
                      category TEXT)''')
        
        # Insert sample services if table is empty
        c.execute("SELECT COUNT(*) FROM services")
        if c.fetchone()[0] == 0:
            sample_services = [
                ("Haircut & Styling", 499.0, 60, "Professional haircut with blow dry and styling", "Hair"),
                ("Hair Coloring", 1499.0, 120, "Full hair coloring service with conditioning treatment", "Hair"),
                ("Hair Spa Treatment", 999.0, 90, "Deep conditioning and scalp massage treatment", "Hair"),
                ("Facial Treatment", 899.0, 75, "Custom facial with cleansing and moisturizing", "Skin"),
                ("Waxing Full Legs", 599.0, 45, "Complete leg waxing with soothing lotion", "Waxing"),
                ("Eyebrow Threading", 99.0, 30, "Precision eyebrow shaping with threading", "Waxing"),
                ("Manicure", 499.0, 45, "Classic nail care with polish", "Nails"),
                ("Pedicure", 599.0, 60, "Luxury foot care with massage and polish", "Nails"),
                ("Makeup Application", 1999.0, 60, "Professional makeup for special occasions", "Makeup"),
                ("Bridal Makeup", 9999.0, 120, "Complete bridal makeup with trial session", "Makeup")
            ]
            
            c.executemany("INSERT INTO services (name, price, duration, description, category) VALUES (?, ?, ?, ?, ?)", 
                          sample_services)
        
        conn.commit()
    except sqlite3.OperationalError as e:
        # If locked, we just log it but don't crash, hoping it's initialized
        print(f"DB Init Warning: {e}")
    finally:
        conn.close()

# Hash password (for future use)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Get user ID by phone number
def get_user_id(phone):
    conn = get_db_connection()
    if not conn: return None
    try:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE phone = ?", (phone,))
        result = c.fetchone()
        return result[0] if result else None
    finally:
        conn.close()

# Get user details
def get_user_details(user_id):
    conn = get_db_connection()
    if not conn: return None
    try:
        c = conn.cursor()
        c.execute("SELECT name, phone, loyalty_points FROM users WHERE id = ?", (user_id,))
        result = c.fetchone()
        return result
    finally:
        conn.close()

# Register new user
def register_user(name, phone):
    conn = get_db_connection()
    if not conn: return False
    try:
        c = conn.cursor()
        c.execute("INSERT INTO users (name, phone, loyalty_points) VALUES (?, ?, 0)", (name, phone))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Update loyalty points
def update_loyalty_points(user_id, points):
    conn = get_db_connection()
    if not conn: return
    try:
        c = conn.cursor()
        c.execute("UPDATE users SET loyalty_points = loyalty_points + ? WHERE id = ?", (points, user_id))
        conn.commit()
    finally:
        conn.close()

# Book appointment
def book_appointment(user_id, service, date, time):
    conn = get_db_connection()
    if not conn: return False
    try:
        c = conn.cursor()
        # Check for existing booking to prevent duplicates
        c.execute("""
            SELECT id FROM appointments 
            WHERE user_id = ? AND service = ? AND date = ? AND time = ? AND status = 'booked'
        """, (user_id, service, date, time))
        existing = c.fetchone()
        
        if existing:
            return True # Idempotent success
            
        c.execute("INSERT INTO appointments (user_id, service, date, time) VALUES (?, ?, ?, ?)", 
                  (user_id, service, date, time))
        conn.commit()
        return True
    except Exception as e:
        print(f"Booking error: {e}")
        return False
    finally:
        conn.close()

# Cancel appointment
def cancel_appointment(appointment_id):
    conn = get_db_connection()
    if not conn: return
    try:
        c = conn.cursor()
        c.execute("UPDATE appointments SET status = 'cancelled' WHERE id = ?", (appointment_id,))
        conn.commit()
    finally:
        conn.close()

# Get user appointments
def get_user_appointments(user_id):
    conn = get_db_connection()
    if not conn: return pd.DataFrame()
    try:
        # Optimized query: Removed JOIN (redundant), added GROUP BY to deduplicate
        df = pd.read_sql_query("""
            SELECT MAX(id) as id, service, date, time, status
            FROM appointments
            WHERE user_id = ?
            GROUP BY service, date, time, status
            ORDER BY date DESC, time DESC
        """, conn, params=[str(user_id)])
        return df
    finally:
        conn.close()

# Get all services
@st.cache_data(ttl=300)
def get_services():
    conn = get_db_connection()
    if not conn: return pd.DataFrame()
    try:
        df = pd.read_sql_query("SELECT * FROM services ORDER BY category, name", conn)
        return df
    finally:
        conn.close()

# Convert image to base64 for embedding
def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

# Custom CSS for styling
def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap');
    
    :root {
        --primary: #FF69B4;
        --secondary: #DA70D6;
        --accent: #BA55D3;
        --light: #FFF0F5;
        --dark: #4B0082;
        --text: #000000;
        --success: #4CAF50;
        --warning: #FF9800;
        --danger: #F44336;
    }
    
    body {
        font-family: 'Poppins', sans-serif;
        background-color: var(--light);
        color: var(--text);
        overflow-x: hidden;
    }

    /* Aesthetic Background */
    .stApp {
        background: linear-gradient(135deg, #fff0f5 0%, #e6e6fa 100%);
        animation: fadeIn 0.8s ease-in;
    }

    /* Selected text styling – keep selected text dark and readable */
    ::selection {
        background: rgba(216, 191, 216, 0.5);
        color: #111111;
    }
    ::-moz-selection {
        background: rgba(216, 191, 216, 0.5);
        color: #111111;
    }

    /* Improve readability on form controls: dark text on light inputs */
    input, select, textarea {
        color: #111111 !important;
        background-color: #ffffff !important;
        border: 1px solid #d8d8d8 !important;
        pointer-events: auto !important;
    }
    input::placeholder, textarea::placeholder {
        color: #666666 !important;
    }
    option {
        color: #111111;
        background-color: #ffffff;
    }
    /* Streamlit select/date/time components */
    .stSelectbox div[data-baseweb="select"] {
        color: #111111 !important;
    }
    .stSelectbox div[data-baseweb="select"] * {
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
        text-shadow: none !important;
    }
    .stDateInput input, .stTimeInput input {
        color: #111111 !important;
        background-color: #ffffff !important;
        border: 1px solid #d8d8d8 !important;
        pointer-events: auto !important;
    }
    .stTextInput input, .stNumberInput input {
        color: #111111 !important;
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid rgba(255, 105, 180, 0.1) !important;
        pointer-events: auto !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border-radius: 10px !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 15px rgba(255, 105, 180, 0.2) !important;
        transform: translateY(-2px);
        background-color: #ffffff !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', serif;
        color: var(--dark);
    }
    
    /* Form labels - darker color for readability */
    label, .stTextInput label, .stNumberInput label, .stSelectbox label,
    .stDateInput label, .stTimeInput label {
        color: #222222 !important;
        font-weight: 500;
    }

    /* Ensure generic text elements are dark and readable */
    p, span, li, small, .stMarkdown, .stAlert, .stAlert p {
        color: #222222 !important;
    }
    
    /* Main content area - ensure all text is readable */
    .main .block-container,
    .main .block-container *,
    .main .element-container,
    .main .element-container * {
        color: #222222 !important;
    }
    
    /* Override any white text in main content */
    .main p, .main span, .main div, .main li {
        color: #222222 !important;
    }
    
    /* Ensure headings are readable */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        color: #4B0082;
    }
    
    /* Dropdown menus in main content - comprehensive fix */
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    div[role="listbox"],
    ul[role="listbox"] {
        background-color: #ffffff !important;
        border: 1px solid #ff69b4 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        z-index: 999999 !important; /* Extremely high z-index */
        visibility: visible !important;
        opacity: 1 !important;
    }

    /* Ensure the list container handles scrolling */
    ul[role="listbox"],
    div[role="listbox"] {
        max-height: 300px !important;
        overflow-y: auto !important;
        padding: 0 !important;
    }
    
    /* Dropdown options - explicit text styling */
    li[role="option"],
    div[role="option"] {
        background-color: #ffffff !important;
        color: #000000 !important; /* Force black text */
        padding: 10px 15px !important;
        border-bottom: 1px solid #f0f0f0 !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
    }

    /* Force all children of options to be black */
    li[role="option"] *,
    div[role="option"] * {
        color: #000000 !important;
        fill: #000000 !important;
        font-weight: 500 !important;
    }

    /* Hover state */
    li[role="option"]:hover,
    div[role="option"]:hover,
    li[role="option"][aria-selected="true"],
    div[role="option"][aria-selected="true"] {
        background-color: #ffe6f0 !important;
        color: #000000 !important;
    }

    /* Input box itself - ensure text is visible */
    div[data-baseweb="select"] div {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    /* Fix for specific Streamlit/BaseWeb internal structures */
    [data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
    }

    /* Parent containers overflow fix */
    [data-testid="stVerticalBlock"] {
        overflow: visible !important;
    }
    
    /* Remove any potential filters/backdrops affecting visibility */
    [data-baseweb="popover"] {
        filter: none !important;
        backdrop-filter: none !important;
    }
    
    /* Sidebar dropdowns */
    [data-testid="stSidebar"] ~ [data-baseweb="popover"] {
        background-color: #1e1e2e !important;
        border: 2px solid #ff69b4 !important;
    }
    
    /* Improve Selectbox Clickable Area */
    .stSelectbox div[data-baseweb="select"] {
        cursor: pointer !important;
        border-color: #ff69b4 !important;
    }
    .stSelectbox div[data-baseweb="select"]:hover {
        border-color: #ff1493 !important;
        background-color: #fff0f5 !important;
    }
    
    /* Form styling */
    [data-testid="stForm"] {
        padding: 2rem;
        background-color: #ffffff;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #ffe6f0;
    }
    
    /* Full width inputs */
    .stSelectbox, .stDateInput, .stTimeInput {
        width: 100% !important;
    }
    
    [data-baseweb="select"] {
        width: 100% !important;
    }
    
    /* Input label styling */
    .stSelectbox label, .stDateInput label, .stTimeInput label {
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    [data-testid="stSidebar"] ~ [data-baseweb="popover"] li,
    [data-testid="stSidebar"] ~ [data-baseweb="popover"] div {
        color: #ffffff !important;
        background-color: #1e1e2e !important;
    }
    [data-testid="stSidebar"] ~ [data-baseweb="popover"] li:hover {
        background-color: #ff69b4 !important;
        color: #ffffff !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, rgba(255,105,180,0.1) 0%, rgba(218,112,214,0.1) 100%);
        animation: fadeIn 0.5s ease-in;
    }

    /* Sidebar readability - comprehensive fixes */
    [data-testid="stSidebar"] {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stMarkdown * {
        color: #ffffff !important;
    }
    
    /* Sidebar selectbox - closed state */
    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stSelectbox > div,
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
        color: #ffffff !important;
        background-color: #1e1e2e !important;
        border: 1px solid #ff69b4 !important;
    }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] input {
        color: #ffffff !important;
        background-color: transparent !important;
    }
    
    /* Sidebar dropdowns – no special popover styling to avoid affecting main area */
    
    /* Sidebar buttons and links */
    [data-testid="stSidebar"] button,
    [data-testid="stSidebar"] a {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] button:hover,
    [data-testid="stSidebar"] a:hover {
        color: #ff69b4 !important;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .header {
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        color: white;
        animation: slideDown 0.8s ease-out;
    }
    
    @keyframes slideDown {
        from { transform: translateY(-8px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .service-card {
        background: white;
        color: #000000; /* Ensure text is visible on white background */
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 5px solid var(--primary);
        animation: slideUp 0.5s ease-out;
    }
    
    .service-card p {
        color: #333333; /* Dark grey for descriptions */
    }
    
    .service-card h4 {
        color: #000000;
    }
    
    .service-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    }
    
    @keyframes slideUp {
        from { transform: translateY(8px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .appointment-card {
        background: white;
        color: #000000;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border-left: 5px solid var(--accent);
        transition: all 0.3s ease;
    }
    
    .appointment-card h4 {
        color: #000000;
        margin-bottom: 0.5rem;
    }
    
    .appointment-card p {
        color: #333333;
        margin-bottom: 0.25rem;
    }
    
    .appointment-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
    }
    
    .btn-primary {
        background-color: var(--primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        box-shadow: 0 4px 10px rgba(255,105,180,0.3) !important;
        text-decoration: none !important;
        display: inline-block !important;
    }
    
    .btn-primary:hover {
        background-color: var(--accent) !important;
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(186,85,211,0.4) !important;
    }

    /* Make Streamlit buttons look like our pink button */
    .stButton > button, 
    .service-card .stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(45deg, var(--primary), var(--accent)) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        box-shadow: 0 4px 15px rgba(255,105,180,0.3) !important;
        letter-spacing: 0.5px;
        background-size: 200% auto !important;
    }
    .stButton > button:hover, 
    .service-card .stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        background-position: right center !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 25px rgba(255, 105, 180, 0.5) !important;
        color: white !important;
    }
    .stButton > button:active,
    div[data-testid="stFormSubmitButton"] > button:active {
        transform: translateY(-1px) !important;
    }

    /* Form Entrance Animations */
    .stTextInput, .stNumberInput, .stSelectbox {
        animation: fadeInUp 0.8s ease-out backwards;
    }
    
    /* Stagger animations for inputs if possible, otherwise they just fade in together which is fine */
    div[data-testid="stForm"] .stTextInput:nth-child(1) { animation-delay: 0.2s; }
    div[data-testid="stForm"] .stTextInput:nth-child(2) { animation-delay: 0.3s; }
    div[data-testid="stForm"] .stButton { animation-delay: 0.4s; }

    
    .btn-danger {
        background-color: var(--danger) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        box-shadow: 0 4px 10px rgba(244,67,54,0.3) !important;
    }
    
    .btn-danger:hover {
        background-color: #d32f2f !important;
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(211,47,47,0.4) !important;
    }
    
    .login-container {
        max-width: 500px;
        margin: 2rem auto;
        background: white;
        color: var(--text);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        animation: fadeInSlide 0.6s ease-out;
    }
    
    .hero-image {
        width: 100%;
        height: 400px;
        object-fit: cover;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        transition: transform 0.5s ease;
    }
    
    .hero-image:hover {
        transform: translateY(-3px);
    }

    /* Modern Landing Page Styles */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translate3d(0, 8px, 0);
        }
        to {
            opacity: 1;
            transform: translate3d(0, 0, 0);
        }
    }

    .landing-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-weight: 700;
        color: #2c2c2c;
        line-height: 1.2;
        margin-bottom: 1rem;
        animation: fadeInUp 1s ease-out;
    }
    
    .landing-subtitle {
        font-family: 'Poppins', sans-serif;
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
        line-height: 1.6;
        letter-spacing: 0.5px;
        animation: fadeInUp 1s ease-out 0.2s backwards;
    }

    .login-card {
        background: rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
        border-radius: 24px;
        padding: 2.5rem;
        animation: fadeInUp 1s ease-out 0.4s backwards;
    }
    
    @keyframes floating {
        0% { transform: translate(0, 0px); }
        50% { transform: translate(0, 12px); }
        100% { transform: translate(0, 0px); }
    }

    .login-hero-img {
        width: 75%;
        aspect-ratio: 3/4;
        border-radius: 24px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.1);
        animation: floating 6s ease-in-out infinite, fadeIn 1.5s ease-out;
        transition: all 0.5s ease;
        object-fit: cover;
        display: block;
        margin: 0 auto;
    }
    
    .login-hero-img:hover {
        transform: scale(1.02);
    }
    
    .stTextInput input::placeholder, .stNumberInput input::placeholder {
        transition: all 0.3s ease !important;
    }
    
    .stTextInput input:focus::placeholder, .stNumberInput input:focus::placeholder {
        opacity: 0.7;
        color: var(--primary) !important;
    }
    
    /* Polished Input Fields */
    .stTextInput input {
        border-radius: 12px !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        padding: 14px 18px !important;
        transition: all 0.3s ease !important;
        background: rgba(255, 255, 255, 0.8) !important;
        font-family: 'Poppins', sans-serif !important;
        font-size: 1rem !important;
        color: #333 !important;
    }

    .stTextInput input:focus {
        border-color: var(--primary) !important;
        background: white !important;
        box-shadow: 0 0 0 4px rgba(255, 105, 180, 0.1) !important;
        outline: none !important;
    }
    
    /* Smooth transition for placeholders */
    .stTextInput input::placeholder {
        transition: transform 0.3s ease, opacity 0.3s ease;
    }
    
    .stTextInput input:focus::placeholder {
        transform: translateX(5px);
        opacity: 0.7;
    }
    
    .feature-box {
        text-align: center;
        padding: 1.5rem;
        background: white;
        color: var(--text);
        border-radius: 15px;
        transition: transform 0.3s ease;
        border: 1px solid #f9f9f9;
        height: 100%;
    }
    
    .feature-box p {
        color: #555555;
    }
    
    .feature-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: inline-block;
    }

    /* Modern Hero Banner (Backup/Alternative) */
    .hero-banner {
        background-color: var(--light); /* Fallback color */
        height: 400px;
        border-radius: 15px;
        position: relative;
        overflow: hidden;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .hero-banner::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url('https://images.unsplash.com/photo-1600948836101-f9ffda59d250?q=80&w=1600&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        z-index: 0;
        animation: heroFadeIn 1.5s ease-out forwards;
    }

    .hero-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(to bottom, rgba(0,0,0,0.3), rgba(0,0,0,0.6));
        backdrop-filter: brightness(0.9) contrast(1.05);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: #FFFFF0;
        text-align: center;
        padding: 2rem;
        transition: background 0.5s ease;
        z-index: 1;
    }
    
    .hero-banner:hover .hero-overlay {
        background: linear-gradient(to bottom, rgba(0,0,0,0.4), rgba(0,0,0,0.7));
        backdrop-filter: brightness(0.85) contrast(1.1);
    }

    @keyframes heroSlideUp {
        0% {
            opacity: 0;
            transform: translateY(8px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes heroFadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }

    /* Increase specificity to override global .main h1 styles using ID */
    #hero-title-text, .hero-banner .hero-title, h1.hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        margin-bottom: 1rem;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.6);
        color: #FFFFF0 !important; /* Ivory White */
        font-weight: 700;
        letter-spacing: 1px;
        animation: heroSlideUp 1.2s ease-in-out;
    }

    #hero-subtitle-text, .hero-banner .hero-subtitle, p.hero-subtitle {
        font-family: 'Poppins', sans-serif;
        font-size: 1.5rem;
        font-weight: 500;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.6);
        color: #F5F5DC !important; /* Light Beige */
        max-width: 800px;
        line-height: 1.6;
        animation: heroFadeIn 1.5s ease-in-out 0.5s backwards;
    }

    .gallery-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    .gallery-item {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
        position: relative;
        height: 250px;
    }
    
    .gallery-item:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    
    .gallery-item img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: opacity 0.5s ease;
    }
    
    .gallery-item:hover img {
        opacity: 0.9;
    }
    
    .gallery-caption {
        padding: 1rem;
        background: rgba(255, 255, 255, 0.95);
        text-align: center;
        font-weight: 500;
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        /* backdrop-filter: blur(5px); Removed for performance */
    }
    
    footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        color: var(--dark);
        font-size: 0.9rem;
    }
    
    .notification {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: 500;
        animation: fadeIn 0.3s ease-in;
    }
    
    .notification.success {
        background-color: rgba(76, 175, 80, 0.2);
        border: 1px solid var(--success);
        color: var(--success);
    }
    
    .notification.error {
        background-color: rgba(244, 67, 54, 0.2);
        border: 1px solid var(--danger);
        color: var(--danger);
    }
    
    /* Confetti animation */
    .confetti {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 9999;
    }
    
    .confetti-piece {
        position: absolute;
        width: 10px;
        height: 10px;
        background: var(--primary);
        top: -10px;
        opacity: 0;
    }
    
    .confetti-piece:nth-child(1) {
        left: 7%;
        background-color: var(--primary);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 182ms;
        animation-duration: 1116ms;
    }
    
    .confetti-piece:nth-child(2) {
        left: 14%;
        background-color: var(--secondary);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 161ms;
        animation-duration: 1076ms;
    }
    
    .confetti-piece:nth-child(3) {
        left: 21%;
        background-color: var(--accent);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 481ms;
        animation-duration: 1103ms;
    }
    
    .confetti-piece:nth-child(4) {
        left: 28%;
        background-color: var(--primary);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 334ms;
        animation-duration: 708ms;
    }
    
    .confetti-piece:nth-child(5) {
        left: 35%;
        background-color: var(--secondary);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 308ms;
        animation-duration: 872ms;
    }
    
    .confetti-piece:nth-child(6) {
        left: 42%;
        background-color: var(--accent);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 180ms;
        animation-duration: 1168ms;
    }
    
    .confetti-piece:nth-child(7) {
        left: 49%;
        background-color: var(--primary);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 390ms;
        animation-duration: 1200ms;
    }
    
    .confetti-piece:nth-child(8) {
        left: 56%;
        background-color: var(--secondary);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 169ms;
        animation-duration: 1056ms;
    }
    
    .confetti-piece:nth-child(9) {
        left: 63%;
        background-color: var(--accent);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 169ms;
        animation-duration: 776ms;
    }
    
    .confetti-piece:nth-child(10) {
        left: 70%;
        background-color: var(--primary);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 351ms;
        animation-duration: 1063ms;
    }
    
    .confetti-piece:nth-child(11) {
        left: 77%;
        background-color: var(--secondary);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 307ms;
        animation-duration: 1188ms;
    }
    
    .confetti-piece:nth-child(12) {
        left: 84%;
        background-color: var(--accent);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 464ms;
        animation-duration: 776ms;
    }
    
    .confetti-piece:nth-child(13) {
        left: 91%;
        background-color: var(--primary);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 287ms;
        animation-duration: 1116ms;
    }
    
    .confetti-piece:nth-child(14) {
        left: 98%;
        background-color: var(--secondary);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 398ms;
        animation-duration: 1100ms;
    }
    
    .confetti-piece:nth-child(15) {
        left: 5%;
        background-color: var(--accent);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 182ms;
        animation-duration: 1116ms;
    }
    
    .confetti-piece:nth-child(16) {
        left: 15%;
        background-color: var(--primary);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 161ms;
        animation-duration: 1076ms;
    }
    
    .confetti-piece:nth-child(17) {
        left: 25%;
        background-color: var(--secondary);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 481ms;
        animation-duration: 1103ms;
    }
    
    .confetti-piece:nth-child(18) {
        left: 35%;
        background-color: var(--accent);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 334ms;
        animation-duration: 708ms;
    }
    
    .confetti-piece:nth-child(19) {
        left: 45%;
        background-color: var(--primary);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 308ms;
        animation-duration: 872ms;
    }
    
    .confetti-piece:nth-child(20) {
        left: 55%;
        background-color: var(--secondary);
        animation: makeItRain 1000ms infinite ease-out;
        animation-delay: 180ms;
        animation-duration: 1168ms;
    }
    
    @keyframes makeItRain {
        0% {
            opacity: 0;
        }
        10% {
            opacity: 1;
        }
        90% {
            opacity: 1;
        }
        100% {
            opacity: 0;
            transform: translateY(100vh) rotate(360deg);
        }
    }
    
    /* Celebration balloons */
    .balloon {
        position: absolute;
        bottom: -80px;
        width: 22px;
        height: 30px;
        border-radius: 50% 50% 45% 45%;
        background: var(--primary);
        opacity: 0.9;
        animation: floatUp 5s ease-in infinite;
        box-shadow: inset -3px -8px 0 rgba(0,0,0,0.08);
    }
    
    .balloon:after {
        content: '';
        position: absolute;
        width: 2px;
        height: 14px;
        background: #ccc;
        top: 30px;
        left: 10px;
    }
    
    .balloon:nth-child(1) { left: 10%; animation-delay: 0s; background: var(--primary); }
    .balloon:nth-child(2) { left: 25%; animation-delay: 0.6s; background: var(--secondary); }
    .balloon:nth-child(3) { left: 40%; animation-delay: 0.3s; background: var(--accent); }
    .balloon:nth-child(4) { left: 55%; animation-delay: 0.8s; background: #FFB6C1; }
    .balloon:nth-child(5) { left: 70%; animation-delay: 0.4s; background: #FFD1DC; }
    .balloon:nth-child(6) { left: 85%; animation-delay: 1s; background: #FFC0CB; }
    
    @keyframes floatUp {
        0% { transform: translateY(0); opacity: 0; }
        20% { opacity: 1; }
        100% { transform: translateY(-120vh); opacity: 0; }
    }
    
    /* Celebration container */
    .celebration {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 9999;
        overflow: hidden;
    }
    
    /* Loyalty points badge */
    .loyalty-badge {
        background: linear-gradient(45deg, var(--primary), var(--accent));
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        display: inline-block;
        margin-left: 10px;
        animation: glowPulse 3s infinite;
    }
    
    @keyframes glowPulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 105, 180, 0.4); }
        50% { box-shadow: 0 0 0 10px rgba(255, 105, 180, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 105, 180, 0); }
    }
    
    /* Dashboard cards */
    .dashboard-card {
        background: white;
        color: var(--text);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: transform 0.3s ease;
        border-top: 4px solid var(--primary);
    }
    
    .dashboard-card p, .dashboard-card li {
        color: #333333;
    }
    
    .dashboard-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    
    .dashboard-card h3 {
        margin-top: 0;
        color: var(--dark);
        border-bottom: 1px solid #eee;
        padding-bottom: 0.5rem;
    }
    
    /* Stats numbers */
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary);
        text-align: center;
        margin: 1rem 0;
    }
    
    /* Chart container */
    .chart-container {
        background: white;
        color: var(--text);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    /* Loading animation */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255,255,255,.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 1s ease-in-out infinite;
        margin-right: 10px;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

# Main app
def main():
    init_db()
    local_css()
    
    try:
        # Check for query params (compatible with Streamlit 1.50+)
        if "go" in st.query_params:
            go = st.query_params.get("go")
            if go == "book":
                st.session_state.navigate_to = "Book Appointment"
                service_param = st.query_params.get("service")
                if service_param:
                    st.session_state.preselected_service = urllib.parse.unquote_plus(service_param)
                st.query_params.clear()
            elif go == "instant_book":
                service_param = st.query_params.get("service")
                if service_param:
                    service_name = urllib.parse.unquote_plus(service_param)
                else:
                    service_name = None
                if st.session_state.logged_in and service_name:
                    now = datetime.now()
                    hour = now.hour
                    minute = now.minute
                    if minute < 30:
                        minute_next = 30
                        hour_next = hour
                    else:
                        minute_next = 0
                        hour_next = hour + 1
                    if hour_next < 9:
                        hour_next = 9
                        minute_next = 0
                    date_dt = now
                    if hour_next >= 19:
                        date_dt = now + timedelta(days=1)
                        hour_next = 9
                        minute_next = 0
                    time_str = f"{hour_next:02d}:{minute_next:02d}"
                    date_str = date_dt.strftime("%Y-%m-%d")
                    date_label = date_dt.strftime("%A, %B %d")
                    if book_appointment(st.session_state.user_id, service_name, date_str, time_str):
                        update_loyalty_points(st.session_state.user_id, 10)
                        st.session_state.show_confetti = True
                        st.session_state.flash_message = f"🎉 Appointment for {service_name} on {date_label} at {time_str} booked!"
                        st.session_state.navigate_to = "My Appointments"
                    else:
                        st.session_state.flash_message = "❌ Failed to book. Please try again."
                        st.session_state.navigate_to = "Book Appointment"
                        st.session_state.preselected_service = service_name
                else:
                    st.session_state.navigate_to = "Book Appointment"
                    st.session_state.preselected_service = service_name
                st.query_params.clear()
    except Exception:
        pass

    # Trigger celebration overlay if needed
    if st.session_state.show_confetti:
        render_celebration()
        st.session_state.show_confetti = False

    # Render the actual app UI
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_main_app()

def render_celebration():
    """Render confetti + balloons overlay when a slot is booked."""
    st.markdown("""
    <div class="celebration">
        <div class="confetti">
            <div class="confetti-piece"></div>
            <div class="confetti-piece"></div>
            <div class="confetti-piece"></div>
            <div class="confetti-piece"></div>
            <div class="confetti-piece"></div>
            <div class="confetti-piece"></div>
            <div class="confetti-piece"></div>
            <div class="confetti-piece"></div>
            <div class="confetti-piece"></div>
            <div class="confetti-piece"></div>
        </div>
        <div class="balloon"></div>
        <div class="balloon"></div>
        <div class="balloon"></div>
    </div>
    """, unsafe_allow_html=True)

def book_next_available_slot(service_name: str):
    """Book the next available half-hour slot during business hours for the given service."""
    try:
        # Check if user is logged in
        if not st.session_state.logged_in or not st.session_state.get("user_id"):
            st.session_state.preselected_service = service_name
            st.session_state.flash_message = "🔐 Please log in to book an appointment."
            st.session_state.navigate_to = "Book Appointment"
            st.rerun()
            return
        
        # Calculate next available slot
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        
        # Round up to next half hour
        if minute < 30:
            minute_next = 30
            hour_next = hour
        else:
            minute_next = 0
            hour_next = hour + 1
        
        # Ensure it's within business hours (9 AM - 7 PM)
        if hour_next < 9:
            hour_next = 9
            minute_next = 0
        
        date_dt = now
        # If past closing time, book for next day
        if hour_next >= 19:
            date_dt = now + timedelta(days=1)
            hour_next = 9
            minute_next = 0
        
        time_str = f"{hour_next:02d}:{minute_next:02d}"
        date_str = date_dt.strftime("%Y-%m-%d")
        date_label = date_dt.strftime("%A, %B %d")
        
        # Book the appointment
        if book_appointment(st.session_state.user_id, service_name, date_str, time_str):
            # Award loyalty points
            update_loyalty_points(st.session_state.user_id, 10)
            st.session_state.show_confetti = True
            st.session_state.flash_message = f"🎉 Appointment for {service_name} on {date_label} at {time_str} booked!"
            st.session_state.navigate_to = "My Appointments"
            st.rerun()
        else:
            st.error("❌ Failed to book appointment. Please try again or select a different time.")
    except Exception as e:
        st.error(f"❌ Error booking slot: {str(e)}")
    
    if st.session_state.flash_message:
        st.success(st.session_state.flash_message)
        st.session_state.flash_message = None
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_main_app()

# Login/Register page
def show_login_page():
    # Split Layout: Left Text/Form, Right Image
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown('<h1 class="landing-title">Redefine Your<br><span style="color: var(--primary);">Beauty Journey</span></h1>', unsafe_allow_html=True)
        st.markdown('<p class="landing-subtitle">Experience luxury services tailored exclusively for women. Join our community of over 500+ satisfied clients and discover your true glow.</p>', unsafe_allow_html=True)
        
        # Login Form
        st.markdown("<h2 style='margin-bottom: 1.5rem; margin-top: 1rem; font-family: Playfair Display, serif; color: #333;'>Welcome Back</h2>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            name = st.text_input("Name", placeholder="Enter your full name")
            phone = st.text_input("Phone Number", placeholder="10-digit mobile number")
            st.caption("We'll create a new account if one doesn't exist.")
            
            submitted = st.form_submit_button("Start Your Journey", use_container_width=True)
            
            if submitted:
                if name and phone:
                    if len(phone) == 10 and phone.isdigit():
                        # Register user if not exists
                        if register_user(name, phone):
                            st.success(f"Welcome {name}! Your account has been created.")
                        else:
                            st.info(f"Welcome back {name}!")
                        
                        # Set session state
                        st.session_state.logged_in = True
                        st.session_state.user_name = name
                        st.session_state.phone_number = phone
                        
                        # Get user ID
                        user_id = get_user_id(phone)
                        st.session_state.user_id = user_id
                        
                        st.rerun()
                    else:
                        st.error("Please enter a valid 10-digit phone number")
                else:
                    st.error("Please enter both name and phone number")
        
        # Auto-focus Script
        components.html("""
        <script>
            function setupFocus() {
                try {
                    const doc = window.parent.document;
                    const inputs = doc.querySelectorAll('input[type="text"]');
                    let nameInput = null;
                    let phoneInput = null;
                    
                    // Find inputs by placeholder or label since IDs change
                    inputs.forEach(input => {
                        if (input.getAttribute('aria-label') === "Name") nameInput = input;
                        if (input.getAttribute('aria-label') === "Phone Number") phoneInput = input;
                    });
                    
                    if (nameInput && phoneInput) {
                        nameInput.addEventListener('keydown', function(e) {
                            if (e.key === 'Enter') {
                                e.preventDefault();
                                phoneInput.focus();
                            }
                        });
                    }
                } catch (e) {
                    console.log("Focus script error:", e);
                }
            }
            // Try multiple times to ensure elements are rendered
            setTimeout(setupFocus, 500);
            setTimeout(setupFocus, 1000);
            setTimeout(setupFocus, 2000);
        </script>
        """, height=0, width=0)

    with col2:
        # High quality portrait image with floating animation
        st.markdown("""
            <img src="https://images.unsplash.com/photo-1562322140-8baeececf3df?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80" 
                 class="login-hero-img" alt="Expert Styling & Care">
            <p style="text-align: center; color: #555; margin-top: 10px; font-style: italic;">Expert Styling & Care</p>
        """, unsafe_allow_html=True)

    # Features Section
    st.markdown("---")
    st.markdown("<h3 style='text-align: center; margin-bottom: 2rem;'>Why Choose Glamour Salon?</h3>", unsafe_allow_html=True)
    
    f1, f2, f3 = st.columns(3)
    
    with f1:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">💇‍♀️</div>
            <h4>Expert Stylists</h4>
            <p>Our team of certified professionals are trained in the latest international techniques.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with f2:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🌿</div>
            <h4>Premium Products</h4>
            <p>We use only high-quality, cruelty-free and organic products for your skin and hair.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with f3:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">✨</div>
            <h4>Luxury Ambience</h4>
            <p>Relax in our serene, hygienic environment designed exclusively for your comfort.</p>
        </div>
        """, unsafe_allow_html=True)

# Main application after login
def show_main_app():
    # Sidebar navigation
    st.sidebar.markdown(f"<h3 style='color: var(--dark);'>Hello, {st.session_state.user_name}!</h3>", unsafe_allow_html=True)
    
    # Display loyalty points in sidebar
    user_details = get_user_details(st.session_state.user_id)
    if user_details:
        _, _, loyalty_points = user_details
        st.session_state.loyalty_points = loyalty_points
        st.sidebar.markdown(f"<div class='loyalty-badge'>💎 {loyalty_points} Points</div>", unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Check if user is admin (for demo purposes, we'll use a special phone number)
    is_admin = st.session_state.phone_number == "0000000000"
    
    menu_options = ["Home", "Profile", "Services", "Book Appointment", "My Appointments", "Contact Us"]
    if is_admin:
        menu_options.append("Admin Panel")
    menu_options.append("Logout")
    
    default_index = 0
    if st.session_state.navigate_to and st.session_state.navigate_to in menu_options:
        try:
            default_index = menu_options.index(st.session_state.navigate_to)
        except Exception:
            default_index = 0

    # Use radio buttons instead of a dropdown for better readability and accessibility
    menu = st.sidebar.radio(
        "Navigation",
        menu_options,
        index=default_index,
        key="nav_select_radio",
    )
    st.session_state.navigate_to = None
    
    if menu == "Home":
        show_home_page()
    elif menu == "Profile":
        show_profile_page()
    elif menu == "Services":
        show_services_page()
    elif menu == "Book Appointment":
        show_booking_page()
    elif menu == "My Appointments":
        show_my_appointments()
    elif menu == "Contact Us":
        show_contact_page()
    elif menu == "Admin Panel":
        show_admin_panel()
    elif menu == "Logout":
        logout()

def show_home_page():
    # Hero Banner
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-overlay">
            <h1 id="hero-title-text" class="hero-title">Welcome to Glamour Salon</h1>
            <p id="hero-subtitle-text" class="hero-subtitle">Where Beauty Meets Elegance - Exclusively for Women</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; margin: 2rem 0;'>
        <h3>Your Journey to Beauty and Confidence Starts Here</h3>
        <p style='font-size: 1.1rem; max-width: 800px; margin: 0 auto; color: #000000;'>
            At Glamour Salon, we specialize in bringing out the natural beauty of every woman. 
            Our expert stylists are dedicated to providing personalized services in a luxurious, 
            comfortable environment designed exclusively for women.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Service recommendations based on booking history
    st.markdown("<h3>🎯 Recommended For You</h3>", unsafe_allow_html=True)
    recommendations = get_service_recommendations(st.session_state.user_id)
    
    if recommendations is not None and len(recommendations) > 0:
        cols = st.columns(2)
        for i in range(min(len(recommendations), 4)):  # Limit to 4 recommendations
            service = recommendations.iloc[i]
            with cols[i % 2]:
                # Handle description safely
                description = ""
                if 'description' in service:
                    if pd.notna(service['description']):
                        description = str(service['description'])
                service_name_encoded = urllib.parse.quote_plus(str(service['name']))
                
                st.markdown(f"""
                <div class="service-card">
                    <div style="display: flex; justify-content: space-between;">
                        <h4>{service['name']}</h4>
                        <h4 style="color: var(--primary);">₹{service['price']:.2f}</h4>
                    </div>
                    <p><strong>Category:</strong> {service['category']}</p>
                    <p>{description}</p>
                """, unsafe_allow_html=True)
                book_button = st.button("Book Now", key=f"book_rec_{i}", use_container_width=True)
                if book_button:
                    book_next_available_slot(str(service['name']))
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Book your first service to get personalized recommendations!")
    
    # Services preview
    st.markdown("<h3>🌟 Popular Services</h3>", unsafe_allow_html=True)
    services_df = get_services()
    
    # Show top 4 services
    top_services = services_df.head(4)
    
    cols = st.columns(2)
    for i, (index, service) in enumerate(top_services.iterrows()):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="service-card">
                <div style="display: flex; justify-content: space-between;">
                    <h4>{service['name']}</h4>
                    <h4 style="color: var(--primary);">₹{service['price']:.2f}</h4>
                </div>
                <p><strong>Duration:</strong> {service['duration']} minutes</p>
                <p>{service['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            book_button = st.button("Book Now", key=f"book_top_{i}", use_container_width=True)
            if book_button:
                book_next_available_slot(str(service['name']))

def show_profile_page():
    st.markdown("<h2>👤 My Profile</h2>", unsafe_allow_html=True)
    
    # Get user details
    user_details = get_user_details(st.session_state.user_id)
    if user_details:
        name, phone, loyalty_points = user_details
        st.session_state.loyalty_points = loyalty_points
    else:
        name, phone, loyalty_points = st.session_state.user_name, st.session_state.phone_number, 0
    
    # User information card
    st.markdown(f"""
    <div class="dashboard-card">
        <h3>Personal Information</h3>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Phone:</strong> {phone}</p>
        <p><strong>Member Since:</strong> {datetime.now().strftime("%B %Y")}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Loyalty points card (rendered via components to avoid Markdown code-block formatting)
    components.html(
        dedent(
            f"""
            <div class="dashboard-card">
                <h3>💎 Loyalty Points</h3>
                <div class="stat-number">{loyalty_points}</div>
                <p style="text-align: center;">Redeem your points for discounts on services!</p>
                
                <div style="display: flex; justify-content: space-around; margin-top: 2rem;">
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: var(--primary);">100 pts</div>
                        <div>10% off any service</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: var(--primary);">250 pts</div>
                        <div>20% off any service</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: var(--primary);">500 pts</div>
                        <div>30% off any service</div>
                    </div>
                </div>
            </div>
            """
        ),
        height=320,
        scrolling=False,
    )
    
    # Loyalty points history
    components.html(
        dedent(
            """
            <div class="dashboard-card">
                <h3>Points History</h3>
                <ul>
                    <li>✅ Booking completed: +10 points</li>
                    <li>⭐ Service review: +5 points</li>
                    <li>📅 Appointment kept: +5 points</li>
                    <li>👥 Referral: +20 points</li>
                    <li>❌ Cancellation: -5 points</li>
                </ul>
            </div>
            """
        ),
        height=260,
        scrolling=False,
    )
    
    # Redeem points form
    st.markdown("<h3>🎁 Redeem Points</h3>", unsafe_allow_html=True)
    with st.form("redeem_points"):
        points_options = [0, 100, 250, 500]
        selected_points = st.select_slider("Select points to redeem", options=points_options)
        
        # Ensure selected_points is an integer
        if isinstance(selected_points, tuple):
            selected_points = int(selected_points[0]) if selected_points else 0
        else:
            selected_points = int(selected_points)
        
        discount = 0
        if selected_points > 0:
            discount = selected_points // 10  # 10 points = 1% discount
            st.info(f"You can get {discount}% off your next service!")
        
        submitted = st.form_submit_button("Redeem Points")
        if submitted and selected_points > 0:
            if loyalty_points >= selected_points:
                # Update loyalty points
                update_loyalty_points(st.session_state.user_id, -selected_points)
                remaining_points = int(loyalty_points) - int(selected_points)
                st.success(f"🎉 Successfully redeemed {selected_points} points! You now have {remaining_points} points remaining.")
                st.info(f"Apply your {discount}% discount at checkout!")
                st.rerun()
            else:
                st.error("❌ You don't have enough points for this redemption.")

def show_services_page():
    st.markdown("<h2>💇‍♀️ Our Services</h2>", unsafe_allow_html=True)
    
    services_df = get_services()
    
    # Group services by category
    categories = services_df['category'].unique()
    
    for category in categories:
        st.markdown(f"<h3 style='color: var(--accent);'>{category}</h3>", unsafe_allow_html=True)
        category_services = services_df[services_df['category'] == category]
        
        for _, service in category_services.iterrows():
            st.markdown(f"""
            <div class="service-card">
                <div style="display: flex; justify-content: space-between;">
                    <h4>{service['name']}</h4>
                    <h4 style="color: var(--primary);">₹{service['price']:.2f}</h4>
                </div>
                <p><strong>Duration:</strong> {service['duration']} minutes</p>
                <p>{service['description']}</p>
            </div>
            """, unsafe_allow_html=True)

def show_booking_page():
    st.markdown("<h2>📅 Book Appointment</h2>", unsafe_allow_html=True)
    st.caption("Choose a service, pick a date and select a time between 09:00 and 18:30.")
    
    services_df = get_services()
    if services_df is None or services_df.empty:
        st.error("No services available right now. Please check back later.")
        return
    
    service_options = [f"{row['name']} (₹{row['price']:.2f})" for _, row in services_df.iterrows()]
    service_dict = {f"{row['name']} (₹{row['price']:.2f})": row['name'] for _, row in services_df.iterrows()}
    
    # Calculate default time
    now = datetime.now()
    minute = now.minute
    next_minute = 30 if minute < 30 else 0
    next_hour = now.hour if minute < 30 else now.hour + 1
    if next_hour < 9:
        next_hour = 9
        next_minute = 0
    default_time = datetime(now.year, now.month, now.day, next_hour, next_minute).time()

    # Determine default index
    default_index = 0
    
    # Check if we have a preselected service from navigation
    if st.session_state.preselected_service:
        try:
            for idx, label in enumerate(service_options):
                if service_dict.get(label) == st.session_state.preselected_service:
                    default_index = idx
                    # Update the widget state to match preselection
                    st.session_state.booking_service = label
                    break
        except Exception:
            default_index = 0
        # Clear preselection so it doesn't persist and lock the dropdown
        st.session_state.preselected_service = None

    # Layout: 2 Columns (Inputs | Summary) - Responsive
    main_cols = st.columns([2, 1], gap="large")
    
    with main_cols[0]:
        with st.container():
            st.markdown("### 1. Select Service")
            
            # Use the key to manage state, but respect default_index if key is not yet set
            # If key is in session_state, index argument is ignored by Streamlit
            if "booking_service" not in st.session_state:
                 st.session_state.booking_service = service_options[default_index] if service_options else None
            
            # Find current index from session state to avoid warnings if possible, 
            # though Streamlit handles this via key mostly.
            current_val = st.session_state.get("booking_service")
            current_idx = 0
            if current_val in service_options:
                current_idx = service_options.index(current_val)
            
            service_selected = st.selectbox(
                "Choose Service", 
                service_options, 
                index=current_idx, 
                key="booking_service"
            )
            
            service_name = service_dict.get(service_selected, service_options[0] if service_options else "")
            st.caption("Service price is shown next to the name.")
            
            st.markdown("### 2. Select Date & Time")
            d_cols = st.columns(2)
            with d_cols[0]:
                today = datetime.today().date()
                date_input = st.date_input(
                    "Date",
                    value=today,
                    min_value=today,
                    max_value=today + timedelta(days=14),
                    key="booking_date"
                )
            with d_cols[1]:
                time_input = st.time_input("Time", value=default_time, step=1800, key="booking_time")
            
            if not (9 <= time_input.hour < 19):
                st.warning("⚠️ Please select a time between 09:00 and 18:30.")

    # Prepare summary data
    date_selected = date_input.strftime("%Y-%m-%d")
    date_label = date_input.strftime("%A, %B %d")
    time_selected = f"{time_input.hour:02d}:{time_input.minute:02d}"

    with main_cols[1]:
        st.markdown("### Summary")
        st.markdown(f"""
        <div class="appointment-card" style="border: 2px solid var(--primary); padding: 1.5rem;">
            <div style="display:flex;justify-content:space-between;margin-bottom:1rem;border-bottom:1px solid #eee;padding-bottom:0.5rem;">
                <h4 style="margin:0;">Selection</h4>
                <h4 style="color:var(--primary);margin:0;">{time_selected}</h4>
            </div>
            <p style="margin-bottom:0.5rem;"><strong>Service:</strong><br>{service_name}</p>
            <p style="margin-bottom:0.5rem;"><strong>Date:</strong><br>{date_label}</p>
            <p style="margin-bottom:0.5rem;"><strong>Time:</strong><br>{time_selected}</p>
            <hr style="margin: 1rem 0; border: 0; border-top: 1px solid #eee;">
            <p style="font-size: 0.85rem; color: #666; line-height: 1.6;">
                <span style="color: var(--primary); font-weight:bold;">✓</span> Free Cancellation<br>
                <span style="color: var(--primary); font-weight:bold;">✓</span> Instant Confirmation
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Confirm Booking", type="primary", use_container_width=True):
            if 9 <= time_input.hour < 19:
                if book_appointment(st.session_state.user_id, service_name, date_selected, time_selected):
                    st.success(f"🎉 Appointment booked successfully for {date_label} at {time_selected}")
                    st.session_state.show_confetti = True
                    update_loyalty_points(st.session_state.user_id, 10)
                    st.session_state.preselected_service = None
                    st.rerun()
                else:
                    st.error("❌ Failed to book appointment. Please try again.")
            else:
                st.error("Please select a valid time slot.")

def show_my_appointments():
    st.markdown("<h2>🗓️ My Appointments</h2>", unsafe_allow_html=True)
    
    # Get user appointments
    appointments_df = get_user_appointments(st.session_state.user_id)
    
    if appointments_df.empty:
        st.info("You don't have any appointments yet. Book your first appointment!")
        if st.button("Book Now"):
            st.session_state.navigate_to = "Book Appointment"
            st.session_state.preselected_service = None
            st.rerun()
    else:
        # Add filtering and sorting options
        st.markdown("<h3>Filter & Sort Appointments</h3>", unsafe_allow_html=True)
        
        # Create filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            # Status filter (radio buttons for better readability)
            status_options = ["All"] + list(appointments_df['status'].unique())
            selected_status = st.radio(
                "Filter by Status",
                status_options,
                index=0,
                key="appt_status_filter",
            )
        
        with col2:
            # Sort by date or time (radio buttons)
            sort_options = ["Date (Ascending)", "Date (Descending)", "Time (Ascending)", "Time (Descending)"]
            selected_sort = st.radio(
                "Sort By",
                sort_options,
                index=0,
                key="appt_sort_by",
            )
        
        with col3:
            # Date range filter (radio buttons)
            date_range = st.radio(
                "Date Range",
                ["Upcoming", "All Time", "Last 7 Days", "Last 30 Days", "Next 7 Days", "Next 30 Days"],
                index=0,
                key="appt_date_range",
            )
        
        # Apply filters
        filtered_df = appointments_df.copy()
        
        # Apply status filter
        if selected_status != "All":
            filtered_df = filtered_df[filtered_df['status'] == selected_status]
        
        # Apply date range filter
        today = datetime.now().date()
        if date_range != "All Time":
            try:
                # Create a list to store indices of rows that match the filter
                filtered_indices = []
                
                for idx, row in filtered_df.iterrows():
                    try:
                        # Convert to string explicitly
                        date_str = str(row['date'])
                        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        
                        if date_range == "Upcoming":
                            if appointment_date >= today:
                                filtered_indices.append(idx)
                        elif date_range == "Last 7 Days":
                            week_ago = today - timedelta(days=7)
                            if appointment_date >= week_ago and appointment_date <= today:
                                filtered_indices.append(idx)
                        elif date_range == "Last 30 Days":
                            month_ago = today - timedelta(days=30)
                            if appointment_date >= month_ago and appointment_date <= today:
                                filtered_indices.append(idx)
                        elif date_range == "Next 7 Days":
                            week_ahead = today + timedelta(days=7)
                            if today <= appointment_date <= week_ahead:
                                filtered_indices.append(idx)
                        elif date_range == "Next 30 Days":
                            month_ahead = today + timedelta(days=30)
                            if today <= appointment_date <= month_ahead:
                                filtered_indices.append(idx)
                    except:
                        # If date parsing fails, skip this row
                        pass
                
                # Filter the DataFrame using the collected indices
                # Even if filtered_indices is empty, we should filter to show empty result
                filtered_df = filtered_df.loc[filtered_indices]
            except Exception as e:
                st.warning(f"Date filtering encountered an issue: {str(e)}")
        
        # Apply sorting
        try:
            if selected_sort == "Date (Ascending)" or selected_sort == "Date (Descending)":
                # Create a temporary column for sorting by date
                date_list = []
                for _, row in filtered_df.iterrows():
                    try:
                        # Convert to string explicitly
                        date_str = str(row['date'])
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        date_list.append(date_obj)
                    except:
                        date_list.append(datetime.min)
                
                filtered_df.loc[:, 'temp_date_sort'] = date_list
                ascending = (selected_sort == "Date (Ascending)")
                # Use a more defensive approach for sorting
                try:
                    sorted_indices = filtered_df['temp_date_sort'].sort_values(ascending=ascending).index
                    filtered_df = filtered_df.loc[sorted_indices]
                except:
                    pass
                filtered_df = filtered_df.drop('temp_date_sort', axis=1)
            elif selected_sort == "Time (Ascending)" or selected_sort == "Time (Descending)":
                ascending = (selected_sort == "Time (Ascending)")
                # Use a more defensive approach for sorting
                try:
                    sorted_indices = filtered_df['time'].sort_values(ascending=ascending).index
                    filtered_df = filtered_df.loc[sorted_indices]
                except:
                    pass
        except Exception as e:
            st.warning(f"Sorting encountered an issue: {str(e)}")
        
        # Display filtered appointments
        if filtered_df.empty:
            st.info("No appointments match your filters.")
        else:
            st.markdown(f"<h3>Your Appointments ({len(filtered_df)} found)</h3>", unsafe_allow_html=True)
            for _, appointment in filtered_df.iterrows():
                status_str = str(appointment['status']) if appointment['status'] is not None else "unknown"
                status_color = "green" if status_str == 'booked' else "red"
                status_badge = f"<span style='color: {status_color}; font-weight: bold;'>{status_str.upper()}</span>"
                st.markdown(f"""
                <div class="appointment-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4>{appointment['service']}</h4>
                            <p><strong>Date:</strong> {appointment['date']}</p>
                            <p><strong>Time:</strong> {appointment['time']}</p>
                        </div>
                        <div style="text-align: right;">
                            {status_badge}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Add cancel button functionality below the card (Streamlit native button)
                if status_str == 'booked':
                    if st.button("Cancel Appointment", key=f"cancel_{appointment['id']}"):
                        cancel_appointment(appointment['id'])
                        st.success("Appointment cancelled successfully!")
                        # Deduct loyalty points for cancellation
                        update_loyalty_points(st.session_state.user_id, -5)
                        st.rerun()

def show_gallery():
    st.markdown("<h2>📸 Salon Gallery</h2>", unsafe_allow_html=True)
    
    # Import image manager
    try:
        from image_manager import ImageManager
        manager = ImageManager()
        local_images = manager.get_local_images()
        
        if local_images:
            # Group images by category
            categorized_images = {}
            for image_path in local_images:
                info = manager.get_image_info(image_path)
                if info:
                    category = info['category']
                    if category not in categorized_images:
                        categorized_images[category] = []
                    categorized_images[category].append(info)
            
            # Display images by category
            for category, images in categorized_images.items():
                st.markdown(f"<h3>{category}</h3>", unsafe_allow_html=True)
                cols = st.columns(3)
                
                for i, image_info in enumerate(images):
                    with cols[i % 3]:
                        # Convert image to base64 for embedding
                        img_base64 = get_image_base64(image_info['path'])
                        if img_base64:
                            st.markdown(f"""
                            <div class="gallery-item">
                                <img src="data:image/{image_info['format'].lower()};base64,{img_base64}" alt="{image_info['filename']}">
                                <div class="gallery-caption">{image_info['filename'].replace('_', ' ').replace('.jpg', '').title()}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            # Fallback to showing file name
                            st.markdown(f"""
                            <div class="gallery-item">
                                <div style="background-color: #f0f0f0; height: 200px; display: flex; align-items: center; justify-content: center;">
                                    <span>Image: {image_info['filename']}</span>
                                </div>
                                <div class="gallery-caption">{image_info['filename'].replace('_', ' ').replace('.jpg', '').title()}</div>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            # Fallback to sample gallery images if no local images found
            st.info("No local images found. Displaying sample images.")
            gallery_images = [
                ("https://images.unsplash.com/photo-1560066984-138dadb4c85a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80", "Salon Interior"),
                ("https://images.unsplash.com/photo-1595475882656-77a42b8840c0?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80", "Hair Styling Station"),
                ("https://images.unsplash.com/photo-1522338242992-e1a54906a8da?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80", "Makeup Artist at Work"),
                ("https://images.unsplash.com/photo-1596347289140-0df7729fe7bd?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80", "Nail Art Station"),
                ("https://images.unsplash.com/photo-1600857062241-98c0a9ed8f63?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80", "Facial Treatment Room"),
                ("https://images.unsplash.com/photo-1595476276938-710a5de2a23d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80", "Hair Coloring Station")
            ]
            
            st.markdown('<div class="gallery-grid">', unsafe_allow_html=True)
            
            for img_url, caption in gallery_images:
                st.markdown(f"""
                <div class="gallery-item">
                    <img src="{img_url}" alt="{caption}">
                    <div class="gallery-caption">{caption}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    except ImportError:
        # Fallback if image_manager is not available
        st.info("Image manager not available. Displaying sample images.")
        gallery_images = [
            ("https://images.unsplash.com/photo-1560066984-138dadb4c85a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80", "Salon Interior"),
            ("https://images.unsplash.com/photo-1595475882656-77a42b8840c0?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80", "Hair Styling Station"),
            ("https://images.unsplash.com/photo-1522338242992-e1a54906a8da?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80", "Makeup Artist at Work"),
            ("https://images.unsplash.com/photo-1596347289140-0df7729fe7bd?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80", "Nail Art Station"),
            ("https://images.unsplash.com/photo-1600857062241-98c0a9ed8f63?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80", "Facial Treatment Room"),
            ("https://images.unsplash.com/photo-1595476276938-710a5de2a23d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80", "Hair Coloring Station")
        ]
        
        st.markdown('<div class="gallery-grid">', unsafe_allow_html=True)
        
        for img_url, caption in gallery_images:
            st.markdown(f"""
            <div class="gallery-item">
                <img src="{img_url}" alt="{caption}">
                <div class="gallery-caption">{caption}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_contact_page():
    st.markdown("<h2>📞 Contact Us</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Visit Our Salon")
        st.markdown("""
        **📍 Address:**  
        E-168 Indrapuram  
        Ghaziabad  
        State – 102100
        
        **🕒 Opening Hours:**  
        Monday – Friday: 9:00 AM  
        Saturday: 9:00 AM  
        Sunday: Closed
        
        **☎️ Phone:**  
        9871509370
        
        **✉️ Email:**  
        srashtikagautam469@gmail.com
        """)
        
        st.markdown("### Follow Us")
        st.markdown("""
        <div style="font-size: 2rem; margin-top: 1rem;">
        <a href="#" style="margin-right: 1rem; color: var(--primary);">📱</a>
        <a href="#" style="margin-right: 1rem; color: var(--primary);">📘</a>
        <a href="#" style="margin-right: 1rem; color: var(--primary);">📷</a>
        <a href="#" style="color: var(--primary);">🐦</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Book Through WhatsApp")
        st.markdown("""
        Quick & Easy Booking:  
        [![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://wa.me/919871509370)
        """)

def show_admin_panel():
    st.markdown("<h2>🔧 Admin Panel</h2>", unsafe_allow_html=True)
    
    admin_tabs = st.tabs(["Service Management", "Image Management", "Analytics", "User Management"])
    
    with admin_tabs[0]:
        st.markdown("<h3>Service Management</h3>", unsafe_allow_html=True)
        
        services_df = get_services()
        
        st.markdown("<h4>Add New Service</h4>", unsafe_allow_html=True)
        with st.form("add_service"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Service Name")
                price = st.number_input("Price (₹)", min_value=0.0, step=5.0)
            with col2:
                duration = st.number_input("Duration (minutes)", min_value=15, step=15)
                category = st.selectbox("Category", ["Hair", "Skin", "Waxing", "Nails", "Makeup", "Other"])
            
            description = st.text_area("Description")
            
            submitted = st.form_submit_button("Add Service")
            if submitted:
                if name and price > 0 and duration > 0:
                    conn = sqlite3.connect('salon.db')
                    c = conn.cursor()
                    try:
                        c.execute(
                            "INSERT INTO services (name, price, duration, description, category) VALUES (?, ?, ?, ?, ?)",
                            (name, price, duration, description, category),
                        )
                        conn.commit()
                        st.success(f"✅ Service '{name}' added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error adding service: {e}")
                    finally:
                        conn.close()
                else:
                    st.error("❌ Please fill in all required fields")
        
        st.markdown("<h4>Existing Services</h4>", unsafe_allow_html=True)
        if not services_df.empty:
            for _, service in services_df.iterrows():
                with st.expander(f"{service['name']} - ₹{service['price']:.2f}"):
                    st.markdown(f"**Category:** {service['category']}")
                    st.markdown(f"**Duration:** {service['duration']} minutes")
                    st.markdown(f"**Description:** {service['description']}")
                    
                    with st.form(f"edit_service_{service['id']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            new_name = st.text_input("Service Name", value=str(service['name']))
                            new_price = st.number_input(
                                "Price (₹)", min_value=0.0, step=5.0, value=float(service['price'])
                            )
                        with col2:
                            new_duration = st.number_input(
                                "Duration (minutes)", min_value=15, step=15, value=int(service['duration'])
                            )
                            category_options = ["Hair", "Skin", "Waxing", "Nails", "Makeup", "Other"]
                            service_category = "Other"
                            try:
                                service_category = (
                                    str(service['category']) if service['category'] is not None else "Other"
                                )
                            except Exception:
                                service_category = "Other"
                            current_category = (
                                service_category if service_category in category_options else "Other"
                            )
                            category_index = (
                                category_options.index(current_category)
                                if current_category in category_options
                                else 5
                            )
                            new_category = st.selectbox("Category", category_options, index=category_index)
                        
                        description_value = ""
                        try:
                            description_value = (
                                str(service['description']) if service['description'] is not None else ""
                            )
                        except Exception:
                            description_value = ""
                        new_description = st.text_area("Description", value=description_value)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            update_submitted = st.form_submit_button("Update Service")
                        with col2:
                            delete_submitted = st.form_submit_button("Delete Service", type="primary")
                        
                        if update_submitted:
                            conn = sqlite3.connect('salon.db')
                            c = conn.cursor()
                            try:
                                c.execute(
                                    """
                                    UPDATE services
                                    SET name = ?, price = ?, duration = ?, description = ?, category = ?
                                    WHERE id = ?
                                    """,
                                    (new_name, new_price, new_duration, new_description, new_category, service['id']),
                                )
                                conn.commit()
                                st.success(f"✅ Service '{new_name}' updated successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error updating service: {e}")
                            finally:
                                conn.close()
                        
                        if delete_submitted:
                            conn = sqlite3.connect('salon.db')
                            c = conn.cursor()
                            try:
                                c.execute("DELETE FROM services WHERE id = ?", (service['id'],))
                                conn.commit()
                                st.success(f"✅ Service '{service['name']}' deleted successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error deleting service: {e}")
                            finally:
                                conn.close()
        else:
            st.info("No services found. Add your first service above!")
    
    with admin_tabs[1]:
        st.markdown("<h3>Image Management</h3>", unsafe_allow_html=True)
        
        st.markdown("<h4>Upload New Image</h4>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png", "gif"])
        if uploaded_file is not None:
            with open(os.path.join("gallery", uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ Image '{uploaded_file.name}' uploaded successfully!")
            
            st.info("Image will be categorized automatically based on filename prefix:")
            st.markdown("- `interior_*.jpg` for interior shots")
            st.markdown("- `service_*.jpg` for service images")
            st.markdown("- `transformation_*.jpg` for before/after results")
            st.markdown("- `team_*.jpg` for staff portraits")
        
        st.markdown("<h4>Existing Images</h4>", unsafe_allow_html=True)
        try:
            from image_manager import ImageManager
            
            manager = ImageManager()
            local_images = manager.get_local_images()
            
            if local_images:
                categorized_images = {}
                for image_path in local_images:
                    info = manager.get_image_info(image_path)
                    if info:
                        category = info['category']
                        if category not in categorized_images:
                            categorized_images[category] = []
                        categorized_images[category].append(info)
                
                for category, images in categorized_images.items():
                    st.markdown(f"<h5>{category}</h5>", unsafe_allow_html=True)
                    cols = st.columns(4)
                    for i, image_info in enumerate(images):
                        with cols[i % 4]:
                            st.image(
                                image_info['path'],
                                caption=image_info['filename'],
                                use_column_width=True,
                            )
            else:
                st.info("No images found in gallery.")
        except ImportError:
            st.error("Image manager not available.")
    
    with admin_tabs[2]:
        st.markdown("<h3>Analytics Dashboard</h3>", unsafe_allow_html=True)
        
        conn = sqlite3.connect('salon.db')
        try:
            appointments_df = pd.read_sql_query(
                """
                SELECT a.*, s.name as service_name, s.price, u.name as user_name, s.category
                FROM appointments a
                JOIN services s ON a.service = s.name
                JOIN users u ON a.user_id = u.id
                ORDER BY a.date, a.time
                """,
                conn,
            )
        except Exception as e:
            appointments_df = pd.DataFrame()
            st.warning(f"Could not load appointment data: {str(e)}")
        finally:
            conn.close()
        
        if not appointments_df.empty:
            try:
                appointments_df['date'] = pd.to_datetime(appointments_df['date'])
            except Exception:
                pass
            
            total_appointments = len(appointments_df)
            total_revenue = 0
            if 'price' in appointments_df.columns:
                try:
                    total_revenue = float(appointments_df['price'].fillna(0).astype(float).sum())
                except Exception:
                    total_revenue = 0
            
            st.markdown("<h4>Key Metrics</h4>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Appointments", total_appointments)
            with col2:
                st.metric("Total Revenue", f"₹{total_revenue:.2f}")
        else:
            st.info("No appointment data available yet.")
    
    with admin_tabs[3]:
        st.markdown("<h3>User Management</h3>", unsafe_allow_html=True)
        
        conn = sqlite3.connect('salon.db')
        try:
            users_df = pd.read_sql_query("SELECT * FROM users ORDER BY created_at DESC", conn)
        except Exception as e:
            users_df = pd.DataFrame()
            st.warning(f"Could not load users: {str(e)}")
        finally:
            conn.close()
        
        if not users_df.empty:
            st.dataframe(users_df[['id', 'name', 'phone', 'loyalty_points', 'created_at']])
            
            search_term = st.text_input("Search users by name or phone")
            if search_term:
                filtered_users = users_df[
                    users_df['name'].str.contains(search_term, case=False)
                    | users_df['phone'].str.contains(search_term, case=False)
                ]
                st.dataframe(filtered_users[['id', 'name', 'phone', 'loyalty_points', 'created_at']])
        else:
            st.info("No users found.")
    
def logout():
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.phone_number = ""
    st.session_state.user_id = None
    st.session_state.loyalty_points = 0
    st.rerun()

def get_user_booking_history(user_id):
    """Get user's booking history"""
    conn = sqlite3.connect('salon.db')
    df = pd.read_sql_query("""
        SELECT a.service, a.date, s.category
        FROM appointments a
        JOIN services s ON a.service = s.name
        WHERE a.user_id = ? AND a.status = 'booked'
        ORDER BY a.date DESC
    """, conn, params=[str(user_id)])
    conn.close()
    return df

def get_service_recommendations(user_id):
    """Get service recommendations based on user's booking history"""
    try:
        # Get user's booking history
        booking_history = get_user_booking_history(user_id)
        
        if booking_history.empty:
            # If no booking history, return popular services
            conn = sqlite3.connect('salon.db')
            popular_services = pd.read_sql_query("""
                SELECT s.name, s.category, s.price, s.description
                FROM services s
                LEFT JOIN appointments a ON s.name = a.service
                GROUP BY s.id
                ORDER BY COUNT(a.service) DESC
                LIMIT 5
            """, conn)
            conn.close()
            return popular_services if popular_services is not None else pd.DataFrame()
        
        # Get user's favorite categories
        category_counts = booking_history['category'].value_counts()
        favorite_categories = category_counts.head(2).index.tolist()
        
        # If no favorite categories, return popular services
        if not favorite_categories:
            conn = sqlite3.connect('salon.db')
            popular_services = pd.read_sql_query("""
                SELECT s.name, s.category, s.price, s.description
                FROM services s
                LEFT JOIN appointments a ON s.name = a.service
                GROUP BY s.id
                ORDER BY COUNT(a.service) DESC
                LIMIT 5
            """, conn)
            conn.close()
            return popular_services if popular_services is not None else pd.DataFrame()
        
        # Get services from favorite categories that user hasn't booked recently
        conn = sqlite3.connect('salon.db')
        # Create placeholders for the IN clause
        placeholders = ','.join('?' * len(favorite_categories))
        query = f"""
            SELECT s.name, s.category, s.price, s.description
            FROM services s
            WHERE s.category IN ({placeholders})
            AND s.name NOT IN (
                SELECT service 
                FROM appointments 
                WHERE user_id = ? AND date > date('now', '-30 days')
            )
            ORDER BY RANDOM()
            LIMIT 5
        """
        # Convert all parameters to strings
        params = [str(cat) for cat in favorite_categories] + [str(user_id)]
        recommended_services = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        # If we got recommendations, return them
        if recommended_services is not None and len(recommended_services) > 0:
            return recommended_services
        
        # Otherwise, return popular services
        conn = sqlite3.connect('salon.db')
        popular_services = pd.read_sql_query("""
            SELECT s.name, s.category, s.price, s.description
            FROM services s
            LEFT JOIN appointments a ON s.name = a.service
            GROUP BY s.id
            ORDER BY COUNT(a.service) DESC
            LIMIT 5
        """, conn)
        conn.close()
        return popular_services if popular_services is not None else pd.DataFrame()
        
    except Exception as e:
        # If any error occurs, return popular services as fallback
        try:
            conn = sqlite3.connect('salon.db')
            popular_services = pd.read_sql_query("""
                SELECT s.name, s.category, s.price, s.description
                FROM services s
                LEFT JOIN appointments a ON s.name = a.service
                GROUP BY s.id
                ORDER BY COUNT(a.service) DESC
                LIMIT 5
            """, conn)
            conn.close()
            return popular_services if popular_services is not None else pd.DataFrame()
        except:
            return pd.DataFrame()

if __name__ == "__main__":
    main()
