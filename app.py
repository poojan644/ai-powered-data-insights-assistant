"""
AI-Powered Data Insights Assistant
Author: Pooja Borade

Analyze CSV & Excel datasets using AI-generated insights.
"""

import os
from io import StringIO

import pandas as pd
import streamlit as st

from anthropic import Anthropic
from dotenv import load_dotenv

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="AI-Powered Data Insights Assistant",
    page_icon="📊",
    layout="wide"
)

# ==========================================================
# ENVIRONMENT
# ==========================================================

load_dotenv()

API_KEY = (
    os.getenv("ANTHROPIC_API_KEY")
    or st.secrets.get("ANTHROPIC_API_KEY", None)
)

# ==========================================================
# APPLICATION SETTINGS
# ==========================================================

DEMO_MODE = True

MODEL = "claude-sonnet-5"

client = None

if not DEMO_MODE:

    if not API_KEY:
        st.error("Anthropic API key not found.")
        st.stop()

    client = Anthropic(api_key=API_KEY)

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title("📊 AI Assistant")

    st.markdown("---")

    if DEMO_MODE:
        st.warning("Demo Mode")
    else:
        st.success("Claude Connected")

    st.markdown("---")

    st.subheader("About")

    st.caption(
        "Analyze CSV and Excel datasets using AI-generated insights."
    )

# ==========================================================
# DATA SUMMARY
# ==========================================================

def build_data_summary(df):

    summary = []

    summary.append(
        f"Rows: {len(df)}"
    )

    summary.append(
        f"Columns: {len(df.columns)}"
    )

    summary.append(
        "\nData Types\n"
    )

    summary.append(
        df.dtypes.to_string()
    )

    missing = df.isnull().sum()

    if missing.sum():

        summary.append(
            "\nMissing Values\n"
        )

        summary.append(
            missing[missing > 0].to_string()
        )

    numeric = df.select_dtypes(include="number")

    if not numeric.empty:

        summary.append(
            "\nStatistics\n"
        )

        summary.append(
            numeric.describe().to_string()
        )

        if len(numeric.columns) >= 2:

            summary.append(
                "\nCorrelation\n"
            )

            summary.append(
                numeric.corr().round(2).to_string()
            )

    categorical = df.select_dtypes(include="object")

    if not categorical.empty:

        summary.append(
            "\nTop Categories\n"
        )

        for col in categorical.columns[:10]:

            summary.append(
                f"\n{col}"
            )

            summary.append(
                categorical[col]
                .value_counts()
                .head(5)
                .to_string()
            )

    summary.append(
        "\nSample Rows\n"
    )

    summary.append(
        df.head().to_string()
    )

    return "\n\n".join(summary)

# ==========================================================
# DATASET HEALTH SCORE
# ==========================================================

def calculate_health_score(df):

    score = 100

    missing_pct = (
        df.isnull().sum().sum()
        /
        (df.shape[0] * df.shape[1])
    ) * 100

    duplicate_pct = (
        df.duplicated().sum()
        /
        max(len(df),1)
    ) * 100

    score -= min(missing_pct * 2,20)

    score -= min(duplicate_pct * 3,20)

    score = round(max(score,0))

    return score

# ==========================================================
# CLAUDE
# ==========================================================

def ask_claude(system_prompt,user_prompt):

    if DEMO_MODE:

        if "executive" in system_prompt.lower():

            return """
## Executive Summary

The uploaded dataset appears suitable for business analysis.

---

## Key Findings

• Numeric metrics were successfully analyzed.

• Correlation analysis was completed.

• Missing values were evaluated.

---

## Risks

• Review possible outliers.

• Validate missing values before reporting.

---

## Recommendations

• Build KPI dashboards

• Clean missing data

• Explore correlations

• Continue with predictive analytics
"""

        return (
            f"Demo Mode\n\n"
            f"Question:\n{user_prompt}\n\n"
            "Claude would answer using the uploaded dataset."
        )

    try:

        response = client.messages.create(

            model=MODEL,

            max_tokens=1000,

            system=system_prompt,

            messages=[
                {
                    "role":"user",
                    "content":user_prompt
                }
            ]
        )

        return response.content[0].text

    except Exception as e:

        return str(e)

    # ==========================================================
# MAIN HEADER
# ==========================================================

