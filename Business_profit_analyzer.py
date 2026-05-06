import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime, timedelta

st.set_page_config(
    page_title="GoExecuteX Insights",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Dark theme base */
    .stApp { background-color: #0e1117; }
    section[data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    
    /* Hero banner */
    .hero-banner {
        background: linear-gradient(135deg, #1a1f3c 0%, #0d1117 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
    }
    .hero-tag {
        display: inline-block;
        background: rgba(88,101,242,0.2);
        color: #7c8aff;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        padding: 4px 12px;
        border-radius: 20px;
        border: 1px solid rgba(88,101,242,0.3);
        margin-bottom: 1rem;
    }
    .hero-title { font-size: 2.4rem; font-weight: 700; color: #c9d1d9; margin: 0.3rem 0; }
    .hero-title span { color: #7c8aff; }
    .hero-sub { color: #8b949e; font-size: 1rem; margin-top: 0.5rem; }

    /* Step badge */
    .step-badge {
        display: inline-block;
        background: rgba(88,101,242,0.15);
        color: #7c8aff;
        border: 1px solid rgba(88,101,242,0.3);
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }

    /* Metric cards */
    .metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 2rem; }
    .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
    }
    .metric-label { font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
    .metric-value { font-size: 2rem; font-weight: 700; margin: 6px 0 4px; }
    .metric-value.revenue { color: #7c8aff; }
    .metric-value.profit { color: #3fb950; }
    .metric-value.margin { color: #3fb950; }
    .metric-value.items { color: #c9d1d9; }
    .metric-sub { font-size: 12px; color: #8b949e; }

    /* Section headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1rem;
        font-weight: 600;
        color: #c9d1d9;
        margin: 2rem 0 1rem;
        padding-bottom: 8px;
        border-bottom: 1px solid #21262d;
    }
    .section-dot { width: 8px; height: 8px; border-radius: 50%; background: #7c8aff; display: inline-block; }

    /* Recommendation cards */
    .rec-card {
        background: rgba(35, 134, 54, 0.15);
        border: 1px solid rgba(35, 134, 54, 0.3);
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 10px;
        color: #3fb950;
        font-size: 14px;
    }
    .rec-card.warning {
        background: rgba(187, 128, 9, 0.15);
        border-color: rgba(187, 128, 9, 0.3);
        color: #d29922;
    }
    .rec-card.danger {
        background: rgba(248, 81, 73, 0.15);
        border-color: rgba(248, 81, 73, 0.3);
        color: #f85149;
    }

    /* Summary box */
    .summary-box {
        background: linear-gradient(135deg, #1a1f3c 0%, #161b22 100%);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 1.5rem 2rem;
        margin-top: 1rem;
    }
    .summary-box p { color: #c9d1d9; font-size: 14px; line-height: 1.8; margin-bottom: 12px; }
    .summary-box p:last-child { margin-bottom: 0; }
    .hl-purple { color: #7c8aff; font-weight: 600; }
    .hl-green { color: #3fb950; font-weight: 600; }
    .hl-red { color: #f85149; font-weight: 600; }

    /* Footer */
    .footer {
        text-align: center;
        color: #484f58;
        font-size: 12px;
        padding: 2rem 0 1rem;
        border-top: 1px solid #21262d;
        margin-top: 3rem;
    }

    /* Hide streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    div[data-testid="stToolbar"] {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────

BUSINESS_TYPES = [
    "🍽️ Restaurant / Cafe",
    "🛍️ Retail Store",
    "🌐 E-commerce",
    "🔧 Service Business",
    "🏥 Healthcare / Clinic",
    "📦 Wholesale / B2B",
    "🗂️ Custom / Other",
]

CURRENCIES = {
    "USD ($)": "$",
    "EUR (€)": "€",
    "GBP (£)": "£",
    "AED (د.إ)": "AED ",
    "SAR (﷼)": "SAR ",
    "INR (₹)": "₹",
    "JPY (¥)": "¥",
    "CNY (¥)": "¥",
}

FIELD_NAMES = {
    "item": "Item / Product Name",
    "qty": "Quantity Sold",
    "sell": "Selling Price",
    "cost": "Cost Price",
    "date": "Date",
}

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#161b22",
    font_color="#c9d1d9",
    font_family="sans-serif",
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(gridcolor="#21262d", zerolinecolor="#30363d"),
    yaxis=dict(gridcolor="#21262d", zerolinecolor="#30363d"),
)

# ─── Helpers ──────────────────────────────────────────────────────────────────

def fmt(val, currency_sym="$", decimals=0):
    """Format number with currency symbol."""
    if decimals == 0:
        return f"{currency_sym}{val:,.0f}"
    return f"{currency_sym}{val:,.{decimals}f}"

def generate_sample_csv(business_type):
    """Generate sample CSV data based on business type."""
    np.random.seed(42)
    days = pd.date_range(start="2026-01-01", periods=90, freq="D")

    menus = {
        "🍽️ Restaurant / Cafe": [
            ("Margherita Pizza", 36, 15), ("Chicken Pasta", 34, 14),
            ("Mojito", 18, 6), ("Chicken Burger", 28, 11),
            ("Chocolate Cake", 24, 9), ("French Fries", 12, 4),
            ("Steak Sandwich", 42, 31), ("Caesar Salad", 26, 18),
        ],
        "🛍️ Retail Store": [
            ("Wireless Headphones", 79, 35), ("Phone Case", 19, 4),
            ("Laptop Stand", 45, 18), ("USB Hub", 29, 12),
            ("Screen Cleaner", 12, 3), ("Keyboard", 65, 28),
        ],
        "🌐 E-commerce": [
            ("T-Shirt", 29, 8), ("Sneakers", 89, 40), ("Cap", 22, 7),
            ("Hoodie", 59, 22), ("Socks Bundle", 15, 4),
        ],
        "🔧 Service Business": [
            ("Consultation", 150, 20), ("Installation", 200, 60),
            ("Repair Service", 120, 40), ("Maintenance", 90, 25),
        ],
        "🏥 Healthcare / Clinic": [
            ("General Checkup", 100, 30), ("Blood Test", 60, 20),
            ("X-Ray", 150, 55), ("Dental Cleaning", 120, 35),
        ],
        "📦 Wholesale / B2B": [
            ("Product Box A", 45, 22), ("Product Box B", 60, 28),
            ("Bulk Pack C", 120, 65), ("Bundle D", 200, 110),
        ],
        "🗂️ Custom / Other": [
            ("Item A", 50, 20), ("Item B", 80, 35),
            ("Item C", 30, 12), ("Item D", 100, 45),
        ],
    }

    items = menus.get(business_type, menus["🗂️ Custom / Other"])
    rows = []
    for day in days:
        n = np.random.randint(1, 4)
        for _ in range(n):
            item = items[np.random.randint(len(items))]
            qty = np.random.randint(1, 15)
            rows.append({
                "Item Name": item[0],
                "Quantity Sold": qty,
                "Selling Price": item[1],
                "Cost Price": item[2],
                "Date": day.strftime("%Y-%m-%d"),
            })
    return pd.DataFrame(rows)

def compute_metrics(df, item_col, qty_col, sell_col, cost_col):
    """Compute all analytics from mapped dataframe."""
    df = df.copy()
    df["_qty"] = pd.to_numeric(df[qty_col], errors="coerce").fillna(0)
    df["_sell"] = pd.to_numeric(df[sell_col], errors="coerce").fillna(0)
    df["_cost"] = pd.to_numeric(df[cost_col], errors="coerce").fillna(0)
    df["_revenue"] = df["_qty"] * df["_sell"]
    df["_cost_total"] = df["_qty"] * df["_cost"]
    df["_profit"] = df["_revenue"] - df["_cost_total"]
    df["_margin"] = ((df["_sell"] - df["_cost"]) / df["_sell"] * 100).where(df["_sell"] > 0, 0)

    summary = df.groupby(df[item_col]).agg(
        qty=("_qty", "sum"),
        revenue=("_revenue", "sum"),
        cost_total=("_cost_total", "sum"),
        profit=("_profit", "sum"),
        sell_price=("_sell", "mean"),
        cost_price=("_cost", "mean"),
    ).reset_index()
    summary.rename(columns={item_col: "Item Name"}, inplace=True)
    summary["Profit Margin %"] = ((summary["sell_price"] - summary["cost_price"]) / summary["sell_price"] * 100).round(1)
    summary["Profit Margin %"] = summary["Profit Margin %"].clip(lower=0)
    return df, summary

# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Setup")
    st.markdown("---")

    business_type = st.selectbox("Business Type", BUSINESS_TYPES)

    if business_type == "🗂️ Custom / Other":
        custom_label = st.text_input("Custom business label", placeholder="e.g. Photography Studio")
        display_type = custom_label if custom_label else "Custom / Other"
    else:
        display_type = business_type

    currency_choice = st.selectbox("Currency", list(CURRENCIES.keys()), index=0)
    currency_sym = CURRENCIES[currency_choice]

    st.markdown("---")
    uploaded_file = st.file_uploader(
        "Upload Your Data",
        type=["csv", "xlsx", "xls"],
        help="Upload a CSV or Excel file with your sales data",
    )

    st.markdown("---")
    st.markdown("**5 Required Fields**")
    for label, desc in [
        ("Item / Product Name", "What was sold"),
        ("Quantity", "How many units"),
        ("Selling Price", "Price charged"),
        ("Cost Price", "Your cost per unit"),
        ("Date", "Date of sale"),
    ]:
        st.markdown(f"**{label}**")
        st.caption(desc)

    st.markdown("---")
    sample_df = generate_sample_csv(business_type)
    csv_bytes = sample_df.to_csv(index=False).encode()
    st.download_button(
        "⬇️ Download Sample CSV",
        data=csv_bytes,
        file_name="sample_data.csv",
        mime="text/csv",
        use_container_width=True,
    )

# ─── Hero Banner ──────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-banner">
    <div class="hero-tag">UNIVERSAL BUSINESS INTELLIGENCE</div>
    <div class="hero-title">⚡ <span>GoExecuteX</span> Insights</div>
    <div class="hero-sub">Upload sales data in any format, map your columns in seconds, and get a full profit intelligence report — works for any type of business.</div>
</div>
""", unsafe_allow_html=True)

# ─── No file uploaded ─────────────────────────────────────────────────────────

if uploaded_file is None:
    st.markdown('<div class="step-badge">🚀 Step 1 of 2 — Upload Your Data</div>', unsafe_allow_html=True)
    st.info("👈 Upload a CSV or Excel file from the sidebar to get started. Download the sample CSV to see the expected format.")
    st.stop()

# ─── Load file ────────────────────────────────────────────────────────────────

try:
    if uploaded_file.name.endswith(".csv"):
        raw_df = pd.read_csv(uploaded_file)
    else:
        raw_df = pd.read_excel(uploaded_file)
    raw_df.columns = raw_df.columns.str.strip()
except Exception as e:
    st.error(f"Could not read file: {e}")
    st.stop()

cols = list(raw_df.columns)

# ─── Step 1: Column Mapping ───────────────────────────────────────────────────

def auto_match(columns, keywords):
    for col in columns:
        cl = col.lower()
        if any(k in cl for k in keywords):
            return col
    return columns[0]

if "mapping_confirmed" not in st.session_state:
    st.session_state.mapping_confirmed = False

st.markdown('<div class="step-badge">🚀 Step 1 of 2 — Map Your Columns</div>', unsafe_allow_html=True)

detected = sum([
    any(k in c.lower() for c in cols for k in ["item", "name", "product"]),
    any(k in c.lower() for c in cols for k in ["qty", "quantity", "units", "sold"]),
    any(k in c.lower() for c in cols for k in ["sell", "selling", "price", "revenue"]),
    any(k in c.lower() for c in cols for k in ["cost"]),
    any(k in c.lower() for c in cols for k in ["date", "day", "time"]),
])

st.markdown(f"""
<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:14px 18px;margin-bottom:1.5rem;">
    Your file has <strong>{len(cols)}</strong> columns and <strong>{len(raw_df)}</strong> rows.
    {"🟢 " + str(detected) + " of 5 detected." if detected == 5 else "⚠️ Not all fields auto-detected — please map manually."}
    <br><small style="color:#8b949e;">Column names don't need to match exactly — select the right field from the dropdown for each.</small>
</div>
""", unsafe_allow_html=True)

with st.form("mapping_form"):
    col1, col2 = st.columns(2)
    with col1:
        item_col = st.selectbox(
            "Item / Product Name",
            cols,
            index=cols.index(auto_match(cols, ["item", "name", "product", "dish", "service"])),
        )
        sell_col = st.selectbox(
            "Selling Price",
            cols,
            index=cols.index(auto_match(cols, ["sell", "selling", "price", "revenue", "amount"])),
        )
        date_col = st.selectbox(
            "Date",
            cols,
            index=cols.index(auto_match(cols, ["date", "day", "time", "period"])),
        )
    with col2:
        qty_col = st.selectbox(
            "Quantity Sold",
            cols,
            index=cols.index(auto_match(cols, ["qty", "quantity", "units", "sold", "count"])),
        )
        cost_col = st.selectbox(
            "Cost Price",
            cols,
            index=cols.index(auto_match(cols, ["cost", "cogs", "expense", "purchase"])),
        )

    submitted = st.form_submit_button("🚀 Confirm & Analyze", use_container_width=False, type="primary")
    if submitted:
        st.session_state.mapping_confirmed = True
        st.session_state.mapping = {
            "item": item_col, "qty": qty_col,
            "sell": sell_col, "cost": cost_col, "date": date_col,
        }

if not st.session_state.mapping_confirmed:
    st.stop()

# ─── Step 2: Profit Dashboard ─────────────────────────────────────────────────

m = st.session_state.mapping
item_col = m["item"]
qty_col = m["qty"]
sell_col = m["sell"]
cost_col = m["cost"]
date_col = m["date"]

df, summary = compute_metrics(raw_df, item_col, qty_col, sell_col, cost_col)

# Parse dates
df["_date"] = pd.to_datetime(df[date_col], errors="coerce")
valid_dates = df["_date"].dropna()

st.markdown('<div class="step-badge">📊 Step 2 of 2 — Profit Dashboard</div>', unsafe_allow_html=True)

# ── Date range filter ─────────────────────────────────────────────────────────
if not valid_dates.empty:
    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()
    with st.expander("📅 Filter by Date Range", expanded=False):
        d1, d2 = st.date_input(
            "Select range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
    mask = (df["_date"].dt.date >= d1) & (df["_date"].dt.date <= d2)
    df_filtered = df[mask]
    _, summary = compute_metrics(df_filtered, item_col, qty_col, sell_col, cost_col)
    date_range_str = f"{d1.strftime('%b %d, %Y')} → {d2.strftime('%b %d, %Y')}"
    days_count = (d2 - d1).days + 1
else:
    df_filtered = df
    date_range_str = "All time"
    days_count = len(df)

# ── Key Metrics ───────────────────────────────────────────────────────────────
total_rev = df_filtered["_revenue"].sum()
total_profit = df_filtered["_profit"].sum()
avg_margin = (total_profit / total_rev * 100) if total_rev > 0 else 0
unique_items = df_filtered[item_col].nunique()
total_tx = len(df_filtered)
margin_label = "Healthy ✓" if avg_margin >= 40 else ("Fair ~" if avg_margin >= 20 else "Low ⚠")

st.markdown(f"""
<div class="metric-grid">
    <div class="metric-card">
        <div class="metric-label">Total Revenue</div>
        <div class="metric-value revenue">{fmt(total_rev, currency_sym)}</div>
        <div class="metric-sub">{date_range_str}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Total Profit</div>
        <div class="metric-value profit">{fmt(total_profit, currency_sym)}</div>
        <div class="metric-sub">{days_count} days of data</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Avg Profit Margin</div>
        <div class="metric-value margin">{avg_margin:.1f}%</div>
        <div class="metric-sub">{margin_label}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Unique Items</div>
        <div class="metric-value items">{unique_items}</div>
        <div class="metric-sub">{total_tx:,} total transactions</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Raw Data Preview ──────────────────────────────────────────────────────────
with st.expander("📋 Raw Data Preview"):
    st.dataframe(df_filtered[[item_col, qty_col, sell_col, cost_col, date_col]].head(50), use_container_width=True)

# ── Item Profitability Breakdown ──────────────────────────────────────────────
st.markdown('<div class="section-header"><span class="section-dot"></span> Item Profitability Breakdown</div>', unsafe_allow_html=True)

display_summary = summary.copy()
display_summary.columns = ["Item Name", "Qty Sold", "Revenue", "Cost", "Profit", "Avg Sell Price", "Avg Cost Price", "Profit Margin %"]
display_summary["Revenue"] = display_summary["Revenue"].apply(lambda x: fmt(x, currency_sym))
display_summary["Cost"] = display_summary["Cost"].apply(lambda x: fmt(x, currency_sym))
display_summary["Profit"] = display_summary["Profit"].apply(lambda x: fmt(x, currency_sym))
display_summary["Avg Sell Price"] = display_summary["Avg Sell Price"].apply(lambda x: fmt(x, currency_sym, 2))
display_summary["Avg Cost Price"] = display_summary["Avg Cost Price"].apply(lambda x: fmt(x, currency_sym, 2))
display_summary["Qty Sold"] = display_summary["Qty Sold"].apply(lambda x: f"{x:,.0f}")
display_summary["Profit Margin %"] = display_summary["Profit Margin %"].apply(lambda x: f"{x:.1f}%")

st.dataframe(
    display_summary[["Item Name", "Qty Sold", "Avg Sell Price", "Avg Cost Price", "Revenue", "Cost", "Profit", "Profit Margin %"]],
    use_container_width=True,
    hide_index=True,
)

# ── Export ────────────────────────────────────────────────────────────────────
col_exp1, col_exp2 = st.columns([1, 5])
with col_exp1:
    export_df = summary.copy()
    export_df.columns = ["Item Name", "Qty Sold", "Revenue", "Cost", "Profit", "Avg Sell Price", "Avg Cost Price", "Profit Margin %"]
    csv_export = export_df.to_csv(index=False).encode()
    st.download_button("⬇️ Export Report CSV", data=csv_export, file_name="profit_report.csv", mime="text/csv")

# ── Performance Charts ────────────────────────────────────────────────────────
st.markdown('<div class="section-header"><span class="section-dot"></span> Performance Charts</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)

# BUG FIX 1: Top 5 Most Profitable — sorted by total profit descending
with c1:
    top5 = summary.nlargest(5, "profit")
    fig1 = go.Figure(go.Bar(
        x=top5["profit"],
        y=top5["Item Name"],
        orientation="h",
        marker_color="#3fb950",
        text=top5["profit"].apply(lambda x: fmt(x, currency_sym)),
        textposition="outside",
        hovertemplate="%{y}: %{x:,.0f}<extra></extra>",
    ))
    fig1.update_layout(title="🏆 Top 5 Most Profitable", **PLOT_LAYOUT, height=300,
                       yaxis=dict(autorange="reversed", gridcolor="#21262d"),
                       xaxis=dict(title="Profit", gridcolor="#21262d"))
    st.plotly_chart(fig1, use_container_width=True)

# BUG FIX 2: Lowest Profit Margins — sorted ASCENDING (lowest first = worst performers)
with c2:
    bottom5 = summary.nsmallest(5, "Profit Margin %")
    fig2 = go.Figure(go.Bar(
        x=bottom5["Profit Margin %"],
        y=bottom5["Item Name"],
        orientation="h",
        marker_color="#f85149",
        text=bottom5["Profit Margin %"].apply(lambda x: f"{x:.1f}%"),
        textposition="outside",
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
    ))
    fig2.update_layout(title="📉 Lowest Profit Margins (worst first)", **PLOT_LAYOUT, height=300,
                       yaxis=dict(autorange="reversed", gridcolor="#21262d"),
                       xaxis=dict(title="Profit Margin %", gridcolor="#21262d"))
    st.plotly_chart(fig2, use_container_width=True)

c3, c4 = st.columns(2)

# Best Sellers by Volume
with c3:
    top_vol = summary.nlargest(5, "qty")
    fig3 = go.Figure(go.Bar(
        x=top_vol["qty"],
        y=top_vol["Item Name"],
        orientation="h",
        marker_color="#7c8aff",
        text=top_vol["qty"].apply(lambda x: f"{x:,.0f}"),
        textposition="outside",
        hovertemplate="%{y}: %{x:,.0f} units<extra></extra>",
    ))
    fig3.update_layout(title="🛒 Best Sellers by Volume", **PLOT_LAYOUT, height=300,
                       yaxis=dict(autorange="reversed", gridcolor="#21262d"),
                       xaxis=dict(title="Units Sold", gridcolor="#21262d"))
    st.plotly_chart(fig3, use_container_width=True)

# BUG FIX 3: Hidden Losers — High volume AND low margin (both conditions must be met)
# Threshold: volume > median volume AND margin < median margin
with c4:
    vol_median = summary["qty"].median()
    margin_median = summary["Profit Margin %"].median()
    # Use lower of (median margin, 40%) as threshold so it's business-meaningful
    margin_threshold = min(margin_median, 40.0)

    hidden_losers = summary[
        (summary["qty"] > vol_median) &
        (summary["Profit Margin %"] < margin_threshold)
    ].sort_values("Profit Margin %")

    if hidden_losers.empty:
        st.markdown("""
        <div style="background:rgba(35,134,54,0.15);border:1px solid rgba(35,134,54,0.3);
        border-radius:8px;padding:40px 20px;text-align:center;color:#3fb950;margin-top:40px;">
            ✅ No hidden losers — great margin discipline!<br>
            <small style="color:#8b949e;font-size:11px;">
            Definition: items with volume above median AND margin below {:.0f}%
            </small>
        </div>
        """.format(margin_threshold), unsafe_allow_html=True)
    else:
        fig4 = go.Figure(go.Scatter(
            x=hidden_losers["qty"],
            y=hidden_losers["Profit Margin %"],
            mode="markers+text",
            text=hidden_losers["Item Name"],
            textposition="top center",
            marker=dict(color="#d29922", size=14, line=dict(color="#fff", width=1)),
            hovertemplate="%{text}<br>Volume: %{x:,.0f}<br>Margin: %{y:.1f}%<extra></extra>",
        ))
        fig4.update_layout(
            title=f"⚠️ Hidden Losers (vol>{vol_median:.0f} & margin<{margin_threshold:.0f}%)",
            **PLOT_LAYOUT, height=300,
            xaxis=dict(title="Volume Sold", gridcolor="#21262d"),
            yaxis=dict(title="Profit Margin %", gridcolor="#21262d"),
        )
        st.plotly_chart(fig4, use_container_width=True)

# ── Sales Trend ───────────────────────────────────────────────────────────────
if not valid_dates.empty:
    st.markdown('<div class="section-header"><span class="section-dot"></span> Sales Trend</div>', unsafe_allow_html=True)

    trend_mode = st.radio("Aggregation", ["Daily", "Weekly", "Monthly"], horizontal=True)
    freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "ME"}
    freq = freq_map[trend_mode]

    df_trend = df_filtered.copy()
    df_trend["_date"] = pd.to_datetime(df_trend[date_col], errors="coerce")
    df_trend = df_trend.dropna(subset=["_date"])
    trend = df_trend.groupby(pd.Grouper(key="_date", freq=freq)).agg(
        Revenue=("_revenue", "sum"),
        Profit=("_profit", "sum"),
    ).reset_index()

    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(x=trend["_date"], y=trend["Revenue"], name="Revenue",
                              line=dict(color="#7c8aff", width=2), fill="tozeroy",
                              fillcolor="rgba(124,138,255,0.1)"))
    fig5.add_trace(go.Scatter(x=trend["_date"], y=trend["Profit"], name="Profit",
                              line=dict(color="#3fb950", width=2), fill="tozeroy",
                              fillcolor="rgba(63,185,80,0.1)"))
    fig5.update_layout(**PLOT_LAYOUT, height=300,
                       yaxis=dict(title=f"Amount ({currency_sym})", gridcolor="#21262d"),
                       legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig5, use_container_width=True)

# ── Recommendations ───────────────────────────────────────────────────────────
st.markdown('<div class="section-header"><span class="section-dot"></span> Recommendations</div>', unsafe_allow_html=True)

# BUG FIX 4: Consistent recommendation logic
# Promote: top margin items (above avg margin)
# Review:  mid margin items
# Phase out: very low margin items (< 35% of max margin)

avg_m = summary["Profit Margin %"].mean()
max_m = summary["Profit Margin %"].max()

promote_threshold = avg_m
phase_threshold = max_m * 0.35

recs_promote = summary[summary["Profit Margin %"] >= promote_threshold].sort_values("Profit Margin %", ascending=False)
recs_review = summary[(summary["Profit Margin %"] >= phase_threshold) & (summary["Profit Margin %"] < promote_threshold)].sort_values("Profit Margin %", ascending=False)
recs_phase = summary[summary["Profit Margin %"] < phase_threshold].sort_values("Profit Margin %")

for _, row in recs_promote.iterrows():
    st.markdown(f"""<div class="rec-card">✅ Promote <strong>"{row['Item Name']}"</strong> — {row['Profit Margin %']:.1f}% margin. Feature it prominently, train your team to upsell it.</div>""", unsafe_allow_html=True)

for _, row in recs_review.iterrows():
    st.markdown(f"""<div class="rec-card warning">⚠️ Review <strong>"{row['Item Name']}"</strong> — {row['Profit Margin %']:.1f}% margin. Consider raising price or reducing cost.</div>""", unsafe_allow_html=True)

for _, row in recs_phase.iterrows():
    st.markdown(f"""<div class="rec-card danger">🔴 Phase Out / Reprice <strong>"{row['Item Name']}"</strong> — {row['Profit Margin %']:.1f}% margin. Raise price, cut cost, or remove it.</div>""", unsafe_allow_html=True)

# ── Business Summary ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header"><span class="section-dot"></span> Business Summary</div>', unsafe_allow_html=True)

# BUG FIX 5: Correct highest margin item logic
best_margin_row = summary.loc[summary["Profit Margin %"].idxmax()]
worst_margin_row = summary.loc[summary["Profit Margin %"].idxmin()]
best_profit_row = summary.loc[summary["profit"].idxmax()]
top_volume_row = summary.loc[summary["qty"].idxmax()]

margin_health = "strong — you're running a tight, profitable operation" if avg_margin >= 45 else \
                "solid — there's room to push margins higher" if avg_margin >= 30 else \
                "below average — urgent action needed on low-margin items"

st.markdown(f"""
<div class="summary-box">
    <p>▸ Your business recorded <span class="hl-purple">{fmt(total_rev, currency_sym)}</span> in total revenue with a net profit of <span class="hl-green">{fmt(total_profit, currency_sym)}</span>. Your overall margin of <span class="hl-green">{avg_margin:.1f}%</span> is {margin_health}.</p>
    <p>▸ <span class="hl-green">{best_margin_row['Item Name']}</span> has your highest profit margin at {best_margin_row['Profit Margin %']:.1f}%. Make sure it's front-and-center — featured, promoted, and recommended to every customer.</p>
    <p>▸ <span class="hl-purple">{top_volume_row['Item Name']}</span> leads in volume ({top_volume_row['qty']:,.0f} units sold). With a {top_volume_row['Profit Margin %']:.1f}% margin, {"it's a genuine star — protect its cost structure." if top_volume_row['Profit Margin %'] >= avg_margin else "watch out — high volume with low margin drains profit quietly."}</p>
    <p>▸ <span class="hl-red">{worst_margin_row['Item Name']}</span> has the weakest margin at {worst_margin_row['Profit Margin %']:.1f}%. Raise its price, reduce material/ingredient cost, or phase it out entirely.</p>
    <p>▸ <strong>Your action plan:</strong> {"You're in a solid position. Double down on your highest-margin items, phase out the bottom 20%, and keep a weekly eye on hidden losers before they quietly erode what you've built." if avg_margin >= 40 else "Your margins need attention. Start by repricing or removing your worst performers, and focus promotions on high-margin items."}</p>
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    GoExecuteX Insights · {display_type} · Analyzed {total_tx:,} rows · Data processed locally — never uploaded anywhere
</div>
""", unsafe_allow_html=True)
