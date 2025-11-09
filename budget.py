#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# -------------------------
# BASIC CONFIG
# -------------------------
st.set_page_config(page_title="Personal Budget Tracker", page_icon="💰", layout="wide")
st.title("💰 Personal Budget Tracker")

# -------------------------
# PASSWORD LOGIN
# -------------------------
PASSWORD = "2580"  # Change this password for your privacy

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.subheader("🔐 Login to Access Your Budget Tracker")
    password = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Incorrect password.")
    st.stop()

# -------------------------
# DATA FILES
# -------------------------
username = "vaibhav"
expense_file = f"expenses_{username}.csv"
income_file = f"income_{username}.csv"

if not os.path.exists(expense_file):
    pd.DataFrame(columns=["Date", "Category", "Description", "Amount"]).to_csv(expense_file, index=False)
if not os.path.exists(income_file):
    pd.DataFrame(columns=["Date", "Source", "Amount"]).to_csv(income_file, index=False)

# -------------------------
# SIDEBAR NAVIGATION
# -------------------------
menu = ["Add Transactions", "Dashboard", "Download Data", "Upload Data"]
choice = st.sidebar.radio("Go to", menu)
st.sidebar.markdown("---")
st.sidebar.info("Made by Ayush")

# -------------------------
# ADD TRANSACTIONS
# -------------------------
if choice == "Add Transactions":
    st.subheader("➕ Add Transactions")

    tab1, tab2 = st.tabs(["💸 Add Expense", "💰 Add Income"])

    with tab1:
        st.subheader("Add a new expense")
        date = st.date_input("Date", datetime.today())
        category = st.selectbox(
            "Category",
            ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"]
        )
        desc = st.text_input("Description")
        amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")

        if st.button("Add Expense"):
            new_expense = pd.DataFrame([[date, category, desc, amount]],
                                       columns=["Date", "Category", "Description", "Amount"])
            old_expenses = pd.read_csv(expense_file)
            updated = pd.concat([old_expenses, new_expense], ignore_index=True)
            updated.to_csv(expense_file, index=False)
            st.success("✅ Expense added successfully!")

    with tab2:
        st.subheader("Add a new income")
        date = st.date_input("Date", datetime.today(), key="income_date")
        source = st.text_input("Source")
        amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f", key="income_amt")

        if st.button("Add Income"):
            new_income = pd.DataFrame([[date, source, amount]], columns=["Date", "Source", "Amount"])
            old_income = pd.read_csv(income_file)
            updated = pd.concat([old_income, new_income], ignore_index=True)
            updated.to_csv(income_file, index=False)
            st.success("✅ Income added successfully!")

