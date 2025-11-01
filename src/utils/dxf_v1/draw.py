import ezdxf
import matplotlib.pyplot as plt
from collections import defaultdict
from utils import unique
import math


def aci_to_rgb(aci_color):
    """Convert AutoCAD Color Index (ACI) to RGB tuple normalized for matplotlib."""
    if not aci_color or aci_color < 1:
        return (0, 0, 0)  # default black if no color
    r, g, b = ezdxf.colors.aci2rgb(aci_color)
    return (r / 255, g / 255, b / 255)


def line_length(start, end):
    """Calculate Euclidean distance between two points."""
    return math.sqrt((end['x'] - start['x']) ** 2 + (end['y'] - start['y']) ** 2)


def draw_entities(
    entities: list[dict],
    entities2: list[dict] = None,  # optional
    width=20,
    height=16,
    dpi=200,
    file_path=None,
    show_length=True
):
    """Draw entities and optionally a second set for comparison.
    entities → colored
    entities2 → optional black dashed lines / black points
    """
    if not file_path:
        file_path = "./tmp/" + unique.unique_string(20) + ".png"

    fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
    ax.set_aspect('equal')
    ax.grid(True)

    def draw_entity_list(ent_list, use_color=True, dashed=False):
        grouped = defaultdict(list)
        for ent in ent_list:
            ent_type = ent.get("entity_type")
            if ent_type:
                grouped[ent_type].append(ent)

        # POINT entities
        for pt in grouped.get("POINT", []):
            color = aci_to_rgb(pt["aci"]) if use_color else 'black'
            ax.scatter(pt['x'], pt['y'], color=color, s=30)

        # LINE entities
        for ln in grouped.get("LINE", []):
            start = ln["start"]
            end = ln["end"]
            color = aci_to_rgb(ln["aci"]) if use_color else 'black'
            style = '--' if dashed else '-'
            ax.plot([start['x'], end['x']], [start['y'], end['y']], color=color, linestyle=style)

            if show_length:
                length = line_length(start, end)
                mid_x = (start['x'] + end['x']) / 2
                mid_y = (start['y'] + end['y']) / 2
                ax.text(mid_x, mid_y + 0.1, f"{length:.2f}",
                        color='black', fontsize=8, ha='center', va='bottom',
                        backgroundcolor='white')

        # LWPOLYLINE entities
        for poly in grouped.get("LWPOLYLINE", []):
            pts = poly["vertices"]
            color = aci_to_rgb(poly["aci"]) if use_color else 'black'
            style = '--' if dashed else '-'
            if poly.get("closed"):
                pts = pts + [pts[0]]

            for i in range(len(pts) - 1):
                x1, y1 = pts[i]['x'], pts[i]['y']
                x2, y2 = pts[i + 1]['x'], pts[i + 1]['y']
                ax.plot([x1, x2], [y1, y2], color=color, linestyle=style)

                if show_length:
                    length = line_length(pts[i], pts[i + 1])
                    mid_x = (x1 + x2) / 2
                    mid_y = (y1 + y2) / 2
                    ax.text(mid_x, mid_y + 0.1, f"{length:.2f}",
                            color='black', fontsize=8, ha='center', va='bottom',
                            backgroundcolor='white')

    # Draw first entities (colored)
    draw_entity_list(entities, use_color=True, dashed=False)

    # Draw second entities if provided (black dashed)
    if entities2:
        draw_entity_list(entities2, use_color=False, dashed=True)

    plt.title("Comparison of Entities" + (" with Lengths" if show_length else ""))
    plt.xlabel("X axis")
    plt.ylabel("Y axis")
    plt.savefig(file_path, dpi=dpi, bbox_inches='tight')
    plt.close()
    return file_path
