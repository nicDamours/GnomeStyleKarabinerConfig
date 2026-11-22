"""Tiny model of Karabiner-Elements complex-modification matching.

First matching manipulator wins (rules in order, manipulators in order).
Held modifiers use side-less names (control, shift, option, command) meaning
the left key, plus right_option for the right Alt / AltGr key.
"""
import re

GENERIC = {"control", "shift", "option", "command"}
SIDED = {"control": "left_control", "shift": "left_shift",
         "option": "left_option", "command": "left_command"}


def _sided(mod):
    return SIDED.get(mod, mod)


def _covers(spec, held):
    """Does modifier spec (e.g. 'option', 'left_option') match held sided key?"""
    if spec == held:
        return True
    return spec in GENERIC and held.endswith("_" + spec)


def _side_less(held):
    return held.split("_", 1)[1] if held.startswith(("left_", "right_")) else held


def _conditions_ok(manip, app):
    for cond in manip.get("conditions", []):
        hit = any(re.search(rx, app) for rx in cond.get("bundle_identifiers", []))
        if cond["type"] == "frontmost_application_if" and not hit:
            return False
        if cond["type"] == "frontmost_application_unless" and hit:
            return False
    return True


def _match(manip, key, held, app):
    frm = manip["from"]
    if frm.get("key_code") != key or not _conditions_ok(manip, app):
        return None
    mods = frm.get("modifiers", {})
    mandatory = mods.get("mandatory", [])
    optional = mods.get("optional", [])
    used = set()
    for spec in mandatory:
        found = [h for h in held if _covers(spec, h)]
        if not found:
            return None
        used.update(found)
    passthrough = []
    for h in held - used:
        if "any" in optional or any(_covers(o, h) for o in optional):
            passthrough.append(_side_less(h))
        else:
            return None
    out = []
    for item in manip.get("to", []):
        item = dict(item)
        if "key_code" in item:
            m = sorted(set(item.get("modifiers", [])) | set(passthrough))
            item.pop("modifiers", None)
            if m:
                item["modifiers"] = m
        out.append(item)
    return out


def press(doc, key, mods, app):
    held = {_sided(m) for m in mods}
    for rule in doc["rules"]:
        for manip in rule["manipulators"]:
            out = _match(manip, key, held, app)
            if out is not None:
                return out
    return None
