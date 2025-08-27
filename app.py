# Importing Required Libraries

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# Page Configuration

st.set_page_config(
    page_title="Railway Journeys Dashboard",
    layout="wide"
)


# Load Dataset

@st.cache_data
def load_data():
    df = pd.read_csv("railway_cleaned.csv", parse_dates=["Date of Journey"])
    return df

df = load_data()

st.title("Railway Data Analysis Dashboard") 

# Sidebar Filters

st.sidebar.header("Filters")

# Filter by date range
min_date, max_date = df["Date of Journey"].min(), df["Date of Journey"].max()
date_range = st.sidebar.date_input("Select Journey Date Range", [min_date, max_date])

# Filter by hour (AM/PM)
hours = ["All"] + sorted(df["Hour_AM_PM"].dropna().unique())
selected_hours = st.sidebar.multiselect("Select Hours", options=hours, default="All")

# Filter by day of week
days = ["All"] + list(df["Day_of_Week"].dropna().unique())
selected_days = st.sidebar.multiselect("Select Days", options=days, default="All")

# Filter by departure station
departures = ["All"] + sorted(df["Departure Station"].dropna().unique())
selected_departures = st.sidebar.multiselect("Departure Station", options=departures, default="All")

# Filter by arrival station
arrivals = ["All"] + sorted(df["Arrival Destination"].dropna().unique())
selected_arrivals = st.sidebar.multiselect("Arrival Station", options=arrivals, default="All")


# Apply Filters to Data

filtered_df = df.copy()

if date_range:
    filtered_df = filtered_df[
        (filtered_df["Date of Journey"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["Date of Journey"] <= pd.to_datetime(date_range[1]))
    ]

if "All" not in selected_hours:
    filtered_df = filtered_df[filtered_df["Hour_AM_PM"].isin(selected_hours)]

if "All" not in selected_days:
    filtered_df = filtered_df[filtered_df["Day_of_Week"].isin(selected_days)]

if "All" not in selected_departures:
    filtered_df = filtered_df[filtered_df["Departure Station"].isin(selected_departures)]

if "All" not in selected_arrivals:
    filtered_df = filtered_df[filtered_df["Arrival Destination"].isin(selected_arrivals)]


# KPIs at Top

total_journeys = len(filtered_df)
total_revenue = filtered_df["Price"].sum()
total_delayed = filtered_df["Is_Delayed"].sum()
total_cancelled = filtered_df["Is_Cancelled"].sum()
filtered_df["Refund Request"] = filtered_df["Refund Request"].map({"Yes": 1, "No": 0})
total_refund = filtered_df["Refund Request"].sum()


col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Journeys", f"{total_journeys:,}")
col2.metric("Total Revenue", f"${int(total_revenue):,}")
col3.metric("Delayed Journeys", f"{total_delayed:,}")
col4.metric("Cancelled Journeys", f"{total_cancelled:,}")
col5.metric("Refund Requests", f"{total_refund:,}")


# Tabs for Analysis

tabs = st.tabs([
    "Popular Routes",
    "Travel Peaks",
    "Delays",
    "Cancellations",
    "Revenue Overview"   
])


# 1️⃣ Popular Routes Tab

with tabs[0]:
    st.subheader("Top 10 Most Popular Routes")
    popular_routes = filtered_df["Route"].value_counts().head(10)
    fig = px.bar(
        x=popular_routes.values,
        y=popular_routes.index,
        orientation="h",
        color=popular_routes.values)
       # color_continuous_scale="Blues")
       # color_continuous_scale="Blues",)
    fig.update_layout(
    xaxis_title=None,
    yaxis_title=None)
    st.plotly_chart(fig, use_container_width=True)



# 2️⃣ Travel Peaks Tab

with tabs[1]:
    st.subheader("Journeys by Hour")
    hour_counts = filtered_df.groupby("Hour_AM_PM").size().reset_index(name="Journeys")
    fig_hour = px.line(hour_counts, x="Hour_AM_PM", y="Journeys", markers=True)
    fig_hour.update_layout(
    xaxis_title=None,
    yaxis_title=None)
    st.plotly_chart(fig_hour, use_container_width=True)

    st.subheader("Journeys by Day of Week")
    day_counts = filtered_df["Day_of_Week"].value_counts().reindex([
        "Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"])
    fig_day = px.bar(
        x=day_counts.index,
        y=day_counts.values,
        color=day_counts.values,
        color_continuous_scale="Blues")
    fig_day.update_layout(
    xaxis_title=None,
    yaxis_title=None)
    st.plotly_chart(fig_day, use_container_width=True)

    st.subheader("Journeys per Month")
    monthly_counts = filtered_df.groupby("Month").size().reset_index(name="Journeys")
    fig_month = px.bar(monthly_counts, x="Month", y="Journeys", color="Journeys", color_continuous_scale="Teal")
    fig_month.update_layout(
    xaxis_title=None,
    yaxis_title=None)
    st.plotly_chart(fig_month, use_container_width=True)


# 3️⃣  Delayed Tab

with tabs[2]:
    st.subheader("Top Reasons for Delayed Journeys")
    delayed= filtered_df[filtered_df["Is_Delayed"] == True]
    delayed_reasons = delayed["Reason_for_Delay"].value_counts()
    fig_delayed = px.bar(
        x=delayed_reasons.values,
        y=delayed_reasons.index,
        orientation="h",
        color=delayed_reasons.values,
        color_continuous_scale="Blues")
    fig_delayed.update_layout(
    xaxis_title=None,
    yaxis_title=None)
    
    st.plotly_chart(fig_delayed, use_container_width=True)


# 4️⃣ Cancellations Tab

with tabs[3]:
    st.subheader("Top Reasons for Cancelled Journeys")
    cancelled = filtered_df[filtered_df["Is_Cancelled"] == True]
    cancel_reasons = cancelled["Reason_for_Delay"].value_counts()
    fig_cancel = px.bar(
        x=cancel_reasons.values,
        y=cancel_reasons.index,
        orientation="h",
        color=cancel_reasons.values,
        color_continuous_scale="Blues")
    
    fig_cancel.update_layout(
    xaxis_title=None,
    yaxis_title=None)
    
    st.plotly_chart(fig_cancel, use_container_width=True)



 # 5️⃣ Revenue Overview Tab

with tabs[4]:
    st.subheader("Revenue by Ticket Type & Class")
    revenue_pivot = filtered_df.pivot_table(
        index="Ticket Type",
        columns="Ticket Class",
        values="Price",
        aggfunc="sum"
    ).fillna(0)

    fig_revenue = go.Figure()
    for cls in revenue_pivot.columns:
        fig_revenue.add_trace(go.Bar(
            x=revenue_pivot.index,
            y=revenue_pivot[cls],
            name=cls
        ))

    fig_revenue.update_layout(
    xaxis_title=None,
    yaxis_title=None)
    st.plotly_chart(fig_revenue, use_container_width=True)