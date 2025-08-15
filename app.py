import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.data_loader import load_properties
from utils.metrics import add_metrics_and_rank

st.set_page_config(page_title="RealEstate AI – Deal Analyzer", page_icon="🏠", layout="wide")

st.title("🏠 RealEstate AI — Deal Analyzer & Ranking (MVP)")

# Sidebar: load data
st.sidebar.header("Data")
uploaded = st.sidebar.file_uploader("Upload CSV (optional)", type=["csv"])
if uploaded:
    df_raw = pd.read_csv(uploaded)
else:
    df_raw = load_properties("data/properties.csv")  # uses default sample if file is missing/empty

st.sidebar.markdown("---")

# Sidebar: filters
cities = sorted(df_raw["city"].dropna().unique().tolist()) if "city" in df_raw.columns else []
city_sel = st.sidebar.multiselect("City filter", options=cities, default=cities)

max_price = int(df_raw["price"].max()) if "price" in df_raw.columns else 1_000_000
price_sel = st.sidebar.slider("Max price", min_value=0, max_value=max_price, value=max_price, step=10_000)

# Sidebar: weights
st.sidebar.subheader("Weights (Deal Score)")
w_cap = st.sidebar.slider("Cap Rate weight", 0.0, 1.0, 0.22)
w_coc = st.sidebar.slider("Cash-on-Cash weight", 0.0, 1.0, 0.22)
w_noi = st.sidebar.slider("NOI weight", 0.0, 1.0, 0.18)
w_risk = st.sidebar.slider("Risk (inverse) weight", 0.0, 1.0, 0.18)
w_growth = st.sidebar.slider("Predicted Growth weight", 0.0, 1.0, 0.12)
w_rrr = st.sidebar.slider("RRR Pass weight", 0.0, 1.0, 0.08)

st.sidebar.caption("Tip: Total weight doesn’t have to equal 1. We normalize internally.")

# Apply simple filters
df_filtered = df_raw.copy()
if city_sel:
    df_filtered = df_filtered[df_filtered["city"].isin(city_sel)]
if "price" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["price"] <= price_sel]

# Compute metrics & ranking
weights = dict(
    cap=w_cap, coc=w_coc, noi=w_noi, risk=w_risk, growth=w_growth, rrr=w_rrr
)
df_ranked = add_metrics_and_rank(df_filtered, weights=weights)

# Top KPIs
colA, colB, colC, colD = st.columns(4)
colA.metric("Properties", len(df_ranked))
colB.metric("Top Deal Score", f"{df_ranked['deal_score'].max():.3f}" if len(df_ranked) else "—")
colC.metric("Median Cap Rate", f"{df_ranked['cap_rate'].median()*100:.2f}%" if "cap_rate" in df_ranked else "—")
colD.metric("Median Risk Score (↓ better)", f"{df_ranked['risk_score'].median():.2f}" if "risk_score" in df_ranked else "—")

# Show ranked deals
st.markdown("### Ranked Deals")
show_cols = [
    "id","address","city","price","monthly_rent","monthly_expenses","vacancy_rate","rehab_cost",
    "NOI","cap_rate","cash_on_cash","predicted_rent_growth","risk_score","deal_score","timeline_months","risk_flags"
]
present_cols = [c for c in show_cols if c in df_ranked.columns]
st.dataframe(df_ranked[present_cols], use_container_width=True, hide_index=True)

# Download button
csv = df_ranked[present_cols].to_csv(index=False)
st.download_button("⬇️ Download Ranked Deals (CSV)", csv, file_name="ranked_deals.csv", mime="text/csv")

# ---------------------------
# 📊 Matplotlib visualizations
# ---------------------------
if not df_ranked.empty:
    st.markdown("## 📊 Visual Analysis")

    # Bar Chart - Deal Scores
    st.markdown("### Top Deals by Score")
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.bar(df_ranked["address"], df_ranked["deal_score"], color="skyblue")
    ax1.set_xlabel("Property Address")
    ax1.set_ylabel("Deal Score")
    ax1.set_title("Top Deals by Score")
    ax1.tick_params(axis='x', rotation=45)
    st.pyplot(fig1)

    # Scatter Plot - Price vs Cap Rate
    st.markdown("### Price vs Cap Rate")
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.scatter(df_ranked["price"], df_ranked["cap_rate"], color="green")
    ax2.set_xlabel("Price")
    ax2.set_ylabel("Cap Rate")
    ax2.set_title("Price vs Cap Rate")
    st.pyplot(fig2)

    # Scatter Plot - Price vs Cash-on-Cash Return
    st.markdown("### Price vs Cash-on-Cash Return")
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    ax3.scatter(df_ranked["price"], df_ranked["cash_on_cash"], color="purple")
    ax3.set_xlabel("Price")
    ax3.set_ylabel("Cash-on-Cash Return")
    ax3.set_title("Price vs Cash-on-Cash Return")
    st.pyplot(fig3)

st.markdown("""
**How to use:** Upload your own CSV (same columns as the sample), tweak weights, filter by city/price, and download the ranked list.
""")
