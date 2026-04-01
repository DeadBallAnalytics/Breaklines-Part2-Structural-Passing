import streamlit as st
from pathlib import Path

def apply_page_style():
    st.set_page_config(
        page_title="Structural Passing",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.markdown("""
    <style>
        .stApp {
            background-color: #FFFFFF;
        }

        .block-container {
            max-width: 1250px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3 {
            color: #111827;
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 800;
            color: #111827;
            margin-top: 1rem;
            margin-bottom: 0.75rem;
        }

        .section-text {
            font-size: 0.98rem;
            line-height: 1.7;
            color: #4B5563;
        }
    </style>
    """, unsafe_allow_html=True)

def apply_global_style():
    st.set_page_config(
        page_title="BreakLines",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown("""
    <style>
        .stApp {
            background-color: #FFFFFF;
        }

        .block-container {
            max-width: 1250px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 800;
            color: #111827;
            margin-top: 1rem;
            margin-bottom: 0.75rem;
        }

        .section-text {
            font-size: 0.98rem;
            line-height: 1.7;
            color: #4B5563;
        }

        .page-footer-brand {
            text-align: right;
            font-size: 12px;
            color: #6B7280;
            margin-top: 1.25rem;
            padding-top: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)


def render_page_branding(logo_path="assets/logos/1.png", logo_width=405):
    left, right = st.columns([3, 1], gap="small")
    with left:
        st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
    with right:
        if Path(logo_path).exists():
            st.image(logo_path, width=logo_width)


def render_page_footer():
    st.markdown("""
    <div class="page-footer-brand">
        © 2026 Dead Ball Analytics · BreakLines Part II: Structural Passing · Data: FIFA World Cup 2022 · For research and demonstration use
    </div>
    """, unsafe_allow_html=True)