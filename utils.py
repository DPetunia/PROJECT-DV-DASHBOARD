"""
Shared helpers used by every page in this multi-page Streamlit app.

Keeping data loading and filtering logic in one place means every page
sees exactly the same dataset and filter behavior, with no risk of pages
drifting out of sync with each other.
"""

import streamlit as st
import pandas as pd


@st.cache_data
def load_data():
    """Load and clean the student performance dataset."""
    df = pd.read_csv("student_lifestyle_performance_dataset.csv")

    # Rename Screen_Time_Hours to act as our Internet usage proxy,
    # as required by the assignment brief.
    df = df.rename(columns={"Screen_Time_Hours": "Internet_Usage_Hours"})

    # Diet_Type and Gym_Hours_per_Week are not part of the brief's required
    # variables. Drop them if present (safe no-op if already removed upstream).
    cols_to_drop = [c for c in ["Diet_Type", "Gym_Hours_per_Week"] if c in df.columns]
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)

    return df


def render_sidebar_filters(df):
    """
    Render the shared sidebar filters and return the filtered dataframe.
    Selections persist across pages via st.session_state.
    """
    st.sidebar.title("🎓 Filters")
    st.sidebar.markdown("These filters apply across every page.")

    branches = sorted(df["Branch"].unique())
    selected_branches = st.sidebar.multiselect(
        "Branch", options=branches, default=branches, key="filter_branch"
    )

    residences = sorted(df["Residence"].unique())
    selected_residence = st.sidebar.multiselect(
        "Residence", options=residences, default=residences, key="filter_residence"
    )

    age_min, age_max = int(df["Age"].min()), int(df["Age"].max())
    selected_age = st.sidebar.slider(
        "Age range", min_value=age_min, max_value=age_max,
        value=(age_min, age_max), key="filter_age"
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("Note: CGPA in this dataset is on a 4.0-point scale.")
    st.sidebar.caption("Data Storytelling Dashboard · Scenario A · Student Performance Analytics")

    filtered_df = df[
        (df["Branch"].isin(selected_branches)) &
        (df["Residence"].isin(selected_residence)) &
        (df["Age"].between(selected_age[0], selected_age[1]))
    ]

    return filtered_df
