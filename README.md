# Layout Switcher

Auto-detect and correct wrong keyboard layout on macOS. When you type in the wrong layout (Russian instead of English or vice versa), Layout Switcher automatically fixes the text in real time.

For example, if you type `ghbdtn` and press space, it automatically corrects to `привет`.

## Features

- **Automatic correction** — detects wrong layout and fixes words as you type
- **Manual conversion** — press `Ctrl+Shift+Space` to convert the last word
- **Undo** — press `Ctrl+Shift+Space` again to revert a correction
- **Russian morphology** — uses [pymorphy3](https://github.com/no-plagiarism/pymorphy3) to recognize all Russian word forms (conjugations, declensions, etc.)
- **236k+ English dictionary** — built from macOS system dictionary plus common tech terms
- **Native macOS UI** — menu bar icon, settings window with tabs, onboarding wizard
- **Smart exclusions** — exclude specific apps or add words to the ignore list
- **Daily stats** — correction counter and recent corrections history in the menu bar

## Quick Install

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/moiz2306/layout-switcher/main/install.sh)"
```

This one command will download, set up the environment, install dependencies, and build the dictionary. You'll be guided through the rest.

> Prefer to inspect the script first? Run `curl -fsSL https://raw.githubusercontent.com/moiz2306/layout-switcher/main/install.sh -o install.sh && less install.sh && bash install.sh`

## Requirements

- macOS 13 (Ventura) or later
- Apple Silicon (M1/M2/M3/M4) or Intel
- Python 3.11 or later

## Manual Installation

<details>
<summary>Click to expand manual installation steps</summary>

### 1. Clone the repository

```bash
git clone https://github.com/moiz2306/layout-switcher.git
cd layout-switcher
```

### 2. Run the setup script

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Build the English word dictionary
- Create a default config file at `~/.config/layout-switcher/config.yaml`

The installer will ask if you want to enable launch at login. Type `y` to start Layout Switcher automatically when you log in, or press Enter to skip.

</details>

### 3. Grant macOS permissions

Layout Switcher needs two macOS permissions to function:

#### Input Monitoring

Allows the app to read keystrokes.

1. Open **System Settings** (click the gear icon in the Dock, or press `Cmd+Space` and type "System Settings")
2. Navigate to **Privacy & Security**
3. Scroll down and click **Input Monitoring**
4. Click the **+** button
5. Navigate to **Applications → Utilities**
6. Select **Terminal** (or whichever terminal app you use) and click **Open**
7. Make sure the toggle next to Terminal is **on**

#### Accessibility

Allows the app to simulate keystrokes for auto-correction.

1. Go back to **Privacy & Security**
2. Click **Accessibility**
3. Click **+**
4. Select **Terminal** again from **Applications → Utilities**
5. Click **Open**
6. Make sure the toggle is **on**

> **Important:** After granting permissions, you must **fully restart your terminal** (`Cmd+Q` to quit, then reopen). Permissions do not take effect until the terminal process is restarted.

> **Note:** If you use multiple terminals or code editors (iTerm2, VS Code, Cursor, etc.), add each of them to both Input Monitoring and Accessibility.

## Usage

### Starting the app

```bash
cd layout-switcher
.venv/bin/python3 src/main.py
```

A colored dot will appear in the menu bar (top-right corner of the screen):

| Dot | Meaning |
|-----|---------|
| 🟢 | Active — monitoring and correcting |
| ⚪ | Disabled — paused by user |
| 🟠 | Error — missing permissions (click for details) |

### How auto-correction works

Just type normally. When you press space, Enter, or punctuation after a word, Layout Switcher checks if the word looks like it was typed in the wrong layout:

| You typed | Corrected to | What happened |
|-----------|-------------|---------------|
| `ghbdtn` + space | `привет` | English layout, but meant Russian |
| `реьд` + space | `html` | Russian layout, but meant English |
| `hello` + space | `hello` | Valid English word — no change |

### Keyboard shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+Space` | Manually convert the last word to the other layout |
| `Ctrl+Shift+Space` (after auto-correction) | Undo the last correction (within 10 seconds) |

### Menu bar

Click the 🟢 dot in the menu bar to see:

- **Status** — active, disabled, or error with details
- **Today's corrections** — how many words were corrected today
- **Enabled** — toggle auto-correction on/off
- **Recent corrections** — last 10 corrections with before/after
- **Settings...** (`Cmd+,`) — open the settings window
- **Quit** (`Cmd+Q`) — stop the app

### Settings window

Open via menu bar → Settings, or press `Cmd+,`.

**General tab:**
- Enable/disable auto-correction
- View current hotkey
- Toggle notifications (coming soon)
- Toggle launch at login

**Apps tab:**
- Add apps where Layout Switcher should **not** run
- Click **+** to pick an app, **−** to remove

**Dictionary tab:**
- Add words that should **never** be corrected (e.g., abbreviations)
- Default ignore list: `gg`, `ok`, `lol`, `bb`, `wp`, `gl`, `hf`

## Configuration

Settings are stored in `~/.config/layout-switcher/config.yaml`:

```yaml
enabled: true
hotkey_convert: "ctrl+shift+space"
excluded_apps: []
ignore_words:
  - "gg"
  - "ok"
  - "lol"
  - "bb"
  - "wp"
  - "gl"
  - "hf"
log_errors: true
show_notifications: false
launch_at_login: false
```

Changes made in the Settings window are saved automatically. If you edit the file manually, restart the app to apply changes.

## Launch at login

To start Layout Switcher automatically when you log in:

- **Via Settings:** Menu bar 🟢 → Settings → General → toggle "Launch at login"
- **Via setup script:** Run `./setup.sh` and answer `y` when asked

## Troubleshooting

### App does not correct text

1. Check that the menu bar dot is **green** 🟢
2. If orange — click it to see which permissions are missing
3. Grant the missing permissions (see [Installation, step 3](#3-grant-macos-permissions))
4. **Restart your terminal completely** (`Cmd+Q`, then reopen)
5. Start the app again

### Dot does not appear in the menu bar

- Make sure the app is running (terminal window is open, no errors)
- If the menu bar is full, icons may be hidden. Try closing other menu bar apps

### App corrects words it shouldn't

Add them to the ignore list:
- Menu bar 🟢 → Settings → Dictionary → type the word → Add
- Or add to `ignore_words` in `~/.config/layout-switcher/config.yaml`

### App interferes with a specific application

Add it to the exclusion list:
- Menu bar 🟢 → Settings → Apps → click **+** → select the app

### App does not start after reboot

Make sure launch at login is enabled:
- Menu bar 🟢 → Settings → General → "Launch at login" should be on

### `Permission denied` when running `./setup.sh`

```bash
chmod +x setup.sh
./setup.sh
```

## Uninstalling

```bash
# Remove launch agent
launchctl unload ~/Library/LaunchAgents/com.layout-switcher.plist 2>/dev/null
rm -f ~/Library/LaunchAgents/com.layout-switcher.plist

# Remove config
rm -rf ~/.config/layout-switcher

# Remove the project
rm -rf ~/Projects/layout-switcher
```

## Tech stack

- **Python 3.13** with **PyObjC** for native macOS integration
- **CGEventTap** (Quartz) for global keystroke monitoring
- **pymorphy3** for Russian morphological analysis
- **AppKit** (NSStatusBar, NSMenu, NSWindow, NSTabView) for native UI
- 66 automated tests

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes and add tests
4. Run tests: `source .venv/bin/activate && pytest tests/ -v`
5. Commit and push
6. Open a Pull Request

## License

MIT License. See [LICENSE](LICENSE) for details.
