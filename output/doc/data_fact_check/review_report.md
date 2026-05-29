# Data and Fact Check Report

Document checked: `/Users/hanyu/Documents/GitHub/ssa-sdi/Measuring_SDI_revised.docx`

Checked against local project files:

- `index_data_two_stage_comparison.csv`
- `index_data.csv`
- `scaled_data.xlsx`
- `selected_indicator_system_variables.xlsx`
- `appendix_missing_data_by_indicator.csv`
- `appendix_missing_data_by_country.csv`
- `critic_weight_two_stage.csv`
- `sensitivity_equal_weight_table.csv`
- `variable_source_dict.csv`
- extracted DOCX tables and paragraphs in this folder

External sources spot-checked:

- UN M49 regional classification: https://unstats.un.org/unsd/methodology/m49/
- UN 2030 Agenda / SDGs: https://sdgs.un.org/2030agenda
- CSD indicator framework references, including the 2007 third edition indicator framework: https://sdgs.un.org/sites/default/files/documents/1470Background_paper_final.pdf
- Africa SDG Index and Dashboards reports: https://www.sustainabledevelopment.report/reports/africa-sdg-index-and-dashboards-2018/ and https://www.sustainabledevelopment.report/reports/2019-africa-sdg-index-and-dashboards-report/
- Dodoo et al. 2025 article metadata: https://link.springer.com/article/10.1007/s43621-025-02079-8

## Overall Assessment

The core empirical results in the manuscript are largely consistent with the local calculation files. The main SDI numbers, country counts, missing-data rates, coverage threshold, rank overlaps, and Spearman correlations are reproducible from the project data.

The main problems are not the headline SDI calculations, but several factual/metadata issues:

1. Some final indicator labels and units do not match the actual variables used in the data.
2. A few literature-history statements appear to mix up years, versions, or country coverage.
3. Some narrative claims about which indicators "broadly deteriorated" are stronger than the 2001-2021 indicator-level data supports.
4. A few references and citations contain likely spelling, year, or DOI errors.

## High-Priority Corrections

### P027: Africa SDG Index country coverage

Current claim:

> 2018 Africa SDG Index and Dashboards Report covered only 11 countries; 2019 and 2020 covered 52 African countries.

Issue:

This appears inaccurate or at least misleading. The 2018 Africa SDG Index and Dashboards Report is not best described as covering only 11 countries. The "11 countries" figure may refer to a separate implementation/readiness analysis or subset, not the overall Africa SDG Index country coverage. Recheck the report text and revise the sentence.

Suggested direction:

Use a more cautious formulation, for example: "Although the Africa SDG Index reports expanded country benchmarking for the continent, severe data gaps remained for several indicators/countries..." Then cite the exact country count from each report after checking the PDFs.

### P023: CSD/MDG indicator framework chronology and counts

Current claim:

> 2003 CSD designed a framework with 14 themes and 96 indicators; 2005 MDGs included 8 goals, 21 targets, and 60 indicators.

Issue:

The CSD 14-theme/96-indicator framework corresponds to the later CSD indicator framework commonly associated with the third edition, not clearly to 2003. The MDG count also needs chronology checking: the original MDG framework used fewer targets/indicators, while the 21-target/60-indicator list is associated with the revised framework.

Suggested direction:

Revise by version rather than using a single year: e.g. "The revised CSD framework later organized indicators under 14 themes..." and "The MDG monitoring framework was later revised to 21 targets and 60 indicators..."

### P032: UN geoscheme wording

Current claim:

> According to the United Nations geoscheme, SSA countries are assigned to Southern, Western, Eastern, and Central Africa.

Issue:

UN M49 uses "Middle Africa", not "Central Africa", as the formal subregion name. "Central Africa" is understandable, but if the sentence says "According to the United Nations geoscheme", it should use the UN wording or explicitly say the paper renames Middle Africa as Central Africa.

Suggested correction:

