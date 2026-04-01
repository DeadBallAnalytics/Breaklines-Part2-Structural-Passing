import re
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import base64
from utils.loaders import load_player_summary
from utils.style import apply_global_style, render_page_branding, render_page_footer, apply_page_style
apply_page_style()
apply_global_style()
render_page_branding()

import numpy as np
from plotly.subplots import make_subplots

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def get_base64_image(image_path):
    if image_path is None:
        return None
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def percentile_rank(series, value):
    s = pd.Series(series).dropna().astype(float)
    if len(s) == 0:
        return np.nan
    return 100.0 * (s <= float(value)).mean()
# --------------------------------------------------
# Helpers
# --------------------------------------------------
def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "_", text)
    return text

import re
import unicodedata
from pathlib import Path
from difflib import SequenceMatcher

def normalize_name(text: str) -> str:
    text = str(text).strip()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s_]+", "_", text)
    return text.strip("_")

import re
import unicodedata
from pathlib import Path

def normalize_text(text: str) -> str:
    text = str(text).strip()
    text = text.replace("\xa0", " ")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s_-]", "", text)
    text = re.sub(r"[\s_-]+", " ", text).strip()
    return text

def compact_token(token: str) -> str:
    return re.sub(r"[^a-z0-9]", "", normalize_text(token))

def name_tokens(text: str):
    norm = normalize_text(text)
    return [compact_token(t) for t in norm.split() if compact_token(t)]

def get_player_photo_path(player_name: str, team_name: str):
    base_dir = Path("assets/player_photos_web")

    # Resolve team folder robustly
    team_folder = None
    target_team = normalize_text(team_name)

    for folder in base_dir.iterdir():
        if folder.is_dir() and normalize_text(folder.name) == target_team:
            team_folder = folder
            break

    if team_folder is None:
        return None

    files = [
        p for p in team_folder.iterdir()
        if p.is_file() and p.suffix.lower() in [".png", ".webp"]
    ]
    if not files:
        return None

    target_tokens = name_tokens(player_name)
    target_set = set(target_tokens)

    best_match = None
    best_score = -1

    for p in files:
        stem_tokens = name_tokens(p.stem)
        stem_set = set(stem_tokens)

        # Base exact token overlap
        overlap = len(target_set & stem_set)

        # Stronger score if all tokens match exactly
        exact_score = 100 if target_set == stem_set else 0

        # Partial token similarity for cases like:
        # Young-gwon -> Younggwon
        # Woo-young -> Wooyoung
        partial_score = 0
        for t in target_tokens:
            for s in stem_tokens:
                if t == s:
                    partial_score += 10
                elif t in s or s in t:
                    partial_score += 6

        score = exact_score + overlap * 10 + partial_score

        if score > best_score:
            best_score = score
            best_match = p

    # Require a minimum score to avoid bad matches
    if best_score >= 20:
        return str(best_match)

    return None


def get_team_flag_path(team_name: str):
    base_dir = Path("assets/flags")
    target = normalize_name(team_name)

    for p in base_dir.iterdir():
        if p.is_file() and p.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
            if normalize_name(p.stem) == target:
                return str(p)

    return None


def pretty_pass_type(x):
    return str(x).replace("_", " ").title()


def normalize_size(series, min_size=14, max_size=42):
    if series.nunique() <= 1:
        return pd.Series([(min_size + max_size) / 2] * len(series), index=series.index)
    s = (series - series.min()) / (series.max() - series.min())
    return min_size + s * (max_size - min_size)


# --------------------------------------------------
# Load data
# --------------------------------------------------
players = load_player_summary().copy()

# Safety + labels
players["dominant_pass_type_label"] = players["dominant_pass_type"].apply(pretty_pass_type)
players["player_label"] = players["passer_name"] + " (" + players["team_name"] + ")"

