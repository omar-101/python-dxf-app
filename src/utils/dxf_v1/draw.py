import os
import ezdxf
import matplotlib.pyplot as plt
from collections import defaultdict
from utils import unique
import math


def aci_to_rgb(aci_color):
    if not aci_color or aci_color < 1:
        return (0, 0, 0)
    r, g, b = ezdxf.colors.aci2rgb(aci_color)
    return (r / 255, g / 255, b / 255)


def line_length(start, end):
    return math.sqrt((end["x"] - start["x"]) ** 2 + (end["y"] - start["y"]) ** 2)


def get_shift_value(aci, shifts):
    if not shifts:
        return None
    for s in shifts:
        if s[0] == aci:
            return s[1]  # 2nd index = shift value
    return None


def draw_entities(
    entities,
    entities2=None,
    width=20,
    height=16,
    dpi=200,
    file_path=None,
    show_length=True,
    round_lengths=True,
    length_fontsize=14,
    shifts=None,  # ← NEW PARAMETER
):
    os.makedirs("./tmp", exist_ok=True)
    if not file_path:
        file_path = "./tmp/" + unique.unique_string(20) + ".png"

    fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
    ax.set_aspect("equal")
    ax.grid(True)

    grouped1 = defaultdict(list)
    grouped2 = defaultdict(list)

    for ent in entities:
        grouped1[ent.get("entity_type")].append(ent)
    if entities2:
        for ent in entities2:
            grouped2[ent.get("entity_type")].append(ent)

    # Draw POINT
    for pt in grouped1.get("POINT", []):
        ax.scatter(
            pt.get("x", 0), pt.get("y", 0), color=aci_to_rgb(pt.get("aci")), s=30
        )
    if entities2:
        for pt in grouped2.get("POINT", []):
            ax.scatter(pt.get("x", 0), pt.get("y", 0), color="black", s=30)

    # Draw LINE
    for ln in grouped1.get("LINE", []):
        start, end = ln.get("start"), ln.get("end")
        if start and end:
            ax.plot(
                [start["x"], end["x"]],
                [start["y"], end["y"]],
                color=aci_to_rgb(ln.get("aci")),
                linestyle="-",
            )

            if show_length:
                length = line_length(start, end)
                length_text = round(length) if round_lengths else length

                # Use shift value if available
                shift_val = get_shift_value(ln.get("aci"), shifts)
                offset_text = f" ({shift_val})" if shift_val is not None else ""

                mid_x = (start["x"] + end["x"]) / 2
                mid_y = (start["y"] + end["y"]) / 2

                ax.text(
                    mid_x,
                    mid_y + 0.1,
                    f"{length_text}{offset_text}",
                    color="black",
                    fontsize=length_fontsize,
                    ha="center",
                    va="bottom",
                    backgroundcolor="white",
                )

    # Draw LWPOLYLINE
    for poly in grouped1.get("LWPOLYLINE", []):
        pts = poly.get("vertices", [])
        if not pts or len(pts) < 2:
            continue

        draw_pts = pts + [pts[0]] if poly.get("closed") else pts

        # Draw edges
        for j in range(len(draw_pts) - 1):
            x1, y1 = draw_pts[j]["x"], draw_pts[j]["y"]
            x2, y2 = draw_pts[j + 1]["x"], draw_pts[j + 1]["y"]
            ax.plot([x1, x2], [y1, y2], color=aci_to_rgb(poly.get("aci")))

        if show_length:
            segment_lengths = [
                line_length(draw_pts[j], draw_pts[j + 1])
                for j in range(len(draw_pts) - 1)
            ]
            full_length = sum(segment_lengths)

            # find middle position
            half = full_length / 2
            cum = 0
            for j, seg in enumerate(segment_lengths):
                if cum + seg >= half:
                    ratio = (half - cum) / seg
                    x_mid = draw_pts[j]["x"] + ratio * (
                        draw_pts[j + 1]["x"] - draw_pts[j]["x"]
                    )
                    y_mid = draw_pts[j]["y"] + ratio * (
                        draw_pts[j + 1]["y"] - draw_pts[j]["y"]
                    )
                    break
                cum += seg

            # Use shift value if available
            shift_val = get_shift_value(poly.get("aci"), shifts)
            offset_text = f" ({shift_val})" if shift_val is not None else ""

            length_text = round(full_length) if round_lengths else full_length

            ax.text(
                x_mid,
                y_mid,
                f"{length_text}{offset_text}",
                color="black",
                fontsize=length_fontsize,
                ha="center",
                va="center",
                backgroundcolor="white",
            )

    # Draw second entities as black dashed lines
    if entities2:
        for ln in grouped2.get("LINE", []):
            start, end = ln.get("start"), ln.get("end")
            if start and end:
                ax.plot(
                    [start["x"], end["x"]],
                    [start["y"], end["y"]],
                    color="black",
                    linestyle="--",
                )

        for poly in grouped2.get("LWPOLYLINE", []):
            pts = poly.get("vertices", [])
            if pts:
                draw_pts = pts + [pts[0]] if poly.get("closed") else pts
                for j in range(len(draw_pts) - 1):
                    ax.plot(
                        [draw_pts[j]["x"], draw_pts[j + 1]["x"]],
                        [draw_pts[j]["y"], draw_pts[j + 1]["y"]],
                        color="black",
                        linestyle="--",
                    )

    # Draw TEXT
    for txt in grouped1.get("TEXT", []):
        pos = txt.get("position", {})
        x, y = pos.get("x", 0), pos.get("y", 0)
        ax.text(
            x,
            y,
            txt.get("text", ""),
            color=aci_to_rgb(txt.get("aci")),
            fontsize=txt.get("height", 12),
        )

    plt.title("Comparison of Entities" + (" with Lengths" if show_length else ""))
    plt.xlabel("X axis")
    plt.ylabel("Y axis")
    plt.savefig(file_path, dpi=dpi, bbox_inches="tight")
    plt.close()
    return file_path
