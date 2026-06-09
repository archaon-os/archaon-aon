# aon 🐦‍⬛

> The Archaon OS package manager.

`aon` is a simple package manager wrapper for Archaon OS built on top of `pacman` and `yay`. It provides a cleaner, simpler syntax for everyday package management.

---

## Installation

`aon` comes pre-installed on Archaon OS.

To install manually:

    git clone https://github.com/archaon-os/archaon-aon.git
    cd archaon-aon
    sudo cp aon /usr/local/bin/aon
    sudo chmod +x /usr/local/bin/aon

---

## Usage

    aon <command> [package]

---

## Commands

| Command | Short | Description |
|---------|-------|-------------|
| `aon install <package>` | `aon i` | Install a package |
| `aon remove <package>` | `aon r` | Remove a package |
| `aon update` | `aon u` | Update all packages |
| `aon search <package>` | `aon s` | Search for a package |
| `aon list` | `aon l` | List installed packages |
| `aon info <package>` | | Show package info |
| `aon clean` | | Clean package cache |

---

## Examples

    # Install a package
    aon install firefox

    # Install multiple packages
    aon install git neovim docker

    # Remove a package
    aon remove firefox

    # Update everything
    aon update

    # Search for a package
    aon search spotify

    # Get info about a package
    aon info hyprland

    # Clean cache
    aon clean

---

## Under the Hood

`aon` uses:
- `pacman` for official Arch repos
- `yay` for AUR packages

Both are searched automatically — no need to specify which one.

---

## Roadmap

- [ ] Archaon curated package repo
- [ ] Packages that install with Archaon theming baked in
- [ ] Custom `.aon` package format
- [ ] Full dependency resolution
- [ ] `aon install discord` auto-applies dark theme

---

## Related Repos

| Repo | Purpose |
|------|---------|
| [archaon-os](https://github.com/archaon-os/archaon-os) | Main repo |
| [archaon-iso](https://github.com/archaon-os/archaon-iso) | ISO build |
| [archaon-branding](https://github.com/archaon-os/archaon-branding) | Dotfiles |

---

## License

GPL v3 — see LICENSE file.

---

**Archaon OS — 1.0.0 "Chaotic Crow" 🐦‍⬛**
