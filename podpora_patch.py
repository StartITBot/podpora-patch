from typing import Any, Union

import warnings


class PointerActions:
    def __init__(self, json):
        self.json = json

    def has_key(self, key: str) -> bool:
        return key in self.json

    def remove_key(self, key: str) -> None:
        self.json.pop(key)

    def get_pointer(self, key: str) -> Any:
        return self.json[key]

    def set_pointer(self, key: str, value: Any) -> None:
        self.json[key] = value


class PointerActionsList(PointerActions):
    def __init__(self, json):
        super().__init__(json)
        self.json_as_dict = {
            cnf["_"]: cnf for cnf in json if isinstance(cnf, dict) and "_" in cnf
        }

    def has_key(self, key: str) -> bool:
        return key in self.json_as_dict

    def remove_key(self, key: str) -> None:
        self.json.remove(self.json_as_dict[key])

    def get_pointer(self, key: str) -> Any:
        return self.json_as_dict[key]

    def set_pointer(self, key: str, value: dict) -> None:
        assert isinstance(value, dict)
        if value.get("_") != key:
            value = {**value, "_": key}

        if key not in self.json_as_dict:
            self.json.append(value)
            return

        index_ = self.json.index(self.json_as_dict[key])
        self.json[index_] = value


def apply_patch(json: Union[list, dict], patch: dict):
    assert isinstance(json, (list, dict)), "You can only patch dict or list types"
    assert isinstance(patch, dict), "Only dict can be valid patch"

    func = PointerActions(json) if isinstance(json, dict) else PointerActionsList(json)

    for patch_key, patch_value in patch.items():
        if patch_key == "_":
            continue

        if not isinstance(patch_value, dict):
            if isinstance(json, list):
                raise KeyError("Cannot change type of array item")

            func.set_pointer(patch_key, patch_value)
            continue

        # Delete action
        if patch_value.get("*", 0) is None:
            if not func.has_key(patch_key):
                warnings.warn("Trying to delete object that doesn't exist anymore")
                continue

            func.remove_key(patch_key)
            continue

        # Overwrite action
        if "*" in patch_value:
            if isinstance(json, list) and not isinstance(patch_value["*"], dict):
                raise KeyError("Cannot change type of array item")

            func.set_pointer(patch_key, patch_value["*"])
            continue

        if not func.has_key(patch_key):
            warnings.warn("Trying to edit object that doesn't exist anymore")
            continue

        before_value = func.get_pointer(patch_key)
        if not isinstance(before_value, (dict, list)):
            raise KeyError("Trying to edit non-patchable object")

        apply_patch(before_value, patch_value)

    return json
