import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime

from database import (
    add_transaction,
    get_transactions,
    update_transaction,
    delete_transaction,
    get_budget,
    update_budget
)

from auth import (
    register_user,
    login_user
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Finance Tracker",
    page_icon="💰",
    layout="wide"
)


# ==================================================
# PINK & WHITE THEME
# ==================================================

st.markdown("""
<style>

.stApp {
    background-color: #fff7fa;
}

.main-title {
    font-size: 42px;
    font-weight: 700;
    color: #d81b60;
    margin-bottom: 5px;
}

.subtitle {
    color: #777777;
    font-size: 17px;
    margin-bottom: 25px;
}

.section-title {
    font-size: 24px;
    font-weight: 600;
    color: #c2185b;
    margin-top: 10px;
    margin-bottom: 15px;
}

div[data-testid="stMetric"] {
    background-color: white;
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #f8bbd0;
    box-shadow: 0px 4px 12px rgba(216, 27, 96, 0.08);
}

div[data-testid="stMetricLabel"] {
    color: #777777;
}

div[data-testid="stMetricValue"] {
    color: #d81b60;
}

.stButton > button {
    background-color: #e91e63;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 22px;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #c2185b;
    color: white;
}

.stDownloadButton > button {
    background-color: white;
    color: #d81b60;
    border: 1px solid #f8bbd0;
    border-radius: 10px;
    font-weight: 600;
}

.stTextInput input,
.stNumberInput input {
    border-radius: 9px;
    border: 1px solid #f8bbd0;
}

div[data-baseweb="select"] > div {
    border-radius: 9px;
    border-color: #f8bbd0;
}

div[data-testid="stAlert"] {
    border-radius: 10px;
}

hr {
    border: none;
    height: 1px;
    background-color: #f8bbd0;
    margin: 25px 0;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# SESSION STATE
# ==================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = None


# ==================================================
# LOGIN / REGISTER
# ==================================================

if not st.session_state.logged_in:

    st.markdown(
        '<div class="main-title">Finance Tracker</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Manage your income, expenses, and financial goals securely.'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    login_tab, register_tab = st.tabs(
        ["Login", "Create Account"]
    )

    # --------------------------------------------------
    # LOGIN
    # --------------------------------------------------

    with login_tab:

        st.markdown(
            '<div class="section-title">Welcome Back</div>',
            unsafe_allow_html=True
        )

        username = st.text_input(
            "Username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            key="login_button"
        ):

            if not username or not password:

                st.error(
                    "Please enter username and password."
                )

            else:

                user = login_user(
                    username,
                    password
                )

                if user:

                    st.session_state.logged_in = True
                    st.session_state.user_id = user["id"]
                    st.session_state.username = user["username"]

                    st.rerun()

                else:

                    st.error(
                        "Invalid username or password."
                    )

    # --------------------------------------------------
    # REGISTER
    # --------------------------------------------------

    with register_tab:

        st.markdown(
            '<div class="section-title">Create Account</div>',
            unsafe_allow_html=True
        )

        new_username = st.text_input(
            "Choose Username",
            key="register_username"
        )

        new_password = st.text_input(
            "Choose Password",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button(
            "Create Account",
            key="register_button"
        ):

            if not new_username or not new_password:

                st.error(
                    "Please fill in all fields."
                )

            elif new_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(new_password) < 6:

                st.error(
                    "Password must contain at least 6 characters."
                )

            else:

                success = register_user(
                    new_username,
                    new_password
                )

                if success:

                    st.success(
                        "Account created successfully! You can now login."
                    )

                else:

                    st.error(
                        "Username already exists."
                    )

    st.stop()


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.markdown(
        "## Finance Tracker"
    )

    st.write(
        f"Welcome, **{st.session_state.username}**"
    )

    st.divider()

    if st.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None

        st.rerun()


# ==================================================
# USER INFORMATION
# ==================================================

user_id = st.session_state.user_id

transactions = get_transactions(user_id)

monthly_budget = get_budget(user_id)


# ==================================================
# CONVERT DATABASE DATA TO DATAFRAME
# ==================================================

if transactions:

    data = []

    for transaction in transactions:

        data.append({
            "ID": transaction["id"],
            "Type": transaction["transaction_type"],
            "Amount": transaction["amount"],
            "Category": transaction["category"],
            "Date": transaction["date"],
            "Description": transaction["description"] or ""
        })

    df = pd.DataFrame(data)

else:

    df = pd.DataFrame(
        columns=[
            "ID",
            "Type",
            "Amount",
            "Category",
            "Date",
            "Description"
        ]
    )


# ==================================================
# CLEAN DATE COLUMN
# ==================================================

if not df.empty:

    df["Date"] = pd.to_datetime(
        df["Date"]
    )

    df["Month"] = df["Date"].dt.strftime(
        "%b %Y"
    )


# ==================================================
# CALCULATE TOTALS
# ==================================================

income = df.loc[
    df["Type"] == "Income",
    "Amount"
].sum()

expenses = df.loc[
    df["Type"] == "Expense",
    "Amount"
].sum()

balance = income - expenses

if income > 0:

    savings_rate = (
        balance / income
    ) * 100

else:

    savings_rate = 0


# ==================================================
# HEADER
# ==================================================

st.markdown(
    '<div class="main-title">Finance Tracker</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Track your income, expenses, savings, and financial habits in one place.'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ==================================================
# DASHBOARD
# ==================================================

st.markdown(
    '<div class="section-title">Financial Dashboard</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Total Income",
        f"₹{income:,.2f}"
    )

with col2:

    st.metric(
        "Total Expenses",
        f"₹{expenses:,.2f}"
    )

with col3:

    st.metric(
        "Current Balance",
        f"₹{balance:,.2f}"
    )

with col4:

    st.metric(
        "Savings Rate",
        f"{savings_rate:.1f}%"
    )


# ==================================================
# MONTHLY BUDGET
# ==================================================

st.divider()

st.markdown(
    '<div class="section-title">Monthly Budget</div>',
    unsafe_allow_html=True
)

budget_col1, budget_col2 = st.columns([2, 1])

with budget_col1:

    if monthly_budget > 0:

        budget_percentage = (
            expenses / monthly_budget
        ) * 100

        progress_value = min(
            expenses / monthly_budget,
            1.0
        )

    else:

        budget_percentage = 0
        progress_value = 0

    st.progress(
        progress_value
    )

    st.write(
        f"**₹{expenses:,.2f}** spent "
        f"of **₹{monthly_budget:,.2f}**"
    )

    st.write(
        f"Budget used: **{budget_percentage:.1f}%**"
    )

    if expenses > monthly_budget:

        st.error(
            "You have exceeded your monthly budget."
        )

    elif expenses >= monthly_budget * 0.8:

        st.warning(
            "You have used more than 80% of your budget."
        )

    else:

        remaining = (
            monthly_budget - expenses
        )

        st.success(
            f"₹{remaining:,.2f} remaining in your budget."
        )


with budget_col2:

    new_budget = st.number_input(
        "Set Monthly Budget",
        min_value=100.0,
        value=float(monthly_budget),
        step=500.0
    )

    if st.button(
        "Update Budget"
    ):

        update_budget(
            user_id,
            new_budget
        )

        st.success(
            "Budget updated successfully!"
        )

        st.rerun()


# ==================================================
# ADD TRANSACTION
# ==================================================

st.divider()

st.markdown(
    '<div class="section-title">Add Transaction</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:

    transaction_type = st.selectbox(
        "Transaction Type",
        ["Income", "Expense"]
    )

with col2:

    amount = st.number_input(
        "Amount (₹)",
        min_value=0.0,
        step=100.0
    )


col1, col2 = st.columns(2)

with col1:

    category = st.selectbox(
        "Category",
        [
            "Food",
            "Travel",
            "Shopping",
            "Bills",
            "Education",
            "Entertainment",
            "Salary",
            "Other"
        ]
    )

with col2:

    transaction_date = st.date_input(
        "Date",
        value=date.today()
    )


description = st.text_input(
    "Description",
    placeholder="Example: Lunch, Bus ticket, Monthly salary..."
)


if st.button(
    "Add Transaction"
):

    if amount <= 0:

        st.error(
            "Please enter an amount greater than ₹0."
        )

    else:

        add_transaction(
            user_id,
            transaction_type,
            amount,
            category,
            transaction_date,
            description
        )

        st.success(
            "Transaction added successfully!"
        )

        st.rerun()


# ==================================================
# ANALYTICS HEADER
# ==================================================

st.divider()

st.markdown(
    '<div class="section-title">Financial Analytics</div>',
    unsafe_allow_html=True
)


# ==================================================
# EXPENSE ANALYTICS
# ==================================================

expense_df = df[
    df["Type"] == "Expense"
].copy()


if not expense_df.empty:

    category_summary = (
        expense_df
        .groupby(
            "Category",
            as_index=False
        )["Amount"]
        .sum()
        .sort_values(
            "Amount",
            ascending=False
        )
    )


    # --------------------------------------------------
    # BAR CHART
    # --------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        fig_bar = px.bar(
            category_summary,
            x="Category",
            y="Amount",
            title="Expenses by Category",
            text="Amount"
        )

        fig_bar.update_traces(
            texttemplate="₹%{text:.0f}",
            textposition="outside"
        )

        fig_bar.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis_title="Category",
            yaxis_title="Amount (₹)",
            showlegend=False
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )


    # --------------------------------------------------
    # DONUT CHART
    # --------------------------------------------------

    with col2:

        fig_pie = px.pie(
            category_summary,
            names="Category",
            values="Amount",
            title="Spending Distribution",
            hole=0.55
        )

        fig_pie.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )


    # --------------------------------------------------
    # TOP CATEGORY
    # --------------------------------------------------

    top_category = category_summary.iloc[0]["Category"]

    top_amount = category_summary.iloc[0]["Amount"]

    percentage_top = (
        top_amount / expenses
    ) * 100

    insight_col1, insight_col2, insight_col3 = st.columns(3)

    with insight_col1:

        st.metric(
            "Top Spending Category",
            top_category
        )

    with insight_col2:

        st.metric(
            "Top Category Amount",
            f"₹{top_amount:,.2f}"
        )

    with insight_col3:

        st.metric(
            "Share of Expenses",
            f"{percentage_top:.1f}%"
        )


else:

    st.info(
        "Add expense transactions to see spending analytics."
    )


# ==================================================
# MONTHLY SPENDING TREND
# ==================================================

st.markdown(
    '<div class="section-title">Monthly Spending Trend</div>',
    unsafe_allow_html=True
)

if not expense_df.empty:

    monthly_expenses = (
        expense_df
        .groupby(
            "Month",
            as_index=False
        )["Amount"]
        .sum()
    )

    monthly_expenses["MonthDate"] = pd.to_datetime(
        monthly_expenses["Month"],
        format="%b %Y"
    )

    monthly_expenses = monthly_expenses.sort_values(
        "MonthDate"
    )

    fig_monthly = px.line(
        monthly_expenses,
        x="Month",
        y="Amount",
        markers=True,
        title="Monthly Expense Trend"
    )

    fig_monthly.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_title="Month",
        yaxis_title="Expenses (₹)"
    )

    st.plotly_chart(
        fig_monthly,
        use_container_width=True
    )

else:

    st.info(
        "Monthly spending analysis will appear after adding expenses."
    )


# ==================================================
# INCOME VS EXPENSES
# ==================================================

st.markdown(
    '<div class="section-title">Income vs Expenses</div>',
    unsafe_allow_html=True
)

if not df.empty:

    comparison_df = pd.DataFrame({
        "Type": [
            "Income",
            "Expenses",
            "Balance"
        ],
        "Amount": [
            income,
            expenses,
            balance
        ]
    })

    fig_comparison = px.bar(
        comparison_df,
        x="Type",
        y="Amount",
        text="Amount",
        title="Overall Financial Comparison"
    )

    fig_comparison.update_traces(
        texttemplate="₹%{text:.0f}",
        textposition="outside"
    )

    fig_comparison.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_title="",
        yaxis_title="Amount (₹)",
        showlegend=False
    )

    st.plotly_chart(
        fig_comparison,
        use_container_width=True
    )


# ==================================================
# AUTOMATIC FINANCIAL INSIGHTS
# ==================================================

st.divider()

st.markdown(
    '<div class="section-title">Smart Financial Insights</div>',
    unsafe_allow_html=True
)

insight_col1, insight_col2 = st.columns(2)


with insight_col1:

    if expenses == 0:

        st.info(
            "💡 Start adding expenses to receive personalized spending insights."
        )

    elif savings_rate >= 30:

        st.success(
            f"Excellent! You are currently saving "
            f"{savings_rate:.1f}% of your income."
        )

    elif savings_rate >= 20:

        st.success(
            f"Good job! You are saving "
            f"{savings_rate:.1f}% of your income."
        )

    elif savings_rate >= 0:

        st.warning(
            f"Your current savings rate is "
            f"{savings_rate:.1f}%. "
            f"Try reducing unnecessary expenses."
        )

    else:

        st.error(
            "Your expenses are higher than your income. "
            "Consider reviewing your spending."
        )


with insight_col2:

    if not expense_df.empty:

        if top_category in [
            "Entertainment",
            "Shopping"
        ]:

            st.warning(
                f"💡 Your highest spending is on "
                f"{top_category}. "
                f"Consider setting a limit for this category."
            )

        else:

            st.info(
                f"💡 Your highest spending category is "
                f"{top_category} at "
                f"₹{top_amount:,.2f}."
            )

    else:

        st.info(
            "💡 Add expenses to receive spending recommendations."
        )


# ==================================================
# TRANSACTION HISTORY
# ==================================================

st.divider()

st.markdown(
    '<div class="section-title">Transaction History</div>',
    unsafe_allow_html=True
)


if not df.empty:

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:

        type_filter = st.selectbox(
            "Transaction Type",
            ["All", "Income", "Expense"]
        )

    with filter_col2:

        category_options = (
            ["All"] +
            sorted(
                df["Category"].unique().tolist()
            )
        )

        category_filter = st.selectbox(
            "Category",
            category_options
        )

    with filter_col3:

        search = st.text_input(
            "Search Description"
        )


    filtered_df = df.copy()


    if type_filter != "All":

        filtered_df = filtered_df[
            filtered_df["Type"] == type_filter
        ]


    if category_filter != "All":

        filtered_df = filtered_df[
            filtered_df["Category"] == category_filter
        ]


    if search:

        filtered_df = filtered_df[
            filtered_df["Description"]
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]


    if filtered_df.empty:

        st.info(
            "No transactions match your filters."
        )

    else:

        for _, transaction in filtered_df.iterrows():

            transaction_id = int(
                transaction["ID"]
            )

            col1, col2, col3, col4, col5, col6 = st.columns(
                [1, 1, 1, 2, 0.7, 0.7]
            )

            with col1:

                st.write(
                    transaction["Type"]
                )

            with col2:

                st.write(
                    f"₹{transaction['Amount']:,.2f}"
                )

            with col3:

                st.write(
                    transaction["Category"]
                )

            with col4:

                st.write(
                    f"{transaction['Date'].strftime('%Y-%m-%d')} - "
                    f"{transaction['Description']}"
                )

            with col5:

                edit_clicked = st.button(
                    "Edit",
                    key=f"edit_{transaction_id}"
                )

            with col6:

                delete_clicked = st.button(
                    "Delete",
                    key=f"delete_{transaction_id}"
                )


            if edit_clicked:

                st.session_state[
                    f"editing_{transaction_id}"
                ] = True

                st.rerun()


            if st.session_state.get(
                f"editing_{transaction_id}",
                False
            ):

                with st.form(
                    f"edit_form_{transaction_id}"
                ):

                    st.markdown(
                        f"### Edit Transaction #{transaction_id}"
                    )

                    edit_col1, edit_col2 = st.columns(2)

                    with edit_col1:

                        edit_type = st.selectbox(
                            "Transaction Type",
                            ["Income", "Expense"],
                            index=(
                                0
                                if transaction["Type"] == "Income"
                                else 1
                            )
                        )

                    with edit_col2:

                        edit_amount = st.number_input(
                            "Amount (₹)",
                            min_value=0.0,
                            value=float(
                                transaction["Amount"]
                            ),
                            step=100.0
                        )

                    edit_col1, edit_col2 = st.columns(2)

                    categories = [
                        "Food",
                        "Travel",
                        "Shopping",
                        "Bills",
                        "Education",
                        "Entertainment",
                        "Salary",
                        "Other"
                    ]

                    with edit_col1:

                        current_category = transaction[
                            "Category"
                        ]

                        category_index = (
                            categories.index(
                                current_category
                            )
                            if current_category in categories
                            else 0
                        )

                        edit_category = st.selectbox(
                            "Category",
                            categories,
                            index=category_index
                        )

                    with edit_col2:

                        edit_date = st.date_input(
                            "Date",
                            value=transaction["Date"].date()
                        )

                    edit_description = st.text_input(
                        "Description",
                        value=transaction["Description"]
                    )

                    save_col1, save_col2 = st.columns(2)

                    with save_col1:

                        save_changes = st.form_submit_button(
                            "Save Changes"
                        )

                    with save_col2:

                        cancel_edit = st.form_submit_button(
                            "Cancel"
                        )


                    if save_changes:

                        if edit_amount <= 0:

                            st.error(
                                "Amount must be greater than ₹0."
                            )

                        else:

                            update_transaction(
                                transaction_id,
                                user_id,
                                edit_type,
                                edit_amount,
                                edit_category,
                                edit_date,
                                edit_description
                            )

                            st.session_state[
                                f"editing_{transaction_id}"
                            ] = False

                            st.success(
                                "Transaction updated successfully!"
                            )

                            st.rerun()


                    if cancel_edit:

                        st.session_state[
                            f"editing_{transaction_id}"
                        ] = False

                        st.rerun()


            if delete_clicked:

                delete_transaction(
                    transaction_id,
                    user_id
                )

                st.success(
                    "Transaction deleted successfully!"
                )

                st.rerun()


else:

    st.info(
        "No transactions yet. Add your first transaction."
    )


# ==================================================
# EXPORT DATA
# ==================================================

st.divider()

st.markdown(
    '<div class="section-title">Export Data</div>',
    unsafe_allow_html=True
)

if not df.empty:

    export_df = df.drop(
        columns=["ID", "Month"],
        errors="ignore"
    )

    export_df["Date"] = export_df[
        "Date"
    ].dt.strftime(
        "%Y-%m-%d"
    )

    csv_data = export_df.to_csv(
        index=False
    )

    st.download_button(
        label="Download Transactions as CSV",
        data=csv_data,
        file_name="finance_transactions.csv",
        mime="text/csv"
    )

else:

    st.info(
        "Add transactions before exporting data."
    )


# ==================================================
# FINAL SUMMARY
# ==================================================

st.divider()

st.markdown(
    '<div class="section-title">Financial Summary</div>',
    unsafe_allow_html=True
)

summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:

    st.write(
        f"**Total Transactions:** {len(df)}"
    )

    st.write(
        f"**Total Income:** ₹{income:,.2f}"
    )

with summary_col2:

    st.write(
        f"**Total Expenses:** ₹{expenses:,.2f}"
    )

    st.write(
        f"**Current Balance:** ₹{balance:,.2f}"
    )

with summary_col3:

    st.write(
        f"**Monthly Budget:** ₹{monthly_budget:,.2f}"
    )

    st.write(
        f"**Savings Rate:** {savings_rate:.1f}%"
    )