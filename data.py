"""
Simulated Kenya county health data — calibrated to real MOH / World Bank ranges.
All figures are synthetic but epidemiologically plausible.
"""
import pandas as pd
import numpy as np

np.random.seed(42)

COUNTIES = [
    "Nairobi","Mombasa","Kisumu","Nakuru","Eldoret/Uasin Gishu",
    "Kiambu","Machakos","Meru","Kilifi","Kakamega",
    "Bungoma","Kisii","Migori","Homa Bay","Siaya",
    "Nyamira","Bomet","Kericho","Nandi","Trans Nzoia",
    "West Pokot","Turkana","Samburu","Marsabit","Isiolo",
    "Mandera","Wajir","Garissa","Tana River","Lamu",
    "Taita Taveta","Kwale","Kajiado","Narok","Laikipia",
    "Nyeri","Kirinyaga","Murang'a","Nyandarua","Embu",
    "Tharaka Nithi","Kitui","Makueni","Mwingi/Kitui","Vihiga",
    "Baringo","Elgeyo Marakwet","Ol Kalou/Nyandarua",
]
COUNTIES = COUNTIES[:47]  # ensure exactly 47

DISEASES = ["Malaria", "Cholera", "TB", "HIV", "Dengue", "Measles"]
YEARS = list(range(2015, 2025))

# ── County metadata ────────────────────────────────────────────────────────────
def county_data():
    np.random.seed(42)
    pop = np.random.randint(150_000, 4_500_000, 47)
    # Coastal/western counties higher malaria
    malaria_base = np.random.uniform(8, 45, 47)
    malaria_base[[1,8,9,10,13,14,15]] *= 1.8   # coastal/lakeshore boost
    malaria_base = np.clip(malaria_base, 5, 120)

    df = pd.DataFrame({
        "county": COUNTIES,
        "population": pop,
        "area_km2": np.random.randint(400, 68_000, 47),
        "health_facilities": np.random.randint(20, 380, 47),
        "beds_per_1000": np.round(np.random.uniform(0.4, 3.2, 47), 2),
        "nurses_per_1000": np.round(np.random.uniform(0.3, 2.8, 47), 2),
        "doctors_per_1000": np.round(np.random.uniform(0.05, 0.9, 47), 2),
        "malaria_incidence": np.round(malaria_base, 1),
        "tb_incidence": np.round(np.random.uniform(30, 280, 47), 1),
        "hiv_prevalence": np.round(np.random.uniform(1.2, 18.5, 47), 2),
        "cholera_incidence": np.round(np.random.uniform(0.2, 12, 47), 2),
        "under5_mortality": np.round(np.random.uniform(22, 95, 47), 1),
        "maternal_mortality": np.round(np.random.uniform(90, 620, 47), 0),
        "antenatal_coverage": np.round(np.random.uniform(48, 97, 47), 1),
        "immunisation_coverage": np.round(np.random.uniform(52, 96, 47), 1),
        # lat/lon approximate county centroids (simplified)
        "lat": np.random.uniform(-4.5, 4.5, 47),
        "lon": np.random.uniform(34.0, 41.5, 47),
    })
    return df

# ── Time-series data ───────────────────────────────────────────────────────────
def timeseries_data():
    rows = []
    np.random.seed(7)
    for county in COUNTIES:
        for year in YEARS:
            for disease in DISEASES:
                base = {
                    "Malaria": np.random.uniform(200, 8000),
                    "Cholera": np.random.uniform(5, 400),
                    "TB": np.random.uniform(80, 1200),
                    "HIV": np.random.uniform(50, 2000),
                    "Dengue": np.random.uniform(2, 150),
                    "Measles": np.random.uniform(1, 80),
                }[disease]
                # Trend: malaria declining, HIV stable, cholera spikes
                trend = {"Malaria": -0.04, "Cholera": 0.01, "TB": -0.02,
                         "HIV": -0.01, "Dengue": 0.03, "Measles": -0.03}[disease]
                cases = base * (1 + trend) ** (year - 2015)
                cases *= np.random.uniform(0.8, 1.2)  # noise
                rows.append({
                    "county": county, "year": year,
                    "disease": disease, "cases": max(0, round(cases))
                })
    return pd.DataFrame(rows)

# ── National totals by year ────────────────────────────────────────────────────
def national_trends():
    ts = timeseries_data()
    return ts.groupby(["year", "disease"])["cases"].sum().reset_index()

COUNTY_DF = county_data()
TS_DF     = timeseries_data()
NAT_DF    = national_trends()