# --------------------------------------------------
# CSS
# --------------------------------------------------
st.markdown("""
<style>
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 22px !important;
    background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 45%, #E5E7EB 100%) !important;
    border: 1px solid #E5E7EB !important;
    padding: 0.8rem 1rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03) !important;
}

.player-hero-title {
    font-size: 2rem;
    font-weight: 800;
    color: #111827;
    margin-bottom: 0.25rem;
    line-height: 1.1;
}

.player-hero-sub {
    font-size: 0.96rem;
    line-height: 1.7;
    color: #4B5563;
}
</style>
""", unsafe_allow_html=True)

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
        font-size: 1.28rem;
        font-weight: 800;
        color: #111827;
        margin-top: 1rem;
        margin-bottom: 0.75rem;
    }

    .section-text {
        font-size: 0.98rem;
        line-height: 1.7;
        color: #4B5563;
        margin-bottom: 0.8rem;
        max-width: 980px;
    }
    .metric-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 18px;
        padding: 1rem 1rem 0.9rem 1rem;
        box-shadow: 0 1px 6px rgba(0,0,0,0.03);
        height: 100%;
    }

    .metric-label {
        font-size: 0.88rem;
        font-weight: 600;
        color: #6B7280;
        margin-bottom: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .metric-value {
        font-size: 1.5rem;
        font-weight: 800;
        color: #111827;
        margin-bottom: 0.12rem;
        line-height: 1.1;
    }

    .metric-sub {
        font-size: 0.88rem;
        color: #4B5563;
        line-height: 1.5;
    }

    .feature-card {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 18px;
        padding: 1.1rem 1rem;
        box-shadow: 0 1px 6px rgba(0,0,0,0.03);
        height: 100%;
    }

    .feature-card h4 {
        margin-top: 0;
        margin-bottom: 0.45rem;
        color: #111827;
        font-size: 1.02rem;
    }

    .feature-card p {
        margin-bottom: 0;
        color: #4B5563;
        line-height: 1.65;
        font-size: 0.95rem;
    }

    .highlight-box {
        background: #ECFDF5;
        border-left: 6px solid #00E68A;
        border-radius: 14px;
        padding: 1rem 1rem;
        color: #14532D;
        line-height: 1.7;
        font-size: 0.95rem;
        margin-bottom: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.player-hero {
    background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 45%, #E5E7EB 100%);
    border-radius: 24px;
    padding: 1.4rem 1.4rem;
    border: 1px solid #E5E7EB;
    margin-bottom: 1rem;
}

.player-hero-grid {
    display: grid;
    grid-template-columns: 1.2fr 4fr 1fr;
    align-items: center;
    gap: 1rem;
}

.player-hero-photo img {
    width: 140px;
    height: auto;
    border-radius: 14px;
}

.player-hero-flag img {
    width: 90px;
    height: auto;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Page intro
# --------------------------------------------------
st.markdown("""
<div class="overview-hero">
    <div class="overview-title">Player Analysis</div>
    <p class="overview-subtitle">
            Identify which players generate structural value through passing, and how they differ stylistically.
    </p>
            <div class="overview-subtitle">
This page profiles players through their structural passing behaviour. Explore how players differ in
line-breaking, space creation, disruption, and Tactical Impact Value, and compare who contributes the
most to progression at both the per-pass and cumulative level.
</div>
</div>
</div>
""", unsafe_allow_html=True)

filtered = players.copy()
# --------------------------------------------------
# Featured player
# --------------------------------------------------
with st.container(border=True):
    st.markdown('### Filters</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    teams = ["All"] + sorted(players["team_name"].dropna().unique().tolist())
    selected_team = c1.selectbox("Team", teams)

    if selected_team == "All":
        available_players = ["All"] + sorted(players["passer_name"].dropna().unique().tolist())
    else:
        available_players = ["All"] + sorted(
            players.loc[players["team_name"] == selected_team, "passer_name"].dropna().unique().tolist()
        )

    selected_player = c2.selectbox("Player", available_players)
    

    if selected_player != "All":
        selected_rows = filtered.loc[filtered["passer_name"] == selected_player]
        if not selected_rows.empty:
            featured_row = selected_rows.iloc[0]
        else:
            featured_row = filtered.sort_values("total_tiv", ascending=False).iloc[0]
    else:
        featured_row = filtered.sort_values("total_tiv", ascending=False).iloc[0]

    flag_path = get_team_flag_path(featured_row["team_name"])
    player_path = get_player_photo_path(featured_row["passer_name"], featured_row["team_name"])

    flag_b64 = get_base64_image(flag_path)
    player_b64 = get_base64_image(player_path)

    player_img_html = (
        f'<img class="player-logo" src="data:image/png;base64,{player_b64}" />'
        if player_b64 else ""
    )

    flag_img_html = (
        f'<img class="flag-logo" src="data:image/png;base64,{flag_b64}" />'
        if flag_b64 else ""
    )
    st.markdown(f"""
        <div class="custom-bg-container">
        <div class="player-hero-title">{featured_row['passer_name']} ({featured_row['team_name']})</div>""", 
        unsafe_allow_html=True)

    hero_left, hero_right = st.columns([1.9, 4.25], gap="medium")
    with hero_left:
    #     if featured_photo:
    #         st.image(featured_photo, width=250)
    # with hero_right:
        st.markdown(f"""
            <div class="custom-bg-container">
                <div class="player-logo-wrap">
            {player_img_html}
        </div>
            </div>""", 
            unsafe_allow_html=True)
    with hero_right:
        st.markdown(f"""
        <div class="custom-bg-container">
        <div class="player-hero-sub">
            <u>Dominant archetype:</u> <b>{featured_row['dominant_pass_type_label']}</b>
        </div>
        <div class="flag-logo-wrap">
            {flag_img_html}
        </div>
            <br>This profile highlights how the player contributes to progression through 
            <b>line-breaking</b>, <b>space gain</b>, <b>defensive disruption</b>, and 
            <b>Tactical Impact Value (TIV)</b>, capturing both the consistency and 
            magnitude of their structural influence in possession.
        
        </div>
        """,
        unsafe_allow_html=True,
    )

# with hero_right:
#     if featured_flag:
#         st.image(featured_flag, width=295)

# Add this CSS block anywhere in your file (e.g., after imports)
st.markdown("""
<style>
.custom-bg-container {
    background-color: #00E68A44; 
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 1rem;
}
.player-logo {
    width: 360px;
    max-width: 100%;
    height: auto;
}
.player-logo-wrap {
        text-align: left;
}
.flag-logo {
    width: 100px;
    max-width: 100%;
    height: auto;
}
.flag-logo-wrap {
        text-align: left;
}
</style>
""", unsafe_allow_html=True)
# --------------------------------------------------
# KPI cards
# --------------------------------------------------
with st.container(border=True):
    st.markdown('### Player profile at a glance</div>', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4, gap="small")

    with k1:
        st.markdown(f"""
        <div class="highlight-box">
            <div class="metric-label">Passes</div>
            <div class="metric-value">{int(featured_row['n_passes']):,}</div>
            <div class="metric-sub">Number of analysed passes by the player.</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="highlight-box">
            <div class="metric-label">Mean TIV</div>
            <div class="metric-value">{featured_row['mean_tiv']:.2f}</div>
            <div class="metric-sub">Average structural impact per pass.</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="highlight-box">
            <div class="metric-label">Total TIV</div>
            <div class="metric-value">{featured_row['total_tiv']:.2f}</div>
            <div class="metric-sub">Cumulative structural contribution.</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="highlight-box">
            <div class="metric-label">Dominant Archetype</div>
            <div class="metric-value" style="font-size:1.15rem;">{featured_row['dominant_pass_type_label']}</div>
            <div class="metric-sub">Most frequent structural pass type.</div>
        </div>
        """, unsafe_allow_html=True)

# --------------------------------------------------
# Filters
# --------------------------------------------------    


# --------------------------------------------------
# Main player explorer
# --------------------------------------------------
with st.container(border=True):

    st.markdown('### Structural player space</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([1, 1.1, 0.8, 1, 1.3], gap="small")

    min_passes = c1.slider("Minimum passes", 1, int(players["n_passes"].max()), 20)

    size_options = {
        "Pass Volume": "n_passes",
        "Total TIV": "total_tiv",
        "Mean TIV": "mean_tiv",
    }
    selected_size_label = c2.selectbox("Bubble size", list(size_options.keys()), index=0)

    axis_options = {
        "Mean LBS": "mean_lbs",
        "Mean SGM": "mean_sgm",
        "Mean SDI": "mean_sdi",
        "Mean TIV": "mean_tiv",
        "Total TIV": "total_tiv",
        "Pass Volume": "n_passes",
    }
    x_axis_label = c3.selectbox("X-axis", list(axis_options.keys()), index=0)
    y_axis_label = c4.selectbox("Y-axis", list(axis_options.keys()), index=1)
    color_by_label = c5.selectbox(
        "Color by",
        ["Mean TIV", "Total TIV", "Dominant Archetype", "Team"],
        index=0
    )

    x_col = axis_options[x_axis_label]
    y_col = axis_options[y_axis_label]
    size_col = size_options[selected_size_label]

    if size_col == "n_passes":
        size_values = filtered[size_col].apply(lambda x: pd.np.log1p(x) if hasattr(pd, "np") else x)
    else:
        size_values = filtered[size_col]

    filtered["size_scaled"] = normalize_size(size_values)
    filtered = filtered[filtered["n_passes"] >= min_passes]

    custom_cols = [
        "team_name",
        "n_passes",
        "mean_tiv",
        "total_tiv",
        "mean_lbs",
        "mean_sgm",
        "mean_sdi",
        "dominant_pass_type_label",
           "passer_name"   ]

    PASS_TYPE_COLORS = {
        "circulatory": "#9CA3AF",        # neutral grey
        "destabilising": "#F59E0B",      # amber / orange
        "line_breaking": "#00E68A",      # DeadBall green (primary)
        "space_expanding": "#3B82F6",    # blue
    }

    PASS_TYPE_LABELS = {
        "circulatory": "Circulatory",
        "destabilising": "Destabilising",
        "line_breaking": "Line-breaking",
        "space_expanding": "Space-expanding",
    }

    PASS_TYPE_ORDER = [
        "circulatory",
        "destabilising",
        "line_breaking",
        "space_expanding",
    ]

    if color_by_label == "Dominant Archetype":
        fig = px.scatter(
            filtered,
            x=x_col,
            y=y_col,
            size="size_scaled",
            color="dominant_pass_type",
            color_discrete_map={
                "circulatory": PASS_TYPE_COLORS["circulatory"],
                "destabilising": PASS_TYPE_COLORS["destabilising"],
                "line_breaking": PASS_TYPE_COLORS["line_breaking"],
                "space_expanding": PASS_TYPE_COLORS["space_expanding"],
            },
            custom_data=custom_cols,
            labels={
                x_col: x_axis_label,
                y_col: y_axis_label,
                "dominant_pass_type": "Dominant Archetype"
            },
            opacity=0.82,
            title=f"{x_axis_label} vs {y_axis_label}",
        )
    elif color_by_label == "Team":
        fig = px.scatter(
            filtered,
            x=x_col,
            y=y_col,
            size="size_scaled",
            color="team_name",
            custom_data=custom_cols,
            labels={
                x_col: x_axis_label,
                y_col: y_axis_label,
                "team_name": "Team"
            },
            opacity=0.82,
            title=f"{x_axis_label} vs {y_axis_label}",
        )
    else:
        color_map = {
            "Mean TIV": "mean_tiv",
            "Total TIV": "total_tiv",
        }
        color_col = color_map[color_by_label]

        fig = px.scatter(
            filtered,
            x=x_col,
            y=y_col,
            size="size_scaled",
            color=color_col,
            color_continuous_scale="Viridis",
            custom_data=custom_cols,
            labels={
                x_col: x_axis_label,
                y_col: y_axis_label,
                color_col: color_by_label,
            },
            opacity=0.82,
            title=f"{x_axis_label} vs {y_axis_label}",
        )

    fig.update_traces(
        marker=dict(line=dict(width=0.8, color="white")),
        hovertemplate=(
            "<b>%{customdata[8]}</b><br>"
            "Team: <b>%{customdata[0]}</b><br>"
            "TIV (avg): %{customdata[2]:.2f}<br>"
            "TIV (total): %{customdata[3]:.2f}<br>"
            "LBS (avg) %{customdata[4]:.2f}<br>"
            "SGM (avg): %{customdata[5]:.2f}<br>"
            "SDI (avg): %{customdata[6]:.2f}<br>"
            "Archetype: <b>%{customdata[7]}</b><br>"
            "# Passes: %{customdata[1]:.0f}"
            "<extra></extra>"
        )
    )
    
    # Highlight selected/featured player
    fig.add_trace(
        go.Scatter(
            x=[featured_row[x_col]],
            y=[featured_row[y_col]],
            mode="markers+text",
            text=[featured_row["passer_name"]],
            textposition="top center",
            marker=dict(
                size=24,
                color="#111827",
                line=dict(width=3, color="#00E68A"),
                symbol="circle-open-dot",
            ),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        template="plotly_white",
        title_x=0.0,
        height=560,
        margin=dict(t=60, l=20, r=20, b=20),
        font=dict(size=12),
        legend_title_text="",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#E5E7EB", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#E5E7EB", zeroline=False)

    st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class="highlight-box">
<b>How to read this figure:</b> each point is a player. Use the axis, color, and bubble-size controls
to compare structural roles across players and teams. The highlighted marker shows the currently featured player.
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Secondary visuals
# --------------------------------------------------
with st.container(border=True):
    st.markdown('### Distribution and stylistic mix</div>', unsafe_allow_html=True)

    left, right = st.columns([1.4, 1], gap="small")

    with left:
        tiv_df = filtered.copy()

        fig_tiv = px.box(
            tiv_df,
            # x="dominant_pass_type_label",
            y="mean_tiv",
            color="dominant_pass_type",
            color_discrete_map={
                "circulatory": PASS_TYPE_COLORS["circulatory"],
                "destabilising": PASS_TYPE_COLORS["destabilising"],
                "line_breaking": PASS_TYPE_COLORS["line_breaking"],
                "space_expanding": PASS_TYPE_COLORS["space_expanding"],
            },
            labels={
                "dominant_pass_type_label": "",
                "mean_tiv": "Mean TIV"
            },
            title="Mean TIV by dominant player archetype",
            points="all",
        )
        
        fig_tiv.update_layout(
            template="plotly_white",
            title_x=0.0,
            height=430,
            margin=dict(t=60, l=20, r=20, b=20),
            showlegend=False,
            font=dict(size=12),
        )
        fig_tiv.update_xaxes(showgrid=False)
        fig_tiv.update_yaxes(showgrid=True, gridcolor="#E5E7EB", zeroline=False)
        fig_tiv.update_traces(hoverinfo="skip",
            hovertemplate="<b>%{x}</b><br>TIV (avg): %{y:.2f}<extra></extra>"
        )
        st.plotly_chart(fig_tiv, use_container_width=True)

    with right:
        style_mix = (
            filtered["dominant_pass_type"]
            .value_counts(normalize=True)
            .reindex(["circulatory", "destabilising", "line_breaking", "space_expanding"], fill_value=0)
            .reset_index()
        )
        style_mix.columns = ["pass_type", "proportion"]
        style_mix["pass_type_label"] = style_mix["pass_type"].apply(pretty_pass_type)

        fig_mix = px.pie(
            style_mix,
            names="pass_type_label",
            values="proportion",
            color="pass_type",
            color_discrete_map={
                "circulatory": PASS_TYPE_COLORS["circulatory"],
                "destabilising": PASS_TYPE_COLORS["destabilising"],
                "line_breaking": PASS_TYPE_COLORS["line_breaking"],
                "space_expanding": PASS_TYPE_COLORS["space_expanding"],
            },
            hole=0.08,
        )

        fig_mix.update_traces(
            textinfo="percent",
            textfont=dict(size=15, color="white"),
            marker=dict(line=dict(color="white", width=2)),
            hovertemplate="<b>%{label}</b><br>Share: %{percent}<extra></extra>",
            sort=False
        )

        fig_mix.update_layout(
            template="plotly_white",
            title=dict(
                text="Dominant archetype mix",
                x=0.0,
                xanchor="left",
                font=dict(size=18, color="#111827"),
            ),
            height=430,
            margin=dict(t=60, l=20, r=20, b=20),
            font=dict(size=12),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.37,
                xanchor="center",
                x=0.5,
                title="",
                font=dict(size=14),
            ),
            # annotations=[
            #     dict(
            #         text="Player<br>mix",
            #         x=0.5,
            #         y=0.5,
            #         font=dict(size=16, color="#374151"),
            #         showarrow=False
            #     )
            # ]
        )

        st.plotly_chart(fig_mix, use_container_width=True)

# --------------------------------------------------
# Ranking board
# --------------------------------------------------
with st.container(border=True):
    st.markdown("### Player ranking board")

    sort_options = {
        "Total TIV": "total_tiv",
        "Mean TIV": "mean_tiv",
        "Mean LBS": "mean_lbs",
        "Mean SGM": "mean_sgm",
        "Mean SDI": "mean_sdi",
        "Pass Volume": "n_passes",
    }

    c1, c2 = st.columns([1, 1])
    sort_label = c1.selectbox("Sort by", list(sort_options.keys()), index=0)
    top_n = c2.slider("Top N players", 5, 40, 15)

    table = (
        filtered.sort_values(sort_options[sort_label], ascending=False)
        .head(top_n)
        .copy()
    )

    table = table[[
        "passer_name",
        "team_name",
        "n_passes",
        "mean_tiv",
        "total_tiv",
        "mean_lbs",
        "mean_sgm",
        "mean_sdi",
        "dominant_pass_type_label",
    ]].rename(columns={
        "passer_name": "Player",
        "team_name": "Team",
        "n_passes": "Passes",
        "mean_tiv": "Mean TIV",
        "total_tiv": "Total TIV",
        "mean_lbs": "Mean LBS",
        "mean_sgm": "Mean SGM",
        "mean_sdi": "Mean SDI",
        "dominant_pass_type_label": "Dominant Archetype",
    })

    numeric_cols = [
        "Passes",
        "Mean TIV",
        "Total TIV",
        "Mean LBS",
        "Mean SGM",
        "Mean SDI",
    ]

    def color_scale(series):
        s = series.astype(float)
        denom = (s.max() - s.min())
        if denom == 0:
            norm = pd.Series([0.5] * len(s), index=s.index)
        else:
            norm = (s - s.min()) / denom

        styles = []
        for v in norm:
            # light grey-green -> dark green
            r = int(240 - v * 160)
            g = int(248 - v * 35)
            b = int(244 - v * 120)

            # darker background => white text
            text_color = "#FFFFFF" if v > 0.55 else "#111827"
            styles.append(f"background-color: rgb({r},{g},{b}); color: {text_color};")
        return styles

    styled_table = (
        table.style
        .apply(color_scale, subset=numeric_cols)
        .format({
            "Passes": "{:,.0f}",
            "Mean TIV": "{:.2f}",
            "Total TIV": "{:.2f}",
            "Mean LBS": "{:.2f}",
            "Mean SGM": "{:.2f}",
            "Mean SDI": "{:.2f}",
        })
        .set_properties(**{
            "text-align": "center",
            "font-size": "13px",
        })
        .set_properties(subset=["Player", "Team", "Dominant Archetype"], **{
            "text-align": "left"
        })
    )

    st.dataframe(
        styled_table,
        use_container_width=True,
        height=520,
    )

# --------------------------------------------------
# Tactical reading
# --------------------------------------------------
with st.container(border=True):
    st.markdown('### Tactical reading', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    selected_team2 = c1.selectbox("Team for Card", teams)

    if selected_team2 == "All":
        available_players2 = ["All"] + sorted(players["passer_name"].dropna().unique().tolist())
    else:
        available_players2 = ["All"] + sorted(
            players.loc[players["team_name"] == selected_team2, "passer_name"].dropna().unique().tolist()
        )

    selected_player2 = c2.selectbox("Player for Card", available_players2)
    

    if selected_player2 != "All":
        selected_rows2 = filtered.loc[filtered["passer_name"] == selected_player2]
        if not selected_rows2.empty:
            featured_row2 = selected_rows2.iloc[0]
        else:
            featured_row2 = filtered.sort_values("total_tiv", ascending=False).iloc[0]
    else:
        featured_row2 = filtered.sort_values("total_tiv", ascending=False).iloc[0]

    flag_path2 = get_team_flag_path(featured_row2["team_name"])
    player_path2 = get_player_photo_path(featured_row2["passer_name"], featured_row2["team_name"])

    flag_b642 = get_base64_image(flag_path2)
    player_b642 = get_base64_image(player_path2)

    player_img_html2 = (
        f'<img class="player-logo" src="data:image/png;base64,{player_b642}" />'
        if player_b642 else ""
    )

    flag_img_html2 = (
        f'<img class="flag-logo" src="data:image/png;base64,{flag_b642}" />'
        if flag_b642 else ""
    )
    st.markdown(f"""
    <div class="highlight-box">
        <h4>What stands out about {featured_row2['passer_name']}?</h4>
        <p>
            {featured_row2['passer_name']} profiles as a <b>{featured_row2['dominant_pass_type_label']}</b>-leaning passer
            for <b>{featured_row2['team_name']}</b>, with a mean Tactical Impact Value of <b>{featured_row2['mean_tiv']:.2f}</b>
            across <b>{int(featured_row2['n_passes'])}</b> analysed passes. Use the scatter plot to position this player
            against teammates or tournament peers, and the ranking board to identify who contributes most through
            structural progression.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------------------
    # Tactical reading
    # --------------------------------------------------

    st.markdown('### Featured player card', unsafe_allow_html=True)

    # Use full competition context, but keep minimum passes filter for fairness
    competition_pool = players.copy()
    competition_pool = competition_pool[competition_pool["n_passes"] >= min_passes].copy()

    # --------------------------------------------------
    # Percentile metrics for the featured player
    # --------------------------------------------------
    percentile_metrics = {
        "Pass Volume": "n_passes",
        "Mean TIV": "mean_tiv",
        "Total TIV": "total_tiv",
        "Mean LBS": "mean_lbs",
        "Mean SGM": "mean_sgm",
        "Mean SDI": "mean_sdi",
        "Shot Prob.": "shot_prob",
        "Box Entry Prob.": "box_entry_prob",
    }

    player_percentiles = {}
    avg_percentiles = {}

    for label, col in percentile_metrics.items():
        player_percentiles[label] = percentile_rank(competition_pool[col], featured_row2[col])
        avg_percentiles[label] = percentile_rank(competition_pool[col], competition_pool[col].mean())

    card_df = pd.DataFrame({
        "metric": list(percentile_metrics.keys()),
        "player_pct": list(player_percentiles.values()),
        "avg_pct": list(avg_percentiles.values()),
    })

    # close loop for scatterpolar line
    theta_closed = card_df["metric"].tolist() + [card_df["metric"].tolist()[0]]
    avg_closed = card_df["avg_pct"].tolist() + [card_df["avg_pct"].tolist()[0]]

    # --------------------------------------------------
    # Competition rankings
    # --------------------------------------------------
    rank_cols = ["total_tiv", "mean_tiv", "mean_lbs", "mean_sgm", "mean_sdi", "n_passes"]
    rankings = {}
    for col in rank_cols:
        rankings[col] = int(
            competition_pool[col]
            .rank(method="min", ascending=False)
            .loc[competition_pool["passer_name"] == featured_row2["passer_name"]]
            .iloc[0]
        ) if (competition_pool["passer_name"] == featured_row2["passer_name"]).any() else None

    n_players_comp = len(competition_pool)

    # --------------------------------------------------
    # Build handcrafted Plotly card
    # --------------------------------------------------
    fig_card = make_subplots(
        rows=1,
        cols=1,
        specs=[[{"type": "polar"}]],
    )

    # Barpolar = player percentile profile
    fig_card.add_trace(
        go.Barpolar(
            r=card_df["player_pct"],
            theta=card_df["metric"],
            # width=[22] * len(card_df),
            marker=dict(
                color=card_df["player_pct"],
                colorscale=[
                    [0.00, "#D1FAE5"],
                    [0.35, "#86EFAC"],
                    [0.70, "#22C55E"],
                    [1.00, "#166534"],
                ],
                line=dict(color="white", width=2.5),
                cmin=0,
                cmax=100,
            ),
            opacity=0.62,
            name="Player percentile",
            hovertemplate="<b>%{theta}</b><br>Player percentile: %{r:.0f}<extra></extra>",
            subplot="polar",
        )
    )

    # Scatterpolar = tournament average baseline percentile
    fig_card.add_trace(
        go.Scatterpolar(
            r=avg_closed,
            theta=theta_closed,
            mode="lines+markers",
            line=dict(color="#111827", width=2.5, dash="dash"),
            marker=dict(size=9, color="#111827"), #fill="toself", fillcolor="#111827", opacity=0.38,
            name="Tournament average percentile",
            hovertemplate="<b>%{theta}</b><br>Average percentile baseline: %{r:.0f}<extra></extra>",
            subplot="polar",
        )
    )

    # --------------------------------------------------
    # Layout styling
    # --------------------------------------------------
    CARD_W = 1000
    CARD_H = 820

    fig_card.update_layout(
        width=CARD_W,
        height=CARD_H,
        paper_bgcolor="#F8FAFC",
        plot_bgcolor="#F8FAFC",
        margin=dict(l=40, r=40, t=40, b=30),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.2,
            xanchor="right",
            x=0.98,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12, color="#111827"),
            title=""
        ),
        polar=dict(
            domain=dict(x=[0.4, 0.9], y=[0.27, 0.8]),
            bgcolor="#FFFFFF",
            radialaxis=dict(
                range=[0, 100],
                tickvals=[20, 40, 60, 80, 100],
                ticktext=["20", "40", "60", "80", "100"],
                angle=0,
                gridcolor="#E5E7EB",
                tickfont=dict(size=12, color="#3B4240"),
                showline=False,
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color="#111827"),
                gridcolor="#F3F4F6",
                direction="clockwise",
                rotation=90,
            )
        ),
        annotations=[],
        shapes=[],
    )

    # --------------------------------------------------
    # Background panels / structure
    # --------------------------------------------------
    # Main card panel
    fig_card.add_shape(
        type="rect",
        xref="paper", yref="paper",
        x0=0.0, x1=1.0, y0=0.0, y1=1.0,
        line=dict(color="#E5E7EB", width=1),
        fillcolor="#F8FAFC",
        layer="below"
    )

    # Header strip
    fig_card.add_shape(
        type="rect",
        xref="paper", yref="paper",
        x0=0.0, x1=1.0, y0=0.88, y1=1.0,
        line=dict(color="#111827", width=0),
        fillcolor="#00E68A", opacity=0.45,
        layer="below"
    )

    # # Left photo panel
    # fig_card.add_shape(
    #     type="rect",
    #     xref="paper", yref="paper",
    #     x0=0.01, x1=0.25, y0=0.55, y1=0.84,
    #     line=dict(color="#E5E7EB", width=1),
    #     fillcolor="#FFFFFF",
    #     layer="below"
    # )

    # # Text/stats panel
    # fig_card.add_shape(
    #     type="rect",
    #     xref="paper", yref="paper",
    #     x0=0.01, x1=0.25, y0=0.06, y1=0.5,
    #     line=dict(color="#E5E7EB", width=1),
    #     fillcolor="#FFFFFF",
    #     layer="below"
    # )

    # # Right top flag panel
    # fig_card.add_shape(
    #     type="rect",
    #     xref="paper", yref="paper",
    #     x0=0.84, x1=0.98, y0=0.88, y1=1.00,
    #     line=dict(color="#111827", width=0),
    #     fillcolor="#00E68A", opacity=0.45,
    #     layer="below"
    # )

    # --------------------------------------------------
    # Images
    # --------------------------------------------------
    if player_b64:
        fig_card.add_layout_image(
            dict(
                source=f"data:image/png;base64,{player_b642}",
                xref="paper", yref="paper",
                x=0.13, y=0.835,
                sizex=0.225, sizey=0.385,
                xanchor="center", yanchor="top",
                layer="above",
                sizing="contain",
            )
        )

    if flag_b64:
        fig_card.add_layout_image(
            dict(
                source=f"data:image/png;base64,{flag_b642}",
                xref="paper", yref="paper",
                x=0.91, y=0.945,
                sizex=0.13, sizey=0.13,
                xanchor="center", yanchor="middle",
                layer="above",
                sizing="contain",
            )
        )

    # --------------------------------------------------
    # Header text
    # --------------------------------------------------
    fig_card.add_annotation(
        x=0.03, y=0.985,
        xref="paper", yref="paper",
        text=f"<b>{featured_row2['passer_name']}</b>",
        showarrow=False,
        xanchor="left",
        font=dict(size=28, color="black")
    )

    fig_card.add_annotation(
        x=0.03, y=0.94,
        xref="paper", yref="paper",
        text=f"<b>{featured_row2['team_name']}</b>",
        showarrow=False,
        xanchor="left",
        font=dict(size=14, color="#71757B")
    )
    fig_card.add_annotation(
        x=0.03, y=0.915,
        xref="paper", yref="paper",
        text=f"Dominant archetype: <b>{featured_row2['dominant_pass_type_label']}</b>",
        showarrow=False,
        xanchor="left",
        font=dict(size=14, color="#71757B")
    )

    # --------------------------------------------------
    # Left / center stats text
    # --------------------------------------------------
    stats_lines = [
        f"<b>Competition sample:</b> {n_players_comp} players",
        f"<b>Passes:</b> {int(featured_row2['n_passes']):,}",
        f"<b>Mean TIV:</b> {featured_row2['mean_tiv']:.2f} (rank #{rankings['mean_tiv']})",
        f"<b>Total TIV:</b> {featured_row2['total_tiv']:.2f} (rank #{rankings['total_tiv']})",
        f"<b>Mean LBS:</b> {featured_row2['mean_lbs']:.2f} (rank #{rankings['mean_lbs']})",
        f"<b>Mean SGM:</b> {featured_row2['mean_sgm']:.2f} (rank #{rankings['mean_sgm']})",
        f"<b>Mean SDI:</b> {featured_row2['mean_sdi']:.2f} (rank #{rankings['mean_sdi']})",
        f"<b>Shot probability:</b> {featured_row2['shot_prob']:.1%}",
        f"<b>Box entry probability:</b> {featured_row2['box_entry_prob']:.1%}",
    ]

    fig_card.add_annotation(
        x=0.03, y=0.5,
        xref="paper", yref="paper",
        text="<br>".join(stats_lines),
        showarrow=False,
        xanchor="left",
        yanchor="top",
        align="left",
        font=dict(size=14, color="#111827")
    )

    # Interpretation block
    fig_card.add_annotation(
        x=0.03, y=0.2,
        xref="paper", yref="paper",
        text=(
            "<b>Profile summary</b><br>"
            f"{featured_row2['passer_name']} profiles as a "
            f"<b>{featured_row2['dominant_pass_type_label']}</b>-leaning passer, "
            "combining structural progression, space gain,<br>and defensive disruption.<br>"
            "The polar chart shows percentile strength across competition-wide passing indicators, "
            "with the dashed line<br>representingthe tournament-average baseline."
        ),
        showarrow=False,
        xanchor="left",
        yanchor="top",
        align="left",
        font=dict(size=15, color="#374151")
    )

    # Polar section label
    fig_card.add_annotation(
        x=0.77, y=0.865,
        xref="paper", yref="paper",
        text="<b>Competition percentile profile</b>",
        showarrow=False,
        font=dict(size=16, color="#111827")
    )

    logo_b64 = get_base64_image("assets/logos/1.png")
    if logo_b64:
        fig_card.add_layout_image(
            dict(
                source=f"data:image/png;base64,{logo_b64}",
                xref="paper", yref="paper",
                x=0.85, y=0.05,
                sizex=0.25, sizey=0.25,
                xanchor="center", yanchor="middle",
                layer="above",
                sizing="contain",
            )
        )
    # # Footer signature
    # fig_card.add_annotation(
    #     x=0.98, y=0.02,
    #     xref="paper", yref="paper",
    #     text="Dead Ball Analytics · Structural Passing",
    #     showarrow=False,
    #     xanchor="right",
    #     font=dict(size=11, color="#6B7280")
    # )

    # --------------------------------------------------
    # Render
    # --------------------------------------------------
    # st.plotly_chart(fig_card, use_container_width=True)
    # st.plotly_chart(fig_card, use_container_width=False, config={"displayModeBar": False})
    # --------------------------------------------------
    # Download as HTML
    # --------------------------------------------------
    # card_html = fig_card.to_html(full_html=True, include_plotlyjs="cdn")
    # st.download_button(
    #     label="Download player card (HTML)",
    #     data=card_html,
    #     file_name=f"{featured_row['passer_name'].replace(' ', '_')}_player_card.html",
    #     mime="text/html",
    # )
    from reportlab.platypus import SimpleDocTemplate, Image as RLImage
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from PIL import Image
    import io

    # Plotly image bytes
    fig_card.update_layout(
        width=CARD_W,
        height=CARD_H,
        paper_bgcolor="#F8FAFC",
        plot_bgcolor="#F8FAFC",
        margin=dict(l=20, r=20, t=20, b=20),
    )

    st.plotly_chart(
        fig_card,
        use_container_width=False,
        config={"displayModeBar": False}
    )

    pdf_bytes = fig_card.to_image(
        format="pdf",
        width=CARD_W,
        height=CARD_H,
        scale=1
    )

    # # Read image size with PIL
    # img_stream = io.BytesIO(img_bytes)
    # pil_img = Image.open(img_stream)
    # img_width, img_height = pil_img.size

    # # PDF buffer
    # buffer = io.BytesIO()
    # doc = SimpleDocTemplate(
    #     buffer,
    #     pagesize=A4,
    #     rightMargin=30,
    #     leftMargin=30,
    #     topMargin=30,
    #     bottomMargin=30,
    # )

    # # Available drawable area
    # page_width, page_height = A4
    # max_width = page_width - doc.leftMargin - doc.rightMargin
    # max_height = page_height - doc.topMargin - doc.bottomMargin

    # # Scale to fit
    # scale = min(max_width / img_width, max_height / img_height)

    # pdf_img_width = img_width * scale
    # pdf_img_height = img_height * scale

    # # Recreate stream for ReportLab
    # img_stream = io.BytesIO(img_bytes)
    # img = RLImage(img_stream, width=pdf_img_width, height=pdf_img_height)

    # doc.build([img])

    # pdf_bytes = buffer.getvalue()
    # buffer.close()

    st.download_button(
        label="Download player card (PDF)",
        data=pdf_bytes,
        file_name=f"{featured_row['passer_name'].replace(' ', '_')}_player_card.pdf",
        mime="application/pdf",
    )

render_page_footer()