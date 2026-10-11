#!/usr/bin/env bash
# material-design-colors — one-line installer
# Usage: bash install.sh [terminal]
#   terminal: ghostty | cmux | kitty | alacritty | warp | wezterm | iterm | all (default: auto-detect)
set -euo pipefail

REPO="benjaminbelaga/material-design-colors"
RAW="https://raw.githubusercontent.com/$REPO/main/themes"
NAME="material-design-colors"
TARGET="${1:-auto}"

fetch() { curl -fsSL "$RAW/$1" -o "$2" && echo "  installed → $2"; }

install_ghostty() {
  mkdir -p "${XDG_CONFIG_HOME:-$HOME/.config}/ghostty/themes"
  fetch "$NAME.ghostty" "${XDG_CONFIG_HOME:-$HOME/.config}/ghostty/themes/$NAME"
  echo "  add to ghostty config: theme = $NAME"
}

install_cmux() {
  local cfg="$HOME/Library/Application Support/com.cmuxterm.app/config.ghostty"
  echo "  CMUX reads Ghostty config — paste the colors from:"
  echo "    $RAW/$NAME.ghostty"
  echo "  into: $cfg (color section), or use the Ghostty themes dir above."
}

install_kitty() {
  mkdir -p "${XDG_CONFIG_HOME:-$HOME/.config}/kitty/themes"
  fetch "$NAME.kitty.conf" "${XDG_CONFIG_HOME:-$HOME/.config}/kitty/themes/$NAME.conf"
  echo "  add to kitty.conf: include themes/$NAME.conf"
}

install_alacritty() {
  mkdir -p "${XDG_CONFIG_HOME:-$HOME/.config}/alacritty"
  fetch "$NAME.alacritty.toml" "${XDG_CONFIG_HOME:-$HOME/.config}/alacritty/themes/$NAME.toml"
  echo "  add to alacritty.toml: [import] = [\"~/.config/alacritty/themes/$NAME.toml\"]"
}

install_warp() {
  mkdir -p "$HOME/.warp/themes"
  fetch "$NAME.warp.yaml" "$HOME/.warp/themes/$NAME.yaml"
  echo "  select it in Warp → Settings → Appearance"
}

install_wezterm() {
  mkdir -p "${XDG_CONFIG_HOME:-$HOME/.config}/wezterm/colors"
  fetch "$NAME.wezterm.toml" "${XDG_CONFIG_HOME:-$HOME/.config}/wezterm/colors/$NAME.toml"
  echo "  add to wezterm.lua: color_scheme = \"$NAME\""
}

install_iterm() {
  local f="/tmp/$NAME.itermcolors"
  fetch "$NAME.itermcolors" "$f"
  open "$f" && echo "  iTerm imports it — pick it under Color Presets"
}

if [[ "$TARGET" == "auto" ]]; then
  TARGET=""
  [[ -d "/Applications/cmux.app" || -d "$HOME/Library/Application Support/com.cmuxterm.app" ]] && TARGET+="cmux "
  command -v ghostty >/dev/null 2>&1 && TARGET+="ghostty "
  [[ -d "/Applications/iTerm.app" ]] && TARGET+="iterm "
  [[ -d "/Applications/kitty.app" ]] && TARGET+="kitty "
  [[ -d "$HOME/.warp" || -d "/Applications/Warp.app" ]] && TARGET+="warp "
  [[ -d "${XDG_CONFIG_HOME:-$HOME/.config}/wezterm" ]] && TARGET+="wezterm "
  [[ -d "${XDG_CONFIG_HOME:-$HOME/.config}/alacritty" ]] && TARGET+="alacritty "
  TARGET="${TARGET:-ghostty}"
  echo "auto-detected: $TARGET"
fi

for t in $TARGET; do
  case "$t" in
    ghostty) install_ghostty ;;
    cmux) install_cmux ;;
    kitty) install_kitty ;;
    alacritty) install_alacritty ;;
    warp) install_warp ;;
    wezterm) install_wezterm ;;
    iterm) install_iterm ;;
    all) install_ghostty; install_kitty; install_alacritty; install_warp; install_wezterm; install_iterm ;;
    *) echo "unknown terminal: $t" >&2; exit 1 ;;
  esac
done

echo "done — material-design-colors installed."
