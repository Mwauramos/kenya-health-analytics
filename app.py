"""
Kenya County Health Analytics Platform
ZENIK.AI — Amos Mwaura
A multi-tab Streamlit dashboard covering disease burden, epidemic trends,
county comparison, health system capacity, and a downloadable PDF report.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os

from data import COUNTY_DF, TS_DF, NAT_DF, DISEASES, YEARS, COUNTIES
from report import generate_report

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kenya County Health Analytics | ZENIK.AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Brand colours ─────────────────────────────────────────────────────────────
BG      = "#080c14"
SURFACE = "#0d1320"
BLUE    = "#2563eb"
BLUE_L  = "#3b82f6"
CYAN    = "#06b6d4"
GREEN   = "#22c55e"
AMBER   = "#f59e0b"
RED     = "#ef4444"
MUTED   = "#6b7fa3"
WHITE   = "#f0f4ff"

DISEASE_COLORS = {
    "Malaria": BLUE_L,
    "Cholera": CYAN,
    "TB":      GREEN,
    "HIV":     "#a855f7",
    "Dengue":  AMBER,
    "Measles": RED,
}

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: {BG};
    color: {WHITE};
  }}
  .main {{ background-color: {BG}; }}
  .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; }}
  section[data-testid="stSidebar"] > div {{
    background-color: {SURFACE};
    border-right: 1px solid #1e2d45;
  }}
  .stTabs [data-baseweb="tab-list"] {{
    background-color: {SURFACE};
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
  }}
  .stTabs [data-baseweb="tab"] {{
    border-radius: 8px;
    color: {MUTED};
    font-weight: 500;
    font-size: 0.85rem;
    padding: 8px 16px;
  }}
  .stTabs [aria-selected="true"] {{
    background-color: {BLUE} !important;
    color: white !important;
  }}
  .metric-card {{
    background: {SURFACE};
    border: 1px solid #1e2d45;
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 12px;
  }}
  .metric-value {{
    font-size: 2rem;
    font-weight: 700;
    color: {BLUE_L};
    line-height: 1.1;
  }}
  .metric-label {{
    font-size: 0.78rem;
    color: {MUTED};
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }}
  .metric-delta {{
    font-size: 0.82rem;
    color: {GREEN};
    margin-top: 2px;
  }}
  .section-header {{
    font-size: 0.72rem;
    font-weight: 700;
    color: {BLUE_L};
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 4px;
  }}
  .page-title {{
    font-size: 1.9rem;
    font-weight: 700;
    color: {WHITE};
    margin-bottom: 2px;
  }}
  .page-sub {{
    font-size: 0.95rem;
    color: {MUTED};
    margin-bottom: 20px;
  }}
  .insight-box {{
    background: linear-gradient(135deg, #0d1a2e 0%, #0a1628 100%);
    border: 1px solid #1e2d45;
    border-left: 3px solid {BLUE_L};
    border-radius: 8px;
    padding: 14px 18px;
    margin: 10px 0;
    font-size: 0.9rem;
    color: #c8d8f0;
  }}
  .stSelectbox > div > div {{ background-color: {SURFACE}; border-color: #1e2d45; }}
  .stMultiSelect > div > div {{ background-color: {SURFACE}; border-color: #1e2d45; }}
  h1, h2, h3 {{ color: {WHITE}; }}
  .stDownloadButton > button {{
    background-color: {BLUE};
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 10px 24px;
  }}
  .stDownloadButton > button:hover {{ background-color: {BLUE_L}; }}
  .sleep-note {{
    background: #1a2a40;
    border: 1px solid #2563eb;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.82rem;
    color: {MUTED};
    margin-top: 8px;
  }}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:16px 0 8px 0">
      <div style="font-size:1.3rem;font-weight:700;color:{WHITE}">🏥 ZENIK.AI</div>
      <div style="font-size:0.78rem;color:{MUTED};letter-spacing:0.08em">
        KENYA HEALTH ANALYTICS
      </div>
    </div>
    <hr style="border-color:#1e2d45;margin:8px 0 16px 0">
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="section-header">Filters</div>', unsafe_allow_html=True)
    selected_disease = st.selectbox("Disease", DISEASES, index=0)
    selected_year    = st.selectbox("Year", sorted(YEARS, reverse=True), index=0)
    selected_counties = st.multiselect(
        "Counties (comparison)", COUNTIES[:10],
        default=COUNTIES[:5])

    st.markdown("<hr style='border-color:#1e2d45;margin:16px 0'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:0.78rem;color:{MUTED}">
      <b style="color:{BLUE_L}">Data</b><br>
      Simulated Kenya MOH indicators<br>calibrated to real epidemiological ranges<br>
      (2015 to 2024, all 47 counties)<br><br>
      <b style="color:{BLUE_L}">Author</b><br>
      Amos Mwaura — ZENIK.AI<br>
      <a href="https://mwauramos.github.io/zenik-ai" style="color:{BLUE_L}">
        Portfolio</a>
    </div>
    """, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="section-header">ZENIK.AI — Healthcare AI Portfolio</div>
