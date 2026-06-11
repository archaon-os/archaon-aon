#!/usr/bin/env python3
"""
aon - Archaon OS Package Manager
Version: 0.1.3 "Chaotic Crow"
"""

import os
import sys
import json
import random
import subprocess
import time
from pathlib import Path

# ─────────────────────────────────────────
# DEPENDENCY CHECK & INSTALL
# ─────────────────────────────────────────

def check_and_install_deps():
    deps = {
        "yay": {
            "check": "which yay",
            "install": "cd /tmp && git clone https://aur.archlinux.org/yay.git && cd yay && makepkg -si --noconfirm && cd / && rm -rf /tmp/yay",
        },
        "flatpak": {
            "check": "which flatpak",
            "install": "sudo pacman -S --noconfirm flatpak && flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo",
        },
        "git": {
            "check": "which git",
            "install": "sudo pacman -S --noconfirm git",
        },
    }

    missing = []
    for name, info in deps.items():
        result = subprocess.run(info["check"], shell=True, capture_output=True)
        if result.returncode != 0:
            missing.append((name, info["install"]))

    if missing:
        print(f"\n\033[92m aon \033[0m — Missing dependencies detected\n")
        for name, cmd in missing:
            print(f"  \033[96m→\033[0m Installing {name}...")
            subprocess.call(cmd, shell=True)
        print(f"\n  \033[92m✓\033[0m All dependencies installed\n")

    try:
        import textual
    except ImportError:
        subprocess.call("pip install textual requests rich pyfiglet --break-system-packages -q", shell=True)

    try:
        import requests
    except ImportError:
        subprocess.call("pip install requests --break-system-packages -q", shell=True)

    try:
        import pyfiglet
    except ImportError:
        subprocess.call("pip install pyfiglet --break-system-packages -q", shell=True)

check_and_install_deps()

# ─────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header, Footer, Label, Button, Static,
    ListView, ListItem, Input
)
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.binding import Binding
import pyfiglet

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────

CONFIG_DIR = Path.home() / ".config" / "aon"
CONFIG_FILE = CONFIG_DIR / "config.json"
VERSION = "0.1.3"
CODENAME = "Chaotic Crow"

DEFAULT_CONFIG = {
    "default_source": "pacman",
    "auto_update": False,
    "confirm_install": True,
    "first_launch": True,
}

SOURCES = ["pacman", "yay", "flatpak", "archaon", "github"]

TIPS = [
    "Use 'aon -U install <package>' to choose where to install from.",
    "Use 'aon upgrade' to pick which packages to update.",
    "Use 'aon remove' to browse and uninstall packages.",
    "Use 'aon search <package>' to search across all sources.",
    "Use 'aon settings' to configure your defaults.",
    "Use spacebar to select packages in upgrade mode.",
    "Press Q anywhere to quit aon.",
    "Arrow keys navigate, Enter selects, Space toggles.",
    "The crow sees all packages. 🐦‍⬛",
    "Chaos is not a bug. Chaos is a feature.",
]

COMMANDS_HELP = {
    "aon install <package>": "Install a package from your default source silently.",
    "aon -U install <package>": "Open TUI source picker to choose where to install from.",
    "aon remove": "Open TUI to browse all installed packages and select one to remove.",
    "aon remove <package>": "Remove a specific package directly without TUI.",
    "aon update": "Update all source databases (pacman, yay, flatpak).",
    "aon upgrade": "Open TUI to select which packages to upgrade with spacebar.",
    "aon search <package>": "Search for a package across all sources simultaneously.",
    "aon settings": "Open the settings TUI to configure defaults.",
    "aon uninstall": "Show uninstall instructions.",
    "aon uninstall --sure --im-not-stupid": "Completely uninstall aon and all its files.",
    "aon --help": "Open this interactive help browser.",
}

# ─────────────────────────────────────────
# ANIMATED LOGO
# ─────────────────────────────────────────

GREEN = '\033[38;2;0;255;136m'
BLUE = '\033[38;2;0;204;255m'
DIM = '\033[38;2;51;51;51m'
RESET = '\033[0m'
BOLD = '\033[1m'

GLITCH = ['░', '▒', '▓', '█', '▄', '▀', '■', '●']

