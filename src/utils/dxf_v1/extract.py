import ezdxf


def extract_entities(dxf_path, keep_text):
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
        if entity.dxftype() in {"3DFACE", "POLYFACE", "MESH"}:
            raise ValueError(f"3D DXF detected: contains {entity.dxftype()} entities")

        # Get ACI
        aci = (
            doc.layers.get(entity.dxf.layer).color
            if entity.dxf.layer in doc.layers
            else None
        )

        # if entity.dxftype() in {"TEXT", "MTEXT"}:
        #     continue
        if keep_text and entity.dxftype() in {"TEXT", "MTEXT"}:
            e = {
                "entity_type": entity.dxftype(),
                "color": getattr(entity.dxf, "color", None),
                "layer": getattr(entity.dxf, "layer", None),
                "aci": aci,
            }
            e.update(
                {
                    "x": entity.dxf.insert.x,
                    "y": entity.dxf.insert.y,
                    "text": (
                        entity.dxf.text
                        if entity.dxftype() == "TEXT"
                        else entity.plain_text()
                    ),
                }
            )

        # POINT
        if entity.dxftype() == "POINT":
            e = {
                "entity_type": entity.dxftype(),
                "color": getattr(entity.dxf, "color", None),
                "layer": getattr(entity.dxf, "layer", None),
                "aci": aci,
            }
            loc = entity.dxf.location
            if loc.z != 0:
                is_3d = True
            e.update({"x": loc.x, "y": loc.y, "z": loc.z})

        # LINE
        if entity.dxftype() == "LINE":
            e = {
                "entity_type": entity.dxftype(),
                "color": getattr(entity.dxf, "color", None),
                "layer": getattr(entity.dxf, "layer", None),
                "aci": aci,
            }
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

        # POLYLINE
        if entity.dxftype() == "POLYLINE":
            e = {
                "entity_type": entity.dxftype(),
                "color": getattr(entity.dxf, "color", None),
                "layer": getattr(entity.dxf, "layer", None),
                "aci": aci,
            }
            # Check if 3D by looking at vertices Z values
            verts = []
            for v in entity.points():
                if len(v) >= 3 and v[2] != 0:
                    raise ValueError("3D DXF detected: POLYLINE has non-zero Z")
                verts.append({"x": v[0], "y": v[1], "z": 0.0})
            e.update(
                {
                    "entity_type": "LWPOLYLINE",
                    "closed": False,
                    "vertices": verts,
                }
            )

        if entity.dxftype() == "CIRCLE":
            e = {
                "entity_type": entity.dxftype(),
                "color": getattr(entity.dxf, "color", None),
                "layer": getattr(entity.dxf, "layer", None),
                "aci": aci,
            }
            center = entity.dxf.center  # Returns Vec3(x, y, z)
            radius = entity.dxf.radius
            e.update(
                {
                    "entity_type": "CIRCLE",
                    "center": {"x": center.x, "y": center.y, "z": center.z},
                    "radius": radius,
                }
            )

        # LWPOLYLINE
        if entity.dxftype() == "LWPOLYLINE":
            e = {
                "entity_type": entity.dxftype(),
                "color": getattr(entity.dxf, "color", None),
                "layer": getattr(entity.dxf, "layer", None),
                "aci": aci,
            }
            verts = []
            for v in entity.get_points():
                verts.append({"x": v[0], "y": v[1], "z": 0.0})
            e.update({"closed": entity.closed, "vertices": verts})

        extracted.append(e)

    if is_3d:
        raise ValueError("3D DXF detected: non-zero Z coordinates found")

    return extracted
