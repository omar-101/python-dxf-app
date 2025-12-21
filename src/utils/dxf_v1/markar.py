from constants import modes

# ------------------ Helper functions ------------------


def center_position_vertices(vertices):
    """
    Returns center coordinates (x, y) AND the width/height based on actual line lengths.
    Works for LWPOLYLINE vertices (closed or open).
    """
    if not vertices or len(vertices) < 2:
        return 0, 0, 0, 0

    xs = [v["x"] for v in vertices]
    ys = [v["y"] for v in vertices]

    # Center (still axis-aligned)
    center_x = sum(xs) / len(xs)
    center_y = sum(ys) / len(ys)

    # Compute edge lengths along X and Y
    width = 0
    height = 0
    for i in range(len(vertices) - 1):
        start = vertices[i]
        end = vertices[i + 1]
        dx = abs(end["x"] - start["x"])
        dy = abs(end["y"] - start["y"])
        width = max(width, dx)
        height = max(height, dy)

    # For closed polylines, include last segment
    if vertices[0] != vertices[-1]:
        dx = abs(vertices[-1]["x"] - vertices[0]["x"])
        dy = abs(vertices[-1]["y"] - vertices[0]["y"])
        width = max(width, dx)
        height = max(height, dy)

    return center_x, center_y, width, height


def center_position_line_box(lines):
    """
    Returns center coordinates (x, y) AND box width and height
    for a group of LINEs forming a rectangle, using actual line lengths.
    """
    if not lines:
        return 0, 0, 0, 0

    xs = []
    ys = []

    width = 0
    height = 0

    for line in lines:
        start = line.get("start")
        end = line.get("end")
        if not start or not end:
            continue

        # Collect for center calculation
        xs.extend([start["x"], end["x"]])
        ys.extend([start["y"], end["y"]])

        # Calculate actual line segment lengths along X and Y
        dx = abs(end["x"] - start["x"])
        dy = abs(end["y"] - start["y"])
        width = max(width, dx)
        height = max(height, dy)

    if not xs or not ys:
        return 0, 0, 0, 0

    # Center coordinates
    center_x = sum(xs) / len(xs)
    center_y = sum(ys) / len(ys)

    return center_x, center_y, width, height


def add_text_entity(x, y, aci, marker_text, width, height, shift, text_height):
    """
    Creates a TEXT entity at given coordinates with two lines:
      marker_text
      width x height
    """
    text = f"{marker_text}({shift})\n{round(width)} x {round(height)}"

    return {
        "entity_type": "TEXT",
        "layer": "sink gas",
        "text": text.capitalize(),
        "position": {"x": x, "y": y, "z": 0},
        "height": text_height,
        "rotation": 0,
        "aci": aci,
    }


def add_text_to_lwpoly_group(lwpoly_group, marker_text, shift, text_height):
    """
    Adds TEXT for a group of LWPOLYLINEs (open or closed).
    """
    vertices = []
    for poly in lwpoly_group:
        vertices.extend(poly.get("vertices", []))
    if not vertices:
        return []
    x, y, width, height = center_position_vertices(vertices)
    aci = lwpoly_group[0].get("aci", 152)
    return [add_text_entity(x, y, aci, marker_text, width, height, shift, text_height)]


def add_text_to_line_group(line_group, marker_text, shift, text_height):
    """
    Adds TEXT for a LINE-based box.
    """
    x, y, width, height = center_position_line_box(line_group)
    aci = line_group[0].get("aci", 152) if line_group else 152
    return [add_text_entity(x, y, aci, marker_text, width, height, shift, text_height)]


# ------------------ Main function ------------------


def gas_sink_marker(
    dxf_entities, marker_aci_target=152, marker_text=None, shift="", text_height=1.0
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
        new_entities += add_text_to_lwpoly_group(
            [poly], marker_text, shift, text_height
        )

    # Open LWPOLYLINEs grouped by 4
    for i in range(0, len(open_lwpolys), 4):
        group = open_lwpolys[i : i + 4]
        new_entities += add_text_to_lwpoly_group(group, marker_text, shift, text_height)

    # --- LINEs ---
    lines = [
        e
        for e in dxf_entities
        if e.get("entity_type") == "LINE" and e.get("aci") == marker_aci_target
    ]
    for i in range(0, len(lines), 4):
        group = lines[i : i + 4]
        new_entities += add_text_to_line_group(group, marker_text, shift, text_height)

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
        coords = gas_sink_marker(
            coords, item["aci"], item["mode_text"], item["shift"], text_height
        )
    # Remove gas or sink lengths
    coords = [
        e for e in coords if e.get("layer") not in ["sink_lengths", "gas_lengths"]
    ]

    return coords
