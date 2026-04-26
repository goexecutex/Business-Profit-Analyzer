# ============================================================
#  GoExecuteX Insights — Universal Business Profit Analyzer
#  ─────────────────────────────────────────────────────────
#  Run:         streamlit run app.py
#  Large files: streamlit run app.py --server.maxUploadSize=1024
#  Install:     pip install streamlit pandas matplotlib openpyxl
# ============================================================

import json
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from difflib import get_close_matches

# ── Page Setup ────────────────────────────────────────────────
st.set_page_config(page_title="GoExecuteX Insights", page_icon="⚡", layout="wide", initial_sidebar_state="expanded") 


# ── Global CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background: #080c14; color: #e2e8f0; }
/* Hide menu and footer only — keep header so sidebar arrow stays visible */
#MainMenu, footer { 
    visibility: hidden; 
}

.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1a1040 50%, #0f172a 100%);
    border: 1px solid #2d2060; border-radius: 20px; padding: 2.5rem 3rem;
    margin-bottom: 2rem; position: relative; overflow: hidden;
}
.hero::before {
    content: ''; position: absolute; top: -40%; right: -5%;
    width: 450px; height: 450px;
    background: radial-gradient(circle, rgba(99,102,241,0.13) 0%, transparent 70%);
    pointer-events: none;
}
.hero .badge {
    display: inline-block; background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.3); color: #a5b4fc;
    font-size: .72rem; font-weight: 600; padding: .2rem .8rem;
    border-radius: 999px; margin-bottom: 1rem; letter-spacing: .08em; text-transform: uppercase;
}
.hero h1 { font-size: 2.4rem; font-weight: 700; color: #fff; margin: 0 0 .5rem; }
.hero h1 span { background: linear-gradient(90deg,#818cf8,#c084fc); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.hero p  { font-size: 1rem; color: #94a3b8; margin: 0; max-width: 580px; }

.sec {
    display: flex; align-items: center; gap: .6rem;
    font-size: 1.05rem; font-weight: 600; color: #e2e8f0;
    margin: 2.2rem 0 1rem; padding-bottom: .6rem; border-bottom: 1px solid #1e293b;
}
.sec .dot { width: 8px; height: 8px; background: #6366f1; border-radius: 50%; flex-shrink: 0; }

.kpi-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 1rem; margin-bottom: 1.5rem; }
.kpi {
    background: #0d1526; border: 1px solid #1e293b; border-radius: 16px;
    padding: 1.3rem 1.5rem;
}
.kpi .lbl { font-size: .68rem; text-transform: uppercase; letter-spacing: .1em; color: #64748b; margin-bottom: .5rem; }
.kpi .val { font-size: 1.85rem; font-weight: 700; color: #f8fafc; line-height: 1.1; }
.kpi .val.g { color: #22c55e; } .kpi .val.r { color: #ef4444; }
.kpi .val.y { color: #eab308; } .kpi .val.p { color: #a78bfa; }
.kpi .sub  { font-size: .75rem; color: #475569; margin-top: .4rem; }

.step-pill {
    display: inline-flex; align-items: center; gap: .5rem;
    background: rgba(99,102,241,.1); border: 1px solid rgba(99,102,241,.25);
    color: #a5b4fc; border-radius: 999px; padding: .3rem 1rem;
    font-size: .8rem; font-weight: 500; margin-bottom: 1rem;
}

.map-hint {
    background: #0d1526; border: 1px solid #1e293b; border-radius: 14px;
    padding: 1rem 1.5rem; margin-bottom: 1.2rem; color: #94a3b8; font-size: .88rem;
}
.map-hint strong { color: #a5b4fc; }

.pill-warn { background:#1c1008;border:1px solid #78350f;color:#fbbf24;border-radius:10px;padding:.8rem 1.2rem;font-size:.88rem;margin:.4rem 0; }
.pill-ok   { background:#052e16;border:1px solid #14532d;color:#4ade80;border-radius:10px;padding:.8rem 1.2rem;font-size:.88rem;margin:.4rem 0; }
.pill-info { background:#0c1a3a;border:1px solid #1e3a8a;color:#93c5fd;border-radius:10px;padding:.8rem 1.2rem;font-size:.88rem;margin:.4rem 0; }

.summary {
    background: linear-gradient(135deg, #0d1526, #1a1040);
    border: 1px solid #2d2060; border-radius: 16px;
    padding: 2rem 2.4rem; line-height: 1.9; color: #cbd5e1; font-size: .97rem;
}
.summary strong { color: #a5b4fc; }

hr.div { border: none; border-top: 1px solid #1e293b; margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  CONFIGURATION
# ════════════════════════════════════════════════════════════

BUSINESS_TYPES = {
    "🍽️ Restaurant / Cafe":  {"noun":"dish",    "emoji":"🍽️", "price_lbl":"Menu Price",     "cost_lbl":"Food Cost",      "qty_lbl":"Portions Sold"},
    "🛍️ Retail Store":       {"noun":"product", "emoji":"🛍️", "price_lbl":"Retail Price",    "cost_lbl":"Purchase Cost",  "qty_lbl":"Units Sold"},
    "🌐 E-commerce":          {"noun":"product", "emoji":"🌐", "price_lbl":"Sale Price",      "cost_lbl":"COGS",           "qty_lbl":"Orders"},
    "🔧 Service Business":    {"noun":"service", "emoji":"🔧", "price_lbl":"Billed Amount",   "cost_lbl":"Service Cost",   "qty_lbl":"Jobs Done"},
    "🏥 Healthcare / Clinic": {"noun":"service", "emoji":"🏥", "price_lbl":"Service Fee",     "cost_lbl":"Direct Cost",    "qty_lbl":"Patients Seen"},
    "📦 Wholesale / B2B":     {"noun":"product", "emoji":"📦", "price_lbl":"Wholesale Price", "cost_lbl":"Unit Cost",      "qty_lbl":"Units"},
    "📊 Custom / Other":      {"noun":"item",    "emoji":"📊", "price_lbl":"Selling Price",   "cost_lbl":"Cost Price",     "qty_lbl":"Quantity"},
}

# Known aliases for each required field (for auto-detection)
FIELD_ALIASES = {
    "item_name": [
        "item name","item","product name","product","service name","service",
        "dish","menu item","name","description","sku","article","category",
        "product title","listing","job type","treatment","procedure","title",
    ],
    "quantity": [
        "quantity","qty","units","units sold","quantity sold","qty sold","orders",
        "count","sold","volume","pieces","jobs","sessions","transactions",
        "portions","covers","patients","visits","invoices","no of units","num units",
    ],
    "selling_price": [
        "selling price","sale price","price","revenue","billed amount","rate","mrp",
        "unit price","sell price","selling","amount","charge","fee","tariff",
        "list price","service fee","wholesale price","unit selling price",
    ],
    "cost_price": [
        "cost price","cost","cogs","purchase price","buy price","expense",
        "unit cost","buying price","landed cost","food cost","ingredient cost",
        "direct cost","variable cost","cost of goods","cost of goods sold",
    ],
    "date": [
        "date","order date","sale date","transaction date","day","period",
        "invoice date","created at","created_at","timestamp","order_date",
        "sale_date","visit date","service date","purchase date",
    ],
}

FIELD_META = {
    "item_name":     ("Item / Product Name",  "The name of what you're selling"),
    "quantity":      ("Quantity Sold",         "How many units/portions were sold"),
    "selling_price": ("Selling Price",         "Price charged per unit"),
    "cost_price":    ("Cost Price",            "Your cost per unit"),
    "date":          ("Date",                  "Date of the sale / transaction"),
}


# ════════════════════════════════════════════════════════════
#  HELPERS
# ════════════════════════════════════════════════════════════

def auto_detect(columns: list[str]) -> dict:
    """Auto-map dataframe columns → internal field names using aliases + fuzzy match."""
    col_lower = {c.lower().strip(): c for c in columns}
    detected = {}
    for field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if alias in col_lower:
                detected[field] = col_lower[alias]
                break
        if field not in detected:
            match = get_close_matches(field.replace("_", " "), list(col_lower), n=1, cutoff=0.52)
            if match:
                detected[field] = col_lower[match[0]]
    return detected


def load_file(f) -> tuple[pd.DataFrame | None, str | None]:
    """Load CSV / Excel / JSON into a DataFrame. Returns (df, error_msg)."""
    name = f.name.lower()
    try:
        if name.endswith(".csv"):
            for enc in ["utf-8", "latin-1", "cp1252"]:
                try:
                    f.seek(0)
                    return pd.read_csv(f, encoding=enc, low_memory=False), None
                except UnicodeDecodeError:
                    continue
            return None, "Cannot decode CSV file — try saving it as UTF-8."
        elif name.endswith((".xlsx", ".xls")):
            return pd.read_excel(f), None
        elif name.endswith(".json"):
            data = json.load(f)
            if isinstance(data, list):
                return pd.DataFrame(data), None
            elif isinstance(data, dict):
                # Handle {key: [{...}]} or flat dict
                for v in data.values():
                    if isinstance(v, list):
                        return pd.DataFrame(v), None
                return pd.DataFrame([data]), None
            return None, "JSON must be an array of objects."
        return None, "Unsupported file type (use CSV, Excel, or JSON)."
    except Exception as e:
        return None, f"Read error: {e}"


def style_chart(fig, ax):
    """Apply dark premium chart theme."""
    BG = "#0d1526"
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    ax.tick_params(colors="#64748b", labelsize=9)
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_color("#94a3b8")
    ax.xaxis.label.set_color("#64748b"); ax.yaxis.label.set_color("#64748b")
    for s in ax.spines.values(): s.set_edgecolor("#1e293b")
    ax.grid(axis="both", color="#1e293b", linewidth=0.4, linestyle="--")
    ax.set_axisbelow(True)


def horiz_bar(ax, fig, data, x_col, y_col, color, fmt_str):
    bars = ax.barh(data[y_col], data[x_col], color=color, height=0.55, zorder=2)
    ax.bar_label(bars, fmt=fmt_str, padding=5, color="#94a3b8", fontsize=8)
    style_chart(fig, ax)


def make_summary(enriched: pd.DataFrame, btype: str) -> str:
    """Generate plain-English business summary with actionable advice."""
    cfg  = BUSINESS_TYPES[btype]
    noun = cfg["noun"]
    tr   = enriched["Revenue"].sum()
    tp   = enriched["Profit"].sum()
    mg   = (tp / tr * 100) if tr else 0
    top  = enriched.nlargest(1, "Profit").iloc[0]
    worst= enriched.nsmallest(1, "Profit Margin %").iloc[0]
    bsell= enriched.nlargest(1, "Quantity Sold").iloc[0]
    hl   = enriched[
        (enriched["Quantity Sold"] >= enriched["Quantity Sold"].quantile(0.6)) &
        (enriched["Profit Margin %"] < 20)
    ]

    mg_desc = (
        "strong — you're running a tight, profitable operation" if mg >= 35 else
        "moderate — solid but there's clear room to grow"       if mg >= 20 else
        "below average — this needs immediate attention"
    )

    lines = [
        f"Your business recorded <strong>{tr:,.0f}</strong> in total revenue with a net profit of "
        f"<strong>{tp:,.0f}</strong>. Your overall margin of <strong>{mg:.1f}%</strong> is {mg_desc}.",

        f"<strong>{top['Item Name']}</strong> is your highest-profit {noun} at "
        f"{top['Profit Margin %']:.1f}% margin. Make sure it's front-and-center — featured, promoted, "
        f"and recommended to every customer.",

        f"<strong>{bsell['Item Name']}</strong> leads in volume "
        f"({int(bsell['Quantity Sold'])} {cfg['qty_lbl'].lower()}). "
        + (f"With {bsell['Profit Margin %']:.1f}% margin, it's a genuine star — protect its cost structure."
           if bsell['Profit Margin %'] >= 25 else
           f"However, its {bsell['Profit Margin %']:.1f}% margin means it's not pulling its profitability weight "
           f"— reprice it or reduce unit cost before it grows into a bigger problem."),

        f"<strong>{worst['Item Name']}</strong> has the weakest margin at "
        f"{worst['Profit Margin %']:.1f}%. Raise its price, reduce material/ingredient cost, or phase it out entirely.",
    ]

    if not hl.empty:
        names = ", ".join(f"<strong>{r}</strong>" for r in hl["Item Name"].tolist()[:3])
        lines.append(
            f"⚠️ Hidden losers detected: {names}. These sell well but quietly drain your profit. "
            f"They feel like winners but they're not — reprice or renegotiate supplier costs urgently."
        )

    lines.append(
        f"<strong>Your action plan:</strong> "
        + ("Focus on cost reduction and repricing your bottom performers immediately. "
           "Even a 5% margin improvement on your top 5 items could meaningfully change monthly profit."
           if mg < 25 else
           "You're in a solid position. Double down on your highest-margin items, phase out the bottom 20%, "
           "and keep a weekly eye on hidden losers before they quietly erode what you've built.")
    )
    return "<br><br>".join(f"▸ {l}" for l in lines)


# ════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## ⚙️ Setup")

    btype = st.selectbox("Business Type", list(BUSINESS_TYPES.keys()), index=0)
    cfg   = BUSINESS_TYPES[btype]

    st.markdown("---")

    uploaded = st.file_uploader(
        "Upload Your Data",
        type=["csv", "xlsx", "xls", "json"],
        help="Supports CSV, Excel (.xlsx/.xls), and JSON. For files over 200 MB, run:\n"
             "streamlit run app.py --server.maxUploadSize=1024",
    )

    st.markdown("---")
    st.markdown("**📐 5 Required Fields**")
    for label, hint in [
        ("Item / Product Name", "What was sold"),
        ("Quantity",            "How many units"),
        ("Selling Price",       "Price charged"),
        ("Cost Price",          "Your cost per unit"),
        ("Date",                "Date of sale"),
    ]:
        st.markdown(
            f"**{label}**  \n<small style='color:#64748b'>{hint}</small>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    sample_csv = (
        "Item Name,Quantity Sold,Selling Price,Cost Price,Date\n"
        "Grilled Chicken,45,55,20,2024-01-01\nBeef Burger,38,48,22,2024-01-02\n"
        "Caesar Salad,20,35,10,2024-01-03\nMargherita Pizza,60,42,15,2024-01-04\n"
        "Lamb Chops,15,110,65,2024-01-05\nVeggie Wrap,28,30,12,2024-01-06\n"
        "Cheesecake,50,30,8,2024-01-07\nPasta Carbonara,33,45,18,2024-01-08\n"
        "Fish & Chips,22,52,28,2024-01-09\nMango Juice,80,18,5,2024-01-10\n"
    )
    st.download_button("⬇️ Download Sample CSV", sample_csv, "sample_data.csv", "text/csv")
    st.markdown(
        "<small style='color:#475569'>Your data never leaves your device.</small>",
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════
#  HERO BANNER
# ════════════════════════════════════════════════════════════

st.markdown("""
<div class="hero">
  <div class="badge">Universal Business Intelligence</div>
  <h1>⚡ GoExecuteX <span>Insights</span></h1>
  <p>Upload sales data in any format, map your columns in seconds, and get a full
  profit intelligence report — works for any type of business.</p>
</div>
""", unsafe_allow_html=True)

if not uploaded:
    c1, c2, c3 = st.columns(3)
    c1.info("**Step 1**  \nChoose your business type from the sidebar")
    c2.info("**Step 2**  \nUpload CSV, Excel, or JSON — any column names")
    c3.info("**Step 3**  \nMap your columns once → instant profit dashboard")
    st.stop()


# ════════════════════════════════════════════════════════════
#  LOAD FILE
# ════════════════════════════════════════════════════════════

df_raw, err = load_file(uploaded)
if err:
    st.error(f"❌ {err}")
    st.stop()

df_raw.columns = df_raw.columns.str.strip()

if df_raw.empty or df_raw.shape[1] < 2:
    st.error("❌ File appears to be empty or has fewer than 2 columns.")
    st.stop()


# ════════════════════════════════════════════════════════════
#  COLUMN MAPPING STEP
# ════════════════════════════════════════════════════════════

st.markdown('<div class="step-pill">📌 Step 1 of 2 — Map Your Columns</div>', unsafe_allow_html=True)
st.markdown('<div class="sec"><div class="dot"></div>Column Mapping</div>', unsafe_allow_html=True)

detected = auto_detect(df_raw.columns.tolist())
n_detected = len(detected)
confidence = "🟢 All 5 detected" if n_detected==5 else f"🟡 {n_detected}/5 auto-detected — review below" if n_detected>=3 else f"🔴 Only {n_detected}/5 detected — please map manually"

st.markdown(f"""
<div class="map-hint">
  Your file has <strong>{len(df_raw.columns)}</strong> columns and 
  <strong>{len(df_raw):,}</strong> rows. {confidence}.<br>
  <span style="color:#475569;font-size:.82rem;">
    Column names don't need to match exactly — select the right field from the dropdown for each.
  </span>
</div>
""", unsafe_allow_html=True)

opts = ["(skip / not in my data)"] + df_raw.columns.tolist()

mapping: dict[str, str | None] = {}
col_left, col_right = st.columns(2)
for i, (field, (label, hint)) in enumerate(FIELD_META.items()):
    col = col_left if i % 2 == 0 else col_right
    with col:
        default = detected.get(field, "(skip / not in my data)")
        idx = opts.index(default) if default in opts else 0
        chosen = st.selectbox(
            f"**{label}**",
            opts,
            index=idx,
            key=f"map_{field}",
            help=hint,
        )
        mapping[field] = chosen if chosen != "(skip / not in my data)" else None

missing = [FIELD_META[f][0] for f in FIELD_META if not mapping.get(f)]
if missing:
    st.warning(f"⚠️ Please map: **{', '.join(missing)}**")

if "analyze_clicked" not in st.session_state:
    st.session_state.analyze_clicked = False

if st.button("🚀 Confirm & Analyze", type="primary", disabled=bool(missing)):
    st.session_state.analyze_clicked = True

if not st.session_state.analyze_clicked:
    st.stop()


# ════════════════════════════════════════════════════════════
#  BUILD CLEAN DATAFRAME
# ════════════════════════════════════════════════════════════

rename_map = {
    mapping["item_name"]:     "Item Name",
    mapping["quantity"]:      "Quantity Sold",
    mapping["selling_price"]: "Selling Price",
    mapping["cost_price"]:    "Cost Price",
    mapping["date"]:          "Date",
}
df = df_raw.rename(columns=rename_map)[list(rename_map.values())].copy()

df["Date"]          = pd.to_datetime(df["Date"], dayfirst=False, errors="coerce")
df["Quantity Sold"] = pd.to_numeric(df["Quantity Sold"].astype(str).str.replace(",",""), errors="coerce")
df["Selling Price"] = pd.to_numeric(df["Selling Price"].astype(str).str.replace("[^0-9.]","",regex=True), errors="coerce")
df["Cost Price"]    = pd.to_numeric(df["Cost Price"].astype(str).str.replace("[^0-9.]","",regex=True), errors="coerce")

bad_count = df.isnull().any(axis=1).sum()
df.dropna(inplace=True)

if df.empty:
    st.error("❌ No valid rows after cleaning. Check your column mapping and data.")
    st.stop()

st.success(
    f"✅ Loaded **{len(df):,} valid rows** across "
    f"**{df['Item Name'].nunique()} unique items**"
    + (f" · {bad_count:,} rows skipped (invalid values)" if bad_count else "")
)


# ════════════════════════════════════════════════════════════
#  ENRICH — PER-ITEM AGGREGATION
# ════════════════════════════════════════════════════════════

enriched = (
    df.groupby("Item Name", as_index=False)
    .agg(
        **{"Quantity Sold":  ("Quantity Sold",  "sum"),
           "Selling Price":  ("Selling Price",  "mean"),
           "Cost Price":     ("Cost Price",     "mean")}
    )
)
enriched["Revenue"]         = enriched["Quantity Sold"] * enriched["Selling Price"]
enriched["Cost"]            = enriched["Quantity Sold"] * enriched["Cost Price"]
enriched["Profit"]          = enriched["Revenue"] - enriched["Cost"]
enriched["Profit Margin %"] = (enriched["Profit"] / enriched["Revenue"] * 100).round(1)


# ════════════════════════════════════════════════════════════
#  DASHBOARD
# ════════════════════════════════════════════════════════════

st.markdown('<hr class="div">', unsafe_allow_html=True)
st.markdown('<div class="step-pill">📊 Step 2 of 2 — Profit Dashboard</div>', unsafe_allow_html=True)

date_min  = df["Date"].min().strftime("%b %d, %Y")
date_max  = df["Date"].max().strftime("%b %d, %Y")
days_span = (df["Date"].max() - df["Date"].min()).days + 1

# ── KPI Cards ─────────────────────────────────────────────────
st.markdown('<div class="sec"><div class="dot"></div>Key Metrics</div>', unsafe_allow_html=True)

tr  = enriched["Revenue"].sum()
tp  = enriched["Profit"].sum()
mg  = (tp / tr * 100) if tr else 0
mgc = "g" if mg >= 30 else "y" if mg >= 15 else "r"

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi">
    <div class="lbl">Total Revenue</div>
    <div class="val p">{tr:,.0f}</div>
    <div class="sub">{date_min} → {date_max}</div>
  </div>
  <div class="kpi">
    <div class="lbl">Total Profit</div>
    <div class="val g">{tp:,.0f}</div>
    <div class="sub">{days_span} days of data</div>
  </div>
  <div class="kpi">
    <div class="lbl">Avg Profit Margin</div>
    <div class="val {mgc}">{mg:.1f}%</div>
    <div class="sub">{'Healthy ✓' if mg>=30 else 'Needs work ⚠️' if mg>=15 else 'Critical ❌'}</div>
  </div>
  <div class="kpi">
    <div class="lbl">Unique Items</div>
    <div class="val">{len(enriched)}</div>
    <div class="sub">{len(df):,} total transactions</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Raw Data Preview ──────────────────────────────────────────
with st.expander("🗂️ Raw Data Preview", expanded=False):
    preview = df.head(1000).reset_index(drop=True)
    st.dataframe(preview, use_container_width=True)
    if len(df) > 1000:
        st.caption(f"Showing first 1,000 of {len(df):,} rows. Full dataset is used for all calculations.")

# ── Profitability Table ───────────────────────────────────────
st.markdown('<hr class="div">', unsafe_allow_html=True)
st.markdown('<div class="sec"><div class="dot"></div>Item Profitability Breakdown</div>', unsafe_allow_html=True)

display_cols = ["Item Name","Quantity Sold","Selling Price","Cost Price","Revenue","Cost","Profit","Profit Margin %"]
table_h = min(500, 70 + 36 * len(enriched))

st.dataframe(
    enriched[display_cols]
    .sort_values("Profit", ascending=False)
    .reset_index(drop=True)
    .style
    .format({"Selling Price":"{:.2f}","Cost Price":"{:.2f}","Revenue":"{:,.0f}",
             "Cost":"{:,.0f}","Profit":"{:,.0f}","Profit Margin %":"{:.1f}%"})
    .background_gradient(subset=["Profit Margin %"], cmap="RdYlGn"),
    use_container_width=True,
    height=table_h,
)

# ── Charts ────────────────────────────────────────────────────
st.markdown('<hr class="div">', unsafe_allow_html=True)
st.markdown('<div class="sec"><div class="dot"></div>Performance Charts</div>', unsafe_allow_html=True)

PURPLE = "#6366f1"; GREEN = "#22c55e"; RED = "#ef4444"; YELLOW = "#eab308"

thresh = enriched["Quantity Sold"].quantile(0.6)
hidden = enriched[(enriched["Quantity Sold"] >= thresh) & (enriched["Profit Margin %"] < 20)].sort_values("Profit Margin %")

c1, c2 = st.columns(2)
with c1:
    st.markdown(f"**🏆 Top 5 Most Profitable**")
    t5 = enriched.nlargest(5, "Profit").sort_values("Profit")
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    horiz_bar(ax, fig, t5, "Profit", "Item Name", GREEN, "%.0f")
    ax.set_xlabel("Profit"); st.pyplot(fig, use_container_width=True); plt.close()

with c2:
    st.markdown("**📉 Lowest Profit Margins**")
    b5 = enriched.nsmallest(5, "Profit Margin %").sort_values("Profit Margin %")
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    horiz_bar(ax, fig, b5, "Profit Margin %", "Item Name", RED, "%.1f%%")
    ax.set_xlabel("Profit Margin %"); st.pyplot(fig, use_container_width=True); plt.close()

c3, c4 = st.columns(2)
with c3:
    st.markdown(f"**🛒 Best Sellers by {cfg['qty_lbl']}**")
    tq = enriched.nlargest(5, "Quantity Sold").sort_values("Quantity Sold")
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    horiz_bar(ax, fig, tq, "Quantity Sold", "Item Name", PURPLE, "%.0f")
    ax.set_xlabel(cfg["qty_lbl"]); st.pyplot(fig, use_container_width=True); plt.close()

with c4:
    st.markdown("**⚠️ High Volume, Low Margin (Hidden Losers)**")
    if hidden.empty:
        st.success("✅ No hidden losers — great margin discipline!")
    else:
        fig, ax = plt.subplots(figsize=(5.5, 3.5))
        horiz_bar(ax, fig, hidden, "Profit Margin %", "Item Name", YELLOW, "%.1f%%")
        ax.axvline(20, color=RED, linestyle="--", linewidth=1.2, label="20% threshold", zorder=3)
        ax.set_xlabel("Profit Margin %")
        ax.legend(fontsize=8, labelcolor="#94a3b8", facecolor="#0d1526", edgecolor="#1e293b")
        st.pyplot(fig, use_container_width=True); plt.close()

# ── Sales Trend ───────────────────────────────────────────────
st.markdown('<hr class="div">', unsafe_allow_html=True)
st.markdown('<div class="sec"><div class="dot"></div>Sales Trend</div>', unsafe_allow_html=True)

df["_rev"] = df["Quantity Sold"] * df["Selling Price"]
df["_pft"] = df["Quantity Sold"] * (df["Selling Price"] - df["Cost Price"])

view = st.radio("View by", ["Daily", "Weekly", "Monthly"], horizontal=True, label_visibility="collapsed", key="trend_view")
freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "MS"}
trend = (
    df.set_index("Date")
    .resample(freq_map[view])
    .agg(Revenue=("_rev","sum"), Profit=("_pft","sum"))
    .reset_index()
)
trend = trend[(trend["Revenue"] > 0) | (trend["Profit"] != 0)]  # remove empty periods

fig, ax = plt.subplots(figsize=(11, 4))
ax.fill_between(trend["Date"], trend["Revenue"], alpha=0.1, color=PURPLE)
ax.fill_between(trend["Date"], trend["Profit"],  alpha=0.1, color=GREEN)
ax.plot(trend["Date"], trend["Revenue"], color=PURPLE, linewidth=2.2, label="Revenue")
ax.plot(trend["Date"], trend["Profit"],  color=GREEN,  linewidth=2.2, label="Profit")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax.legend(fontsize=9, labelcolor="#94a3b8", facecolor="#0d1526", edgecolor="#1e293b")
style_chart(fig, ax)
plt.xticks(rotation=30, ha="right")
st.pyplot(fig, use_container_width=True); plt.close()

# ── Recommendations ───────────────────────────────────────────
st.markdown('<hr class="div">', unsafe_allow_html=True)
st.markdown('<div class="sec"><div class="dot"></div>Recommendations</div>', unsafe_allow_html=True)

any_rec = False
for _, row in enriched[enriched["Profit Margin %"] >= 40].nlargest(3, "Profit Margin %").iterrows():
    st.markdown(
        f'<div class="pill-ok">✅ <strong>Promote "{row["Item Name"]}"</strong> — '
        f'{row["Profit Margin %"]:.1f}% margin. Feature it prominently, train your team to upsell it.</div>',
        unsafe_allow_html=True,
    ); any_rec = True

for _, row in enriched[enriched["Profit Margin %"] < 15].nsmallest(3, "Profit Margin %").iterrows():
    st.markdown(
        f'<div class="pill-warn">⚠️ <strong>Fix or Remove "{row["Item Name"]}"</strong> — '
        f'only {row["Profit Margin %"]:.1f}% margin. Raise price, cut unit cost, or discontinue it.</div>',
        unsafe_allow_html=True,
    ); any_rec = True

for _, row in hidden.iterrows():
    st.markdown(
        f'<div class="pill-warn">🔍 <strong>Hidden Loser: "{row["Item Name"]}"</strong> — '
        f'{int(row["Quantity Sold"])} units sold but only {row["Profit Margin %"]:.1f}% margin. '
        f"Looks like a winner — it isn't. Fix it now.</div>",
        unsafe_allow_html=True,
    ); any_rec = True

if not any_rec:
    st.markdown('<div class="pill-info">ℹ️ Margins look balanced across your catalog. Review weekly to catch trends early.</div>', unsafe_allow_html=True)

# ── Business Summary ─────────────────────────────────────────
st.markdown('<hr class="div">', unsafe_allow_html=True)
st.markdown('<div class="sec"><div class="dot"></div>Business Summary</div>', unsafe_allow_html=True)

st.markdown(f'<div class="summary">{make_summary(enriched, btype)}</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.caption(
    f"GoExecuteX Insights · {cfg['emoji']} {btype.split(' ',1)[1]} · "
    f"Analyzed {len(df):,} rows · Data processed locally — never uploaded anywhere"
)