st.title("📊 AI-Powered Data Insights Assistant")
st.caption("Analyze CSV and Excel datasets using AI-powered insights.")

uploaded_file = st.file_uploader(
    "Upload Dataset",
    type=["csv", "xlsx"],
    help="Supported formats: CSV and Excel (.xlsx)"
)

# ==========================================================
# LOAD DATA
# ==========================================================

if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # ------------------------------------------------------
    # SIDEBAR DATASET DETAILS
    # ------------------------------------------------------

    with st.sidebar:

        st.markdown("---")
        st.subheader("Dataset")

        st.write(f"**File:** {uploaded_file.name}")
        st.write(f"**Rows:** {len(df):,}")
        st.write(f"**Columns:** {len(df.columns)}")

    # ------------------------------------------------------
    # HEALTH SCORE
    # ------------------------------------------------------

    health = calculate_health_score(df)

    if health >= 90:
        st.success(f"🟢 Dataset Health Score: {health}/100")
    elif health >= 70:
        st.warning(f"🟡 Dataset Health Score: {health}/100")
    else:
        st.error(f"🔴 Dataset Health Score: {health}/100")

    # ------------------------------------------------------
    # KPI CARDS
    # ------------------------------------------------------

    numeric_cols = len(df.select_dtypes(include="number").columns)
    categorical_cols = len(df.select_dtypes(exclude="number").columns)

    missing = int(df.isnull().sum().sum())
    duplicates = int(df.duplicated().sum())

    k1, k2, k3, k4, k5, k6 = st.columns(6)

    k1.metric("Rows", f"{len(df):,}")
    k2.metric("Columns", len(df.columns))
    k3.metric("Numeric", numeric_cols)
    k4.metric("Categorical", categorical_cols)
    k5.metric("Missing", missing)
    k6.metric("Duplicates", duplicates)

    st.markdown("---")

    # ------------------------------------------------------
    # PREVIEW + PROFILE
    # ------------------------------------------------------

    left, right = st.columns([2, 1])

    with left:

        st.subheader("📋 Dataset Preview")

        st.dataframe(
            df.head(20),
            use_container_width=True
        )

    with right:

        st.subheader("📑 Dataset Profile")

        profile = pd.DataFrame({

            "Column": df.columns,

            "Type": df.dtypes.astype(str),

            "Missing":
                df.isnull().sum().values,

            "Unique":
                df.nunique().values

        })

        st.dataframe(
            profile,
            height=520,
            use_container_width=True
        )

    st.markdown("---")

    # ------------------------------------------------------
    # STATISTICS + VISUALIZATION
    # ------------------------------------------------------

    left, right = st.columns([1, 1])

    numeric = df.select_dtypes(include="number")

    with left:

        st.subheader("📊 Statistical Summary")

        if numeric.empty:

            st.info("No numeric columns detected.")

        else:

            st.dataframe(
                numeric.describe(),
                use_container_width=True
            )

    with right:

        st.subheader("📈 Visual Analytics")

        if numeric.empty:

            st.info("No numeric columns available.")

        else:

            chart = st.selectbox(

                "Chart Type",

                [
                    "Histogram",
                    "Bar",
                    "Line",
                    "Box"
                ]
            )

            column = st.selectbox(
                "Column",
                numeric.columns
            )

            if chart == "Histogram":

                st.bar_chart(
                    df[column].value_counts(
                        bins=20,
                        sort=False
                    )
                )

            elif chart == "Bar":

                st.bar_chart(df[column])

            elif chart == "Line":

                st.line_chart(df[column])

            elif chart == "Box":

                st.write(
                    df[[column]]
                )

    st.markdown("---")

    # ------------------------------------------------------
    # CORRELATION
    # ------------------------------------------------------

    if len(numeric.columns) >= 2:

        st.subheader("🔥 Correlation Heatmap")

        corr = numeric.corr().round(2)

        st.dataframe(
            corr,
            use_container_width=True
        )

    # ------------------------------------------------------
    # SESSION STATE
    # ------------------------------------------------------

    if (
        "data_summary" not in st.session_state
        or st.session_state.get("file_name") != uploaded_file.name
    ):

        st.session_state.data_summary = build_data_summary(df)

        st.session_state.file_name = uploaded_file.name

        st.session_state.messages = []

        if "insights" in st.session_state:
            del st.session_state["insights"]

                # ==========================================================
    # EXECUTIVE REPORT
    # ==========================================================

    st.header("🧠 AI Executive Report")

    generate = st.button(
        "✨ Generate Executive Report",
        use_container_width=True,
        type="primary"
    )

    if generate:

        with st.spinner("Analyzing your dataset..."):

            system_prompt = """
You are a Senior Business Data Analyst.

Using the dataset summary provided, generate:

1. Executive Summary

2. Key Business Findings

3. Data Quality Assessment

4. Risks & Anomalies

5. Business Recommendations

6. Suggested Next Steps

Keep the report concise and business focused.
"""

            report = ask_claude(
                system_prompt,
                st.session_state.data_summary
            )

            st.session_state.report = report

    # ==========================================================
    # DISPLAY REPORT
    # ==========================================================

    if "report" in st.session_state:

        st.success("Executive Report Generated")

        with st.expander("📝 Executive Summary", expanded=True):

            st.markdown(st.session_state.report)

        with st.expander("📈 Business Recommendations"):

            st.markdown("""
- Investigate columns with missing values.

- Validate possible outliers.

- Monitor highly correlated variables.

- Build dashboards for KPI monitoring.

- Continue with predictive analytics.
""")

        with st.expander("📊 Data Quality Checklist"):

            st.write(
                pd.DataFrame({

                    "Check":[
                        "Missing Values",
                        "Duplicate Rows",
                        "Numeric Columns",
                        "Categorical Columns"
                    ],

                    "Value":[
                        missing,
                        duplicates,
                        numeric_cols,
                        categorical_cols
                    ]

                })
            )

    # ==========================================================
    # SUGGESTED QUESTIONS
    # ==========================================================

    if "report" in st.session_state:

        st.markdown("---")

        st.subheader("💡 Suggested Questions")

        q1, q2 = st.columns(2)

        with q1:

            if st.button("📈 Which columns are highly correlated?"):

                st.session_state.quick_question = (
                    "Which columns have the strongest correlation?"
                )

            if st.button("⚠ Show missing values"):

                st.session_state.quick_question = (
                    "Which columns have missing values?"
                )

        with q2:

            if st.button("📊 Detect outliers"):

                st.session_state.quick_question = (
                    "Are there any potential outliers?"
                )

            if st.button("💡 Recommend data cleaning"):

                st.session_state.quick_question = (
                    "Recommend data cleaning steps."
                )

    # ==========================================================
    # CHATBOT
    # ==========================================================

    if "report" in st.session_state:

        st.markdown("---")

        st.header("💬 Ask AI About Your Data")

        if "messages" not in st.session_state:

            st.session_state.messages = []

        if "quick_question" in st.session_state:

            prompt = st.session_state.quick_question

            del st.session_state.quick_question

        else:

            prompt = st.chat_input(
                "Ask a question about your dataset..."
            )

        if prompt:

            st.session_state.messages.append({

                "role":"user",

                "content":prompt

            })

            with st.chat_message("user"):

                st.markdown(prompt)

            with st.chat_message("assistant"):

                with st.spinner("Thinking..."):

                    system_prompt = f"""
You are a professional business analyst.

Answer ONLY using the dataset summary below.

DATASET SUMMARY

{st.session_state.data_summary}
"""

                    answer = ask_claude(
                        system_prompt,
                        prompt
                    )

                    st.markdown(answer)

            st.session_state.messages.append({

                "role":"assistant",

                "content":answer

            })

        for msg in st.session_state.messages:

            with st.chat_message(msg["role"]):

                st.markdown(msg["content"])

    # ==========================================================
    # DOWNLOAD REPORT
    # ==========================================================

    if "report" in st.session_state:

        st.markdown("---")

        report_text = StringIO()

        report_text.write(st.session_state.report)

        st.download_button(

            "⬇ Download Executive Report",

            report_text.getvalue(),

            file_name="AI_Executive_Report.md",

            mime="text/markdown"

        )

else:

    st.info("Upload a CSV or Excel file to begin.")

    st.markdown(
        """
### 🚀 What this application can do

✔ Dataset Profiling

✔ Interactive Visualizations

✔ Statistical Summary

✔ Correlation Analysis

✔ AI Executive Report

✔ Natural Language Q&A

✔ Business Recommendations

---

**Built using**

- Streamlit
- Pandas
- Anthropic Claude
- Python
"""
    )