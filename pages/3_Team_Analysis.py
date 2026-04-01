import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

from utils.loaders import load_team_summary, load_team_style_map
from utils.config import PASS_TYPE_COLORS, PASS_TYPE_LABELS, PASS_TYPE_ORDER
from utils.style import apply_global_style, render_page_branding, render_page_footer, apply_page_style
apply_page_style()
apply_global_style()
render_page_branding()

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def get_flag_path(team_name: str):
    slug = team_name.lower().replace(" ", "_")
    for ext in ["png", "jpg", "jpeg", "webp"]:
        path = Path(f"assets/flags/{slug}.{ext}")
        if path.exists():
            return str(path)
    return None


def pct(x, digits=1):
    return f"{100*x:.{digits}f}%"


# --------------------------------------------------
# Load data
# --------------------------------------------------
team_summary = load_team_summary().copy()
team_style = load_team_style_map().copy()

# Safety
team_summary = team_summary.sort_values("team_name").reset_index(drop=True)
team_style = team_style.sort_values("team_name").reset_index(drop=True)

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
        margin-bottom: 0.75rem;
        max-width: 950px;
    }

    .team-hero {
        background: linear-gradient(135deg, #0f172a 0%, #111827 45%, #1f2937 100%);
        border-radius: 24px;
        padding: 1.5rem 1.5rem 1.25rem 1.5rem;
        color: white;
        border: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 1rem;
    }

    .team-hero-title {
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.1;
        margin: 0 0 0.35rem 0;
        color: #FFFFFF;
    }

    .team-hero-sub {
        font-size: 0.98rem;
        line-height: 1.7;
        color: #E5E7EB;
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
    }
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="overview-hero">
    <div class="overview-title">Team Analysis</div>
    <p class="overview-subtitle">
        Explore how teams differ in structural progression, pass archetype usage, and tactical outcomes.
    </p>
</div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Team selector
# --------------------------------------------------

with st.container(border=True):
    teams = sorted(team_summary["team_name"].dropna().unique().tolist())
    st.markdown('### Select team</div>', unsafe_allow_html=True)
    selected_team = st.selectbox("Select team", options=teams,
    label_visibility="collapsed")

    team_row = team_summary.loc[team_summary["team_name"] == selected_team].iloc[0]
    style_row = team_style.loc[team_style["team_name"] == selected_team].iloc[0]
    flag_path = get_flag_path(selected_team)

    # --------------------------------------------------
    # Intro
    # --------------------------------------------------
    st.markdown("""
    <div class="section-text">
    This page shows how a team progresses the ball structurally: where it sits in the tournament-wide style space,
    which pass archetypes it relies on, and how its structural metrics and attacking outcomes compare with the rest
    of the World Cup field.
    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------------------
    # Team hero
    # --------------------------------------------------
with st.container(border=True):
    col1, col2 = st.columns([4.25, 1.5], gap="small")

    with col1:
        st.markdown(f"## {selected_team}")
        st.markdown(f"""
        A structural profile of how <b>{selected_team}</b> moves the ball, breaks lines,
                creates space, and generates attacking progression through passing.
        """, unsafe_allow_html=True)

    with col2:
        if flag_path:
            st.image(flag_path, width=190)

# --------------------------------------------------
# KPI cards
# --------------------------------------------------
with st.container(border=True):
    st.markdown('### Team profile at a glance', unsafe_allow_html=True)

    dominant_archetype = str(team_row["dominant_pass_type"]).replace("_", " ").title()

    k1, k2, k3, k4 = st.columns(4, gap="small")

    with k1:
        st.markdown(f"""
        <div class="highlight-box" style="border-color: #00E68A;">
            <div class="metric-label">Passes</div>
            <div class="metric-value">{int(team_row["n_passes"]):,}</div>
            <div class="metric-sub">Open-play passes analysed for this team.</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="highlight-box" style="border-color: #00E68A;">
            <div class="metric-label">Mean TIV</div>
            <div class="metric-value">{team_row["mean_tiv"]:.2f}</div>
            <div class="metric-sub">Average structural impact per pass.</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="highlight-box" style="border-color: #00E68A;">
            <div class="metric-label">Total TIV</div>
            <div class="metric-value">{team_row["total_tiv"]:.2f}</div>
            <div class="metric-sub">Accumulated structural contribution across all passes.</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="highlight-box" style="border-color: #00E68A;">
            <div class="metric-label">Dominant Archetype</div>
            <div class="metric-value" style="font-size:1.15rem;">{dominant_archetype}</div>
            <div class="metric-sub">Most frequent structural pass type in this team’s profile.</div>
        </div>
        """, unsafe_allow_html=True)

# --------------------------------------------------
# Style map + archetype mix
# --------------------------------------------------
color_options = {
    "Box Entry %": "box_entry_prob",
    "Shot Probability": "shot_prob",
    "Goal Probability": "goal_prob",
    "Mean TIV": "mean_tiv",
    "Total TIV": "total_tiv",
    "Pass Volume": "n_passes"
}

def normalize_size(series, min_size=3, max_size=70):
    if series.nunique() == 1:
        return pd.Series([ (min_size + max_size) / 2 ] * len(series), index=series.index)

    norm = (series - series.min()) / (series.max() - series.min())
    return min_size + norm * (max_size - min_size)

with st.container(border=True):
    st.markdown('### Structural style and pass mix</div>', unsafe_allow_html=True)

    k1, k2 = st.columns(2, gap="medium")

    with k1:
        selected_color_label = st.selectbox(
            "Color teams by",
            list(color_options.keys()),
            index=0
        )

    with k2:
        selected_size_label = st.selectbox(
            "Size teams by",
            list(color_options.keys()),
            index=0
    )

    color_col = color_options[selected_color_label]
    size_col = color_options[selected_size_label]
    team_style["size_scaled"] = normalize_size(team_style[size_col])
    custom_cols = [
        "team_name",
        "mean_tiv",
        "shot_prob",
        "goal_prob",
        "circulatory",
        "destabilising",
        "line_breaking",
        "space_expanding",
        "n_passes",
    ]
    fig_style = px.scatter(
            team_style,
            x="style_x",
            y="style_y",
            size="size_scaled",
            color=color_col,
            # hover_name="team_name",
            custom_data=custom_cols,
            # hover_data={
            #     "mean_tiv": ":.2f",
            #     "shot_prob": ":.1%",
            #     "goal_prob": ":.1%",
            #     "circulatory": ":.1%",
            #     "destabilising": ":.1%",
            #     "line_breaking": ":.1%",
            #     "space_expanding": ":.1%",
            #     "style_x": False,
            #     "style_y": False,
            #     "size_scaled": False,
            #     "n_passes": ":,.0f",
            # },
            labels={
                "style_x": "Line-breaking ↔ Circulatory",
                "style_y": "Space-expanding ↔ Destabilising",
                "box_entry_prob": "Box Entry %",
            },
            color_continuous_scale="Viridis",
            title="Tournament structural style map",
    )

    fig_style.update_traces(
            marker=dict(line=dict(width=1, color="white")),
            opacity=0.85,
    )

    fig_style.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "TIV (avg): %{customdata[1]:.2f}<br>"
            "Shot Probability: %{customdata[2]:.1%}<br>"
            "Goal Probability: %{customdata[3]:.1%}<br>"
            "Circulatory: %{customdata[4]:.1%}<br>"
            "Destabilising: %{customdata[5]:.1%}<br>"
            "Line Breaking: %{customdata[6]:.1%}<br>"
            "Space Expanding: %{customdata[7]:.1%}<br>"
            "# Passes: %{customdata[8]:.0f}"
            "<extra></extra>"
        )
    )

    fig_style.add_trace(
            go.Scatter(
                x=[style_row["style_x"]],
                y=[style_row["style_y"]],
                mode="markers+text",
                text=[selected_team],
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

    fig_style.update_layout(
            template="plotly_white",
            title_x=0.0,
            height=520,
            margin=dict(t=60, l=20, r=20, b=20),
            font=dict(size=12),
    )
    fig_style.update_xaxes(showgrid=True, gridcolor="#E5E7EB", zeroline=False)
    fig_style.update_yaxes(showgrid=True, gridcolor="#E5E7EB", zeroline=False)

    st.plotly_chart(fig_style, use_container_width=True)

    st.markdown("""
    <div class="highlight-box">
    <b>How to read this figure:</b><br>
    Each point represents a team positioned according to its structural passing tendencies.

    - Teams on the <b>left</b> rely more on <b>line-breaking</b> passing, while teams on the <b>right</b> are more <b>circulatory</b>
    - Teams toward the <b>top</b> are more <b>destabilising</b>, while those toward the <b>bottom</b> are more <b>space-expanding</b>
    - <b>Bubble size</b> and <b>Colour</b> encode the selected performance variable (e.g., box entries or shot probability)


    This means the <b>top-left</b> region reflects teams that are both line-breaking and destabilising, while the <b>bottom-right</b> region reflects teams that are more circulatory and space-expanding.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""<br>""", unsafe_allow_html=True)
with st.container(border=True):
    mix_df = pd.DataFrame({
        "pass_type": PASS_TYPE_ORDER,
        "proportion": [
            team_row.get("circulatory", 0.0),
            team_row.get("destabilising", 0.0),
            team_row.get("line_breaking", 0.0),
            team_row.get("space_expanding", 0.0),
        ]
    })
    mix_df["pass_type_label"] = mix_df["pass_type"].map(PASS_TYPE_LABELS)

    fig_mix = px.pie(
        mix_df,
        names="pass_type_label",
        values="proportion",
        color="pass_type",
        color_discrete_map=PASS_TYPE_COLORS,
        hole=0.28,
    )

    fig_mix.update_traces(
        textinfo="percent",
        textfont=dict(size=13, color="white"),
        marker=dict(line=dict(color="white", width=2)),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Share of passes: %{percent}<br>"
            "<extra></extra>"
        ),
        sort=False
    )

    fig_mix.update_layout(
        template="plotly_white",
        title=dict(
            text=f"{selected_team} archetype composition",
            x=0.0,
            xanchor="left",
            font=dict(size=18, color="#111827"),
        ),
        height=520,
        margin=dict(t=60, l=20, r=20, b=20),
        font=dict(size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.12,
            xanchor="center",
            x=0.5,
            title="",
            font=dict(size=12),
        ),
        annotations=[
            dict(
                text="Pass<br>mix",
                x=0.5,
                y=0.5,
                font=dict(size=16, color="#374151"),
                showarrow=False
            )
        ]
    )
    dominant_idx = mix_df["proportion"].idxmax()
    pull_values = [0.0] * len(mix_df)
    pull_values[dominant_idx] = 0.06

    fig_mix.update_traces(pull=pull_values)
    st.plotly_chart(fig_mix, use_container_width=True)

    st.markdown("""
    <div class="highlight-box">
    <b>How to read these visuals:</b> The archetype chart shows the internal passing mechanisms that shape its profile.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""<br>""", unsafe_allow_html=True)
# --------------------------------------------------
# Tournament comparison
# --------------------------------------------------
with st.container(border=True):
    st.markdown('### Comparison against tournament averages</div>', unsafe_allow_html=True)

    tournament_means = team_summary[[
        "mean_lbs", "mean_sgm", "mean_sdi",
        "final_third_prob", "box_entry_prob", "shot_prob", "goal_prob"
    ]].mean()

    c_left, c_right = st.columns([1, 1], gap="large")
    with c_left:
        metrics_df = pd.DataFrame({
            "metric": ["Mean LBS", "Mean SGM", "Mean SDI"],
            "selected_team": [
                team_row["mean_lbs"],
                team_row["mean_sgm"],
                team_row["mean_sdi"],
            ],
            "tournament_avg": [
                tournament_means["mean_lbs"],
                tournament_means["mean_sgm"],
                tournament_means["mean_sdi"],
            ]
        })

        metrics_df["selected_norm"] = metrics_df["selected_team"] / metrics_df["tournament_avg"]
        metrics_df["avg_norm"] = 1.0

        fig_metrics = go.Figure()

        fig_metrics.add_trace(go.Bar(
            x=metrics_df["metric"],
            y=metrics_df["selected_norm"],
            name=selected_team,
            marker_color="#00E68A",
            text=metrics_df["selected_norm"].map(lambda x: f"{x:.2f}x"),
            textposition="outside",
            customdata=metrics_df[["selected_team", "tournament_avg"]],
            hovertemplate=(
                "<b>%{x}</b><br>"
                + f"{selected_team}: %{{customdata[0]:.3f}}<br>"
                + "Tournament avg: %{customdata[1]:.3f}<br>"
                + "Relative: %{y:.2f}x"
                + "<extra></extra>"
            )
        ))

        fig_metrics.add_trace(go.Bar(
            x=metrics_df["metric"],
            y=metrics_df["avg_norm"],
            name="Tournament average",
            marker_color="#9CA3AF",
            customdata=metrics_df[["selected_team", "tournament_avg"]],
            hovertemplate=(
                "<b>%{x}</b><br>"
                + "Tournament avg: %{customdata[1]:.3f}<br>"
                + "Baseline: 1.00x"
                + "<extra></extra>"
            )
        ))

        fig_metrics.update_layout(
            barmode="group",
            template="plotly_white",
            title="Structural metrics vs tournament average (relative)",
            title_x=0.0,
            height=430,
            margin=dict(t=90, l=20, r=20, b=20),
            legend=dict(
                orientation="h",
                y=1.05,
                x=0
            ),
        )

        fig_metrics.update_yaxes(
            title="Relative to average (1.0 = baseline)",
            showgrid=True,
            gridcolor="#E5E7EB"
        )
        st.plotly_chart(fig_metrics, use_container_width=True)
        st.markdown("""
        <div class="section-text">
        Values are shown relative to the tournament average (1.0). Values above 1 indicate above-average structural impact.
        </div>
        """, unsafe_allow_html=True)
    with c_right:
        outcome_df = pd.DataFrame({
            "metric": ["Final 3rd", "Box<br>Entry", "Shot", "Goal"],
            "selected_team": [
                team_row["final_third_prob"],
                team_row["box_entry_prob"],
                team_row["shot_prob"],
                team_row["goal_prob"],
            ],
            "tournament_avg": [
                tournament_means["final_third_prob"],
                tournament_means["box_entry_prob"],
                tournament_means["shot_prob"],
                tournament_means["goal_prob"],
            ]
        })

        # Close the loop explicitly for a cleaner radar
        theta_vals = outcome_df["metric"].tolist() + [outcome_df["metric"].tolist()[0]]
        selected_vals = outcome_df["selected_team"].tolist() + [outcome_df["selected_team"].tolist()[0]]
        avg_vals = outcome_df["tournament_avg"].tolist() + [outcome_df["tournament_avg"].tolist()[0]]

        # Dynamic radial max with a bit of headroom
        radial_max = max(max(selected_vals), max(avg_vals)) * 1.18

        fig_outcomes = go.Figure()

        fig_outcomes.add_trace(go.Scatterpolar(
            r=selected_vals,
            theta=theta_vals,
            fill="toself",
            name=selected_team,
            line=dict(color="#00E68A", width=3),
            fillcolor="rgba(0, 230, 138, 0.22)",
            hovertemplate=(
                "<b>%{theta}</b><br>"
                f"{selected_team}: %{{r:.1%}}"
                "<extra></extra>"
            )
        ))

        fig_outcomes.add_trace(go.Scatterpolar(
            r=avg_vals,
            theta=theta_vals,
            fill="toself",
            name="Tournament average",
            line=dict(color="#9CA3AF", width=2),
            fillcolor="rgba(156, 163, 175, 0.18)",
            hovertemplate=(
                "<b>%{theta}</b><br>"
                "Tournament average: %{r:.1%}"
                "<extra></extra>"
            )
        ))

        fig_outcomes.update_layout(
            template="plotly_white",
            title=dict(
                text="Outcome Profile vs Tournament Average",
                x=0.0,
                xanchor="left"
            ),
            height=520,
            margin=dict(t=95, l=40, r=40, b=40),
            font=dict(size=13, color="#111827"),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.01,
                xanchor="left",
                x=0.0,
                title="",
                font=dict(size=12),
                bgcolor="rgba(0,0,0,0)"
            ),
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    visible=True,
                    range=[0, radial_max],
                    tickformat=".0%",
                    tickfont=dict(size=11, color="#6B7280"),
                    gridcolor="#E5E7EB",
                    gridwidth=1,
                    linecolor="#D1D5DB",
                    linewidth=1,
                    angle=90,
                    showline=False
                ),
                angularaxis=dict(
                    tickfont=dict(size=13, color="#111827"),
                    gridcolor="#F3F4F6",
                    linecolor="#D1D5DB",
                    linewidth=1,
                    rotation=90,
                    direction="clockwise"
                )
            )
        )

        st.plotly_chart(fig_outcomes, use_container_width=True)
# --------------------------------------------------
# Tactical reading
# --------------------------------------------------


with st.container(border=True):
    st.markdown('### Tactical reading</div>', unsafe_allow_html=True)
    selected_team2 = st.selectbox("Select team2", options=teams,
    label_visibility="collapsed")
    team_row2 = team_summary.loc[team_summary["team_name"] == selected_team2].iloc[0]
    style_row2 = team_style.loc[team_style["team_name"] == selected_team2].iloc[0]
    flag_path2 = get_flag_path(selected_team2)
    mix_df2 = pd.DataFrame({
        "pass_type": PASS_TYPE_ORDER,
        "proportion": [
            team_row2.get("circulatory", 0.0),
            team_row2.get("destabilising", 0.0),
            team_row2.get("line_breaking", 0.0),
            team_row2.get("space_expanding", 0.0),
        ]
    })
    mix_df2["pass_type_label"] = mix_df2["pass_type"].map(PASS_TYPE_LABELS)

    archetype_max2 = mix_df2.sort_values("proportion", ascending=False).iloc[0]["pass_type_label"]
    box_prob2 = pct(team_row2["box_entry_prob"])
    shot_prob2 = pct(team_row2["shot_prob"])

    t_left, t_right = st.columns([4.25, 1.5], gap="large")
    with t_left:
        st.markdown(f"""<b>What stands out about {selected_team2}?</b>""", unsafe_allow_html=True)
        st.markdown(f"""
                The structural profile of <b>{selected_team2}</b> is led by <b>{archetype_max2}</b> passing.
                
                Across the analysed sample, the team records a mean Tactical Impact Value of <b>{team_row2["mean_tiv"]:.2f}</b>, alongside downstream probabilities of <b>{box_prob2}</b> for box entries and <b>{shot_prob2}</b> for shots.
                
                The visualisations above help show whether those outputs are driven more by circulation, destabilisation, line-breaking progression, or space-expanding passing.
        """, unsafe_allow_html=True)

    with t_right:
        if flag_path2:
            st.image(flag_path2, width=250)

render_page_footer()