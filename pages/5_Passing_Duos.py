import re
import base64
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.loaders import load_duo_summary
from utils.style import apply_global_style, render_page_branding, render_page_footer, apply_page_style
apply_page_style()
apply_global_style()
render_page_branding()


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def slugify(text: str) -> str:
    text = str(text).strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
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
    slug = slugify(team_name)
    for ext in ["png", "jpg", "jpeg", "webp"]:
        candidate = Path("assets/flags") / f"{slug}.{ext}"
        if candidate.exists():
            return str(candidate)
    return None

def get_base64_image(image_path):
    if image_path is None:
        return None
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def normalize_size(series, min_size=14, max_size=42):
    s = pd.Series(series).astype(float)
    if s.nunique() <= 1:
        return pd.Series([(min_size + max_size) / 2] * len(s), index=s.index)
    s = (s - s.min()) / (s.max() - s.min())
    return min_size + s * (max_size - min_size)


def percentile_rank(series, value):
    s = pd.Series(series).dropna().astype(float)
    if len(s) == 0:
        return np.nan
    return 100.0 * (s <= float(value)).mean()


# --------------------------------------------------
# Load data
# --------------------------------------------------
duos = load_duo_summary().copy()

if "duo_label" not in duos.columns:
    duos["duo_label"] = duos["passer_name"] + " → " + duos["receiver_name"]

