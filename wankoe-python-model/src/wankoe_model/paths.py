"""Shared path utilities: get/set by key path, deep merge, validation.

Single implementation used by scenario, planning, optimize and fit
(expert review 2026-08-08: previously duplicated, with bare KeyError on
mistakes). Paths are LISTS of keys (not dotted strings) because keys like
"SR.5008" or "1.1" contain dots.

Errors are actionable: a missing key raises ValueError naming the full
path, the valid sibling keys, and the closest match when one exists.
"""

from __future__ import annotations

import copy
import difflib


def dotted(path) -> str:
    return ".".join(str(k) for k in path)


def _missing_key_error(container, path, index) -> ValueError:
    key = str(path[index])
    if isinstance(container, dict):
        keys = [str(k) for k in container.keys()]
        close = difflib.get_close_matches(key, keys, n=1)
        hint = f" — did you mean '{close[0]}'?" if close else ""
        shown = ", ".join(sorted(keys)[:12])
        return ValueError(
            f"path {dotted(path)}: key '{key}' not found (valid keys here: {shown}){hint}"
        )
    return ValueError(
        f"path {dotted(path)}: cannot descend into a non-dict value at '{key}'"
    )


def get_path(node, path: list):
    """Reads a value at a key path; raises an actionable ValueError if absent."""
    current = node
    for i, key in enumerate(path):
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            raise _missing_key_error(current, path, i)
    return current


def set_path(node, path: list, value) -> None:
    """Writes a value at an EXISTING key path (guards against typos)."""
    parent = get_path(node, path[:-1]) if len(path) > 1 else node
    if not isinstance(parent, dict) or path[-1] not in parent:
        raise _missing_key_error(parent, path, len(path) - 1)
    parent[path[-1]] = value


# keys whose dict value is semantically ONE value (replaced wholesale on
# merge, never key-merged): a size curve merged key-by-key with the default
# curve would silently blend two different measurements.
ATOMIC_KEYS = {"cumulative_passing_curve"}

# collections whose members may legitimately be added by overrides
OPEN_COLLECTIONS = {("output_products",), ("production_targets",)}


def deep_merge(base: dict, override: dict, validate: bool = False, _trail: tuple = ()) -> dict:
    """Recursive merge of ``override`` onto ``base`` (both left untouched).

    With ``validate=True``, a key absent from the base raises an actionable
    ValueError (typo protection) — except underscore-prefixed keys, members
    of OPEN_COLLECTIONS, and the content of ATOMIC_KEYS.
    """
    result = copy.deepcopy(base)
    for key, value in override.items():
        known = key in result
        if (
            validate
            and not known
            and not str(key).startswith("_")
            and _trail not in OPEN_COLLECTIONS
        ):
            raise _missing_key_error(result, list(_trail) + [key], len(_trail))
        if (
            key not in ATOMIC_KEYS
            and isinstance(value, dict)
            and isinstance(result.get(key), dict)
        ):
            result[key] = deep_merge(result[key], value, validate, _trail + (key,))
        else:
            result[key] = copy.deepcopy(value)
    return result
