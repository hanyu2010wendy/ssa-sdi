from __future__ import annotations

from itertools import chain, pairwise
from pathlib import Path
import struct
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize
from matplotlib.patches import Patch, Polygon, Rectangle

warnings.filterwarnings("ignore")

PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = Path.home() / "OneDrive" / "Rawdata"
OUTPUT_DIR = PROJECT_DIR / "figures" / "geographical_graphs"
YEARS = (2001, 2008, 2015, 2021)
EXTENT = (-20, 55, -37, 40)

INDEX_COLUMNS = {
    "SDI": "SDI_TwoStage",
    "SDI_Economy": "SDI_Economy_TwoStage",
    "SDI_Society": "SDI_Society_TwoStage",
    "SDI_Resource": "SDI_Resource_TwoStage",
    "SDI_Ecology": "SDI_Ecology_TwoStage",
}

MAP_TITLES = {
    "SDI": "Sustainable Development Index",
    "SDI_Economy": "Economic Sustainability Index",
    "SDI_Society": "Social Sustainability Index",
    "SDI_Resource": "Resource Sustainability Index",
    "SDI_Ecology": "Ecological Sustainability Index",
}

# Keep one comparable classification system across the five maps.
MAP_BINS = [30, 35, 40, 45, 50, 55, 60, 65, 70, 75]


def decode_dbf_value(raw: bytes) -> str:
    raw = raw.strip()
    for encoding in ("utf-8", "gb18030", "gbk", "latin1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin1", errors="ignore")


def read_dbf(path: Path) -> list[dict[str, str]]:
    with path.open("rb") as f:
        header = f.read(32)
        record_count = struct.unpack("<I", header[4:8])[0]
        header_length = struct.unpack("<H", header[8:10])[0]
        record_length = struct.unpack("<H", header[10:12])[0]

        fields: list[tuple[str, int]] = []
        while True:
            descriptor = f.read(32)
            if descriptor[0] == 0x0D:
                break
            name = descriptor[:11].split(b"\x00", 1)[0].decode("ascii")
            fields.append((name, descriptor[16]))

        f.seek(header_length)
        records: list[dict[str, str]] = []
        for _ in range(record_count):
            record = f.read(record_length)
            if not record or record[:1] == b"*":
                continue
            cursor = 1
            row: dict[str, str] = {}
            for name, length in fields:
                row[name] = decode_dbf_value(record[cursor : cursor + length])
                cursor += length
            records.append(row)
    return records


def read_shp_polygons(path: Path) -> list[list[list[tuple[float, float]]]]:
    polygons: list[list[list[tuple[float, float]]]] = []
    with path.open("rb") as f:
        f.seek(100)
        while True:
            record_header = f.read(8)
            if len(record_header) < 8:
                break
            _, content_length_words = struct.unpack(">2i", record_header)
            content = f.read(content_length_words * 2)
            if len(content) < 4:
                break
            shape_type = struct.unpack("<i", content[:4])[0]
            if shape_type == 0:
                polygons.append([])
                continue
            if shape_type not in (5, 15, 25):
                polygons.append([])
                continue

            num_parts, num_points = struct.unpack("<2i", content[36:44])
            parts_offset = 44
            points_offset = parts_offset + 4 * num_parts
            parts = list(struct.unpack(f"<{num_parts}i", content[parts_offset:points_offset]))
            points = [
                struct.unpack("<2d", content[points_offset + 16 * i : points_offset + 16 * (i + 1)])
                for i in range(num_points)
            ]
            part_ends = parts[1:] + [num_points]
            polygons.append([points[start:end] for start, end in zip(parts, part_ends)])
    return polygons


def load_map_data() -> tuple[list[dict], pd.DataFrame]:
    shp_path = RAW_DIR / "Geographic Information Data" / "World map" / "world_std.shp"
    dbf_path = shp_path.with_suffix(".dbf")
    attributes = read_dbf(dbf_path)
    geometries = read_shp_polygons(shp_path)

    # Draw SSA countries from the project country-code file. Mauritania is in
    # UN M49 Western Africa, so it remains grey if absent from the SDI sample.
    countries = pd.read_excel(PROJECT_DIR / "Variables Chosen.xlsx", sheet_name="Countries")
    north_africa_codes = {"DZA", "EGY", "LBY", "MAR", "SDN", "TUN", "ESH"}
    non_country_territory_codes = {"ATF", "IOT", "MYT", "REU", "SHN"}
    research_codes = (
        set(countries["Alpha-3 code"].dropna().unique())
        - north_africa_codes
        - non_country_territory_codes
    )
    features = [
        {**row, "parts": parts}
        for row, parts in zip(attributes, geometries)
        if row.get("SOC") in research_codes
    ]

    index_data = pd.read_csv(PROJECT_DIR / "index_data_two_stage_comparison.csv")
    index_data = index_data[
        [
            "Alpha-3 code",
            "CountryName_CN",
            "Numeric",
            "Year",
            *INDEX_COLUMNS.values(),
        ]
    ].rename(columns={v: k for k, v in INDEX_COLUMNS.items()})
    index_data[list(INDEX_COLUMNS)] = index_data[list(INDEX_COLUMNS)] * 100
    return features, index_data


