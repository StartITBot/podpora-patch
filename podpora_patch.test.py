import warnings
import copy
from podpora_patch import apply_patch

warnings.filterwarnings("error")


def test(config, patch, expected):
    cnf1 = copy.deepcopy(config)
    cnf2 = copy.deepcopy(config)
    print(expected)
    try:
        print(apply_patch(cnf1, patch))
        print()
        return apply_patch(cnf2, patch) == expected
    except Exception as e:
        print(e.__class__)
        print()
        return e.__class__ == expected


def main():
    c1 = {
        "b": 7,
        "c": {
            "d": 8,
            "e": 9,
        },
    }

    # Edit
    assert test(c1, {"c": {"d": 3}}, {"b": 7, "c": {"d": 3, "e": 9}}), "Failed test 1"

    # Overwrite with *
    assert test(c1, {"c": {"*": {"d": 3}}}, {"b": 7, "c": {"d": 3}}), "Failed test 2"

    c2 = {
        "a": [
            {
                "_": "123456",
                "b": 1,
            },
            {
                "_": "654321",
                "b": 2,
            },
        ]
    }

    # Edit by serial
    assert test(
        c2,
        {"a": {"123456": {"b": 3}}},
        {"a": [{"_": "123456", "b": 3}, {"_": "654321", "b": 2}]},
    ), "Failed test 3"

    # Edit by serial, serial not found
    assert test(
        c2,
        {"a": {"999999": {"b": 3}}},
        UserWarning,
    ), "Failed test 4"

    # Overwrite by serial - can be used as addition
    assert test(
        c2,
        {"a": {"999999": {"*": {"b": 3}}}},
        {
            "a": [
                {"_": "123456", "b": 1},
                {"_": "654321", "b": 2},
                {"_": "999999", "b": 3},
            ]
        },
    ), "Failed test 5"

    c = {
        "a": 1,
        "b": 2,
        "c": 3,
    }

    # Edit, nothing unusual
    assert test(c, {"a": None}, {"a": None, "b": 2, "c": 3}), "Failed test 6"

    # Special notation {"*": None} - delete key
    assert test(c, {"a": {"*": None}}, {"b": 2, "c": 3}), "Failed test 7"


if __name__ == "__main__":
    main()
