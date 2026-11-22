import pytest

import build
from karabiner_sim import press

SAFARI = "com.apple.Safari"
TERMINAL = "com.apple.Terminal"
TERMINAL_SAMPLES = [
    "com.apple.Terminal", "com.googlecode.iterm2", "com.mitchellh.ghostty",
    "net.kovidgoyal.kitty", "org.alacritty", "io.alacritty",
    "com.github.wez.wezterm", "dev.warp.Warp-Stable",
]
GENERIC_KEYS = (
    [chr(c) for c in range(ord("a"), ord("z") + 1)]
    + [str(d) for d in range(10)]
    + "hyphen equal_sign open_bracket close_bracket backslash semicolon quote "
      "grave_accent_and_tilde comma period slash non_us_backslash".split()
)


@pytest.fixture(scope="module")
def doc():
    return build.build()


def k(key, *mods):
    out = {"key_code": key}
    if mods:
        out["modifiers"] = sorted(mods)
    return [out]


# --- Task 1: Ctrl shortcuts & text editing (not in terminals) ---

def test_ctrl_c_is_cmd_c_in_safari(doc):
    assert press(doc, "c", {"control"}, SAFARI) == k("c", "command")


def test_ctrl_shift_t_is_cmd_shift_t(doc):
    assert press(doc, "t", {"control", "shift"}, SAFARI) == k("t", "command", "shift")


@pytest.mark.parametrize("app", TERMINAL_SAMPLES)
def test_ctrl_c_untouched_in_terminal(doc, app):
    assert press(doc, "c", {"control"}, app) is None


def test_generic_rule_ignores_ctrl_alt(doc):
    out = press(doc, "t", {"control", "option"}, SAFARI)
    assert not (out and "command" in out[0].get("modifiers", []))


@pytest.mark.parametrize("arrow", ["left_arrow", "right_arrow"])
def test_ctrl_arrows_jump_words(doc, arrow):
    assert press(doc, arrow, {"control"}, SAFARI) == k(arrow, "option")
    assert press(doc, arrow, {"control", "shift"}, SAFARI) == k(arrow, "option", "shift")


@pytest.mark.parametrize("key", ["delete_or_backspace", "delete_forward"])
def test_ctrl_backspace_delete_word(doc, key):
    assert press(doc, key, {"control"}, SAFARI) == k(key, "option")


def test_home_end_line(doc):
    assert press(doc, "home", set(), SAFARI) == k("left_arrow", "command")
    assert press(doc, "end", set(), SAFARI) == k("right_arrow", "command")
    assert press(doc, "home", {"shift"}, SAFARI) == k("left_arrow", "command", "shift")
    assert press(doc, "end", {"shift"}, SAFARI) == k("right_arrow", "command", "shift")


def test_ctrl_home_end_document(doc):
    assert press(doc, "home", {"control"}, SAFARI) == k("up_arrow", "command")
    assert press(doc, "end", {"control"}, SAFARI) == k("down_arrow", "command")
    assert press(doc, "end", {"control", "shift"}, SAFARI) == k("down_arrow", "command", "shift")


def test_ctrl_f4_closes_tab(doc):
    assert press(doc, "f4", {"control"}, SAFARI) == k("w", "command")


@pytest.mark.parametrize("key", GENERIC_KEYS)
def test_generic_covers_keys(doc, key):
    assert press(doc, key, {"control"}, SAFARI) == k(key, "command")


# --- Task 2: Terminal copy & paste ---

@pytest.mark.parametrize("app", TERMINAL_SAMPLES)
@pytest.mark.parametrize("key", ["c", "v"])
def test_terminal_ctrl_shift_c_v(doc, app, key):
    assert press(doc, key, {"control", "shift"}, app) == k(key, "command")


def test_terminal_other_ctrl_shift_untouched(doc):
    assert press(doc, "t", {"control", "shift"}, TERMINAL) is None


def test_ctrl_shift_c_in_safari_is_cmd_shift_c(doc):
    assert press(doc, "c", {"control", "shift"}, SAFARI) == k("c", "command", "shift")


def test_terminal_lists_identical(doc):
    lists = [cond["bundle_identifiers"]
             for rule in doc["rules"] for m in rule["manipulators"]
             for cond in m.get("conditions", []) if "bundle_identifiers" in cond]
    types = {cond["type"] for rule in doc["rules"] for m in rule["manipulators"]
             for cond in m.get("conditions", [])}
    assert "frontmost_application_if" in types
    assert all(lst == build.TERMINALS for lst in lists)


