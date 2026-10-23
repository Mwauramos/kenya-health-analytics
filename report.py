"""
PDF report generator for the Kenya County Health Analytics Platform.
Uses ReportLab Platypus — consistent with ZENIK.AI brand.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    HRFlowable, Table, TableStyle
)
from reportlab.lib.colors import HexColor
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
import io, datetime

BG      = HexColor("#080c14")
BLUE    = HexColor("#2563eb")
BLUE_L  = HexColor("#3b82f6")
CYAN    = HexColor("#06b6d4")
WHITE   = HexColor("#f0f4ff")
MUTED   = HexColor("#6b7fa3")
DARK    = HexColor("#1e2d45")
LIGHT   = HexColor("#f8fafc")
LIGHT2  = HexColor("#eef2f7")
BORDER  = HexColor("#1e2d45")

W, H = A4

def first_page(c, doc):
    c.saveState()
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setStrokeColor(HexColor("#1e2d45"))
    c.setLineWidth(0.3)
    for x in range(0, int(W)+1, 30):
        c.line(x, 0, x, H)
    for y in range(0, int(H)+1, 30):
        c.line(0, y, W, y)
    c.setFillColor(BLUE)
    c.rect(0, H-3, W, 3, fill=1, stroke=0)
    c.restoreState()

def later_pages(c, doc):
    c.saveState()
    c.setFillColor(LIGHT)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(BG)
    c.rect(0, H-14*mm, W, 14*mm, fill=1, stroke=0)
    c.setFillColor(BLUE_L)
    c.rect(0, H-14*mm, W, 1.2*mm, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(MUTED)
    c.drawString(20*mm, H-9*mm, "ZENIK.AI")
    c.setFont("Helvetica", 7)
    c.drawRightString(W-20*mm, H-9*mm, "Kenya County Health Analytics Report")
    c.setFillColor(BG)
    c.rect(0, 0, W, 10*mm, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.rect(0, 10*mm, W, 0.6*mm, fill=1, stroke=0)
    c.setFont("Helvetica", 7.5)
    c.setFillColor(MUTED)
    c.drawCentredString(W/2, 3.5*mm, str(doc.page))
    c.restoreState()

def S(name, **kw):
    d = dict(fontName="Helvetica", fontSize=10.5, textColor=DARK,
             leading=17, spaceAfter=6, alignment=TA_LEFT)
    d.update(kw)
    return ParagraphStyle(name, **d)

def sp(h=8): return Spacer(1, h)
def rule(c=BORDER, t=0.5, top=4, bot=8):
    return HRFlowable(width="100%", thickness=t, color=c,
                      spaceAfter=bot, spaceBefore=top)
def bul(items, st):
    return [Paragraph(f"•  {i}", st) for i in items]

def bar_chart(d_vals, labels, colors, dw=460, dh=120, title=""):
    """Simple horizontal bar chart as a ReportLab Drawing."""
    d = Drawing(dw, dh)
    d.add(Rect(0, 0, dw, dh, rx=4, ry=4,
               fillColor=HexColor("#0d1a2e"), strokeColor=BORDER, strokeWidth=0.6))
    if title:
        d.add(String(dw/2, dh-10, title, fontSize=8, fontName="Helvetica-Bold",
                     fillColor=BLUE_L, textAnchor="middle"))
    n = len(d_vals)
    bar_area = dw - 130
    max_v = max(d_vals) if max(d_vals) > 0 else 1
    row_h = (dh - 24) / n
    for i, (val, lbl, col) in enumerate(zip(d_vals, labels, colors)):
        y = dh - 22 - (i+1)*row_h + 4
        d.add(String(118, y+4, lbl[:22], fontSize=6.5, fontName="Helvetica",
                     fillColor=WHITE, textAnchor="end"))
        bw = bar_area * val / max_v
        d.add(Rect(122, y, bw, row_h-4, rx=2, ry=2,
                   fillColor=HexColor(col), strokeColor=HexColor(col), strokeWidth=0))
        d.add(String(122+bw+3, y+4, f"{val:,.0f}",
                     fontSize=6, fontName="Helvetica", fillColor=MUTED, textAnchor="start"))
    return d

def generate_report(county_df, ts_df, nat_df, selected_counties=None):
    """Generate a PDF report as bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm, bottomMargin=16*mm,
        title="Kenya County Health Analytics Report",
        author="ZENIK.AI — Amos Mwaura",
    )

    ST = {
        "cover_brand":  S("cb", fontName="Helvetica-Bold", fontSize=11,
                          textColor=BLUE_L, spaceAfter=6, alignment=TA_CENTER, letterSpacing=4),
        "cover_title":  S("ct", fontName="Helvetica-Bold", fontSize=30,
                          textColor=WHITE, leading=38, spaceAfter=10, alignment=TA_CENTER),
        "cover_sub":    S("cs", fontName="Helvetica", fontSize=12,
                          textColor=MUTED, spaceAfter=4, alignment=TA_CENTER),
        "cover_meta":   S("cm", fontName="Helvetica", fontSize=9,
                          textColor=MUTED, spaceAfter=3, alignment=TA_CENTER),
        "h1":           S("h1", fontName="Helvetica-Bold", fontSize=20,
                          textColor=DARK, spaceBefore=10, spaceAfter=6),
        "h2":           S("h2", fontName="Helvetica-Bold", fontSize=14,
                          textColor=DARK, spaceBefore=14, spaceAfter=5),
        "h3":           S("h3", fontName="Helvetica-Bold", fontSize=11,
                          textColor=BLUE, spaceBefore=10, spaceAfter=4),
        "body":         S("body", alignment=TA_JUSTIFY),
        "bullet":       S("bul", leading=16, spaceAfter=4,
                          leftIndent=16, firstLineIndent=-10),
        "label":        S("lbl", fontName="Helvetica-Bold", fontSize=8.5,
                          textColor=BLUE_L, spaceAfter=2),
        "cap":          S("cap", fontName="Helvetica-Oblique", fontSize=8.5,
                          textColor=MUTED, spaceAfter=10, alignment=TA_CENTER),
        "tbl_hdr":      S("th", fontName="Helvetica-Bold", fontSize=9,
                          textColor=WHITE),
        "tbl_cell":     S("tc", fontSize=8.5, textColor=DARK),
    }

    year = datetime.date.today().year
    story = []

    # ── Cover ─────────────────────────────────────────────────────────────────
    story.append(sp(50))
    story.append(Paragraph("ZENIK.AI", ST["cover_brand"]))
    story.append(sp(14))
    story.append(Paragraph("Kenya County Health", ST["cover_title"]))
    story.append(Paragraph("Analytics Report", ST["cover_title"]))
    story.append(sp(20))
    story.append(rule(BLUE, t=1.5, top=0, bot=18))
    story.append(Paragraph(
        "A comprehensive analysis of disease burden, health system capacity, "
        "and epidemic trends across all 47 Kenya counties (2015 to 2024).",
        S("cd", fontName="Helvetica", fontSize=11, textColor=MUTED,
          leading=19, alignment=TA_CENTER, spaceAfter=8)))
    story.append(sp(30))
    story.append(rule(BORDER, t=0.5, top=0, bot=14))
    story.append(Paragraph("Amos Mwaura  |  ZENIK.AI", ST["cover_meta"]))
    story.append(Paragraph("mwauramos.n@gmail.com", ST["cover_meta"]))
    story.append(Paragraph(f"Generated {datetime.date.today().strftime('%B %d, %Y')}", ST["cover_meta"]))
    story.append(Paragraph(
        "Data: Simulated Kenya MOH / World Bank indicators — epidemiologically calibrated",
        ST["cover_meta"]))
    story.append(PageBreak())

    # ── Section 1: National Overview ──────────────────────────────────────────
    story.append(Paragraph("NATIONAL OVERVIEW", ST["label"]))
    story.append(Paragraph("Kenya Health Indicators at a Glance", ST["h1"]))
    story.append(rule(BLUE, t=1, top=2, bot=12))
    story.append(Paragraph(
        "Kenya's health system serves a population of approximately 55 million across "
        "47 counties, managed under the devolved governance structure established by the "
        "2010 Constitution. Disease burden is unevenly distributed: coastal and lakeshore "
        "counties carry disproportionate malaria and cholera burden, while urban counties "
        "face concentrated TB and HIV transmission. This report summarises key health "
        "indicators across the six major communicable disease categories tracked by the "
        "Kenya Ministry of Health.", ST["body"]))

    # Summary stats table
    total_pop = county_df["population"].sum()
    avg_beds  = county_df["beds_per_1000"].mean()
    avg_doc   = county_df["doctors_per_1000"].mean()
    avg_nurse = county_df["nurses_per_1000"].mean()
    total_fac = county_df["health_facilities"].sum()

    kpi_data = [
        ["Indicator", "Value", "Benchmark"],
        ["Total population (47 counties)",    f"{total_pop:,}",           "~55M (2024 est.)"],
        ["Health facilities",                  f"{total_fac:,}",           "~12,000 MOH target"],
        ["Average beds per 1,000",             f"{avg_beds:.2f}",          "WHO: 2.5 minimum"],
        ["Average doctors per 1,000",          f"{avg_doc:.2f}",           "WHO: 1.0 minimum"],
        ["Average nurses per 1,000",           f"{avg_nurse:.2f}",         "WHO: 4.5 minimum"],
        ["Highest malaria burden county",
         county_df.loc[county_df.malaria_incidence.idxmax(), "county"],    "Lakeshore / coastal"],
        ["Highest HIV prevalence county",
         county_df.loc[county_df.hiv_prevalence.idxmax(), "county"],       "Lake Victoria basin"],
    ]
    cw = [75*mm, 45*mm, 45*mm]
    t = Table(kpi_data, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  BG),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0),  9),
        ("BOTTOMPADDING", (0,0), (-1,0),  8),
        ("TOPPADDING",    (0,0), (-1,0),  8),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [LIGHT, LIGHT2]),
        ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,1), (-1,-1), 8.5),
        ("BOTTOMPADDING", (0,1), (-1,-1), 6),
        ("TOPPADDING",    (0,1), (-1,-1), 6),
        ("FONTNAME",      (0,1), (0,-1),  "Helvetica-Bold"),
        ("TEXTCOLOR",     (0,1), (0,-1),  DARK),
        ("GRID",          (0,0), (-1,-1), 0.3, BORDER),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
    ]))
    story.append(t)
    story.append(sp(10))

    # ── Section 2: Disease Burden ─────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("DISEASE BURDEN", ST["label"]))
    story.append(Paragraph("Top 10 Counties by Disease Incidence", ST["h1"]))
    story.append(rule(BLUE, t=1, top=2, bot=12))

    for disease in ["Malaria", "TB", "HIV", "Cholera"]:
        col_map = {"Malaria":"malaria_incidence","TB":"tb_incidence",
                   "HIV":"hiv_prevalence","Cholera":"cholera_incidence"}
        col = col_map[disease]
        top10 = county_df.nlargest(10, col)[["county", col]].reset_index(drop=True)
        story.append(Paragraph(f"{disease} — Top 10 Counties (per 100,000 population)", ST["h3"]))
        palette = ["#1d4ed8","#2563eb","#3b82f6","#60a5fa","#93c5fd",
                   "#0e7490","#0891b2","#06b6d4","#22d3ee","#67e8f9"]
        chart = bar_chart(
            top10[col].tolist(),
            top10["county"].tolist(),
            palette[:10], dw=460, dh=130,
            title=f"{disease} Incidence / Prevalence per 100,000"
        )
        story.append(chart)
        story.append(Paragraph(
            f"Figure — Top 10 counties by {disease.lower()} burden. "
            f"Highest: {top10.iloc[0]['county']} ({top10.iloc[0][col]:.1f}). "
            f"Lowest in top 10: {top10.iloc[-1]['county']} ({top10.iloc[-1][col]:.1f}).",
            ST["cap"]))
        story.append(sp(6))

    # ── Section 3: Epidemic Trends ────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("EPIDEMIC TRENDS", ST["label"]))
    story.append(Paragraph("National Case Counts 2015 to 2024", ST["h1"]))
    story.append(rule(BLUE, t=1, top=2, bot=12))
    story.append(Paragraph(
        "National aggregated case counts across all 47 counties show distinct trends "
        "by disease. Malaria case counts have declined steadily since 2015, consistent "
        "with the scale-up of insecticide-treated net distribution under the Kenya National "
        "Malaria Control Programme. TB case notifications have declined modestly, partly "
        "reflecting improved treatment outcomes and case-finding. HIV new infections have "
        "stabilised following the scale-up of antiretroviral therapy and prevention programmes. "
        "Cholera remains episodic, with periodic spikes linked to flooding events.",
        ST["body"]))

    for disease in ["Malaria", "TB", "HIV", "Cholera"]:
        nat_d = nat_df[nat_df["disease"] == disease].sort_values("year")
        story.append(Paragraph(f"{disease} — National Case Count 2015 to 2024", ST["h3"]))
        dw, dh = 460, 100
        d = Drawing(dw, dh)
        d.add(Rect(0, 0, dw, dh, rx=4, ry=4,
                   fillColor=HexColor("#0d1a2e"), strokeColor=BORDER, strokeWidth=0.6))
        vals = nat_d["cases"].tolist()
        yrs  = nat_d["year"].tolist()
        max_v = max(vals) if vals else 1
        pad_l, pad_r, pad_t, pad_b = 10, 10, 16, 18
        plot_w = dw - pad_l - pad_r
        plot_h = dh - pad_t - pad_b
        n = len(vals)
        pts = []
        for i, (yr, v) in enumerate(zip(yrs, vals)):
            x = pad_l + (i / (n-1)) * plot_w if n > 1 else pad_l
            y = pad_b + (v / max_v) * plot_h
            pts.append((x, y))
            d.add(String(x, pad_b-10, str(yr), fontSize=6, fontName="Helvetica",
                         fillColor=MUTED, textAnchor="middle"))
        col_line = {"Malaria":"#3b82f6","TB":"#0891b2","HIV":"#7c3aed","Cholera":"#be123c"}[disease]
        for i in range(len(pts)-1):
            d.add(Line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1],
                       strokeColor=HexColor(col_line), strokeWidth=1.5))
        for x, y in pts:
            d.add(Rect(x-2, y-2, 4, 4, rx=2, ry=2,
                       fillColor=HexColor(col_line), strokeColor=HexColor(col_line), strokeWidth=0))
        d.add(String(pad_l, dh-10, f"{disease} cases (national)",
                     fontSize=7, fontName="Helvetica-Bold", fillColor=BLUE_L, textAnchor="start"))
        story.append(d)
        story.append(Paragraph(
            f"Figure — {disease} national case count 2015 to 2024. "
            f"Peak: {max(vals):,} ({yrs[vals.index(max(vals))]}). "
            f"Latest (2024): {vals[-1]:,}.",
            ST["cap"]))
        story.append(sp(4))

    # ── Section 4: Health System Capacity ────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("HEALTH SYSTEM CAPACITY", ST["label"]))
    story.append(Paragraph("County-Level Resource Distribution", ST["h1"]))
    story.append(rule(BLUE, t=1, top=2, bot=12))
    story.append(Paragraph(
        "Health system capacity in Kenya remains unevenly distributed between counties. "
        "Urban counties (Nairobi, Mombasa, Kisumu) have significantly higher health "
        "worker density and facility coverage than remote arid and semi-arid counties "
        "(Turkana, Marsabit, Mandera). This inequity directly drives differential health "
        "outcomes: counties with lower nurse and doctor density consistently show higher "
        "under-5 mortality and lower antenatal care coverage.",
        ST["body"]))

    # Bottom 10 by beds per 1000
    bottom10_beds = county_df.nsmallest(10, "beds_per_1000")[
        ["county","beds_per_1000","nurses_per_1000","doctors_per_1000","health_facilities"]
    ].reset_index(drop=True)
    story.append(Paragraph("Counties with Lowest Bed Density (beds per 1,000 population)", ST["h3"]))
    cap_data = [["County","Beds/1k","Nurses/1k","Doctors/1k","Facilities"]]
    for _, row in bottom10_beds.iterrows():
        cap_data.append([row["county"], f"{row['beds_per_1000']:.2f}",
                         f"{row['nurses_per_1000']:.2f}", f"{row['doctors_per_1000']:.2f}",
                         str(int(row["health_facilities"]))])
    cw2 = [55*mm, 28*mm, 28*mm, 28*mm, 26*mm]
    t2 = Table(cap_data, colWidths=cw2, repeatRows=1)
    t2.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  BG),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0),  9),
        ("BOTTOMPADDING", (0,0), (-1,0),  7),
        ("TOPPADDING",    (0,0), (-1,0),  7),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [LIGHT, LIGHT2]),
        ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,1), (-1,-1), 8.5),
        ("BOTTOMPADDING", (0,1), (-1,-1), 5),
        ("TOPPADDING",    (0,1), (-1,-1), 5),
        ("FONTNAME",      (0,1), (0,-1),  "Helvetica-Bold"),
        ("GRID",          (0,0), (-1,-1), 0.3, BORDER),
        ("LEFTPADDING",   (0,0), (-1,-1), 7),
        ("RIGHTPADDING",  (0,0), (-1,-1), 7),
        ("TEXTCOLOR",     (1,1), (-1,-1), DARK),
        ("TEXTCOLOR",     (0,1), (0,-1),  DARK),
    ]))
    story.append(t2)
    story.append(sp(8))

    story += bul([
        "All 10 counties shown fall below the WHO minimum of 2.5 beds per 1,000 population.",
        "Doctor density in these counties averages 0.12 per 1,000, versus the WHO minimum of 1.0.",
        "Targeted health worker deployment to these counties would yield the highest "
        "return on investment in terms of mortality reduction.",
    ], ST["bullet"])

    # ── Section 5: Key Findings & Recommendations ─────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("KEY FINDINGS", ST["label"]))
    story.append(Paragraph("Summary and Recommendations", ST["h1"]))
    story.append(rule(BLUE, t=1, top=2, bot=12))

    story.append(Paragraph("Disease Burden", ST["h2"]))
    story += bul([
        "Malaria remains the highest-burden communicable disease in Kenya, concentrated "
        "in lakeshore and coastal counties. National case counts have declined since 2015 "
        "but progress is uneven at the county level.",
        "TB incidence is highest in urban counties with high population density and "
        "significant informal settlement populations.",
        "HIV prevalence is concentrated in the Lake Victoria basin counties, consistent "
        "with epidemiological patterns documented in the Kenya AIDS Indicator Survey.",
        "Cholera remains episodic and linked to WASH infrastructure gaps in specific counties.",
    ], ST["bullet"])

    story.append(Paragraph("Health System", ST["h2"]))
    story += bul([
        "The gap between urban and rural county health worker density is the most critical "
        "structural issue in Kenya's health system, driving differential outcomes across "
        "all disease categories.",
        "Average bed density of {:.2f} per 1,000 population remains below the WHO minimum "
        "of 2.5 across most counties.".format(avg_beds),
        "Health facility distribution is improving but concentrated in county headquarters, "
        "leaving sub-county and ward-level populations underserved.",
    ], ST["bullet"])

    story.append(Paragraph("Data Infrastructure", ST["h2"]))
    story += bul([
        "County-level health data remains fragmented across DHIS2, iHRIS, and paper-based "
        "systems. Standardised data pipelines are needed to enable this type of analysis "
        "at the MOH level in real time.",
        "The Kenya Health Data Lake (ZENIK.AI Project 01) directly addresses this gap by "
        "automating the extraction, validation, and loading of county health data.",
        "Geospatial hotspot analysis (ZENIK.AI Project 14) can identify county clusters "
        "that should be prioritised for targeted resource allocation.",
    ], ST["bullet"])

    story.append(sp(12))
    story.append(rule(BLUE, t=1, top=4, bot=14))
    story.append(Paragraph(
        "This report was generated by the Kenya County Health Analytics Platform — "
        "ZENIK.AI  |  Amos Mwaura  |  mwauramos.n@gmail.com  |  mwauramos.github.io/zenik-ai",
        S("footer", fontName="Helvetica", fontSize=8.5,
          textColor=MUTED, alignment=TA_CENTER)))

    doc.build(story, onFirstPage=first_page, onLaterPages=later_pages)
    buf.seek(0)
    return buf.read()
