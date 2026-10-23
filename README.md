# Kenya County Health Analytics Platform

**ZENIK.AI · Amos Mwaura**

A multi-tab Streamlit dashboard for exploratory analysis of disease burden, epidemic trends, county-level comparison, and health system capacity across all **47 Kenyan counties** (2015–2024), with a downloadable PDF report.

---

## Live Demo

https://kenya-health-analytics-cwvysdra5syldcntwbnyry.streamlit.app/
---

## Overview

| Tab | What it shows |
|-----|---------------|
| 🗺️ **Disease Burden** | Bubble map + top-10 bar chart per disease; full 47-county indicator table |
| 📈 **Epidemic Trends** | National case counts 2015–2024, YoY change, county-level trend comparison |
| 🏥 **County Comparison** | Multi-disease radar chart, Malaria-vs-TB scatter, U5 mortality ranking |
| ⚕️ **Health System** | WHO-threshold gauges for beds/nurses/doctors, facility scatter, capacity heatmap |
| 📄 **Download Report** | One-click PDF export — cover, KPIs, disease rankings, trend charts, recommendations |

---

## Tech Stack

- **Streamlit** — multi-tab dashboard framework
- **Plotly** — interactive charts (scatter, bar, line, radar, heatmap, gauge)
- **ReportLab** — programmatic PDF generation (same brand as ZENIK.AI portfolio)
- **Pandas / NumPy** — data simulation and transformation

---

## Data

All figures are **synthetic but epidemiologically calibrated** to real Kenya Ministry of Health (MOH) and World Bank ranges:

- 47 counties, 6 diseases (Malaria, Cholera, TB, HIV, Dengue, Measles)
- 10-year time series with realistic trend factors (malaria declining, Dengue rising)
- County-level population, facility count, and workforce density
- Health outcome indicators: U5 mortality, maternal mortality, immunisation and ANC coverage

---

## Run Locally

```bash
git clone https://github.com/Mwauramos/kenya-health-analytics.git
cd kenya-health-analytics
pip install -r requirements.txt
streamlit run app.py
```

---

## Key Findings (2024)

- Kenya's average **bed density (≈ 1.8 / 1,000)** is below the WHO minimum of 2.5 — with arid counties (Turkana, Marsabit, Mandera) showing the widest gaps.
- **Malaria incidence** is highest in coastal and lakeshore counties (Kilifi, Homa Bay, Siaya) — consistent with ITN coverage gaps.
- **HIV prevalence** remains elevated in Nyanza counties despite ART scale-up.
- National **Malaria case counts** have declined ~35% from 2015–2024, while **Dengue** shows a gradual upward trend.

---

## Related Portfolio Projects

This platform is part of the [ZENIK.AI Healthcare AI Portfolio](https://mwauramos.github.io/zenik-ai):

- **Outbreak Surveillance Agent** — LangGraph multi-agent epidemic alerting system
- **Malaria-TB Dual Classifier** — XGBoost + SHAP clinical decision support
- **Kenya / Nigeria / South Africa Population Analysis** — Pan-African R analysis

---

## Author

**Amos Mwaura** — Machine Learning Engineer · Nairobi, Kenya  
[mwauramos.github.io/zenik-ai](https://mwauramos.github.io/zenik-ai) · [mwauramos.n@gmail.com](mailto:mwauramos.n@gmail.com)
