#!/bin/bash
# aon installer

GREEN='\033[0;32m'
CYAN='\033[0;36m'
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
echo -e "${GREEN}Installing aon — Archaon Package Manager${NC}"
echo ""

# Install dependencies
echo -e "${CYAN}→${NC} Installing Python dependencies..."
pip install textual requests rich --break-system-packages 2>/dev/null || \
pip install textual requests rich 2>/dev/null

# Download aon
echo -e "${CYAN}→${NC} Downloading aon..."
curl -fsSL https://raw.githubusercontent.com/archaon-os/archaon-aon/main/aon.py -o /tmp/aon.py

# Install
echo -e "${CYAN}→${NC} Installing to /usr/local/bin/aon..."
sudo cp /tmp/aon.py /usr/local/bin/aon
sudo chmod +x /usr/local/bin/aon

echo ""
echo -e "${GREEN}✓ aon installed successfully!${NC}"
echo -e "${CYAN}Run 'aon' to get started.${NC}"