from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "figures" / "distribution_graphs"
YEARS = list(range(2001, 2022))

KDE_COLUMNS = {
    "SDI_TwoStage": ("Sustainable development score", "comprehensive_sustainable_development_kde"),
    "SDI_Economy_TwoStage": ("Economic sustainability score", "economic_sustainability_kde"),
    "SDI_Society_TwoStage": ("Social sustainability score", "social_sustainability_kde"),
    "SDI_Resource_TwoStage": ("Resource sustainability score", "resource_sustainability_kde"),
    "SDI_Ecology_TwoStage": ("Ecological sustainability score", "ecological_sustainability_kde"),
}

ENGLISH_INDICATOR_LABELS = {
    "GDP per capita growth (annual %)_x": "GDP per capita growth",
    "Merchandise exports (% of GDP)": "Merchandise exports",
    "Final consumption expenditure (% of GDP)": "Final consumption expenditure",
    "Gross fixed capital formation (% of GDP)": "Gross fixed capital formation",
    "Inflation, GDP deflator (annual %)": "Inflation",
    "Agriculture, forestry, and fishing, value added per worker (constant 2015 US$)_x": "Agriculture value added per worker",
    "Industry (including construction), value added per worker (constant 2015 US$)_x": "Industry value added per worker",
    "Services, value added per worker (constant 2015 US$)_x": "Services value added per worker",
    "Current account balance, percent of GDP (Percent of GDP)(IMF)": "Current account balance",
    "Proportion of seats held by women in national parliaments (%)_x": "Women in parliament",
    "Prevalence of undernourishment (percent) (3-year average)": "Undernourishment prevalence",
    "Life expectancy at birth, total (years)_pct_change": "Life expectancy growth",
    "Population growth (annual %)": "Population growth",
    "Scientific and technical journal articles per million people": "Scientific articles per million people",
    "Prevalence of HIV, total (% of population ages 15-49)_x": "HIV prevalence",
    "Domestic general government health expenditure (% of GDP)": "Government health expenditure",
    "Individuals using the Internet (% of population)_x": "Internet users",
    "Mobile cellular subscriptions (per 100 people)": "Mobile cellular subscriptions",
    "Access to electricity (% of population)_x": "Access to electricity",
    "Agricultural land (% of land area)": "Agricultural land share",
    "Arable land (% of land area)": "Arable land share",
    "Adjusted savings: mineral depletion (% of GNI)": "Mineral depletion",
    "Adjusted savings: net forest depletion (% of GNI)": "Net forest depletion",
    "Renewable internal freshwater resources per capita (cubic meters)_x": "Renewable freshwater per capita",
    "Energy intensity level of primary energy (MJ/$2017 PPP GDP)_x": "Energy intensity",
    "Water productivity, total (constant 2015 US$ GDP per cubic meter of total freshwater withdrawal)_x": "Water productivity",
    "Adjusted savings: energy depletion (% of GNI)": "Energy depletion",
    "Energy consumption per capita (million Btu per person)": "Energy consumption per capita",
    "Solar, tide, wave, fuel cell electricity installed capacity (million kilowatts)_per_capita": "Solar/tide/wave/fuel-cell capacity per capita",
    "Biomass and waste electricity net generation (million metric tons of oil equivalent)_per_capita": "Biomass and waste electricity per capita",
    "Forest area (% of land area)_x": "Forest area share",
    "Wetland area(% of land area)": "Wetland area share",
    "Grassland area(% of land area)": "Grassland area share",
    "Terrestrial barren land|1000 HA|ECCCT|Terrestrial Barren Land|Environment, Climate Change, Climate Indicators, Land Cover Accounts, Terrestrial Barren Land|Climate neutral(% of land area)": "Barren land share",
    "CO2 emissions (metric tons per capita)_x": "CO2 emissions per capita",
    "PM2.5 exposure/Ambient particulate matter pollution": "PM2.5 exposure",
    "Terrestrial biome protection (global weights)": "Terrestrial biome protection",
    "Species Protection Index": "Species Protection Index",
}


def configure_plot_style() -> None:
    sns.set_theme(
        style="white",
        rc={
            "font.sans-serif": ["Songti SC", "Arial Unicode MS", "Heiti SC"],
            "font.family": "DejaVu Sans",
            "axes.unicode_minus": False,
        },
    )
    plt.rc("font", family="DejaVu Sans", weight="bold", size=12)


def load_two_stage_index() -> pd.DataFrame:
    data = pd.read_csv(PROJECT_DIR / "index_data_two_stage_comparison.csv")
    data = data[data["Year"].isin(YEARS)].copy()
    for column in KDE_COLUMNS:
        data[column] = data[column] * 100
    return data


def plot_kde(data: pd.DataFrame, column: str, xlabel: str, output_name: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 7.5))
    palette = sns.color_palette("Blues", n_colors=len(YEARS))
    sns.kdeplot(
        data=data,
        x=column,
        hue="Year",
        hue_order=YEARS,
        bw_adjust=1.0,
        common_norm=False,
        palette=palette,
        linewidth=1.15,
        ax=ax,
    )
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Density")
    ax.tick_params(
        axis="both",
        direction="in",
        length=4,
        width=1.2,
        colors="black",
        left=True,
        bottom=True,
    )
    if ax.legend_ is not None:
        ax.legend_.set_title("")
        for text in ax.legend_.texts:
            text.set_fontsize(8)
    fig.savefig(OUTPUT_DIR / f"{output_name}.png", dpi=600, bbox_inches="tight")
    plt.close(fig)


