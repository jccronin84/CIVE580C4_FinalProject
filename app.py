"""Data Center Water Risk Dashboard with two pages."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import DEFAULT_DATA_PATH, inject_css, setup_sidebar

CITY_ORDER = ["Denver", "Miami", "Phoenix", "San Diego", "Seattle"]

CITY_PARAMS = {
    "Denver": {"electricity_rate": 0.133, "water_rate": 4.9, "range_c": 15, "coc": 4},
    "Miami": {"electricity_rate": 0.116, "water_rate": 5.5, "range_c": 20, "coc": 3},
    "Phoenix": {"electricity_rate": 0.131, "water_rate": 3.5, "range_c": 15, "coc": 3},
    "San Diego": {"electricity_rate": 0.295, "water_rate": 11.5, "range_c": 20, "coc": 3},
    "Seattle": {"electricity_rate": 0.119, "water_rate": 5.5, "range_c": 10, "coc": 4},
}

COOLING_DATA_POINTS = [
    "Electricity Rate ($/kWh)",
    "Total Electricity Cost ($/year)",
    "Load Factor (%)",
    "Range (°C)",
    "CoC",
    "Tons",
    "Evap (gpm)",
    "Blowdown (gpm)",
    "Drift (gpm)",
    "Peak Makeup (gpm)",
    "Peak Makeup (MGD)",
    "Peak Annual Makeup (MGY)",
    "Actual Annual Makeup (MGY)",
    "Water Rate ($/1000 gal)",
    "Total Water Cost ($/year)",
]

DOLLAR_FIELDS = {
    "Electricity Rate ($/kWh)",
    "Total Electricity Cost ($/year)",
    "Water Rate ($/1000 gal)",
    "Total Water Cost ($/year)",
}

CITY_ACCENTS = {
    "Denver": "#FFFFFF",
    "Miami": "#CCCCCC",
    "Phoenix": "#AAAAAA",
    "San Diego": "#888888",
    "Seattle": "#555555",
}

st.set_page_config(
    page_title="Data Center Water Risk Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
setup_sidebar()

st.sidebar.markdown("<h1 style='color:#FFFFFF; font-family: Space Grotesk, sans-serif; font-weight:700; font-size:1.6rem; margin-bottom:0.25rem;'>Data Center Site Selection</h1>", unsafe_allow_html=True)
section = st.sidebar.radio(
    "Navigate",
    options=["Site Selection Analysis", "Environmental Impacts"],
)


def compute_city_metrics(city, dc_type, it_load):
    params = CITY_PARAMS[city]
    electricity_rate = params["electricity_rate"]
    water_rate = params["water_rate"]
    range_c = params["range_c"]
    coc = params["coc"]

    load_factor = 0.8 if dc_type == "AI/ML Cluster" else 0.6
    total_elec_cost = it_load * 1000 * 365 * electricity_rate
    tons = it_load * 1000 / 3.517
    evap = 0.001 * tons * range_c
    blowdown = evap / (coc - 1)
    drift = 0.01 * evap
    peak_makeup_gpm = evap + blowdown + drift
    peak_makeup_mgd = peak_makeup_gpm * 60 * 24 / 1_000_000
    peak_annual_mgy = peak_makeup_mgd * 365
    actual_annual_mgy = peak_annual_mgy * load_factor
    total_water_cost = (actual_annual_mgy * 1_000) * water_rate

    return {
        "Electricity Rate ($/kWh)": electricity_rate,
        "Total Electricity Cost ($/year)": total_elec_cost,
        "Load Factor (%)": load_factor * 100,
        "Range (°C)": range_c,
        "CoC": coc,
        "Tons": tons,
        "Evap (gpm)": evap,
        "Blowdown (gpm)": blowdown,
        "Drift (gpm)": drift,
        "Peak Makeup (gpm)": peak_makeup_gpm,
        "Peak Makeup (MGD)": peak_makeup_mgd,
        "Peak Annual Makeup (MGY)": peak_annual_mgy,
        "Actual Annual Makeup (MGY)": actual_annual_mgy,
        "Water Rate ($/1000 gal)": water_rate,
        "Total Water Cost ($/year)": total_water_cost,
    }


def fmt_value(field_name, value):
    if field_name in DOLLAR_FIELDS:
        return f"${value:,.2f}"
    return f"{value:,.2f}"


st.markdown("<h1 style='color:#FFFFFF; font-family: Space Grotesk, sans-serif; font-weight:700; font-size:2.5rem; margin-bottom: 0.25rem;'>Data Center Site Selection</h1>", unsafe_allow_html=True)
if section == "Site Selection Analysis":
    st.title("Site Selection Analysis")

    selected_cities = st.multiselect(
        "Select Cities",
        options=CITY_ORDER,
        default=[],
    )

    selected_data_points = st.multiselect(
        "Select Data Points to Compare",
        options=COOLING_DATA_POINTS,
        default=["Total Electricity Cost ($/year)", "Total Water Cost ($/year)"],
    )

    city_inputs = {}
    if selected_cities:
        input_cols = st.columns(len(selected_cities))
        for idx, city in enumerate(selected_cities):
            with input_cols[idx]:
                st.markdown(f"**{city}**")
                dc_type = st.selectbox(
                    "Data Center Type",
                    options=["AI/ML Cluster", "Hyperscale Cloud"],
                    key=f"dc_type_{city}",
                )
                it_load = st.number_input(
                    "IT Load (MW)",
                    min_value=1,
                    max_value=100,
                    value=100,
                    step=1,
                    key=f"it_load_{city}",
                )
                city_inputs[city] = {"dc_type": dc_type, "it_load": int(it_load)}

    city_results = {}
    for city in selected_cities:
        cfg = city_inputs.get(city, {"dc_type": "AI/ML Cluster", "it_load": 100})
        city_results[city] = compute_city_metrics(city, cfg["dc_type"], cfg["it_load"])

    st.markdown(
        """
        <style>
        .cooling-card {
            background-color: #141414;
            border: 1px solid #2E2E2E;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
            padding: 24px;
            margin-bottom: 16px;
            overflow: hidden;
        }
        .cooling-card .accent-bar {
            height: 6px;
            border-radius: 10px;
            margin: -24px -24px 16px -24px;
        }
        .cooling-card .card-header {
            color: #F5F5F5;
            font-weight: 800;
            margin-bottom: 16px;
            padding-bottom: 10px;
            font-size: 1.5rem;
            border-bottom: 1px solid #FFFFFF;
        }
        .cooling-card .metric-row {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 12px;
            padding: 10px 0;
            border-bottom: 1px solid #2E2E2E;
        }
        .cooling-card .metric-row:last-child {
            border-bottom: none;
        }
        .cooling-card .metric-row.key-row {
            background: #1F1F1F;
            border-radius: 8px;
            padding: 12px 10px;
            margin: 4px 0;
        }
        .cooling-card .metric-label {
            color: #888888;
            font-size: 0.8rem;
            line-height: 1.2;
            max-width: 58%;
        }
        .cooling-card .metric-value {
            color: #FFFFFF;
            font-size: 1.4rem;
            font-weight: 800;
            text-align: right;
            line-height: 1.1;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if selected_cities and selected_data_points:
        card_cols = st.columns(len(selected_cities))
        for idx, city in enumerate(selected_cities):
            accent = CITY_ACCENTS.get(city, "#CCCCCC")
            parts = [
                '<div class="cooling-card">',
                f'<div class="accent-bar" style="background-color: {accent};"></div>',
                f'<div class="card-header">{city}</div>',
            ]
            for metric in selected_data_points:
                val = city_results[city][metric]
                key_row_class = (
                    " key-row"
                    if metric in {"Total Electricity Cost ($/year)", "Total Water Cost ($/year)"}
                    else ""
                )
                parts.append(
                    (
                        f'<div class="metric-row{key_row_class}">'
                        f'<div class="metric-label">{metric}</div>'
                        f'<div class="metric-value">{fmt_value(metric, val)}</div>'
                        "</div>"
                    )
                )
            parts.append("</div>")
            with card_cols[idx]:
                st.markdown("".join(parts), unsafe_allow_html=True)
    elif selected_cities:
        st.info("Select at least one data point to display city cards.")

    chart_cities = selected_cities
    elec_vals = [city_results[city]["Total Electricity Cost ($/year)"] for city in chart_cities]
    water_vals = [city_results[city]["Total Water Cost ($/year)"] for city in chart_cities]

    fig_cc = go.Figure()
    fig_cc.add_trace(
        go.Bar(
            x=chart_cities,
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
            x=chart_cities,
            y=water_vals,
            name="Total Water Cost ($/year)",
            marker_color="#CCCCCC",
            text=[f"${v:,.0f}" for v in water_vals],
            textposition="outside",
            textfont=dict(color="#F5F5F5", size=11),
        )
    )
    fig_cc.update_layout(
        title=dict(text="Cooling Cost Comparison by City", font=dict(color="#F5F5F5", size=14)),
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
    fig_cc.update_yaxes(tickformat="$,.0f")
    st.plotly_chart(fig_cc, use_container_width=True)

else:
    st.title("Environmental Impacts")

    try:
        ENV_COLUMNS = [
            "City",
            "Avg Temp (°C)",
            "Avg Annual Precipitation (mm/year)",
            "Grid Carbon Intensity (kgCO2/kWh)",
            "Climate Adjusted Electricity (MWh/year)",
            "Annual CO2 (metric tons)",
            "Climate Adjusted Water Use (gallons/year)",
            "Raw Water Stress Index",
            "Calculated Water Stress Score (1=low, 5=high)",
            "Sustainability Score",
            "Monthly Precip (mm)",
        ]

        df_env = pd.read_excel(
            DEFAULT_DATA_PATH,
            sheet_name="Cooling Cost Method",
            usecols="E:O",
            header=None,
            skiprows=17,
            nrows=5,
            engine="openpyxl",
        )
        df_env.columns = ENV_COLUMNS
        df_env = df_env.dropna(subset=["City"]).copy()
        df_env["City"] = df_env["City"].astype(str).str.strip()
        df_env = df_env[df_env["City"].isin(CITY_ORDER)].reset_index(drop=True)

        numeric_cols = [c for c in ENV_COLUMNS if c != "City"]
        for col in numeric_cols:
            df_env[col] = pd.to_numeric(df_env[col], errors="coerce")

        df_env["Raw Water Stress Index"] = (
            df_env["Climate Adjusted Water Use (gallons/year)"]
            / df_env["Avg Annual Precipitation (mm/year)"]
        ).round(0)

        L = df_env["Raw Water Stress Index"]
        if L.max() == L.min():
            df_env["Calculated Water Stress Score (1=low, 5=high)"] = 1.0
        else:
            df_env["Calculated Water Stress Score (1=low, 5=high)"] = (
                1 + 4 * (L - L.min()) / (L.max() - L.min())
            ).round(0)

        selected_cities_env = st.multiselect(
            "Select Cities",
            options=CITY_ORDER,
            default=[],
        )
        selected_data_points_env = st.multiselect(
            "Select Data Points to Compare",
            options=[c for c in ENV_COLUMNS if c != "City"],
            default=[],
        )

        st.markdown(
            """
            <style>
            .env-card {
                background-color: #141414;
                border: 1px solid #2E2E2E;
                border-radius: 12px;
                box-shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
                padding: 24px;
                margin-bottom: 16px;
            }
            .env-card .card-header {
                color: #F5F5F5;
                font-weight: 800;
                margin-bottom: 16px;
                padding-bottom: 10px;
                font-size: 1.5rem;
                border-bottom: 1px solid #FFFFFF;
            }
            .env-card .metric-row {
                display: flex;
                justify-content: space-between;
                align-items: baseline;
                gap: 12px;
                padding: 10px 0;
                border-bottom: 1px solid #2E2E2E;
            }
            .env-card .metric-row:last-child {
                border-bottom: none;
            }
            .env-card .metric-row.key-row {
                background: #1F1F1F;
                border-radius: 8px;
                padding: 12px 10px;
                margin: 4px 0;
            }
            .env-card .metric-label {
                color: #888888;
                font-size: 0.8rem;
                line-height: 1.2;
                max-width: 58%;
            }
            .env-card .metric-value {
                color: #FFFFFF;
                font-size: 1.4rem;
                font-weight: 800;
                text-align: right;
                line-height: 1.1;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        if not selected_cities_env:
            st.info("Select one or more cities to view the Environmental Impacts dashboard.")
        else:
            env_df_selected = df_env[df_env["City"].isin(selected_cities_env)].copy()
            card_cols = st.columns(len(selected_cities_env))
            for idx, city in enumerate(selected_cities_env):
                city_row = env_df_selected[env_df_selected["City"] == city]
                if city_row.empty:
                    continue
                city_row = city_row.iloc[0]

                parts = [f'<div class="env-card"><div class="card-header">{city}</div>']
                for metric in selected_data_points_env:
                    value = city_row.get(metric)
                    value_fmt = f"{value:,.2f}" if pd.notna(value) else "N/A"
                    key_row_class = (
                        " key-row"
                        if metric
                        in {
                            "Calculated Water Stress Score (1=low, 5=high)",
                            "Sustainability Score",
                        }
                        else ""
                    )
                    parts.append(
                        (
                            f'<div class="metric-row{key_row_class}">'
                            f'<div class="metric-label">{metric}</div>'
                            f'<div class="metric-value">{value_fmt}</div>'
                            "</div>"
                        )
                    )
                parts.append("</div>")
                with card_cols[idx]:
                    st.markdown("".join(parts), unsafe_allow_html=True)
    except Exception as exc:
        st.error(f"Unable to load Environmental Impacts table: {exc}")
