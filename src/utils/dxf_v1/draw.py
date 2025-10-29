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


def draw_entities(entities: list[dict], width=20, height=16, dpi=200, file_path=None, show_length=True):
    """Draw entities with matplotlib and save as a PNG image, optionally showing line lengths."""
    if not file_path:
        file_path = "./tmp/" + unique.unique_string(20) + ".png"

    # Group entities by type
    grouped = defaultdict(list)
    for ent in entities:
        ent_type = ent.get("entity_type")
        if ent_type:
            grouped[ent_type].append(ent)

    # Create figure
    fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
    ax.set_aspect('equal')
    ax.grid(True)

    # Draw POINT entities
    for pt in grouped.get("POINT", []):
        ax.scatter(pt['x'], pt['y'], color=aci_to_rgb(pt["aci"]), s=30)

    # Draw LINE entities
    for ln in grouped.get("LINE", []):
        start = ln["start"]
        end = ln["end"]
        color = aci_to_rgb(ln["aci"])
        ax.plot([start['x'], end['x']], [start['y'], end['y']], color=color)

        if show_length:
            length = line_length(start, end)
            mid_x = (start['x'] + end['x']) / 2
            mid_y = (start['y'] + end['y']) / 2
            ax.text(
                mid_x,
                mid_y,
                f"{length:.2f}",
                color='black',
                fontsize=8,
                ha='center',
                va='bottom',
                backgroundcolor='white'
            )

    # Draw LWPOLYLINE entities
    for poly in grouped.get("LWPOLYLINE", []):
        pts = poly["vertices"]
        color = aci_to_rgb(poly["aci"])

        if poly.get("closed"):
            pts = pts + [pts[0]]  # close shape

        for i in range(len(pts) - 1):
            x1, y1 = pts[i]['x'], pts[i]['y']
            x2, y2 = pts[i + 1]['x'], pts[i + 1]['y']
            ax.plot([x1, x2], [y1, y2], color=color)

            if show_length:
                length = line_length(pts[i], pts[i + 1])
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                ax.text(
                    mid_x,
                    mid_y,
                    f"{length:.2f}",
                    color='black',
                    fontsize=8,
                    ha='center',
                    va='bottom',
                    backgroundcolor='white'
                )

    plt.title("Drawing Entities Visualization" + (" with Lengths" if show_length else ""))
    plt.xlabel("X axis")
    plt.ylabel("Y axis")
    plt.savefig(file_path, dpi=dpi, bbox_inches='tight')
    plt.close()
    return file_path


# Example usage:
if __name__ == "__main__":
    # Sample entities
    entities = [
        {"entity_type": "LINE", "start": {"x": 0, "y": 0}, "end": {"x": 5, "y": 5}, "aci": 1},
        {"entity_type": "LWPOLYLINE", "vertices": [{"x": 0, "y": 0}, {"x": 5, "y": 0}, {"x": 5, "y": 5}], "closed": True, "aci": 3},
        {"entity_type": "POINT", "x": 2, "y": 2, "aci": 5}
    ]

    file_path = draw_entities(entities, show_length=True)
    print("Saved drawing to:", file_path)
