import streamlit as st
import sqlite3
import base64
import json
from streamlit_lottie import st_lottie
import pandas as pd
import matplotlib.pyplot as plt

# Load Lottie animation
def load_lottie_file(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

lottie_animation = load_lottie_file("C:/Users/chvai/Desktop/usar final project/Animation - 1729896198439.json")

# Database connection
conn = sqlite3.connect('green_invest.db')
cursor = conn.cursor()

# Create users table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    invested_amount REAL DEFAULT 0,
    energy_produced REAL DEFAULT 0,
    co_saved REAL DEFAULT 0
)
''')

# Commit changes and close the connection
conn.commit()

# User functions
def create_user(username, password):
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def check_credentials(username, password):
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    return cursor.fetchone()

# Streamlit app layout
st.set_page_config(page_title="Green Invest", layout="wide")

# CSS for styling
st.markdown("""
    <style>
    .logo-container {
        text-align: center;  
        margin: 100px;       
    }
    .logo {
        width: 350px;        
        height: auto;        
    }
    .main-title {
        text-align: center;
        font-size: 36px;
        color: #4CAF50; /* Green color */
    }
    </style>
""", unsafe_allow_html=True)

# Display the logo
st.markdown('<div class="logo-container"><img class="logo" src="data:login.jpg;base64,{}" alt="Logo"></div>'.format(
    base64.b64encode(open('login.jpg', 'rb').read()).decode()
), unsafe_allow_html=True)

# Login or Signup Form Selection
auth_mode = st.sidebar.selectbox("Select Mode", ["Login", "Sign Up"])

# Sign Up Form
if auth_mode == "Sign Up" and "logged_in" not in st.session_state:
    st.markdown("<h1 class='main-title'>Sign Up for Green Invest</h1>", unsafe_allow_html=True)
    with st.form("signup_form"):
        st.write("Create a new account.")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        signup_button = st.form_submit_button("Sign Up")

    if signup_button:
        if create_user(new_username, new_password):
            st.success("Account created successfully! Please log in.")
        else:
            st.error("Username already exists. Please choose a different one.")

# Login Form
elif auth_mode == "Login" and "logged_in" not in st.session_state:
    st.markdown("<h1 class='main-title'>Login to Green Invest</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        st.write("Please enter your login details.")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

    # Verify login
    if login_button:
        user = check_credentials(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user[0]  # Store user ID for session
            st.success("Login successful!")
            st.experimental_set_query_params()  # Reload the app to show the main content
        else:
            st.error("Invalid username or password.")

# Main Content after Login
if "logged_in" in st.session_state and st.session_state.logged_in:
    st.markdown("<h1 class='main-title'>Green Invest</h1>", unsafe_allow_html=True)

    # Sidebar Navigation
    page = st.sidebar.selectbox("Navigation", ["Explore Investment Opportunities", "Chatbot", "User Profile", "Logout"])

    # Sample dummy companies data
    dummy_companies = [
        {
            "name": "SolarTech Innovations",
            "description": "Leading the way in solar technology and sustainable energy solutions.",
            "target_funding": 1000000,
            "energy_output": 50000,
            "image": "company1.jpg"
        },
        {
            "name": "Green Energy Solutions",
            "description": "Committed to providing renewable energy solutions for a sustainable future.",
            "target_funding": 500000,
            "energy_output": 30000,
            "image": "company2.jpg"
        },
        {
            "name": "EcoPower Inc.",
            "description": "Harnessing the power of the sun to provide clean energy.",
            "target_funding": 750000,
            "energy_output": 45000,
            "image": "company3.jpg"
        },
    ]

    # Page 1: Explore Investment Opportunities
    if page == "Explore Investment Opportunities":
        st.header("Explore Investment Opportunities")
        st.write("Browse available solar energy projects to make sustainable investments.")

        for company in dummy_companies:
            st.write(f"### {company['name']}")  # Company Name
            st.write(f"{company['description']}")  # Description
            st.write(f"**Target Funding:** ${company['target_funding']:,.2f}")
            st.write(f"**Energy Output:** {company['energy_output']:,.2f} kWh")
            
            # Invest button
            if st.button(f"Invest in {company['name']}"):
                st.write(f"### Investment Details for {company['name']}")
                st.write(f"**Description:** {company['description']}")
                st.write(f"**Target Funding:** ${company['target_funding']:,.2f}")
                st.write(f"**Energy Output:** {company['energy_output']:,.2f} kWh")
                st.write("Thank you for your interest in investing!")
            st.markdown("---")

        if lottie_animation:
            st_lottie(lottie_animation, speed=1, height=50, width=300, key="animation")

    # Page 3: User Profile
    elif page == "User Profile":
        st.header("User Profile")
        st.write("View your investment summary and environmental impact.")

        # Fetch user profile data
        def get_user_profile(user_id):
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return cursor.fetchone()

        user_profile = get_user_profile(st.session_state.user_id)

        # Display user profile information
        if user_profile:
            profile_data = {
                "Attribute": ["Username", "Invested Amount", "Energy Produced", "CO₂ Saved"],
                "Value": [
                    user_profile[1],  # Username
                    f"${user_profile[3]:,.2f}",  # Invested Amount
                    f"{user_profile[4]:,.2f} kWh",  # Energy Produced
                    f"{user_profile[5]:,.2f} tons"  # CO₂ Saved
                ]
            }

            profile_df = pd.DataFrame(profile_data)

            st.table(profile_df.style.set_table_attributes('style="margin: 0 auto; border-collapse: separate; border-spacing: 0 15px;"'))
            
            # Investment Calculator
            st.subheader("Solar Project Share Calculator")
            user_share = st.slider("Enter your share in the company (%):", 0.0, 100.0, 10.0) / 100
            initial_credits = st.number_input("Initial Credits (e.g., 1,000,000):", value=1000000)
            manufacturing_duration = st.number_input("Manufacturing Duration (in months):", value=6)
            growth_rate = st.slider("Monthly Growth Rate After Manufacturing (%)", 0.0, 10.0, 2.0) / 100

            # Calculate Credits
            class CreditCalculator:
                def __init__(self, user_share, initial_credits, manufacturing_duration, growth_rate):
                    self.user_share = user_share
                    self.initial_credits = initial_credits
                    self.manufacturing_duration = manufacturing_duration
                    self.growth_rate = growth_rate
                    self.credit_data = []

                def calculate_manufacturing_loss(self):
                    decline_rate = 0.05  # 5% monthly loss in credits during manufacturing
                    credits = self.initial_credits
                    for month in range(self.manufacturing_duration):
                        credits -= credits * decline_rate
                        self.credit_data.append((f'Month {month+1}', credits, credits * self.user_share))

                def calculate_growth_after_manufacturing(self):
                    credits = self.credit_data[-1][1]
                    for month in range(12):
                        credits += credits * self.growth_rate
                        self.credit_data.append((f'Month {self.manufacturing_duration + month + 1}', credits, credits * self.user_share))

                def get_data(self):
                    return pd.DataFrame(self.credit_data, columns=["Time Period", "Company Credits", "User's Share Credits"])

            calculator = CreditCalculator(user_share, initial_credits, manufacturing_duration, growth_rate)
            calculator.calculate_manufacturing_loss()
            calculator.calculate_growth_after_manufacturing()
            credits_df = calculator.get_data()

            # Plotting
            plt.figure(figsize=(10, 5))
            plt.plot(credits_df["Time Period"], credits_df["User's Share Credits"], marker='o')
            plt.title("Projected Credits Over Time")
            plt.xlabel("Time Period")
            plt.ylabel("User's Share Credits")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(plt)

            st.dataframe(credits_df.style.set_table_attributes('style="margin: 0 auto; border-collapse: separate; border-spacing: 0 15px;"'))

    # Logout
    elif page == "Logout":
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.success("You have logged out successfully. Please log in again.")

# Close the database connection when the app ends
conn.close()
