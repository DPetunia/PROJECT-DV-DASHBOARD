import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data, render_sidebar_filters

st.set_page_config(
    page_title="Factors Analysis",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

df = load_data()
filtered_df = render_sidebar_filters(df)

st.title("🔍 Factors Influencing Academic Performance")
st.markdown(
    "How sleep, study habits, attendance, internet usage, demographics, "
    "and stress relate to CGPA. Trend lines show the overall direction "
    "of each relationship."
)

if filtered_df.empty:
    st.warning("No students match the selected filters. Please widen your selection.")
    st.stop()

# ----------------------------------------------------------------------------
# DIRECT ANSWER: WHICH FACTORS ACTUALLY MATTER (Management Question 1)
# ----------------------------------------------------------------------------
st.subheader("✅ Answer: which factors actually influence CGPA?")
st.markdown(
    "Not every factor matters equally. The chart below ranks each factor "
    "by how strongly it relates to CGPA, from strongest to weakest."
)

factor_cols = {
    "Sleep_Hours": "Sleep hours",
    "Study_Hours_per_Day": "Study hours/day",
    "Attendance_Percentage": "Attendance",
    "Internet_Usage_Hours": "Internet usage",
    "Stress_Level_1_to_10": "Stress level",
    "Age": "Age",
}

corr_rows = []
for col, label in factor_cols.items():
    corr_rows.append({
        "Factor": label,
        "Correlation": filtered_df[col].corr(filtered_df["CGPA"])
    })

corr_df = pd.DataFrame(corr_rows)
corr_df["AbsCorrelation"] = corr_df["Correlation"].abs()
corr_df = corr_df.sort_values("AbsCorrelation", ascending=True)

def classify(val):
    a = abs(val)
    if a >= 0.5:
        strength = "Strong"
    elif a >= 0.3:
        strength = "Moderate"
    elif a >= 0.1:
        strength = "Weak"
    else:
        strength = "Negligible"
    direction = "boosts" if val > 0 else "hurts"
    return f"{strength} — {direction} CGPA" if a >= 0.1 else f"{strength} effect"

corr_df["Verdict"] = corr_df["Correlation"].apply(classify)

fig_corr = px.bar(
    corr_df, x="Correlation", y="Factor", orientation="h",
    color="Correlation", color_continuous_scale="RdYlGn",
    range_color=[-1, 1],
    text="Verdict",
    labels={"Correlation": "Correlation with CGPA", "Factor": ""}
)
fig_corr.update_traces(textposition="outside")
fig_corr.update_layout(coloraxis_showscale=False, margin=dict(r=160))
st.plotly_chart(fig_corr, use_container_width=True)

strongest = corr_df.sort_values("AbsCorrelation", ascending=False).iloc[0]
weakest = corr_df.sort_values("AbsCorrelation", ascending=False).iloc[-1]
st.success(
    f"**Bottom line:** {strongest['Factor']} has the strongest relationship with CGPA "
    f"(correlation = {strongest['Correlation']:.2f}). "
    f"{weakest['Factor']} has almost no measurable relationship "
    f"(correlation = {weakest['Correlation']:.2f}) — the university shouldn't "
    f"prioritize interventions targeting it."
)

st.markdown("---")
st.markdown(
    "The charts below show each relationship in detail, including how it "
    "varies by branch and residence."
)

# ----------------------------------------------------------------------------
# ROW 1: SLEEP VS CGPA + STUDY HOURS VS CGPA
# ----------------------------------------------------------------------------
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown("#### Sleep hours vs CGPA")
    fig_sleep = px.scatter(
        filtered_df, x="Sleep_Hours", y="CGPA",
        color="Branch", trendline="ols",
        labels={"Sleep_Hours": "Sleep hours per day", "CGPA": "CGPA (/4.0)"}
    )
    st.plotly_chart(fig_sleep, use_container_width=True)
    corr_sleep = filtered_df["Sleep_Hours"].corr(filtered_df["CGPA"])
    st.caption(f"Correlation coefficient: {corr_sleep:.2f}")

with row1_col2:
    st.markdown("#### Study hours vs CGPA")
    fig_study = px.scatter(
        filtered_df, x="Study_Hours_per_Day", y="CGPA",
        color="Branch", trendline="ols",
        labels={"Study_Hours_per_Day": "Study hours per day", "CGPA": "CGPA (/4.0)"}
    )
    st.plotly_chart(fig_study, use_container_width=True)
    corr_study = filtered_df["Study_Hours_per_Day"].corr(filtered_df["CGPA"])
    st.caption(f"Correlation coefficient: {corr_study:.2f}")

# ----------------------------------------------------------------------------
# ROW 2: ATTENDANCE VS CGPA + INTERNET USAGE VS CGPA
# ----------------------------------------------------------------------------
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown("#### Attendance vs CGPA")
    fig_att = px.scatter(
        filtered_df, x="Attendance_Percentage", y="CGPA",
        color="Residence", trendline="ols",
        labels={"Attendance_Percentage": "Attendance (%)", "CGPA": "CGPA (/4.0)"}
    )
    st.plotly_chart(fig_att, use_container_width=True)
    corr_att = filtered_df["Attendance_Percentage"].corr(filtered_df["CGPA"])
    st.caption(f"Correlation coefficient: {corr_att:.2f}")

with row2_col2:
    st.markdown("#### Internet usage vs CGPA")
    fig_internet = px.scatter(
        filtered_df, x="Internet_Usage_Hours", y="CGPA",
        color="Residence", trendline="ols",
        labels={"Internet_Usage_Hours": "Internet usage (hours/day)", "CGPA": "CGPA (/4.0)"}
    )
    st.plotly_chart(fig_internet, use_container_width=True)
    corr_internet = filtered_df["Internet_Usage_Hours"].corr(filtered_df["CGPA"])
    st.caption(f"Correlation coefficient: {corr_internet:.2f}")
    st.caption("Internet usage is approximated from device screen-time hours in this dataset.")

# ----------------------------------------------------------------------------
# ROW 3: DEMOGRAPHICS (AGE) + STRESS LEVEL (BONUS FACTOR)
# ----------------------------------------------------------------------------
row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    st.markdown("#### Average CGPA by age — demographics")
    age_avg = (
        filtered_df.groupby("Age")["CGPA"]
        .mean()
        .reset_index()
        .sort_values("Age")
    )
    fig_age = px.line(
        age_avg, x="Age", y="CGPA", markers=True,
        color_discrete_sequence=["#534AB7"],
        labels={"Age": "Age", "CGPA": "Average CGPA (/4.0)"}
    )
    st.plotly_chart(fig_age, use_container_width=True)

with row3_col2:
    st.markdown("#### Stress level vs CGPA (bonus factor)")
    fig_stress = px.scatter(
        filtered_df, x="Stress_Level_1_to_10", y="CGPA",
        color="Residence", trendline="ols",
        labels={"Stress_Level_1_to_10": "Stress level (1-10)", "CGPA": "CGPA (/4.0)"}
    )
    st.plotly_chart(fig_stress, use_container_width=True)
    corr_stress = filtered_df["Stress_Level_1_to_10"].corr(filtered_df["CGPA"])
    st.caption(f"Correlation coefficient: {corr_stress:.2f}")

st.markdown("---")

# ----------------------------------------------------------------------------
# EXPLICIT PAGE NAVIGATION (in addition to the sidebar nav)
# ----------------------------------------------------------------------------
st.markdown("#### Continue exploring")
nav_col1, nav_col2 = st.columns(2)
with nav_col1:
    st.page_link("app.py", label="📊 Back to Overview", use_container_width=True)
with nav_col2:
    st.page_link("pages/2_Predictive_Visualization.py", label="🔮 Go to Predictive Visualization", use_container_width=True)
