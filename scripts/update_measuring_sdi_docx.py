from __future__ import annotations

import csv
import json
import shutil
import tempfile
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from docx import Document
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph


PROJECT_DIR = Path(__file__).resolve().parents[1]
DOCX_PATH = PROJECT_DIR / "manuscript" / "Measuring_SDI_v5.docx"
TABLE_DIR = Path("/private/tmp/sdi_doc_update_tables")


def read_csv_table(name: str) -> list[list[str]]:
    with (TABLE_DIR / name).open(newline="", encoding="utf-8-sig") as f:
        return [[str(value) for value in row] for row in csv.reader(f)]


def set_paragraph(paragraph, text: str) -> None:
    paragraph.text = text


def insert_paragraph_after(paragraph, text: str) -> Paragraph:
    new_p = OxmlElement("w:p")
    paragraph._p.addnext(new_p)
    new_paragraph = Paragraph(new_p, paragraph._parent)
    new_paragraph.style = paragraph.style
    new_paragraph.text = text
    return new_paragraph


def ensure_method_references(document: Document) -> None:
    references = [
        "OECD and Joint Research Centre-European Commission. (2008). Handbook on Constructing Composite Indicators: Methodology and User Guide. OECD Publishing. https://doi.org/10.1787/9789264043466-en",
        "Transparency International. (2024). Corruption Perceptions Index 2024: Technical Methodology. Transparency International. https://www.transparency.org/en/cpi/2024",
        "WIPO. (2024). Global Innovation Index 2024: Appendix I: Conceptual and measurement framework. World Intellectual Property Organization. https://www.wipo.int/web-publications/global-innovation-index-2024/en/appendix-i-conceptual-and-measurement-framework-of-the-global-innovation-index.html",
    ]
    existing_text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    anchor = next(paragraph for paragraph in reversed(document.paragraphs) if paragraph.text.strip())
    for reference in references:
        if reference not in existing_text:
            anchor = insert_paragraph_after(anchor, reference)


def set_table(table, rows: list[list[str]]) -> None:
    while len(table.rows) > len(rows):
        table._tbl.remove(table.rows[-1]._tr)
    while len(table.rows) < len(rows):
        table.add_row()
    for r_idx, row in enumerate(rows):
        if len(row) != len(table.columns):
            raise ValueError(
                f"Column mismatch for table: expected {len(table.columns)}, got {len(row)}"
            )
        for c_idx, value in enumerate(row):
            table.cell(r_idx, c_idx).text = value


def replace_table(document: Document, table, rows: list[list[str]]) -> None:
    """Replace a table so stale merged-cell layout cannot shift the data."""
    if not rows:
        return
    old_tbl = table._tbl
    parent = old_tbl.getparent()
    index = parent.index(old_tbl)

    new_table = document.add_table(rows=len(rows), cols=len(rows[0]))
    new_table.style = table.style
    new_table.alignment = table.alignment
    new_table.autofit = True
    set_table(new_table, rows)

    parent.insert(index, new_table._tbl)
    parent.remove(old_tbl)