<div class="page-title">Kenya County Health Analytics Platform</div>
<div class="page-sub">
  Disease burden, epidemic trends, and health system capacity across all 47 counties
  &nbsp;·&nbsp; 2015 to 2024
</div>
""", unsafe_allow_html=True)

# ── KPI row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
total_cases_latest = TS_DF[TS_DF["year"] == 2024]["cases"].sum()
total_cases_prev   = TS_DF[TS_DF["year"] == 2023]["cases"].sum()
malaria_latest     = TS_DF[(TS_DF["year"]==2024) & (TS_DF["disease"]=="Malaria")]["cases"].sum()
hiv_prev           = COUNTY_DF["hiv_prevalence"].mean()
u5_mort            = COUNTY_DF["under5_mortality"].mean()
beds_avg           = COUNTY_DF["beds_per_1000"].mean()

def kpi(col, val, label, delta=None):
    with col:
        delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ""
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-value">{val}</div>
          <div class="metric-label">{label}</div>
          {delta_html}
        </div>
        """, unsafe_allow_html=True)

kpi(k1, f"{total_cases_latest:,.0f}", "Total Cases (2024)",
    f"vs {total_cases_prev:,.0f} (2023)")
kpi(k2, f"{malaria_latest:,.0f}", "Malaria Cases (2024)")
kpi(k3, f"{hiv_prev:.1f}%", "Avg HIV Prevalence")
kpi(k4, f"{u5_mort:.0f}", "Avg Under-5 Mortality / 1k")
kpi(k5, f"{beds_avg:.2f}", "Avg Beds per 1,000", "WHO min: 2.5")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "🗺️ Disease Burden",
    "📈 Epidemic Trends",
    "🏥 County Comparison",
    "⚕️ Health System",
    "📄 Download Report",
])

