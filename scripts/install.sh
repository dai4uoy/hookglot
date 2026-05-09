#!/usr/bin/env bash
# hookglot installation helper
# This is for users who clone the repo. After running this, use `hookglot install`
# for interactive setup.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🌐 hookglot installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 not found. Install Python 3.10+ first."
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python $PY_VERSION found"

# Check pip
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo "❌ pip not found. Install pip first."
    exit 1
fi
echo "✅ pip found"

# Install package
cd "$REPO_ROOT"
echo ""
echo "📦 Installing hookglot Python package..."
python3 -m pip install -e . --user --break-system-packages 2>/dev/null || \
    python3 -m pip install -e . --user

if ! command -v hookglot &> /dev/null; then
    USER_BIN="$(python3 -m site --user-base)/bin"
    if [ -d "$USER_BIN" ]; then
        echo ""
        echo "⚠️  hookglot installed but not in PATH"
        echo "   Add to your shell rc file:"
        echo "   export PATH=\"$USER_BIN:\$PATH\""
        echo ""
        echo "   Then run: hookglot install"
    fi
else
    echo "✅ hookglot CLI available"
    echo ""
    echo "Next step:"
    echo "  hookglot install"
fi
