# aon 🐦‍⬛

> The Archaon OS package manager. Chaos is not a bug. Chaos is a feature.

aon is a full TUI package manager for Archaon OS. It wraps pacman, yay, flatpak, and more into one beautiful interactive interface with full mouse and keyboard support.

---

## Install 🐦‍⬛

    curl -fsSL https://raw.githubusercontent.com/archaon-os/archaon-aon/main/install.sh | bash

Or manually:

    git clone https://github.com/archaon-os/archaon-aon.git
    cd archaon-aon
    sudo cp aon.py /usr/local/bin/aon
    sudo chmod +x /usr/local/bin/aon
    pip install textual requests rich --break-system-packages

---

## Commands 🐦‍⬛

| Command | Description |
|---------|-------------|
| `aon install <package>` | Install from your default source |
| `aon -U install <package>` | Open TUI to choose source |
| `aon remove` | Open TUI to browse and remove packages |
| `aon remove <package>` | Remove a package directly |
| `aon update` | Update all source databases |
| `aon upgrade` | Open TUI to select packages to upgrade |
| `aon search <package>` | Search across all sources |
| `aon settings` | Open settings TUI |
| `aon --help` | Open interactive help browser |

---

## Sources 🐦‍⬛

| Source | Description |
|--------|-------------|
| pacman | Official Arch Linux repositories |
| yay | AUR — Arch User Repository |
| flatpak | Flathub |
| archaon | Archaon OS official packages |
| github | Search GitHub for Linux install packages |

---

## Features 🐦‍⬛

- Full screen TUI with mouse and keyboard support
- Pure black and neon green and blue Archaon theme
- Interactive source picker
- Browse and select packages to remove
- Spacebar multi-select for upgrades
- GitHub repo search with stars and descriptions
- First launch setup wizard
- Daily tips on every launch
- Settings page for defaults and preferences
- Auto installs missing dependencies on first run

---

## First Launch 🐦‍⬛

On first run aon will automatically install any missing dependencies including yay, flatpak, git and python libraries. Then it opens a setup wizard to choose your default package source.

---

## Roadmap 🐦‍⬛

- Archaon OS official package repository
- Custom .aon package format
- Automatic theming when installing apps
- aon package builder for maintainers
- Continuous integration with archaon-iso

---

## Part of Archaon OS 🐦‍⬛

| Repo | Purpose |
|------|---------|
| archaon-os | Main repo |
| archaon-iso | ISO build profile |
| archaon-branding | Dotfiles and assets |
| archaon-aon | This repo |

---

## License 🐦‍⬛

GPL v3 — see LICENSE file.

---

Archaon OS — 1.0.0 "Chaotic Crow" 🐦‍⬛
