from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ------------------------------------------------------------
# PAGE SETUP
# ------------------------------------------------------------
st.set_page_config(
    page_title="Kenya Food Prices Dashboard",
    page_icon="🌽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🇰🇪 Kenya Food Prices Dashboard")
st.markdown(
    "Explore **maize and bean prices** over time, compare markets, "
    "study monthly patterns, and inspect the underlying data."
)
st.caption("Capstone project • Python • Pandas • Plotly • Streamlit")

# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------
DEFAULT_FILE = "KEN_RTFP_mkt_2007_2026-10-05.csv"

@st.cache_data(show_spinner="Loading food prices data...")
def load_data(file_bytes=None, file_name=None):
    if file_bytes is not None:
        data = pd.read_csv(file_bytes)
    else:
        candidates = [
            Path(DEFAULT_FILE),
            Path(__file__).parent / DEFAULT_FILE,
            Path.cwd() / DEFAULT_FILE,
        ]
        csv_path = next((p for p in candidates if p.exists()), None)
        if csv_path is None:
            return None, None
        data = pd.read_csv(csv_path)

    # Make column names consistent and tolerate common spelling variants.
    data.columns = [str(c).strip() for c in data.columns]
    lower_to_original = {c.lower(): c for c in data.columns}

    def find_column(possible_names):
        for name in possible_names:
            if name.lower() in lower_to_original:
                return lower_to_original[name.lower()]
        return None

    date_col = find_column(["price_date", "date", "price date"])
    market_col = find_column(["mkt_name", "market", "market_name"])
    county_col = find_column(["adm1_name", "county", "region", "admin1"])
    subcounty_col = find_column(["adm2_name", "subcounty", "district", "admin2"])
    beans_col = find_column(["beans", "beans_fao", "bean"])
    maize_col = find_column(["maize_fao", "maize", "maize white", "maize_white"])

    if date_col is None:
        raise ValueError("Could not find the date column. Expected 'price_date'.")
    if beans_col is None and maize_col is None:
        raise ValueError("Could not find maize or beans price columns in this CSV.")

    # Rename key fields into consistent names used by the dashboard.
    rename_map = {date_col: "price_date"}
    if market_col:
        rename_map[market_col] = "mkt_name"
    if county_col:
        rename_map[county_col] = "adm1_name"
    if subcounty_col:
        rename_map[subcounty_col] = "adm2_name"
    if beans_col:
        rename_map[beans_col] = "beans"
    if maize_col:
        rename_map[maize_col] = "maize_fao"
    data = data.rename(columns=rename_map)

    # Add location columns if the source file does not contain them.
    for col in ["mkt_name", "adm1_name", "adm2_name"]:
        if col not in data.columns:
            data[col] = "Unknown"
        data[col] = data[col].fillna("Unknown").astype(str)

    data["price_date"] = pd.to_datetime(data["price_date"], errors="coerce")
    data = data.dropna(subset=["price_date"]).copy()

    for col in ["beans", "maize_fao"]:
        if col not in data.columns:
            data[col] = pd.NA
        data[col] = pd.to_numeric(data[col], errors="coerce")
        # Treat impossible non-positive values as missing for price analysis.
        data.loc[data[col] <= 0, col] = pd.NA

    data["year"] = data["price_date"].dt.year.astype(int)
    data["month_number"] = data["price_date"].dt.month.astype(int)
    data["month"] = data["price_date"].dt.strftime("%B")
    data["month_short"] = data["price_date"].dt.strftime("%b")
    data["product_month"] = data["price_date"].dt.to_period("M").dt.to_timestamp()
    return data, {"date": "price_date", "market": "mkt_name", "county": "adm1_name"}

uploaded = st.sidebar.file_uploader(
    "Optional: upload the food prices CSV", type=["csv"],
    help="Normally the CSV should sit in the same folder as app.py. Upload it here if needed."
)

try:
    if uploaded is not None:
        df, column_info = load_data(uploaded, uploaded.name)
    else:
        df, column_info = load_data()
except Exception as exc:
    st.error(f"The CSV could not be read: {exc}")
    st.info("Check that the CSV is the original Kenya food-prices file and that it is beside app.py.")
    st.stop()

if df is None:
    st.error(f"Could not find **{DEFAULT_FILE}**.")
    st.markdown(
        "Place `KEN_RTFP_mkt_2007_2026-10-05.csv` in the same folder as `app.py`, "
        "or use the CSV upload button in the sidebar."
    )
    st.stop()

products = {"Maize": "maize_fao", "Beans": "beans"}
available_products = [label for label, col in products.items() if df[col].notna().any()]
if not available_products:
    st.error("The file loaded, but it contains no usable maize or bean prices.")
    st.stop()

# ------------------------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------------------------
st.sidebar.header("🔎 Dashboard Filters")
min_date = df["price_date"].min().date()
max_date = df["price_date"].max().date()
date_range = st.sidebar.date_input(
    "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
)
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

