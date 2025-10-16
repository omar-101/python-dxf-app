import ezdxf
from utils import unique


def generate_dxf(entities: list[dict], file_path=None):
    """Generate a DXF file from a list of extracted entities."""

    if not file_path:
        file_path = "./tmp/" + unique.unique_string(20) + ".dxf"

    # Create a new DXF document
    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()

    # Cache created layers to avoid duplicates
    existing_layers = set()

    for ent in entities:
        etype = ent.get("entity_type")
        layer = ent.get("layer", "0")
        aci = ent.get("aci", 7)  # Default white

        # Ensure the layer exists
        if layer not in existing_layers:
            try:
                doc.layers.new(name=layer, dxfattribs={"color": aci})
                existing_layers.add(layer)
            except ezdxf.DXFTableEntryError:
                # Layer may already exist or invalid color
                pass

        # ✅ POINT entity
        if etype == "POINT":
            msp.add_point(
                (ent["x"], ent["y"], ent.get("z", 0.0)),
                dxfattribs={"layer": layer, "color": aci},
            )

        # ✅ LINE entity
        elif etype == "LINE":
            start = ent.get("start")
            end = ent.get("end")
            if start and end:
                msp.add_line(
                    (start["x"], start["y"], start.get("z", 0.0)),
                    (end["x"], end["y"], end.get("z", 0.0)),
                    dxfattribs={"layer": layer, "color": aci},
                )

        # ✅ LWPOLYLINE entity
        elif etype == "LWPOLYLINE":
            pts = [(v["x"], v["y"], v.get("z", 0.0)) for v in ent["vertices"]]
            msp.add_lwpolyline(
                pts,
                dxfattribs={
                    "layer": layer,
                    "color": aci,
                    "closed": ent.get("closed", False),
                },
            )

        # ✅ TEXT entity
        elif etype == "TEXT":
            pos = ent.get("position", {"x": 0, "y": 0, "z": 0})
            text = msp.add_text(
                ent.get("text", ""),
                dxfattribs={
                    "height": ent.get("height", 2.5),
                    "rotation": ent.get("rotation", 0),
                    "layer": layer,
                    "color": aci,
                },
            )
            # Set text insertion point
            text.dxf.insert = (pos["x"], pos["y"], pos.get("z", 0.0))

        # ⚠️ Unsupported entity
        else:
            print(f"⚠️ Skipping unsupported entity type: {etype}")

    # Save DXF
    doc.saveas(file_path)
    print(f"✅ DXF successfully saved at: {file_path}")
    return file_path