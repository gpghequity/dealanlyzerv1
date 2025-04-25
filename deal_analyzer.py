import streamlit as st
import openai
import os
import matplotlib.pyplot as plt

# 🔒 Set your OpenAI API key via environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="📈 Real Estate Analyzer Deluxe", layout="centered")

st.title("🏠 AI-Powered Real Estate Analyzer")
st.caption("Now 63% sassier than your real estate agent.")

# -------------------- Inputs -------------------- #
st.subheader("🔢 Property Inputs")
address = st.text_input("Property Address")
purchase_price = st.number_input("Purchase Price ($)", min_value=0)
monthly_rent = st.number_input("Expected Monthly Rent Income ($)", min_value=0)
monthly_expenses = st.number_input("Monthly Fixed Expenses (Insurance, Taxes, etc.) ($)", min_value=0)
mortgage_payment = st.number_input("Monthly Mortgage Payment ($)", min_value=0)

st.subheader("🎯 Your Investment Goals")
desired_cap_rate = st.number_input("Target Cap Rate (%)", min_value=0.0, step=0.1)
desired_dscr = st.number_input("Target DSCR (Debt Service Coverage Ratio)", min_value=0.0, step=0.1)

st.subheader("🔧 Rental Expense Buffers")
vacancy_rate = st.slider("Vacancy Reserve (%)", 0, 20, 5)
maintenance_rate = st.slider("Maintenance Reserve (%)", 0, 20, 5)
management_rate = st.slider("Property Management Fee (%)", 0, 20, 8)

st.subheader("🎭 AI Analysis Style")
tone = st.radio("Choose Your AI Tone", ["Snarky", "Professional", "Motivational"], index=0)

tone_prompts = {
    "Snarky": "You're a sarcastic, seasoned real estate investor who gives brutally honest deal analysis with humor. Be snarky but insightful.",
    "Professional": "You are a professional real estate analyst. Provide an objective, data-driven assessment of this deal.",
    "Motivational": "You're a positive mentor. Analyze the deal and provide encouragement with practical advice."
}

# -------------------- Deal Analysis -------------------- #
if st.button("💡 Analyze My Deal"):
    if purchase_price == 0:
        st.warning("Please enter a purchase price greater than $0.")
    else:
        reserves = (vacancy_rate + maintenance_rate + management_rate) / 100
        adjusted_expenses = monthly_expenses + (monthly_rent * reserves)
        net_operating_income = (monthly_rent - adjusted_expenses) * 12
        actual_cap_rate = (net_operating_income / purchase_price) * 100
        annual_debt_service = mortgage_payment * 12
        dscr = (net_operating_income / annual_debt_service) if annual_debt_service > 0 else 0
        cash_flow = (monthly_rent - adjusted_expenses - mortgage_payment)

        # -------------------- Metrics -------------------- #
        st.subheader("📉 Raw Numbers")
        st.metric("Monthly Cash Flow", f"${cash_flow:,.2f}")
        st.metric("Cap Rate", f"{actual_cap_rate:.2f}%")
        st.metric("DSCR", f"{dscr:.2f}")

        # -------------------- Pie Chart -------------------- #
        st.subheader("📊 Rent Allocation")
        labels = ['Mortgage', 'Fixed Expenses', 'Reserves', 'Cash Flow']
        values = [mortgage_payment, monthly_expenses, monthly_rent * reserves, cash_flow]

        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)

        # -------------------- GPT Analysis -------------------- #
        prompt = (
            f"Analyze this real estate deal:\n"
            f"Address: {address}\n"
            f"Purchase Price: ${purchase_price}\n"
            f"Monthly Rent: ${monthly_rent}\n"
            f"Fixed Expenses: ${monthly_expenses}\n"
            f"Vacancy Rate: {vacancy_rate}%\n"
            f"Maintenance Rate: {maintenance_rate}%\n"
            f"Management Fee: {management_rate}%\n"
            f"Mortgage Payment: ${mortgage_payment}\n"
            f"Net Operating Income: ${net_operating_income:.2f}\n"
            f"Cap Rate: {actual_cap_rate:.2f}% (Target: {desired_cap_rate}%)\n"
            f"DSCR: {dscr:.2f} (Target: {desired_dscr})\n"
            f"Monthly Cash Flow: ${cash_flow:.2f}\n"
            f"Compare actual numbers to target goals and offer insight."
        )

        with st.spinner("Consulting the real estate oracle..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": tone_prompts[tone]},
                        {"role": "user", "content": prompt}
                    ]
                )
                ai_response = response["choices"][0]["message"]["content"]
                st.subheader("🤖 AI Analysis")
                st.write(ai_response)
            except Exception as e:
                st.error(f"Error with GPT request: {e}")
