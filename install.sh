#!/bin/bash
# aon installer — Archaon OS Package Manager v0.1.3

GREEN='\033[38;2;0;255;136m'
BLUE='\033[38;2;0;204;255m'
DIM='\033[38;2;51;51;51m'
RESET='\033[0m'
BOLD='\033[1m'

GLITCH=('░' '▒' '▓' '█' '▄' '▀' '■' '●')

get_logo() {
python3 -c "
import pyfiglet
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
for line in result:
    print(line)
"
}

animate_logo() {
    local logo
    mapfile -t logo < <(get_logo)
    local frames=20
    local total_chars=0
    for line in "${logo[@]}"; do
        total_chars=$((total_chars + ${#line}))
    done

    for ((frame=0; frame<=frames; frame++)); do
        clear
        local revealed=$(( (frame * total_chars) / frames ))
        local pos=0
        for line in "${logo[@]}"; do
            local out=""
            for ((i=0; i<${#line}; i++)); do
                local ch="${line:$i:1}"
                if ((pos < revealed)); then
                    if [[ "$ch" == "░" ]]; then
                        out+="${BLUE}${ch}${RESET}"
                    elif [[ "$ch" != " " ]]; then
                        out+="${GREEN}${ch}${RESET}"
                    else
                        out+=" "
                    fi
                elif [[ "$ch" != " " ]]; then
                    local r=$((RANDOM % ${#GLITCH[@]}))
                    out+="${DIM}${GLITCH[$r]}${RESET}"
                else
                    out+=" "
                fi
                ((pos++))
            done
            echo -e "$out"
        done
        sleep 0.12
    done

    echo ""
    echo -e "  ${GREEN}${BOLD}A R C H A O N  O S${RESET}"
    echo -e "  ${BLUE}aon v0.1.3 — Chaotic Crow 🐦‍⬛${RESET}"
    echo ""
}

crow_log() {
    echo -e "${BLUE}  🐦‍⬛  $1${RESET}"
    sleep 0.8
}

# Check pyfiglet first for the animation
pip install pyfiglet -q --break-system-packages 2>/dev/null || pip install pyfiglet -q 2>/dev/null

animate_logo

crow_log "Waking up the crow..."
crow_log "Pecking at seeds..."
crow_log "Raiding rival humans..."
crow_log "Stealing shiny packages..."
crow_log "Cawing at dependencies..."
crow_log "Sharpening talons..."

crow_log "Building the nest..."
pip install textual requests rich --break-system-packages -q 2>/dev/null || \
pip install textual requests rich -q 2>/dev/null

crow_log "Hiding treasures..."
curl -fsSL https://raw.githubusercontent.com/archaon-os/archaon-aon/main/aon.py -o /tmp/aon.py 2>/dev/null

crow_log "Claiming territory..."
sudo cp /tmp/aon.py /usr/local/bin/aon 2>/dev/null
sudo chmod +x /usr/local/bin/aon 2>/dev/null
rm -f /tmp/aon.py

crow_log "Teaching the crow to speak..."

echo ""
echo -e "${GREEN}  ✓ aon v0.1.3 installed successfully! 🐦‍⬛${RESET}"
echo -e "${BLUE}  Run 'aon' to get started.${RESET}"
echo ""