# -------------------------
# DASHBOARD
# -------------------------
elif choice == "Dashboard":
    st.subheader("📊 Dashboard Overview")

    expenses = pd.read_csv(expense_file)
    income = pd.read_csv(income_file)

    total_expense = expenses["Amount"].sum() if not expenses.empty else 0
    total_income = income["Amount"].sum() if not income.empty else 0
    savings = total_income - total_expense

    # Summary metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("💸 Total Expenses", f"₹{total_expense:,.2f}")
    c2.metric("💰 Total Income", f"₹{total_income:,.2f}")
    c3.metric("💵 Savings", f"₹{savings:,.2f}")

    st.markdown("---")

    if not expenses.empty:
        st.subheader("📉 Expense Insights")
        expenses["Date"] = pd.to_datetime(expenses["Date"])

        # 1️⃣ Category Pie
        fig1 = px.pie(expenses, names="Category", values="Amount", title="Expense Distribution by Category", hole=0.4)
        st.plotly_chart(fig1, use_container_width=True)

        # 2️⃣ Top 5 Categories
        top_cat = expenses.groupby("Category")["Amount"].sum().sort_values(ascending=False).head(5).reset_index()
        fig2 = px.bar(top_cat, x="Amount", y="Category", orientation="h",
                      title="Top 5 Spending Categories", text="Amount", color="Category")
        st.plotly_chart(fig2, use_container_width=True)

        # 3️⃣ Daily Spending Trend
        daily = expenses.groupby("Date")["Amount"].sum().reset_index()
        fig3 = px.line(daily, x="Date", y="Amount", markers=True, title="Daily Spending Trend (₹)")
        st.plotly_chart(fig3, use_container_width=True)

        # 4️⃣ Monthly Breakdown by Category
        expenses["Month"] = expenses["Date"].dt.to_period("M")
        monthly_cat = expenses.groupby(["Month", "Category"])["Amount"].sum().reset_index()
        monthly_cat["Month"] = monthly_cat["Month"].astype(str)
        fig4 = px.bar(monthly_cat, x="Month", y="Amount", color="Category",
                      title="Monthly Expense Breakdown by Category", text="Amount")
        st.plotly_chart(fig4, use_container_width=True)

    if not income.empty:
        st.subheader("💰 Income Insights")
        income["Date"] = pd.to_datetime(income["Date"])

        # 5️⃣ Income Sources
        fig5 = px.bar(income, x="Source", y="Amount", color="Source", title="Income by Source", text="Amount")
        st.plotly_chart(fig5, use_container_width=True)

        # 6️⃣ Monthly Income Trend
        income["Month"] = income["Date"].dt.to_period("M")
        monthly_income = income.groupby("Month")["Amount"].sum().reset_index()
        monthly_income["Month"] = monthly_income["Month"].astype(str)
        fig6 = px.line(monthly_income, x="Month", y="Amount", markers=True, title="Monthly Income Trend")
        st.plotly_chart(fig6, use_container_width=True)

    # 7️⃣ Income vs Expense Comparison
    if not income.empty and not expenses.empty:
        st.subheader("📈 Income vs Expense Comparison")
        expenses["Month"] = pd.to_datetime(expenses["Date"]).dt.to_period("M")
        income["Month"] = pd.to_datetime(income["Date"]).dt.to_period("M")
        exp_monthly = expenses.groupby("Month")["Amount"].sum().reset_index(name="Expenses")
        inc_monthly = income.groupby("Month")["Amount"].sum().reset_index(name="Income")

        compare = pd.merge(inc_monthly, exp_monthly, on="Month", how="outer").fillna(0)
        compare["Month"] = compare["Month"].astype(str)
        fig7 = px.bar(compare, x="Month", y=["Income", "Expenses"], barmode="group",
                      title="Income vs Expenses per Month")
        st.plotly_chart(fig7, use_container_width=True)

        # 8️⃣ Cumulative Savings
        compare["Savings"] = compare["Income"].cumsum() - compare["Expenses"].cumsum()
        fig8 = px.line(compare, x="Month", y="Savings", markers=True, title="Cumulative Savings Over Time")
        st.plotly_chart(fig8, use_container_width=True)

# -------------------------
# DOWNLOAD DATA
# -------------------------
elif choice == "Download Data":
    st.subheader("📥 Download Your Data")

    with open(expense_file, "rb") as f:
        st.download_button("⬇️ Download Expenses CSV", f, file_name=expense_file)

    with open(income_file, "rb") as f:
        st.download_button("⬇️ Download Income CSV", f, file_name=income_file)

# -------------------------
# UPLOAD DATA
# -------------------------
elif choice == "Upload Data":
    st.header("📤 Upload Your Existing Expense or Income File")

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded successfully!")

        st.subheader("Preview of Uploaded Data")
        st.dataframe(df)

        if "Category" in df.columns:
            st.info("📊 Detected as Expense Data")
            total = df["Amount"].sum()
            st.write(f"**Total Expenses:** ₹{total:,.2f}")

            fig = px.bar(df, x="Category", y="Amount", color="Category",
                         title="Expenses by Category", text="Amount")
            st.plotly_chart(fig, use_container_width=True)

            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"])
                monthly = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum().reset_index()
                monthly["Date"] = monthly["Date"].astype(str)
                fig2 = px.line(monthly, x="Date", y="Amount", markers=True,
                               title="Monthly Spending Trend")
                st.plotly_chart(fig2, use_container_width=True)

        elif "Source" in df.columns:
            st.info("💰 Detected as Income Data")
            total = df["Amount"].sum()
            st.write(f"**Total Income:** ₹{total:,.2f}")

            fig = px.bar(df, x="Source", y="Amount", color="Source",
                         title="Income Sources", text="Amount")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Unrecognized file format. Please ensure your CSV columns match the expected format.")

