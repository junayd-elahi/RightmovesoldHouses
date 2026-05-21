import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

plt.rcParams.update({
    "figure.dpi": 110,
    "savefig.dpi": 140,
    "savefig.bbox": "tight",
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "--",
})

OUT = "outputs"
os.makedirs(OUT, exist_ok=True)

# Load and clean data
df = pd.read_csv("rightmove_data.csv")
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date", "price"]).copy()
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
df["postcode"] = df["postcode"].astype(str).str.upper().str.strip()
df["postcode_district"] = df["postcode"].str.extract(r"^([A-Z]{1,2}\d{1,2}[A-Z]?)")
df["price_per_sqft"] = df["price"] / df["sqft"]
df["property_type"] = df["property_type"].replace({"unknown": "Unknown"})

print(f"Loaded {len(df):,} transactions from {df['year'].min()} to {df['year'].max()}")

# Chart 1: Median price trend by year with transaction volume
yearly = df.groupby("year").agg(
    median_price=("price", "median"),
    mean_price=("price", "mean"),
    volume=("price", "size")
).reset_index()
yearly = yearly[yearly["volume"] >= 5]

fig, ax1 = plt.subplots(figsize=(11, 5.5))
ax2 = ax1.twinx()

ax2.bar(yearly["year"], yearly["volume"], color="#cfd8dc", width=0.75, label="Transaction volume", zorder=1)
ax2.set_ylabel("Transactions", color="#607d8b")
ax2.tick_params(axis="y", labelcolor="#607d8b")
ax2.grid(False)

ax1.plot(yearly["year"], yearly["median_price"], color="#1f3a93", linewidth=2.5, marker="o", markersize=5,
         label="Median price", zorder=3)
ax1.plot(yearly["year"], yearly["mean_price"], color="#c0392b", linewidth=1.5, linestyle="--", marker="s", markersize=4,
         label="Mean price", zorder=3)
ax1.set_ylabel("Sale price (£)")
ax1.set_xlabel("Year")
ax1.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"£{x / 1000:.0f}k"))
ax1.set_zorder(ax2.get_zorder() + 1)
ax1.patch.set_visible(False)

plt.title("Price trend & transaction volume by year", fontsize=13, fontweight="bold", loc="left")
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=False)
plt.savefig(f"{OUT}/01_price_trend_volume.png")
plt.close()
print("✓ Chart 1: Price trend & volume")

# Chart 2: Year-over-year price growth
yearly["yoy_growth"] = yearly["median_price"].pct_change() * 100
yoy = yearly.dropna(subset=["yoy_growth"])

fig, ax = plt.subplots(figsize=(11, 5.5))
colors = ["#2e7d32" if v >= 0 else "#c62828" for v in yoy["yoy_growth"]]
ax.bar(yoy["year"], yoy["yoy_growth"], color=colors, width=0.75)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_ylabel("YoY change in median price (%)")
ax.set_xlabel("Year")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))

for _, row in yoy.iterrows():
    if abs(row["yoy_growth"]) > 15:
        ax.text(row["year"], row["yoy_growth"] + (1.5 if row["yoy_growth"] >= 0 else -2.5),
                f"{row['yoy_growth']:+.0f}%", ha="center", fontsize=8,
                color="#2e7d32" if row["yoy_growth"] >= 0 else "#c62828")

plt.title("Year-over-year price growth — green = growth, red = decline", fontsize=13, fontweight="bold", loc="left")
plt.savefig(f"{OUT}/02_yoy_growth.png")
plt.close()
print("✓ Chart 2: YoY growth")

# Chart 3: Top postcodes by median price
postcode_stats = df.groupby("postcode").agg(
    median=("price", "median"),
    volume=("price", "size")
).reset_index()
postcode_stats = postcode_stats[postcode_stats["volume"] >= 30].sort_values("median", ascending=False).head(25)

fig, ax = plt.subplots(figsize=(11, max(4, 0.35 * len(postcode_stats))))
norm = plt.Normalize(postcode_stats["median"].min(), postcode_stats["median"].max())
cmap = plt.cm.RdYlGn
colors = cmap(norm(postcode_stats["median"]))

ax.barh(postcode_stats["postcode"], postcode_stats["median"], color=colors, edgecolor="white")
ax.invert_yaxis()
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"£{x / 1000:.0f}k"))
ax.set_xlabel("Median sale price (£)")

