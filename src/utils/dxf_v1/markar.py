from constants import modes


def middle_left_position(vertices, offset_x=10):
    """
    Returns coordinates near the middle-left of a polygon.
    """
    xs = [v["x"] for v in vertices]
    ys = [v["y"] for v in vertices]
    x = min(xs) + offset_x  # left edge + offset
    y = sum(ys) / len(ys)  # vertical middle
    return x, y


def add_text_to_boxes_middle_left(boxes, marker_text, text_height):
    """
    Adds TEXT entities near the middle-left of each closed LWPOLYLINE box.
    """
    new_entities = []
    for i, box in enumerate(boxes, start=1):
        vertices = box.get("vertices", [])
        if len(vertices) < 2:
            continue
        x, y = middle_left_position(vertices)
        text_entity = {
            "entity_type": "TEXT",
            "layer": "sink/gas",
            "text": marker_text,
            "position": {
                "x": x,
                "y": y,
                "z": 0,
            },
            "height": text_height,
            "rotation": 0,
            "aci": box.get("aci", 152),
        }
        new_entities.append(text_entity)
    return new_entities


def middle_left_position_line_box(lines, offset_x=10):
    """
    Returns coordinates near the middle-left of a box made of 4 LINEs.
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
    x = min(xs) + offset_x
    y = sum(ys) / len(ys)
    return x, y


def add_text_to_line_boxes_middle_left(line_boxes, marker_text, text_height):
    """
    Adds TEXT entities near the middle-left of each LINE-based box.
    """
    new_entities = []
    for i, lines in enumerate(line_boxes, start=1):
        x, y = middle_left_position_line_box(lines)
        text_entity = {
            "entity_type": "TEXT",
            "layer": "sink/gas",
            "text": marker_text,
            "position": {
                "x": x,
                "y": y,
                "z": 0,
            },
            "height": text_height,
            "rotation": 0,
            "aci": lines[0].get("aci", 152) if lines else 152,
        }
        new_entities.append(text_entity)
    return new_entities


def gas_sink_marker(
    dxf_entities, marker_aci_target=152, marker_text=any, text_height=any
):
    """
    Adds TEXT to boxes (LWPOLYLINE or 4 LINEs) near the middle-left.
    """
    # LWPOLYLINE boxes
    lwpolys = [
        e
        for e in dxf_entities
        if e.get("entity_type") == "LWPOLYLINE"
        and e.get("closed")
        and e.get("aci") == marker_aci_target
    ]
    text_lwpoly = add_text_to_boxes_middle_left(lwpolys, marker_text, text_height)

    # LINE boxes
    lines = [
        e
        for e in dxf_entities
        if e.get("entity_type") == "LINE" and e.get("aci") == marker_aci_target
    ]
    line_boxes = [
        lines[i : i + 4] for i in range(0, len(lines), 4)
    ]  # simple 4-line grouping
    text_lines = add_text_to_line_boxes_middle_left(
        line_boxes, marker_text, text_height
    )

    # Merge
    merged_entities = dxf_entities + text_lwpoly + text_lines
    return merged_entities


def create_markers(coords, shifts, text_height):
    modes_by_value = {v: k for k, v in modes.MODES.items()}

    # Filter only gas/sink modes and add mode_text
    gas_sink_shifts = [
        {
            "aci": aci,
            "shift": shift,
            "mode": mode,
            "mode_text": modes_by_value[mode],
        }
        for aci, shift, mode in shifts
        if mode == modes.MODES["sink"] or mode == modes.MODES["gas"]
    ]

    # Apply markers
    for item in gas_sink_shifts:
        coords = gas_sink_marker(coords, item["aci"], item["mode_text"], text_height)

    return coords