"According to the United Nations M49 geoscheme, SSA countries are grouped into Eastern, Middle (Central), Southern, and Western Africa; North Africa is excluded from the study sample."

### Table 1 / Table C: Life expectancy variable does not match label

Current table label:

> Life expectancy at birth (years)

Actual selected variable:

> `Life expectancy at birth, total (years)_pct_change`

Issue:

The manuscript describes C11 as the level of life expectancy, but the actual variable is the percentage change in life expectancy. This changes the interpretation materially. A country can have high life expectancy but low percentage growth, or low life expectancy but high growth.

Suggested correction:

Either replace the data column with the level variable, or rename C11 throughout as "Growth in life expectancy at birth" / "Percentage change in life expectancy at birth" and adjust the description and interpretation of social-sustainability health gains.

### Table 1 / Table C: Energy variable units do not match actual data

Current table labels:

- C27 Energy consumption per capita (kg of oil equivalent)
- C28 Solar, tidal, wave, and fuel-cell electricity capacity per capita (kW)
- C29 Biomass and waste electricity net generation per capita (kWh)

Actual selected variables:

- `Energy consumption per capita (million Btu per person)`
- `Solar, tide, wave, fuel cell electricity installed capacity (million kilowatts)_per_capita`
- `Biomass and waste electricity net generation (million metric tons of oil equivalent)_per_capita`

Issue:

The table gives different units from the data columns. This is a factual metadata problem and should be corrected before submission.

Suggested correction:

Use the exact units from the source variables, or document any conversion if one was performed.

### Table C / source metadata: Grassland source appears inconsistent

Current source in Table C:

> Yale EPI

Local source dictionary / notebook trail:

> IMF Climate Change Indicators / land cover account source appears to be the source for grassland-style land cover data.

Issue:

`Grassland area (% of land area)` is listed as Yale EPI in the selected-indicator metadata, but local source tracing points to IMF-CID land-cover data. Recheck and correct the source entry. If it is constructed from IMF-CID land-cover accounts, Table C should not list Yale EPI.

### P067 and P075: "broad deterioration" is overstated for some indicators

Local 2001-2021 normalized-score check:

- Merchandise export share: 25 countries improved, 20 declined.
- Industrial value added per worker: 25 improved, 17 declined.
- Current account balance score: 19 improved, 22 declined.
- Biomass and waste electricity generation per capita: 21 improved, 8 declined, 16 unchanged.

Issue:

The text says these indicators "deteriorated most broadly" or "all declined across many countries". That is well supported for renewable freshwater per capita, forest area, CO2 emissions, grassland, and mineral depletion, but not for merchandise exports, industrial labor productivity, or biomass/waste electricity.

Suggested correction:

Narrow the statement: "A subset of indicators deteriorated broadly, especially renewable freshwater resources per capita, forest area share, CO2 emissions per capita, grassland area, and mineral depletion. Other economic indicators showed mixed country-level changes but contributed to weak aggregate performance."

### P081 / Reference P108: Dodoo et al. DOI likely wrong

Current reference:

> https://doi.org/10.1007/s43621-025-01426-5

Issue:

The searched article metadata for "Revisiting sustainable development in Africa through a national economic environmental social and governance perspective" points to a different DOI/article metadata than the DOI currently listed. Recheck the exact article page and replace the DOI.

## Paragraph-by-Paragraph Notes

