import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from utils import load_data, render_sidebar_filters

st.set_page_config(
    page_title="Predictive Visualization",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

df = load_data()
filtered_df = render_sidebar_filters(df)

st.title("🔮 Predictive Visualization: Estimate a Student's CGPA")
st.markdown(
    "**Challenge feature: Predictive visualization.** This tool uses the "
    "strongest predictors from the dataset (sleep, study hours, and "
    "attendance) to estimate a likely CGPA (out of 4.0) for a hypothetical "
    "student profile, and plots that estimate against the real class data "
    "so you can see exactly where it falls."
)

# Model is trained on the full dataset (not the sidebar-filtered subset)
# so the prediction tool always has the largest possible sample to learn from.
features = ["Sleep_Hours", "Study_Hours_per_Day", "Attendance_Percentage"]
X = df[features]
y = df["CGPA"]
model = LinearRegression().fit(X, y)

st.markdown("#### Try it yourself")

pred_col1, pred_col2, pred_col3, pred_col4 = st.columns(4)

with pred_col1:
    in_sleep = st.slider("Sleep hours", 3.0, 10.0, 7.0, 0.1)
with pred_col2:
    in_study = st.slider("Study hours/day", 0.0, 9.0, 4.0, 0.1)
with pred_col3:
    in_att = st.slider("Attendance (%)", 50.0, 100.0, 80.0, 0.5)
with pred_col4:
    pred_cgpa = model.predict(pd.DataFrame(
        [[in_sleep, in_study, in_att]], columns=features
    ))[0]
    pred_cgpa = min(max(pred_cgpa, 0), 4.0)
    st.metric("Estimated CGPA (/4.0)", f"{pred_cgpa:.2f}")

st.caption(
    "Model: linear regression on Sleep_Hours, Study_Hours_per_Day, and "
    "Attendance_Percentage. For demonstration purposes — not a substitute "
    "for formal academic advising."
)

st.markdown("---")

# ----------------------------------------------------------------------------
# THE ACTUAL VISUALIZATION: where does this hypothetical student land?
# ----------------------------------------------------------------------------
st.markdown("#### Where this student falls against the class")
st.markdown(
    "Sleep hours is the strongest single predictor of CGPA in this dataset, "
    "so the chart below plots every student on that axis. The trend line shows "
    "the model's fitted relationship, and the highlighted point shows your "
    "hypothetical student's predicted position based on all three sliders above."
)

# Simple 1D view on the strongest predictor (Sleep_Hours), holding study hours
# and attendance at the slider's chosen values, so the trend line reflects
# the same multi-factor model used for the prediction above.
sleep_range = np.linspace(df["Sleep_Hours"].min(), df["Sleep_Hours"].max(), 100)
trend_input = pd.DataFrame({
    "Sleep_Hours": sleep_range,
    "Study_Hours_per_Day": in_study,
    "Attendance_Percentage": in_att
})[features]
trend_cgpa = model.predict(trend_input)
trend_cgpa = np.clip(trend_cgpa, 0, 4.0)

fig_pred = go.Figure()

# All actual students (the real data points)
fig_pred.add_trace(go.Scatter(
    x=df["Sleep_Hours"], y=df["CGPA"],
    mode="markers",
    marker=dict(size=6, color="#9CA3AF", opacity=0.5),
    name="Actual students"
))

# Fitted trend line at the chosen study hours / attendance
fig_pred.add_trace(go.Scatter(
    x=sleep_range, y=trend_cgpa,
    mode="lines",
    line=dict(color="#1D9E75", width=3),
    name="Model trend (at chosen study hrs & attendance)"
))

# The hypothetical student, highlighted
fig_pred.add_trace(go.Scatter(
    x=[in_sleep], y=[pred_cgpa],
    mode="markers",
    marker=dict(size=18, color="#D85A30", symbol="star", line=dict(width=2, color="white")),
    name="Your hypothetical student"
))

fig_pred.update_layout(
    xaxis_title="Sleep hours per day",
    yaxis_title="CGPA (/4.0)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
)
st.plotly_chart(fig_pred, use_container_width=True)

st.markdown("---")

# ----------------------------------------------------------------------------
# EXPLICIT PAGE NAVIGATION (in addition to the sidebar nav)
# ----------------------------------------------------------------------------
st.markdown("#### Continue exploring")
nav_col1, nav_col2 = st.columns(2)
with nav_col1:
    st.page_link("app.py", label="📊 Back to Overview", use_container_width=True)
with nav_col2:
    st.page_link("pages/1_Factors_Analysis.py", label="🔍 Back to Factors Analysis", use_container_width=True)