for i, (median, volume) in enumerate(zip(postcode_stats["median"], postcode_stats["volume"])):
    ax.text(median, i, f"  £{median / 1000:.0f}k  (n={volume})", va="center", fontsize=9)

ax.set_xlim(0, postcode_stats["median"].max() * 1.22)
plt.title("Top 25 postcodes ranked by median price (min 30 sales)", fontsize=13, fontweight="bold", loc="left")
plt.savefig(f"{OUT}/03_postcode_ranking.png")
plt.close()
print("✓ Chart 3: Postcode rankings")

# Chart 4: Price distribution by property type
property_counts = df["property_type"].value_counts()
common_types = property_counts[property_counts >= 10].index.tolist()
filtered_df = df[df["property_type"].isin(common_types)]

order = filtered_df.groupby("property_type")["price"].median().sort_values(ascending=False).index.tolist()

fig, ax = plt.subplots(figsize=(10, 5.5))
data = [filtered_df[filtered_df["property_type"] == p]["price"].values for p in order]
bp = ax.boxplot(data, labels=order, patch_artist=True, showfliers=False, widths=0.55)
palette = ["#1f3a93", "#3498db", "#16a085", "#f39c12", "#7f8c8d"]
for patch, c in zip(bp["boxes"], palette):
    patch.set_facecolor(c)
    patch.set_alpha(0.75)
for median in bp["medians"]:
    median.set_color("white")
    median.set_linewidth(2)

ax.set_yscale("log")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"£{x / 1000:.0f}k"))
ax.set_ylabel("Sale price (£, log scale)")

for i, p in enumerate(order, 1):
    count = (filtered_df["property_type"] == p).sum()
    ax.text(i, ax.get_ylim()[0] * 1.4, f"n={count:,}", ha="center", fontsize=9, color="#555")

plt.title("Price distribution by property type", fontsize=13, fontweight="bold", loc="left")
plt.savefig(f"{OUT}/04_price_by_proptype.png")
plt.close()
print("✓ Chart 4: Price by property type")

# Chart 5: Price per sqft by property type
sqft_data = df.dropna(subset=["sqft", "price_per_sqft"]).copy()
sqft_data = sqft_data[(sqft_data["sqft"] > 100) & (sqft_data["sqft"] < 10000) &
                      (sqft_data["price_per_sqft"] < sqft_data["price_per_sqft"].quantile(0.99))]
sqft_data = sqft_data[sqft_data["property_type"].isin(common_types)]

fig, ax = plt.subplots(figsize=(10, 5.5))
order_ppsf = sqft_data.groupby("property_type")["price_per_sqft"].median().sort_values(ascending=False).index.tolist()
data = [sqft_data[sqft_data["property_type"] == p]["price_per_sqft"].values for p in order_ppsf]
bp = ax.boxplot(data, labels=order_ppsf, patch_artist=True, showfliers=False, widths=0.55)
for patch, c in zip(bp["boxes"], palette):
    patch.set_facecolor(c)
    patch.set_alpha(0.75)
for median in bp["medians"]:
    median.set_color("white")
    median.set_linewidth(2)

ax.set_ylabel("Price per sqft (£)")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"£{x:.0f}"))
plt.title("Price per square foot by property type", fontsize=13, fontweight="bold", loc="left")
plt.savefig(f"{OUT}/05_ppsf_by_proptype.png")
plt.close()
print("✓ Chart 5: Price per sqft")

# Chart 6: Bedrooms vs price
bedroom_data = df.dropna(subset=["bedrooms", "price"]).copy()
bedroom_data["bed_count"] = pd.to_numeric(bedroom_data["bedrooms"], errors="coerce")
bedroom_data = bedroom_data.dropna(subset=["bed_count"])

fig, ax = plt.subplots(figsize=(11, 5.5))
bedroom_median = bedroom_data.groupby("bed_count")["price"].median()
ax.plot(bedroom_median.index, bedroom_median.values, color="#16a085", marker="o", linewidth=2.5, markersize=8)
ax.fill_between(bedroom_median.index, bedroom_median.values * 0.75, bedroom_median.values * 1.25, alpha=0.15,
                color="#16a085")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"£{x / 1000:.0f}k"))
ax.set_xlabel("Bedrooms")
ax.set_ylabel("Median price (£)")
plt.title("How price scales with bedroom count", fontsize=13, fontweight="bold", loc="left")
plt.savefig(f"{OUT}/06_bedrooms_vs_price.png")
plt.close()
print("✓ Chart 6: Bedrooms vs price")

