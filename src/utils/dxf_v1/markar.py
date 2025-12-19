from constants import modes

# ------------------ Helper functions ------------------


def center_position_vertices(vertices):
    """
    Returns the center coordinates (x, y) of a set of vertices.
    """
    if not vertices:
        return 0, 0
    xs = [v["x"] for v in vertices]
    ys = [v["y"] for v in vertices]
    x = sum(xs) / len(xs)
    y = sum(ys) / len(ys)
    return x, y


def center_position_line_box(lines):
    """
    Returns the center coordinates (x, y) of a LINE-based box.
    """
    xs = []
    ys = []
    for line in lines:
        start = line.get("start")
        end = line.get("end")
        if start and end:
            xs.extend([start["x"], end["x"]])
            ys.extend([start["y"], end["y"]])
    if not xs or not ys:
        return 0, 0
    x = sum(xs) / len(xs)
    y = sum(ys) / len(ys)
    return x, y


def add_text_entity(x, y, aci, marker_text, text_height):
    """
    Creates a TEXT entity at given coordinates.
    """
    return {
        "entity_type": "TEXT",
        "layer": "sink/gas",
        "text": marker_text,
        "position": {"x": x, "y": y, "z": 0},
        "height": text_height,
        "rotation": 0,
        "aci": aci,
    }


def add_text_to_lwpoly_group(lwpoly_group, marker_text, text_height):
    """
    Adds TEXT for a group of LWPOLYLINEs (open or closed).
    """
    vertices = []
    for poly in lwpoly_group:
        vertices.extend(poly.get("vertices", []))
    if not vertices:
        return []
    x, y = center_position_vertices(vertices)
    aci = lwpoly_group[0].get("aci", 152)
    return [add_text_entity(x, y, aci, marker_text, text_height)]


def add_text_to_line_group(line_group, marker_text, text_height):
    """
    Adds TEXT for a LINE-based box.
    """
    x, y = center_position_line_box(line_group)
    aci = line_group[0].get("aci", 152) if line_group else 152
    return [add_text_entity(x, y, aci, marker_text, text_height)]


# ------------------ Main function ------------------


def gas_sink_marker(
    dxf_entities, marker_aci_target=152, marker_text=None, text_height=1.0
):
    """
    Adds TEXT entities to boxes:
      - Closed LWPOLYLINEs
      - 4 open LWPOLYLINEs forming a box
      - 4 LINEs forming a box
    Text will appear in the center of the box.
    """
    new_entities = []

    # --- LWPOLYLINEs ---
    lwpolys = [
        e
        for e in dxf_entities
        if e.get("entity_type") == "LWPOLYLINE" and e.get("aci") == marker_aci_target
    ]
    closed_lwpolys = [p for p in lwpolys if p.get("closed")]
    open_lwpolys = [p for p in lwpolys if not p.get("closed")]

    # Closed LWPOLYLINEs
    for poly in closed_lwpolys:
        new_entities += add_text_to_lwpoly_group([poly], marker_text, text_height)

    # Open LWPOLYLINEs grouped by 4
    for i in range(0, len(open_lwpolys), 4):
        group = open_lwpolys[i : i + 4]
        new_entities += add_text_to_lwpoly_group(group, marker_text, text_height)

    # --- LINEs ---
    lines = [
        e
        for e in dxf_entities
        if e.get("entity_type") == "LINE" and e.get("aci") == marker_aci_target
    ]
    for i in range(0, len(lines), 4):
        group = lines[i : i + 4]
        new_entities += add_text_to_line_group(group, marker_text, text_height)

    return dxf_entities + new_entities


# ------------------ Apply markers ------------------


def create_markers(coords, shifts, text_height):
    """
    Adds gas/sink markers based on shifts.
    """
    modes_by_value = {v: k for k, v in modes.MODES.items()}

    # Filter only gas/sink modes
    gas_sink_shifts = [
        {"aci": aci, "shift": shift, "mode": mode, "mode_text": modes_by_value[mode]}
        for aci, shift, mode in shifts
        if mode in (modes.MODES["sink"], modes.MODES["gas"])
    ]

    # Apply markers
    for item in gas_sink_shifts:
        coords = gas_sink_marker(coords, item["aci"], item["mode_text"], text_height)

    return coords