counties = sorted(x for x in df["adm1_name"].dropna().unique().tolist() if x != "Unknown")
selected_counties = st.sidebar.multiselect("Region / county", counties, default=[])
markets = sorted(x for x in df["mkt_name"].dropna().unique().tolist() if x != "Unknown")
selected_markets = st.sidebar.multiselect("Market", markets, default=[])
selected_products = st.sidebar.multiselect(
    "Products", available_products, default=available_products
)
if not selected_products:
    st.sidebar.warning("Choose at least one product to display its price analysis.")

filtered = df[
    (df["price_date"].dt.date >= start_date)
    & (df["price_date"].dt.date <= end_date)
].copy()
if selected_counties:
    filtered = filtered[filtered["adm1_name"].isin(selected_counties)]
if selected_markets:
    filtered = filtered[filtered["mkt_name"].isin(selected_markets)]

# Long-format data is useful for charts comparing both products.
long_parts = []
for product_name in selected_products:
    col = products[product_name]
    part = filtered.dropna(subset=[col]).copy()
    if not part.empty:
        part["Product"] = product_name
        part["Price"] = part[col]
        long_parts.append(part)
long_df = pd.concat(long_parts, ignore_index=True) if long_parts else pd.DataFrame()

if filtered.empty:
    st.warning("No records match these filters. Widen the date range or remove a market/region filter.")

# ------------------------------------------------------------
# OVERVIEW METRICS
# ------------------------------------------------------------
st.header("📌 Overview")
metric_cols = st.columns(4)
metric_cols[0].metric("Records after filters", f"{len(filtered):,}")
metric_cols[1].metric("Markets represented", f"{filtered['mkt_name'].nunique():,}" if not filtered.empty else "0")
metric_cols[2].metric(
    "Average maize price",
    f"{filtered['maize_fao'].mean():,.2f}" if filtered["maize_fao"].notna().any() else "No data",
)
metric_cols[3].metric(
    "Average bean price",
    f"{filtered['beans'].mean():,.2f}" if filtered["beans"].notna().any() else "No data",
)
st.caption("Prices are shown in the units provided by the source dataset; averages exclude missing values.")

# Tabs keep all dashboard sections available without hiding the other analyses.
tab_overview, tab_trends, tab_markets, tab_seasonal, tab_data = st.tabs(
    ["🏠 Overview", "📈 Price Trends", "📍 Market Comparisons", "🗓️ Seasonal Analysis", "🧾 Data Explorer"]
)

# ------------------------------------------------------------
# TAB 1: OVERVIEW
# ------------------------------------------------------------
with tab_overview:
    st.subheader("Price summary")
    summary_rows = []
    for product_name in available_products:
        col = products[product_name]
        vals = filtered[col].dropna()
        summary_rows.append({
            "Product": product_name,
            "Valid price records": int(vals.count()),
            "Average price": round(vals.mean(), 2) if not vals.empty else None,
            "Lowest price": round(vals.min(), 2) if not vals.empty else None,
            "Highest price": round(vals.max(), 2) if not vals.empty else None,
            "Missing values": int(filtered[col].isna().sum()),
        })
    if summary_rows:
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

    st.subheader("Average price by year")
    yearly_parts = []
    for product_name in selected_products:
        col = products[product_name]
        temp = filtered.dropna(subset=[col]).groupby("year", as_index=False)[col].mean()
        if not temp.empty:
            temp = temp.rename(columns={col: "Average price"})
            temp["Product"] = product_name
            yearly_parts.append(temp)
    if yearly_parts:
        yearly_df = pd.concat(yearly_parts, ignore_index=True)
        fig_year = px.line(
            yearly_df, x="year", y="Average price", color="Product", markers=True,
            title="Average maize and bean prices by year",
            labels={"year": "Year", "Average price": "Average price"},
        )
        fig_year.update_xaxes(dtick=1, tickformat="d")
        st.plotly_chart(fig_year, use_container_width=True, key="overview_yearly_average")
    else:
        st.info("There are no valid price observations for the selected products and filters.")

# ------------------------------------------------------------
# TAB 2: PRICE TRENDS
# ------------------------------------------------------------
with tab_trends:
    st.subheader("How prices change over time")
    st.write("The lines show monthly average prices for each selected product.")
    if not long_df.empty:
        trend_df = long_df.groupby(["product_month", "Product"], as_index=False)["Price"].mean()
        fig_trend = px.line(
            trend_df, x="product_month", y="Price", color="Product", markers=True,
            title="Monthly average price trends",
            labels={"product_month": "Month", "Price": "Average price"},
        )
        st.plotly_chart(fig_trend, use_container_width=True, key="monthly_price_trends")

        for product_name in selected_products:
            col = products[product_name]
            one = filtered.dropna(subset=[col]).groupby("product_month", as_index=False)[col].mean()
            if not one.empty:
                fig_one = px.line(
                    one, x="product_month", y=col, markers=True,
                    title=f"{product_name} price trend",
                    labels={"product_month": "Month", col: "Average price"},
                )
                safe_key = "single_product_trend_" + col
                st.plotly_chart(fig_one, use_container_width=True, key=safe_key)
    else:
        st.info("No valid maize or bean prices match the current filters. Try widening the date range or changing filters.")