| Paragraph | Status | Check result |
|---|---|---|
| P009 | Clarify | Data availability lists WDI, EPI, FAO, Global Data Lab, EIA, IMF climate database, and WIID. The final 37-indicator set no longer uses Global Data Lab or WIID, although they appear in the candidate pool. If referring to final data, remove them; if referring to candidate data, say so. |
| P014 | Mostly verified | 45 countries, 2001-2021, 37 indicators, 13 sub-dimensions, two-stage CRITIC, social +60.6%, economic +6.8%, economic decline in 19 countries all match local data. "Health outcomes" should be used carefully because the life-expectancy indicator is currently a percentage-change variable. |
| P017 | Plausible | Main historical dates are plausible, but references to Silent Spring, Limits to Growth, Stockholm, and World Conservation Strategy should be cited in the reference list if retained. |
| P018 | Mostly verified | Brundtland definition and 17 SDGs are correct. The 2002 Johannesburg "establishing pillars" wording may be stronger than necessary; consider "reaffirming" or "emphasizing" the three pillars. |
| P019 | Needs citation check | "Over 100 definitions since 1980" needs a direct source. The named authors are plausible but several are not in the current reference list. |
| P020 | Conceptual | No numeric issue; this is a theoretical framing paragraph. |
| P021 | Conceptual | Chinese paragraph; no direct data issue. |
| P022 | Needs citation cleanup | PSR/DSR/DPSIR chronology broadly plausible, but CSD-UNDESA, Smeets & Wetering, and OECD citations should appear in the references. |
| P023 | Revise | CSD/MDG years and counts need correction as noted above. Also "Sach et al." should be "Sachs et al." |
| P024 | Needs citation check | World Bank wealth/genuine savings description is broadly plausible; check "O'Connor (1995)" attribution and "IDWI" abbreviation, which may be nonstandard compared with "IWI". |
| P025 | Needs citation cleanup | "Sach et al." should be "Sachs et al."; references to Zafar et al. and Ahmed et al. are not currently in the reference list. |
| P026 | Plausible but broad | No local-data issue; consider adding citations for HDI, SSI, EPI, ecological footprint, eco-efficiency claims. |
| P027 | Revise | Africa SDG Index coverage claim likely inaccurate; "Nhemachenael al." typo should be "Nhemachena et al."; Bartniczak citation year should align with the reference list, likely 2019. |
| P028 | Plausible | No local-data issue; "可持续 发展" contains an extra space. |
| P031 | Verified with caveat | 45 countries, 21 years, 945 observations, 37 indicators, missing rates 2.73% / 1.09% / 1.65%, and 80% coverage threshold all match local files. Caveat: final 37-indicator set does not use GDL or WIID. |
| P032 | Revise wording | Use "Middle (Central) Africa" if citing UN M49. |
| P034 | Verified | Four dimensions, 13 second-level dimensions, and initial 44 third-level indicators match local candidate/final files. There is a stray comma after "Africa, ,". |
| P035 | Mostly ok | Indicator examples are present, but C28/C29 units need correction as above. |
| P036 | Verified | CV/VIF screening claim is consistent with 44 candidate indicators to 37 final indicators. |
| P039-P049 | Mostly verified | Two-stage CRITIC method, 25% first-level weights, within-dimension CRITIC weights, min-max normalization, and equal-weight sensitivity check match local data. |
| P052 | Verified | Mean SDI 39.38 to 46.46, +17.99%, 44 improved, Equatorial Guinea -0.6% all match local data. |
| P053 | Verified | 2021 top five and bottom five country scores match local data after rounding. |
| P054 | Verified | Highest/lowest score ratios 1.65:1 to 1.60:1 match local data. |
| P059 | Mostly verified | Economic means, +6.8%, 19 declines, and ratios match local data. However, "weak industrial value added per worker" as a broad deterioration driver should be softened because 25 countries improved and 17 declined on the normalized industrial labor productivity indicator. |
| P060 | Verified | Social means, +60.6%, 45 improved, and ratios match local data. |
| P061 | Mostly verified | Resource means, +4.7%, 14 declines, and ratios match local data. Biomass/waste electricity wording should be softened because only 8 countries declined, while 21 improved and 16 were unchanged. |
| P062 | Verified | Ecological means, +10.7%, 39 improved, 6 declined, and ratios match local data. Forest, CO2, and grassland deterioration are supported. |
| P065 | Mostly verified | 2021 top cluster and lower Central African countries match local data. The claim that Southern Africa consistently had the highest regional average should be supported by a regional-average table or figure. |
| P066 | Plausible | Spatial interpretation is consistent with results but should be treated as interpretation unless regional averages by subsystem are reported. |
| P067 | Revise | Positive shifts are supported. Deterioration list should be narrowed; biomass/waste electricity and some economic indicators do not show broad country-level decline. |
| P070 | Verified | Spearman correlations 0.982 and 0.973, top-10 overlap 9/10, bottom-10 overlap 10/10 match local data. |
| P073 | Verified | Social >60%, economic <7%, and 19 economic declines match local data. |
| P074 | Interpretive | Access-based social gains are supported by internet, mobile, electricity, and gender indicators. Claims about aid/external financing need citation or softer wording. |
| P075 | Partly overstated | 19 economic declines verified. The listed deteriorating drivers are mixed; merchandise exports and industrial productivity do not decline in a majority of countries over 2001-2021. |
| P076 | Interpretive | No direct data error; structural-transformation claim needs supporting literature citation. |
| P077 | Mostly verified | Resource stagnation and widened resource disparity verified. "Reduce lead exposure" is problematic because lead exposure was removed from the final 37-indicator system. Remove or replace with PM2.5/CO2/other retained indicators. |
| P078 | Interpretive | Consistent with framework; claims about donor conservation finance need citation or softer wording. |
| P079 | Interpretive | Broadly plausible; institutional capacity/governance/landlockedness claims need citations if stated as causal. |
| P080 | Verified | Comprehensive ratio narrows marginally; social catch-up and resource widening are supported. |
| P081 | Needs reference correction | Bartniczak comparison broadly plausible; Dodoo et al. DOI/reference needs correction. |
| P082 | Interpretive | No local-data issue; claims about causal-literature measurement quality should be supported by citations. |
| P083 | Verified | Limitations are consistent with available data and methods. |
| P085 | Mostly verified | Summary matches results; "most rapid social improvements observed anywhere" is a broad comparative claim and needs external support or softer wording. |
| P086 | Verified | Regional mean +17.99%, 44/45 improved, social +60.6%, economic +6.8%, 19 declines all match local data. |
| P087 | Interpretive | Policy priorities are consistent with findings; financing-source claims need citation or softer wording. |
| P088 | Verified with caveat | Spearman 0.982 verified. "Official SDG scoreboards...not always adequate" is plausible but should cite Africa SDG data-gap discussion. |
| P091 | Verified | 37 indicators x 45 countries x 21 years = 945 observations per indicator; minimum coverage 30/37 = 81.08%; no country-year excluded. |
| Tables A1/A2 | Verified | Missing-data tables match local CSV files. |
| Table B | Verified | Country rankings and 2001/2021 scores match local data after rounding. |
| Table C | Needs metadata fixes | Weights match `critic_weight_two_stage.csv`, but life-expectancy label, energy units, biomass/waste unit, and grassland source need correction. |

## Local Calculation Checks

Key values reproduced from local data:

| Claim | Recalculated value |
|---|---:|
| Countries | 45 |
| Country-year observations | 945 |
| Final indicators | 37 |
| Mean SDI, 2001 | 39.38 |
| Mean SDI, 2021 | 46.46 |
| SDI growth | 17.99% |
| Countries with comprehensive SDI improvement | 44 |
| Countries with economic sustainability decline | 19 |
| Social sustainability growth | 60.55% |
| Economic sustainability growth | 6.75% |
| Resource sustainability growth | 4.73% |
| Ecological sustainability growth | 10.67% |
| Raw missing rate | 2.73% |
| Interpolation share | 1.09% |
| Final missing rate | 1.65% |
| Minimum post-interpolation coverage | 30/37 = 81.08% |
| Spearman, equal weight vs two-stage CRITIC, all observations | 0.982 |
| Spearman, equal weight vs two-stage CRITIC, 2021 | 0.973 |
