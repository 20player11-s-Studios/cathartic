#!/bin/bash
set -e

APPIMAGE="build/dist/Cathartic-x86_64.AppImage"
APP="cathartic"
VER="0.1.0"

if [ ! -f "$APPIMAGE" ]; then
    echo "AppImage not found at $APPIMAGE" >&2
    echo "Run 'make appimage' first." >&2
    exit 1
fi

DEST="${DESTDIR:-$HOME/.local}"
BINDIR="$DEST/bin"
APPDIR="$DEST/share/applications"
ICONDIR="$DEST/share/icons/hicolor/256x256/apps"
METADIR="$DEST/share/metainfo"

EXISTING=$(command -v cathartic 2>/dev/null || true)
if [ -n "$EXISTING" ]; then
    echo "cathartic already installed at: $EXISTING"
    echo -n "Reinstall? [y/N] "
    read -r ans
    if [ "$ans" != "y" ] && [ "$ans" != "Y" ]; then
        echo "Aborted."
        exit 0
    fi
    if [ "$EXISTING" != "$BINDIR/$APP" ]; then
        rm -f "$EXISTING"
        echo "Removed old entry: $EXISTING"
    fi
fi

mkdir -p "$BINDIR" "$APPDIR" "$ICONDIR" "$METADIR"

install -m 755 "$APPIMAGE" "$BINDIR/$APP"
install -m 644 build/AppDir/cathartic.desktop "$APPDIR/"
install -m 644 build/AppDir/cathartic.png "$ICONDIR/"
install -m 644 build/AppDir/usr/share/metainfo/io.github.cathartic.appdata.xml "$METADIR/"

echo "Installed Cathartic $VER to $DEST"

if ! command -v cathartic &>/dev/null; then
    RC="$HOME/.bashrc"
    [[ -n "$ZSH_VERSION" ]] && RC="$HOME/.zshrc"
    if [[ -f "$HOME/.config/fish/config.fish" ]]; then
        if ! grep -q "$BINDIR" "$HOME/.config/fish/config.fish" 2>/dev/null; then
            echo "fish_add_path $BINDIR" >> "$HOME/.config/fish/config.fish"
        fi
        export PATH="$PATH:$BINDIR"
        echo "Added $BINDIR to fish PATH. Run: exec fish"
    else
        if ! grep -q "$BINDIR" "$RC" 2>/dev/null; then
            echo "" >> "$RC"
            echo "# Added by Cathartic installer" >> "$RC"
            echo "export PATH=\"\$PATH:$BINDIR\"" >> "$RC"
        fi
        export PATH="$PATH:$BINDIR"
        echo "Added $BINDIR to $RC. Run: source $RC"
    fi
else
    echo "cathartic is in your PATH"
fi

for dup in $(which -a cathartic 2>/dev/null); do
    if [ "$dup" != "$BINDIR/$APP" ]; then
        rm -f "$dup"
        echo "Removed duplicate: $dup"
    fi
done