# --------------------------------------------------
# Page intro
# --------------------------------------------------
st.markdown("""
<div class="overview-hero">
    <div class="overview-title">Passing Duos</div>
    <p class="overview-subtitle">
Explore passer-receiver partnerships that amplify structural value and tactical progression.
                </p>
            <div class="overview-subtitle">
This page focuses on passing relationships rather than isolated players. It highlights which
partnerships increase structural impact, produce more dangerous downstream outcomes, and outperform
a passer's typical baseline behaviour.
</div>
</div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# CSS
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

    .duo-hero {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 45%, #E5E7EB 100%);
        border-radius: 24px;
        padding: 1.4rem 1.4rem 1.2rem 1.4rem;
        color: #111827;
        border: 1px solid #E5E7EB;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }

    .duo-hero-title {
        font-size: 1.9rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 0.3rem;
        color: #111827;
    }

    .duo-hero-sub {
        font-size: 0.96rem;
        line-height: 1.7;
        color: #4B5563;
        margin: 0;
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

# --------------------------------------------------
# Filters
# --------------------------------------------------
with st.container(border=True):

    st.markdown('### Filters', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4, gap="small")

    teams = ["All"] + sorted(duos["team_name"].dropna().unique().tolist())
    selected_team = c1.selectbox("Team", teams)

    if selected_team == "All":
        available_passers = ["All"] + sorted(duos["passer_name"].dropna().unique().tolist())
    else:
        available_passers = ["All"] + sorted(
            duos.loc[duos["team_name"] == selected_team, "passer_name"].dropna().unique().tolist()
        )

    selected_passer = c2.selectbox("Passer", available_passers)
    min_duo_passes = c3.slider("Minimum duo passes", 1, 75, 10)
    
    sort_label = c4.selectbox(
        "Sort ranking board by",
        ["ΔTIV", "Duo Mean TIV", "Duo Passes", "Box Entry Probability", "Shot Probability"],
        index=0
    )

    # --------------------------------------------------
    # Filter data
    # --------------------------------------------------
    filtered = duos.copy()

    if selected_team != "All":
        filtered = filtered[filtered["team_name"] == selected_team]

    if selected_passer != "All":
        filtered = filtered[filtered["passer_name"] == selected_passer]

    filtered = filtered[filtered["duo_passes"] >= min_duo_passes].copy()

    if filtered.empty:
        st.warning("No passing duos match the current filter combination.")
        st.stop()

    # --------------------------------------------------
    # Featured duo
    # --------------------------------------------------
    sort_map = {
        "ΔTIV": "delta_tiv",
        "Duo Mean TIV": "duo_mean_tiv",
        "Duo Passes": "duo_passes",
        "Box Entry Probability": "box_entry_prob",
        "Shot Probability": "shot_prob",
    }

    featured_row = filtered.sort_values(sort_map[sort_label], ascending=False).iloc[0]

    passer_photo = get_player_photo_path(featured_row["passer_name"], featured_row["team_name"])
    receiver_photo = get_player_photo_path(featured_row["receiver_name"], featured_row["team_name"])
    flag_path = get_team_flag_path(featured_row["team_name"])
    flag_b64 = get_base64_image(flag_path)
    # --------------------------------------------------
    # Duo hero
    # --------------------------------------------------
    hero_left, hero_right = st.columns([1.8, 5], gap="medium")
    delta = featured_row["delta_tiv"]

    if delta > 0.02:
        tiv_text = f"increases structural value by <b>{delta:.2f}</b> TIV per pass relative to the passer’s baseline"
    elif delta < -0.02:
        tiv_text = f"reduces structural value by <b>{abs(delta):.2f}</b> TIV per pass relative to the passer’s baseline"
    else:
        tiv_text = f"operates close to the passer’s baseline structural impact (<b>{delta:.2f}</b> ΔTIV)"

    duo_passes = int(featured_row["duo_passes"])

    volume_note = ""
    if duo_passes < 20:
        volume_note = " Results should be interpreted cautiously due to limited sample size."
    elif duo_passes > 60:
        volume_note = " High-volume relationship, offering a stable view of the partnership."

    sentence = f"""
    This partnership {tiv_text}, across <b>{duo_passes}</b> completed passes. 
    It leads to <b>{featured_row['box_entry_prob']:.1%}</b> box entries and 
    <b>{featured_row['shot_prob']:.1%}</b> shots per pass, reflecting its downstream attacking impact.{volume_note}
    """
    with hero_left:
        if passer_photo:
            st.image(passer_photo, width=200)
        if receiver_photo:
            st.image(receiver_photo, width=200)

    with hero_right:
        st.markdown(f"""
        <div class="duo-hero">
            <div class="duo-hero-title">{featured_row['passer_name']} → {featured_row['receiver_name']}</div>
            <p class="duo-hero-sub">
            <img class="hero-logo" src="data:image/png;base64,{flag_b64}" width=100 /><br><br>
                <b>{featured_row['team_name']}</b> &middot; Duo passes: <b>{int(featured_row['duo_passes'])}</b><br><br>
                {sentence}
        """, unsafe_allow_html=True)

    # --------------------------------------------------
    # KPI cards
    # --------------------------------------------------
    st.markdown('<div class="section-title">Duo profile at a glance</div>', unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5, gap="small")

    with k1:
        st.markdown(f"""
        <div class="highlight-box">
            <div class="metric-label">Duo Passes</div>
            <div class="metric-value">{int(featured_row['duo_passes'])}</div>
            <div class="metric-sub">Completed passes between the pair.</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="highlight-box">
            <div class="metric-label">ΔTIV</div>
            <div class="metric-value">{featured_row['delta_tiv']:.2f}</div>
            <div class="metric-sub">Structural lift over the passer baseline.</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="highlight-box">
            <div class="metric-label">Duo Mean TIV</div>
            <div class="metric-value">{featured_row['duo_mean_tiv']:.2f}</div>
            <div class="metric-sub">Average structural value per duo pass.</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="highlight-box">
            <div class="metric-label">Box Entry %</div>
            <div class="metric-value">{featured_row['box_entry_prob']:.1%}</div>
            <div class="metric-sub">Probability of entering the box after the pass.</div>
        </div>
        """, unsafe_allow_html=True)

    with k5:
        st.markdown(f"""
        <div class="highlight-box">
            <div class="metric-label">Shot %</div>
            <div class="metric-value">{featured_row['shot_prob']:.1%}</div>
            <div class="metric-sub">Probability of taking a shot after the pass.</div>
        </div>
        """, unsafe_allow_html=True)

# --------------------------------------------------
# Main duo explorer
# --------------------------------------------------

# --------------------------------------------------
# Filters
# --------------------------------------------------
with st.container(border=True):
    st.markdown('### Duo relationship explorer', unsafe_allow_html=True)

    # st.markdown('#### Filters', unsafe_allow_html=True)

    c5, c6, c7, c8 = st.columns(4)

    color_options = {
        "Box Entry Probability": "box_entry_prob",
        "Shot Probability": "shot_prob",
        "Goal Probability": "goal_prob",
        "ΔTIV": "delta_tiv",
        "Duo Mean TIV": "duo_mean_tiv",
    }
    selected_color_label = c5.selectbox("Color by", list(color_options.keys()), index=0)

    size_options = {
        "Duo Passes": "duo_passes",
        "ΔTIV": "delta_tiv",
        "Duo Mean TIV": "duo_mean_tiv",
    }
    selected_size_label = c6.selectbox("Bubble size", list(size_options.keys()), index=0)

    x_options = {
        "ΔTIV": "delta_tiv",
        "Duo Mean TIV": "duo_mean_tiv",
        "Passer Mean TIV": "passer_mean_tiv",
        "Box Entry Probability": "box_entry_prob",
        "Shot Probability": "shot_prob",
    }
    y_options = {
        "Duo Mean TIV": "duo_mean_tiv",
        "ΔTIV": "delta_tiv",
        "Box Entry Probability": "box_entry_prob",
        "Shot Probability": "shot_prob",
        "Goal Probability": "goal_prob",
    }

    selected_x_label = c7.selectbox("X-axis", list(x_options.keys()), index=0)
    selected_y_label = c8.selectbox("Y-axis", list(y_options.keys()), index=0)

    x_col = x_options[selected_x_label]
    y_col = y_options[selected_y_label]
    color_col = color_options[selected_color_label]
    size_col = size_options[selected_size_label]

    filtered["size_scaled"] = normalize_size(filtered[size_col])

    fig = px.scatter(
        filtered,
        x=x_col,
        y=y_col,
        size="size_scaled",
        color=color_col,
        color_continuous_scale="YlOrRd",
        hover_name="duo_label",
        hover_data={
            "team_name": True,
            "duo_passes": ":,.0f",
            "delta_tiv": ":.2f",
            "duo_mean_tiv": ":.2f",
            "passer_mean_tiv": ":.2f",
            "box_entry_prob": ":.1%",
            "shot_prob": ":.1%",
            "goal_prob": ":.1%",
            "size_scaled": False,
        },
        labels={
            x_col: selected_x_label,
            y_col: selected_y_label,
            color_col: selected_color_label,
        },
        title=f"{selected_x_label} vs {selected_y_label}",
        opacity=0.82,
    )

    fig.update_traces(
        marker=dict(line=dict(width=0.8, color="white")),
    )

    fig.add_trace(
        go.Scatter(
            x=[featured_row[x_col]],
            y=[featured_row[y_col]],
            mode="markers+text",
            text=[featured_row["duo_label"]],
            textposition="top center",
            marker=dict(
                size=26,
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
<b>How to read this figure:</b> each point is a passer-receiver duo. Use the axis, color, and bubble-size
controls to explore how structural value, downstream progression, and passing volume vary across partnerships.
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Secondary visuals
# --------------------------------------------------
with st.container(border=True):
    st.markdown('### Distribution and composition', unsafe_allow_html=True)

    left, right = st.columns([1.15, 1], gap="large")

    with left:
        if selected_team == "All":
            # Top 10 teams by total duo volume
            top_teams = (
                filtered.groupby("team_name")["duo_passes"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .index
            )

            plot_df = filtered[filtered["team_name"].isin(top_teams)].copy()

            # Order teams by median ΔTIV for cleaner reading
            team_order = (
                plot_df.groupby("team_name")["delta_tiv"]
                .median()
                .sort_values(ascending=False)
                .index.tolist()
            )

            fig_box = px.box(
                plot_df,
                y="delta_tiv",
                x="team_name",
                color="team_name",
                category_orders={"team_name": team_order},
                labels={"delta_tiv": "ΔTIV", "team_name": ""},
                title="ΔTIV distribution (Top 10 teams by duo volume)",
                points="outliers",
            )

            fig_box.update_layout(showlegend=False)

        else:
            # If a team is selected, show passer-level distribution within that team
            # If a passer is also selected, this still works and shows only that passer's duos
            passer_order = (
                filtered.groupby("passer_name")["delta_tiv"]
                .median()
                .sort_values(ascending=False)
                .index.tolist()
            )

            fig_box = px.box(
                filtered,
                y="delta_tiv",
                x="passer_name",
                color="passer_name" if selected_passer == "All" else None,
                category_orders={"passer_name": passer_order},
                labels={"delta_tiv": "ΔTIV", "passer_name": ""},
                title="ΔTIV distribution by passer",
                points="outliers",
            )

            fig_box.update_layout(showlegend=False)

        fig_box.update_traces(
            marker=dict(size=3, opacity=0.5)
        )

        fig_box.update_layout(
            template="plotly_white",
            title_x=0.0,
            height=430,
            margin=dict(t=60, l=20, r=20, b=20),
            font=dict(size=12),
        )
        fig_box.update_xaxes(showgrid=False, title_text="")
        fig_box.update_yaxes(showgrid=True, gridcolor="#E5E7EB", zeroline=False)

        st.plotly_chart(fig_box, use_container_width=True)

    with right:
        if selected_passer == "All":
            # No passer selected -> show passer share
            comp_df = (
                filtered.groupby("passer_name", as_index=False)["duo_passes"]
                .sum()
                .sort_values("duo_passes", ascending=False)
                .head(8)
            )

            pie_names = "passer_name"
            pie_title = "Passer share of filtered duo volume"
            center_text = "Passer<br>volume"
            hover_label = "Share of duo passes"

        else:
            # Passer selected -> show receiver distribution
            comp_df = (
                filtered.groupby("receiver_name", as_index=False)["duo_passes"]
                .sum()
                .sort_values("duo_passes", ascending=False)
                .head(8)
            )

            pie_names = "receiver_name"
            pie_title = f"Receiver distribution for {selected_passer}"
            center_text = "Receiver<br>share"
            hover_label = "Share of passes to receiver"

        fig_comp = px.pie(
            comp_df,
            names=pie_names,
            values="duo_passes",
            hole=0.38,
        )

        fig_comp.update_traces(
            textinfo="percent",
            marker=dict(line=dict(color="white", width=2)),
            hovertemplate=f"<b>%{{label}}</b><br>{hover_label}: %{{percent}}<extra></extra>"
        )

        fig_comp.update_layout(
            template="plotly_white",
            title=dict(
                text=pie_title,
                x=0.0,
                xanchor="left",
                font=dict(size=18, color="#111827"),
            ),
            height=450,
            margin=dict(t=60, l=20, r=20, b=80),
            font=dict(size=12),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.42,
                xanchor="center",
                x=0.5,
                title="",
            ),
            annotations=[
                dict(
                    text=center_text,
                    x=0.5,
                    y=0.5,
                    font=dict(size=16, color="#374151"),
                    showarrow=False
                )
            ]
        )

        st.plotly_chart(fig_comp, use_container_width=True)

# --------------------------------------------------
# Ranking board
# --------------------------------------------------
with st.container(border=True):

    st.markdown('### Duo ranking board', unsafe_allow_html=True)
    c9, c10 = st.columns([1.5, 1], gap="small")
    top_n = c9.slider("Top N duos", 5, 40, 15)
    sort_label2 = c10.selectbox(
        "Sort Table by",
        ["ΔTIV", "Duo Mean TIV", "Duo Passes", "Box Entry Probability", "Shot Probability"],
        index=0
    )
    table = (
        filtered.sort_values(sort_map[sort_label2], ascending=False)
        .head(top_n)
        .copy()
    )

    table = table[[
        "duo_label",
        "team_name",
        "duo_passes",
        "delta_tiv",
        "duo_mean_tiv",
        "passer_mean_tiv",
        "box_entry_prob",
        "shot_prob",
        "goal_prob",
    ]].rename(columns={
        "duo_label": "Duo",
        "team_name": "Team",
        "duo_passes": "Duo Passes",
        "delta_tiv": "ΔTIV",
        "duo_mean_tiv": "Duo Mean TIV",
        "passer_mean_tiv": "Passer Mean TIV",
        "box_entry_prob": "Box Entry %",
        "shot_prob": "Shot %",
        "goal_prob": "Goal %",
    })

    st.dataframe(
        table.style.format({
            "Duo Passes": "{:,.0f}",
            "ΔTIV": "{:.2f}",
            "Duo Mean TIV": "{:.2f}",
            "Passer Mean TIV": "{:.2f}",
            "Box Entry %": "{:.1%}",
            "Shot %": "{:.1%}",
            "Goal %": "{:.1%}",
        }),
        use_container_width=True,
        height=520,
    )

# --------------------------------------------------
# Downloadable duo card
# --------------------------------------------------
with st.container(border=True):
    st.markdown('### Featured duo card', unsafe_allow_html=True)

    competition_pool = duos[duos["duo_passes"] >= min_duo_passes].copy()

    percentile_metrics = {
        "Duo Passes": "duo_passes",
        "ΔTIV": "delta_tiv",
        "Duo Mean TIV": "duo_mean_tiv",
        "Box Entry %": "box_entry_prob",
        "Shot %": "shot_prob",
        "Goal %": "goal_prob",
    }

    duo_percentiles = {}
    avg_percentiles = {}

    for label, col in percentile_metrics.items():
        duo_percentiles[label] = percentile_rank(competition_pool[col], featured_row[col])
        avg_percentiles[label] = percentile_rank(competition_pool[col], competition_pool[col].mean())

    card_df = pd.DataFrame({
        "metric": list(percentile_metrics.keys()),
        "duo_pct": list(duo_percentiles.values()),
        "avg_pct": list(avg_percentiles.values()),
    })

    theta_closed = card_df["metric"].tolist() + [card_df["metric"].tolist()[0]]
    avg_closed = card_df["avg_pct"].tolist() + [card_df["avg_pct"].tolist()[0]]

    passer_b64 = get_base64_image(passer_photo)
    receiver_b64 = get_base64_image(receiver_photo)
    flag_b64 = get_base64_image(flag_path)

    CARD_W = 1000
    CARD_H = 920
    from plotly.subplots import make_subplots
    fig_card = make_subplots(
        rows=1,
        cols=1,
        specs=[[{"type": "polar"}]],
    )

    fig_card.add_trace(
        go.Barpolar(
            r=card_df["duo_pct"],
            theta=card_df["metric"],
            marker=dict(
                color=card_df["duo_pct"],
                colorscale=[
                    [0.00, "#FDE68A"],
                    [0.35, "#F59E0B"],
                    [0.70, "#EA580C"],
                    [1.00, "#991B1B"],
                ],
                line=dict(color="white", width=1.5),
                cmin=0,
                cmax=100,
            ),
            opacity=0.62,
            name="Duo percentile",
            hovertemplate="<b>%{theta}</b><br>Duo percentile: %{r:.0f}<extra></extra>",
            subplot="polar",
        )
    )

    fig_card.add_trace(
        go.Scatterpolar(
            r=avg_closed,
            theta=theta_closed,
            mode="lines+markers",
            line=dict(color="#111827", width=2.5, dash="dash"),
            marker=dict(size=6, color="#111827"), fill="toself", fillcolor="rgba(17,24,39,0.45)",
            name="Tournament average percentile",
            hovertemplate="<b>%{theta}</b><br>Average percentile baseline: %{r:.0f}<extra></extra>",
            subplot="polar",
        )
    )

    fig_card.update_layout(
        width=CARD_W,
        height=CARD_H,
        paper_bgcolor="#F8FAFC",
        plot_bgcolor="#F8FAFC",
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.8,
            xanchor="right",
            x=0.98,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12, color="#111827"),
            title=""
        ),
        polar=dict(
            domain=dict(x=[0.4, 0.9], y=[0.22, 0.8]),
            bgcolor="#FFFFFF",
            radialaxis=dict(
                range=[0, 100],
                tickvals=[20, 40, 60, 80, 100],
                ticktext=["20", "40", "60", "80", "100"],
                angle=0,
                gridcolor="#E5E7EB",
                tickfont=dict(size=10, color="#6B7280"),
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

    fig_card.add_shape(type="rect", xref="paper", yref="paper", x0=0, x1=1, y0=0, y1=1,
                    line=dict(color="#E5E7EB", width=1), fillcolor="#F8FAFC", layer="below")
    fig_card.add_shape(type="rect", xref="paper", yref="paper", x0=0, x1=1, y0=0.88, y1=1.00,
                    line=dict(color="#111827", width=0), fillcolor="#111827", layer="below")

    if passer_b64:
        fig_card.add_layout_image(dict(
            source=f"data:image/png;base64,{passer_b64}",
            xref="paper", yref="paper",
            x=0.13, y=0.89,
            sizex=0.25, sizey=0.385,
            xanchor="center", yanchor="top",
            layer="above", sizing="contain"
        ))
    if receiver_b64:
        fig_card.add_layout_image(dict(
            source=f"data:image/png;base64,{receiver_b64}",
            xref="paper", yref="paper",
            x=0.13, y=0.6,
            sizex=0.225, sizey=0.385,
            xanchor="center", yanchor="top",
            layer="above", sizing="contain"
        ))
    if flag_b64:
        fig_card.add_layout_image(dict(
            source=f"data:image/png;base64,{flag_b64}",
            xref="paper", yref="paper",
            x=0.91, y=0.94,
            sizex=0.13, sizey=0.13,
            xanchor="center", yanchor="middle",
            layer="above", sizing="contain"
        ))

    fig_card.add_annotation(
        x=0.03, y=0.985, xref="paper", yref="paper",
        text=f"<b>{featured_row['passer_name']} --> {featured_row['receiver_name']}</b>",
        showarrow=False, xanchor="left",
        font=dict(size=28, color="white")
    )

    fig_card.add_annotation(
        x=0.03, y=0.94, xref="paper", yref="paper",
        text=f"{featured_row['team_name']} - Duo passes: <b>{int(featured_row['duo_passes'])}</b>",
        showarrow=False, xanchor="left",
        font=dict(size=14, color="#D1D5DB")
    )

    stats_lines = [
        f"<b>ΔTIV:</b> {featured_row['delta_tiv']:.2f}",
        f"<b>Duo Mean TIV:</b> {featured_row['duo_mean_tiv']:.2f}",
        f"<b>Passer Mean TIV:</b> {featured_row['passer_mean_tiv']:.2f}",
        f"<b>Box Entry %:</b> {featured_row['box_entry_prob']:.1%}",
        f"<b>Shot %:</b> {featured_row['shot_prob']:.1%}",
        f"<b>Goal %:</b> {featured_row['goal_prob']:.1%}",
    ]

    fig_card.add_annotation(
        x=0.05, y=0.315, xref="paper", yref="paper",
        text="<br>".join(stats_lines),
        showarrow=False, xanchor="left", yanchor="top", align="left",
        font=dict(size=14, color="#111827")
    )

    fig_card.add_annotation(
        x=0.03, y=0.155, xref="paper", yref="paper",
        text=(
            "<b>Partnership summary</b><br>"
            "This card positions the passer-receiver relationship within the competition landscape, "
            "highlighting how the duo performs<br>in terms of structural impact (ΔTIV), passing volume, "
            "and downstream attacking outcomes.<br>The polar bars show percentile rankings across key metrics, "
            "while the dashed profile represents the tournament-average<br>benchmark."
        ),
        showarrow=False, xanchor="left", yanchor="top", align="left",
        font=dict(size=13, color="#374151")
    )

    fig_card.add_annotation(
        x=0.77, y=0.865, xref="paper", yref="paper",
        text="<b>Competition percentile profile</b>",
        showarrow=False, font=dict(size=16, color="#111827")
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
    st.download_button(
        label="Download duo card as PDF",
        data=pdf_bytes,
        file_name=f"{featured_row['duo_label']}_duo_card.pdf",
        mime="application/pdf",
    )

render_page_footer()