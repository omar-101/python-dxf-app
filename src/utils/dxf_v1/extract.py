import ezdxf


def extract_entities(dxf_path):
    """Read a DXF file and extract supported 2D entities into a list of dicts.
    Rejects 3D DXF files with an explicit error. Skips text and ACI=253 entities.
    """
    try:
        doc = ezdxf.readfile(dxf_path)
    except ezdxf.DXFStructureError as e:
        raise ValueError(f"Invalid DXF file: {e}")

    msp = doc.modelspace()
    extracted = []
    is_3d = False

    for entity in msp:
        # Reject known 3D entity types immediately
        if entity.dxftype() in {"3DFACE", "POLYFACE", "MESH", "POLYLINE"}:
            raise ValueError(f"3D DXF detected: contains {entity.dxftype()} entities")

        # Skip text entities
        if entity.dxftype() in {"TEXT", "MTEXT"}:
            continue

        # Get ACI
        aci = (
            doc.layers.get(entity.dxf.layer).color
            if entity.dxf.layer in doc.layers
            else None
        )

        # Skip ACI 253
        if aci == 253:
            continue

        e = {
            "entity_type": entity.dxftype(),
            "color": getattr(entity.dxf, "color", None),
            "layer": getattr(entity.dxf, "layer", None),
            "aci": aci,
        }

        # POINT
        if entity.dxftype() == "POINT":
            loc = entity.dxf.location
            if loc.z != 0:
                is_3d = True
            e.update({"x": loc.x, "y": loc.y, "z": loc.z})

        # LINE
        elif entity.dxftype() == "LINE":
            start_z, end_z = entity.dxf.start.z, entity.dxf.end.z
            if start_z != 0 or end_z != 0:
                is_3d = True
            e.update(
                {
                    "start": {
                        "x": entity.dxf.start.x,
                        "y": entity.dxf.start.y,
                        "z": start_z,
                    },
                    "end": {"x": entity.dxf.end.x, "y": entity.dxf.end.y, "z": end_z},
                }
            )

        # LWPOLYLINE
        elif entity.dxftype() == "LWPOLYLINE":
            verts = []
            for v in entity.get_points():
                # v = (x, y, start_width, end_width, bulge)
                if len(v) >= 3 and v[2] != 0:
                    is_3d = True
                verts.append({"x": v[0], "y": v[1], "z": 0.0})
            e.update({"closed": entity.closed, "vertices": verts})

        extracted.append(e)

    if is_3d:
        raise ValueError("3D DXF detected: non-zero Z coordinates found")

    return extracted
