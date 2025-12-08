def gas_sink_marker(entities, text_prefix="sink", text_height=16, sink_size=4):
    text_entities = []

    # Filter only electric/gas sink entities
    sinks = [e for e in entities if e.get("is_electric_gas_sink")]

    def get_entity_points(e):
        if e["entity_type"] == "LINE":
            return [(e["start"]["x"], e["start"]["y"]), (e["end"]["x"], e["end"]["y"])]
        elif e["entity_type"] in ("LWPOLYLINE", "POLYLINE"):
            return [(v["x"], v["y"]) for v in e.get("vertices", [])]
        elif e["entity_type"] == "TEXT":
            return [(e["position"]["x"], e["position"]["y"])]
        return []

    # Process sinks in groups
    for i in range(0, len(sinks), sink_size):
        group = sinks[i : i + sink_size]

        # Collect all points from all entities in the group
        all_points = []
        for e in group:
            all_points.extend(get_entity_points(e))

        if not all_points:
            continue

        # Compute bounding box center
        xs, ys = zip(*all_points)
        center_x = (min(xs) + max(xs)) / 2
        center_y = (min(ys) + max(ys)) / 2

        # Pick first and fourth text as before
        x_text = group[0]["text"]
        y_text = group[3]["text"] if len(group) > 3 else group[-1]["text"]

        # Create label at the center
        text_entities.append(
            {
                "entity_type": "TEXT",
                "text": f"{text_prefix}\n{x_text} × {y_text}",
                "position": {"x": center_x, "y": center_y, "z": 0},
                "height": text_height,
                "layer": "SINK_GAS_LAYER",
                "color": 256,
            }
        )

    # Return original entities without sinks + new labels
    return [e for e in entities if not e.get("is_electric_gas_sink")] + text_entities
