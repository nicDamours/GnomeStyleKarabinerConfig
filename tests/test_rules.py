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
