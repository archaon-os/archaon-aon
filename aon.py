#!/usr/bin/env python3
"""
aon - Archaon OS Package Manager
Version: 0.1.0 "Chaotic Crow"
"""

import os
import sys
import json
import random
import subprocess
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

    # Install textual if missing
    try:
        import textual
    except ImportError:
        print("  \033[96m→\033[0m Installing textual...")
        subprocess.call("pip install textual requests rich --break-system-packages", shell=True)

    # Install requests if missing
    try:
        import requests
    except ImportError:
        subprocess.call("pip install requests --break-system-packages", shell=True)

check_and_install_deps()

# ─────────────────────────────────────────
# IMPORTS (after deps installed)
# ─────────────────────────────────────────

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header, Footer, Label, Button, Static,
    ListView, ListItem, Checkbox, Select, Input
)
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.binding import Binding

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────

CONFIG_DIR = Path.home() / ".config" / "aon"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "default_source": "pacman",
    "auto_update": False,
    "confirm_install": True,
    "first_launch": True,
    "color_accent": "#00ff88",
    "color_secondary": "#00ccff",
}

SOURCES = ["pacman", "yay", "flatpak", "archaon", "github"]

TIPS = [
    "Use 'aon -U install <package>' to choose where to install from.",
    "Use 'aon upgrade' to pick which packages to update.",
    "Use 'aon remove' to browse and uninstall packages.",
    "Use 'aon search <package>' to search across all sources.",
    "Use 'aon settings' to configure your defaults.",
    "Archaon packages (.aon) are hosted at archaon.is-a.dev",
    "Use spacebar to select packages in upgrade mode.",
    "aon wraps pacman, yay, flatpak and more in one tool.",
    "Press Q anywhere to quit aon.",
    "Arrow keys navigate, Enter selects, Space toggles.",
]