def update_media(docx_path: Path) -> None:
    replacements = {
        "word/media/image1.png": PROJECT_DIR
        / "figures"
        / "distribution_graphs"
        / "comprehensive_sustainable_development_kde.png",
        "word/media/image2.png": PROJECT_DIR
        / "figures"
        / "distribution_graphs"
        / "subsystem_mean_scores_2001_2021.png",
        "word/media/image3.png": PROJECT_DIR
        / "figures"
        / "geographical_graphs"
        / "SDI_spatial_distribution.png",
    }
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp_path = Path(tmp.name)

    with ZipFile(docx_path, "r") as zin, ZipFile(tmp_path, "w", ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename in replacements:
                zout.writestr(item, replacements[item.filename].read_bytes())
            else:
                zout.writestr(item, zin.read(item.filename))
    shutil.move(tmp_path, docx_path)


def main() -> None:
    facts = json.loads((TABLE_DIR / "facts.json").read_text(encoding="utf-8"))
    doc = Document(DOCX_PATH)

    paragraph_updates = {
        17: (
            "Between 2001 and 2021, Sub-Saharan Africa (SSA) recorded rapid gains in "
            "electrification, mobile connectivity, and health outcomes, yet many countries "
            "simultaneously experienced weak economic sustainability, resource pressures "
            "deepened, and ecological gains reflected conservation commitments more than "
            "reduced extraction pressure. The divergence of social progress coexisting with "
            "economic fragility and mounting resource pressure is difficult to detect with "
            "existing frameworks, which are either too data-intensive for long-run country "
            "comparison in SSA or too narrow to capture multidimensional dynamics. This paper "
            "develops a region-adapted composite sustainable development index (SDI) for 45 SSA "
            "countries over 2001-2021 using a four-dimensional framework of economic, social, "
            "resource, and ecological sustainability, screened to 34 indicators across 13 "
            "secondary dimensions. A two-stage Criteria Importance Through Intercriteria "
            "Correlation (CRITIC) weighting procedure assigns equal first-level weights and "
            "objective within-dimension weights. Kernel density estimation, geographic "
            "information system (GIS)-based mapping, a four-dimension equal-weight sensitivity test, "
            "and a single-stage CRITIC sensitivity test "
            "address temporal dynamics, spatial differentiation, and robustness. The results "
            "confirm and quantify the divergence: social sustainability improved by 60.8% on "
            "average and all 45 countries gained; economic sustainability rose by only 3.7% "
            "and declined in 16 countries; resource sustainability advanced by only 1.3% while "
            "19 countries declined and cross-country dispersion widened modestly; ecological "
            "sustainability improved moderately, concentrated in conservation indicators. "
            "These findings provide a region-sensitive measurement framework for long-run "
            "comparison and an empirical foundation for research on the structural drivers of "
            "sustainability in SSA."
        ),
        34: (
            "This study focuses on 45 countries in Sub-Saharan Africa from 2001 to 2021. The "
            "sample is determined by data availability and cross-country comparability. Data "
            "are drawn mainly from the World Bank World Development Indicators (WDI), the Yale "
            "Environmental Performance Index (EPI), the Food and Agriculture Organization "
            "(FAO), the U.S. Energy Information Administration (EIA), and the IMF Climate "
            "Change Dashboard. Missing values are interpolated linearly. To improve "
            "transparency, Appendix Table A1 reports the missing-value ratio, interpolation "
            "share, and final missing ratio after interpolation by indicator, and Appendix "
            "Table A2 reports the countries with the largest data gaps. Across the final "
            "34-indicator panel, the raw missing rate is 2.51%, the interpolation share is "
            "1.04%, and the remaining missing rate after interpolation is 1.47%. Any residual "
            "missing values after interpolation are excluded from aggregation, and the "
            "indicator weights are rescaled over the available indicators within each "
            "country-year observation, consistent with composite-indicator guidance and "
            "the treatment of missing values in other cross-country index systems (OECD "
            "and JRC, 2008; WIPO, 2024; Transparency International, 2024). Country-year observations are retained for SDI "
            "comparison only if at least 80% of the final indicators are available after "
            "interpolation; all 945 country-year observations meet this threshold."
        ),
        39: (
            "Indicators are then screened in two steps after data-coverage and conceptual "
            "checks of the candidate pool. Indicators with insufficient long-run country-year "
            "coverage are not retained in the final panel; in particular, gross fixed capital "
            "formation is excluded because its missingness is too high for a balanced "
            "2001-2021 comparison across SSA. Agricultural land and arable land shares are "
            "also excluded because they measure land availability rather than sustainable "
            "resource use. First, the coefficient of variation (CV) is computed for each "
            "candidate indicator, and indicators with a CV below 0.25 are removed for "
            "insufficient discriminatory power. Second, variance inflation factors (VIFs) are "
            "computed within each first-level dimension. The indicator with the highest VIF "
            "is dropped if it exceeds the threshold of 7.5, and the procedure repeats "
            "iteratively until all remaining indicators within the dimension satisfy VIF <= "
            "7.5. The final indicator system retains 34 third-level indicators grouped into "
            "13 second-level sub-dimensions and 4 first-level dimensions."
        ),
        46: (
            "The study adopts a two-stage procedure to determine dimension-level and "
            "indicator-level weights separately. At the first stage, the four first-level "
            "dimensions are assigned equal weights of 25% each. This reflects the conceptual "
            "design of the framework: each dimension captures a distinct and equally important "
            "facet of sustainability, and their relative importance should not be determined "
            "by how much the underlying indicators happen to vary across countries. If CRITIC "
            "were applied in a single stage across all 34 indicators, a dimension whose "
            "indicators happen to vary more across countries would automatically receive more "
            "weight in the composite score, even if it is not conceptually more important than "
            "the others. At the second stage, the CRITIC method is applied separately within "
            "each dimension to derive objective within-dimension weights based on each "
            "indicator's discriminatory power and its correlation with other indicators in "
            "the same dimension. When constructing the weights of the CRITIC, this paper "
            "adopts the absolute value of the correlation coefficient because whether the "
            "indicators show a significant positive correlation or a significant negative "
            "correlation, it indicates that there is a high degree of information overlap. "
            "Therefore, its marginal weight in the comprehensive evaluation should be reduced. "
            "The CRITIC weights are estimated on the pooled country-year panel for 45 SSA "
            "countries over 2001-2021, rather than separately by year. After pooled min-max "
            "normalization, both the correlation matrix and the standard deviations used in "
            "CRITIC are computed from all available country-year observations, so the resulting "
            "weights are fixed over the full study period and applied consistently to all "
            "countries and years. When residual missing values remain after interpolation, "
            "the fixed weights are rescaled over the available indicators within the relevant "
            "country-year observation rather than being re-estimated."
        ),
        53: (
            "All indicators are standardized using min-max normalization, with separate "
            "treatment for positive and negative indicators. The normalization is based on "
            "the pooled country-year sample for 2001-2021 rather than being performed "
            "separately by year, so each indicator is transformed using a single minimum and "
            "maximum over the full panel. This preserves intertemporal comparability of "
            "country scores. The composite sustainable development score for country k in "
            "year t is then given by:"
        ),
        56: (
            "In addition, two sensitivity specifications are used to examine whether the main "
            "findings depend strongly on the weighting design. The first is a four-dimension "
            "equal-weight specification, in which each first-level dimension receives 25% of "
            "the composite score and indicators within each dimension are weighted equally. "
            "The second is a single-stage CRITIC specification, in which CRITIC weights are "
            "estimated across all 34 indicators at once rather than within dimensions."
        ),
        59: (
            "The composite sustainable development index (SDI) shows clear and consistent "
            "upward movement across SSA over the two-decade study period. The regional mean "
            "score rose from 40.22 in 2001 to 46.78 in 2021, an increase of 16.31%, and 44 of "
            "the 45 sample countries recorded a net improvement in their composite score. "
            "Only Equatorial Guinea experienced a net decline over the full period, with its "
            "composite score falling by 6.6% between 2001 and 2021."
        ),
        60: (
            "Yet aggregate progress conceals substantial cross-country variation in pace and "
            "trajectory. By 2021, the highest composite scores were concentrated among island, "
            "Central, and Southern African economies: Seychelles (62.8), Gabon (57.5), Namibia (56.7), "
            "Botswana (55.1), and Mauritius (54.0) led the regional distribution. At the lower "
            "end, Burundi (38.1), the Democratic Republic of the Congo (38.6), Liberia (39.6), "
            "the Central African Republic (39.7), and Eritrea (39.9) remained well below the "
            "regional mean. In terms of absolute gains, Djibouti, South Africa, Guinea, Namibia, "
            "Comoros, Seychelles, and Ethiopia recorded comparatively rapid improvements. Nevertheless, several "
            "fast-improving countries still scored below the regional leaders in 2021, "
            "suggesting that cross-country gaps remain substantial."
        ),
        61: (
            "The kernel density plots reveal how the country-score distribution evolved over "
            "the study period (Figure 1). The distribution shifted steadily to the right, while "
            "its spread remained persistent, indicating that overall progress was accompanied "
            "by limited convergence across countries. A group of higher-performing countries "
            "pulled ahead while a cluster of lower-performing countries remained behind, yet "
            "the distribution retained its broadly unimodal shape throughout, suggesting no "
            "sharp structural break between country groups. The ratio between the highest and "
            "lowest national scores was 1.54:1 in 2001 and 1.65:1 in 2021, indicating that "
            "cross-country disparities in composite sustainable development have proven "
            "highly persistent. Progress was widespread but not strongly equalizing."
        ),
        63: "Figure 1. Kernel density of composite sustainable development scores, 2001-2021.",
        72: (
            "Economic sustainability was the weakest subsystem at the start of the period and "
            "remained so throughout. The regional mean rose only from 30.70 in 2001 to 31.83 "
            "in 2021, with a gain of 3.7% over two decades, compared with 16.31% for the "
            "composite index. Of greater concern, 16 of the 45 sample countries experienced a "
            "net decline in their economic sustainability scores, including several that "
            "improved substantially in the social and ecological dimensions. Key drivers of "
            "underperformance include weak per capita GDP growth, unstable external balances, "
            "inflation instability, and uneven industrial value added, which signal not merely "
            "slow growth but a fragile and potentially unsustainable development trajectory. Cross-country "
            "inequality in economic sustainability narrowed only modestly, with the ratio of "
            "the highest to the lowest score falling from 4.16:1 to 3.57:1."
        ),
        73: (
            "Social sustainability tells a sharply contrasting story. The regional mean climbed "
            "from 31.91 in 2001 to 51.29 in 2021, an increase of 60.8% and by far the largest "
            "gain of any subsystem, and all 45 sample countries recorded improvements. The gains "
            "were driven primarily by access-related indicators: mobile cellular subscriptions, "
            "internet penetration, electrification rates, health-related indicators, and gender "
            "equality indicators all moved strongly in a positive direction across most of the "
            "region. The ratio between the highest and lowest national social scores narrowed "
            "substantially, from 3.33:1 to 2.08:1, indicating genuine regional catch-up. By 2021, "
            "social sustainability had overtaken economic sustainability but remained below "
            "resource and ecological sustainability on average, reversing its position as one of "
            "the two weakest dimensions at the start of the period."
        ),
        74: (
            "Resource sustainability improved only marginally over the study period, rising "
            "from 50.64 to 51.29, with a gain of 1.3%. Nineteen of the 45 countries experienced "
            "a net decline, and the ratio between the highest and lowest resource scores "
            "increased from 1.63:1 to 1.70:1, making resource sustainability the subsystem "
            "with the weakest overall improvement and modestly worsening dispersion. This "
            "pattern reflects the combined pressure of freshwater resource depletion, rising "
            "mineral extraction intensities as a share of national income, and limited "
            "progress in energy efficiency and diversification. Declining renewable freshwater "
            "resources per capita across countries with available data contributed further to "
            "this outcome."
        ),
        79: (
            "In overall terms, Southern Africa remained one of the stronger subregions, but the "
            "2021 country ranking also placed Seychelles at the top of the distribution, followed "
            "by Gabon, Namibia, Botswana, and Mauritius (Figure 3). Lower scores remained "
            "concentrated among fragile and lower-income countries, including Burundi, "
            "the Democratic Republic of the Congo, Liberia, the Central African Republic, and Eritrea. "
            "Even where individual country rankings shifted, the broad spatial hierarchy "
            "between higher-performing Southern/coastal economies and lower-performing inland "
            "or fragile economies remained visible throughout the study period."
        ),
        81: (
            "The strongest positive shifts were concentrated in social and ecological indicators: "
            "mobile cellular subscriptions, internet penetration, electrification access, "
            "gender equality indicators, terrestrial biome protection, and species protection "
            "all recorded widespread improvement. Gains in scientific publication output and "
            "selected clean-energy variables were also visible. By contrast, a cluster of "
            "indicators deteriorated broadly across SSA: mineral depletion as a share of GNI, "
            "renewable internal freshwater resources per capita, forest area share, CO2 "
            "emissions per capita, and energy consumption per capita all worsened across many "
            "countries. These patterns confirm that recent progress in SSA has been "
            "disproportionately anchored in basic service expansion and formal conservation "
            "commitments, while the underlying productive structure, resource extraction "
            "trajectory, and natural capital base have remained under pressure."
        ),
        86: (
            "The main findings are robust to alternative weighting specifications. The "
            "four-dimension equal-weight specification has a Spearman rank correlation of "
            "0.992 with the two-stage CRITIC index across all country-year observations and "
            "0.989 in 2021. The single-stage CRITIC specification is also strongly correlated "
            "with the main index, with Spearman correlations of 0.955 across all country-year "
            "observations and 0.940 in 2021. Nine of the top ten and nine of the bottom ten "
            "countries in 2021 are identical under both sensitivity specifications (Table 4). "
            "The results therefore indicate that overall improvement, subsystem divergence, "
            "spatial differentiation, and the broad stability of high- and low-performing "
            "country groups are not artifacts of the weighting procedure, even though the "
            "single-stage CRITIC specification produces larger rank shifts than the "
            "four-dimension equal-weight specification."
        ),
        87: (
            "Table 4. Sensitivity test: main index versus alternative weighting specifications, "
            "selected years"
        ),
        89: (
            "Sub-Saharan countries' aggregate improvement over 2001-2021 is real, but the "
            "6.56-point gain in the composite SDI obscures more than it reveals. Social "
            "sustainability accounted for more than 70% of that improvement, while the "
            "economic subsystem contributed only 0.40 points to the composite gain. This "
            "compositional imbalance echoes earlier evidence of structural fragility in SSA's "
            "development trajectory (Bissoon, 2017). Equatorial Guinea illustrates this "
            "pattern as the only country whose composite SDI declined over the two decades, "
            "driven primarily by a sharp deterioration in economic sustainability even as "
            "social sustainability improved substantially."
        ),
        91: (
            "Economic indicators present a more troubling picture. Per capita value added in "
            "services and agriculture rose across most countries, but industry value added per "
            "worker declined in 17 of the 42 countries with both endpoint observations and the "
            "regional mean fell, consistent with the broader stagnation of manufacturing "
            "productivity in developing economies (Kruse et al., 2023). Current account "
            "balances deteriorated in 22 of 41 countries with both endpoint observations, and "
            "goods exports declined in 20 of 45 countries. Taken together with the limited "
            "industrial base noted above, these patterns suggest that growth over the past two "
            "decades has rested largely on commodity exports. The structural fragility "
            "produced by resource dependence is well documented (Corden, 1984): economies "
            "without a diversified production base have limited capacity to absorb shocks when "
            "commodity cycles turn."
        ),
        92: (
            "The resource dimension presents a more differentiated pattern than the economic "
            "dimension. Improvements in water productivity, energy intensity, and selected "
            "renewable energy capacity mark the early stages of an efficiency transition. "
            "Alongside these improvements, however, mineral depletion rose sharply, with the "
            "regional mean increasing by roughly sixteen times, and per capita renewable "
            "freshwater declined in all 44 countries with both endpoint observations. The "
            "former reinforces the resource-dependence concern raised in the economic "
            "dimension, while the latter reflects population pressure. This divergence "
            "indicates that efficiency improvement and extractive pressure are evolving on "
            "separate tracks, and aggregate sustainability scores may mask the trade-off "
            "between them."
        ),
        93: (
            "The ecological dimension shows a clear structural split: formal protection "
            "indicators have improved significantly, while ecological conditions and pollution "
            "pressure have not. Terrestrial biome conservation and species protection indices "
            "improved in every country with available data, indicating that the institutional "
            "framework for ecological protection has been widely strengthened. However, the "
            "share of forest area declined in 38 out of 45 countries, and per capita carbon "
            "dioxide emissions rose in 34 out of 45 countries. Anthropogenic PM2.5 exposure eased slightly, "
            "but the improvement is concentrated in a few countries rather than across the "
            "region. The gap between formal protection and actual ecological outcomes echoes "
            "a long-standing concern in the literature: institutional improvements do not "
            "necessarily translate into measurable ecological change. Together with the "
            "economic and resource dimensions, this pattern suggests that institutional "
            "progress in sub-Saharan Africa has outpaced the material conditions it is "
            "intended to govern. Middle Africa shows this pattern most sharply. It was the "
            "only subregion with a negative average change in both the economic and resource "
            "subsystems, yet it recorded the largest improvement in the ecological subsystem "
            "of any subregion. Formal protection indicators can advance independently of the "
            "economic and resource pressures that constrain the same countries."
        ),
        95: (
            "The pandemic in 2020 affected the economic subsystem most sharply, yet the "
            "composite SDI did not decline because gains in social sustainability offset the "
            "economic drag. The social index rose by roughly 1.69 points on average (+0.42 to "
            "the composite), more than compensating for the -0.13 contribution from economic "
            "deterioration. Economic subsystem scores fell in 33 of 45 countries, driven "
            "primarily by contractions in per capita GDP growth, alongside declines in export "
            "performance, inflation stability, and industrial value added. The shock was "
            "uneven: economies with concentrated exposure to tourism "
            "(Cape Verde, Mauritius), resource rents (Equatorial Guinea), or macroeconomic "
            "fragility (Zimbabwe) recorded the steepest declines, consistent with the "
            "structural fragility argument developed above."
        ),
        96: (
            "One data limitation is worth noting. For a small number of countries, particularly "
            "Eritrea, Seychelles, Djibouti, Equatorial Guinea, and Sao Tome and Principe, "
            "endpoint values are comparatively sparse for some indicators, so part of the "
            "measured change may reflect improved data availability rather than substantive "
            "improvement. The regional-level conclusions are unaffected; for countries with "
            "larger endpoint gaps, trend readings should be treated as indicative rather than "
            "definitive."
        ),
        97: (
            "The weighting scheme raises a related concern. The two-stage CRITIC procedure "
            "determines weights objectively from the data, but the four-dimension equal-weight "
            "and single-stage CRITIC sensitivity tests confirm that the main findings are not "
            "artifacts of the chosen weights. The comparison is also informative: the "
            "single-stage CRITIC index remains strongly correlated with the main index, but "
            "its larger rank shifts show why the two-stage design is useful for preserving "
            "the conceptual balance among economic, social, resource, and ecological "
            "dimensions. "
            "Nevertheless, any composite index reflects implicit normative choices: the "
            "decision to assign equal weight to the four first-level dimensions, for instance, "
            "embeds a specific assumption about the relative importance of economic, social, "
            "resource, and ecological sustainability. Analysts with different prior judgements "
            "about dimensional importance would arrive at different country rankings, and this "
            "subjectivity is an inherent feature of any composite index, not unique to the one "
            "developed here."
        ),
        100: (
            "SSA's sustainable development record over 2001-2021 is genuine but uneven in "
            "ways that aggregate progress measures tend to obscure. The regional mean SDI "
            "rose by 16.31 percent, and 44 of 45 countries improved on the composite index. "
            "But social sustainability drove most of that movement, rising 60.8 percent "
            "across all countries, while economic sustainability rose by only 3.7 percent "
            "and declined in 16 countries. Resource sustainability barely advanced, rising "
            "only 1.3 percent, and declined in 19 countries. Ecological sustainability "
            "improved, but through conservation commitments rather than reduced extraction "
            "pressure. Closer inspection reveals a story of one subsystem advancing while "
            "the others stagnated or fell behind."
        ),
        102: (
            "The resource and ecological findings add a further layer. Formal conservation "
            "advanced significantly, with terrestrial protection and species indices improving "
            "in nearly all countries. Yet freshwater availability declined in all 44 countries "
            "with both endpoint observations, forest cover fell in 38 of 45 countries, and "
            "energy consumption per capita worsened in 34 countries. Conservation commitments "
            "and resource trajectories pulled in opposite directions, a distinction that "
            "collapses when resource and ecological sustainability are treated as a single "
            "environmental dimension. Separating them, as the index developed here does, is "
            "not a methodological preference but a substantive necessity."
        ),
        103: (
            "Spatial patterns reinforce the interpretation. The subregional hierarchy remained "
            "structurally stable across the full two decades, even though Seychelles moved to the "
            "top of the 2021 country ranking. Middle Africa was the only subregion to record "
            "negative average change in both the economic and resource subsystems, despite "
            "posting the largest ecological gains. Conservation commitments advanced "
            "independently of the productive and resource pressures bearing down on these "
            "same economies."
        ),
        105: (
            "The index developed here is highly correlated with both the four-dimension "
            "equal-weight and single-stage CRITIC sensitivity specifications, which confirms "
            "that the main findings are not driven by the weighting scheme. But the more "
            "important methodological point is that how "
            "SSA's sustainability is measured shapes what can be seen. Aggregating across "
            "dimensions or collapsing resource and ecological sustainability into a single "
            "environmental score would have hidden the divergence that is the central finding "
            "of this paper."
        ),
        108: (
            "The missing-data diagnostics are calculated for the final 34-indicator panel "
            "covering 45 SSA countries from 2001 to 2021. The denominator is therefore 945 "
            "country-year observations for each indicator. Linear interpolation is applied "
            "within countries and indicators when sufficient observed values are available. "
            "After interpolation, residual missing values are excluded from aggregation and "
            "the indicator weights are rescaled over the available indicators within each "
            "country-year observation. A country-year observation is retained for SDI "
            "comparison only if at least 80% of indicators are available. The minimum "
            "post-interpolation coverage is 28 out of 34 indicators, or 82.35%, so no "
            "country-year observation is excluded by this threshold. All indicators are "
            "then standardized using pooled min-max normalization over the full 2001-2021 "
            "sample, rather than year-specific normalization, to preserve temporal "
            "comparability."
        ),
    }

    for idx, text in paragraph_updates.items():
        set_paragraph(doc.paragraphs[idx], text)

    table_files = [
        "table1_final_indicator_system.csv",
        "table2_sdi_scores.csv",
        "table3_subsystem_summary.csv",
        "table4_sensitivity.csv",
        "tableA1_missing_by_indicator.csv",
        "tableA2_missing_by_country.csv",
        "tableB_country_rankings.csv",
        "tableC_indicator_weights.csv",
    ]
    for table, file_name in zip(list(doc.tables), table_files):
        replace_table(doc, table, read_csv_table(file_name))

    ensure_method_references(doc)
    doc.save(DOCX_PATH)
    update_media(DOCX_PATH)
    print(f"Updated {DOCX_PATH}")


if __name__ == "__main__":
    main()
