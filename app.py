"""
Africa Health Systems Comparative Dashboard
Kenya · Nigeria · South Africa · 2010 to 2024
ZENIK.AI — Amos Mwaura
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data import SNAPSHOT_DF, TS_DF, RADAR_DF, COUNTRIES, YEARS, COUNTRY_COLORS
from report import generate_report

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Africa Health Systems | ZENIK.AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

BG    = "#080c14"
SURF  = "#0d1320"
BLUE  = "#2563eb"
BLUE_L= "#3b82f6"
CYAN  = "#06b6d4"
GREEN = "#22c55e"
AMBER = "#f59e0b"
RED   = "#ef4444"
MUTED = "#6b7fa3"
WHITE = "#f0f4ff"

C = {"Kenya": BLUE_L, "Nigeria": AMBER, "South Africa": GREEN}

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  html, body, [class*="css"] {{ font-family:'Inter',sans-serif; background:{BG}; color:{WHITE}; }}
  .main {{ background:{BG}; }}
  .block-container {{ padding-top:1.5rem; padding-bottom:2rem; }}
  section[data-testid="stSidebar"] > div {{ background:{SURF}; border-right:1px solid #1e2d45; }}
  .stTabs [data-baseweb="tab-list"] {{ background:{SURF}; border-radius:10px; padding:4px; gap:4px; }}
  .stTabs [data-baseweb="tab"] {{ border-radius:8px; color:{MUTED}; font-weight:500; font-size:0.85rem; padding:8px 16px; }}
  .stTabs [aria-selected="true"] {{ background:{BLUE} !important; color:white !important; }}
  .metric-card {{ background:{SURF}; border:1px solid #1e2d45; border-radius:12px; padding:16px 18px; margin-bottom:10px; }}
  .metric-value {{ font-size:1.7rem; font-weight:700; line-height:1.1; }}
  .metric-label {{ font-size:0.75rem; color:{MUTED}; margin-top:3px; text-transform:uppercase; letter-spacing:0.05em; }}
  .section-header {{ font-size:0.72rem; font-weight:700; color:{BLUE_L}; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:4px; }}
  .page-title {{ font-size:1.8rem; font-weight:700; color:{WHITE}; margin-bottom:2px; }}
  .page-sub {{ font-size:0.92rem; color:{MUTED}; margin-bottom:20px; }}
  .insight-box {{ background:linear-gradient(135deg,#0d1a2e 0%,#0a1628 100%); border:1px solid #1e2d45; border-left:3px solid {BLUE_L}; border-radius:8px; padding:14px 18px; margin:10px 0; font-size:0.88rem; color:#c8d8f0; }}
  .country-pill {{ display:inline-block; padding:3px 12px; border-radius:20px; font-size:0.78rem; font-weight:600; margin-right:6px; }}
  .stDownloadButton > button {{ background:{BLUE}; color:white; border:none; border-radius:8px; font-weight:600; padding:10px 24px; }}
  .stDownloadButton > button:hover {{ background:{BLUE_L}; }}
  h1,h2,h3 {{ color:{WHITE}; }}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:16px 0 8px 0">
      <div style="font-size:1.3rem;font-weight:700;color:{WHITE}">🌍 ZENIK.AI</div>
      <div style="font-size:0.78rem;color:{MUTED};letter-spacing:0.08em">AFRICA HEALTH SYSTEMS</div>
    </div>
    <hr style="border-color:#1e2d45;margin:8px 0 16px 0">
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="section-header">Filters</div>', unsafe_allow_html=True)
    selected_countries = st.multiselect("Countries", COUNTRIES, default=COUNTRIES)
    year_range = st.slider("Year range", 2010, 2024, (2010, 2024))

    st.markdown("<hr style='border-color:#1e2d45;margin:16px 0'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:0.78rem;color:{MUTED}">
      <b style="color:{BLUE_L}">Data</b><br>
      World Bank Health Nutrition and Population Statistics<br>
      Live API via wbgapi · 2010 to 2024<br><br>
      <b style="color:{BLUE_L}">Author</b><br>
      Amos Mwaura — ZENIK.AI<br>
      <a href="https://mwauramos.github.io/zenik-ai" style="color:{BLUE_L}">Portfolio</a>
    </div>
    """, unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="section-header">ZENIK.AI — Healthcare AI Portfolio</div>
