import ezdxf
import matplotlib.pyplot as plt
from collections import defaultdict
from utils import unique

def aci_to_rgb(aci_color):
    """Convert AutoCAD Color Index (ACI) to RGB tuple normalized for matplotlib."""
    if not aci_color or aci_color < 1:
        return (0, 0, 0)  # default black if no color
    r, g, b = ezdxf.colors.aci2rgb(aci_color)
    return (r / 255, g / 255, b / 255)


def draw_entities(entities: list[dict], width=20, height=16, dpi=200, file_path=None):
    """Draw entities with matplotlib and save as a PNG image."""
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

    # ❌ Skipping TEXT rendering (to remove placeholders)
    # If you want to show them, uncomment:
    # for txt in grouped.get("TEXT", []):
    #     pos = txt.get("position") or txt
    #     ax.text(pos['x'], pos['y'], txt['text'], color=aci_to_rgb(txt["aci"]))

    # Draw LINE entities
    for ln in grouped.get("LINE", []):
        start = ln["start"]
        end = ln["end"]
        ax.plot(
            [start['x'], end['x']],
            [start['y'], end['y']],
            color=aci_to_rgb(ln["aci"]),
        )

    # Draw LWPOLYLINE entities
    for poly in grouped.get("LWPOLYLINE", []):
        pts = poly["vertices"]
        xs = [pt['x'] for pt in pts]
        ys = [pt['y'] for pt in pts]
        if poly.get("closed"):
            xs.append(xs[0])
            ys.append(ys[0])
        ax.plot(xs, ys, color=aci_to_rgb(poly["aci"]))

    # ❌ Legend removed — no label box will be displayed

    plt.title("Drawing Entities Visualization")
    plt.xlabel("X axis")
    plt.ylabel("Y axis")
    plt.savefig(file_path, dpi=dpi, bbox_inches='tight')
    plt.close()
    return file_path
            