COMMANDS_HELP = {
    "aon install <package>": "Install a package from your default source.",
    "aon -U install <package>": "Open TUI to choose which source to install from.",
    "aon remove": "Open TUI to browse and select packages to remove.",
    "aon remove <package>": "Remove a specific package directly.",
    "aon update": "Update all source databases.",
    "aon upgrade": "Open TUI to select which packages to upgrade.",
    "aon search <package>": "Search for a package across all sources.",
    "aon settings": "Open the settings TUI.",
    "aon --help": "Open this help browser.",
}

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
    cmd = cmds.get(source, f"sudo pacman -S {package}")
    run(cmd)

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
        data = r.json()
        results = []
        for repo in data.get("items", []):
            results.append({
                "name": repo["full_name"],
                "description": repo.get("description", "No description"),
                "stars": repo["stargazers_count"],
                "url": repo["html_url"],
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

Checkbox {
    color: #00ff88;
    background: #000000;
}

Select {
    background: #0a0a0a;
    color: #00ff88;
    border: solid #00ff88;
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

LOGO = """\
        /\\
       /  \\
      / /\\ \\
     / /  \\ \\
    / / /\\ \\ \\
   /_/ /__\\ \\_\\
      /\\  /\\
     /  \\/  \\
     \\  /\\  /
      \\/  \\/"""

# ─────────────────────────────────────────
# GREETER SCREEN
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
            Static(LOGO, classes="logo"),
            Static("A R C H A O N  O S", classes="title"),
            Static("aon — Package Manager v0.1.0 Chaotic Crow", classes="version"),
            Static("─" * 40, classes="subtitle"),
            Static(f"💡 {tip}", classes="tip"),
            Static("─" * 40, classes="subtitle"),
            Static(f"Default source: {config['default_source']}", classes="subtitle"),
            Static("Press ENTER to continue or Q to quit", classes="tip"),
        )
        yield Footer()

    def action_dismiss(self):
        self.app.pop_screen()

# ─────────────────────────────────────────
# FIRST LAUNCH SCREEN
# ─────────────────────────────────────────

class FirstLaunchScreen(Screen):
    BINDINGS = [Binding("q", "app.quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static(LOGO, classes="logo"),
            Static("Welcome to aon!", classes="title"),
            Static("Let's get you set up.", classes="subtitle"),
            Static("", classes="tip"),
            Static("Choose your default package source:", classes="subtitle"),
            Static("", classes="tip"),
            Button("pacman  — Official Arch repos", id="src_pacman"),
            Button("yay     — AUR (Arch User Repository)", id="src_yay"),
            Button("flatpak — Flathub", id="src_flatpak"),
            Button("archaon — Archaon OS repo", id="src_archaon"),
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

# ─────────────────────────────────────────
# HELP SCREEN
# ─────────────────────────────────────────

class HelpScreen(Screen):
    BINDINGS = [
        Binding("q", "app.quit", "Quit"),
        Binding("escape", "dismiss", "Back"),
    ]

    selected_command = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static("aon — Help Browser", classes="title"),
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

# ─────────────────────────────────────────
# SOURCE PICKER SCREEN
# ─────────────────────────────────────────

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
            Static("Choose a source:", classes="subtitle"),
            Static("", classes="tip"),
            Button("📦  pacman  — Official Arch repos", id="src_pacman"),
            Button("🔧  yay     — AUR", id="src_yay"),
            Button("📱  flatpak — Flathub", id="src_flatpak"),
            Button("🔮  archaon — Archaon repo", id="src_archaon"),
            Button("🐙  github  — Search GitHub", id="src_github"),
            Static("", classes="tip"),
            Static("ESC — Back", classes="dim"),
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

# ─────────────────────────────────────────
# REMOVE SCREEN
# ─────────────────────────────────────────

class RemoveScreen(Screen):
    BINDINGS = [
        Binding("q", "app.quit", "Quit"),
        Binding("escape", "dismiss", "Back"),
        Binding("enter", "remove_selected", "Remove"),
    ]

    def compose(self) -> ComposeResult:
        packages = get_installed_packages()
        yield Header(show_clock=True)
        yield Container(
            Static("aon remove — Installed Packages", classes="title"),
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
            packages = get_installed_packages()
            package = packages[idx]
            self.app.exit()
            remove_package(package)

    def action_dismiss(self):
        self.app.pop_screen()

# ─────────────────────────────────────────
# UPGRADE SCREEN
# ─────────────────────────────────────────

class UpgradeScreen(Screen):
    BINDINGS = [
        Binding("q", "app.quit", "Quit"),
        Binding("escape", "dismiss", "Back"),
        Binding("enter", "upgrade_selected", "Upgrade"),
    ]

    def __init__(self):
        super().__init__()
        self.selected = set()

    def compose(self) -> ComposeResult:
        packages = get_upgradeable_packages()
        self.packages = packages
        yield Header(show_clock=True)
        yield Container(
            Static("aon upgrade — Available Updates", classes="title"),
            Static("SPACE to select, ENTER to upgrade selected", classes="subtitle"),
            Static("", classes="tip"),
            ListView(
                *[ListItem(Label(f"○  {p}"), id=f"upg_{i}")
                  for i, p in enumerate(packages)] if packages
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
                idx = int(str(list_view.highlighted_child.id).replace("upg_", ""))
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

# ─────────────────────────────────────────
# SEARCH SCREEN
# ─────────────────────────────────────────

class SearchScreen(Screen):
    BINDINGS = [
        Binding("q", "app.quit", "Quit"),
        Binding("escape", "dismiss", "Back"),
    ]

    def __init__(self, package: str):
        super().__init__()
        self.package = package
        self.results = {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static(f"Search results for: [bold #00ccff]{self.package}[/bold #00ccff]", classes="title"),
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
        self.query_one("#search_status", Static).update("Done!")

    def action_dismiss(self):
        self.app.pop_screen()

# ─────────────────────────────────────────
# SETTINGS SCREEN
# ─────────────────────────────────────────

class SettingsScreen(Screen):
    BINDINGS = [
        Binding("q", "app.quit", "Quit"),
        Binding("escape", "dismiss", "Back"),
    ]

    def compose(self) -> ComposeResult:
        config = load_config()
        yield Header(show_clock=True)
        yield Container(
            Static("aon settings", classes="title"),
            Static("", classes="tip"),
            Container(
                Static("Default Source", classes="panel-title"),
                Button("pacman", id="set_pacman"),
                Button("yay", id="set_yay"),
                Button("flatpak", id="set_flatpak"),
                Button("archaon", id="set_archaon"),
                Static(f"Current: {config['default_source']}", id="current_source", classes="subtitle"),
                classes="panel",
            ),
            Container(
                Static("Options", classes="panel-title"),
                Button(
                    f"Auto Update: {'ON' if config['auto_update'] else 'OFF'}",
                    id="toggle_autoupdate"
                ),
                Button(
                    f"Confirm Install: {'ON' if config['confirm_install'] else 'OFF'}",
                    id="toggle_confirm"
                ),
                classes="panel",
            ),
            Static("ESC — Back  |  Q — Quit", classes="dim"),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        config = load_config()
        bid = str(event.button.id)

        if bid == "set_pacman":
            config["default_source"] = "pacman"
        elif bid == "set_yay":
            config["default_source"] = "yay"
        elif bid == "set_flatpak":
            config["default_source"] = "flatpak"
        elif bid == "set_archaon":
            config["default_source"] = "archaon"
        elif bid == "toggle_autoupdate":
            config["auto_update"] = not config["auto_update"]
            event.button.label = f"Auto Update: {'ON' if config['auto_update'] else 'OFF'}"
        elif bid == "toggle_confirm":
            config["confirm_install"] = not config["confirm_install"]
            event.button.label = f"Confirm Install: {'ON' if config['confirm_install'] else 'OFF'}"

        save_config(config)
        self.query_one("#current_source", Static).update(
            f"Current: {config['default_source']}"
        )

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

    if not args or "--help" in args or "-h" in args:
        AonApp(HelpScreen()).run()
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
        print("\033[92m→\033[0m Updating package databases...")
        run("sudo pacman -Sy")
        run("yay -Sy 2>/dev/null")
        run("flatpak update 2>/dev/null")
        print("\033[92m✓\033[0m Done!")
        return

    if args[0] == "search" and len(args) > 1:
        AonApp(SearchScreen(args[1])).run()
        return

    if args[0] == "-U" and len(args) > 2 and args[1] == "install":
        package = args[2]
        AonApp(SourcePickerScreen(package)).run()
        return

    if args[0] == "install" and len(args) > 1:
        package = args[1]
        config = load_config()
        source = config.get("default_source", "pacman")
        install_package(package, source)
        return

    print(f"\033[91m✗\033[0m Unknown command: {' '.join(args)}")
    print("Run 'aon --help' for usage.")

if __name__ == "__main__":
    main()