"""Generate gnome-pc-style.json: GNOME-style shortcuts for a Windows keyboard on macOS.

Physical keys on a Windows keyboard under macOS: Super = command, Alt = option, Ctrl = control.
Run `python3 build.py` after editing; import the JSON into Karabiner-Elements.
"""
import json
import pathlib

OUTPUT = pathlib.Path(__file__).with_name("gnome-pc-style.json")

TERMINALS = [
    r"^com\.apple\.Terminal$",
    r"^com\.googlecode\.iterm2$",
    r"^com\.mitchellh\.ghostty$",
    r"^net\.kovidgoyal\.kitty$",
    r"^(org|io)\.alacritty$",
    r"^com\.github\.wez\.wezterm$",
    r"^dev\.warp\.Warp",
]

GENERIC_KEYS = (
    [chr(c) for c in range(ord("a"), ord("z") + 1)]
    + [str(d) for d in range(10)]
    + "hyphen equal_sign open_bracket close_bracket backslash semicolon quote "
      "grave_accent_and_tilde comma period slash non_us_backslash".split()
)


def not_in_terminals():
    return [{"type": "frontmost_application_unless", "bundle_identifiers": TERMINALS}]


def manip(key, to_key, mandatory=(), optional=(), to_mods=(), conditions=None):
    frm = {"key_code": key}
    mods = {}
    if mandatory:
        mods["mandatory"] = list(mandatory)
    if optional:
        mods["optional"] = list(optional)
    if mods:
        frm["modifiers"] = mods
    to = {"key_code": to_key}
    if to_mods:
        to["modifiers"] = list(to_mods)
    m = {"type": "basic", "from": frm, "to": [to]}
    if conditions:
        m["conditions"] = conditions
    return m


def ctrl_text_rule():
    c = not_in_terminals()
    sel = ["shift"]  # Shift passes through so selection works
    ms = [
        manip("left_arrow", "left_arrow", ["control"], sel, ["option"], c),
        manip("right_arrow", "right_arrow", ["control"], sel, ["option"], c),
        manip("delete_or_backspace", "delete_or_backspace", ["control"], [], ["option"], c),
        manip("delete_forward", "delete_forward", ["control"], [], ["option"], c),
        manip("home", "up_arrow", ["control"], sel, ["command"], c),
        manip("end", "down_arrow", ["control"], sel, ["command"], c),
        manip("home", "left_arrow", [], sel, ["command"], c),
        manip("end", "right_arrow", [], sel, ["command"], c),
        manip("f4", "w", ["control"], [], ["command"], c),
    ]
    # Generic Ctrl -> Cmd. Optional is only Shift (never "any"), so Ctrl+Alt
    # combos fall through to the desktop rule.
    ms += [manip(key, key, ["control"], sel, ["command"], c) for key in GENERIC_KEYS]
    return {"description": "GNOME: Ctrl shortcuts & text editing (not in terminals)",
            "manipulators": ms}


def build():
    return {
        "title": "GNOME-style shortcuts for a Windows keyboard",
        "rules": [ctrl_text_rule()],
    }


def main():
    OUTPUT.write_text(json.dumps(build(), indent=2) + "\n")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
