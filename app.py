"""
Data Center Water Risk Dashboard — single-file app with sidebar navigation.
"""
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
    options=["Dashboard", "Overview Chart", "City Comparison"],
)
setup_sidebar()

df = st.session_state.get("df")

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
        st.subheader("Loaded data")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info(
            "No data loaded. Add **Final.Project.Data.xlsx** to this folder."
        )

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
else:
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

            if not selected_cities or not selected_metrics:
                st.info("Select at least one city and one metric to see charts.")
            else:
                metric_to_color = {m: METRIC_COLORS[i % len(METRIC_COLORS)] for i, m in enumerate(selected_metrics)}

                def make_bar_chart(city_name):
                    row = df[df[city_col].astype(str).str.strip() == city_name]
                    if row.empty:
                        return None
                    row = row.iloc[0]
                    x_vals = selected_metrics
                    y_vals = [row[m] for m in selected_metrics]
                    colors = [metric_to_color[m] for m in selected_metrics]
                    fig = go.Figure(
                        data=[
                            go.Bar(
                                x=x_vals,
                                y=y_vals,
                                marker_color=colors,
                                text=[f"{v:.2f}" if isinstance(v, (int, float)) else str(v) for v in y_vals],
                                textposition="outside",
                                textfont=dict(color="#000000", size=11),
                            )
                        ]
                    )
                    fig.update_layout(
                        title=dict(text=city_name, font=dict(color="#000000", size=14)),
                        template="plotly_white",
                        paper_bgcolor="#FFFFFF",
                        plot_bgcolor="#FFFFFF",
                        font=dict(family="Space Grotesk, sans-serif", color="#000000", size=11),
                        xaxis=dict(
                            title="",
                            tickangle=-30,
                            showgrid=False,
                            zeroline=True,
                            linecolor="#E0E0E0",
                            tickfont=dict(color="#000000"),
                        ),
                        yaxis=dict(
                            title="",
                            showticklabels=False,
                            showline=False,
                            showgrid=False,
                        ),
                        margin=dict(t=40, b=80),
                        showlegend=False,
                        height=320,
                        uniformtext_minsize=8,
                        hoverlabel=dict(
                            bgcolor="#FFFFFF",
                            font=dict(color="#000000", size=11),
                            bordercolor="#E0E0E0",
                        ),
                    )
                    return fig

                n_cities = len(selected_cities)
                cols_per_row = 2 if n_cities > 2 else n_cities
                rows = (n_cities + cols_per_row - 1) // cols_per_row

                for r in range(rows):
                    cols = st.columns(cols_per_row)
                    for c in range(cols_per_row):
                        idx = r * cols_per_row + c
                        if idx >= n_cities:
                            break
                        city_name = selected_cities[idx]
                        fig = make_bar_chart(city_name)
                        if fig is not None:
                            cols[c].plotly_chart(fig, use_container_width=True)
