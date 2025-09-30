import ezdxf
import matplotlib.pyplot as plt
from collections import defaultdict
from utils import unique
from utils import shift_measurements

def aci_to_rgb(aci_color):
    """Convert AutoCAD Color Index (ACI) to RGB tuple normalized for matplotlib."""
    if not aci_color or aci_color < 1:
        return (0, 0, 0)  # default black if no color
    r, g, b = ezdxf.colors.aci2rgb(aci_color)
    return (r / 255, g / 255, b / 255)


class Dxf:
    def extract_entities(self, dxf_path):
        """Read a DXF file and extract supported entities into a list of dicts."""
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()
        extracted = []

        for entity in msp:
            e = {
                "entity_type": entity.dxftype(),
                "color": entity.dxf.color,
                "layer": entity.dxf.layer,
                "aci": doc.layers.get(entity.dxf.layer).color,
            }

            if entity.dxftype() == "POINT":
                e.update({
                    "x": entity.dxf.location.x,
                    "y": entity.dxf.location.y,
                    "z": entity.dxf.location.z,
                })

            elif entity.dxftype() == "LINE":
                e.update({
                    "start": {
                        "x": entity.dxf.start.x,
                        "y": entity.dxf.start.y,
                        "z": entity.dxf.start.z,
                    },
                    "end": {
                        "x": entity.dxf.end.x,
                        "y": entity.dxf.end.y,
                        "z": entity.dxf.end.z,
                    },
                })

            elif entity.dxftype() == "LWPOLYLINE":
                e.update({
                    "closed": entity.closed,
                    "vertices": [
                        {"x": v[0], "y": v[1], "z": 0.0} for v in entity.get_points()
                    ],
                })

            elif entity.dxftype() == "TEXT":
                e.update({
                    "text": entity.dxf.text,
                    "position": {
                        "x": entity.dxf.insert.x,
                        "y": entity.dxf.insert.y,
                        "z": entity.dxf.insert.z,
                    },
                    "height": entity.dxf.height,
                    "rotation": entity.dxf.rotation,
                })

            extracted.append(e)

        return extracted

    def draw_entities(self, entities: list[dict], width=20, height=16, dpi=200, file_path=None):
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
    
    def shift_measurements(self, entities: list[dict], shifts):
        return shift_measurements.smartscale_main(entities, shifts)
            
