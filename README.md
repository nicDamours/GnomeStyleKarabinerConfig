# GNOME-style shortcuts for a Windows keyboard on macOS

> **Note:** This project was written with the help of AI agents (Claude Code). The rules
> were tested with an automated test suite and checked on a real Mac, but review them
> before relying on them.

One Karabiner-Elements file (`gnome-pc-style.json`) that makes a Windows keyboard on a Mac
behave like GNOME on Linux. Physical keys: **Super** = Win, **Alt**, **Ctrl**.

## Install

1. Install the three free apps:
   - [Karabiner-Elements](https://karabiner-elements.pqrs.org/): open it and approve everything it asks for
     (driver extension and Input Monitoring).
   - [AltTab](https://alt-tab-macos.netlify.app/): keep its default shortcut (Alt+Tab).
   - [Rectangle](https://rectangleapp.com/): on first launch choose **Recommended** shortcuts.
2. Copy the rules file:
   ```sh
   mkdir -p ~/.config/karabiner/assets/complex_modifications
   cp gnome-pc-style.json ~/.config/karabiner/assets/complex_modifications/
   ```
3. Karabiner-Elements → **Complex Modifications** → **Add predefined rule** →
   "GNOME-style shortcuts for a Windows keyboard" → **Enable All**.

## macOS settings

- **Keyboard layout**: System Settings → Keyboard → Input Sources → add **Canadian French – PC**
  (remove the others if you like).
- **Workspaces**: System Settings → Keyboard → Keyboard Shortcuts → Mission Control →
  keep **Move left a space** (Ctrl+←) and **Move right a space** (Ctrl+→) turned **on**.
  You need at least two Spaces (Mission Control → `+`).
- **Keyboard type (important for Canadian and most European keyboards)**: Karabiner shows up
  to macOS as its own virtual keyboard, ANSI (US-style) by default. On an ISO keyboard
  (one with an extra key next to left Shift, like Canadian French) that puts some keys in the
  wrong place: for example `{ }` stop typing with AltGr, or the key left of `1` swaps
  with the one next to left Shift. Fix: Karabiner-Elements → Virtual Keyboard →
  Keyboard type → **ISO**.
- **Alt+F4 does nothing?** Open Karabiner-EventViewer and press F4. If it shows a media key
  instead of `f4`, your keyboard's Fn-lock is on (often toggled with Fn+Esc).
- **Mouse scrolling**: System Settings → Mouse → turn off **Natural scrolling**.

## What you get

| Keys | Where | Does |
|---|---|---|
| Ctrl+C/V/X/Z/A/S/F/T/W/L/Q… (+Shift) | everywhere except terminals | the Mac Cmd version |
| Ctrl+←/→ (+Shift) | everywhere | jump by word |
| Ctrl+Backspace/Delete | except terminals | delete by word |
| Home / End (+Shift to select) | except terminals and browsers | line start & end |
| Ctrl+Home / Ctrl+End (+Shift to select) | except terminals | document start & end |
| Ctrl+F4 | except terminals | close tab |
| Ctrl+click (+Shift) | everywhere | Cmd+click: open link in new tab, add to selection |
| Ctrl+Shift+C / Ctrl+Shift+V | terminals | copy / paste (other Ctrl keys stay real Ctrl) |
| Super alone | everywhere | Spotlight |
| Alt+Tab | everywhere | switch windows (AltTab) |
| Alt+F4 | everywhere | close window |
| Super+H / Super+L | everywhere | minimize / lock screen |
| Super+← / → / ↑ / ↓ | everywhere | snap left / right, maximize, restore (Rectangle) |
| Super+Page Up/Down, Ctrl+Alt+←/→ | everywhere | previous / next workspace |
| Print Screen | everywhere | screenshot tool |
| Ctrl+Alt+T | everywhere | open Terminal |

Right Alt (AltGr) is never touched, so `[ ] { } @ |` etc. type normally.
Terminals recognised: Terminal, iTerm2, Ghostty, kitty, Alacritty, WezTerm, Warp.

## Test checklist on the Mac

1. In Safari/Chrome, **Ctrl+Alt+T** opens Terminal and **Ctrl+Alt+←/→** switches Spaces.
2. **Ctrl+Shift+T** reopens a closed browser tab; in Terminal, **Ctrl+C** stops `sleep 100`
   and **Ctrl+Shift+C/V** copy/paste.
3. Type `[ ] { } @ # | \ < > « »` with AltGr in a text editor — all land as on Linux.
4. **Home/End in TextEdit** go to line start/end; **in a browser** they keep the browser's own
   behaviour (top/bottom of the page) and never trigger Back/Forward.
5. **Alt+F4** closes a window (see the Function Keys setting above if not).

## Editing

Change rules in `build.py`, then run `python3 build.py` and re-copy the JSON.
Using another terminal app? Edit `open -a Terminal` in `build.py` (e.g. `open -a Ghostty`).
Tests: `python3 -m pytest -q`.

## Known gaps

- Home/End don't go to line start/end inside browser text fields (that mapping would be
  Back/Forward on the page). Browsers recognised: Safari, Chrome, Firefox, Edge, Brave, Arc,
  Vivaldi, Opera, Chromium, Zen.
- Middle-click paste of selected text (Linux primary selection) doesn't exist on macOS.
- Ctrl+H becomes Cmd+H, which **hides** the app on a Mac (on Linux it's history/replace).
- Alt+F4 sends Cmd+W, so in a browser it closes the tab rather than the whole window.
- Terminals built into VS Code or JetBrains aren't separate apps, so Ctrl+C there becomes
  Cmd+C (copy) and doesn't stop a running program. No key sends a real Ctrl+C there yet.
- App-specific Ctrl shortcuts that differ on Mac (e.g. Ctrl+H, Ctrl+, for settings) follow
  the Mac app's Cmd shortcut, not the Linux one.