# Chart 7: Floor area vs price (scatter with regression)
scatter_data = df.dropna(subset=["sqft"]).copy()
scatter_data = scatter_data[(scatter_data["sqft"].between(150, 5000)) &
                            (scatter_data["price"] < scatter_data["price"].quantile(0.99))]

fig, ax = plt.subplots(figsize=(11, 6))
color_map = {p: palette[i] for i, p in enumerate(common_types)}
for p in common_types:
    subset = scatter_data[scatter_data["property_type"] == p]
    if len(subset) > 0:
        ax.scatter(subset["sqft"], subset["price"], s=10, alpha=0.35,
                   color=color_map.get(p, "#999"), label=f"{p} (n={len(subset)})")

# Linear regression line
x = scatter_data["sqft"].values
y = scatter_data["price"].values
slope, intercept = np.polyfit(x, y, 1)
x_line = np.linspace(x.min(), x.max(), 100)
ax.plot(x_line, slope * x_line + intercept, color="black", linewidth=1.5, linestyle="--",
        label=f"Linear fit: £{slope:.0f}/sqft + £{intercept / 1000:.0f}k")

ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"£{x / 1000:.0f}k"))
ax.set_xlabel("Floor area (sqft)")
ax.set_ylabel("Sale price (£)")
ax.legend(frameon=False, fontsize=9, loc="upper left")
plt.title("Floor area vs sale price", fontsize=13, fontweight="bold", loc="left")
plt.savefig(f"{OUT}/07_sqft_vs_price.png")
plt.close()
print("✓ Chart 7: Sqft vs price")

# Chart 8: Tenure premium over time
tenure_data = df.groupby([df["date"].dt.year, "tenure"])["price"].median().unstack()
tenure_data = tenure_data.dropna()
tenure_data = tenure_data[tenure_data.index >= 2000]

fig, ax = plt.subplots(figsize=(11, 5.5))
if "Freehold" in tenure_data.columns:
    ax.plot(tenure_data.index, tenure_data["Freehold"], color="#2e7d32", marker="o", linewidth=2.5, label="Freehold")
if "Leasehold" in tenure_data.columns:
    ax.plot(tenure_data.index, tenure_data["Leasehold"], color="#1f3a93", marker="s", linewidth=2.5, label="Leasehold")

ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"£{x / 1000:.0f}k"))
ax.set_xlabel("Year")
ax.set_ylabel("Median price (£)")
ax.legend(frameon=False)
plt.title("Freehold vs Leasehold median price over time", fontsize=13, fontweight="bold", loc="left")
plt.savefig(f"{OUT}/08_tenure_trend.png")
plt.close()
print("✓ Chart 8: Tenure trends")

# Chart 9: Heatmap of median price by postcode and year
postcode_volume = df["postcode"].value_counts()
top_postcodes = postcode_volume[postcode_volume >= 50].head(15).index.tolist()
heatmap_data = df[df["postcode"].isin(top_postcodes)].groupby(["postcode", "year"])["price"].median().unstack()
heatmap_data = heatmap_data.loc[:, heatmap_data.columns >= 2005]

order_by_price = df[df["postcode"].isin(top_postcodes)].groupby("postcode")["price"].median().sort_values(
    ascending=False).index.tolist()
heatmap_data = heatmap_data.reindex(order_by_price)

fig, ax = plt.subplots(figsize=(12, 6))
im = ax.imshow(heatmap_data.values / 1000, aspect="auto", cmap="RdYlGn_r")
ax.set_xticks(range(len(heatmap_data.columns)))
ax.set_xticklabels(heatmap_data.columns, rotation=45, ha="right")
ax.set_yticks(range(len(heatmap_data.index)))
ax.set_yticklabels(heatmap_data.index)
ax.grid(False)

cbar = plt.colorbar(im, ax=ax, pad=0.01)
cbar.set_label("Median price (£k)")

plt.title("Median price heatmap: postcode district × year", fontsize=13, fontweight="bold", loc="left")
plt.savefig(f"{OUT}/09_heatmap_postcode_year.png")
plt.close()
print("✓ Chart 9: Postcode-year heatmap")

