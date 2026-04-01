import streamlit as st
from utils.style import apply_global_style, apply_page_style, render_page_branding, render_page_footer
apply_page_style()
apply_global_style()
render_page_branding()


# --------------------------------------------------
# Page intro
# --------------------------------------------------
st.markdown("""
<div class="overview-hero">
    <div class="overview-title">Project Context</div>
    <p class="overview-subtitle">
Research context for BreakLines, Structural Passing, and the Tactical Intelligence Platform (T.I.P.).                </p>
            <div class="overview-subtitle">
            This page places the current dashboard within the broader BreakLines research programme and its
        role inside the Tactical Intelligence Platform (T.I.P.). Rather than serving as a technical manual,
        it provides the academic and conceptual framing behind the work, clarifying how Part I and Part II
        connect and how they contribute to a larger long-term research vision.
</div>
</div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# Optional page-specific CSS
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
    .section-title {
        font-size: 1.32rem;
        font-weight: 800;
        color: #111827;
        margin-top: 1.1rem;
        margin-bottom: 0.7rem;
    }

    .section-text {
        font-size: 1rem;
        line-height: 1.78;
        color: #4B5563;
        margin-bottom: 0.85rem;
        max-width: 980px;
    }

    .hero-box {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 45%, #E5E7EB 100%);
        border-radius: 24px;
        padding: 1.6rem 1.5rem 1.4rem 1.5rem;
        border: 1px solid #E5E7EB;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        color: #111827;
        margin-bottom: 0.4rem;
        line-height: 1.1;
    }

    .hero-sub {
        font-size: 1rem;
        line-height: 1.75;
        color: #4B5563;
        margin: 0;
        max-width: 980px;
    }

    .feature-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 18px;
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
        line-height: 1.7;
        font-size: 0.96rem;
    }

    .highlight-box {
        background: #ECFDF5;
        border-left: 6px solid #00E68A;
        border-radius: 14px;
        padding: 1rem 1rem;
        color: #14532D;
        font-size: 0.98rem;
        line-height: 1.75;
        margin-top: 0.9rem;
        margin-bottom: 1rem;
    }

    .subtle-divider {
        height: 1px;
        background: linear-gradient(to right, transparent, #D1D5DB, transparent);
        margin-top: 1.25rem;
        margin-bottom: 1.25rem;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# BreakLines in context
# --------------------------------------------------
st.markdown('### BreakLines Project', unsafe_allow_html=True)

st.markdown("""
<div class="section-text">
BreakLines is a research programme within the broader <b>Tactical Intelligence Platform (T.I.P.)</b>, 
aimed at quantifying how teams create and manipulate structure in football.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="section-text">
Rather than focusing solely on outcomes (e.g. shots, xG), the project investigates the <i>process</i> 
of attacking play, specifically how passing interactions reshape defensive organisation.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="section-text">
This dashboard presents <b>Part II</b> of the BreakLines project, focused on structural passing.
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="subtle-divider"></div>', unsafe_allow_html=True)

# --------------------------------------------------
# BreakLines project overview
# --------------------------------------------------
# st.markdown('<div class="section-title">The BreakLines project</div>', unsafe_allow_html=True)

st.markdown("""
<div class="section-text">
BreakLines is designed as a multi-stage framework for analysing progression in football:
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="section-text">
- identifying how passes interact with defensive lines<br>
- quantifying access to space and structural disruption<br>
- translating these effects into measurable tactical value
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="section-text">
The project moves from <i>event-level detection</i> to <i>structural understanding</i> of passing behaviour.
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Part I and Part II cards
# --------------------------------------------------
left, right = st.columns([1, 1.5], gap="small")

with left:
    st.markdown("""
    <div class="highlight-box">
        <h4>Part I — Line-breaking passes</h4>
        <p>
            The first stage of BreakLines focuses on detecting and quantifying <b>line-breaking passes</b> 
            using a graph-theoretic representation of defensive structure.<br><br>
            This work introduces:<br>
            - a formal definition of line-breaking behaviour<br>
            - a method for identifying passes that bypass defensive lines<br>
            - initial metrics capturing vertical progression<br><br>
            📄 Paper: <a href="https://arxiv.org/abs/2506.06666" target="_blank">https://arxiv.org/abs/2506.06666</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown("""
    <div class="highlight-box">
        <h4>Part II — Structural passing</h4>
        <p>
            Part II extends the framework beyond line-breaking to a broader structural perspective.<br><br>
            Instead of analysing passes only by penetration, it evaluates how they:<br>
            - bypass defensive lines (<b>LBS</b>)<br>
            - create access to space (<b>SGM</b>)<br>
            - disrupt defensive organisation (<b>SDI</b>)<br><br>
            These components are combined into <b>Tactical Impact Value (TIV)</b> and used to identify 
            distinct <b>pass archetypes</b>.<br><br>
            This dashboard provides an interactive view of these structural behaviours across teams, players, and passing duos.<br><br>
            📄 Paper: <a href="https://arxiv.org/abs/2603.28916" target="_blank">https://arxiv.org/abs/2603.28916</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="subtle-divider"></div>', unsafe_allow_html=True)

# --------------------------------------------------
# TIP
# --------------------------------------------------
st.markdown('### Tactical Intelligence Platform (T.I.P.)', unsafe_allow_html=True)

st.markdown("""
<div class="section-text">
Tactical Intelligence Platform (T.I.P.) is a research-driven AI framework that is currently under development by Dead Ball Analytics 
to transform football tracking data into meaningful tactical insights. By capturing team structure, spatial 
organisation, and match dynamics over time, T.I.P. enables a deeper understanding of how the game is played 
beyond traditional event-based analysis.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="section-text">
Designed as a modular and evolving system, the platform will form the foundation for a new generation of 
data-driven tools supporting performance analysis, player evaluation, and recruitment strategy. Projects 
such as BreakLines represent early applications of this vision, with further developments aimed at advancing 
the way football is analysed, interpreted, and understood.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="highlight-box">
<b>Why this matters:</b><br>
BreakLines should not be viewed only as a standalone paper or dashboard. It is an early research application
within a broader tactical AI ecosystem, where structural representations, spatio-temporal modelling, and
interpretable football intelligence are brought together under the T.I.P. vision.
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="subtle-divider"></div>', unsafe_allow_html=True)

# --------------------------------------------------
# How this dashboard fits
# --------------------------------------------------
st.markdown('### How this dashboard fits the project', unsafe_allow_html=True)

st.markdown("""
<div class="section-text">
The dashboard is designed as an <b>interactive companion</b> to Part II of the BreakLines project.
It does not attempt to reproduce the full paper. Instead, it translates the main ideas into an
explorable visual environment where users can investigate:
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="section-text">
- structural pass archetypes<br>
- team-level structural styles<br>
- player-level structural profiles<br>
- passer-receiver relationships and duo effects
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="section-text">
In this sense, the dashboard acts as a bridge between formal academic work and applied tactical interpretation.
It is intended to support communication, exploration, and demonstration of the ideas introduced in the project.
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="subtle-divider"></div>', unsafe_allow_html=True)

# --------------------------------------------------
# Citation
# --------------------------------------------------
st.markdown('### Citation', unsafe_allow_html=True)

st.markdown("""
<div class="section-text">
If you use this work, please cite:
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="highlight-box">
    <h4>BreakLines — Part I</h4>
    <h4>Through the Gaps: Uncovering Tactical Line-Breaking Passes with Clustering</h4>
    <p>
        Oktay Karakus & Hasan Arkadas (2025)<br>
        <i> In International Workshop on Machine Learning and Data Mining for Sports Analytics (ECML/PKDD 2025)</i><br>
        This paper introduces the line-breaking pass detection framework and initial metrics for vertical progression.<br>
        <a href="https://arxiv.org/abs/2506.06666" target="_blank">https://arxiv.org/abs/2506.06666</a>
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="height: 0.8rem;"></div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="highlight-box">
    <h4>BreakLines — Part II</h4>
    <h4>Structural Pass Analysis in Football: Learning Pass Archetypes and Tactical Impact from Spatio-Temporal Tracking Data</h4>
    <p>
        Oktay Karakus & Hasan Arkadas (2026)<br>
        <i> Under Review — preprint available on arXiv</i><br>
        This dashboard serves as an interactive companion to the research.<br>
    <a href="https://arxiv.org/abs/2603.28916" target="_blank">https://arxiv.org/abs/2603.28916</a>
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="subtle-divider"></div>', unsafe_allow_html=True)

# --------------------------------------------------
# Closing note
# --------------------------------------------------
st.markdown('### Closing note', unsafe_allow_html=True)

st.markdown("""
<div class="section-text">
BreakLines represents an effort to move football analytics beyond isolated outcomes and toward a more structural,
interpretable understanding of tactical behaviour. By linking Part I and Part II under the broader T.I.P. vision,
the project aims to establish a long-term research pathway for modelling football as a dynamic system of spatial
organisation, interaction, and tactical intelligence.
</div>
""", unsafe_allow_html=True)

render_page_footer()