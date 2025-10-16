import ezdxf

def extract_entities(dxf_path):
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
            
