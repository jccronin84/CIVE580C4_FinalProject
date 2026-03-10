"""
Data Center Water Risk Dashboard — single-file app with sidebar navigation.
"""
import html
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import get_metric_columns, inject_css, setup_sidebar

# Monochromatic grayscale palette for City Comparison (one shade per metric)
METRIC_COLORS = [
    "#FFFFFF",
    "#CCCCCC",
    "#999999",
    "#666666",
    "#444444",
    "#2A2A2A",
]

st.set_page_config(
    page_title="Data Center Water Risk Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# Navigation at top of sidebar
section = st.sidebar.radio(
    "Navigate",
    options=["Dashboard", "Overview Chart", "City Comparison", "Cooling Cost Analysis"],
)
setup_sidebar()

df = st.session_state.get("df")
df_cooling = st.session_state.get("df_cooling")

# -----------------------------------------------------------------------------
# Dashboard
# -----------------------------------------------------------------------------
if section == "Dashboard":
    st.title("Data Center Water Risk Dashboard")
    st.markdown(
        "A decision-support tool for evaluating US cities for data center facility placement "
        "based on water risk and climate data."
    )
    if df is not None and not df.empty:
        st.subheader("City Data")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info(
            "No data loaded. Add **Final.Project.Data.xlsx** to this folder."
        )

    # Cooling Cost Data Overview (only when cooling data is loaded)
    if df_cooling is not None and not df_cooling.empty:
        st.subheader("Cooling Cost Data Overview")

        elec_col_cc = "Total Electricity Cost ($/year)"
        water_col_cc = "Total Water Cost ($/year)"
        city_col_cc = "City"
        type_col_cc = "Data Center Type"

        # Metric card styling (dark theme)
        st.markdown(
            """
            <style>
            div[data-testid="stMetric"] {
                background-color: #141414 !important;
                color: #F5F5F5 !important;
                border: 1px solid #2E2E2E !important;
                padding: 1rem !important;
                border-radius: 4px !important;
            }
            div[data-testid="stMetric"] label { color: #F5F5F5 !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Use only AI/ML Cluster rows for summary metrics (complete data)
        df_aml = df_cooling[df_cooling[type_col_cc].astype(str).str.strip() == "AI/ML Cluster"].copy()
        if not df_aml.empty and elec_col_cc in df_aml.columns and water_col_cc in df_aml.columns:
            idx_elec_high = df_aml[elec_col_cc].idxmax()
            idx_elec_low = df_aml[elec_col_cc].idxmin()
            idx_water_high = df_aml[water_col_cc].idxmax()
            idx_water_low = df_aml[water_col_cc].idxmin()
            row_elec_high = df_aml.loc[idx_elec_high]
            row_elec_low = df_aml.loc[idx_elec_low]
            row_water_high = df_aml.loc[idx_water_high]
            row_water_low = df_aml.loc[idx_water_low]
            m1, m2 = st.columns(2)
            with m1:
                st.metric(
                    "Highest Total Electricity Cost",
                    f"${float(row_elec_high[elec_col_cc]):,.2f}",
                    row_elec_high[city_col_cc],
                )
            with m2:
                st.metric(
                    "Lowest Total Electricity Cost",
                    f"${float(row_elec_low[elec_col_cc]):,.2f}",
                    row_elec_low[city_col_cc],
                )
            m3, m4 = st.columns(2)
            with m3:
                st.metric(
                    "Highest Total Water Cost",
                    f"${float(row_water_high[water_col_cc]):,.2f}",
                    row_water_high[city_col_cc],
                )
            with m4:
                st.metric(
                    "Lowest Total Water Cost",
                    f"${float(row_water_low[water_col_cc]):,.2f}",
                    row_water_low[city_col_cc],
                )

        # Table: forward fill City, drop first (category) column, format numerics to 2 decimals
        df_cooling_show = df_cooling.copy()
        df_cooling_show[city_col_cc] = df_cooling_show[city_col_cc].ffill()
        df_cooling_show = df_cooling_show.iloc[:, 1:]
        numeric_cols = df_cooling_show.select_dtypes(include=["number"]).columns.tolist()
        for c in numeric_cols:
            df_cooling_show[c] = df_cooling_show[c].round(2)
        st.dataframe(df_cooling_show, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# Overview Chart
# -----------------------------------------------------------------------------
elif section == "Overview Chart":
    st.title("Overview Chart")
    st.markdown("Compare all cities on a single metric. Cities are sorted alphabetically on the X-axis.")

    if df is None or df.empty:
        st.warning("No data loaded. Ensure Final.Project.Data.xlsx is in the app folder.")
    else:
        city_col = df.columns[0]
        metrics = get_metric_columns(df)
        if not metrics:
            st.warning("No metric columns found in the data.")
        else:
            selected_metric = st.selectbox("Select metric (Y-axis)", options=metrics, key="overview_metric")

            plot_df = df.sort_values(by=city_col).copy()
            cities = plot_df[city_col].tolist()
            values = plot_df[selected_metric].tolist()
            avg_val = plot_df[selected_metric].mean()

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=cities,
                    y=values,
                    mode="markers",
                    marker=dict(size=10, color="#FFFFFF", line=dict(width=1, color="#555555")),
                    hovertemplate="<b>%{x}</b><br>" + selected_metric + ": %{y}<extra></extra>",
                    name="Cities",
                )
            )
            fig.add_hline(
                y=avg_val,
                line_dash="dash",
                line_color="#000000",
                annotation_text=f"Average: {avg_val:.2f}",
                annotation_position="right",
                annotation_font=dict(color="#000000", size=11),
            )
            fig.update_layout(
                template="plotly_white",
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(family="Space Grotesk, sans-serif", color="#000000", size=12),
                xaxis=dict(
                    title=dict(text="City", font=dict(color="#000000")),
                    tickangle=-45,
                    showgrid=True,
                    gridcolor="#E0E0E0",
                    zeroline=True,
                    linecolor="#000000",
                    tickfont=dict(color="#000000"),
                ),
                yaxis=dict(
                    title=dict(text=selected_metric, font=dict(color="#000000")),
                    showgrid=True,
                    gridcolor="#E0E0E0",
                    zeroline=True,
                    linecolor="#000000",
                    tickfont=dict(color="#000000"),
                ),
                margin=dict(b=120),
                showlegend=False,
                height=500,
                hoverlabel=dict(
                    bgcolor="#FFFFFF",
                    font=dict(color="#000000", size=12),
                    bordercolor="#E0E0E0",
                ),
            )
            st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# City Comparison
# -----------------------------------------------------------------------------
elif section == "City Comparison":
    st.title("City Comparison")
    st.markdown("Select up to 4 cities and up to 6 metrics to compare side by side.")

    if df is None or df.empty:
        st.warning("No data loaded. Ensure Final.Project.Data.xlsx is in the app folder.")
    else:
        city_col = df.columns[0]
        metrics = get_metric_columns(df)
        cities_all = df[city_col].dropna().astype(str).str.strip().unique().tolist()
        cities_all.sort()

        if not metrics or not cities_all:
            st.warning("No cities or metric columns in the data.")
        else:
            selected_cities = st.multiselect(
                "Select cities (max 4)",
                options=cities_all,
                default=[],
                max_selections=4,
                key="compare_cities",
            )
            selected_metrics = st.multiselect(
                "Select metrics (max 6)",
                options=metrics,
                default=metrics[: min(6, len(metrics))],
                max_selections=6,
                key="compare_metrics",
            )
            st.caption("Best value among selected cities is highlighted.")

            if not selected_cities or not selected_metrics:
                st.info("Select at least one city and one metric to see cards.")
            else:
                # Best-value logic: lower is better vs higher is better (by metric name)
                LOWER_IS_BETTER = [
                    "Water Stress Score",
                    "Sustainability Score",
                    "Annual CO2",
                    "Climate Adjusted Water Use",
                ]
                HIGHER_IS_BETTER = ["avg precipitation", "Climate Adjusted Electricity"]

                def is_lower_better(metric_name):
                    return any(s in metric_name for s in LOWER_IS_BETTER)

                def is_higher_better(metric_name):
                    return any(s in metric_name for s in HIGHER_IS_BETTER)

                # For each metric, which city has the best value (for highlighting)
                sub_df = df[df[city_col].astype(str).str.strip().isin(selected_cities)].copy()
                sub_df["_city_norm"] = sub_df[city_col].astype(str).str.strip()
                best_by_metric = {}
                for m in selected_metrics:
                    vals = sub_df.set_index("_city_norm")[m]
                    numeric = pd.to_numeric(vals, errors="coerce")
                    if is_lower_better(m):
                        best_by_metric[m] = numeric.idxmin() if numeric.notna().any() else None
                    elif is_higher_better(m):
                        best_by_metric[m] = numeric.idxmax() if numeric.notna().any() else None
                    else:
                        best_by_metric[m] = None

                def format_val(v):
                    if isinstance(v, (int, float)) and pd.notna(v):
                        return f"{v:,.2f}" if isinstance(v, float) else f"{v:,}"
                    return str(v)

                st.markdown(
                    """
                    <style>
                    .city-compare-card { background-color: #141414; border: 1px solid #2E2E2E; border-radius: 4px; padding: 12px; margin-bottom: 12px; }
                    .city-compare-card .card-header { font-weight: bold; color: #F5F5F5; font-size: 1.1rem; margin-bottom: 12px; }
                    .city-compare-card .metric-value { font-size: 2rem; font-weight: bold; color: #F5F5F5; margin-bottom: 4px; }
                    .city-compare-card .metric-value.metric-best { color: #FFFFFF; background-color: #1F1F1F; padding: 4px 8px; border-radius: 4px; }
                    .city-compare-card .metric-label { color: #A0A0A0; font-size: 0.875rem; margin-bottom: 8px; }
                    .city-compare-card .metric-divider { border: none; border-top: 1px solid #2E2E2E; margin: 8px 0; }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )

                n_cities = len(selected_cities)
                num_cols = 2 if n_cities == 2 else n_cities
                cols = st.columns(num_cols)
                for idx, city_name in enumerate(selected_cities):
                    row = df[df[city_col].astype(str).str.strip() == city_name]
                    if row.empty:
                        continue
                    row = row.iloc[0]
                    parts = [
                        f'<div class="city-compare-card">',
                        f'<div class="card-header">{html.escape(city_name)}</div>',
                    ]
                    for i, m in enumerate(selected_metrics):
                        v = row[m]
                        is_best = best_by_metric.get(m) == city_name
                        val_class = ' metric-best' if is_best else ''
                        parts.append(f'<div class="metric-value{val_class}">{html.escape(format_val(v))}</div>')
                        parts.append(f'<div class="metric-label">{html.escape(m)}</div>')
                        if i < len(selected_metrics) - 1:
                            parts.append('<hr class="metric-divider">')
                    parts.append("</div>")
                    with cols[idx]:
                        st.markdown("".join(parts), unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Cooling Cost Analysis
# -----------------------------------------------------------------------------
else:
    st.title("Cooling Cost Analysis")
    st.markdown("Compare cooling costs by data center type.")

    if df_cooling is None or df_cooling.empty:
        st.warning("No cooling cost data loaded. Ensure Final.Project.Data.xlsx has a 'Cooling Cost Method' sheet.")
    else:
        elec_col = "Total Electricity Cost ($/year)"
        water_col = "Total Water Cost ($/year)"
        city_col_cc = "City"
        type_col = "Data Center Type"

        dc_type_selection = st.radio(
            "Data Center Type",
            options=["AI/ML Cluster", "Hyperscale Cloud"],
            horizontal=True,
            key="cooling_dc_type",
        )

        if elec_col not in df_cooling.columns or water_col not in df_cooling.columns:
            st.markdown(
                '<p style="color: #FFFFFF;">No data available for this selection.</p>',
                unsafe_allow_html=True,
            )
        else:
            elec_vals = []
            water_vals = []
            if dc_type_selection == "AI/ML Cluster":
                # Use AI/ML Cluster rows directly: one row per city, elec and water from that row
                filtered = df_cooling[
                    df_cooling[type_col].astype(str).str.strip() == "AI/ML Cluster"
                ].copy()
                cities = sorted(filtered[city_col_cc].dropna().astype(str).str.strip().unique().tolist())
                for c in cities:
                    row = filtered[filtered[city_col_cc].astype(str).str.strip() == c]
                    if len(row) > 0:
                        elec_vals.append(float(row[elec_col].iloc[0]))
                        water_vals.append(float(row[water_col].iloc[0]))
                    else:
                        elec_vals.append(0)
                        water_vals.append(0)
            else:
                # Hyperscale Cloud: combine AI/ML row (electricity) + Hyperscale row (water) per city
                cities = sorted(df_cooling[city_col_cc].dropna().astype(str).str.strip().unique().tolist())
                for c in cities:
                    ai_ml_row = df_cooling[
                        (df_cooling[city_col_cc].astype(str).str.strip() == c)
                        & (df_cooling[type_col].astype(str).str.strip() == "AI/ML Cluster")
                    ]
                    hyp_row = df_cooling[
                        (df_cooling[city_col_cc].astype(str).str.strip() == c)
                        & (df_cooling[type_col].astype(str).str.strip() == "Hyperscale Cloud")
                    ]
                    elec = float(ai_ml_row[elec_col].iloc[0]) if len(ai_ml_row) > 0 and pd.notna(ai_ml_row[elec_col].iloc[0]) else 0
                    water = float(hyp_row[water_col].iloc[0]) if len(hyp_row) > 0 and pd.notna(hyp_row[water_col].iloc[0]) else 0
                    elec_vals.append(elec)
                    water_vals.append(water)

            if not cities:
                st.markdown(
                    '<p style="color: #FFFFFF;">No data available for this selection.</p>',
                    unsafe_allow_html=True,
                )
            else:
                fig_cc = go.Figure()
                fig_cc.add_trace(
                    go.Bar(
                        x=cities,
                        y=elec_vals,
                        name="Total Electricity Cost ($/year)",
                        marker_color="#FFFFFF",
                        text=[f"${v:,.0f}" for v in elec_vals],
                        textposition="outside",
                        textfont=dict(color="#F5F5F5", size=11),
                    )
                )
                fig_cc.add_trace(
                    go.Bar(
                        x=cities,
                        y=water_vals,
                        name="Total Water Cost ($/year)",
                        marker_color="#CCCCCC",
                        text=[f"${v:,.0f}" for v in water_vals],
                        textposition="outside",
                        textfont=dict(color="#F5F5F5", size=11),
                    )
                )
                chart_title = f"Cooling Costs — {dc_type_selection}."
                fig_cc.update_layout(
                    title=dict(text=chart_title, font=dict(color="#F5F5F5", size=14)),
                    barmode="group",
                    template="plotly_white",
                    paper_bgcolor="#141414",
                    plot_bgcolor="#141414",
                    font=dict(family="Space Grotesk, sans-serif", color="#F5F5F5", size=11),
                    xaxis=dict(
                        title="",
                        tickangle=-30,
                        showgrid=False,
                        linecolor="#2E2E2E",
                        tickfont=dict(color="#F5F5F5"),
                    ),
                    yaxis=dict(
                        title="Cost ($/year)",
                        showgrid=True,
                        gridcolor="#2E2E2E",
                        linecolor="#2E2E2E",
                        tickfont=dict(color="#F5F5F5"),
                    ),
                    margin=dict(t=80, b=100),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        font=dict(color="#F5F5F5"),
                    ),
                    height=500,
                    hoverlabel=dict(
                        bgcolor="#1A1A1A",
                        font=dict(color="#F5F5F5", size=11),
                        bordercolor="#2E2E2E",
                    ),
                )
                # Y-axis tick format: $ and commas
                fig_cc.update_yaxes(tickformat="$,.0f")
                st.plotly_chart(fig_cc, use_container_width=True)