<div class="page-title">Africa Health Systems Comparative Analysis</div>
<div class="page-sub">
  Health spending, outcomes, and system capacity across Kenya, Nigeria, and South Africa
  &nbsp;·&nbsp; 2010 to 2024 &nbsp;·&nbsp; World Bank data
</div>
""", unsafe_allow_html=True)

# ── KPI row ────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
kpis = [
    (k1, "$563", "SA Health Spend / cap", GREEN, "vs Kenya $88 / Nigeria $74"),
    (k2, "69%",  "Nigeria OOP Burden",    CYAN,  "vs Kenya 24% / SA 7%"),
    (k3, "116",  "Nigeria U5 Mortality",  "#ef4444", "per 1,000 — highest of 3"),
    (k4, "18.3%","SA HIV Prevalence",     GREEN, "highest in the world"),
    (k5, "58",   "Kenya UHC Index (2023)",BLUE_L,"up from 43 in 2010"),
]
for col, val, label, color, note in kpis:
    with col:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-value" style="color:{color}">{val}</div>
          <div class="metric-label">{label}</div>
          <div style="font-size:0.75rem;color:{MUTED};margin-top:3px">{note}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "💰 Health Spending",
    "❤️ Health Outcomes",
    "⚕️ System Capacity",
    "🌐 Country Profiles",
    "📄 Download Report",
])

ts_filtered = TS_DF[
    (TS_DF["country"].isin(selected_countries)) &
    (TS_DF["year"] >= year_range[0]) &
    (TS_DF["year"] <= year_range[1])
]

def layout(title="", subtitle=""):
    return dict(
        plot_bgcolor=SURF, paper_bgcolor=SURF, font_color=WHITE,
        title=title, title_font=dict(size=13, color=WHITE),
        legend=dict(bgcolor=BG, bordercolor="#1e2d45", borderwidth=1),
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis=dict(gridcolor="#1e2d45"),
        yaxis=dict(gridcolor="#1e2d45"),
    )

colors = [C.get(c, BLUE_L) for c in selected_countries]

# ─── Tab 1: Health Spending ───────────────────────────────────────────────────
with tabs[0]:
    st.markdown('<div class="section-header">Health Financing — Trends and Structure</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        fig = go.Figure()
        for i, country in enumerate(selected_countries):
            d = ts_filtered[ts_filtered["country"] == country].sort_values("year")
            fig.add_trace(go.Scatter(x=d["year"], y=d["health_spend_per_cap"],
                mode="lines+markers", name=country,
                line=dict(color=C.get(country, BLUE_L), width=2), marker=dict(size=5)))
        fig.update_layout(**layout("Health Expenditure per Capita (USD)"))
        fig.update_yaxes(title_text="USD")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = go.Figure()
        for country in selected_countries:
            d = ts_filtered[ts_filtered["country"] == country].sort_values("year")
            fig2.add_trace(go.Scatter(x=d["year"], y=d["oop_pct_health"],
                mode="lines+markers", name=country,
                line=dict(color=C.get(country, BLUE_L), width=2), marker=dict(size=5)))
        fig2.add_hline(y=15, line_dash="dash", line_color=RED,
                       annotation_text="WHO target: <15%", annotation_font_color=RED)
        fig2.update_layout(**layout("Out-of-Pocket as % of Health Spend"))
        fig2.update_yaxes(title_text="%")
        st.plotly_chart(fig2, use_container_width=True)

    # Bar: current spend comparison
    snap = SNAPSHOT_DF[SNAPSHOT_DF["country"].isin(selected_countries)]
    fig3 = px.bar(snap, x="country", y="health_spend_per_cap",
        color="country", color_discrete_map=C,
        title="Health Spend per Capita (2023, USD)",
        labels={"health_spend_per_cap": "USD", "country": ""})
    fig3.update_layout(**layout())
    fig3.update_traces(showlegend=False)
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(fig3, use_container_width=True)
    with c4:
        fig4 = px.bar(snap, x="country", y="health_spend_pct_gdp",
            color="country", color_discrete_map=C,
            title="Health Spend as % of GDP (2023)",
            labels={"health_spend_pct_gdp": "% of GDP", "country": ""})
        fig4.add_hline(y=5, line_dash="dash", line_color=AMBER,
                       annotation_text="WHO rec: 5%", annotation_font_color=AMBER)
        fig4.update_layout(**layout())
        fig4.update_traces(showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
      <b>Key finding:</b> Nigeria allocates only 3.4% of GDP to health, below the Abuja Declaration
      target of 15%, forcing households to shoulder 69% of costs directly. South Africa's 8.1%
      GDP allocation funds a dual public/private system but has not resolved equity gaps.
      Kenya's trajectory — rising spend with falling OOP — reflects the most sustainable
      financing reform path of the three.
    </div>
    """, unsafe_allow_html=True)

