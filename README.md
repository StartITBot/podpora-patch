# PODPORA:PATCH Format Specification

This specification describes the PODPORA:PATCH format and its processing rules. The format is mainly designed 
for use with the [HTTP PATCH method](https://www.rfc-editor.org/rfc/rfc5789), allowing users to describe a series of 
changes to the content of a target resource.

It's a direct alternative to [JSON Patch](https://www.rfc-editor.org/rfc/rfc6902) and 
[JSON Merge Patch](https://www.rfc-editor.org/rfc/rfc7396/), aimed at reducing storage usage and providing enhanced 
support for list operations in JSON.

## Table of Contents

* [Abstract](#podporapatch-format-specification)
* [Table of Contents](#table-of-contents)
* [Introduction](#introduction)
* [MIME media type](#mime-media-type)
* [PATCH Structure](#patch-structure)
* [PATCH Operations for Dictionaries](#patch-operations-for-dictionaries)
  * [Rule 1: Overwrite Values](#rule-1-overwrite-values)
  * [Rule 2: The Star Symbol (`*`) in PATCH Keys](#rule-2-the-star-symbol--in-patch-keys)
    * [Rule 2.1: Deletion with `*`](#rule-21-deletion-with-)
    * [Rule 2.2: Overwrite or Create with `*`](#rule-22-overwrite-or-create-with-)
  * [Rule 3: Edit Action](#rule-3-edit-action)
* [PATCH Operations for Lists](#patch-operations-for-lists)
  * [Rule 4: Direct List Modification](#rule-4-direct-list-modification)
  * [Rule 5: Handling Lists with Serial Keys](#rule-5-handling-lists-with-serial-keys)
    * [Rule 5.1: Editing List Items by Serial](#rule-51-editing-list-items-by-serial)
    * [Rule 5.2: Deleting List Items by Serial](#rule-52-deleting-list-items-by-serial)
    * [Rule 5.3: Creating New Items with Serial](#rule-53-creating-new-items-with-serial)
    * [Rule 5.4: Invalid Serial Handling](#rule-54-invalid-serial-handling)

## Introduction

The PODPORA:PATCH format represents the changes to be made to a target JSON document in a format similar to the document 
being modified, providing a flexible and storage-efficient way to modify JSON objects, with enhanced handling for lists 
through the use of serial keys. Implementations should take care to handle edge cases, such as invalid serial keys and 
mismatched types, according to the rules described in this document.

Definitions used in this specification:

- **JSON**: The target data structure, which may be a dictionary or list, that PATCH will modify.
- **PATCH**: A dictionary-based file format used to describe changes to be applied to a JSON object.

## MIME media type

The `application/podpora-patch+json` media type allows clients to signal that they want the server to determine 
which specific changes should be made to a resource. The server is responsible for assessing whether a change is 
appropriate and whether the client is authorized to request it. The process for making these determinations falls 
outside the scope of this specification.

Resources that utilize addressed media type must adhere to the "application/json" media type. 
As a result, they are subject to the same encoding rules and considerations outlined in 
[Section 8 of RFC7159](https://www.rfc-editor.org/rfc/rfc7159).

Also, all security concerns mentioned in [Section 5 of RFC5789](https://www.rfc-editor.org/rfc/rfc5789) apply when 
using the HTTP PATCH method with the "application/podpora-patch+json" media type.

## PATCH Structure

- **PATCH** is always represented as a dictionary.
- Each key in PATCH corresponds to a key in the target JSON object.
- PATCH operations can manipulate both dictionaries and lists within JSON.

### Rule 0: Ignoring the Underscore Key (`_`)

If a key in PATCH is named `"_"`, it is always ignored unless explicitly handled, as described in later sections.

## PATCH Operations for Dictionaries

### Rule 1: Overwrite Values

If the value in PATCH is not an object, the corresponding value in JSON is overwritten:

#### Example 1:
```py
JSON = {"a": 1}
PATCH = {"a": 6}
Result: JSON = {"a": 6}
```

#### Example 2:
```py
JSON = {}
PATCH = {"a": [{"a": 3}, {"a": 4}]}
Result: JSON = {"a": [{"a": 3}, {"a": 4}]}
```

### Rule 2: The Star Symbol (`*`) in PATCH Keys

#### Rule 2.1: Deletion with `*`

If the key `*` is set to `null`, the corresponding key in the target JSON is deleted:

#### Example:
```py
JSON = {"a": 1}
PATCH = {"a": {"*": null}}
Result: JSON = {}
```

If no `*` symbol is present in PATCH, the value is simply overwritten, even if the value is `null`.

#### Example:
```py
JSON = {"a": 1}
PATCH = {"a": null}
Result: JSON = {"a": null}
```

#### Rule 2.2: Overwrite or Create with `*`

If the key `*` is not `null`, it represents an overwrite or creation of a new value, based on whether the target exists:

#### Example 1:
```py
JSON = {"a": 1}
PATCH = {"a": {"*": {"foo": "bar"}}}
Result: JSON = {"a": {"foo": "bar"}}
```

#### Example 2:
```py
JSON = {}
PATCH = {"a": {"*": {"foo": "bar"}}}
Result: JSON = {"a": {"foo": "bar"}}
```

Note: When using `*`, additional keys in the PATCH object are ignored:

```py
PATCH = {"a": {"*": 4, "foo": "bar"}}
Equivalent to: {"a": {"*": 4}}
```

### Rule 3: Edit Action

If the value in PATCH is a dictionary, it performs an edit on the target JSON:

#### Example:
```py
JSON = {
    "a": 23,
    "b": {"c": 123, "d": 432}
}
PATCH = {"b": {"d": 999}}
Result: JSON = {
    "a": 23,
    "b": {"c": 123, "d": 999}
}
```

#### Rule 3.1: Recursion for Nested Objects

PATCH operations are applied recursively to nested objects:

#### Example (Invalid):
```py
JSON = {"a": 23}
PATCH = {"a": {"foo": "bar"}}
Error: "Invalid patch, as '23' is not a dictionary or list."
```

To resolve this error, use `*` for overwriting:

```py
PATCH = {"a": {"*": {"foo": "bar"}}}
```

Other actions like, for example, deletion within nested objects also work recursively:

#### Example:
```py
JSON = {
    "a": 23,
    "b": {"c": 123, "d": 432}
}
PATCH = {"b": {"d": {"*": null}}}
Result: JSON = {
    "a": 23,
    "b": {"c": 123}
}
```

## PATCH Operations for Lists

### Rule 4: Direct List Modification

Lists in JSON can be directly modified using PATCH, which replaces or edits list elements:

#### Example:
```py
JSON = {
    "a": 23,
    "b": [{"foo": "bar"}, {"foo": "bar"}, {"foo": "bar"}]
}
PATCH = {
    "b": [{"foo": "bar"}, {"foo": "bar"}]
}
Result: JSON = {
    "a": 23,
    "b": [{"foo": "bar"}, {"foo": "bar"}]
}
```

### Rule 5: Handling Lists with Serial Keys

For more complex list manipulations, each item in the list can be assigned a serial key (`_`), which is a unique identifier:

#### Example:
```py
JSON = {
    "a": 23,
    "b": [
        {"_": "111111", "foo": "bar"},
        {"_": "222222", "foo": "bar"},
        {"_": "333333", "foo": "bar"}
    ]
}
```

#### Rule 5.1: Editing List Items by Serial

PATCH can modify list items using their serials:

#### Example 1:
```py
PATCH = {"b": {"222222": {"foo": "baz"}}}
Result: JSON = {
    "a": 23,
    "b": [
        {"_": "111111", "foo": "bar"},
        {"_": "222222", "foo": "baz"},
        {"_": "333333", "foo": "bar"}
    ]
}
```

#### Rule 5.2: Deleting List Items by Serial

PATCH can delete list items using their serial:

#### Example:
```py
PATCH = {"b": {"222222": {"*": null}}}
Result: JSON = {
    "a": 23,
    "b": [
        {"_": "111111", "foo": "bar"},
        {"_": "333333", "foo": "bar"}
    ]
}
```

#### Rule 5.3: Creating New Items with Serial

New list items can be created using the serial key and the `*` symbol:

#### Example:
```py
PATCH = {"b": {"999999": {"*": {"foo": "bar"}}}}
Result: JSON = {
    "a": 23,
    "b": [
        {"_": "111111", "foo": "bar"},
        {"_": "222222", "foo": "bar"},
        {"_": "333333", "foo": "bar"},
        {"_": "999999", "foo": "bar"}
    ]
}
```

#### Rule 5.4: Invalid Serial Handling

PATCH implementations should either ignore or throw errors for non-existent serials:

```py
PATCH = {"b": {"999999": {"foo": "bar"}}}  // Should throw or be ignored
```

However, using the `*` method to create new items is valid:

```py
PATCH = {"b": {"999999": {"*": {"foo": "bar"}}}}  // Creates a new item
```
