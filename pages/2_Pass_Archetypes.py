import streamlit as st
import pandas as pd
import plotly.express as px

from utils.loaders import load_passes
from utils.config import PASS_TYPE_COLORS, PASS_TYPE_LABELS, PASS_TYPE_ORDER
from utils.style import apply_global_style, render_page_branding, render_page_footer, apply_page_style
apply_page_style()
apply_global_style()
render_page_branding()
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
        margin-bottom: 0.7rem;
    }

    .section-text {
        font-size: 0.98rem;
        line-height: 1.7;
        color: #4B5563;
        margin-bottom: 0.7rem;
        max-width: 950px;
    }

    .filter-card {
        background: #F8FAFC;
        border: 1px solid #E5E7EB;
        border-radius: 18px;
        padding: 1rem 1rem 0.8rem 1rem;
        box-shadow: 0 1px 6px rgba(0,0,0,0.03);
        margin-bottom: 1rem;
    }

    .metric-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 18px;
        padding: 1rem 1rem 0.85rem 1rem;
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
        font-size: 1.55rem;
        font-weight: 800;
        color: #111827;
        margin-bottom: 0.15rem;
        line-height: 1.1;
    }

    .metric-sub {
        font-size: 0.88rem;
        color: #4B5563;
        line-height: 1.5;
    }

    .info-box {
        background: #ECFDF5;
        border-left: 6px solid #00E68A;
        border-radius: 14px;
        padding: 1rem 1rem;
        color: #14532D;
        font-size: 0.95rem;
        line-height: 1.7;
        margin-bottom: 0.8rem;
    }

    .subtle-divider {
        height: 1px;
        background: linear-gradient(to right, transparent, #D1D5DB, transparent);
        margin-top: 1.2rem;
        margin-bottom: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Load data
# --------------------------------------------------
passes = load_passes().copy()

# Pretty labels
passes["pass_type_label"] = passes["pass_type"].map(PASS_TYPE_LABELS).fillna(passes["pass_type"])

# --------------------------------------------------
# Friendly metric mappings
# --------------------------------------------------
metric_options = {
    "Line Bypass Score": "line_bypass_score",
    "Space Gain Metric": "space_gain_metric",
    "Structural Disruption Index": "structural_disruption_index",
    "Tactical Impact Value": "TIV_structural",
    "Pass Distance": "pass_distance",
    "Pass Verticality": "pass_verticality",
}

color_options = {
    "Pass Archetype": "pass_type",
    "Tactical Impact Value": "TIV_structural",
    "Team": "team_name",
    "Pass Distance": "pass_distance",
    "Pass Verticality": "pass_verticality",
}

st.markdown("""
<div class="overview-hero">
    <div class="overview-title">Pass Archetypes</div>
    <p class="overview-subtitle">
        Explore how structural pass archetypes differ across teams, players, and tactical contexts.<br>
        This page is designed as an interactive structural passing explorer. Filter the data by team,
player, or archetype, then choose which metrics to compare in the main scatter plot. <br>
            Use the secondary charts to understand how archetypes are distributed and how Tactical Impact Value varies
across the selected sample. <br>
            Finally, dive into the table to see the underlying pass details and identify specific examples of high-impact passes.
    </p>
</div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Filters
# --------------------------------------------------
with st.container(border=True):
    st.markdown('### Filters</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    # Team filter
    teams = ["All"] + sorted(passes["team_name"].dropna().unique().tolist())
    selected_team = c1.selectbox("Team", teams)

    # Dependent player filter
    if selected_team == "All":
        available_players = ["All"] + sorted(passes["passer_name"].dropna().unique().tolist())
    else:
        available_players = ["All"] + sorted(
            passes.loc[passes["team_name"] == selected_team, "passer_name"].dropna().unique().tolist()
        )

    selected_player = c2.selectbox("Passer", available_players)

    pass_types = ["All"] + [PASS_TYPE_LABELS.get(x, x) for x in PASS_TYPE_ORDER if x in passes["pass_type"].unique()]
    selected_pass_type_label = c3.selectbox("Archetype", pass_types)

    tiv_min = float(passes["TIV_structural"].min())
    tiv_max = float(passes["TIV_structural"].max())
    selected_tiv_range = st.slider(
        "TIV range",
        min_value=tiv_min,
        max_value=tiv_max,
        value=(tiv_min, tiv_max),
    )


    # --------------------------------------------------
    # Filtering logic
    # --------------------------------------------------
    filtered = passes.copy()

    if selected_team != "All":
        filtered = filtered[filtered["team_name"] == selected_team]

    if selected_player != "All":
        filtered = filtered[filtered["passer_name"] == selected_player]

    selected_pass_type = None
    if selected_pass_type_label != "All":
        reverse_labels = {v: k for k, v in PASS_TYPE_LABELS.items()}
        selected_pass_type = reverse_labels.get(selected_pass_type_label, selected_pass_type_label)
        filtered = filtered[filtered["pass_type"] == selected_pass_type]

    filtered = filtered[
        (filtered["TIV_structural"] >= selected_tiv_range[0]) &
        (filtered["TIV_structural"] <= selected_tiv_range[1])
    ].copy()

    # --------------------------------------------------
    # Empty-state protection
    # --------------------------------------------------
    if filtered.empty:
        st.warning("No passes match the current filter combination. Try widening the TIV range or resetting team/player filters.")
        st.stop()

    # --------------------------------------------------
    # KPI summary
    # --------------------------------------------------
    st.markdown('### Current selection summary', unsafe_allow_html=True)

    dominant_archetype = (
        filtered["pass_type"]
        .value_counts(normalize=True)
        .rename(index=PASS_TYPE_LABELS)
        .idxmax()
    )

    mc1, mc2, mc3, mc4, mc5 = st.columns([1, 1, 1.2, 1, 1], gap="small")

    with mc1:
        st.markdown(f"""
        <div class="info-box">
            <div class="metric-label">Filtered Passes</div>
            <div class="metric-value">{len(filtered):,}</div>
            <div class="metric-sub">Passes currently matching the selected filters.</div>
        </div>
        """, unsafe_allow_html=True)

    with mc2:
        st.markdown(f"""
        <div class="info-box">
            <div class="metric-label">Mean TIV</div>
            <div class="metric-value">{filtered['TIV_structural'].mean():.2f}</div>
            <div class="metric-sub">Average structural impact of the selected passes.</div>
        </div>
        """, unsafe_allow_html=True)

    with mc3:
        st.markdown(f"""
        <div class="info-box">
            <div class="metric-label">Dominant Archetype</div>
            <div class="metric-value" style="font-size:1.2rem;">{dominant_archetype}</div>
            <div class="metric-sub">Most frequent structural pass archetype in the filtered sample.</div>
        </div>
        """, unsafe_allow_html=True)

    with mc4:
        st.markdown(f"""
        <div class="info-box">
            <div class="metric-label">Shot Probability</div>
            <div class="metric-value">{100*filtered['shot_within_window'].mean():.1f}%</div>
            <div class="metric-sub">Probability of a shot occurring within the analysis window.</div>
        </div>
        """, unsafe_allow_html=True)
    with mc5:
        st.markdown(f"""
        <div class="info-box">
            <div class="metric-label">Goal Probability</div>
            <div class="metric-value">{100*filtered['goal_within_window'].mean():.1f}%</div>
            <div class="metric-sub">Probability of a goal occurring within the analysis window.</div>
        </div>
        """, unsafe_allow_html=True)

# --------------------------------------------------
# Main interactive explorer
# --------------------------------------------------
with st.container(border=True):
    st.markdown('### Structural space explorer', unsafe_allow_html=True)

    c4, c5, c6 = st.columns(3)

    x_axis_label = c4.selectbox("X-axis", list(metric_options.keys()), index=0)
    y_axis_label = c5.selectbox("Y-axis", list(metric_options.keys()), index=1)
    color_by_label = c6.selectbox("Color by", list(color_options.keys()), index=0)

    x_col = metric_options[x_axis_label]
    y_col = metric_options[y_axis_label]
    color_col = color_options[color_by_label]
    # filtered["pass_type_label"] = filtered["pass_type"].map(PASS_TYPE_LABELS)
    custom_cols = [
        "team_name",
        "passer_name",
        "receiver_name",
        "pass_type_label",
        "TIV_structural",
        "line_bypass_score",
        "space_gain_metric",
        "structural_disruption_index",
        "pass_distance",
        "pass_verticality",
    ]

    if color_col == "pass_type":
        fig = px.scatter(
        filtered,
        x=x_col,
        y=y_col,
        color="pass_type",
        opacity=0.68,
        color_discrete_map=PASS_TYPE_COLORS,
        custom_data=custom_cols,
        labels={
            x_col: x_axis_label,
            y_col: y_axis_label,
            "pass_type": "Archetype",
        },
        title=f"{x_axis_label} vs {y_axis_label}",
    )
        legend_name_map = {
        "circulatory": "Circulatory",
        "destabilising": "Destabilising",
        "line_breaking": "Line-breaking",
        "space_expanding": "Space-expanding",
        "Circulatory": "Circulatory",
        "Destabilising": "Destabilising",
        "Line-breaking": "Line-breaking",
        "Space-expanding": "Space-expanding",
    }

        for tr in fig.data:
            if tr.name in legend_name_map:
                tr.name = legend_name_map[tr.name]
    else:
        fig = px.scatter(
            filtered,
            x=x_col,
            y=y_col,
            color=color_col,
            custom_data=custom_cols,
            labels={
                x_col: x_axis_label,
                y_col: y_axis_label,
                color_col: color_by_label,
            },
            title=f"{x_axis_label} vs {y_axis_label}",
            opacity=0.78,
            color_continuous_scale="Viridis" if pd.api.types.is_numeric_dtype(filtered[color_col]) else None,
        )

    fig.update_traces(
        marker=dict(size=10, line=dict(width=0.5, color="white")),
        hovertemplate=(
            "<b>%{customdata[1]}</b><br>"
            "Team: %{customdata[0]}<br>"
            "Receiver: %{customdata[2]}<br>"
            "Archetype: %{customdata[3]}<br>"
            "TIV: %{customdata[4]:.2f}<br>"
            "LBS: %{customdata[5]:.2f}<br>"
            "SGM: %{customdata[6]:.2f}<br>"
            "SDI: %{customdata[7]:.2f}<br>"
            "Pass Distance: %{customdata[8]:.2f}<br>"
            "Pass Verticality: %{customdata[9]:.2f}"
            "<extra></extra>"
        )
    )
    fig.update_layout(
        template="plotly_white",
        height=560,
        title_x=0.0,
        font=dict(size=12),
        margin=dict(t=50, l=20, r=20, b=20),
        legend_title_text="",
    )

    fig.update_xaxes(showgrid=True, gridcolor="#E5E7EB", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#E5E7EB", zeroline=False)

    st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class="info-box">
<b>How to read this figure:</b> each point is a pass. Use the axis selectors above to compare different
structural metrics and explore how pass archetypes, teams, and Tactical Impact Value occupy different
regions of structural space.
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Secondary charts
# --------------------------------------------------
with st.container(border=True):
    st.markdown('### Archetype mix and Tactical Impact Value</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1.2], gap="large")

    with left:
        mix = (
            filtered["pass_type"]
            .value_counts(normalize=True)
            .rename_axis("pass_type")
            .reset_index(name="percentage")
        )
        mix["pass_type_label"] = mix["pass_type"].map(PASS_TYPE_LABELS).fillna(mix["pass_type"])

        fig_mix = px.pie(
            mix,
            names="pass_type_label",
            values="percentage",
            color="pass_type",
            color_discrete_map=PASS_TYPE_COLORS,
            hole=0.45,
        )

        fig_mix.update_traces(
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Share: %{percent}<extra></extra>"
        )
        fig_mix.update_layout(
            template="plotly_white",
            title="Archetype composition",
            title_x=0.0,
            height=420,
            margin=dict(t=50, l=20, r=20, b=20),
            showlegend=False,
        )
        st.plotly_chart(fig_mix, use_container_width=True)

    with right:
        box_df = filtered.copy()
        box_df["pass_type_label"] = box_df["pass_type"].map(PASS_TYPE_LABELS).fillna(box_df["pass_type"])

        fig_tiv = px.box(
            box_df,
            # x="pass_type_label",
            y="TIV_structural",
            color="pass_type",
            color_discrete_map=PASS_TYPE_COLORS,
            points="outliers",
            labels={
                "pass_type_label": "",
                "TIV_structural": "Tactical Impact Value (TIV)"
            },
            title="TIV distribution by pass archetype"
        )

        fig_tiv.update_layout(
            template="plotly_white",
            title_x=0.0,
            height=420, 
            margin=dict(t=50, l=20, r=20, b=50),
            showlegend=True,
            legend_title_text="",
            legend=dict(orientation="h", yanchor="bottom", y=-0.12, xanchor="right", x=1)
        )
        fig_tiv.update_xaxes(showgrid=False)
        fig_tiv.update_yaxes(showgrid=True, gridcolor="#E5E7EB", zeroline=False)

        st.plotly_chart(fig_tiv, use_container_width=True)

# --------------------------------------------------
# Better table
# --------------------------------------------------
with st.container(border=True):
    st.markdown('### Pass table', unsafe_allow_html=True)
    
    top_n_table = st.slider("Rows in table", min_value=10, max_value=100, value=25, step=5)

    sort_options = {
        "Tactical Impact Value": "TIV_structural",
        "Line Bypass Score": "line_bypass_score",
        "Space Gain Metric": "space_gain_metric",
        "Structural Disruption Index": "structural_disruption_index",
        "Pass Distance": "pass_distance",
        "Pass Verticality": "pass_verticality",
    }

    tc1, tc2 = st.columns([1, 1])
    sort_label = tc1.selectbox("Sort table by", list(sort_options.keys()), index=0)
    sort_col = sort_options[sort_label]
    sort_desc = tc2.toggle("Sort descending", value=True)

    table_df = (
        filtered.sort_values(sort_col, ascending=not sort_desc)
        .head(top_n_table)
        .copy()
    )

    display_cols = [
        "team_name",
        "passer_name",
        "receiver_name",
        "pass_type_label",
        "TIV_structural",
        "line_bypass_score",
        "space_gain_metric",
        "structural_disruption_index",
        "pass_distance",
        "pass_verticality",
        "final_third_entry",
        "box_entry",
        "shot_within_window",
        "goal_within_window",
    ]

    table_df = table_df[display_cols].rename(columns={
        "team_name": "Team",
        "passer_name": "Passer",
        "receiver_name": "Receiver",
        "pass_type_label": "Archetype",
        "TIV_structural": "TIV",
        "line_bypass_score": "LBS",
        "space_gain_metric": "SGM",
        "structural_disruption_index": "SDI",
        "pass_distance": "Distance",
        "pass_verticality": "Verticality",
        "final_third_entry": "Final 3rd",
        "box_entry": "Box Entry",
        "shot_within_window": "Shot",
        "goal_within_window": "Goal",
    })

    st.dataframe(
        table_df,
        use_container_width=True,
        height=500,
    )

render_page_footer()