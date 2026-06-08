#!/bin/bash
# scripts/setup.sh
# ============================================================
# One-command development environment setup for ApolloDroid.
#
# What this does:
#   1. Checks Python and Java are installed
#   2. Creates a Python virtual environment
#   3. Installs all dependencies
#   4. Copies .env.example → .env (if not already there)
#   5. Creates the wake word models directory
#   6. Prints next steps
#
# Usage:
#   chmod +x scripts/setup.sh
#   ./scripts/setup.sh
# ============================================================

set -e  # Exit immediately if any command fails

# ---- Colors for output ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step()  { echo -e "\n${BLUE}▶ $1${NC}"; }
print_ok()    { echo -e "${GREEN}✓ $1${NC}"; }
print_warn()  { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }

echo -e "${BLUE}"
echo "  ___              ____           ____            _     _ "
echo " / _ \            |  _ \         |  _ \          (_)   | |"
echo "| | | |  _ __   _ | |_) | _ __  | | | |  _ __    _   __| |"
echo "| |_| | | '_ \ (_)|  _ < | '__| | |_| | | '__|  | | / _\` |"
echo " \___/  | .__/    |_| \_\|_|    |____/  |_|     |_| \__,_|"
echo "        | |"
echo "        |_|   Development Setup"
echo -e "${NC}"

# ============================================================
# STEP 1: Check Python version
# ============================================================
print_step "Checking Python version..."

if ! command -v python3 &>/dev/null; then
    print_error "Python 3 not found. Install it from https://python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_MAJOR=3
REQUIRED_MINOR=11

python3 -c "
import sys
if sys.version_info < (3, 11):
    print(f'Python 3.11+ required, found {sys.version}')
    sys.exit(1)
" || { print_error "Python 3.11+ is required. Found: $PYTHON_VERSION"; exit 1; }

print_ok "Python $PYTHON_VERSION found"

# ============================================================
# STEP 2: Check Java (required by Briefcase for Android builds)
# ============================================================
print_step "Checking Java JDK..."

if ! command -v java &>/dev/null; then
    print_warn "Java not found — required for Android APK builds (not needed for desktop testing)"
    echo "  Install JDK 17 from: https://adoptium.net/"
    echo "  You can continue setup and install Java later."
else
    JAVA_VERSION=$(java -version 2>&1 | head -1 | cut -d'"' -f2 | cut -d'.' -f1)
    if [ "$JAVA_VERSION" -ge 17 ] 2>/dev/null; then
        print_ok "Java $JAVA_VERSION found"
    else
        print_warn "Java 17+ recommended for Briefcase. Found: Java $JAVA_VERSION"
    fi
fi

# ============================================================
# STEP 3: Create virtual environment
# ============================================================
print_step "Creating Python virtual environment..."

if [ -d ".venv" ]; then
    print_warn ".venv already exists — skipping creation"
else
    python3 -m venv .venv
    print_ok "Virtual environment created at .venv/"
fi

# Activate the venv
source .venv/bin/activate
print_ok "Virtual environment activated"

# ============================================================
# STEP 4: Upgrade pip
# ============================================================
print_step "Upgrading pip..."
pip install --upgrade pip --quiet
print_ok "pip up to date"

# ============================================================
# STEP 5: Install dependencies
# ============================================================
print_step "Installing Python dependencies..."

# Install dev dependencies (includes production deps via -r requirements.txt)
pip install -r requirements-dev.txt --quiet
print_ok "All dependencies installed"

# ============================================================
# STEP 6: Copy .env.example → .env
# ============================================================
print_step "Setting up environment file..."

if [ -f ".env" ]; then
    print_warn ".env already exists — not overwriting (your keys are safe)"
else
    cp .env.example .env
    print_ok ".env created from template"
    print_warn "Open .env and add your API keys before running Apollo!"
fi

# ============================================================
# STEP 7: Create wake word models directory
# ============================================================
print_step "Creating wake word models directory..."
mkdir -p apollo/core/wakeword/models
print_ok "apollo/core/wakeword/models/ ready"

# ============================================================
# STEP 8: Create UI assets directory placeholder
# ============================================================
mkdir -p ui/assets
print_ok "ui/assets/ ready"

# ============================================================
# DONE — print next steps
# ============================================================
echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}  ✅ ApolloDroid setup complete!${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "  1. Add your API keys to .env:"
echo "     ${YELLOW}nano .env${NC}"
echo ""
echo "  2. Download your 'Hey Apollo' wake word model:"
echo "     → https://console.picovoice.ai/"
echo "     → Train 'Hey Apollo' for Android"
echo "     → Save to: apollo/core/wakeword/models/"
echo ""
echo "  3. Run Apollo on your desktop (for testing):"
echo "     ${YELLOW}source .venv/bin/activate${NC}"
echo "     ${YELLOW}briefcase dev${NC}"
echo ""
echo "  4. Build and deploy to your Android phone:"
echo "     ${YELLOW}briefcase create android${NC}   # first time only"
echo "     ${YELLOW}briefcase build android${NC}"
echo "     ${YELLOW}briefcase run android${NC}      # phone must be connected via USB"
echo ""
echo -e "  Full docs: ${BLUE}README.md${NC}"
echo ""
