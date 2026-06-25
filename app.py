import streamlit as st
import plotly.express as px
from utils import load_data, render_sidebar_filters

# ----------------------------------------------------------------------------
# PAGE CONFIG (only set once, here in the main entry file)
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Student Lifestyle Performance Dataset Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------------------------------
# LOAD DATA + SIDEBAR FILTERS
# ----------------------------------------------------------------------------
df = load_data()
filtered_df = render_sidebar_filters(df)

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
st.title("📊 University Student Performance Analytics")
st.markdown(
    "Understanding the factors that influence academic performance, "
    "and where the university should focus its interventions. "
    "**CGPA is reported on a 4.0-point scale.** "
    "Use the page navigation in the sidebar to explore Factors Analysis "
    "and the Predictive Insight tool."
)

if filtered_df.empty:
    st.warning("No students match the selected filters. Please widen your selection.")
    st.stop()

# ----------------------------------------------------------------------------
# KPI SUMMARY SECTION
# ----------------------------------------------------------------------------
st.subheader("Key metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Students analyzed",
        value=f"{len(filtered_df)}",
        delta=f"of {len(df)} total"
    )
    
with col2:
    st.metric(
        label="Average CGPA (/4.0)",
        value=f"{filtered_df['CGPA'].mean():.2f}",
        delta=f"{filtered_df['CGPA'].mean() - df['CGPA'].mean():.2f} vs overall"
    )

with col3:
    st.metric(
        label="Average attendance",
        value=f"{filtered_df['Attendance_Percentage'].mean():.1f}%",
        delta=f"{filtered_df['Attendance_Percentage'].mean() - df['Attendance_Percentage'].mean():.1f}% vs overall"
    )

with col4:
    st.metric(
        label="Average study hours/day",
        value=f"{filtered_df['Study_Hours_per_Day'].mean():.2f}",
        delta=f"{filtered_df['Study_Hours_per_Day'].mean() - df['Study_Hours_per_Day'].mean():.2f} vs overall"
    )


st.markdown("---")

# ----------------------------------------------------------------------------
# CGPA DISTRIBUTION + BRANCH COMPARISON
# ----------------------------------------------------------------------------
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown("#### CGPA distribution (out of 4.0)")
    fig_hist = px.histogram(
        filtered_df, x="CGPA", nbins=20,
        color_discrete_sequence=["#1D9E75"],
        labels={"CGPA": "CGPA (/4.0)"}
    )
    fig_hist.update_layout(
        bargap=0.05,
        yaxis_title="Number of students",
        xaxis_title="CGPA (/4.0)",
        showlegend=False
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with row1_col2:
    st.markdown("#### Average CGPA by branch — which groups perform best")
    branch_avg = (
        filtered_df.groupby("Branch")["CGPA"]
        .mean()
        .sort_values(ascending=True)
        .reset_index()
    )
    fig_branch = px.bar(
        branch_avg, x="CGPA", y="Branch", orientation="h",
        color="CGPA", color_continuous_scale="Tealgrn",
        labels={"CGPA": "Average CGPA (/4.0)", "Branch": ""}
    )
    fig_branch.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_branch, use_container_width=True)

best_branch = branch_avg.sort_values("CGPA", ascending=False).iloc[0]
worst_branch = branch_avg.sort_values("CGPA", ascending=False).iloc[-1]
st.info(
    f"**✅ Answer: which student groups perform best?** "
    f"{best_branch['Branch']} students have the highest average CGPA "
    f"({best_branch['CGPA']:.2f}/4.0), while {worst_branch['Branch']} students "
    f"have the lowest ({worst_branch['CGPA']:.2f}/4.0). Use the sidebar filters "
    f"to compare by residence and age as well."
)

st.markdown("---")

# ----------------------------------------------------------------------------
# RAW DATA VIEW
# ----------------------------------------------------------------------------
with st.expander("View filtered raw data"):
    st.dataframe(filtered_df, use_container_width=True)
    st.caption(f"Showing {len(filtered_df)} of {len(df)} total students")

st.markdown("---")

# ----------------------------------------------------------------------------
# DIRECT ANSWER: RECOMMENDED INTERVENTIONS (Management Question 3)
# ----------------------------------------------------------------------------
st.subheader("✅ Answer: what interventions should the university implement?")

corr_sleep = filtered_df["Sleep_Hours"].corr(filtered_df["CGPA"])
corr_study = filtered_df["Study_Hours_per_Day"].corr(filtered_df["CGPA"])
corr_att = filtered_df["Attendance_Percentage"].corr(filtered_df["CGPA"])

st.markdown(
    f"""
Based on the strength of each factor's relationship with CGPA (see the
Factors Analysis page for full detail):

1. **Protect student sleep.** Sleep has the strongest link to CGPA in this
   dataset (correlation = {corr_sleep:.2f}). Consider scheduling guidance,
   later morning class start times, or awareness campaigns on sleep hygiene.
2. **Encourage consistent daily study habits.** Study hours show a strong
   positive relationship with CGPA (correlation = {corr_study:.2f}).
   Structured study groups or time-management workshops could help.
3. **Reinforce attendance policies.** Attendance has a moderate positive
   relationship with CGPA (correlation = {corr_att:.2f}), supporting
   continued (but not overly punitive) attendance monitoring.
4. **Don't over-invest in internet-usage restrictions.** Internet usage
   shows almost no measurable relationship with CGPA in this data, so
   blanket restrictions are unlikely to move the needle on their own.

These are data-driven starting points, not a complete policy — they
should be combined with student feedback before rollout.
"""
)

st.markdown("---")

# ----------------------------------------------------------------------------
# EXPLICIT PAGE NAVIGATION (in addition to the sidebar nav)
# ----------------------------------------------------------------------------
st.markdown("#### Continue exploring")
nav_col1, nav_col2 = st.columns(2)
with nav_col1:
    st.page_link("pages/1_Factors_Analysis.py", label="🔍 Go to Factors Analysis", use_container_width=True)
with nav_col2:
    st.page_link("pages/2_Predictive_Visualization.py", label="🔮 Go to Predictive Visualization", use_container_width=True)