def plot_north_arrow(ax, xT: float = 42, yT: float = 24, scale: float = 1.5) -> None:
    def transform(point: tuple[float, float]) -> tuple[float, float]:
        x, y = point
        return xT + x * scale, yT + y * scale

    left = Polygon([transform(point) for point in [(0, 5), (0, 1), (2, 0)]], closed=True)
    right = Polygon([transform(point) for point in [(0, 5), (0, 1), (-2, 0)]], closed=True)
    left.set(facecolor="none", edgecolor="black", linewidth=1.2, zorder=6)
    right.set(facecolor="black", edgecolor="black", linewidth=0.8, zorder=6)
    ax.add_patch(left)
    ax.add_patch(right)
    ax.text(
        xT + 0.25 * scale,
        yT + 6 * scale,
        "N",
        fontsize=13,
        ha="center",
        va="center",
        weight="bold",
    )


def plot_scale_bar(
    ax,
    x: float = -16,
    y: float = -32,
    segment_km: int = 500,
    segments: int = 2,
    height: float = 0.6,
) -> None:
    # Around the southern SSA map extent, one longitude degree is about 100 km.
    segment_width = segment_km / 100
    for i in range(segments):
        ax.add_patch(
            Rectangle(
                (x + i * segment_width, y),
                segment_width,
                height,
                facecolor="black" if i % 2 == 0 else "white",
                edgecolor="black",
                linewidth=0.6,
                zorder=5,
            )
        )
    ax.plot([x, x + segments * segment_width], [y, y], color="black", linewidth=0.6, zorder=5)
    for i in range(segments + 1):
        tick_x = x + i * segment_width
        ax.plot([tick_x, tick_x], [y, y - 0.45], color="black", linewidth=0.6, zorder=5)
        ax.text(
            tick_x,
            y - 1.0,
            f"{i * segment_km}",
            ha="center",
            va="top",
            fontsize=7.2,
            zorder=5,
        )
    ax.text(
        x + segments * segment_width + 3.5,
        y - 1.0,
        "KM",
        ha="left",
        va="top",
        fontsize=7.2,
        weight="bold",
        zorder=5,
    )


def draw_info_panel(fig: plt.Figure, legend_patches: list[Patch], rect: list[float]) -> None:
    """Draw north arrow, legend, and scale bar together in one right-side panel."""
    ax = fig.add_axes(rect)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 100)
    ax.axis("off")

    font_kw: dict = {"fontfamily": "serif", "fontsize": 6.5}

    # ── North arrow (top of panel, y ≈ 91–100) ──────────────────────────
    cx, cy, s = 5.0, 94.0, 1.8
    east = Polygon([(cx, cy + s), (cx, cy - s * 0.3), (cx + s * 0.55, cy - s)], closed=True)
    west = Polygon([(cx, cy + s), (cx, cy - s * 0.3), (cx - s * 0.55, cy - s)], closed=True)
    east.set(facecolor="none", edgecolor="black", linewidth=0.9, zorder=6)
    west.set(facecolor="black", edgecolor="black", linewidth=0.7, zorder=6)
    ax.add_patch(east)
    ax.add_patch(west)
    ax.text(cx, cy + s + 0.8, "N", ha="center", va="bottom",
            fontsize=8, weight="bold", fontfamily="serif")

    # ── Legend (middle of panel, y ≈ 26–88) ─────────────────────────────
    n = len(legend_patches)
    y_top = 87.0
    dy = (y_top - 26.0) / n
    for i, patch in enumerate(legend_patches):
        y_center = y_top - (i + 0.5) * dy
        rect_patch = Rectangle(
            (0.3, y_center - dy * 0.38), 1.5, dy * 0.76,
            facecolor=patch.get_facecolor(),
            edgecolor=patch.get_edgecolor(),
            linewidth=0.4,
        )
        ax.add_patch(rect_patch)
        ax.text(2.2, y_center, patch.get_label(), va="center", ha="left", **font_kw)

    # ── Scale bar (bottom of panel, y ≈ 8–17) ───────────────────────────
    x0, y0, seg_w, bar_h = 0.3, 14.0, 2.2, 1.5
    for i in range(2):
        ax.add_patch(Rectangle(
            (x0 + i * seg_w, y0), seg_w, bar_h,
            facecolor="black" if i == 0 else "white",
            edgecolor="black", linewidth=0.45,
        ))
    ax.plot([x0, x0 + 2 * seg_w], [y0, y0], color="black", linewidth=0.45)
    for i in range(3):
        xp = x0 + i * seg_w
        ax.plot([xp, xp], [y0, y0 - 0.8], color="black", linewidth=0.45)
        ax.text(xp, y0 - 1.4, f"{i * 500}", ha="center", va="top", **font_kw)
    ax.text(x0 + 2 * seg_w + 0.45, y0 - 1.4, "km", ha="left", va="top",
            weight="bold", **font_kw)