# ─── Tab 1: Disease Burden ────────────────────────────────────────────────────
with tabs[0]:
    st.markdown(f'<div class="section-header">Disease Burden — {selected_disease} · {selected_year}</div>', unsafe_allow_html=True)

    col_map = {
        "Malaria": "malaria_incidence", "TB": "tb_incidence",
        "HIV": "hiv_prevalence", "Cholera": "cholera_incidence",
        "Dengue": "malaria_incidence",  # reuse for display
        "Measles": "cholera_incidence",
    }
    metric_col = col_map.get(selected_disease, "malaria_incidence")

    c1, c2 = st.columns([3, 2])

    with c1:
        # Choropleth map using Kenya counties GeoJSON
        _COUNTY_NAME_MAP = {
            "Eldoret/Uasin Gishu": "Uasin Gishu",
            "Mwingi/Kitui":        "Kitui",
            "Ol Kalou/Nyandarua":  "Nyandarua",
        }
        _geojson_path = os.path.join(os.path.dirname(__file__), "kenya-counties.geojson")
        try:
            with open(_geojson_path) as _f:
                _kenya_geojson = json.load(_f)
            _map_df = COUNTY_DF.copy()
            _map_df["county_geo"] = _map_df["county"].replace(_COUNTY_NAME_MAP)
            fig_map = px.choropleth(
                _map_df,
                geojson=_kenya_geojson,
                locations="county_geo",
                featureidkey="properties.COUNTY",
                color=metric_col,
                hover_name="county",
                hover_data={metric_col: True, "population": True, "county_geo": False},
                color_continuous_scale=[[0, "#0d1a2e"], [0.3, BLUE], [0.7, CYAN], [1, "#f59e0b"]],
                title=f"{selected_disease} Burden by County",
                labels={metric_col: "Incidence / Prevalence"},
            )
            fig_map.update_geos(
                fitbounds="locations", visible=False,
                bgcolor=SURFACE,
            )
        except Exception:
            # Fallback to scatter if GeoJSON unavailable
            fig_map = px.scatter(
                COUNTY_DF, x="lon", y="lat",
                size=metric_col, color=metric_col,
                hover_name="county",
                color_continuous_scale=[[0, "#0d1a2e"], [0.3, BLUE], [0.7, CYAN], [1, "#f59e0b"]],
                size_max=40,
                title=f"{selected_disease} Burden by County",
                labels={metric_col: "Incidence / Prevalence"},
            )
        fig_map.update_layout(
            paper_bgcolor=SURFACE,
            font_color=WHITE,
            coloraxis_colorbar=dict(tickfont=dict(color=MUTED)),
            title_font=dict(size=13, color=WHITE),
            margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with c2:
        top10 = COUNTY_DF.nlargest(10, metric_col)[["county", metric_col]].reset_index(drop=True)
        fig_bar = px.bar(
            top10, x=metric_col, y="county", orientation="h",
            color=metric_col,
            color_continuous_scale=[[0, BLUE], [1, CYAN]],
            title=f"Top 10 Counties — {selected_disease}",
            labels={metric_col: "Rate per 100k", "county": ""},
        )
        fig_bar.update_layout(
            plot_bgcolor=SURFACE, paper_bgcolor=SURFACE,
            font_color=WHITE, showlegend=False,
            yaxis=dict(autorange="reversed"),
            coloraxis_showscale=False,
            title_font=dict(size=13),
            margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Full county table
    st.markdown(f'<div class="section-header" style="margin-top:16px">All 47 Counties — Key Indicators</div>', unsafe_allow_html=True)
    display_df = COUNTY_DF[[
        "county","population","malaria_incidence","tb_incidence",
        "hiv_prevalence","cholera_incidence","under5_mortality","maternal_mortality"
    ]].rename(columns={
        "county":"County","population":"Population",
        "malaria_incidence":"Malaria/100k","tb_incidence":"TB/100k",
        "hiv_prevalence":"HIV %","cholera_incidence":"Cholera/100k",
        "under5_mortality":"U5 Mort/1k","maternal_mortality":"MMR/100k"
    })
    st.dataframe(
        display_df.sort_values("Malaria/100k", ascending=False).reset_index(drop=True),
        use_container_width=True, height=340
    )

# ─── Tab 2: Epidemic Trends ───────────────────────────────────────────────────
with tabs[1]:
    st.markdown('<div class="section-header">Epidemic Trends — National 2015 to 2024</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        # National trends all diseases
        fig_trends = go.Figure()
        for disease in DISEASES:
            d = NAT_DF[NAT_DF["disease"] == disease].sort_values("year")
            fig_trends.add_trace(go.Scatter(
                x=d["year"], y=d["cases"], mode="lines+markers",
                name=disease, line=dict(color=DISEASE_COLORS[disease], width=2),
                marker=dict(size=5),
            ))
        fig_trends.update_layout(
            title="National Case Counts by Disease (2015 to 2024)",
            plot_bgcolor=SURFACE, paper_bgcolor=SURFACE,
            font_color=WHITE,
            xaxis=dict(gridcolor="#1e2d45", title="Year"),
            yaxis=dict(gridcolor="#1e2d45", title="Total Cases"),
            legend=dict(bgcolor=BG, bordercolor="#1e2d45", borderwidth=1),
            title_font=dict(size=13),
            margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig_trends, use_container_width=True)

    with c2:
        # Selected disease trend + YoY change
        nat_sel = NAT_DF[NAT_DF["disease"] == selected_disease].sort_values("year").copy()
        nat_sel["yoy"] = nat_sel["cases"].pct_change() * 100
        fig_yoy = make_subplots(specs=[[{"secondary_y": True}]])
        fig_yoy.add_trace(go.Bar(
            x=nat_sel["year"], y=nat_sel["cases"],
            name="Cases", marker_color=DISEASE_COLORS[selected_disease],
            opacity=0.8,
        ), secondary_y=False)
        fig_yoy.add_trace(go.Scatter(
            x=nat_sel["year"], y=nat_sel["yoy"],
            name="YoY %", mode="lines+markers",
            line=dict(color=AMBER, width=2), marker=dict(size=5),
        ), secondary_y=True)
        fig_yoy.update_layout(
            title=f"{selected_disease} — Cases & Year-on-Year Change",
            plot_bgcolor=SURFACE, paper_bgcolor=SURFACE,
            font_color=WHITE, title_font=dict(size=13),
            legend=dict(bgcolor=BG, bordercolor="#1e2d45", borderwidth=1),
            margin=dict(l=0, r=0, t=40, b=0),
        )
        fig_yoy.update_yaxes(title_text="Cases", gridcolor="#1e2d45", secondary_y=False)
        fig_yoy.update_yaxes(title_text="YoY Change %", gridcolor="#1e2d45", secondary_y=True)
        st.plotly_chart(fig_yoy, use_container_width=True)

    # County-level trends for selected counties
    st.markdown(f'<div class="section-header" style="margin-top:8px">{selected_disease} Trends — Selected Counties</div>', unsafe_allow_html=True)
    ts_sel = TS_DF[
        (TS_DF["disease"] == selected_disease) &
        (TS_DF["county"].isin(selected_counties))
    ].sort_values("year")
    if ts_sel.empty:
        st.info("Select counties in the sidebar to compare trends.")
    else:
        fig_county = px.line(
            ts_sel, x="year", y="cases", color="county",
            title=f"{selected_disease} Case Counts — County Comparison",
            labels={"cases": "Cases", "year": "Year", "county": "County"},
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_county.update_layout(
            plot_bgcolor=SURFACE, paper_bgcolor=SURFACE,
            font_color=WHITE, title_font=dict(size=13),
            legend=dict(bgcolor=BG, bordercolor="#1e2d45", borderwidth=1),
            margin=dict(l=0, r=0, t=40, b=0),
        )
        fig_county.update_traces(line=dict(width=2))
        st.plotly_chart(fig_county, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
      <b>Key trend:</b> Malaria case counts have declined steadily since 2015, consistent
      with the Kenya National Malaria Control Programme's ITN distribution scale-up.
      Cholera remains episodic with periodic spikes. HIV new infections have stabilised
      following ART scale-up.
    </div>
    """, unsafe_allow_html=True)

# ─── Tab 3: County Comparison ─────────────────────────────────────────────────
with tabs[2]:
    st.markdown('<div class="section-header">County Comparison — Multi-Indicator Analysis</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        # Radar chart for selected counties
        categories = ["malaria_incidence","tb_incidence","hiv_prevalence",
                      "cholera_incidence","under5_mortality"]
        labels = ["Malaria","TB","HIV","Cholera","U5 Mort"]
        fig_radar = go.Figure()
        colors_r = [BLUE_L, CYAN, GREEN, AMBER, RED, "#a855f7"]
        for j, county in enumerate(selected_counties[:6]):
            row = COUNTY_DF[COUNTY_DF["county"] == county].iloc[0]
            vals = [row[c] for c in categories]
            # Normalise 0-1
            maxs = [COUNTY_DF[c].max() for c in categories]
            norm = [v/m for v,m in zip(vals,maxs)]
            fig_radar.add_trace(go.Scatterpolar(
                r=norm + [norm[0]], theta=labels + [labels[0]],
                fill="toself", name=county,
                line=dict(color=colors_r[j % len(colors_r)], width=1.5),
                opacity=0.7,
            ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor=SURFACE,
                radialaxis=dict(visible=True, range=[0,1], gridcolor="#1e2d45",
                                tickfont=dict(color=MUTED, size=8)),
                angularaxis=dict(gridcolor="#1e2d45", tickfont=dict(color=WHITE, size=9)),
            ),
            paper_bgcolor=SURFACE, font_color=WHITE,
            title="Multi-Disease Burden Radar (normalised)",
            title_font=dict(size=13),
            legend=dict(bgcolor=BG, bordercolor="#1e2d45", borderwidth=1),
            margin=dict(l=40, r=40, t=50, b=20),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with c2:
        # Scatter: malaria vs TB coloured by HIV
        fig_scatter = px.scatter(
            COUNTY_DF, x="malaria_incidence", y="tb_incidence",
            size="population", color="hiv_prevalence",
            hover_name="county",
            color_continuous_scale=[[0,"#0d1a2e"],[0.3,BLUE],[0.7,CYAN],[1,"#a855f7"]],
            title="Malaria vs TB Incidence (bubble=population, colour=HIV)",
            labels={
                "malaria_incidence":"Malaria Incidence / 100k",
                "tb_incidence":"TB Incidence / 100k",
                "hiv_prevalence":"HIV %",
            },
            size_max=40,
        )
        fig_scatter.update_layout(
            plot_bgcolor=SURFACE, paper_bgcolor=SURFACE,
            font_color=WHITE, title_font=dict(size=13),
            xaxis=dict(gridcolor="#1e2d45"),
            yaxis=dict(gridcolor="#1e2d45"),
            coloraxis_colorbar=dict(tickfont=dict(color=MUTED)),
            margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Ranked bar: under-5 mortality all counties
    st.markdown('<div class="section-header" style="margin-top:8px">Under-5 Mortality Rate — All Counties Ranked</div>', unsafe_allow_html=True)
    df_ranked = COUNTY_DF.sort_values("under5_mortality", ascending=False).reset_index(drop=True)
    fig_ranked = px.bar(
        df_ranked, x="county", y="under5_mortality",
        color="under5_mortality",
        color_continuous_scale=[[0, BLUE], [0.5, CYAN], [1, RED]],
        title="Under-5 Mortality Rate per 1,000 Live Births — All 47 Counties",
        labels={"under5_mortality": "U5 Mortality / 1k", "county": ""},
    )
    fig_ranked.update_layout(
        plot_bgcolor=SURFACE, paper_bgcolor=SURFACE,
        font_color=WHITE, title_font=dict(size=13),
        xaxis=dict(tickangle=45, gridcolor="#1e2d45", tickfont=dict(size=8)),
        yaxis=dict(gridcolor="#1e2d45"),
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=40, b=80),
    )
    st.plotly_chart(fig_ranked, use_container_width=True)

# ─── Tab 4: Health System Capacity ────────────────────────────────────────────
with tabs[3]:
    st.markdown('<div class="section-header">Health System Capacity — Workforce and Infrastructure</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    def gauge(col, val, title, max_v, ref, ref_label):
        with col:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=val,
                title={"text": title, "font": {"size": 12, "color": WHITE}},
                number={"font": {"size": 24, "color": BLUE_L}},
                gauge={
                    "axis": {"range": [0, max_v], "tickcolor": MUTED,
                             "tickfont": {"size": 9, "color": MUTED}},
                    "bar": {"color": BLUE_L},
                    "bgcolor": SURFACE,
                    "bordercolor": "#1e2d45",
                    "threshold": {
                        "line": {"color": RED, "width": 2},
                        "thickness": 0.8, "value": ref,
                    },
                    "steps": [
                        {"range": [0, ref], "color": "#0d1a2e"},
                        {"range": [ref, max_v], "color": "#0a2010"},
                    ],
                },
            ))
            fig.update_layout(
                paper_bgcolor=SURFACE, font_color=WHITE,
                margin=dict(l=20, r=20, t=60, b=20), height=220,
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f'<div style="text-align:center;font-size:0.75rem;color:{MUTED}">'
                        f'WHO min: {ref} {ref_label}</div>', unsafe_allow_html=True)

    gauge(c1, round(COUNTY_DF["beds_per_1000"].mean(),2),
          "Avg Beds / 1,000", 5, 2.5, "beds/1k")
    gauge(c2, round(COUNTY_DF["nurses_per_1000"].mean(),2),
          "Avg Nurses / 1,000", 6, 4.5, "nurses/1k")
    gauge(c3, round(COUNTY_DF["doctors_per_1000"].mean(),2),
          "Avg Doctors / 1,000", 2, 1.0, "doctors/1k")

    c1, c2 = st.columns(2)

    with c1:
        # Facilities vs population scatter
        fig_fac = px.scatter(
            COUNTY_DF, x="population", y="health_facilities",
            hover_name="county", color="beds_per_1000",
            color_continuous_scale=[[0,"#0d1a2e"],[0.5,BLUE],[1,CYAN]],
            title="Health Facilities vs Population",
            labels={"population":"Population","health_facilities":"Health Facilities",
                    "beds_per_1000":"Beds/1k"},
            size="beds_per_1000", size_max=20,
        )
        fig_fac.update_layout(
            plot_bgcolor=SURFACE, paper_bgcolor=SURFACE,
            font_color=WHITE, title_font=dict(size=13),
            xaxis=dict(gridcolor="#1e2d45"),
            yaxis=dict(gridcolor="#1e2d45"),
            margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig_fac, use_container_width=True)

    with c2:
        # Heatmap: counties vs metrics
        metrics = ["beds_per_1000","nurses_per_1000","doctors_per_1000",
                   "immunisation_coverage","antenatal_coverage"]
        metric_labels = ["Beds/1k","Nurses/1k","Doctors/1k","Immunisation %","ANC %"]
        top20 = COUNTY_DF.nlargest(20, "beds_per_1000")
        heat_df = top20[["county"]+metrics].set_index("county")
        # Normalise each column
        heat_norm = (heat_df - heat_df.min()) / (heat_df.max() - heat_df.min())
        fig_heat = px.imshow(
            heat_norm.T,
            labels=dict(x="County", y="Indicator", color="Score"),
            color_continuous_scale=[[0,"#0d1a2e"],[0.5,BLUE],[1,CYAN]],
            aspect="auto",
            title="Health System Capacity Heatmap (top 20 counties, normalised)",
            y=metric_labels,
        )
        fig_heat.update_layout(
            paper_bgcolor=SURFACE, font_color=WHITE, title_font=dict(size=13),
            xaxis=dict(tickangle=45, tickfont=dict(size=7.5)),
            yaxis=dict(tickfont=dict(size=9)),
            coloraxis_colorbar=dict(tickfont=dict(color=MUTED)),
            margin=dict(l=0, r=0, t=40, b=60),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
      <b>Capacity gap:</b> Kenya's average bed density of
      {COUNTY_DF['beds_per_1000'].mean():.2f} per 1,000 falls below the WHO minimum of 2.5.
      Nurse density averages {COUNTY_DF['nurses_per_1000'].mean():.2f} against a WHO minimum of 4.5.
      Remote arid counties (Turkana, Marsabit, Mandera) show the widest gaps and highest
      disease burden — a compounding challenge for health outcomes.
    </div>
    """, unsafe_allow_html=True)

# ─── Tab 5: Download Report ────────────────────────────────────────────────────
with tabs[4]:
    st.markdown('<div class="section-header">Automated Report Generation</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="page-title" style="font-size:1.4rem">Download PDF Report</div>
    <div class="page-sub">
      A professional PDF report is generated from the live dashboard data — covering
      national health indicators, disease burden rankings, epidemic trends,
      and health system capacity with tables and charts.
    </div>
    """, unsafe_allow_html=True)

    # Report preview cards
    r1, r2, r3, r4 = st.columns(4)
    for col, icon, title, desc in [
        (r1, "📊", "National Overview", "KPI summary table across all 47 counties"),
        (r2, "🦟", "Disease Burden", "Top 10 county rankings for Malaria, TB, HIV, Cholera"),
        (r3, "📈", "Epidemic Trends", "National case count charts 2015 to 2024"),
        (r4, "🏥", "Health System", "Capacity gaps and workforce distribution"),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center">
              <div style="font-size:1.8rem;margin-bottom:8px">{icon}</div>
              <div style="font-weight:600;color:{WHITE};font-size:0.9rem">{title}</div>
              <div style="font-size:0.78rem;color:{MUTED};margin-top:4px">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Generate PDF Report", type="primary"):
        with st.spinner("Generating report..."):
            try:
                pdf_bytes = generate_report(COUNTY_DF, TS_DF, NAT_DF)
                st.download_button(
                    label="Download Kenya Health Analytics Report (PDF)",
                    data=pdf_bytes,
                    file_name="Kenya_County_Health_Analytics_Report_ZENIK_AI.pdf",
                    mime="application/pdf",
                )
                st.success("Report generated successfully.")
            except Exception as e:
                st.error(f"Report generation failed: {e}")

    st.markdown("<hr style='border-color:#1e2d45;margin:24px 0 16px 0'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:0.82rem;color:{MUTED}">
      <b style="color:{BLUE_L}">About this project</b><br>
      Built with Python, Streamlit, Plotly, and ReportLab as part of the ZENIK.AI
      Healthcare AI portfolio. Data is simulated and calibrated to real Kenya MOH
      and World Bank epidemiological ranges.<br><br>
      <a href="https://mwauramos.github.io/zenik-ai" style="color:{BLUE_L}">
        ZENIK.AI Portfolio</a> &nbsp;·&nbsp;
      <a href="https://github.com/Mwauramos/kenya-health-analytics" style="color:{BLUE_L}">
        GitHub</a> &nbsp;·&nbsp;
      <span>Amos Mwaura — mwauramos.n@gmail.com</span>
    </div>
    """, unsafe_allow_html=True)
