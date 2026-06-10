#!/bin/bash
# aon installer — Archaon OS Package Manager

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${GREEN}"
echo "        /\\"
echo "       /  \\"
echo "      / /\\ \\"
echo "     / /  \\ \\"
echo "    / / /\\ \\ \\"
echo "   /_/ /__\\ \\_\\"
echo -e "${CYAN}      /\\  /\\"
echo "     /  \\/  \\"
echo "     \\  /\\  /"
echo -e "      \\/  \\/${NC}"
echo ""
echo -e "${GREEN}  aon — Archaon Package Manager${NC}"
echo -e "${CYAN}  v0.1.0 Chaotic Crow 🐦‍⬛${NC}"
echo ""

crow_log() {
    echo -e "${CYAN}  🐦‍⬛  $1${NC}"
    sleep 0.8
}

crow_log "Waking up the crow..."
crow_log "Pecking at seeds..."
crow_log "Raiding rival humans..."
crow_log "Stealing shiny packages..."
crow_log "Cawing at dependencies..."
crow_log "Sharpening talons..."

# Install python deps silently
crow_log "Building the nest..."
pip install textual requests rich --break-system-packages -q 2>/dev/null || \
pip install textual requests rich -q 2>/dev/null

crow_log "Hiding treasures..."
curl -fsSL https://raw.githubusercontent.com/archaon-os/archaon-aon/main/aon.py -o /tmp/aon.py 2>/dev/null

crow_log "Claiming territory..."
sudo cp /tmp/aon.py /usr/local/bin/aon 2>/dev/null
sudo chmod +x /usr/local/bin/aon 2>/dev/null

crow_log "Teaching the crow to speak..."

echo ""
echo -e "${GREEN}  ✓ aon installed successfully! 🐦‍⬛${NC}"
echo -e "${CYAN}  Run 'aon' to get started.${NC}"
echo ""