# ------------------------------------------------------------
# TAB 3: MARKET COMPARISONS
# ------------------------------------------------------------
with tab_markets:
    st.subheader("Compare average prices across markets")
    if not long_df.empty:
        market_df = long_df.groupby(["mkt_name", "Product"], as_index=False)["Price"].mean()
        if not market_df.empty:
            top_n = st.slider("Number of markets to show", min_value=5, max_value=30, value=15, step=5, key="market_top_n")
            # Select top markets based on average price within each product, then plot the selected rows.
            top_market_parts = []
            for product_name in selected_products:
                sub = market_df[market_df["Product"] == product_name].nlargest(top_n, "Price")
                if not sub.empty:
                    top_market_parts.append(sub)
            top_market_df = pd.concat(top_market_parts, ignore_index=True) if top_market_parts else pd.DataFrame()
            if not top_market_df.empty:
                fig_market = px.bar(
                    top_market_df.sort_values("Price"), x="Price", y="mkt_name", color="Product",
                    barmode="group", orientation="h",
                    title=f"Markets with the highest average prices (top {top_n} per product)",
                    labels={"Price": "Average price", "mkt_name": "Market"},
                )
                st.plotly_chart(fig_market, use_container_width=True, key="market_highest_average_prices")

            fig_all_markets = px.bar(
                market_df, x="mkt_name", y="Price", color="Product", barmode="group",
                title="Average prices across all matching markets",
                labels={"mkt_name": "Market", "Price": "Average price"},
            )
            fig_all_markets.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_all_markets, use_container_width=True, key="market_all_average_prices")
            st.dataframe(
                market_df.sort_values(["Product", "Price"], ascending=[True, False]),
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("No market price summaries are available for these filters.")
    else:
        st.info("No valid maize or bean prices match the current filters.")

# ------------------------------------------------------------
# TAB 4: SEASONAL ANALYSIS
# ------------------------------------------------------------
with tab_seasonal:
    st.subheader("Monthly and seasonal patterns")
    st.write("This compares average prices by calendar month across all selected years.")
    if not long_df.empty:
        seasonal_df = long_df.groupby(["month_number", "month", "Product"], as_index=False)["Price"].mean()
        seasonal_df = seasonal_df.sort_values("month_number")
        fig_seasonal = px.line(
            seasonal_df, x="month", y="Price", color="Product", markers=True,
            category_orders={"month": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]},
            title="Average price by month",
            labels={"month": "Month of year", "Price": "Average price"},
        )
        st.plotly_chart(fig_seasonal, use_container_width=True, key="seasonal_monthly_line")

        fig_seasonal_bar = px.bar(
            seasonal_df, x="month", y="Price", color="Product", barmode="group",
            category_orders={"month": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]},
            title="Monthly average price comparison",
            labels={"month": "Month of year", "Price": "Average price"},
        )
        st.plotly_chart(fig_seasonal_bar, use_container_width=True, key="seasonal_monthly_bar")
        st.dataframe(seasonal_df, use_container_width=True, hide_index=True)
    else:
        st.info("No valid maize or bean prices match the current filters.")

# ------------------------------------------------------------
# TAB 5: DATA EXPLORER
# ------------------------------------------------------------
with tab_data:
    st.subheader("Explore and download filtered records")
    st.write("Use the sidebar filters above to narrow the records shown here.")
    display_columns = [
        c for c in ["price_date", "adm1_name", "adm2_name", "mkt_name", "maize_fao", "beans"]
        if c in filtered.columns
    ]
    display_df = filtered[display_columns].sort_values("price_date", ascending=False)
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=420)

    csv_data = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download filtered data as CSV",
        data=csv_data,
        file_name="kenya_maize_beans_filtered.csv",
        mime="text/csv",
        key="download_filtered_csv",
    )

    st.subheader("Missing values")
    missing_rows = []
    for product_name, col in products.items():
        if col in filtered.columns:
            missing_rows.append({
                "Product": product_name,
                "Missing values": int(filtered[col].isna().sum()),
                "Valid prices": int(filtered[col].notna().sum()),
                "Total records": int(len(filtered)),
                "Missing (%)": round(float(filtered[col].isna().mean() * 100), 2) if len(filtered) else 0,
            })
    st.dataframe(pd.DataFrame(missing_rows), use_container_width=True, hide_index=True)

    st.subheader("Data preview")
    st.code(", ".join(df.columns.astype(str)), language="text")

# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------
st.markdown("---")
st.caption("Kenya Food Prices Capstone Project | Python • Pandas • Plotly • Streamlit")