# --- Task 3: Desktop & window shortcuts ---

BOTH = [SAFARI, TERMINAL]


def desktop_rule(doc):
    return next(r for r in doc["rules"] if r["description"].startswith("GNOME: desktop"))


@pytest.mark.parametrize("key", ["left_command", "right_command"])
def test_super_alone_spotlight(doc, key):
    m = next(m for m in desktop_rule(doc)["manipulators"] if m["from"]["key_code"] == key)
    assert m["to"] == [{"key_code": key}]
    assert m["to_if_alone"] == [{"key_code": "spacebar", "modifiers": ["left_command"]}]
    assert m["from"]["modifiers"]["optional"] == ["any"]


@pytest.mark.parametrize("app", BOTH)
def test_alt_f4_closes_window(doc, app):
    assert press(doc, "f4", {"option"}, app) == k("w", "command")


@pytest.mark.parametrize("app", BOTH)
def test_super_h_minimize(doc, app):
    assert press(doc, "h", {"command"}, app) == k("m", "command")


@pytest.mark.parametrize("app", BOTH)
def test_super_l_lock(doc, app):
    assert press(doc, "l", {"command"}, app) == k("q", "command", "control")


@pytest.mark.parametrize("app", BOTH)
def test_super_arrows_rectangle(doc, app):
    assert press(doc, "left_arrow", {"command"}, app) == k("left_arrow", "control", "option")
    assert press(doc, "right_arrow", {"command"}, app) == k("right_arrow", "control", "option")
    assert press(doc, "up_arrow", {"command"}, app) == k("return_or_enter", "control", "option")
    assert press(doc, "down_arrow", {"command"}, app) == k("delete_or_backspace", "control", "option")


@pytest.mark.parametrize("app", BOTH)
def test_workspaces(doc, app):
    assert press(doc, "page_up", {"command"}, app) == k("left_arrow", "control")
    assert press(doc, "page_down", {"command"}, app) == k("right_arrow", "control")
    assert press(doc, "left_arrow", {"control", "option"}, app) == k("left_arrow", "control")
    assert press(doc, "right_arrow", {"control", "option"}, app) == k("right_arrow", "control")


@pytest.mark.parametrize("app", BOTH)
def test_print_screen(doc, app):
    assert press(doc, "print_screen", set(), app) == k("5", "command", "shift")


@pytest.mark.parametrize("app", BOTH)
def test_ctrl_alt_t_terminal(doc, app):
    assert press(doc, "t", {"control", "option"}, app) == [{"shell_command": "open -a Terminal"}]


def test_right_alt_never_remapped(doc):
    for rule in doc["rules"]:
        for m in rule["manipulators"]:
            assert "right_option" not in m["from"].get("modifiers", {}).get("mandatory", [])
    keys = GENERIC_KEYS + ["f4", "left_arrow", "right_arrow", "t"]
    for key in keys:
        for mods in ({"right_option"}, {"right_option", "shift"}):
            assert press(doc, key, mods, SAFARI) is None, (key, mods)


def test_no_cross_rule_overlap(doc):
    """Karabiner may reorder rules on enable: results must not depend on rule order."""
    reversed_doc = {"rules": list(reversed(doc["rules"]))}
    for rule in doc["rules"]:
        for m in rule["manipulators"]:
            key = m["from"].get("key_code") or m["from"]["pointing_button"]
            mand = m["from"].get("modifiers", {}).get("mandatory", [])
            base = {x.replace("left_", "") for x in mand}
            for extra in (set(), {"shift"}):
                for app in BOTH:
                    held = base | extra
                    assert press(doc, key, held, app) == press(reversed_doc, key, held, app), \
                        (key, held, app)


# --- Final review fix: Ctrl+click ---

@pytest.mark.parametrize("app", BOTH)
def test_ctrl_click_is_cmd_click(doc, app):
    assert press(doc, "button1", {"control"}, app) == [{"pointing_button": "button1", "modifiers": ["command"]}]
    assert press(doc, "button1", {"control", "shift"}, app) == \
        [{"pointing_button": "button1", "modifiers": ["command", "shift"]}]


def test_right_ctrl_works_like_left(doc):
    assert press(doc, "c", {"right_control"}, SAFARI) == k("c", "command")
