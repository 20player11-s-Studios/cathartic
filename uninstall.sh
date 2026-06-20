#!/bin/bash
set -e

APP="cathartic"
DEST="${DESTDIR:-$HOME/.local}"
BINDIR="$DEST/bin"
APPDIR="$DEST/share/applications"
ICONDIR="$DEST/share/icons/hicolor/256x256/apps"
METADIR="$DEST/share/metainfo"

EXISTING=$(command -v cathartic 2>/dev/null || true)
if [ -z "$EXISTING" ] && [ ! -f "$BINDIR/$APP" ]; then
    echo "cathartic is not installed."
    exit 0
fi

echo "Found cathartic at: ${EXISTING:-$BINDIR/$APP}"
echo "This will remove:"
echo "  - $BINDIR/$APP"
echo "  - $APPDIR/cathartic.desktop"
echo "  - $ICONDIR/cathartic.png"
echo "  - $METADIR/io.github.cathartic.appdata.xml"
if grep -q "$BINDIR" "$HOME/.bashrc" 2>/dev/null; then
    echo "  - PATH entry in ~/.bashrc"
fi
if grep -q "$BINDIR" "$HOME/.zshrc" 2>/dev/null; then
    echo "  - PATH entry in ~/.zshrc"
fi
if grep -q "$BINDIR" "$HOME/.config/fish/config.fish" 2>/dev/null; then
    echo "  - PATH entry in ~/.config/fish/config.fish"
fi

echo
echo -n "Uninstall cathartic? [y/N] "
read -r ans
if [ "$ans" != "y" ] && [ "$ans" != "Y" ]; then
    echo "Aborted."
    exit 0
fi

rm -f "$BINDIR/$APP"
rm -f "$APPDIR/cathartic.desktop"
rm -f "$ICONDIR/cathartic.png"
rm -f "$METADIR/io.github.cathartic.appdata.xml"

for RC in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$RC" ]; then
        sed -i "/# Added by Cathartic installer/d" "$RC" 2>/dev/null || true
        sed -i "\|$BINDIR|d" "$RC" 2>/dev/null || true
    fi
done

if [ -f "$HOME/.config/fish/config.fish" ]; then
    sed -i "/$BINDIR/d" "$HOME/.config/fish/config.fish" 2>/dev/null || true
fi

echo "cathartic uninstalled."
echo "Run 'exec $SHELL' or start a new terminal to update PATH."
