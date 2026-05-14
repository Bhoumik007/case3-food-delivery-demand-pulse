"""
Case 3 · Food Delivery Demand Pulse
Streamlit Dashboard for Operations Leadership

Author: Bhoumik Parmar
Purpose: Interactive analytics dashboard translating 90 days of order data into
         actionable surge-pricing policy recommendations for the Ops Head.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta

# ─────────────────────────────────────────────
# PAGE CONFIG & STYLING
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Demand Pulse · Food Delivery Ops",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    h1 { font-size: 1.8rem !important; }
    h2 { font-size: 1.3rem !important; color: #1a1a2e; }
    h3 { font-size: 1.1rem !important; }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px; padding: 1rem; border-left: 4px solid #0d6efd;
    }
    .insight-box {
        background: #fff3cd; border-radius: 8px; padding: 0.8rem;
        border-left: 4px solid #ffc107; margin: 0.5rem 0;
    }
    .rec-box {
        background: #d1e7dd; border-radius: 8px; padding: 0.8rem;
        border-left: 4px solid #198754; margin: 0.5rem 0;
    }
    div[data-testid="stMetric"] {
        background-color: #f8f9fa; border-radius: 8px;
        padding: 0.8rem; border-left: 3px solid #0d6efd;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA LOADING & PREPROCESSING
# ─────────────────────────────────────────────
@st.cache_data
def load_and_preprocess():
    df = pd.read_csv("case3_food_delivery_orders.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    df['hour'] = df['timestamp'].dt.hour
    df['dow'] = df['timestamp'].dt.dayofweek
    df['dow_name'] = df['timestamp'].dt.day_name()
    df['is_weekend'] = df['dow'].isin([5, 6])
    df['week'] = df['timestamp'].dt.isocalendar().week.astype(int)
    df['month'] = df['timestamp'].dt.month
    df['revenue'] = df['order_value']  # alias for clarity

    # Time buckets for readability
    bins = [-1, 5, 11, 14, 17, 21, 24]
    labels = ['Late Night (12-5am)', 'Morning (6-11am)', 'Lunch (12-2pm)',
              'Afternoon (3-5pm)', 'Dinner (6-9pm)', 'Late Evening (10pm-12am)']
    df['time_bucket'] = pd.cut(df['hour'], bins=bins, labels=labels)

    # Peak flag
    df['is_peak'] = df['hour'].isin([12, 13, 19, 20, 21])
    return df


@st.cache_data
def build_forecast(df):
    """Trend + day-of-week seasonal decomposition forecast."""
    daily = df.groupby('date').agg(orders=('order_id', 'count')).reset_index()
    daily['date'] = pd.to_datetime(daily['date'])
    daily['dow'] = daily['date'].dt.dayofweek

    x = np.arange(len(daily))
    coeffs = np.polyfit(x, daily['orders'].values, 1)
    trend = np.polyval(coeffs, x)

    detrended = daily['orders'].values - trend
    dow_effect = pd.Series(detrended).groupby(daily['dow']).mean()

    seasonal = daily['dow'].map(dow_effect).values
    residual = detrended - seasonal
    residual_std = np.std(residual)

    # Forecast next 7 days
    last_date = daily['date'].max()
    forecast_dates = pd.date_range(last_date + timedelta(days=1), periods=7)
    forecast_x = np.arange(len(daily), len(daily) + 7)
    forecast_trend = np.polyval(coeffs, forecast_x)
    forecast_dow = np.array([dow_effect[d.dayofweek] for d in forecast_dates])
    forecast_orders = forecast_trend + forecast_dow

    ci_lower = forecast_orders - 1.96 * residual_std
    ci_upper = forecast_orders + 1.96 * residual_std

    forecast_df = pd.DataFrame({
        'date': forecast_dates,
        'predicted_orders': forecast_orders.round(0).astype(int),
        'ci_lower': ci_lower.round(0).astype(int),
        'ci_upper': ci_upper.round(0).astype(int),
        'day': [d.day_name() for d in forecast_dates]
    })

    # Also return historical daily for plotting
    daily['trend'] = trend
    daily['fitted'] = trend + seasonal
    return forecast_df, daily, coeffs, residual_std


df = load_and_preprocess()
forecast_df, daily_ts, trend_coeffs, residual_std = build_forecast(df)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.title("🎛️ Filters")
selected_cities = st.sidebar.multiselect(
    "Cities",
    options=sorted(df['city'].unique()),
    default=sorted(df['city'].unique())
)
selected_cuisines = st.sidebar.multiselect(
    "Cuisines",
    options=sorted(df['cuisine'].unique()),
    default=sorted(df['cuisine'].unique())
)
day_type = st.sidebar.radio("Day Type", ["All", "Weekday", "Weekend"])

# Apply filters
filtered = df[df['city'].isin(selected_cities) & df['cuisine'].isin(selected_cuisines)]
if day_type == "Weekday":
    filtered = filtered[~filtered['is_weekend']]
elif day_type == "Weekend":
    filtered = filtered[filtered['is_weekend']]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("📊 Demand Pulse — Food Delivery Operations Intelligence")
st.caption("90-day order analysis (Jan–Mar 2025) · 7 cities · 50,000 orders · Built for the Ops Head")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Executive Summary",
    "🕐 Demand Patterns",
    "⚡ Surge Analysis",
    "🔮 7-Day Forecast",
    "🎯 Recommendations"
])

# ═══════════════════════════════════════════════
# TAB 1: EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════
with tab1:
    st.header("Executive Summary")

    # Top-line KPIs
    n_days = filtered['date'].nunique()
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Orders", f"{len(filtered):,}")
    with col2:
        st.metric("Daily Average", f"{len(filtered) / n_days:.0f}")
    with col3:
        st.metric("Total Revenue", f"₹{filtered['revenue'].sum():,.0f}")
    with col4:
        st.metric("Avg Order Value", f"₹{filtered['revenue'].mean():.0f}")
    with col5:
        st.metric("Surge Rate", f"{filtered['surge_applied'].mean():.1%}")

    st.divider()

    # Headline insight
    st.markdown("""
    <div class="insight-box">
    <strong>🔑 Headline Finding:</strong> Surge pricing is over-applied during weekends
    and under-optimised for the dinner ramp-up. Weekend dinner surge rate is <strong>72%</strong>
    vs weekday <strong>45%</strong> — despite near-identical order volumes. The company is
    overpaying riders by ~₹22K every 90 days on weekend dinner alone. Off-peak hours carry
    a 5.4% surge rate that serves no operational purpose — another ₹30K in waste per quarter.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # Revenue by city
    col_a, col_b = st.columns(2)
    with col_a:
        city_rev = filtered.groupby('city').agg(
            revenue=('revenue', 'sum'),
            orders=('order_id', 'count')
        ).sort_values('revenue', ascending=True).reset_index()

        fig = px.bar(city_rev, x='revenue', y='city', orientation='h',
                     color='revenue', color_continuous_scale='Blues',
                     title="Revenue by City (90 Days)")
        fig.update_layout(showlegend=False, coloraxis_showscale=False,
                          height=350, margin=dict(l=0, r=0, t=40, b=0),
                          yaxis_title="", xaxis_title="Revenue (₹)")
        fig.update_traces(text=[f"₹{v / 1e5:.1f}L" for v in city_rev['revenue']],
                          textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        cuisine_orders = filtered.groupby('cuisine')['order_id'].count().sort_values(
            ascending=True).reset_index()
        cuisine_orders.columns = ['cuisine', 'orders']

        fig = px.bar(cuisine_orders, x='orders', y='cuisine', orientation='h',
                     color='orders', color_continuous_scale='Oranges',
                     title="Order Volume by Cuisine (90 Days)")
        fig.update_layout(showlegend=False, coloraxis_showscale=False,
                          height=350, margin=dict(l=0, r=0, t=40, b=0),
                          yaxis_title="", xaxis_title="Orders")
        fig.update_traces(text=[f"{v:,}" for v in cuisine_orders['orders']],
                          textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    # Daily trend
    daily_filtered = filtered.groupby('date').agg(
        orders=('order_id', 'count'),
        revenue=('revenue', 'sum')
    ).reset_index()
    daily_filtered['date'] = pd.to_datetime(daily_filtered['date'])
    daily_filtered['7d_ma'] = daily_filtered['orders'].rolling(7, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_filtered['date'], y=daily_filtered['orders'],
                             mode='lines', name='Daily Orders',
                             line=dict(color='#adb5bd', width=1), opacity=0.6))
    fig.add_trace(go.Scatter(x=daily_filtered['date'], y=daily_filtered['7d_ma'],
                             mode='lines', name='7-Day Moving Average',
                             line=dict(color='#0d6efd', width=2.5)))
    fig.update_layout(title="Daily Order Volume with 7-Day Moving Average",
                      height=300, margin=dict(l=0, r=0, t=40, b=0),
                      xaxis_title="", yaxis_title="Orders",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════
# TAB 2: DEMAND PATTERNS
# ═══════════════════════════════════════════════
with tab2:
    st.header("When Does Demand Actually Spike?")

    # Hourly heatmap by day of week
    hour_dow = filtered.groupby(['dow_name', 'hour']).size().reset_index(name='orders')
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hour_dow['dow_name'] = pd.Categorical(hour_dow['dow_name'], categories=dow_order, ordered=True)
    pivot = hour_dow.pivot(index='dow_name', columns='hour', values='orders').fillna(0)

    fig = px.imshow(pivot, color_continuous_scale='YlOrRd',
                    labels=dict(x="Hour of Day", y="Day of Week", color="Orders"),
                    title="Demand Heatmap: Day of Week × Hour",
                    aspect='auto')
    fig.update_layout(height=350, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    <strong>📌 Pattern:</strong> Two clear demand peaks — <strong>Lunch (12–1pm)</strong> and
    <strong>Dinner (7–9pm)</strong> — are consistent across all 7 days. Dinner peak is ~20% larger
    than lunch. The pattern holds across all cities. No day-of-week shows a materially different shape.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        # Hourly demand curve with peak zones highlighted
        hourly = filtered.groupby('hour').agg(
            orders=('order_id', 'count'),
            avg_delivery=('delivery_time_min', 'mean')
        ).reset_index()

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Peak zone shading
        for start, end in [(11.5, 13.5), (18.5, 21.5)]:
            fig.add_vrect(x0=start, x1=end, fillcolor="#ffc107", opacity=0.15,
                          line_width=0)
        fig.add_trace(go.Bar(x=hourly['hour'], y=hourly['orders'],
                             name='Orders', marker_color='#0d6efd', opacity=0.7))
        fig.add_trace(go.Scatter(x=hourly['hour'], y=hourly['avg_delivery'],
                                 name='Avg Delivery (min)', line=dict(color='#dc3545', width=2)),
                      secondary_y=True)
        fig.update_layout(title="Hourly Demand + Delivery Time",
                          height=380, margin=dict(l=0, r=0, t=40, b=0),
                          xaxis_title="Hour of Day",
                          legend=dict(orientation="h", yanchor="bottom", y=1.02))
        fig.update_yaxes(title_text="Orders", secondary_y=False)
        fig.update_yaxes(title_text="Delivery Time (min)", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # City-level hourly comparison
        city_hourly = filtered.groupby(['city', 'hour']).size().reset_index(name='orders')
        n_days_per_city = filtered.groupby('city')['date'].nunique().reset_index()
        n_days_per_city.columns = ['city', 'n_days']
        city_hourly = city_hourly.merge(n_days_per_city, on='city')
        city_hourly['orders_per_day'] = city_hourly['orders'] / city_hourly['n_days']

        fig = px.line(city_hourly, x='hour', y='orders_per_day', color='city',
                      title="Hourly Demand by City (Orders/Day)",
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=380, margin=dict(l=0, r=0, t=40, b=0),
                          xaxis_title="Hour of Day", yaxis_title="Orders per Day",
                          legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, use_container_width=True)

    # Weekend vs Weekday comparison
    st.subheader("Weekend vs Weekday Demand Shape")
    wk_compare = filtered.groupby(['is_weekend', 'hour']).agg(
        orders=('order_id', 'count')
    ).reset_index()
    n_wkday = filtered[~filtered['is_weekend']]['date'].nunique()
    n_wknd = filtered[filtered['is_weekend']]['date'].nunique()
    wk_compare['orders_per_day'] = wk_compare.apply(
        lambda r: r['orders'] / n_wknd if r['is_weekend'] else r['orders'] / n_wkday, axis=1
    )
    wk_compare['type'] = wk_compare['is_weekend'].map({False: 'Weekday', True: 'Weekend'})

    fig = px.line(wk_compare, x='hour', y='orders_per_day', color='type',
                  color_discrete_map={'Weekday': '#0d6efd', 'Weekend': '#dc3545'},
                  title="Weekday vs Weekend: Almost Identical Demand Shape")
    fig.update_layout(height=320, margin=dict(l=0, r=0, t=40, b=0),
                      xaxis_title="Hour of Day", yaxis_title="Orders per Day",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    <strong>⚠️ Key Insight:</strong> Weekend and weekday demand shapes are virtually identical
    (~160 orders/day at dinner peak for both). Yet surge policy treats weekends very differently —
    see the <strong>Surge Analysis</strong> tab for the cost implications.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# TAB 3: SURGE ANALYSIS
# ═══════════════════════════════════════════════
with tab3:
    st.header("Surge Pricing: Where the Money Leaks")
    st.caption("Surge should correlate with demand. It doesn't — at least not on weekends.")

    # Surge vs Demand overlay
    hourly_surge = filtered.groupby('hour').agg(
        demand_share=('order_id', 'count'),
        surge_rate=('surge_applied', 'mean')
    ).reset_index()
    hourly_surge['demand_share'] = hourly_surge['demand_share'] / hourly_surge['demand_share'].sum() * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=hourly_surge['hour'], y=hourly_surge['demand_share'],
                         name='Demand Share (%)', marker_color='#0d6efd', opacity=0.5))
    fig.add_trace(go.Scatter(x=hourly_surge['hour'], y=hourly_surge['surge_rate'] * 100,
                             name='Surge Rate (%)', line=dict(color='#dc3545', width=3)),
                  secondary_y=True)
    fig.update_layout(title="Demand Share vs Surge Rate by Hour",
                      height=380, margin=dict(l=0, r=0, t=40, b=0),
                      xaxis_title="Hour of Day",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02))
    fig.update_yaxes(title_text="Demand Share (%)", secondary_y=False)
    fig.update_yaxes(title_text="Surge Rate (%)", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

    # The Weekend Surge Problem
    st.subheader("The Weekend Over-Surge Problem")
    col1, col2, col3 = st.columns(3)

    wkday_dinner = filtered[(~filtered['is_weekend']) & (filtered['hour'].isin([19, 20, 21]))]
    wknd_dinner = filtered[(filtered['is_weekend']) & (filtered['hour'].isin([19, 20, 21]))]

    with col1:
        st.metric("Weekday Dinner Surge", f"{wkday_dinner['surge_applied'].mean():.0%}")
        st.caption(f"{len(wkday_dinner):,} orders across {wkday_dinner['date'].nunique()} days")
    with col2:
        st.metric("Weekend Dinner Surge", f"{wknd_dinner['surge_applied'].mean():.0%}",
                  delta=f"+{(wknd_dinner['surge_applied'].mean() - wkday_dinner['surge_applied'].mean()) * 100:.0f}pp vs weekday",
                  delta_color="inverse")
        st.caption(f"{len(wknd_dinner):,} orders across {wknd_dinner['date'].nunique()} days")
    with col3:
        excess = int(wknd_dinner['surge_applied'].sum() -
                     len(wknd_dinner) * wkday_dinner['surge_applied'].mean())
        SURGE_PREMIUM = 20
        st.metric("Excess Surged Orders (90d)", f"{excess:,}",
                  delta=f"₹{excess * SURGE_PREMIUM:,} wasted",
                  delta_color="inverse")
        st.caption("If weekend matched weekday surge rate")

    # Surge rate comparison chart
    surge_compare = filtered.groupby(['is_weekend', 'hour']).agg(
        surge_rate=('surge_applied', 'mean')
    ).reset_index()
    surge_compare['type'] = surge_compare['is_weekend'].map({False: 'Weekday', True: 'Weekend'})

    fig = px.line(surge_compare, x='hour', y='surge_rate', color='type',
                  color_discrete_map={'Weekday': '#0d6efd', 'Weekend': '#dc3545'},
                  title="Surge Rate: Weekend vs Weekday (Same Demand, Different Pricing)")
    fig.update_layout(height=350, margin=dict(l=0, r=0, t=40, b=0),
                      xaxis_title="Hour of Day",
                      yaxis_title="Surge Rate",
                      yaxis_tickformat='.0%',
                      legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig, use_container_width=True)

    # Off-peak surge
    st.subheader("Off-Peak Surge Waste")
    off_peak_hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16, 17, 22, 23]
    offpeak = filtered[filtered['hour'].isin(off_peak_hours)]
    offpeak_surged = offpeak[offpeak['surge_applied'] == 1]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Off-Peak Surged Orders (90d)", f"{len(offpeak_surged):,}")
        st.metric("Off-Peak Surge Rate", f"{offpeak['surge_applied'].mean():.1%}")
    with col2:
        st.metric("Wasted Surge Cost (90d)", f"₹{len(offpeak_surged) * SURGE_PREMIUM:,}")
        st.metric("Annualised Waste", f"₹{len(offpeak_surged) * SURGE_PREMIUM * 4:,}")

    # The Hour 18 transition problem
    st.subheader("The Pre-Dinner Blind Spot: Hour 18")
    h18 = filtered[filtered['hour'] == 18]
    h19 = filtered[filtered['hour'] == 19]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Hour 18 Orders", f"{len(h18):,}")
        st.metric("Hour 18 Surge", f"{h18['surge_applied'].mean():.1%}")
    with col2:
        st.metric("Hour 19 Orders", f"{len(h19):,}")
        st.metric("Hour 19 Surge", f"{h19['surge_applied'].mean():.1%}")
    with col3:
        st.metric("Demand Jump", f"+{(len(h19) - len(h18)) / len(h18) * 100:.0f}%")
        st.metric("Delivery Time Jump", f"+{h19['delivery_time_min'].mean() - h18['delivery_time_min'].mean():.0f} min")

    st.markdown("""
    <div class="insight-box">
    <strong>📌 The Transition Problem:</strong> Demand jumps <strong>52%</strong> from 6pm to 7pm
    while surge rate jumps <strong>815%</strong>. This is reactive, not predictive. If riders were
    pre-positioned at 5–6pm based on the predictable dinner ramp, the 7pm surge spike could be
    reduced significantly — cutting both rider costs and delivery times.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# TAB 4: 7-DAY FORECAST
# ═══════════════════════════════════════════════
with tab4:
    st.header("7-Day Demand Forecast (April 1–7, 2025)")
    st.caption("Trend + Day-of-Week Seasonal Decomposition · 95% Confidence Interval")

    # Forecast chart
    fig = go.Figure()

    # Historical
    fig.add_trace(go.Scatter(x=daily_ts['date'], y=daily_ts['orders'],
                             mode='lines', name='Actual Orders',
                             line=dict(color='#adb5bd', width=1), opacity=0.5))
    fig.add_trace(go.Scatter(x=daily_ts['date'], y=daily_ts['fitted'],
                             mode='lines', name='Fitted (Trend + Seasonal)',
                             line=dict(color='#0d6efd', width=1.5, dash='dot')))

    # Forecast CI band
    fig.add_trace(go.Scatter(
        x=list(forecast_df['date']) + list(forecast_df['date'][::-1]),
        y=list(forecast_df['ci_upper']) + list(forecast_df['ci_lower'][::-1]),
        fill='toself', fillcolor='rgba(13,110,253,0.15)',
        line=dict(width=0), name='95% CI', showlegend=True
    ))
    # Forecast line
    fig.add_trace(go.Scatter(x=forecast_df['date'], y=forecast_df['predicted_orders'],
                             mode='lines+markers', name='Forecast',
                             line=dict(color='#dc3545', width=2.5),
                             marker=dict(size=8)))

    fig.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0),
                      title="90-Day Historical + 7-Day Forecast",
                      xaxis_title="", yaxis_title="Daily Orders",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig, use_container_width=True)

    # Forecast table
    st.subheader("Forecast Detail")
    display_fc = forecast_df[['date', 'day', 'predicted_orders', 'ci_lower', 'ci_upper']].copy()
    display_fc.columns = ['Date', 'Day', 'Predicted Orders', '95% CI Lower', '95% CI Upper']
    display_fc['Date'] = display_fc['Date'].dt.strftime('%Y-%m-%d')
    st.dataframe(display_fc, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Week Total Forecast", f"{forecast_df['predicted_orders'].sum():,} orders")
        st.metric("Avg Daily Forecast", f"{forecast_df['predicted_orders'].mean():.0f} orders")
    with col2:
        weekly_rev_est = forecast_df['predicted_orders'].sum() * df['revenue'].mean()
        st.metric("Est. Weekly Revenue", f"₹{weekly_rev_est:,.0f}")
        st.metric("Forecast Uncertainty (±)", f"{1.96 * residual_std:.0f} orders/day")

    # Model performance note
    st.markdown("""
    <div class="insight-box">
    <strong>📊 Forecast Methodology:</strong> Linear trend + day-of-week seasonal adjustment.
    The trend is essentially flat (−0.13 orders/day), so demand is stable and predictable.
    Day-of-week effects are small (±9 orders). Residual standard deviation is 22.7 orders,
    giving a 95% CI of ±45 orders around the point forecast.<br><br>
    <strong>Production evaluation:</strong> In production, measure forecast accuracy using MAPE
    (Mean Absolute Percentage Error) and track whether actuals fall within the 95% CI at least
    90% of the time. If the product launches new features, campaigns, or enters new geographies,
    the forecast model needs retraining with those covariates.
    </div>
    """, unsafe_allow_html=True)

    # Hourly rider planning view
    st.subheader("Rider Planning: Predicted Hourly Demand for Next Weekday")
    hourly_avg = df[~df['is_weekend']].groupby('hour').size() / df[~df['is_weekend']]['date'].nunique()
    hourly_planning = pd.DataFrame({
        'hour': range(24),
        'expected_orders': [hourly_avg.get(h, 0) for h in range(24)]
    })
    hourly_planning['riders_needed'] = (hourly_planning['expected_orders'] / 3).round(0).astype(int)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=hourly_planning['hour'], y=hourly_planning['riders_needed'],
                         name='Riders Needed (est.)',
                         marker_color=['#dc3545' if h in [12, 13, 19, 20, 21] else '#0d6efd'
                                       for h in range(24)]))
    fig.update_layout(title="Estimated Riders Needed per Hour (Weekday, 3 orders/rider/hour)",
                      height=320, margin=dict(l=0, r=0, t=40, b=0),
                      xaxis_title="Hour of Day", yaxis_title="Riders")
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════
# TAB 5: RECOMMENDATIONS
# ═══════════════════════════════════════════════
with tab5:
    st.header("3 Recommendations for Monday Morning")
    st.caption("Each is actionable, quantified, and tied to a specific data finding.")

    # Rec 1
    st.markdown("""
    <div class="rec-box">
    <h3>🎯 Recommendation 1: Eliminate Off-Peak Surge Entirely</h3>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    **The problem:** 5.4% of orders during off-peak hours (midnight–5am, 6am–11am, 2pm–5pm, 10pm–midnight)
    are triggering surge pricing. There is no supply constraint during these hours — demand is 3–7× lower
    than peak, and delivery times are already at baseline (37 min vs 44 min at peak).

    **The fix:** Set surge threshold to zero for hours outside 12–1pm and 6–9pm windows.
    Hard-code the off-peak block until the team has a dynamic model.

    **Expected impact:**
    - **1,515 fewer surged orders per quarter** (based on 90-day data)
    - **₹30,300 saved per quarter** in unnecessary rider incentives (at ₹20 surge premium per order)
    - **₹1.2L annualised savings** — small but immediate and zero-risk

    **Edge case to watch:** Late-night orders (midnight–5am) in party-heavy cities like Bangalore
    and Mumbai *might* have genuine supply constraints during event nights (NYE, IPL).
    Build an exception list for known high-demand dates rather than a blanket surge.
    """)

    st.divider()

    # Rec 2
    st.markdown("""
    <div class="rec-box">
    <h3>🎯 Recommendation 2: Cap Weekend Dinner Surge at Weekday Levels</h3>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    **The problem:** Weekend dinner (7–9pm) surge rate is **72%** vs weekday dinner at **45%**. But the
    underlying demand is nearly identical — ~160 orders/day at peak for both. The over-surge is a supply
    problem (fewer riders available on weekends), not a demand problem. Paying 72% surge doesn't create
    more riders — it just costs more per existing rider.

    **The fix:** Two-pronged approach:
    1. **Immediate:** Cap weekend dinner surge rate at 50% (still above weekday, acknowledging some
       supply tightness, but 22pp lower than current)
    2. **Next month:** Introduce a weekend shift guarantee bonus (flat ₹200–300/day) to attract
       riders to weekend shifts, reducing the need for reactive surge pricing altogether

    **Expected impact:**
    - **~1,100 fewer surged orders per quarter** (the excess above weekday-equivalent rate)
    - **₹22,260 saved per quarter** in rider over-incentivisation
    - **₹89K annualised savings** — the single largest surge cost lever in the data
    - Shift guarantee bonus at ₹250/day × 26 weekends × estimated 50 riders = ₹3.25L/year investment,
      but expected to reduce weekend surge rate to <40%, saving more than the bonus costs

    **Edge case:** Monitor weekend delivery times after the cap. If p95 delivery time exceeds 70 min,
    the cap is too aggressive — raise to 55% and increase the shift bonus pool.
    """)

    st.divider()

    # Rec 3
    st.markdown("""
    <div class="rec-box">
    <h3>🎯 Recommendation 3: Pre-Position Riders at 5–6pm for the Dinner Ramp</h3>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    **The problem:** Demand jumps 52% from hour 18 (6pm) to hour 19 (7pm), but surge jumps 815% in
    the same window. The system is reactive — it only triggers surge after supply is already exhausted.
    Delivery times spike from 37 min (off-peak) to 44 min (peak), meaning customers are waiting
    ~7 minutes longer at dinner than they need to.

    **The fix:** Use hour 17–18 order velocity as a leading indicator. When 5pm demand exceeds the
    weekly average for that hour, send a push notification to off-duty riders offering a pre-positioned
    dinner bonus (smaller than surge — ₹10–15/order) to come online by 6:30pm. This creates a
    supply buffer before the 7pm spike hits.

    **Expected impact:**
    - **Target: reduce dinner surge rate from 52% to 40%** by absorbing the initial wave with
      pre-positioned supply
    - **₹2.4L annualised savings** (12pp reduction × ~24,500 dinner orders/quarter × ₹20 surge vs
      ₹12 pre-position cost = ₹8/order saved × 24,500 orders × 4 quarters)
    - **Delivery time improvement:** Target p95 dinner delivery under 60 min (currently 65 min)

    **How to validate:** A/B test this in one city first (Bangalore — highest volume). Run for 4 weeks.
    Primary metric: dinner surge rate. Guardrail metrics: rider earnings (should not drop), p95 delivery
    time, rider acceptance rate for pre-position notifications.
    """)

    st.divider()

    # Impact summary
    st.subheader("Combined Impact Summary")
    impact_data = pd.DataFrame({
        'Recommendation': [
            '1. Eliminate off-peak surge',
            '2. Cap weekend dinner surge',
            '3. Pre-position riders for dinner'
        ],
        'Quarterly Savings': ['₹30,300', '₹22,260', '₹60,000 (est.)'],
        'Annualised Savings': ['₹1.2L', '₹89K', '₹2.4L'],
        'Implementation Risk': ['None — pure policy change', 'Low — monitor delivery times',
                                'Medium — requires A/B test'],
        'Time to Implement': ['1 day', '1 week', '4–6 weeks']
    })
    st.dataframe(impact_data, use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="insight-box">
    <strong>💡 Suggested A/B Test Design for Recommendation 3:</strong><br>
    <strong>Hypothesis:</strong> Pre-positioning riders at 5–6pm reduces dinner surge rate without
    degrading delivery times.<br>
    <strong>Test city:</strong> Bangalore (highest volume, most statistical power).<br>
    <strong>Design:</strong> Alternating-day test (pre-position on Mon/Wed/Fri, control on Tue/Thu) for
    4 weeks to avoid spillover effects. Not user-level randomisation — this is a supply-side intervention
    affecting all orders in the city during the test hours.<br>
    <strong>Primary metric:</strong> Dinner surge rate (7–9pm).<br>
    <strong>Secondary:</strong> p95 delivery time, rider earnings, pre-position acceptance rate.<br>
    <strong>Guardrail:</strong> If p95 delivery exceeds 70 min on any test day, pause and investigate.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.divider()
st.caption("Built by Bhoumik Parmar · Case 3: Food Delivery Demand Pulse · Infinia Technologies FutureAI Assessment")
