def add_length_layer_with_shifts_note(
    entities,
    shifts_array=None,
    layer_name="LENGTHS",
    round_lengths=True,
    text_height=16,
    sink_size=4,  # number of LENGTHS per sink
):
    from copy import deepcopy
    import math

    new_entities = deepcopy(entities)
    aci_to_offset = {item[0]: item[1] for item in shifts_array} if shifts_array else {}

    sink_counter = 0
    sink_index = 1

    for ent in entities:
        etype = ent.get("entity_type")
        aci = ent.get("aci", 0)

        # Calculate midpoint
        if etype == "LINE":
            start, end = ent["start"], ent["end"]
            length_val = math.sqrt(
                (end["x"] - start["x"]) ** 2 + (end["y"] - start["y"]) ** 2
            )
            mid_x = (start["x"] + end["x"]) / 2
            mid_y = (start["y"] + end["y"]) / 2
        elif etype == "LWPOLYLINE":
            pts = ent.get("vertices", [])
            if len(pts) < 2:
                continue
            draw_pts = pts + [pts[0]] if ent.get("closed") else pts
            seg_lengths = [
                math.sqrt(
                    (draw_pts[i + 1]["x"] - draw_pts[i]["x"]) ** 2
                    + (draw_pts[i + 1]["y"] - draw_pts[i]["y"]) ** 2
                )
                for i in range(len(draw_pts) - 1)
            ]
            length_val = sum(seg_lengths)
            half = length_val / 2
            cum = 0
            for i, seg in enumerate(seg_lengths):
                if cum + seg >= half:
                    ratio = (half - cum) / seg
                    mid_x = draw_pts[i]["x"] + ratio * (
                        draw_pts[i + 1]["x"] - draw_pts[i]["x"]
                    )
                    mid_y = draw_pts[i]["y"] + ratio * (
                        draw_pts[i + 1]["y"] - draw_pts[i]["y"]
                    )
                    break
                cum += seg
        else:
            continue

        # Round length
        length_text = str(round(length_val)) if round_lengths else str(length_val)
        if aci in aci_to_offset:
            length_text += f"({aci_to_offset[aci]})"

        # Determine sink_index
        if aci == 152:
            sink_counter += 1
            if sink_counter > sink_size:
                sink_counter = 1
                sink_index += 1
        else:
            sink_index = 0  # not a sink

        new_entities.append(
            {
                "entity_type": "TEXT",
                "text": length_text,
                "color": 256,
                "layer": layer_name,
                "aci": 0,
                "is_electric_gas_sink": aci == 152,
                "sink_index": sink_index if aci == 152 else None,
                "position": {"x": mid_x, "y": mid_y, "z": 0.0},
                "height": text_height,
            }
        )

    return new_entities
