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

# Home/End are left alone here: Cmd+left/right means Back/Forward on a web page.
BROWSERS = [
    r"^com\.apple\.Safari",
    r"^com\.google\.Chrome",
    r"^org\.mozilla\.firefox",
    r"^com\.microsoft\.edgemac",
    r"^com\.brave\.Browser",
    r"^company\.thebrowser\.Browser$",
    r"^com\.vivaldi\.Vivaldi$",
    r"^com\.operasoftware\.Opera",
    r"^org\.chromium\.Chromium$",
    r"^app\.zen-browser\.zen$",
]

GENERIC_KEYS = (
    [chr(c) for c in range(ord("a"), ord("z") + 1)]
    + [str(d) for d in range(10)]
    + "hyphen equal_sign open_bracket close_bracket backslash semicolon quote "
      "grave_accent_and_tilde comma period slash non_us_backslash".split()
)


def not_in_terminals():
    return [{"type": "frontmost_application_unless", "bundle_identifiers": TERMINALS}]


def not_in_browsers():
    return [{"type": "frontmost_application_unless", "bundle_identifiers": BROWSERS}]


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
        manip("home", "left_arrow", [], sel, ["command"], c + not_in_browsers()),
        manip("end", "right_arrow", [], sel, ["command"], c + not_in_browsers()),
        manip("f4", "w", ["control"], [], ["command"], c),
    ]
    # Generic Ctrl -> Cmd. Optional is only Shift (never "any"), so Ctrl+Alt
    # combos fall through to the desktop rule.
    ms += [manip(key, key, ["control"], sel, ["command"], c) for key in GENERIC_KEYS]
    return {"description": "GNOME: Ctrl shortcuts & text editing (not in terminals)",
            "manipulators": ms}


def terminal_rule():
    c = [{"type": "frontmost_application_if", "bundle_identifiers": TERMINALS}]
    return {"description": "GNOME: Ctrl+Shift+C/V copy & paste in terminals",
            "manipulators": [manip(key, key, ["control", "shift"], [], ["command"], c)
                             for key in ("c", "v")]}


def desktop_rule():
    # Applies in every app. Alt combos use left_option only: right Alt is AltGr.
    cmd, ctrl_alt, rect = ["command"], ["control", "left_option"], ["control", "option"]
    super_alone = [
        {"type": "basic",
         "from": {"key_code": key, "modifiers": {"optional": ["any"]}},
         "to": [{"key_code": key}],
         "to_if_alone": [{"key_code": "spacebar", "modifiers": ["left_command"]}]}
        for key in ("left_command", "right_command")
    ]
    ms = super_alone + [
        manip("f4", "w", ["left_option"], [], ["command"]),            # Alt+F4 close window
        manip("h", "m", cmd, [], ["command"]),                          # Super+H minimize
        manip("l", "q", cmd, [], ["control", "command"]),               # Super+L lock
        # Super+arrows -> Rectangle defaults
        manip("left_arrow", "left_arrow", cmd, [], rect),
        manip("right_arrow", "right_arrow", cmd, [], rect),
        manip("up_arrow", "return_or_enter", cmd, [], rect),
        manip("down_arrow", "delete_or_backspace", cmd, [], rect),
        # Workspaces -> macOS Spaces (Ctrl+arrows)
        manip("page_up", "left_arrow", cmd, [], ["control"]),
        manip("page_down", "right_arrow", cmd, [], ["control"]),
        manip("left_arrow", "left_arrow", ctrl_alt, [], ["control"]),
        manip("right_arrow", "right_arrow", ctrl_alt, [], ["control"]),
        manip("print_screen", "5", [], [], ["command", "shift"]),      # screenshot tool
        {"type": "basic",                                               # Ctrl+click = Cmd+click
         "from": {"pointing_button": "button1",
                  "modifiers": {"mandatory": ["control"], "optional": ["shift"]}},
         "to": [{"pointing_button": "button1", "modifiers": ["command"]}]},
        {"type": "basic",                                               # Ctrl+Alt+T terminal
         "from": {"key_code": "t", "modifiers": {"mandatory": ctrl_alt}},
         "to": [{"shell_command": "open -a Terminal"}]},
    ]
    return {"description": "GNOME: desktop & window shortcuts (Super, Alt+F4, workspaces)",
            "manipulators": ms}


def build():
    return {
        "title": "GNOME-style shortcuts for a Windows keyboard",
        "rules": [ctrl_text_rule(), terminal_rule(), desktop_rule()],
    }


def main():
    OUTPUT.write_text(json.dumps(build(), indent=2) + "\n")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
