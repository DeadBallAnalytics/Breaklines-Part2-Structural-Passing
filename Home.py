import streamlit as st
from utils.loaders import load_global_summary, load_duo_summary
from utils.config import APP_TITLE
import base64
import numpy as np
from utils.style import apply_global_style, render_page_branding, render_page_footer, apply_page_style
apply_page_style()
apply_global_style()
render_page_branding()
# --------------------------------------------------
# Load summary data
# --------------------------------------------------
summary = load_global_summary()
# --------------------------------------------------
# Load logo as base64
# --------------------------------------------------
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = get_base64_image("assets/logos/deadball_logo.png")
event_logo = get_base64_image("assets/logos/event.png")

# --------------------------------------------------
# CSS
# --------------------------------------------------
st.markdown("""
<style>
    .hero-box {
        background: linear-gradient(135deg, #0f172a 0%, #111827 45%, #1f2937 100%);
        border-radius: 24px;
        padding: 2.2rem 2rem 2rem 2rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.06);
    }

    .hero-top {
        display: grid;
        grid-template-columns: 5fr 2fr;
        align-items: center;
        column-gap: 1rem;
        margin-bottom: 1rem;
    }

    .hero-title {
        font-size: 3.1rem;
        font-weight: 800;
        line-height: 1.05;
        color: #00E68A;
        letter-spacing: -0.02em;
        margin: 0;
    }

    .hero-logo-wrap {
        text-align: right;
    }

    .hero-logo {
        width: 260px;
        max-width: 100%;
        height: auto;
    }

    .hero-text {
        font-size: 1.02rem;
        line-height: 1.8;
        color: #E5E7EB;
        max-width: 900px;
        margin: 0;
    }

    @media (max-width: 900px) {
        .hero-top {
            grid-template-columns: 1fr;
            row-gap: 1rem;
        }

        .hero-logo-wrap {
            text-align: left;
        }

        .hero-title {
            font-size: 2.4rem;
        }

        .hero-logo {
            width: 220px;
        }
    }
</style>
""", unsafe_allow_html=True)
# --------------------------------------------------
# Custom CSS
# --------------------------------------------------
st.markdown("""
<style>
    .section-title {
        font-size: 1.35rem;
        font-weight: 750;
        margin-top: 1.3rem;
        margin-bottom: 0.8rem;
        color: #111827;
    }

    .section-text {
        font-size: 1rem;
        line-height: 1.7;
        color: #4B5563;
        margin-bottom: 0.8rem;
    }

    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E5E7EB;
        border-radius: 18px;
        padding: 1rem 1rem 0.85rem 1rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
        text-align: center;
        height: 100%;
    }

    .metric-value {
        font-size: 1.55rem;
        font-weight: 800;
        color: #111827;
        margin-bottom: 0.15rem;
    }

    .metric-label {
        font-size: 0.92rem;
        color: #6B7280;
        font-weight: 500;
    }

    .card {
        background: #F9FAFB;
        border-radius: 18px;
        padding: 1.2rem 1.1rem;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 6px rgba(0,0,0,0.03);
        height: 100%;
    }

    .card-title {
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-size: 1.05rem;
        color: #111827;
        font-weight: 600;
    }

    .card p {
        margin-bottom: 0;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #4B5563;
    }

    .highlight-box {
        background: #ECFDF5;
        border-left: 6px solid #00E68A;
        border-radius: 14px;
        padding: 1rem 1rem;
        margin-top: 1rem;
        color: #14532D;
        font-size: 0.98rem;
        line-height: 1.7;
    }

    .footer-box {
        background: #F9FAFB;
        border: 1px dashed #D1D5DB;
        border-radius: 16px;
        padding: 1rem 1.2rem;
        margin-top: 1.5rem;
        color: #4B5563;
        font-size: 0.96rem;
        line-height: 1.65;
    }

    .subtle-divider {
        height: 1px;
        background: linear-gradient(to right, transparent, #D1D5DB, transparent);
        margin-top: 1.2rem;
        margin-bottom: 1.2rem;
    }
    .logo-top {
        display: grid;
        grid-template-columns: 5fr 2fr;
        align-items: center;
        column-gap: 1rem;
        margin-bottom: 1rem;
    }
            
    .flag-logo-wrap {
        text-align: left;
    }
    
    .flag-logo {
    width: 70px;     
    max-width: 100%;
    height: auto;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px !important;
    background: #F8FAFC !important;
    border: 1px solid #E5E7EB !important;
    padding: 0.4rem 0.6rem !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.03) !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Hero
# --------------------------------------------------
st.markdown(f"""
<div class="hero-box">
    <div class="hero-top">
        <div class="hero-title">Structural Passing</div>
        <div class="hero-logo-wrap">
            <img class="hero-logo" src="data:image/png;base64,{logo_b64}" />
        </div>
    </div>
    <p class="hero-text">
        An interactive exploration of how passes reshape defensive structure in football.
        Instead of focusing only on outcomes, this framework reveals how passing decisions
        create space, break lines, and drive tactical progression across teams, players,
        and passer-receiver combinations.
    </p>
</div>
""", unsafe_allow_html=True)
# --------------------------------------------------
# KPI row
# --------------------------------------------------

with st.container(border=True):
    col1, col2 = st.columns([4.25, 1.5], gap="small")

    with col1:
        st.markdown("### At a glance")
        st.markdown("""
        This app is built on **synchronised tracking and event data from the 2022 FIFA World Cup**,
        covering all **64 matches** of the tournament. The framework uses this spatio-temporal data
        to evaluate passing not only by outcome, but by **structural impact** on the defensive organisation.
        """)

    with col2:
        st.image("assets/logos/event.png", width=250)

# st.markdown('', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{summary.get("n_matches", "-")}</div>
        <div class="metric-label">Matches</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{summary.get("n_teams", "-")}</div>
        <div class="metric-label">Teams</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    n_passes = summary.get("n_passes", "-")
    n_passes_display = f"{n_passes:,}" if isinstance(n_passes, int) else n_passes
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{n_passes_display}</div>
        <div class="metric-label">Analysed Passes</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    top_pass_type = str(summary.get("top_pass_type", "-")).replace("_", " ").title()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{top_pass_type}</div>
        <div class="metric-label">Most Common Archetype</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="subtle-divider"></div>', unsafe_allow_html=True)

# --------------------------------------------------
# What makes this different
# --------------------------------------------------
# st.markdown('', unsafe_allow_html=True)

st.markdown("""
<div class="section-title">What makes this different?</div>
<div class="section-text">
Traditional pass evaluation models often focus on outcomes such as scoring probability or possession value. This framework instead focuses on <b>structural impact</b>: how passes alter the opponent's defensive organisation, open new spaces, and change the geometry of play.
</div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="section-title">
    The framework combines three structural metrics.
    </div>
    """, unsafe_allow_html=True)

# left, right = st.columns([1.45, 1], gap="large")
# with left:
st.markdown("""
<div class="card">
    <div class="card-title">Line Bypass Score (LBS)</div>
    <p>Captures how strongly a pass penetrates defensive lines and advances the ball beyond defenders.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card" style="margin-top:0.8rem;">
    <div class="card-title">Space Gain Metric (SGM)</div>
    <p>Measures whether the pass moves the ball into regions with more attacking space and lower defensive density.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card" style="margin-top:0.8rem;">
    <div class="card-title">Structural Disruption Index (SDI)</div>
    <p>Quantifies how much the pass stretches, deforms, or reorganises the defensive structure.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="section-title">
    The novel impact metric, <b>Tactical Impact Value (TIV)</b>
    </div>
    """, unsafe_allow_html=True)
# with right:
st.markdown("""
<div class="highlight-box">
    <b>Tactical Impact Value (TIV)</b> combines these structural signals into a single interpretable score,
    allowing users to compare pass archetypes, team styles, player roles, and passing relationships through
    one structural lens.
</div>
""", unsafe_allow_html=True)

# st.markdown("""
# <div class="highlight-box">
#     <b>Start here:</b><br>
#     If this is your first visit, begin with <b>Team Analysis</b> or <b>Player Analysis</b> to quickly
#     understand how structural progression differs across teams and players.
# </div>
# """, unsafe_allow_html=True)

# --------------------------------------------------
# Explore the analysis
# --------------------------------------------------
st.markdown('<div class="section-title">Explore the analysis</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4, gap="medium")

with c1:
    st.markdown("""
    <div class="card">
        <div class="card-title">Pass Archetypes</div>
        <p>Explore circulatory, destabilising, line-breaking, and space-expanding passes and how they differ structurally.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="card">
        <div class="card-title">Team Styles</div>
        <p>Compare tactical fingerprints across teams and examine how structural progression takes different forms.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="card">
        <div class="card-title">Player Profiles</div>
        <p>Identify players who generate structural value through their passing and understand how those roles differ.</p>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="card">
        <div class="card-title">Passing Duos</div>
        <p>Discover passer-receiver combinations that amplify tactical progression and reveal structural partnerships.</p>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# Quick highlights
# --------------------------------------------------
st.markdown('<div class="section-title">Headline highlights</div>', unsafe_allow_html=True)

h1, h2, h3 = st.columns(3, gap="medium")

summary2 = load_duo_summary()
summary2 = summary2[summary2["duo_passes"] >= 25].reset_index(drop=True)
summary2.sort_values("delta_tiv", ascending=False, inplace=True)

team_b64 = get_base64_image(f"assets/flags/{summary.get("top_team_name", "-").lower()}.png")
pla_b64 = get_base64_image(f"assets/flags/{summary.get("top_player_team", "-").lower()}.png")
duo_b64 = get_base64_image(f"assets/flags/{summary2.iloc[0].get("team_name", "-").lower()}.png")


with h1:
    st.markdown(f"""
    <div class="highlight-box">
            <div class="card-title">Top Team</div>
            <div class="flag-logo-wrap">
                <img class="flag-logo" src="data:image/png;base64,{team_b64}" />
            </div>
        <p><b>{summary.get("top_team_name", "-")}</b><br>
        Total TIV: {summary.get("top_team_total_tiv", "-")}<br>
        Mean TIV: {summary.get("top_team_mean_tiv", "-")}<br></p>
    </div>
    """, unsafe_allow_html=True)

with h2:
    st.markdown(f"""
    <div class="highlight-box">
        <div class="card-title">Top Player</div>
                <div class="flag-logo-wrap">
                <img class="flag-logo" src="data:image/png;base64,{pla_b64}" />
            </div>
        <p><b>{summary.get("top_player_name", "-")}</b><br>
        Team: {summary.get("top_player_team", "-")}<br>
        Total TIV: {summary.get("top_player_total_tiv", "-")}</p>
    </div>
    """, unsafe_allow_html=True)

with h3:
    st.markdown(f"""
    <div class="highlight-box">
        <div class="card-title">Top ΔTIV Duo (25+ passes)</div>
        <div class="flag-logo-wrap">
                <img class="flag-logo" src="data:image/png;base64,{duo_b64}" />
            </div>
        <p><b>{summary2.iloc[0].get("duo_label", "-")}</b><br>
        Team: {summary2.iloc[0].get("team_name", "-")}<br>
        ΔTIV: {np.round(summary2.iloc[0].get("delta_tiv", "-"), 4)}</p>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("""
<div class="footer-box">
    <b>About this app</b><br>
    This interactive companion was developed to make structural pass analysis accessible to football fans,
    analysts, and Dead Ball Analytics readers. Use the sidebar to move through the framework from multiple
    perspectives and interact with the core findings of the paper.
</div>
""", unsafe_allow_html=True)

render_page_footer()