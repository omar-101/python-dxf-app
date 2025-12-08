import ezdxf
from utils import unique
from ezdxf.enums import TextEntityAlignment


def generate_dxf(entities: list[dict], file_path=None):
    """Generate a DXF file from a list of extracted entities, preserving layers."""

    if not file_path:
        file_path = "./tmp/" + unique.unique_string(20) + ".dxf"

    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()

    # Keep track of created layers to avoid duplicates
    existing_layers = {}

    for ent in entities:
        etype = ent.get("entity_type")
        layer = ent.get("layer", "0")
        aci = ent.get("aci", 7)  # default color if missing

        # ---- Create layer if not already created ----
        if layer not in existing_layers:
            try:
                doc.layers.new(name=layer, dxfattribs={"color": aci})
            except ezdxf.DXFTableEntryError:
                # Layer already exists, skip
                pass
            existing_layers[layer] = aci

        # ---- Add entities ----
        if etype == "POINT":
            msp.add_point(
                (ent["x"], ent["y"], ent.get("z", 0.0)), dxfattribs={"layer": layer}
            )

        elif etype == "LINE":
            start = ent.get("start")
            end = ent.get("end")
            if start and end:
                msp.add_line(
                    (start["x"], start["y"], start.get("z", 0.0)),
                    (end["x"], end["y"], end.get("z", 0.0)),
                    dxfattribs={"layer": layer},
                )

        elif etype == "LWPOLYLINE":
            pts = [(v["x"], v["y"]) for v in ent["vertices"]]  # drop Z for LWPOLYLINE
            msp.add_lwpolyline(
                pts, dxfattribs={"layer": layer, "closed": ent.get("closed", False)}
            )

        elif etype == "TEXT":
            pos = ent.get("position")
            if pos:
                text_entity = msp.add_text(
                    ent.get("text", ""),
                    dxfattribs={
                        "layer": layer,
                        "height": ent.get("height", 2.5),
                        "color": aci,
                    },
                )
                # Default alignment can be LEFT if not specified
                align = ent.get("align", TextEntityAlignment.LEFT)
                text_entity.set_placement(
                    (pos["x"], pos["y"], pos.get("z", 0.0)), align=align
                )

        else:
            print(f"⚠️ Skipping unsupported entity type: {etype}")

    # Save the DXF
    doc.saveas(file_path)
    print(f"✅ DXF successfully saved at: {file_path}")
    return file_path
