import ezdxf
import matplotlib.pyplot as plt
from collections import defaultdict
from utils import unique


def aci_to_rgb(aci_color):
    r, g, b = ezdxf.colors.aci2rgb(aci_color)
    return (r / 255, g / 255, b / 255)

class Dxf: 
    def extract_entities(self, dxf_path):
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()
        extracted = []

        for entity in msp:
            e = {
                "entity_type": entity.dxftype(), 
                "color": entity.dxf.color, 
                "layer": entity.dxf.layer,
                "aci": doc.layers.get(entity.dxf.layer).color
                }

            if entity.dxftype() == "POINT":
                e.update({
                    "x": entity.dxf.location.x,
                    "y": entity.dxf.location.y,
                    "z": entity.dxf.location.z
                })

            elif entity.dxftype() == "LINE":
                e.update({
                    "start": {
                        "x": entity.dxf.start.x,
                        "y": entity.dxf.start.y,
                        "z": entity.dxf.start.z
                    },
                    "end": {
                        "x": entity.dxf.end.x,
                        "y": entity.dxf.end.y,
                        "z": entity.dxf.end.z
                    }
                })
                

            elif entity.dxftype() == "LWPOLYLINE":
                e.update({
                    "closed": entity.closed,
                    "vertices": [
                        {"x": v[0], "y": v[1], "z": 0.0} for v in entity.get_points()
                    ]
                })

            elif entity.dxftype() == "TEXT":
                e.update({
                    "text": entity.dxf.text,
                    "position": {
                        "x": entity.dxf.insert.x,
                        "y": entity.dxf.insert.y,
                        "z": entity.dxf.insert.z
                    },
                    "height": entity.dxf.height,
                    "rotation": entity.dxf.rotation
                })

            # Optional: Add support for CIRCLE, ARC, MTEXT, etc.

            extracted.append(e)

        return extracted
    
    
    def draw_entities(self, entities: list[dict]):
        file_path = "./tmp/" + unique.unique_string(20) + ".png"
        # Group entities by their type
        grouped = defaultdict(list)
        for ent in entities:
            ent_type = ent.get("entity_type")
            if ent_type:
                grouped[ent_type].append(ent)

        fig, ax = plt.subplots()
        ax.set_aspect('equal')
        ax.grid(True)

        # Draw POINT entities as blue circles
        for pt in grouped.get("POINT", []):
            ax.scatter(pt['x'], pt['y'], color=aci_to_rgb(pt["aci"]), s=30, label='Point')

        # Draw TEXT entities as labels
        for txt in grouped.get("TEXT", []):
            pos = txt.get("position") or txt
            ax.text(pos['x'], pos['y'], txt['text'], color=aci_to_rgb(txt["aci"]))

        # Draw LINE entities as green segments
        for idx, ln in enumerate(grouped.get("LINE", [])):
            start = ln["start"]
            end = ln["end"]
            ax.plot([start['x'], end['x']], [start['y'], end['y']], color=aci_to_rgb(ln["aci"]), label='Line' if idx == 0 else "")

        # Draw LWPOLYLINE entities
        poly_label_drawn = False
        for poly in grouped.get("LWPOLYLINE", []):
            pts = poly["vertices"]
            xs = [pt['x'] for pt in pts]
            ys = [pt['y'] for pt in pts]
            if poly.get("closed"):
                xs.append(xs[0])
                ys.append(ys[0])
            label = 'Frame' if poly.get("layer") == "Frames" else ('Polyline' if not poly_label_drawn else "")
            ax.plot(xs, ys, color=aci_to_rgb(poly["aci"]), label=label)
            if label == 'Polyline':
                poly_label_drawn = True

        ax.legend(loc='best')
        plt.title("Drawing Entities Visualization")
        plt.xlabel("X axis")
        plt.ylabel("Y axis")
        plt.savefig(file_path)
        plt.close()
        return file_path
