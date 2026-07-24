from __future__ import annotations

from pathlib import Path

import pandas as pd


LEVEL1_EN = {
    "经济": "Economic",
    "社会": "Social",
    "资源": "Resource",
    "生态": "Ecological",
}

LEVEL2_EN = {
    "发展质量": "Development quality",
    "产业发展": "Industrial development",
    "外部经济联系": "External economic linkages",
    "社会公平": "Social equity",
    "人口状况": "Population conditions",
    "教科医卫": "Health, science and education",
    "基础设施": "Infrastructure",
    "自然资源": "Natural resources",
    "资源利用效率": "Resource-use efficiency",
    "能源生产和消费": "Energy production and consumption",
    "生态环境": "Ecological conditions",
    "环境污染": "Environmental pollution",
    "生态保护": "Ecological protection",
}

TYPE_EN = {
    "正向": "Positive",
    "负向": "Negative",
}

SOURCE_EN = {
    "世界银行WDI数据库": "World Bank World Development Indicators (WDI)",
    "联合国大学世界发展经济研究所WIID数据库": "UNU-WIDER World Income Inequality Database (WIID)",
    "联合国粮食及农业组织FAO数据库": "Food and Agriculture Organization of the United Nations (FAO)",
    "Global Data Lab": "Global Data Lab",
    "美国能源信息署": "U.S. Energy Information Administration (EIA)",
    "世界货币基金组织气候变化数据库": "IMF Climate Change Indicators Dashboard",
    "耶鲁大学EPI数据库": "Yale Environmental Performance Index (EPI)",
    "联合国粮食及农业组织FAOSTAT土地覆盖数据库（经IMF-CID整理）": (
        "FAOSTAT Land Cover data via the IMF Climate Change Indicators Dashboard"
    ),
}

INDICATOR_EN = {
    "人均GDP增长率": "GDP per capita growth",
    "商品出口占GDP比重": "Merchandise exports (% of GDP)",
    "最终消费支出占GDP百分比": "Final consumption expenditure (% of GDP)",
    "固定资产形成占GDP百分比": "Gross fixed capital formation (% of GDP)",
    "通货膨胀率": "Inflation, GDP deflator (annual %)",
    "每工人农业增加值": "Agriculture, forestry, and fishing value added per worker",
    "每工人工业增加值": "Industry value added per worker",
    "每工人服务业增加值": "Services value added per worker",
    "经常账户余额占GDP百分比": "Current account balance (% of GDP)",
    "就业率": "Employment-to-population ratio",
    "基尼系数": "Gini coefficient",
    "性别平等": "Women in national parliament (% of seats)",
    "营养不良发生率": "Prevalence of undernourishment",
    "出生时预期寿命": "Life expectancy at birth",
    "劳动力比例": "Labor force (% of total population)",
    "人口增长率": "Population growth (annual %)",
    "成年人平均受教育年限": "Mean years of schooling",
    "发表科技论文数量（每百万人）": "Scientific and technical journal articles per million people",
    "艾滋病病毒感染率": "HIV prevalence (% of population ages 15-49)",
    "国内政府卫生支出（占GDP百分比）": "Domestic general government health expenditure (% of GDP)",
    "道路交通伤害造成的死亡率(每10万人)": "Mortality from road traffic injury (per 100,000 population)",
    "使用基本饮用水服务的人口比例": (
        "People using at least basic drinking water services (% of population)"
    ),
    "使用互联网的人口比例": "Individuals using the Internet (% of population)",
    "移动手机使用数": "Mobile cellular subscriptions (per 100 people)",
    "通电率": "Access to electricity (% of population)",
    "农业用地占比": "Agricultural land (% of land area)",
    "耕地面积占比": "Arable land (% of land area)",
    "矿石资源损耗占GNI比": "Mineral depletion (% of GNI)",
    "森林资源损耗占GNI比": "Net forest depletion (% of GNI)",
    "人均可再生内陆淡水资源": "Renewable internal freshwater resources per capita",
    "一次能源的能源强度": "Energy intensity of primary energy",
    "水资源生产效率": "Water productivity",
    "能源损耗占GNI比": "Energy depletion (% of GNI)",
    "人均能源消耗": "Energy consumption per capita",
    "人均太阳能、潮汐、波浪、燃料电池发电装机容量": (
        "Solar, tidal, wave, and fuel-cell electricity capacity per capita"
    ),
    "人均生物质和废弃物发电净发电量": (
        "Biomass and waste electricity net generation per capita"
    ),
    "森林面积占比": "Forest area (% of land area)",
    "湿地面积占比": "Wetland area (% of land area)",
    "草原面积占比": "Grassland area (% of land area)",
    "陆地贫瘠土地面积占比": "Terrestrial barren land (% of land area)",
    "人均二氧化碳排放": "CO2 emissions per capita",
    "PM2.5暴露量": "Anthropogenic PM2.5 exposure",
    "铅暴露量": "Lead exposure",
    "陆地生物群落保护": "Terrestrial biome protection",
    "物种保护指数": "Species Protection Index",
}


def indicator_label(row: pd.Series) -> str:
    label = INDICATOR_EN.get(str(row.get("三级指标", "")))
    if label:
        return label
    variable = str(row.get("Variables", "")).strip()
    return variable.replace("_pct_change", " growth").replace("_per_capita", " per capita").replace("_x", "")


def source_label(value: object) -> str:
    return SOURCE_EN.get(str(value), str(value))


def load_country_names(project_dir: Path) -> pd.DataFrame:
    country_names = pd.read_csv(
        project_dir / "df_final.csv",
        usecols=["Alpha-3 code", "CountryName"],
        engine="python",
        encoding="utf-8-sig",
    )
    country_names = (
        country_names.dropna(subset=["Alpha-3 code", "CountryName"])
        .drop_duplicates(subset=["Alpha-3 code"])
    )
    return country_names.rename(columns={"CountryName": "Country"})
