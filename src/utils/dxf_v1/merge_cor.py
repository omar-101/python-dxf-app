from copy import deepcopy


def merge_entities_with_dashed(entities1, entities2):
    """
    Merge entities1 and entities2.
    - entities1 remains unchanged.
    - entities2 is always marked as dashed.
    - entities2 layers are entities1 layers + 1 (numeric).

    Assumes entities1 and entities2 are aligned by index.

    Args:
        entities1 (list): Primary entities
        entities2 (list): Secondary entities (will be dashed)

    Returns:
        list: Merged entities
    """
    dashed_entities2 = deepcopy(entities2)

    for i, ent in enumerate(dashed_entities2):
        ent["dashed"] = True

        # Get corresponding layer from entities1, default "0" if not enough entities
        base_layer = entities1[i].get("layer", "0") if i < len(entities1) else "0"

        # Try to parse layer as integer, else keep original string + "_dashed"
        try:
            ent["layer"] = str(int(base_layer) + 1)
        except ValueError:
            ent["layer"] = f"{base_layer}_dashed"

    return entities1 + dashed_entities2