def make_legend_patches(cmap, bins: list[int]) -> list[Patch]:
    norm = Normalize(vmin=0, vmax=len(bins))
    categories = [
        (
            f"<{upper:.0f}"
            if np.isneginf(lower)
            else f">{lower:.0f}"
            if np.isposinf(upper)
            else f"{lower:.0f}-{upper:.0f}"
        )
        for lower, upper in pairwise(chain([-np.inf], bins, [np.inf]))
    ] + ["Non-study area / no data"]

    patches: list[Patch] = []
    for i, label in enumerate(categories):
        facecolor = "lightgrey" if label == "Non-study area / no data" else cmap(norm(i))
        edgecolor = "dimgray" if label == "Non-study area / no data" else facecolor
        patches.append(Patch(facecolor=facecolor, edgecolor=edgecolor, label=label))
    return patches


def plot_index_map(
    features: list[dict],
    index_data: pd.DataFrame,
    column: str,
    output_file_path: Path,
    bins: list[int] | None = None,
    dpi: int = 600,
) -> None:
    bins = MAP_BINS if bins is None else bins
    palette = cm.get_cmap("Blues", len(bins) + 1)
    values = index_data.set_index(["Alpha-3 code", "Year"])[column].to_dict()

    fig = plt.figure(figsize=(11.2, 8.3))
    for i, year in enumerate(YEARS):
        ax = plt.subplot(2, 2, i + 1)
        ax.set_xlim(EXTENT[0], EXTENT[1])
        ax.set_ylim(EXTENT[2], EXTENT[3])
        ax.set_axis_off()
        ax.text(
            (EXTENT[0] + EXTENT[1]) / 2, EXTENT[3] - 1, f"{year}",
            fontsize=11, ha="center", va="top",
            fontfamily="serif", weight="bold",
            transform=ax.transData, zorder=10,
        )

        patches = []
        facecolors = []
        for feature in features:
            value = values.get((feature["SOC"], year), np.nan)
            color_index = len(bins) if pd.notna(value) else None
            if pd.notna(value):
                color_index = int(np.searchsorted(bins, float(value), side="right"))
            facecolor = "lightgrey" if color_index is None else palette(color_index)
            for part in feature["parts"]:
                if len(part) >= 3:
                    patches.append(Polygon(part, closed=True))
                    facecolors.append(facecolor)
        collection = PatchCollection(
            patches,
            facecolor=facecolors,
            edgecolor="dimgray",
            linewidth=0.55,
            zorder=2,
        )
        ax.add_collection(collection)


    if column != "SDI":
        fig.suptitle(MAP_TITLES[column], fontsize=13, y=0.992)
        top = 0.955
    else:
        top = 0.985
    fig.subplots_adjust(top=top, bottom=0.015, right=0.72, left=0.02, hspace=0.0, wspace=0.03)

    legend_patches = make_legend_patches(cm.ScalarMappable(cmap=palette).cmap, bins)
    draw_info_panel(fig, legend_patches, rect=[0.745, 0.04, 0.16, top - 0.04])

    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_file_path, dpi=dpi, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def main() -> None:
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = ["Times New Roman", "Liberation Serif", "DejaVu Serif"]
    plt.rc("font", weight="bold", size=10)
    plt.rc("axes", unicode_minus=False)

    features, index_data = load_map_data()
    for column in INDEX_COLUMNS:
        plot_index_map(features, index_data, column, OUTPUT_DIR / f"{column}_spatial_distribution.png")

    print(f"Exported {len(INDEX_COLUMNS)} geographical figures to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