def export_kde_figures() -> None:
    data = load_two_stage_index()
    for column, (xlabel, output_name) in KDE_COLUMNS.items():
        plot_kde(data, column, xlabel, output_name)


def load_scaled_indicator_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    selected = pd.read_excel(PROJECT_DIR / "selected_indicator_system_variables.xlsx")
    scaled = pd.read_excel(PROJECT_DIR / "scaled_data.xlsx")
    countries = pd.read_excel(PROJECT_DIR / "Variables Chosen.xlsx", sheet_name="Countries")
    country_codes = countries[["CountryName_CN", "Alpha-3 code"]].drop_duplicates()
    scaled[["CountryName_CN", "Numeric"]] = scaled[["CountryName_CN", "Numeric"]].ffill()
    scaled = scaled.merge(country_codes, on="CountryName_CN", how="left")
    scaled["Year"] = scaled["Year"].astype(int)
    scaled = scaled[scaled["Year"].isin(YEARS)].copy()
    return selected, scaled


def build_indicator_change_matrix() -> pd.DataFrame:
    selected, scaled = load_scaled_indicator_data()
    variable_names = selected["Variables"].tolist()
    rename_map = {name: ENGLISH_INDICATOR_LABELS.get(name, name) for name in variable_names}

    missing = [column for column in variable_names if column not in scaled.columns]
    if missing:
        raise ValueError(f"Missing scaled indicator columns: {missing}")

    baseline = (
        scaled.loc[scaled["Year"].eq(YEARS[0]), ["Alpha-3 code", *variable_names]]
        .drop_duplicates(subset=["Alpha-3 code"])
        .set_index("Alpha-3 code")
    )
    endpoint = (
        scaled.loc[scaled["Year"].eq(YEARS[-1]), ["Alpha-3 code", *variable_names]]
        .drop_duplicates(subset=["Alpha-3 code"])
        .set_index("Alpha-3 code")
    )

    country_order = endpoint.mean(axis=1).sort_values(ascending=False).index
    change = (endpoint.loc[country_order, variable_names] - baseline.loc[country_order, variable_names]).T
    change = change.rename(index=rename_map)
    change.index.name = "Indicator"
    return change


def export_indicator_change_heatmap() -> None:
    change = build_indicator_change_matrix()
    change.to_csv(OUTPUT_DIR / "indicator_change_2001_2021_matrix.csv", encoding="utf-8-sig")

    fig_height = max(11, len(change) * 0.28)
    fig_width = max(16, change.shape[1] * 0.30)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    sns.heatmap(
        change,
        xticklabels=True,
        yticklabels=True,
        cmap="RdBu",
        vmax=1,
        vmin=-1,
        center=0,
        linewidths=0.08,
        linecolor="white",
        cbar_kws={"label": "Change in normalized score"},
        ax=ax,
    )
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="x", labelrotation=90, labelsize=7)
    ax.tick_params(axis="y", labelsize=8)
    fig.savefig(OUTPUT_DIR / "indicator_change_heatmap_2001_2021.png", dpi=700, bbox_inches="tight")
    plt.close(fig)


def export_subsystem_mean_scores() -> None:
    data = pd.read_csv(PROJECT_DIR / "index_data_two_stage_comparison.csv")
    score_columns = {
        "SDI_TwoStage": "Composite",
        "SDI_Economy_TwoStage": "Economic",
        "SDI_Society_TwoStage": "Social",
        "SDI_Resource_TwoStage": "Resource",
        "SDI_Ecology_TwoStage": "Ecological",
    }
    mean_scores = (
        data[data["Year"].isin(YEARS)]
        .groupby("Year")[list(score_columns)]
        .mean()
        .mul(100)
        .rename(columns=score_columns)
    )

    styles = {
        "Composite": {"color": "#111111", "marker": "o", "linestyle": "-", "linewidth": 2.3},
        "Economic": {"color": "#C75D3A", "marker": "s", "linestyle": "--", "linewidth": 2.0},
        "Social": {"color": "#2F7F75", "marker": "^", "linestyle": "-.", "linewidth": 2.0},
        "Resource": {"color": "#7A6BAF", "marker": "D", "linestyle": ":", "linewidth": 2.3},
        "Ecological": {"color": "#4D8D3F", "marker": "X", "linestyle": (0, (5, 2, 1, 2)), "linewidth": 2.0},
    }

    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    for column, style in styles.items():
        ax.plot(
            mean_scores.index,
            mean_scores[column],
            label=column,
            markersize=5.2,
            markeredgecolor="white",
            markeredgewidth=0.6,
            markevery=2,
            **style,
        )

    ax.set_xlabel("Year", fontsize=10)
    ax.set_ylabel("Mean score (0-100)", fontsize=10)
    ax.set_xticks([2001, 2005, 2010, 2015, 2021])
    ax.grid(True, axis="y", linestyle="--", linewidth=0.6, alpha=0.35)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.14), frameon=False, fontsize=9)
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    fig.savefig(OUTPUT_DIR / "subsystem_mean_scores_2001_2021.png", dpi=600, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    configure_plot_style()
    export_kde_figures()
    export_indicator_change_heatmap()
    export_subsystem_mean_scores()
    print(f"Exported KDE and heatmap figures to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
