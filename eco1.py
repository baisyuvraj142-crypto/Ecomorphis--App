import streamlit as st
import datetime
import pandas as pd
import qrcode
from PIL import Image
import io
import cv2
import numpy as np
import random

# The pyzbar import is no longer needed and has been removed.

st.set_page_config(
    page_title="Ecomorphis",
    page_icon="♻️",
    layout="wide"
)

# -------------------------
# Custom CSS for Background, Logo, and Font Styling
# -------------------------
def set_custom_style():
    st.markdown("""
        <style>
        /* Main App background */
        .stApp {
            background-image: url("https://i.ibb.co/mVrBQPdM/Whats-App-Image-2025-09-18-at-13-04-43-1.jpg");
            background-size: cover;
            background-attachment: fixed;
        }

        /* Main content area styling with a DARK overlay for readability */
        .main .block-container {
            background: rgba(10, 25, 10, 0.92); /* Dark Green semi-transparent */
            border-radius: 10px;
            padding: 2rem;
            margin-top: 1rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        /* Specific styling for the login page container with a DARK overlay */
        .login-container {
            padding: 2rem 3rem;
            background-color: rgba(10, 25, 10, 0.88); /* Dark Green semi-transparent */
            border-radius: 10px;
            text-align: center;
        }

        /* Headers - Changed to a lighter green for visibility */
        h1, h2, h3 {
            color: #4CAF50; /* Primary Green */
            font-family: 'Roboto', sans-serif;
            font-weight: 700;
        }

        /* General text - Changed to a light color for visibility */
        .stMarkdown, p, .st-emotion-cache-1c7y2kd {
            color: #F5F5F5; /* Off-white */
            font-family: 'Roboto', sans-serif;
        }
        
        /* Logo styling - MODIFIED BORDER RADIUS */
        .logo-container {
            text-align: center;
            padding-bottom: 20px;
        }
        .logo-img {
            width: 180px;
            height: auto;
            border-radius: 10px; /* Changed from 50% to 10px for a square look */
            border: 3px solid #4CAF50;
        }

        /* General Button Styling */
        .stButton > button {
            background-color: #4CAF50; /* Primary Green */
            color: white;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: bold;
            border: none;
            width: 100%; /* Make buttons full-width in their container */
            transition: background-color 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #45a049; /* Darker Green */
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        /* Input fields now have a dark background and light text */
        .stTextInput input, .stSelectbox > div > div {
            border: 2px solid #4CAF50;
            border-radius: 8px;
            background-color: rgba(255, 255, 255, 0.1); /* Subtle dark background */
            color: #FFFFFF !important; /* White text */
        }
        
        /* This targets the placeholder text specifically */
        .stTextInput input::placeholder {
            color: #B0B0B0 !important;
        }
        
        /* This targets the selectbox displayed value */
        .stSelectbox div[data-baseweb="select"] > div {
             color: #FFFFFF !important;
        }

        /* Add a focus effect to input fields for better UX */
        .stTextInput input:focus, .stSelectbox select:focus {
            border-color: #66bb6a; /* Lighter Green */
            box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
            outline: none;
        }
        
        /* Custom styling for the new navigation bar */
        div[data-testid="stHorizontalBlock"] {
            background-color: rgba(10, 25, 10, 0.95);
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 2rem;
        }
        
        /* CSS for the Eco Garden */
        .garden-container {
            position: relative;
            width: 100%;
            height: 400px; /* Provides space for plants to appear */
            margin: 20px auto; /* Center the container block */
        }
        .plant {
            position: absolute;
            bottom: 20px;
            transform: translateX(-50%);
            transition: all 0.5s ease;
            animation: grow 1s ease-out;
        }
        @keyframes grow {
            from { opacity: 0; transform: translateX(-50%) scale(0.5); }
            to { opacity: 1; transform: translateX(-50%) scale(1); }
        }

        </style>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    # Display logo at the top of the main page (but not on the login/signup page itself)
    if st.session_state.page not in ["Welcome", "Login", "Sign Up"]:
        st.markdown("""
            <div class="logo-container">
                <img class="logo-img" src="https://i.ibb.co/XfyN3cN3/ecomorphis.png" alt="Ecomorphis Logo">
            </div>
        """, unsafe_allow_html=True)

# -------------------------
# Session State Setup
# -------------------------
if "page" not in st.session_state:
    st.session_state.page = "Welcome"
if "active_page" not in st.session_state:
    st.session_state.active_page = "User Details"
if "users" not in st.session_state:
    st.session_state.users = {}
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Add progress trackers for gamified learning
if "citizen_progress" not in st.session_state:
    st.session_state.citizen_progress = {}
if "worker_progress" not in st.session_state:
    st.session_state.worker_progress = {}

# -------------------------
# Data Setup
# -------------------------
if "facilities" not in st.session_state:
    st.session_state.facilities = pd.DataFrame([
        {"Name": "City Compost Plant", "Type": "Compost", "Waste_Type": "Wet", "Latitude": 28.6139, "Longitude": 77.2090},
        {"Name": "Green Recycling Center", "Type": "Recycling", "Waste_Type": "Dry", "Latitude": 28.6200, "Longitude": 77.2100},
        {"Name": "Waste-to-Energy Plant", "Type": "W-to-E", "Waste_Type": "Mixed", "Latitude": 28.6250, "Longitude": 77.2150},
        {"Name": "Hazardous Waste Collection", "Type": "Scrap Shop", "Waste_Type": "Hazardous", "Latitude": 28.6300, "Longitude": 77.2200},
    ])

# Data for the new QR Bin feature
if "bins" not in st.session_state:
    st.session_state.bins = {
        "BIN-BH-001": {"location": "Kolar Road, Near SBI", "status": "Clean", "last_updated": None, "reported_by": None},
        "BIN-BH-002": {"location": "Arera Colony, Market Area", "status": "Clean", "last_updated": None, "reported_by": None},
        "BIN-BH-003": {"location": "MP Nagar, Zone 1", "status": "Overflowing", "last_updated": "2025-09-19 09:30:00", "reported_by": "citizen"}
    }

# -------------------------
# Navigation Callback Function
# -------------------------
def navigate():
    changed_selectbox_key = None
    if st.session_state.get("home_nav", "Home") != "Home":
        changed_selectbox_key = "home_nav"
    elif st.session_state.get("profile_nav", "Profile") != "Profile":
        changed_selectbox_key = "profile_nav"
    elif st.session_state.get("learning_nav", "Learning") != "Learning":
        changed_selectbox_key = "learning_nav"
    elif st.session_state.get("others_nav", "Others") != "Others":
        changed_selectbox_key = "others_nav"

    if changed_selectbox_key:
        st.session_state.active_page = st.session_state[changed_selectbox_key]
        st.session_state.home_nav = "Home"
        st.session_state.profile_nav = "Profile"
        st.session_state.learning_nav = "Learning"
        st.session_state.others_nav = "Others"

# -------------------------
# Welcome Page
# -------------------------
def welcome_page():
    set_custom_style()
    st.markdown("""
    <style>
    .welcome-container { padding: 2rem 1rem; text-align: center; }
    .welcome-container h1, .welcome-container h3, .welcome-container h4, .welcome-container p, .welcome-container li {
        color: #FFFFFF; text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.9);
    }
    .features-list { list-style-type: none; padding: 0; max-width: 600px; margin: 1rem auto; font-size: 1.1rem; }
    .features-list li { margin-bottom: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("<div class='welcome-container'>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size: 3.5rem;'>Welcome to Ecomorphis 🌿</h1>", unsafe_allow_html=True)
    st.markdown("<h3><i>A New Era in Waste Management for a Cleaner India</i></h3>", unsafe_allow_html=True)
    st.write("---")
    st.markdown("<p style='font-size: 1.2rem; max-width: 750px; margin: auto;'>Our mission is to build a complete digital system that ensures every citizen is trained, every waste worker is equipped, and every piece of waste is accounted for through community participation and strict monitoring.</p>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top: 2rem;'>Key Features of Our Platform</h4>", unsafe_allow_html=True)
    st.markdown("""
    <ul class='features-list'>
        <li>🎓 <strong>Citizen Training:</strong> Mandatory app-based modules on waste segregation and composting for all.</li>
        <li>🏆 <strong>Green Champions:</strong> A decentralized network of trained monitors to ensure protocols are followed.</li>
        <li>📸 <strong>Community Reporting:</strong> See waste? Snap a geo-tagged photo to report illegal dumping and earn rewards.</li>
        <li>💰 <strong>Incentives & Penalties:</strong> Earn Eco-Points for correct practices and face fines for non-compliance.</li>
        <li>🌐 <strong>Digital Hub:</strong> Easily locate recycling centers, request compost kits, and track waste collection.</li>
    </ul>
    """, unsafe_allow_html=True)
    _, btn_col, _ = st.columns([2.5, 1, 2.5])
    with btn_col:
        if st.button("Let's Get Started 🚀"):
            st.session_state.page = "Login"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------
# Login & Sign Up Pages
# -------------------------
def login_page():
    set_custom_style()
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""<div class="logo-container"><img class="logo-img" src="https://i.ibb.co/XfyN3cN3/ecomorphis.png" alt="Ecomorphis Logo"></div>""", unsafe_allow_html=True)
        with st.container():
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            st.header("Welcome Back! 🌿")
            st.write("Log in to continue your green journey.")
            username = st.text_input("👤 Username", key="login_username")
            password = st.text_input("🔒 Password", type="password", key="login_password")
            st.write("")
            _, login_col, signup_col, _ = st.columns([1.5, 2, 2, 1.5])
            with login_col:
                if st.button("Login"):
                    # Pre-populate dummy users for demo purposes
                    if 'citizen' not in st.session_state.users:
                        st.session_state.users['citizen'] = {"password": "123", "role": "Citizen", "points": 125, "last_green_snap": None}
                    if 'champion' not in st.session_state.users:
                        st.session_state.users['champion'] = {"password": "123", "role": "Green Champion", "points": 250, "last_green_snap": None}

                    if username in st.session_state.users and st.session_state.users[username]["password"] == password:
                        st.session_state.current_user = {"username": username, "role": st.session_state.users[username]["role"], "points": st.session_state.users[username]["points"]}
                        st.session_state.page = "App"
                        st.success("Login successful!")
                        st.rerun() 
                    else:
                        st.error("Invalid username or password")
            with signup_col:
                if st.button("Sign Up"):
                    st.session_state.page = "Sign Up"
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

def signup_page():
    set_custom_style()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("📝 Create Your Account")
        new_username = st.text_input("Choose a username")
        new_password = st.text_input("Choose a password", type="password")
        role = st.selectbox("Sign up as", ["Citizen", "Green Champion"])
        _, create_col, back_col, _ = st.columns([0.5, 2, 2, 0.5])
        with create_col:
            if st.button("Create Account"):
                if new_username in st.session_state.users:
                    st.error("Username already exists!")
                else:
                    st.session_state.users[new_username] = {"password": new_password, "role": role, "points": 0, "last_green_snap": None}
                    st.success("Account created successfully! Please login.")
                    st.session_state.page = "Login"
                    st.rerun()
        with back_col:
            if st.button("Back to Login"):
                st.session_state.page = "Login"
                st.rerun()

# -------------------------
# Placeholder & Content Pages
# -------------------------
def about_us_page():
    st.title("About Ecomorphis 🌱")
    st.markdown("---")
    st.markdown("### *Our mission is to revolutionize waste management in India by fostering a culture of responsibility, enabled by technology and driven by community action.*")
    st.markdown("---")

    st.subheader("The Challenge We Face")
    st.markdown("""
    India faces a monumental waste management crisis. With over **1.7 lakh tonnes** of municipal solid waste generated daily, **less than 54%** is properly treated. 
    The rest ends up in overflowing landfills or pollutes our environment, posing severe risks to public health and our ecosystems. 
    At Ecomorphis, we believe this is not just a civic problem, but a collective responsibility that requires a modern, systemic solution.
    """)

    st.subheader("Our Approach: A Four-Pillar Strategy")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🎓 Education & Empowerment
        We start at the source. Our platform provides **mandatory, accessible training modules** for every citizen, teaching effective waste segregation, home composting, and sustainable practices. An educated citizen is our first line of defense against waste mismanagement.
        """)
        st.markdown("""
        #### 🤝 Community & Accountability
        Change is a collective effort. We empower local **"Green Champions"** to monitor their areas and enable citizens to become the eyes and ears of the city. Our **"See Waste, Send Photo"** feature allows for geo-tagged reporting of illegal dumping, fostering a culture of accountability.
        """)
    
    with col2:
        st.markdown("""
        #### 💡 Technology & Transparency
        Ecomorphis is a **fully digital, transparent ecosystem**. From tracking waste collection vehicles to locating the nearest recycling facility or scrap shop, our app brings the entire waste management chain to your fingertips, eliminating leakages and inefficiencies.
        """)
        st.markdown("""
        #### 🏆 Incentivization & Gamification
        We believe in positive reinforcement. Our **Eco-Points system** rewards citizens for responsible behavior like timely reporting and proper segregation. This gamified approach, combined with a fair **penalization system**, encourages consistent participation and lasting behavioral change.
        """)

    st.subheader("Our Vision for Tomorrow")
    st.success("""
    We envision a future where every street is clean, every landfill is shrinking, and every citizen is an active participant in building a sustainable India. Ecomorphis is more than an app; it's a movement towards a cleaner, healthier, and more responsible tomorrow.
    """)
    
    st.markdown("---")
    st.markdown("#### Join us in transforming our nation, one piece of segregated waste at a time.")
    
def contact_us_page():
    st.title("Contact Us 📧")
    st.write("Have questions or feedback? Reach out to us!")
    st.write("Email: contact@ecomorphis.org")

def impact_page():
    st.title("🌍 Our Projected Impact")
    st.markdown("---")
    st.markdown("#### Transforming India's waste landscape through data-driven action and community engagement. Here's a look at the future we're building.")

    st.subheader("Key Performance Indicators (Projected - Year 1 in Bhopal)")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Citizen Engagement", value="50,000+ Active Users", delta="Rapid Adoption")
    col2.metric(label="Complaints Resolved", value="15,000+", delta="95% Resolution Rate")
    col3.metric(label="Waste Segregation Rate", value="75%", delta="21% Improvement from baseline")

    st.markdown("---")

    st.subheader("♻️ Environmental Impact")
    p1, p2 = st.columns(2)
    with p1:
        st.markdown("##### Landfill Diversion (Projected)")
        st.write("Our primary goal is to drastically reduce the burden on our city's landfills by improving segregation and processing.")
        st.info("Projected **60,000+ tonnes** of waste diverted from landfills annually.")
        
        st.markdown("##### Waste Treatment Efficiency")
        st.write("From a national average of 54% to a projected 75% in the first year of implementation.")
        st.progress(75)

    with p2:
        st.markdown("##### Reduction in CO2 Emissions")
        st.write("Recycling and composting significantly reduce greenhouse gas emissions compared to landfilling.")
        st.info("Equivalent to **~60,000 tonnes** of CO2 emissions saved annually.")
        
        st.markdown("##### Cleaner Public Spaces")
        st.write("Reduced illegal dumping through active community reporting and quick ULB response.")
        st.info("Targeting an **80% reduction** in open waste piles in monitored areas.")

    st.markdown("---")
    
    st.subheader("👥 Social & Community Impact")
    s1, s2 = st.columns(2)
    with s1:
        st.markdown("##### Mandatory Citizen Training")
        st.info("Over **100,000+** training modules completed, creating a more informed and responsible citizenry.")
    with s2:
        st.markdown("##### Empowered Green Champions")
        st.info("**500+** trained Green Champions actively monitoring and improving their local communities.")

    st.markdown("---")

    st.subheader("🌟 Featured Heroes & Testimonials")
    h1, h2 = st.columns(2)
    with h1:
        st.image("https://i.ibb.co/60snfSQ6/male-citizen.jpg", caption="Rohan S. - Citizen, Kolar Road", use_container_width=True)
        st.info(
            '"Using the Ecomorphis app has completely changed how my family handles waste. The learning modules were so easy. Reporting a garbage pile and seeing it get cleaned within a day was amazing! I feel like I\'m actually making a difference."'
        )
    with h2:
        st.image("https://i.ibb.co/Pv3KDLPJ/female-citizen.jpg", caption="Anjali P. - Green Champion, Arera Colony", use_container_width=True)
        st.info(
            '"As a Green Champion, the dashboard is my most powerful tool. I can see real-time data on complaints in my area and coordinate with ULB workers. The penalization system has already improved segregation compliance on my street. It\'s about accountability."'
        )

# -------------------------
# Core App Pages
# -------------------------
def profile_page():
    user = st.session_state.current_user
    # Refresh points from master user list
    st.session_state.current_user['points'] = st.session_state.users[user['username']]['points']
    st.title(f"👤 User Details: {user['username']}")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://www.svgrepo.com/show/384670/account-avatar-profile-user.svg", width=150)
        st.subheader(f"Role: {user['role']}")
        st.write("---")

    with col2:
        total_points = user['points']
        user_complaints_count = sum(1 for c in st.session_state.get('complaints', []) if c['user'] == user['username'])
        metric1, metric2 = st.columns(2)
        metric1.metric(label="♻️ Eco-Points", value=total_points)
        metric2.metric(label="📢 Complaints Submitted", value=user_complaints_count)
        
        st.write("---")
        st.subheader("Your Progress")
        ranks = {"Eco-Novice": (0, 50), "Green Starter": (51, 150), "Community Contributor": (151, 300), "Sustainability Steward": (301, 500), "Eco-Champion": (501, float('inf'))}
        current_rank, next_rank_points = "Eco-Novice", 50
        for rank, (min_pts, max_pts) in ranks.items():
            if min_pts <= total_points <= max_pts:
                current_rank, next_rank_points = rank, max_pts + 1
                break
        progress = total_points / next_rank_points if next_rank_points != float('inf') + 1 else 1.0
        st.write(f"**Current Rank:** {current_rank}")
        st.progress(progress)
        if progress < 1.0:
            st.write(f"{next_rank_points - total_points} points to the next rank!")
        else:
            st.success("You've reached the highest rank!")

def facilities_page():
    st.title("🏭 ULB Waste Facility Map")
    st.write("Explore nearby waste management facilities in your city.")
    df = st.session_state.facilities
    facility_types = df['Type'].unique().tolist()
    selected_type = st.multiselect("Select Facility Type:", facility_types, default=facility_types)
    waste_types = df['Waste_Type'].unique().tolist()
    selected_waste = st.multiselect("Select Waste Type:", waste_types, default=waste_types)
    filtered_df = df[df['Type'].isin(selected_type) & df['Waste_Type'].isin(selected_waste)]
    if filtered_df.empty:
        st.warning("No facilities match your selection.")
        return
    st.map(filtered_df.rename(columns={"Latitude": "lat", "Longitude": "lon"}))
    st.subheader("Facility Details")
    for _, row in filtered_df.iterrows():
        st.write(f"**{row['Name']}** | Type: {row['Type']} | Handles: {row['Waste_Type']}")

def complaint_page():
    st.title("📢 Report Community Waste Issue")
    if st.session_state.current_user["role"] != "Citizen":
        st.warning("⚠️ This feature is available for Citizens only.")
        return
    if "complaints" not in st.session_state: st.session_state.complaints = []
    tab1, tab2 = st.tabs([" 📝 Submit a New Report ", " 📜 Your Report History "])
    with tab1:
        st.subheader("📍 Submit a New Report")
        with st.form(key="complaint_form", clear_on_submit=True):
            location = st.text_input("Enter Location or Landmark")
            waste_type = st.selectbox("Type of Waste", ["Mixed Garbage", "Dry Waste", "Wet Waste", "Hazardous Waste"])
            photo = st.file_uploader("Upload Photo", type=["jpg", "png", "jpeg"])
            if st.form_submit_button(label="Submit Report"):
                if not all([location, waste_type, photo]):
                    st.error("Please fill all fields and upload a photo.")
                else:
                    st.session_state.complaints.append({"user": st.session_state.current_user["username"], "location": location, "waste_type": waste_type, "photo": photo, "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "status": "Pending", "verified_by": None})
                    st.success("✅ Report submitted successfully! A Green Champion will verify it shortly.")
    with tab2:
        st.subheader("📌 Your Submitted Reports")
        user_complaints = [c for c in st.session_state.complaints if c["user"] == st.session_state.current_user["username"]]
        if not user_complaints: st.info("You have not submitted any reports yet.")
        else:
            for c in reversed(user_complaints):
                with st.expander(f"📍 {c['location']}  |  🗓️ {c['timestamp'].split(' ')[0]}"):
                    st.image(c["photo"], use_container_width=True)
                    st.write(f"**Status:** {c['status']}")

def verify_reports_page():
    st.title("🛡️ Verify Citizen Reports")
    if st.session_state.current_user["role"] != "Green Champion":
        st.warning("⚠️ Only Green Champions can verify reports.")
        return

    st.info("Review new reports from citizens. Verify them to escalate for cleanup.")
    
    pending_reports = [report for report in st.session_state.get('complaints', []) if report['status'] == 'Pending']

    if not pending_reports:
        st.success("✅ No new reports pending verification. Great work!")
        return

    for i, report in enumerate(st.session_state.get('complaints', [])):
        if report['status'] == 'Pending':
            st.markdown("---")
            st.subheader(f"Report from: {report['user']} at {report['location']}")
            _, img_col, _ = st.columns([1,2,1])
            with img_col:
                st.image(report["photo"], use_container_width=True)
            
            b_col1, b_col2, _ = st.columns([1, 1, 3])
            with b_col1:
                if st.button("👍 Verify Report", key=f"verify_{i}"):
                    st.session_state.complaints[i]['status'] = 'Verified'
                    st.session_state.complaints[i]['verified_by'] = st.session_state.current_user['username']
                    st.session_state.users[st.session_state.current_user['username']]['points'] += 5
                    st.success("Report verified! You earned 5 points.")
                    st.rerun()
            with b_col2:
                if st.button("👎 Invalid Report", key=f"invalidate_{i}"):
                    st.session_state.complaints[i]['status'] = 'Invalid'
                    st.warning("Report marked as invalid.")
                    st.rerun()

def dashboard_page():
    st.title("📊 Dashboard - Operations Overview")
    if st.session_state.current_user["role"] != "Green Champion":
        st.warning("⚠️ Only Green Champions can view the dashboard.")
        return
    
    # Complaints Section
    st.subheader("📋 Community Reports Status")
    all_complaints = st.session_state.get('complaints', [])
    pending = [c for c in all_complaints if c['status'] == 'Pending']
    verified = [c for c in all_complaints if c['status'] == 'Verified']
    resolved = [c for c in all_complaints if c['status'] == 'Resolved']
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Pending Verification", len(pending))
    col2.metric("Pending Resolution", len(verified))
    col3.metric("Total Resolved", len(resolved))
    
    st.write("---")
    st.subheader("Verified Reports Pending Resolution")
    verified_reports = [c for c in all_complaints if c['status'] == 'Verified']
    if not verified_reports:
        st.info("No verified reports are awaiting resolution.")
    else:
        for i, c in enumerate(all_complaints):
            if c['status'] == 'Verified':
                with st.expander(f"📍 {c['location']} - Verified by {c['verified_by']}"):
                    st.image(c["photo"], use_container_width=True)
                    st.write(f"Originally reported by: {c['user']}")
                    if st.button("✅ Mark as Resolved", key=f"resolve_{i}"):
                        st.session_state.complaints[i]["status"] = "Resolved"
                        # Reward the original reporter and the resolver
                        st.session_state.users[c["user"]]["points"] += 10
                        st.session_state.users[st.session_state.current_user["username"]]["points"] += 5
                        st.success(f"Report resolved! 10 points to {c['user']}, 5 points to you.")
                        st.rerun()

    st.markdown("---") 

    # Overflowing Bins Section
    st.subheader("🗑️ Overflowing Bins Report")
    overflowing_bins = {bin_id: details for bin_id, details in st.session_state.bins.items() if details['status'] == 'Overflowing'}
    
    if not overflowing_bins:
        st.info("✅ All bins are currently clean.")
    else:
        st.warning(f"Action needed! There are {len(overflowing_bins)} overflowing bins reported.")
        for bin_id, details in overflowing_bins.items():
            with st.container(border=True): 
                st.markdown(f"**Bin ID:** `{bin_id}`")
                st.markdown(f"**Location:** {details['location']}")
                st.markdown(f"**Reported by:** {details['reported_by']} on {details['last_updated']}")
                if st.button("Mark as Cleaned", key=f"clean_{bin_id}"):
                    st.session_state.bins[bin_id]['status'] = 'Clean'
                    st.success(f"Bin {bin_id} marked as cleaned.")
                    st.rerun()


def penalization_page():
    st.title("⚖️ Penalization - Report Littering")
    if st.session_state.current_user["role"] != "Green Champion":
        st.warning("⚠️ Only Green Champions can access this page.")
        return
    citizen_name = st.text_input("Enter Citizen Username")
    if st.button("Impose Fine"):
        if citizen_name not in st.session_state.users:
            st.error("Citizen not found!")
        else:
            st.success(f"✅ Fine imposed on {citizen_name}.")
            st.session_state.users[citizen_name]["points"] = max(0, st.session_state.users[citizen_name]["points"] - 10)

# -------------------------
# ADVANCED Scan Bin Page with QR Generation & Scanning
# -------------------------
def decode_qr_from_image(image_file):
    """Reads an uploaded image file and decodes the first QR code found using OpenCV."""
    try:
        # Convert the uploaded file to an OpenCV image
        file_bytes = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Initialize the QRCode detector
        detector = cv2.QRCodeDetector()

        # Detect and decode the QR code
        data, bbox, straight_qrcode = detector.detectAndDecode(img)

        # If a QR code is found, data will not be empty
        if data:
            return data
        return None
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return None

def scan_bin_page():
    st.title("♻️ Scan Bin QR Code")
    st.write("Upload a QR code image to report an overflowing bin or mark it as cleaned.")
    st.markdown("---")

    # Section to generate and display sample QR codes for testing
    with st.expander("Show Sample QR Codes for Testing"):
        st.write("Right-click and save these images to your device to test the upload feature.")
        qr_cols = st.columns(len(st.session_state.bins))
        for i, bin_id in enumerate(st.session_state.bins.keys()):
            with qr_cols[i]:
                qr_img = qrcode.make(bin_id)
                buf = io.BytesIO()
                qr_img.save(buf, format='PNG')
                st.image(buf.getvalue(), caption=bin_id, width=150)

    st.markdown("---")

    # File uploader for the QR code
    qr_image = st.file_uploader("Upload QR Code Image", type=['png', 'jpg', 'jpeg'], key="qr_uploader")

    # This session state variable will hold the scanned bin ID
    if 'scanned_bin_id' not in st.session_state:
        st.session_state.scanned_bin_id = None

    # If an image is uploaded, try to decode it
    if qr_image:
        scanned_id = decode_qr_from_image(qr_image)
        if scanned_id and scanned_id in st.session_state.bins:
            st.session_state.scanned_bin_id = scanned_id
            st.success(f"Successfully scanned Bin ID: **{scanned_id}**")
        else:
            st.session_state.scanned_bin_id = None
            st.error("Could not find a valid Bin QR code in the uploaded image. Please try again.")

    # Display bin details and actions only if a valid bin has been scanned
    selected_bin_id = st.session_state.scanned_bin_id
    if selected_bin_id:
        st.markdown("---")
        bin_details = st.session_state.bins[selected_bin_id]
        st.subheader(f"Bin Details: {selected_bin_id}")
        st.write(f"**Location:** {bin_details['location']}")
        
        status_color = "red" if bin_details['status'] == 'Overflowing' else "green"
        st.markdown(f"**Current Status:** <span style='color:{status_color}; font-weight:bold;'>{bin_details['status']}</span>", unsafe_allow_html=True)

        if bin_details['status'] == 'Overflowing':
            st.write(f"**Reported by:** {bin_details['reported_by']} at {bin_details['last_updated']}")

        user_role = st.session_state.current_user['role']

        if user_role == "Citizen":
            if st.button("Report as Overflowing", disabled=(bin_details['status'] == 'Overflowing')):
                st.session_state.bins[selected_bin_id]['status'] = 'Overflowing'
                st.session_state.bins[selected_bin_id]['reported_by'] = st.session_state.current_user['username']
                st.session_state.bins[selected_bin_id]['last_updated'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.success(f"Bin {selected_bin_id} has been reported as overflowing. Our team has been notified.")
                st.session_state.users[st.session_state.current_user['username']]['points'] += 5
                # Reset after action
                st.session_state.scanned_bin_id = None
                st.rerun()
        
        elif user_role == "Green Champion":
            if st.button("Mark as Cleaned", disabled=(bin_details['status'] == 'Clean')):
                st.session_state.bins[selected_bin_id]['status'] = 'Clean'
                st.success(f"Thank you! Bin {selected_bin_id} has been marked as cleaned.")
                # Reset after action
                st.session_state.scanned_bin_id = None
                st.rerun()
        else:
            st.warning("This feature is available for Citizens and Green Champions.")
    else:
        st.info("Upload an image containing a Bin QR code to see details and perform actions.")


def shop_page():
    st.title("🛒 Eco-Rewards Shop")
    st.info("Redeem your hard-earned Eco-Points for amazing nature-friendly products!")
    
    username = st.session_state.current_user["username"]
    current_points = st.session_state.users[username]["points"]

    st.subheader(f"Your Balance: {current_points} ♻️ Points")
    st.markdown("---")

    # Define the product catalog
    products = {
        "prod1": {"name": "Set of 3 Bamboo Toothbrushes", "cost": 50, "img": "https://i.ibb.co/5Z0TBsv/bamboo-toothbrush.jpg", "desc": "Biodegradable and eco-friendly alternative to plastic brushes."},
        "prod2": {"name": "Reusable Canvas Shopping Bag", "cost": 100, "img": "https://i.ibb.co/8LYhmFVb/shoping-bag.jpg", "desc": "A sturdy and stylish bag to eliminate single-use plastics."},
        "prod3": {"name": "Home Composting Starter Kit", "cost": 200, "img": "https://i.ibb.co/fdHjr5Vt/starter-kit.jpg", "desc": "Everything you need to start turning your kitchen scraps into black gold."},
        "prod4": {"name": "Recycled Paper Notebooks (Pack of 5)", "cost": 75, "img": "https://i.ibb.co/PZCkQQft/paper-book.jpg", "desc": "Jot down your thoughts on paper that saves trees."}
    }

    # Display products in columns
    col1, col2 = st.columns(2)
    
    # A simple way to alternate products between columns
    i = 0
    for key, product in products.items():
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            st.subheader(product["name"])
            st.image(product["img"], use_container_width=True)
            st.write(product["desc"])
            st.success(f"**Cost: {product['cost']} Points**")
            
            # Disable button if user can't afford the item
            can_afford = current_points >= product['cost']
            if st.button(f"Redeem Now", key=key, disabled=not can_afford):
                # Deduct points and show success message
                st.session_state.users[username]["points"] -= product['cost']
                st.success(f"You have successfully redeemed the {product['name']}!")
                st.balloons()
                st.rerun() # Rerun to update the points balance immediately
            
            if not can_afford:
                st.warning(f"You need {product['cost'] - current_points} more points for this item.")
            
            st.markdown("---")
        i += 1

def achievements_page():
    st.title("🏆 Achievements & Leaderboard")
    if not st.session_state.users:
        st.info("No users yet.")
        return
    citizens = {u:d["points"] for u,d in st.session_state.users.items() if d["role"]=="Citizen"}
    champions = {u:d["points"] for u,d in st.session_state.users.items() if d["role"]=="Green Champion"}
    st.subheader("👥 Top Citizens")
    if citizens:
        for r, (u, p) in enumerate(sorted(citizens.items(), key=lambda x: x[1], reverse=True), 1):
            st.write(f"🏅 {r}. **{u}** - {p} points")
    else: st.write("No Citizens yet.")
    st.subheader("💚 Top Green Champions")
    if champions:
        for r, (u, p) in enumerate(sorted(champions.items(), key=lambda x: x[1], reverse=True), 1):
            st.write(f"🌟 {r}. **{u}** - {p} points")
    else: st.write("No Green Champions yet.")

# -------------------------
# NEW Eco Garden Page
# -------------------------
def eco_garden_page():
    st.title("🌳 Your Eco Garden")
    st.markdown("---")
    st.info("Earn points by performing daily green acts and watch your garden grow!")

    username = st.session_state.current_user["username"]
    user_data = st.session_state.users[username]

    # --- Daily Green Snap Section ---
    st.subheader("📸 Daily Green Snap")
    
    today = datetime.date.today().isoformat()
    last_snap = user_data.get("last_green_snap")

    if last_snap == today:
        st.success("You've already earned your point for today! Come back tomorrow.")
    else:
        st.write("Upload a photo of your eco-friendly action for today (e.g., using a compost bin, correct waste segregation) to earn **1 Eco-Point**.")
        uploaded_photo = st.file_uploader("Upload your green snap!", type=['jpg', 'png', 'jpeg'])
        if uploaded_photo is not None:
            st.session_state.users[username]["points"] += 1
            st.session_state.users[username]["last_green_snap"] = today
            st.success("Great job! You've earned 1 Eco-Point. Your garden is growing!")
            st.balloons()
            st.rerun()
            
    st.markdown("---")

    # --- Garden Visualization Section ---
    st.subheader("Your Digital Forest")
    
    total_points = user_data["points"]
    grown_trees = total_points // 10
    current_plant_points = total_points % 10

    # MODIFICATION: Define plant stages with corresponding images and sizes
    plant_stages = {
        (0, 1): {"img": "https://i.ibb.co/ymHhwt9J/seed.png", "size": 450},      # Seed
        (2, 4): {"img": "https://i.ibb.co/2YWwHdn4/sapling.png", "size": 450},    # Sprout
        (5, 7): {"img": "https://i.ibb.co/fYVxH58p/sapling-2.png", "size": 450},   # Sapling
        (8, 9): {"img": "https://i.ibb.co/sJJLgRVd/small-tree.png", "size": 450}# Small Tree
    }
    full_tree_img = "https://i.ibb.co/VYQWY4G8/full-tree.png" # Full Tree

    # Display the garden
    garden_html = "<div class='garden-container'>"
    
    if grown_trees == 0 and current_plant_points == 0:
        garden_html += "<p style='color: white; text-align: center; padding-top: 100px;'>Your garden is bare. Earn your first point to plant a seed!</p>"
    else:
        plant_elements_html = ""
        random.seed(username) 
        for i in range(grown_trees):
            left = random.randint(5, 95)
            size = random.randint(90, 130) # Adjusted full tree size slightly
            plant_elements_html += f'<img src="{full_tree_img}" alt="Tree" class="plant" style="left:{left}%; height:{size}px;">'

        # MODIFICATION: Determine the stage and size of the current plant
        current_plant_img = ""
        current_plant_size = 0
        for point_range, stage_details in plant_stages.items():
            if point_range[0] <= current_plant_points <= point_range[1]:
                current_plant_img = stage_details["img"]
                current_plant_size = stage_details["size"]
                break
        
        if current_plant_img:
            left = random.randint(10, 90)
            # MODIFICATION: Apply the dynamic size to the growing plant
            plant_elements_html += f'<img src="{current_plant_img}" alt="Growing Plant" class="plant" style="left:{left}%; height:{current_plant_size}px;">'
        
        garden_html += plant_elements_html
    
    garden_html += "</div>"

    st.markdown(garden_html, unsafe_allow_html=True)
    
    # Progress towards the next tree
    st.subheader("Next Tree Progress")
    if grown_trees < 100: # Some arbitrary limit
        st.progress(current_plant_points / 10)
        st.write(f"You have **{grown_trees}** mature trees in your garden.")
        st.write(f"Your current plant needs **{10 - current_plant_points}** more points to become a full tree!")


# -------------------------
# REBUILT Learning Pages
# -------------------------
def waste_worker_training_page():
    st.title("🛠️ Waste Worker Training")
    st.info("Essential training for our on-ground heroes. Complete modules to earn points and badges!")

    username = st.session_state.current_user["username"]
    # Initialize progress for the user if not already present
    if username not in st.session_state.worker_progress:
        st.session_state.worker_progress[username] = {"m1": False, "m2": False, "quiz": False}

    progress = st.session_state.worker_progress[username]

    m1_completed = progress["m1"]
    m2_completed = progress["m2"]
    quiz_completed = progress["quiz"]

    tab1, tab2, tab3 = st.tabs(["Module 1: Safety First (PPE)", "Module 2: Handling Hazardous Waste", "Safety Quiz"])

    with tab1:
        st.subheader("Module 1: Personal Protective Equipment (PPE)")
        st.write("Your safety is our priority. Always use the correct PPE on the job.")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.image("https://i.ibb.co/chDp7M5J/gloves.jpg", caption="Heavy-Duty Gloves", use_container_width=True)
        with col2:
            st.image("https://i.ibb.co/fV8rLbnh/n95.jpg", caption="N95 Masks", use_container_width=True)
        with col3:
            st.image("https://i.ibb.co/DfRf9R4f/shoe.jpg", caption="Steel-Toed Boots", use_container_width=True)
        
        if m1_completed:
            st.success("Module 1 Completed! You earned 15 points.")
        else:
            if st.button("Mark Module 1 as Complete"):
                st.session_state.users[username]["points"] += 15
                st.session_state.worker_progress[username]["m1"] = True
                st.success("Great job! 15 points awarded.")
                st.balloons()
                st.rerun()

    with tab2:
        st.subheader("Module 2: Identifying & Handling Hazardous Waste")
        st.warning("Never handle these items with bare hands. Follow special disposal protocols.")
        st.markdown("""
        - **Batteries & E-Waste:** Contain heavy metals.
        - **Medical Waste:** Syringes, bandages can be infectious.
        - **Chemicals & Paint Cans:** Can be corrosive or flammable.
        """)
        if m2_completed:
            st.success("Module 2 Completed! You earned 15 points.")
        else:
            if st.button("Mark Module 2 as Complete"):
                st.session_state.users[username]["points"] += 15
                st.session_state.worker_progress[username]["m2"] = True
                st.success("Excellent work! 15 points awarded.")
                st.balloons()
                st.rerun()

    with tab3:
        st.subheader("Final Safety Quiz")
        if not (m1_completed and m2_completed):
            st.warning("Please complete Module 1 and Module 2 to unlock the quiz.")
        elif quiz_completed:
            st.success("You have already completed the quiz! Well done.")
        else:
            st.write("Test your knowledge to earn bonus points!")
            with st.form("worker_quiz"):
                q1 = st.radio("What should you wear when handling sharp objects?", ["Cotton Gloves", "Heavy-Duty Gloves", "No Gloves"])
                q2 = st.radio("Which item is considered hazardous waste?", ["Apple Core", "Used Batteries", "Plastic Bottle"])
                
                submitted = st.form_submit_button("Submit Quiz")
                if submitted:
                    score = 0
                    if q1 == "Heavy-Duty Gloves": score += 1
                    if q2 == "Used Batteries": score += 1
                    
                    points_earned = score * 10
                    st.session_state.users[username]["points"] += points_earned
                    st.session_state.worker_progress[username]["quiz"] = True

                    st.success(f"Quiz submitted! You scored {score}/2 and earned {points_earned} points!")
                    st.balloons()
                    st.rerun()

def learning_page():
    st.title("📚 Citizen Learning Hub")
    st.info("Become a Waste Wise Citizen! Complete modules to earn points and make a difference.")

    username = st.session_state.current_user["username"]
    # Initialize progress for the user if not already present
    if username not in st.session_state.citizen_progress:
        st.session_state.citizen_progress[username] = {"m1": False, "m2": False, "quiz": False}

    progress = st.session_state.citizen_progress[username]

    m1_completed = progress["m1"]
    m2_completed = progress["m2"]
    quiz_completed = progress["quiz"]

    tab1, tab2, tab3 = st.tabs(["Module 1: The Three Bins ♻️", "Module 2: Home Composting 🌱", "Final Quiz 🧠"])

    with tab1:
        st.subheader("Mastering Waste Segregation")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.success("#### 🟢 Green Bin\nFor Wet/Organic Waste like vegetable peels, leftover food, and garden waste.")
        with col2:
            st.info("#### 🔵 Blue Bin\nFor Dry/Recyclable Waste like paper, plastic bottles, and metal cans.")
        with col3:
            st.error("#### 🔴 Red Bin\nFor Domestic Hazardous Waste like batteries, e-waste, and expired medicines.")

        if m1_completed:
            st.success("Module 1 Completed! You earned 10 points.")
        else:
            if st.button("I understand the Three Bins!"):
                st.session_state.users[username]["points"] += 10
                st.session_state.citizen_progress[username]["m1"] = True
                st.success("Awesome! 10 points have been added to your account.")
                st.balloons()
                st.rerun()

    with tab2:
        st.subheader("Turn Your Waste into Wealth!")
        st.write("Home composting is an easy way to reduce landfill waste and create nutrient-rich soil for your plants.")
        _, img_col, _ = st.columns([1, 2, 1])
        with img_col:
            st.image("https://i.ibb.co/DgCsyjSJ/home-composting.jpg", caption="A simple mix of 'Greens' (kitchen scraps) and 'Browns' (dry leaves, cardboard)", use_container_width=True)
        
        if m2_completed:
            st.success("Module 2 Completed! You earned 10 points.")
        else:
            if st.button("I'm ready to compost!"):
                st.session_state.users[username]["points"] += 10
                st.session_state.citizen_progress[username]["m2"] = True
                st.success("Fantastic! 10 points awarded.")
                st.balloons()
                st.rerun()

    with tab3:
        st.subheader("Test Your Green Knowledge!")
        if not (m1_completed and m2_completed):
            st.warning("Please complete Module 1 and Module 2 to unlock the quiz.")
        elif quiz_completed:
            st.success("You have already aced the quiz! Great job.")
        else:
            st.write("Answer correctly to earn bonus points!")
            with st.form("citizen_quiz"):
                q1 = st.radio("Which bin does a plastic milk packet go into?", ["🟢 Green", "🔵 Blue", "🔴 Red"])
                q2 = st.radio("What is a key ingredient for good compost?", ["Plastic wrappers", "Dry leaves", "Glass bottles"])
                
                submitted = st.form_submit_button("Submit Quiz")
                if submitted:
                    score = 0
                    if q1 == "🔵 Blue": score += 1
                    if q2 == "Dry leaves": score += 1
                    
                    points_earned = score * 5
                    st.session_state.users[username]["points"] += points_earned
                    st.session_state.citizen_progress[username]["quiz"] = True

                    st.success(f"Quiz submitted! You scored {score}/2 and earned {points_earned} points!")
                    st.balloons()
                    st.rerun()

# -------------------------
# Main App Flow
# -------------------------
if st.session_state.page == "Welcome":
    welcome_page()
elif st.session_state.page == "Login":
    login_page()
elif st.session_state.page == "Sign Up":
    signup_page()
elif st.session_state.page == "App":
    set_custom_style()

    home_col, profile_col, learning_col, others_col, _, logout_col = st.columns([1.5, 1.5, 1.5, 1.5, 3, 1])

    with home_col:
        st.selectbox("Home", ["Home", "About Us", "Impact", "Contact Us"], key="home_nav", on_change=navigate)
    with profile_col:
        st.selectbox("Profile", ["Profile", "User Details", "Achievements", "Eco Garden"], key="profile_nav", on_change=navigate)
    with learning_col:
        st.selectbox("Learning", ["Learning", "Citizen Learning", "Waste Worker Training"], key="learning_nav", on_change=navigate)
    with others_col:
        st.selectbox("Others", ["Others", "Report Waste", "Verify Reports", "Dashboard", "Shop", "Facilities", "Penalization", "Scan Bin"], key="others_nav", on_change=navigate)
    with logout_col:
        if st.button("Logout 🚪"):
            st.session_state.current_user = None
            st.session_state.page = "Login"
            st.session_state.active_page = "User Details"
            st.rerun()
    
    page_to_load = st.session_state.active_page
    
    page_map = {
        "About Us": about_us_page, 
        "Impact": impact_page, 
        "Contact Us": contact_us_page,
        "User Details": profile_page, 
        "Achievements": achievements_page, 
        "Eco Garden": eco_garden_page,
        "Citizen Learning": learning_page, 
        "Waste Worker Training": waste_worker_training_page,
        "Report Waste": complaint_page, 
        "Verify Reports": verify_reports_page, 
        "Dashboard": dashboard_page, 
        "Shop": shop_page,
        "Facilities": facilities_page, 
        "Penalization": penalization_page, 
        "Scan Bin": scan_bin_page
    }
    
    page_function = page_map.get(page_to_load, profile_page)
    page_function()

