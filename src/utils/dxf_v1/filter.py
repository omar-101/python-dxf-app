from constants import modes


def aci_points_to_keep(shifts):
    # shifts_set = set(shifts)  # convert to set for faster lookup
    return [shift[0] for shift in shifts if shift[2] == modes.MODES["keep_point"]]


def filter_points(entities, shifts=[]):
    acis_to_keep = aci_points_to_keep(shifts)
    return [
        ent
        for ent in entities
        if not (
            ent.get("entity_type") == "POINT" and ent.get("aci") not in acis_to_keep
        )
    ]