# ─── Tab 2: Health Outcomes ───────────────────────────────────────────────────
with tabs[1]:
    st.markdown('<div class="section-header">Health Outcomes — Mortality, Life Expectancy, Immunisation</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        fig = go.Figure()
        for country in selected_countries:
            d = ts_filtered[ts_filtered["country"] == country].sort_values("year")
            fig.add_trace(go.Scatter(x=d["year"], y=d["life_expectancy"],
                mode="lines+markers", name=country,
                line=dict(color=C.get(country, BLUE_L), width=2), marker=dict(size=5)))
        fig.update_layout(**layout("Life Expectancy at Birth (years)"))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = go.Figure()
        for country in selected_countries:
            d = ts_filtered[ts_filtered["country"] == country].sort_values("year")
            fig2.add_trace(go.Scatter(x=d["year"], y=d["u5_mortality"],
                mode="lines+markers", name=country,
                line=dict(color=C.get(country, BLUE_L), width=2), marker=dict(size=5)))
        fig2.update_layout(**layout("Under-5 Mortality Rate (per 1,000 live births)"))
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig3 = go.Figure()
        for country in selected_countries:
            d = ts_filtered[ts_filtered["country"] == country].sort_values("year")
            fig3.add_trace(go.Scatter(x=d["year"], y=d["maternal_mortality"],
                mode="lines+markers", name=country,
                line=dict(color=C.get(country, BLUE_L), width=2), marker=dict(size=5)))
        fig3.update_layout(**layout("Maternal Mortality Ratio (per 100,000 live births)"))
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        fig4 = go.Figure()
        for country in selected_countries:
            d = ts_filtered[ts_filtered["country"] == country].sort_values("year")
            fig4.add_trace(go.Scatter(x=d["year"], y=d["immunisation_dtp3"],
                mode="lines+markers", name=country,
                line=dict(color=C.get(country, BLUE_L), width=2), marker=dict(size=5)))
        fig4.add_hline(y=90, line_dash="dash", line_color=GREEN,
                       annotation_text="WHO target: 90%", annotation_font_color=GREEN)
        fig4.update_layout(**layout("DTP3 Immunisation Coverage (%)"))
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
      <b>Key finding:</b> Nigeria's under-5 mortality (116 / 1,000) is nearly 4x South Africa's (31)
      despite similar GDP per capita — a reflection of health system access rather than wealth alone.
      South Africa's life expectancy improvement from 57.0 to 64.9 years (2010 to 2023) is largely
      attributable to ART programme scale-up. Nigeria's DTP3 coverage of 54% leaves 46% of children
      unprotected against vaccine-preventable disease.
    </div>
    """, unsafe_allow_html=True)

# ─── Tab 3: System Capacity ───────────────────────────────────────────────────
with tabs[2]:
    st.markdown('<div class="section-header">Health System Capacity — Workforce and Infrastructure</div>', unsafe_allow_html=True)
    snap = SNAPSHOT_DF[SNAPSHOT_DF["country"].isin(selected_countries)]

    c1, c2, c3 = st.columns(3)
    def gauge(col, metric, title, who_min, unit=""):
        with col:
            vals = {row["country"]: row[metric] for _, row in snap.iterrows()}
            fig = go.Figure()
            for i, (country, val) in enumerate(vals.items()):
                fig.add_trace(go.Indicator(
                    mode="number+gauge",
                    value=val,
                    title={"text": country, "font": {"size": 10, "color": C.get(country, WHITE)}},
                    number={"font": {"size": 18, "color": C.get(country, WHITE)},
                            "suffix": unit},
                    gauge={
                        "axis": {"range": [0, max(who_min * 2, max(vals.values()) * 1.2)],
                                 "tickfont": {"size": 7, "color": MUTED}},
                        "bar": {"color": C.get(country, BLUE_L)},
                        "bgcolor": SURF,
                        "threshold": {"line": {"color": RED, "width": 2},
                                      "thickness": 0.8, "value": who_min},
                    },
                    domain={"row": i, "column": 0},
                ))
            fig.update_layout(
                grid={"rows": len(vals), "columns": 1, "pattern": "independent"},
                paper_bgcolor=SURF, font_color=WHITE,
                title=dict(text=title, font=dict(size=11, color=WHITE), x=0.5),
                margin=dict(l=20, r=20, t=50, b=10),
                height=220,
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f'<div style="text-align:center;font-size:0.72rem;color:{RED}">WHO min: {who_min}{unit}</div>', unsafe_allow_html=True)

    gauge(c1, "beds_per_1000",    "Beds per 1,000",    2.5)
    gauge(c2, "doctors_per_1000", "Doctors per 1,000", 1.0)
    gauge(c3, "nurses_per_1000",  "Nurses per 1,000",  4.5)

    # Capacity radar
    st.markdown('<div class="section-header" style="margin-top:16px">System Performance Radar</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        fig_radar = go.Figure()
        for country in selected_countries:
            d = RADAR_DF[RADAR_DF["country"] == country]
            vals = d["score"].tolist()
            lbls = d["metric"].tolist()
            fig_radar.add_trace(go.Scatterpolar(
                r=vals + [vals[0]], theta=lbls + [lbls[0]],
                fill="toself", name=country,
                line=dict(color=C.get(country, BLUE_L), width=1.5), opacity=0.7,
            ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor=SURF,
                radialaxis=dict(visible=True, range=[0,1], gridcolor="#1e2d45",
                                tickfont=dict(color=MUTED, size=8)),
                angularaxis=dict(gridcolor="#1e2d45", tickfont=dict(color=WHITE, size=9)),
            ),
            paper_bgcolor=SURF, font_color=WHITE,
            title="Overall Health System Performance (normalised)",
            title_font=dict(size=12),
            legend=dict(bgcolor=BG, bordercolor="#1e2d45", borderwidth=1),
            margin=dict(l=40, r=40, t=50, b=20),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with c2:
        # UHC index trend
        fig_uhc = go.Figure()
        for country in selected_countries:
            d = ts_filtered[ts_filtered["country"] == country].sort_values("year")
            fig_uhc.add_trace(go.Scatter(x=d["year"], y=d["uhc_index"],
                mode="lines+markers", name=country,
                line=dict(color=C.get(country, BLUE_L), width=2), marker=dict(size=5)))
        fig_uhc.add_hline(y=80, line_dash="dash", line_color=AMBER,
                          annotation_text="SDG target: 80", annotation_font_color=AMBER)
        uhc_layout = layout("UHC Service Coverage Index (2010 to 2024)")
        uhc_layout["yaxis"]["range"] = [0, 100]
        fig_uhc.update_layout(**uhc_layout)
        st.plotly_chart(fig_uhc, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
      <b>Capacity gap:</b> All three countries fall below the WHO minimum of 2.5 hospital beds
      per 1,000 population. Nigeria at 0.5 beds per 1,000 faces the most acute infrastructure
      deficit. Only South Africa approaches adequate nurse density (4.98 vs WHO min 4.5).
      Kenya and Nigeria face compounding workforce and infrastructure gaps that limit the
      impact of any financing reform.
    </div>
    """, unsafe_allow_html=True)

