from constants import modes


def add_length_layer_with_shifts_note(
    entities,
    shifts=None,
    round_lengths=True,
    text_height=any,
):
    from copy import deepcopy
    import math

    new_entities = deepcopy(entities)
    aci_to_offset = {item[0]: item[1] for item in shifts} if shifts else {}
    modes_by_value = {v: k for k, v in modes.MODES.items()}

    gas_sink_shifts = (
        {
            aci: modes_by_value[mode]
            for aci, shift, mode in shifts
            if mode in (modes.MODES["sink"], modes.MODES["gas"])
        }
        if shifts
        else {}
    )

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
        new_entities.append(
            {
                "entity_type": "TEXT",
                "text": length_text,
                "color": 256,
                "layer": (
                    gas_sink_shifts.get(aci, "") + "_lengths"
                    if gas_sink_shifts.get(aci)
                    else "LENGTHS"
                ),
                "aci": 0,
                "position": {"x": mid_x, "y": mid_y, "z": 0.0},
                "height": text_height,
            }
        )

    return new_entities