def get_logo():
    text = pyfiglet.figlet_format('AON', font='colossal')
    lines = text.split('\n')
    max_len = max(len(l) for l in lines)
    result = []
    for i, line in enumerate(lines):
        padded = line.ljust(max_len + 2)
        new_line = ''
        for j, ch in enumerate(padded):
            if ch != ' ':
                new_line += ch
            else:
                if i > 0 and j > 0 and j-1 < len(lines[i-1]) and lines[i-1][j-1] != ' ':
                    new_line += '░'
                else:
                    new_line += ' '
        result.append(new_line)
    return result

def animate_logo():
    logo = get_logo()
    total = sum(len(l) for l in logo)
    frames = 20
    for frame in range(frames + 1):
        os.system('clear')
        revealed = int((frame / frames) * total)
        output = ''
        pos = 0
        for line in logo:
            for ch in line:
                if pos < revealed:
                    if ch == '░':
                        output += BLUE + ch + RESET
                    else:
                        output += GREEN + ch + RESET
                elif ch != ' ':
                    output += DIM + random.choice(GLITCH) + RESET
                else:
                    output += ' '
                pos += 1
            output += '\n'
        print(output)
        time.sleep(0.12)

    # Print subtitle after logo
    print(f"  {GREEN}{BOLD}A R C H A O N  O S{RESET}")
    print(f"  {BLUE}aon v{VERSION} — {CODENAME} 🐦‍⬛{RESET}")
    print()

# ─────────────────────────────────────────
# CONFIG FUNCTIONS
# ─────────────────────────────────────────

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE) as f:
        return json.load(f)

