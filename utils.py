"""Shared data loading and UI setup for the Data Center Water Risk Dashboard."""
import os
import pandas as pd
import streamlit as st

# Default data path (same directory as this project)
DEFAULT_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Final.Project.Data.xlsx")

# Metric columns = all columns except the first (city name)
def get_metric_columns(df):
    """Return list of column names excluding the first column (city)."""
    if df is None or df.empty or len(df.columns) < 2:
        return []
    return list(df.columns[1:])


def load_excel():
    """
    Load data from the hardcoded Final.Project.Data.xlsx file.
    Uses Sheet1, columns F:N. Tries header in row 3 (0-based index 2) first;
    if column names are Unnamed, tries row 4 (index 3) for compatibility.
    """
    def _read(header_row=2):
        return pd.read_excel(
            DEFAULT_DATA_PATH,
            sheet_name="Sheet1",
            usecols="F:N",
            header=header_row,
            engine="openpyxl",
        )
    if not os.path.isfile(DEFAULT_DATA_PATH):
        return None
    df = _read()
    # If we got Unnamed columns, retry with next row (some sheets use row 4 for headers)
    if df.columns[0].startswith("Unnamed"):
        df = _read(header_row=3)
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    # Drop rows where city name is null or empty
    city_col = df.columns[0]
    df = df.dropna(subset=[city_col])
    df = df[df[city_col].astype(str).str.strip() != ""]
    return df.reset_index(drop=True)


def inject_css():
    """Apply custom CSS for modern black and white theme."""
    st.markdown(
        """
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            /* Global font */
            html, body, [class*="css"] {
                font-family: 'Space Grotesk', sans-serif !important;
            }
            /* Page background */
            .stApp {
                background-color: #0D0D0D;
            }
            /* Sidebar */
            [data-testid="stSidebar"] {
                background-color: #1A1A1A;
                border-right: 1px solid #2E2E2E;
            }
            [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
                color: #F5F5F5 !important;
            }
            [data-testid="stSidebar"] .stFileUploader label {
                color: #F5F5F5 !important;
            }
            /* Primary text */
            p, label, span {
                color: #F5F5F5 !important;
            }
            /* Page title */
            h1 {
                font-family: 'Space Grotesk', sans-serif !important;
                color: #FFFFFF !important;
                font-weight: 700 !important;
                letter-spacing: 0.05em !important;
            }
            /* Section headers */
            h2, h3 {
                font-family: 'Space Grotesk', sans-serif !important;
                color: #CCCCCC !important;
            }
            /* Metric boxes, dataframes, selectboxes */
            [data-testid="stMetric"], [data-testid="stDataFrame"], [data-testid="stDataFrame"] table,
            div[data-testid="stSelectbox"] > div, div[data-testid="stMultiSelect"] > div {
                background-color: #1A1A1A !important;
                border: 1px solid #2E2E2E !important;
                color: #F5F5F5 !important;
            }
            [data-testid="stDataFrame"] table {
                background-color: #141414 !important;
            }
            [data-testid="stDataFrame"] th {
                background-color: #1A1A1A !important;
                color: #F5F5F5 !important;
                border: 1px solid #2E2E2E !important;
            }
            [data-testid="stDataFrame"] tr:nth-child(even) td {
                background-color: #141414 !important;
                color: #F5F5F5 !important;
                border: 1px solid #2E2E2E !important;
            }
            [data-testid="stDataFrame"] tr:nth-child(odd) td {
                background-color: #1A1A1A !important;
                color: #F5F5F5 !important;
                border: 1px solid #2E2E2E !important;
            }
            /* Remove default blue hover; white accent / underline */
            .stButton > button {
                background-color: #1A1A1A !important;
                color: #FFFFFF !important;
                border: 1px solid #2E2E2E !important;
            }
            .stButton > button:hover {
                background-color: #2E2E2E !important;
                color: #FFFFFF !important;
                border-color: #FFFFFF !important;
                text-decoration: underline;
            }
            /* Selectbox and multiselect dark theme */
            .stSelectbox label, .stMultiSelect label {
                color: #F5F5F5 !important;
            }
            [data-testid="stSelectbox"] [data-baseweb="select"],
            [data-testid="stMultiSelect"] [data-baseweb="tag"] {
                background-color: #1A1A1A !important;
                border-color: #2E2E2E !important;
                color: #F5F5F5 !important;
            }
            /* Alerts / info boxes */
            [data-testid="stAlert"] {
                background-color: #1A1A1A !important;
                border: 1px solid #2E2E2E !important;
                color: #F5F5F5 !important;
            }
            /* Sidebar collapse/expand arrow - broad nuclear override */
            [data-testid="collapsedControl"],
            [data-testid="collapsedControl"] *,
            [data-testid="collapsedControl"] svg,
            [data-testid="collapsedControl"] svg path,
            button[data-testid="baseButton-header"],
            .css-1rs6os, .css-17ziqus,
            section[data-testid="stSidebar"] button,
            section[data-testid="stSidebar"] button svg,
            section[data-testid="stSidebar"] button svg path {
                color: #8B0000 !important;
                fill: #8B0000 !important;
                stroke: #8B0000 !important;
                background-color: transparent !important;
            }
            /* Top toolbar / header bar */
            header[data-testid="stHeader"],
            header[data-testid="stHeader"] * {
                background-color: #000000 !important;
                color: #FFFFFF !important;
            }
            .stApp > header {
                background-color: #000000 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def setup_sidebar():
    """
    Load data into session_state and show status in sidebar.
    Call this at the top of every page so navigation and data stay in sync.
    """
    df = load_excel()
    st.session_state["df"] = df
    if df is not None:
        st.sidebar.caption(f"Loaded: **{len(df)}** cities")