# Chart 10: Seasonality - when buyers buy vs when prices peak
df["month_num"] = df["date"].dt.month
seasonality = df.groupby("month_num").agg(volume=("price", "size"), median=("price", "median")).reset_index()
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].bar(seasonality["month_num"], seasonality["volume"], color="#3498db", edgecolor="white")
axes[0].set_xticks(range(1, 13))
axes[0].set_xticklabels(months)
axes[0].set_ylabel("Total transactions")
axes[0].set_title("Volume by month", loc="left", fontweight="bold")

axes[1].plot(seasonality["month_num"], seasonality["median"], color="#c0392b", marker="o", linewidth=2.5, markersize=7)
axes[1].set_xticks(range(1, 13))
axes[1].set_xticklabels(months)
axes[1].yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"£{x / 1000:.0f}k"))
axes[1].set_ylabel("Median price")
axes[1].set_title("Median price by month", loc="left", fontweight="bold")

plt.suptitle("Seasonality: when buyers buy vs when prices peak", fontsize=13, fontweight="bold", x=0.07, ha="left",
             y=1.02)
plt.savefig(f"{OUT}/10_seasonality.png")
plt.close()
print("✓ Chart 10: Seasonality")

# Chart 11: Repeat-sale capital appreciation
repeat_sales = df.groupby("address").filter(lambda g: len(g) >= 2).copy()
returns_data = []
for address, group in repeat_sales.groupby("address"):
    group = group.sort_values("date")
    first_sale = group.iloc[0]
    last_sale = group.iloc[-1]
    years_held = (last_sale["date"] - first_sale["date"]).days / 365.25

    if years_held < 1 or first_sale["price"] <= 0:
        continue

    cagr = (last_sale["price"] / first_sale["price"]) ** (1 / years_held) - 1
    returns_data.append({
        "address": address,
        "years": years_held,
        "cagr": cagr * 100,
        "first_price": first_sale["price"],
        "last_price": last_sale["price"]
    })

returns_df = pd.DataFrame(returns_data)

fig, ax = plt.subplots(figsize=(11, 5.5))
returns_clipped = returns_df[returns_df["cagr"].between(-15, 30)]
ax.hist(returns_clipped["cagr"], bins=50, color="#1f3a93", edgecolor="white", alpha=0.85)
median_cagr = returns_df["cagr"].median()
ax.axvline(median_cagr, color="#c0392b", linewidth=2, linestyle="--", label=f"Median CAGR: {median_cagr:.1f}%")
ax.axvline(0, color="black", linewidth=0.8)
ax.set_xlabel("Annualised return (CAGR, %)")
ax.set_ylabel("Number of properties")
ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.legend(frameon=False)
plt.title(f"Repeat-sale capital appreciation — {len(returns_df):,} properties", fontsize=13, fontweight="bold",
          loc="left")
plt.savefig(f"{OUT}/11_repeat_sale_returns.png")
plt.close()
print("✓ Chart 11: Capital appreciation")

# Chart 12: 12-month rolling median price with downturns highlighted
monthly_data = df.groupby("month")["price"].median().reset_index()
monthly_data = monthly_data.sort_values("month")
monthly_data["rolling_median"] = monthly_data["price"].rolling(12, min_periods=6).median()

fig, ax = plt.subplots(figsize=(11, 5.5))
ax.plot(monthly_data["month"], monthly_data["price"], color="#bdc3c7", linewidth=0.7, alpha=0.7, label="Monthly median")
ax.plot(monthly_data["month"], monthly_data["rolling_median"], color="#1f3a93", linewidth=2.5,
        label="12-month rolling median")

# Highlight downturns: rolling median >5% below its cumulative peak
cumulative_peak = monthly_data["rolling_median"].cummax()
in_downturn = monthly_data["rolling_median"] < cumulative_peak * 0.95
ax.fill_between(monthly_data["month"], 0, monthly_data["rolling_median"].max() * 1.1,
                where=in_downturn, color="#c62828", alpha=0.08, label="Period >5% below prior peak")

ax.set_ylim(0, monthly_data["rolling_median"].max() * 1.1)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"£{x / 1000:.0f}k"))
ax.set_xlabel("Date")
ax.set_ylabel("Median price (£)")
ax.legend(frameon=False, loc="upper left")
plt.title("Long-term price trend with downturn periods highlighted", fontsize=13, fontweight="bold", loc="left")
plt.savefig(f"{OUT}/12_rolling_trend_downturns.png")
plt.close()
print("✓ Chart 12: Rolling trend")

print(f"\n✓ All charts saved to: {OUT}")
