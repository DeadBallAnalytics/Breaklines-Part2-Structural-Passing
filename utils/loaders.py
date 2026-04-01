import json
import pandas as pd
import streamlit as st

from utils.config import DATA_DIR


@st.cache_data
def load_passes():
    return pd.read_parquet(DATA_DIR / "passes_master.parquet")


@st.cache_data
def load_team_summary():
    return pd.read_parquet(DATA_DIR / "team_summary.parquet")


@st.cache_data
def load_player_summary():
    return pd.read_parquet(DATA_DIR / "player_summary.parquet")


@st.cache_data
def load_duo_summary():
    return pd.read_parquet(DATA_DIR / "duo_summary.parquet")


@st.cache_data
def load_pass_type_summary():
    return pd.read_parquet(DATA_DIR / "pass_type_summary.parquet")


@st.cache_data
def load_team_style_map():
    return pd.read_parquet(DATA_DIR / "team_style_map.parquet")


@st.cache_data
def load_global_summary():
    with open(DATA_DIR / "global_summary.json", "r", encoding="utf-8") as f:
        return json.load(f)