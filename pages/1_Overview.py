import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import pandas as pd

from utils.loaders import load_global_summary, load_pass_type_summary
from utils.config import PASS_TYPE_COLORS, PASS_TYPE_LABELS
from utils.style import apply_global_style, render_page_branding, render_page_footer, apply_page_style
apply_page_style()
apply_global_style()
render_page_branding()
# --------------------------------------------------
# Load data
# --------------------------------------------------
summary = load_global_summary()
pass_type_summary = load_pass_type_summary().copy()

pass_type_summary["pass_type_label"] = pass_type_summary["pass_type"].map(PASS_TYPE_LABELS)

top_pass_type = str(summary.get("top_pass_type", "-")).replace("_", " ").title()
n_passes = summary.get("n_passes", "-")
n_passes_display = f"{n_passes:,}" if isinstance(n_passes, int) else n_passes

# --------------------------------------------------
# Page header
# --------------------------------------------------

st.markdown("""
<style>
    .overview-hero {
        background: linear-gradient(135deg, #0f172a 0%, #111827 45%, #1f2937 100%);
        border-radius: 24px;
        padding: 2rem 2rem 1.8rem 2rem;
        color: white;
        margin-bottom: 1.25rem;
        border: 1px solid rgba(255,255,255,0.05);
    }

    .overview-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #00E68A;
        margin-bottom: 0.45rem;
        letter-spacing: -0.02em;
    }

    .overview-subtitle {
        font-size: 1rem;
        line-height: 1.8;
        color: #E5E7EB;
        max-width: 950px;
        margin-bottom: 0;
    }

    .context-strip {
        background: #F8FAFC;
        border: 1px solid #E5E7EB;
        border-radius: 18px;
        padding: 0.95rem 1.1rem;
        margin-bottom: 1.1rem;
        color: #374151;
        font-size: 0.97rem;
        line-height: 1.7;
    }

    .section-title {
        font-size: 1.28rem;
        font-weight: 800;
        color: #111827;
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
    }

    .stat-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 20px;
        padding: 1.05rem 1rem 0.95rem 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.035);
        height: 100%;
    }

    .stat-label {
        font-size: 0.88rem;
        font-weight: 600;
        color: #6B7280;
        margin-bottom: 0.35rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .stat-value {
        font-size: 1.7rem;
        font-weight: 800;
        color: #111827;
        line-height: 1.1;
        margin-bottom: 0.35rem;
    }

    .stat-desc {
        font-size: 0.9rem;
        line-height: 1.55;
        color: #4B5563;
    }

    .feature-card {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 20px;
        padding: 1.15rem 1.1rem;
        box-shadow: 0 1px 6px rgba(0,0,0,0.03);
        height: 100%;
    }

    .feature-card h4 {
        margin-top: 0;
        margin-bottom: 0.5rem;
        color: #111827;
        font-size: 1.05rem;
    }

    .feature-card p {
        margin-bottom: 0;
        color: #4B5563;
        font-size: 0.95rem;
        line-height: 1.65;
    }

    .highlight-box {
        background: #ECFDF5;
        border-left: 6px solid #00E68A;
        border-radius: 14px;
        padding: 1rem 1rem;
        color: #14532D;
        font-size: 0.96rem;
        line-height: 1.7;
    }

    .subtle-divider {
        height: 1px;
        background: linear-gradient(to right, transparent, #D1D5DB, transparent);
        margin-top: 1.2rem;
        margin-bottom: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="overview-hero">
    <div class="overview-title">Overview</div>
    <p class="overview-subtitle">
        A visual entry point into structural pass analysis. This page summarises the framework,
        the dataset, and the most important findings before you move into teams, players,
        pass archetypes, and passer–receiver relationships.
    </p>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("### Key Insights")
    st.markdown("""
    <div class="section-text">What structural pass analysis reveals about football passing behaviour.</div>
    """, unsafe_allow_html=True)
    st.markdown("""<p> <br> </p>""", unsafe_allow_html=True)


# --------------------------------------------------
# Insight cards (NOT KPIs)
# --------------------------------------------------
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="feature-card">
        <h4>Line-breaking drives progression</h4>
        <p>
            Line-breaking passes show the strongest relationship with
            final-third and box entries, highlighting their role in
            advancing play through defensive lines.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="feature-card">
        <h4>Defenders dominate TIV</h4>
        <p>
            Centre-backs such as <b>{summary["top_player_name"]}</b>
            generate the highest cumulative Tactical Impact Value,
            reflecting their role in build-up progression.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="feature-card">
        <h4>Passing partnerships matter</h4>
        <p>
            High ΔTIV combinations like <b>{summary["top_duo_label"]}</b>
            reveal structured progression channels within teams.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""<p> <br> </p>""", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("### Understanding the four structural pass archetypes")

    st.markdown("""
    <div class="section-text">
    The framework groups passes into four interpretable structural archetypes based on how they interact
    with defensive organisation. Rather than focusing only on outcomes, these categories describe the
    different tactical mechanisms through which passes maintain possession, destabilise shape, break lines,
    or exploit newly created space.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""<p> <br> </p>""", unsafe_allow_html=True)

# c1, c2, c3, c4 = st.columns(4, gap="small")

# with c1:
#     st.markdown("""
#     <div class="feature-card">
#         <h4>Circulatory</h4>
#         <p>Passes that help maintain possession with limited immediate structural change in the defensive block.</p>
#     </div>
#     """, unsafe_allow_html=True)

# with c2:
#     st.markdown("""
#     <div class="feature-card">
#         <h4>Destabilising</h4>
#         <p>Passes that subtly deform defensive organisation by shifting or stretching the structure.</p>
#     </div>
#     """, unsafe_allow_html=True)

# with c3:
#     st.markdown("""
#     <div class="feature-card">
#         <h4>Line-breaking</h4>
#         <p>Passes that penetrate defensive lines by bypassing players positioned between the ball and goal.</p>
#     </div>
#     """, unsafe_allow_html=True)

# with c4:
#     st.markdown("""
#     <div class="feature-card">
#         <h4>Space-expanding</h4>
#         <p>Passes that move the ball into regions with greater available attacking space and lower pressure.</p>
#     </div>
#     """, unsafe_allow_html=True)


def render_html_figure(path, height=360, scale=1.0):
    with open(path, "r", encoding="utf-8") as f:
        html_data = f.read()

    wrapped_html = f"""
    <div style="
        width: 100%;
        height: {height}px;
        overflow: hidden;
        background: white;
    ">
        <div style="
            transform: scale({scale});
            transform-origin: top left;
            width: {100/scale}%;
            height: {height/scale}px;
        ">
            {html_data}
        </div>
    </div>
    """
    components.html(wrapped_html, height=height, scrolling=False)


col1, col2 = st.columns([30, 68], gap="medium")
with col1:
        st.markdown("""
    <div class="highlight-box">
        <h4>Circulatory</h4>
        <p>Passes that help maintain possession with limited immediate structural change in the defensive block.</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    render_html_figure(
        "assets/figures/Figure_03_Pass_Types_circulatory.html",
        height=300,
        scale=0.625
    )
col1, col2 = st.columns([30, 68], gap="medium")
with col1:
        st.markdown("""
    <div class="highlight-box">
        <h4>Destabilising</h4>
        <p>Passes that subtly deform defensive organisation by shifting or stretching the structure.</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    render_html_figure(
        "assets/figures/Figure_03_Pass_Types_destabilising.html",
        height=300,
        scale=0.625
    )

col1, col2 = st.columns([30, 68], gap="medium")
with col1:
        st.markdown("""
    <div class="highlight-box">
        <h4>Line-breaking</h4>
        <p>Passes that penetrate defensive lines by bypassing players positioned between the ball and goal.</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    render_html_figure(
        "assets/figures/Figure_03_Pass_Types_line_breaking.html",
        height=300,
        scale=0.625
    )

col1, col2 = st.columns([30, 68], gap="medium")
with col1:
        st.markdown("""
    <div class="highlight-box">
        <h4>Space-expanding</h4>
        <p>Passes that move the ball into regions with greater available attacking space and lower pressure.</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    render_html_figure(
        "assets/figures/Figure_03_Pass_Types_space_expanding.html",
        height=300,
        scale=0.625
    )

# --------------------------------------------------
# Main chart
# --------------------------------------------------
st.markdown("""<p> <br> </p>""", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("### Distribution of Structural Pass Archetypes")

    fig = px.bar(
        pass_type_summary,
        x="pass_type_label",
        y="percentage",
        color="pass_type",
        color_discrete_map=PASS_TYPE_COLORS,
        text=pass_type_summary["percentage"].map(lambda x: f"{100*x:.1f}%"),
    )

    # -------------------------------
    # Bar styling
    # -------------------------------
    fig.update_traces(
        textposition="outside",
        textfont=dict(size=14, color="#111827"),
        marker=dict(line=dict(width=0)), width=0.99986,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Share of passes: %{y:.1%}<br>"
            "<extra></extra>"
        )
    )

    # -------------------------------
    # Layout styling
    # -------------------------------
    fig.update_layout(
        template="plotly_white",
        showlegend=True,
        legend_title="Pass Archetype",

        # Axes
        xaxis=dict(
            tickfont=dict(size=14, color="#374151"),
            showticklabels=False,
            showgrid=False,
        ),

        yaxis=dict(
            tickformat=".0%",
            title=dict(text="Share of passes", font=dict(size=14, color="#374151")),
            tickfont=dict(size=13, color="#374151"),
            showgrid=True,
            gridcolor="#E5E7EB",
            zeroline=False,
        ),

        # Margins
        margin=dict(t=60, l=40, r=20, b=40),

        # Bar spacing (IMPORTANT)
        bargap=0.015,        # space between bars
        bargroupgap=0.001,
        height=420,
    )

    # -------------------------------
    # Slight axis range padding (for labels)
    # -------------------------------
    fig.update_yaxes(range=[0, pass_type_summary["percentage"].max() * 1.15])
    fig.update_xaxes(title="")

    st.plotly_chart(fig)#, width='stretch')

# --------------------------------------------------
# Tactical takeaway
# --------------------------------------------------
st.markdown("""
<div class="highlight-box">
<b>Tactical takeaway</b><br>
Structural pass analysis shows that progression in football is not only about outcomes,
but about how teams reshape defensive organisation. The most impactful passes are those
that break lines, create space, and disrupt defensive structure — often initiated from
deep build-up zones.
</div>
""", unsafe_allow_html=True)

render_page_footer()