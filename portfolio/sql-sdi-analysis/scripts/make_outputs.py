from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_DIR / "data" / "index_data.csv"
OUTPUT_DIR = PROJECT_DIR / "outputs"
FIGURE_DIR = PROJECT_DIR / "figures"


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    FIGURE_DIR.mkdir(exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    score_columns = [
        "Year",
        "SDI",
        "SDI_Economy",
        "SDI_Society",
        "SDI_Resource",
        "SDI_Ecology",
    ]
    for column in score_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    latest_year = int(df["Year"].max())
    latest = df[df["Year"] == latest_year].dropna(subset=["SDI"]).copy()

    top15 = latest.sort_values("SDI", ascending=False).head(15)[
        [
            "Alpha-3 code",
            "CountryName_CN",
            "Year",
            "SDI",
            "SDI_Economy",
            "SDI_Society",
            "SDI_Resource",
            "SDI_Ecology",
            "Region",
        ]
    ]
    top15.to_csv(OUTPUT_DIR / "latest_year_top15_sdi.csv", index=False)

    region_names = {
        "S": "Southern Africa",
        "W": "Western Africa",
        "C": "Central Africa",
        "E": "Eastern Africa",
    }
    latest["Region_Name"] = latest["Region"].map(region_names).fillna(latest["Region"].astype(str))
    regional = (
        latest.groupby(["Region", "Region_Name"], dropna=False)
        .agg(
            country_count=("Alpha-3 code", "count"),
            avg_sdi=("SDI", "mean"),
            avg_economy=("SDI_Economy", "mean"),
            avg_society=("SDI_Society", "mean"),
            avg_resource=("SDI_Resource", "mean"),
            avg_ecology=("SDI_Ecology", "mean"),
        )
        .reset_index()
        .sort_values("avg_sdi", ascending=False)
    )
    regional.to_csv(OUTPUT_DIR / "latest_year_regional_average_sdi.csv", index=False)

    trend = df[df["Alpha-3 code"] == "KEN"].sort_values("Year")[
        [
            "Alpha-3 code",
            "CountryName_CN",
            "Year",
            "SDI",
            "SDI_Economy",
            "SDI_Society",
            "SDI_Resource",
            "SDI_Ecology",
            "Region",
        ]
    ]
    trend.to_csv(OUTPUT_DIR / "kenya_sdi_trend.csv", index=False)

    plt.style.use("seaborn-v0_8-whitegrid")
    make_top15_chart(top15, latest_year)
    make_regional_chart(regional, latest_year)
    make_kenya_trend_chart(trend)


def make_top15_chart(top15: pd.DataFrame, latest_year: int) -> None:
    plot_top = top15.sort_values("SDI")
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(plot_top["Alpha-3 code"], plot_top["SDI"], color="#2f6f73")
    ax.set_title(
        f"Top 15 Sub-Saharan African Countries by SDI, {latest_year}",
        loc="left",
        fontsize=13,
        weight="bold",
    )
    ax.set_xlabel("Sustainable Development Index (SDI)")
    ax.set_ylabel("ISO alpha-3 country code")
    ax.set_xlim(0, max(1, plot_top["SDI"].max() * 1.08))
    for index, value in enumerate(plot_top["SDI"]):
        ax.text(value + 0.01, index, f"{value:.3f}", va="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "latest_year_top15_sdi.png", dpi=200)
    plt.close(fig)


def make_regional_chart(regional: pd.DataFrame, latest_year: int) -> None:
    plot_reg = regional.sort_values("avg_sdi")
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.barh(plot_reg["Region_Name"], plot_reg["avg_sdi"], color="#7c6f9f")
    ax.set_title(f"Regional Average SDI, {latest_year}", loc="left", fontsize=13, weight="bold")
    ax.set_xlabel("Average SDI")
    ax.set_ylabel("Region")
    ax.set_xlim(0, max(1, plot_reg["avg_sdi"].max() * 1.14))
    for index, row in enumerate(plot_reg.itertuples()):
        ax.text(row.avg_sdi + 0.01, index, f"{row.avg_sdi:.3f}  n={row.country_count}", va="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "latest_year_regional_average_sdi.png", dpi=200)
    plt.close(fig)


def make_kenya_trend_chart(trend: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.plot(trend["Year"], trend["SDI"], marker="o", linewidth=2.2, color="#2f6f73", label="Overall SDI")
    ax.plot(trend["Year"], trend["SDI_Economy"], linewidth=1.4, color="#6d8cc3", label="Economy")
    ax.plot(trend["Year"], trend["SDI_Society"], linewidth=1.4, color="#d08c60", label="Society")
    ax.plot(trend["Year"], trend["SDI_Resource"], linewidth=1.4, color="#8aa15f", label="Resource")
    ax.plot(trend["Year"], trend["SDI_Ecology"], linewidth=1.4, color="#9a6aa8", label="Ecology")
    ax.set_title("Kenya SDI and Dimension Scores Over Time", loc="left", fontsize=13, weight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Index score")
    ax.set_ylim(0, 1)
    ax.legend(frameon=False, ncol=3, fontsize=9)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "kenya_sdi_trend.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