# ─── Tab 4: Country Profiles ──────────────────────────────────────────────────
with tabs[3]:
    st.markdown('<div class="section-header">Country Profiles — Side-by-Side Comparison</div>', unsafe_allow_html=True)

    cols = st.columns(len(selected_countries))
    metrics = [
        ("population_m",         "Population (M)",            ".1f", ""),
        ("gdp_per_capita",       "GDP per Capita",            ",.0f", "$"),
        ("health_spend_per_cap", "Health Spend / cap",        ",.0f", "$"),
        ("health_spend_pct_gdp", "Health Spend % GDP",        ".1f",  "%"),
        ("oop_pct_health",       "Out-of-Pocket %",           ".1f",  "%"),
        ("uhc_index",            "UHC Index",                 ".0f",  ""),
        ("life_expectancy",      "Life Expectancy",           ".1f",  " yrs"),
        ("u5_mortality",         "U5 Mortality / 1k",         ".0f",  ""),
        ("maternal_mortality",   "Maternal Mortality / 100k", ",.0f", ""),
        ("immunisation_dtp3",    "DTP3 Coverage",             ".0f",  "%"),
        ("hiv_prevalence",       "HIV Prevalence",            ".1f",  "%"),
        ("tb_incidence",         "TB Incidence / 100k",       ".0f",  ""),
        ("beds_per_1000",        "Beds / 1,000",              ".1f",  ""),
        ("doctors_per_1000",     "Doctors / 1,000",           ".2f",  ""),
        ("nurses_per_1000",      "Nurses / 1,000",            ".2f",  ""),
    ]

    for col, country in zip(cols, selected_countries):
        with col:
            row = SNAPSHOT_DF[SNAPSHOT_DF["country"] == country].iloc[0]
            st.markdown(f"""
            <div style="background:{SURF};border:1px solid {C.get(country,'#1e2d45')};
                 border-radius:12px;padding:20px;margin-bottom:12px">
              <div style="font-size:1.1rem;font-weight:700;color:{C.get(country,WHITE)};
                   margin-bottom:16px">🌍 {country}</div>
            """, unsafe_allow_html=True)
            for field, label, fmt, prefix in metrics:
                val = row[field]
                if pd.isna(val):
                    formatted = "n/a"
                elif prefix == "$":
                    formatted = f"{prefix}{val:{fmt}}"
                else:
                    formatted = f"{val:{fmt}}{prefix}"
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;
                     padding:5px 0;border-bottom:1px solid #1e2d45">
                  <span style="font-size:0.78rem;color:{MUTED}">{label}</span>
                  <span style="font-size:0.82rem;font-weight:600;color:{WHITE}">{formatted}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ─── Tab 5: Download Report ───────────────────────────────────────────────────
