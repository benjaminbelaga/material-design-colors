#!/usr/bin/env python3
"""Verify every generated theme file matches palette.json (single source of truth).

Also cross-checks live local sources (CMUX config.ghostty, iTerm preset) when
present — those are skipped silently on machines that don't have them.

Usage: python3 scripts/check_parity.py   (exit 0 = parity OK, 1 = drift)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME = "material-design-colors"


def hexs(p):
    out = [p["background"], p["foreground"], p["cursor"]["cursor"], p["cursor"]["text"],
           p["selection"]["background"], p["selection"]["foreground"], p["bold"]]
    out += p["ansi"]
    return [h.upper() for h in out]


def parse_ghostty(text):
    vals = {}
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("palette ="):
            i, c = line.split("=", 1)[1].split("=")
            vals[f"ansi{i.strip()}"] = c.strip().upper()
        elif "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip().upper()
    return vals


def main():
    p = json.loads((ROOT / "palette.json").read_text())
    expected = hexs(p)
    errors = []

    # 1. Ghostty projection
    g = parse_ghostty((ROOT / "themes" / f"{NAME}.ghostty").read_text())
    got = [g.get("background"), g.get("foreground"), g.get("cursor-color"), g.get("cursor-text"),
           g.get("selection-background"), g.get("selection-foreground"), g.get("bold")]
    got += [g.get(f"ansi{i}") for i in range(16)]
    for e, a in zip(expected, got):
        if e != a:
            errors.append(f"ghostty: expected {e} got {a}")

    # 2. Alacritty / WezTerm / kitty / warp — regex-extract every #RRGGBB and compare sets
    #    Warp's YAML schema has no cursor/selection keys — only bg/fg/ANSI apply there.
    warp_expected = set(expected[:2] + expected[7:])
    for fname, exp in ((f"{NAME}.alacritty.toml", set(expected)), (f"{NAME}.wezterm.toml", set(expected)),
                       (f"{NAME}.kitty.conf", set(expected)), (f"{NAME}.warp.yaml", warp_expected)):
        text = (ROOT / "themes" / fname).read_text()
        found = {m.upper() for m in re.findall(r"#[0-9A-Fa-f]{6}", text)}
        missing = exp - found
        if missing:
            errors.append(f"{fname}: missing colors {sorted(missing)}")

    # 3. iTermcolors round-trip
    import plistlib
    with (ROOT / "themes" / f"{NAME}.itermcolors").open("rb") as f:
        doc = plistlib.load(f)

    def to_hex(c):
        return "#%02X%02X%02X" % tuple(round(c[k] * 255) for k in ("Red Component", "Green Component", "Blue Component"))

    it_keys = ["Background Color", "Foreground Color", "Cursor Color", "Cursor Text Color",
               "Selection Color", "Selected Text Color", "Bold Color"] + [f"Ansi {i} Color" for i in range(16)]
    for k, e in zip(it_keys, expected):
        got_h = to_hex(doc[k])
        if got_h != e:
            errors.append(f"itermcolors {k}: expected {e} got {got_h}")

    # 4. Local live sources (best-effort drift check)
    local = Path.home() / "Library/Application Support/com.cmuxterm.app/config.ghostty"
    if local.exists():
        lg = parse_ghostty(local.read_text())
        for key, e in (("background", expected[0]), ("foreground", expected[1])):
            if lg.get(key) and lg[key] != e:
                errors.append(f"LOCAL CMUX config.ghostty {key}: {lg[key]} != palette {e}")
        for i in range(16):
            if lg.get(f"ansi{i}") and lg[f"ansi{i}"] != expected[7 + i]:
                errors.append(f"LOCAL CMUX palette {i}: {lg[f'ansi{i}']} != {expected[7 + i]}")

    if errors:
        print("PARITY FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print(f"PARITY OK — {len(expected)} colors match across all projections"
          + (" (+ local CMUX source)" if local.exists() else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
