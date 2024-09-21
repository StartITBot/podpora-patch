
# pep8 violation enhances code readability
# noinspection PyPep8Naming
def merge_patch(minor_patch: dict, MAJOR_patch: dict) -> dict:
    assert isinstance(minor_patch, dict), "Only dict can be valid patch"
    assert isinstance(MAJOR_patch, dict), "Only dict can be valid patch"

    result = {}
    keys = list(minor_patch.keys())
    for item in MAJOR_patch.keys():
        if item not in keys:
            keys.append(item)

    for patch_key in keys:
        if patch_key not in MAJOR_patch:
            result[patch_key] = minor_patch[patch_key]
            continue

        if patch_key not in minor_patch:
            result[patch_key] = MAJOR_patch[patch_key]
            continue

        MAJOR_value = MAJOR_patch[patch_key]
        minor_value = minor_patch[patch_key]

        if not isinstance(MAJOR_value, dict) or "*" in MAJOR_value:
            result[patch_key] = MAJOR_value
            continue

        if not isinstance(minor_value, dict):
            minor_value = {}

        if "*" in minor_value:
            if isinstance(minor_value["*"], dict):
                result[patch_key] = {"*": merge_patch(minor_value["*"], MAJOR_value)}
                continue

            minor_value = {}

        result[patch_key] = merge_patch(minor_value, MAJOR_value)

    return result