with tabs[4]:
    st.markdown('<div class="section-header">Automated Report Generation</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="page-title" style="font-size:1.4rem">Download PDF Report</div>
    <div class="page-sub">
      A professional comparative health systems report covering financing, outcomes,
      capacity, and policy recommendations for Kenya, Nigeria, and South Africa.
    </div>
    """, unsafe_allow_html=True)

    r1, r2, r3, r4 = st.columns(4)
    for col, icon, title, desc in [
        (r1, "💰", "Health Financing", "Spend per capita, % GDP, OOP burden"),
        (r2, "❤️", "Health Outcomes", "Life expectancy, U5 mortality, MMR"),
        (r3, "⚕️", "System Capacity", "Beds, doctors, nurses vs WHO thresholds"),
        (r4, "📋", "Policy Insights", "Country-specific findings and recommendations"),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center">
              <div style="font-size:1.8rem;margin-bottom:8px">{icon}</div>
              <div style="font-weight:600;color:{WHITE};font-size:0.88rem">{title}</div>
              <div style="font-size:0.76rem;color:{MUTED};margin-top:4px">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Generate PDF Report", type="primary"):
        with st.spinner("Generating report..."):
            try:
                pdf_bytes = generate_report(SNAPSHOT_DF, TS_DF)
                st.download_button(
                    label="Download Africa Health Systems Report (PDF)",
                    data=pdf_bytes,
                    file_name="Africa_Health_Systems_Analysis_ZENIK_AI.pdf",
                    mime="application/pdf",
                )
                st.success("Report generated successfully.")
            except Exception as e:
                st.error(f"Report generation failed: {e}")

    st.markdown("<hr style='border-color:#1e2d45;margin:24px 0 16px 0'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:0.82rem;color:{MUTED}">
      <b style="color:{BLUE_L}">About this project</b><br>
      Rebuilt from a comparative R analysis as a live interactive dashboard using Python,
      Streamlit, Plotly, and ReportLab. Data calibrated to World Bank Health Nutrition and
      Population Statistics (2010 to 2024).<br><br>
      <a href="https://mwauramos.github.io/zenik-ai" style="color:{BLUE_L}">ZENIK.AI Portfolio</a>
      &nbsp;·&nbsp;
      <a href="https://github.com/Mwauramos/Health-and-Population-Analysis-for-Kenya-Nigeria-and-South-Africa"
         style="color:{BLUE_L}">GitHub</a>
      &nbsp;·&nbsp;
      <span>Amos Mwaura — mwauramos.n@gmail.com</span>
    </div>
    """, unsafe_allow_html=True)
 
