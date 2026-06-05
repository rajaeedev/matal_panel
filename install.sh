```bash
#!/bin/bash
set -e

APP_NAME="ov-panel"
INSTALL_DIR="/opt/$APP_NAME"
REPO_URL="https://github.com/rajaeedev/matal_panel.git"
REPO_BRANCH="fix-panel-node-user-flow"

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

echo -e "${YELLOW}Updating system...${NC}"
apt update -y
apt install -y python3 python3-full python3-venv wget curl git build-essential

echo -e "${YELLOW}Installing uv...${NC}"
curl -LsSf https://astral.sh/uv/install.sh | sh

export PATH="$HOME/.local/bin:$PATH"
grep -qxF 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

if ! command -v uv >/dev/null 2>&1; then
    echo -e "${RED}uv installation failed or uv is not in PATH.${NC}"
    exit 1
fi

if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Cloning fixed OV-Panel fork...${NC}"
    git clone --branch "$REPO_BRANCH" "$REPO_URL" "$INSTALL_DIR"
else
    echo -e "${GREEN}Directory exists: $INSTALL_DIR${NC}"
    echo -e "${YELLOW}Updating existing installation from fork...${NC}"
    cd "$INSTALL_DIR"

    if [ -d ".git" ]; then
        git remote set-url origin "$REPO_URL"
        git fetch origin
        git checkout "$REPO_BRANCH"
        git pull origin "$REPO_BRANCH"
    else
        echo -e "${RED}$INSTALL_DIR exists but is not a git repository.${NC}"
        echo -e "${RED}Move it away or delete it, then run this installer again.${NC}"
        echo -e "${YELLOW}Example:${NC}"
        echo "mv $INSTALL_DIR ${INSTALL_DIR}.backup.\$(date +%Y%m%d-%H%M%S)"
        exit 1
    fi
fi

cd "$INSTALL_DIR"

echo -e "${YELLOW}Installing Python dependencies...${NC}"
uv sync

echo -e "${YELLOW}Installing Node.js 20...${NC}"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

echo -e "${YELLOW}Installing frontend dependencies and building...${NC}"
cd "$INSTALL_DIR/frontend"
URLPATH=metal npm install
URLPATH=metal npm run build

cd "$INSTALL_DIR"

echo -e "${YELLOW}Running OV-Panel installer...${NC}"
uv run python installer.py

echo -e "${GREEN}OV-Panel installation completed.${NC}"
echo -e "${GREEN}Open your panel at:${NC}"
echo "http://YOUR_SERVER_IP:8443/metal/"
```
