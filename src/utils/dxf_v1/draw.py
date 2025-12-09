import os
import ezdxf
import matplotlib.pyplot as plt
from collections import defaultdict
from utils import unique


def aci_to_rgb(aci_color):
    """
    Convert an AutoCAD Color Index (ACI) to normalized RGB tuple.
    If the ACI is 0 or invalid, default to black.
    """
    try:
        if not aci_color or aci_color < 1 or aci_color > 255:
            return (0, 0, 0)
        r, g, b = ezdxf.colors.aci2rgb(aci_color)
        return (r / 255, g / 255, b / 255)
    except Exception:
        return (0, 0, 0)


def draw_entities(
    entities,
    width=20,
    height=16,
    dpi=200,
    file_path=None,
):
    os.makedirs("./tmp", exist_ok=True)
    if not file_path:
        file_path = "./tmp/" + unique.unique_string(20) + ".png"

    fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
    ax.set_aspect("equal")
    ax.grid(True)

    grouped = defaultdict(list)
    for ent in entities:
        grouped[ent.get("entity_type")].append(ent)

    # ---- POINT ----
    for pt in grouped.get("POINT", []):
        ax.scatter(
            pt.get("x", 0), pt.get("y", 0), color=aci_to_rgb(pt.get("aci")), s=30
        )

    # ---- LINE ----
    for ln in grouped.get("LINE", []):
        start, end = ln.get("start"), ln.get("end")
        if not start or not end:
            continue

        is_dashed = ln.get("dashed", False)

        ax.plot(
            [start["x"], end["x"]],
            [start["y"], end["y"]],
            color="black" if is_dashed else aci_to_rgb(ln.get("aci")),
            linestyle="--" if is_dashed else "-",
            linewidth=1.2,
        )

    # ---- LWPOLYLINE ----
    for poly in grouped.get("LWPOLYLINE", []):
        pts = poly.get("vertices", [])
        if not pts or len(pts) < 2:
            continue

        draw_pts = pts + [pts[0]] if poly.get("closed") else pts
        is_dashed = poly.get("dashed", False)

        for j in range(len(draw_pts) - 1):
            x1, y1 = draw_pts[j]["x"], draw_pts[j]["y"]
            x2, y2 = draw_pts[j + 1]["x"], draw_pts[j + 1]["y"]

            ax.plot(
                [x1, x2],
                [y1, y2],
                color="black" if is_dashed else aci_to_rgb(poly.get("aci")),
                linestyle="--" if is_dashed else "-",
                linewidth=1.2,
            )

    # ---- TEXT ----
    for txt in grouped.get("TEXT", []):
        pos = txt.get("position", {})
        x, y = pos.get("x", 0), pos.get("y", 0)
        fontsize = txt.get("height", 12)
        ax.text(
            x,
            y,
            txt.get("text", ""),
            color=aci_to_rgb(txt.get("aci")),
            fontsize=fontsize,
        )

    plt.title("Entities")
    plt.xlabel("X axis")
    plt.ylabel("Y axis")
    plt.savefig(file_path, dpi=dpi, bbox_inches="tight")
    plt.close()
    return file_path
