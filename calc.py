import streamlit as st
import numpy as np
import pandas as pd

# Mock Database (dictionary) for Users and Shares
user_database = {
    "user1@example.com": {"share_percentage": 0.1, "initial_investment": 100000},
    "user2@example.com": {"share_percentage": 0.2, "initial_investment": 200000},
    "user3@example.com": {"share_percentage": 0.05, "initial_investment": 50000},
}

# Backend calculations for credit simulation
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
        columns = ["Time Period", "Company Credits", "User's Share Credits"]
        return pd.DataFrame(list(self.credit_data), columns=columns)

# Streamlit App with Multi-Page Setup
st.sidebar.title("Solar Investment Platform")
page = st.sidebar.selectbox("Select Page", ["Investment Calculator", "Company Statistics"])

if page == "Investment Calculator":
    st.title("Solar Project Share Calculator")

    # Input Fields
    user_share = st.slider("Enter your share in the company (%):", 0.0, 100.0, 10.0) / 100
    initial_credits = st.number_input("Initial Credits (e.g., 1,000,000):", value=1000000)
    manufacturing_duration = st.number_input("Manufacturing Duration (in months):", value=6)
    growth_rate = st.slider("Monthly Growth Rate After Manufacturing (%)", 0.0, 10.0, 2.0) / 100

    # Calculate Credits
    calculator = CreditCalculator(user_share, initial_credits, manufacturing_duration, growth_rate)
    calculator.calculate_manufacturing_loss()
    calculator.calculate_growth_after_manufacturing()

    # Display Results
    credit_data = calculator.get_data()
    st.write("### Credit Projection Table")
    st.dataframe(credit_data)

    st.write("### Credit Projection Chart")
    st.line_chart(credit_data.set_index("Time Period")[["Company Credits", "User's Share Credits"]])

elif page == "Company Statistics":
    st.title("Company Statistics and User Shares")

    # Overall Company Statistics
    total_credits = 5000000  # Example of total initial company credits
    st.write(f"**Total Company Credits Available:** {total_credits}")

    # User Share Check
    st.write("### Check Your Share")
    user_email = st.text_input("Enter your email to check your share:")

    if user_email in user_database:
        user_data = user_database[user_email]
        user_share_percentage = user_data["share_percentage"] * 100
        user_investment = user_data["initial_investment"]
        st.write(f"**User Email:** {user_email}")
        st.write(f"**Share Percentage:** {user_share_percentage}%")
        st.write(f"**Initial Investment:** ${user_investment}")
    else:
        st.write("User not found. Please check your email or register with the platform.")