def save_config(config: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

# ─────────────────────────────────────────
# SHELL HELPERS
# ─────────────────────────────────────────

def run(cmd: str) -> int:
    return subprocess.call(cmd, shell=True)

def run_output(cmd: str) -> str:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def install_package(package: str, source: str):
    cmds = {
        "pacman": f"sudo pacman -S {package}",
        "yay": f"yay -S {package}",
        "flatpak": f"flatpak install flathub {package}",
        "archaon": f"echo 'Archaon repo coming soon'",
        "github": f"echo 'GitHub install coming soon'",
    }
    run(cmds.get(source, f"sudo pacman -S {package}"))

def remove_package(package: str):
    run(f"sudo pacman -Rns {package}")

def get_installed_packages() -> list:
    output = run_output("pacman -Qqe 2>/dev/null")
    system = run_output("pacman -Qqg base base-devel 2>/dev/null").split("\n")
    return sorted([p for p in output.split("\n") if p and p not in system])

def get_upgradeable_packages() -> list:
    output = run_output("checkupdates 2>/dev/null || yay -Qu --noconfirm 2>/dev/null")
    return [line.split()[0] for line in output.split("\n") if line]

def search_github(package: str) -> list:
    try:
        import requests
        url = f"https://api.github.com/search/repositories?q={package}+linux+install&sort=stars&per_page=10"
        r = requests.get(url, timeout=5)
        results = []
        for repo in r.json().get("items", []):
            results.append({
                "name": repo["full_name"],
                "description": repo.get("description", "No description"),
                "stars": repo["stargazers_count"],
            })
        return results
    except Exception:
        return []

def search_all(package: str) -> dict:
    results = {}
    pacman = run_output(f"pacman -Ss {package} 2>/dev/null | grep '^[^ ]' | head -10")
    results["pacman"] = [l.split()[0] for l in pacman.split("\n") if l]
    yay_out = run_output(f"yay -Ss {package} 2>/dev/null | grep '^[^ ]' | head -10")
    results["yay"] = [l.split()[0] for l in yay_out.split("\n") if l]
    flatpak_out = run_output(f"flatpak search {package} 2>/dev/null | head -10")
    results["flatpak"] = [l.split()[0] for l in flatpak_out.split("\n") if l and l != "No matches found"]
    results["github"] = search_github(package)
    return results

# ─────────────────────────────────────────
# UNINSTALL
# ─────────────────────────────────────────

def uninstall_aon():
    print(f"\n{GREEN}🐦‍⬛ aon uninstaller{RESET}\n")
    print(f"{BLUE}Removing aon binary...{RESET}")
    run("sudo rm -f /usr/local/bin/aon")
    print(f"{BLUE}Removing config...{RESET}")
    run("rm -rf ~/.config/aon")
    print(f"{BLUE}Removing pip packages...{RESET}")
    run("pip uninstall -y textual rich requests pyfiglet --break-system-packages 2>/dev/null || pip uninstall -y textual rich requests pyfiglet 2>/dev/null")
    print(f"\n{GREEN}✓ aon has been completely removed. Goodbye! 🐦‍⬛{RESET}\n")

def uninstall_instructions():
    print(f"\n{GREEN}🐦‍⬛ aon uninstall{RESET}\n")
    print(f"  To uninstall aon run:\n")
    print(f"  {BLUE}aon uninstall --sure --im-not-stupid{RESET}\n")
    print(f"  {DIM}This will remove the binary, config, and all pip packages.{RESET}\n")

# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────

AON_CSS = """
Screen {
    background: #000000;
    color: #00ff88;
}
Header {
    background: #000000;
    color: #00ff88;
}
Footer {
    background: #000000;
    color: #00ccff;
}
.logo {
    color: #00ff88;
    text-align: center;
    padding: 1 0;
}
.title {
    color: #00ff88;
    text-align: center;
    text-style: bold;
    padding: 0 0 1 0;
}
.subtitle {
    color: #00ccff;
    text-align: center;
}
.tip {
    color: #333333;
    text-align: center;
    padding: 1 0;
}
.version {
    color: #00ccff;
    text-align: center;
    text-style: italic;
}
Button {
    background: #0a0a0a;
    color: #00ff88;
    border: solid #00ff88;
    margin: 0 1;
    min-width: 20;
}
Button:hover {
    background: #00ff88;
    color: #000000;
}
Button:focus {
    background: #00ff88;
    color: #000000;
}
.panel {
    background: #0a0a0a;
    border: solid #00ff88;
    padding: 1;
    margin: 1;
    height: auto;
}
.panel-title {
    color: #00ccff;
    text-style: bold;
    padding: 0 0 1 0;
}
.error { color: #ff0055; }
.warning { color: #ffaa00; }
.success { color: #00ff88; }
.dim { color: #333333; }
ListView {
    background: #000000;
    border: solid #00ff88;
    height: 20;
}
ListItem {
    background: #000000;
    color: #00ff88;
    padding: 0 1;
}
ListItem:hover {
    background: #00ff88;
    color: #000000;
}
ListItem.--highlight {
    background: #00ff88;
    color: #000000;
}
Input {
    background: #0a0a0a;
    color: #00ff88;
    border: solid #00ff88;
}
Input:focus {
    border: solid #00ccff;
}
"""

LOGO_STATIC = """
       d8888 .d88888b. 888b    888
      d88888d88P"░"Y88b8888b   888░
     d88P888888░░░ ░88888888b  888░
    d88P░888888░    888888Y88b 888░
   d88P░░888888░    888888░Y88b888░
  d88P░░ 888888░    888888░ Y88888░
 d8888888888Y88b. .d88P888░  Y8888░
d88P░░░░░888░"Y88888P"░888░   Y888░
"""

# ─────────────────────────────────────────
# SCREENS
# ─────────────────────────────────────────

class GreeterScreen(Screen):
    BINDINGS = [
        Binding("q", "app.quit", "Quit"),
        Binding("enter", "dismiss", "Continue"),
    ]

    def compose(self) -> ComposeResult:
        tip = random.choice(TIPS)
        config = load_config()
        yield Header(show_clock=True)
        yield Container(
            Static(LOGO_STATIC, classes="logo"),
            Static("A R C H A O N  O S", classes="title"),
            Static(f"aon v{VERSION} — {CODENAME} 🐦‍⬛", classes="version"),
            Static("─" * 40, classes="subtitle"),
            Static(f"💡 {tip}", classes="tip"),
            Static("─" * 40, classes="subtitle"),
            Static(f"Default source: {config['default_source']}", classes="subtitle"),
            Static("Press ENTER to continue or Q to quit", classes="tip"),
        )
        yield Footer()

    def action_dismiss(self):
        self.app.pop_screen()

class FirstLaunchScreen(Screen):
    BINDINGS = [Binding("q", "app.quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static(LOGO_STATIC, classes="logo"),
            Static("Welcome to aon! 🐦‍⬛", classes="title"),
            Static("Let's get you set up.", classes="subtitle"),
            Static("", classes="tip"),
            Static("Choose your default package source:", classes="subtitle"),
            Static("", classes="tip"),
            Button("📦  pacman  — Official Arch repos", id="src_pacman"),
            Button("🔧  yay     — AUR", id="src_yay"),
            Button("📱  flatpak — Flathub", id="src_flatpak"),
            Button("🔮  archaon — Archaon OS repo", id="src_archaon"),
            Static("", classes="tip"),
            Static("You can change this later in aon settings", classes="dim"),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        source_map = {
            "src_pacman": "pacman",
            "src_yay": "yay",
            "src_flatpak": "flatpak",
            "src_archaon": "archaon",
        }
        source = source_map.get(str(event.button.id), "pacman")
        config = load_config()
        config["default_source"] = source
        config["first_launch"] = False
        save_config(config)
        self.app.pop_screen()

class HelpScreen(Screen):
    BINDINGS = [
        Binding("q", "app.quit", "Quit"),
        Binding("escape", "dismiss", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static("aon — Help Browser 🐦‍⬛", classes="title"),
            Static("Select a command to see its usage", classes="subtitle"),
            Static("", classes="tip"),
            Horizontal(
                ScrollableContainer(
                    ListView(
                        *[ListItem(Label(cmd), id=f"cmd_{i}")
                          for i, cmd in enumerate(COMMANDS_HELP.keys())],
                        id="cmd_list"
                    ),
                    classes="panel",
                ),
                Container(
                    Static("← Select a command", id="cmd_detail", classes="subtitle"),
                    classes="panel",
                ),
            ),
            Static("ESC — Back  |  Q — Quit", classes="tip"),
        )
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        idx = int(str(event.item.id).replace("cmd_", ""))
        cmd = list(COMMANDS_HELP.keys())[idx]
        desc = COMMANDS_HELP[cmd]
        self.query_one("#cmd_detail", Static).update(
            f"[bold #00ff88]{cmd}[/bold #00ff88]\n\n[#00ccff]{desc}[/#00ccff]"
        )

    def action_dismiss(self):
        self.app.pop_screen()

class SourcePickerScreen(Screen):
    BINDINGS = [
        Binding("q", "app.quit", "Quit"),
        Binding("escape", "dismiss", "Back"),
    ]

    def __init__(self, package: str):
        super().__init__()
        self.package = package

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static(f"Installing: [bold #00ccff]{self.package}[/bold #00ccff]", classes="title"),
            Static("Choose a source 🐦‍⬛", classes="subtitle"),
            Static("", classes="tip"),
            Button("📦  pacman  — Official Arch repos", id="src_pacman"),
            Button("🔧  yay     — AUR", id="src_yay"),
            Button("📱  flatpak — Flathub", id="src_flatpak"),
            Button("🔮  archaon — Archaon repo", id="src_archaon"),
            Button("🐙  github  — Search GitHub", id="src_github"),
            Static("", classes="tip"),
            Static("ESC — Back  |  Q — Quit", classes="dim"),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        source_map = {
            "src_pacman": "pacman",
            "src_yay": "yay",
            "src_flatpak": "flatpak",
            "src_archaon": "archaon",
            "src_github": "github",
        }
        source = source_map.get(str(event.button.id))
        if source:
            self.app.exit()
            install_package(self.package, source)

    def action_dismiss(self):
        self.app.pop_screen()

class RemoveScreen(Screen):
    BINDINGS = [
        Binding("q", "app.quit", "Quit"),
        Binding("escape", "dismiss", "Back"),
        Binding("enter", "remove_selected", "Remove"),
    ]

    def compose(self) -> ComposeResult:
        packages = get_installed_packages()
        self.packages = packages
        yield Header(show_clock=True)
        yield Container(
            Static("aon remove 🐦‍⬛", classes="title"),
            Static("Select a package to remove", classes="subtitle"),
            Static("", classes="tip"),
            ListView(
                *[ListItem(Label(p), id=f"pkg_{i}")
                  for i, p in enumerate(packages)],
                id="pkg_list"
            ),
            Static("", classes="tip"),
            Static("ENTER — Remove  |  ESC — Back  |  Q — Quit", classes="dim"),
        )
        yield Footer()

    def action_remove_selected(self):
        list_view = self.query_one("#pkg_list", ListView)
        if list_view.highlighted_child:
            idx = int(str(list_view.highlighted_child.id).replace("pkg_", ""))
            package = self.packages[idx]
            self.app.exit()
            remove_package(package)

    def action_dismiss(self):
        self.app.pop_screen()

class UpgradeScreen(Screen):
    BINDINGS = [
        Binding("q", "app.quit", "Quit"),
        Binding("escape", "dismiss", "Back"),
        Binding("enter", "upgrade_selected", "Upgrade"),
    ]

    def __init__(self):
        super().__init__()
        self.selected = set()
        self.packages = []

    def compose(self) -> ComposeResult:
        self.packages = get_upgradeable_packages()
        yield Header(show_clock=True)
        yield Container(
            Static("aon upgrade 🐦‍⬛", classes="title"),
            Static("SPACE to select, ENTER to upgrade selected", classes="subtitle"),
            Static("", classes="tip"),
            ListView(
                *[ListItem(Label(f"○  {p}"), id=f"upg_{i}")
                  for i, p in enumerate(self.packages)] if self.packages
                else [ListItem(Label("✓  All packages are up to date!"))],
                id="upg_list"
            ),
            Static("", classes="tip"),
            Static("SPACE — Toggle  |  ENTER — Upgrade  |  ESC — Back", classes="dim"),
        )
        yield Footer()

    def on_key(self, event) -> None:
        if event.key == "space":
            list_view = self.query_one("#upg_list", ListView)
            if list_view.highlighted_child:
                item_id = str(list_view.highlighted_child.id)
                if not item_id.startswith("upg_"):
                    return
                idx = int(item_id.replace("upg_", ""))
                if idx in self.selected:
                    self.selected.remove(idx)
                    list_view.highlighted_child.query_one(Label).update(f"○  {self.packages[idx]}")
                else:
                    self.selected.add(idx)
                    list_view.highlighted_child.query_one(Label).update(f"●  {self.packages[idx]}")

    def action_upgrade_selected(self):
        if not self.selected:
            return
        packages = [self.packages[i] for i in self.selected]
        self.app.exit()
        run(f"sudo pacman -S {' '.join(packages)}")

    def action_dismiss(self):
        self.app.pop_screen()

class SearchScreen(Screen):
    BINDINGS = [
        Binding("q", "app.quit", "Quit"),
        Binding("escape", "dismiss", "Back"),
    ]

    def __init__(self, package: str):
        super().__init__()
        self.package = package

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static(f"aon search — {self.package} 🐦‍⬛", classes="title"),
            Static("Searching all sources...", id="search_status", classes="subtitle"),
            Static("", classes="tip"),
            ScrollableContainer(
                Static("", id="results_area"),
                classes="panel",
            ),
            Static("ESC — Back  |  Q — Quit", classes="dim"),
        )
        yield Footer()

    def on_mount(self) -> None:
        self.run_worker(self.do_search(), exclusive=True)

    async def do_search(self):
        results = search_all(self.package)
        output = []
        for source, packages in results.items():
            if source == "github":
                output.append(f"[bold #00ccff]── GitHub ──[/bold #00ccff]")
                for r in packages[:5]:
                    output.append(f"  [#00ff88]{r['name']}[/#00ff88] ⭐{r['stars']}")
                    output.append(f"  [#333333]{r['description']}[/#333333]")
            else:
                output.append(f"[bold #00ccff]── {source} ──[/bold #00ccff]")
                for p in packages[:5]:
                    output.append(f"  [#00ff88]{p}[/#00ff88]")
            output.append("")
        self.query_one("#results_area", Static).update("\n".join(output))
        self.query_one("#search_status", Static).update("🐦‍⬛ Done!")

    def action_dismiss(self):
        self.app.pop_screen()

class SettingsScreen(Screen):
    BINDINGS = [
        Binding("q", "app.quit", "Quit"),
        Binding("escape", "dismiss", "Back"),
    ]

    def compose(self) -> ComposeResult:
        config = load_config()
        yield Header(show_clock=True)
        yield Container(
            Static("aon settings 🐦‍⬛", classes="title"),
            Static("", classes="tip"),
            Container(
                Static("Default Source", classes="panel-title"),
                Button("📦  pacman", id="set_pacman"),
                Button("🔧  yay", id="set_yay"),
                Button("📱  flatpak", id="set_flatpak"),
                Button("🔮  archaon", id="set_archaon"),
                Static(f"Current: {config['default_source']}", id="current_source", classes="subtitle"),
                classes="panel",
            ),
            Container(
                Static("Options", classes="panel-title"),
                Button(f"Auto Update: {'ON' if config['auto_update'] else 'OFF'}", id="toggle_autoupdate"),
                Button(f"Confirm Install: {'ON' if config['confirm_install'] else 'OFF'}", id="toggle_confirm"),
                classes="panel",
            ),
            Static("ESC — Back  |  Q — Quit", classes="dim"),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        config = load_config()
        bid = str(event.button.id)
        if bid == "set_pacman": config["default_source"] = "pacman"
        elif bid == "set_yay": config["default_source"] = "yay"
        elif bid == "set_flatpak": config["default_source"] = "flatpak"
        elif bid == "set_archaon": config["default_source"] = "archaon"
        elif bid == "toggle_autoupdate":
            config["auto_update"] = not config["auto_update"]
            event.button.label = f"Auto Update: {'ON' if config['auto_update'] else 'OFF'}"
        elif bid == "toggle_confirm":
            config["confirm_install"] = not config["confirm_install"]
            event.button.label = f"Confirm Install: {'ON' if config['confirm_install'] else 'OFF'}"
        save_config(config)
        self.query_one("#current_source", Static).update(f"Current: {config['default_source']}")

    def action_dismiss(self):
        self.app.pop_screen()

# ─────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────

class AonApp(App):
    CSS = AON_CSS
    TITLE = "aon — Archaon Package Manager"

    def __init__(self, screen: Screen):
        super().__init__()
        self.initial_screen = screen

    def on_mount(self) -> None:
        config = load_config()
        if config.get("first_launch", True):
            self.push_screen(FirstLaunchScreen())
        else:
            self.push_screen(GreeterScreen())
        self.push_screen(self.initial_screen)

# ─────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if not args:
        animate_logo()
        config = load_config()
        screen = FirstLaunchScreen() if config.get("first_launch", True) else GreeterScreen()
        AonApp(screen).run()
        return

    if "--help" in args or "-h" in args:
        animate_logo()
        AonApp(HelpScreen()).run()
        return

    if args[0] == "uninstall":
        if "--sure" in args and "--im-not-stupid" in args:
            animate_logo()
            uninstall_aon()
        else:
            uninstall_instructions()
        return

    if args[0] == "settings":
        AonApp(SettingsScreen()).run()
        return

    if args[0] == "remove":
        if len(args) > 1:
            remove_package(args[1])
        else:
            AonApp(RemoveScreen()).run()
        return

    if args[0] == "upgrade":
        AonApp(UpgradeScreen()).run()
        return

    if args[0] == "update":
        print(f"\n{GREEN}🐦‍⬛ aon{RESET} — Updating sources...")
        run("sudo pacman -Sy")
        run("yay -Sy 2>/dev/null")
        run("flatpak update 2>/dev/null")
        print(f"{GREEN}✓{RESET} Done!")
        return

    if args[0] == "search" and len(args) > 1:
        AonApp(SearchScreen(args[1])).run()
        return

    if args[0] == "-U" and len(args) > 2 and args[1] == "install":
        animate_logo()
        AonApp(SourcePickerScreen(args[2])).run()
        return

    if args[0] == "install" and len(args) > 1:
        config = load_config()
        install_package(args[1], config.get("default_source", "pacman"))
        return

    print(f"{RED}✗{RESET} Unknown command: {' '.join(args)}")
    print("Run 'aon --help' for usage.")

if __name__ == "__main__":
    main()