#!/usr/bin/env python3
"""Generate terminal theme files from palette.json (the single source of truth).

Usage: python3 scripts/generate.py
Outputs land in themes/ plus a preview.png at the repo root.
"""
import json
import plistlib
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEMES = ROOT / "themes"
NAME = "material-design-colors"


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))


def hex_to_rgb_int(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def iterm_color(hexval):
    r, g, b = hex_to_rgb(hexval)
    return {
        "Red Component": r,
        "Green Component": g,
        "Blue Component": b,
        "Alpha Component": 1.0,
        "Color Space": "sRGB",
    }


def gen_itermcolors(p):
    doc = {
        "Ansi 0 Color": iterm_color(p["ansi"][0]),
        "Ansi 1 Color": iterm_color(p["ansi"][1]),
        "Ansi 2 Color": iterm_color(p["ansi"][2]),
        "Ansi 3 Color": iterm_color(p["ansi"][3]),
        "Ansi 4 Color": iterm_color(p["ansi"][4]),
        "Ansi 5 Color": iterm_color(p["ansi"][5]),
        "Ansi 6 Color": iterm_color(p["ansi"][6]),
        "Ansi 7 Color": iterm_color(p["ansi"][7]),
        "Ansi 8 Color": iterm_color(p["ansi"][8]),
        "Ansi 9 Color": iterm_color(p["ansi"][9]),
        "Ansi 10 Color": iterm_color(p["ansi"][10]),
        "Ansi 11 Color": iterm_color(p["ansi"][11]),
        "Ansi 12 Color": iterm_color(p["ansi"][12]),
        "Ansi 13 Color": iterm_color(p["ansi"][13]),
        "Ansi 14 Color": iterm_color(p["ansi"][14]),
        "Ansi 15 Color": iterm_color(p["ansi"][15]),
        "Background Color": iterm_color(p["background"]),
        "Foreground Color": iterm_color(p["foreground"]),
        "Bold Color": iterm_color(p["bold"]),
        "Cursor Color": iterm_color(p["cursor"]["cursor"]),
        "Cursor Text Color": iterm_color(p["cursor"]["text"]),
        "Selection Color": iterm_color(p["selection"]["background"]),
        "Selected Text Color": iterm_color(p["selection"]["foreground"]),
        "Link Color": iterm_color(p["ansi"][4]),
        "Badge Color": iterm_color(p["ansi"][5]),
    }
    out = THEMES / f"{NAME}.itermcolors"
    with out.open("wb") as f:
        plistlib.dump(doc, f)
    return out


def gen_ghostty(p):
    lines = [
        f"# {NAME} — Ghostty / CMUX theme",
        f"# https://github.com/benjaminbelaga/{NAME}",
        "",
        f"background = {p['background']}",
        f"foreground = {p['foreground']}",
        f"cursor-color = {p['cursor']['cursor']}",
        f"cursor-text = {p['cursor']['text']}",
        f"selection-background = {p['selection']['background']}",
        f"selection-foreground = {p['selection']['foreground']}",
        f"bold = {p['bold']}",
        "",
    ]
    for i, c in enumerate(p["ansi"]):
        lines.append(f"palette = {i}={c}")
    out = THEMES / f"{NAME}.ghostty"
    out.write_text("\n".join(lines) + "\n")
    return out


def gen_kitty(p):
    lines = [
        f"# {NAME} — kitty theme",
        f"background {p['background']}",
        f"foreground {p['foreground']}",
        f"cursor {p['cursor']['cursor']}",
        f"cursor_text_color {p['cursor']['text']}",
        f"selection_background {p['selection']['background']}",
        f"selection_foreground {p['selection']['foreground']}",
    ]
    names = [
        "color0", "color1", "color2", "color3", "color4", "color5", "color6", "color7",
        "color8", "color9", "color10", "color11", "color12", "color13", "color14", "color15",
    ]
    for n, c in zip(names, p["ansi"]):
        lines.append(f"{n} {c}")
    out = THEMES / f"{NAME}.kitty.conf"
    out.write_text("\n".join(lines) + "\n")
    return out


def gen_alacritty(p):
    lines = [
        f"# {NAME} — Alacritty theme (TOML)",
        "[colors.primary]",
        f'background = "{p["background"]}"',
        f'foreground = "{p["foreground"]}"',
        "",
        "[colors.cursor]",
        f'text = "{p["cursor"]["text"]}"',
        f'cursor = "{p["cursor"]["cursor"]}"',
        "",
        "[colors.selection]",
        f'text = "{p["selection"]["foreground"]}"',
        f'background = "{p["selection"]["background"]}"',
        "",
        "[colors.normal]",
    ]
    for i in range(8):
        lines.append(f'color{i} = "{p["ansi"][i]}"')
    lines += ["", "[colors.bright]"]
    for i in range(8, 16):
        lines.append(f'color{i} = "{p["ansi"][i]}"')
    out = THEMES / f"{NAME}.alacritty.toml"
    out.write_text("\n".join(lines) + "\n")
    return out


def gen_warp(p):
    lines = [
        f"# {NAME} — Warp theme (YAML)",
        "name: material-design-colors",
        f"accent: '{p['ansi'][4]}'",
        f"background: '{p['background']}'",
        "details: darker",
        f"foreground: '{p['foreground']}'",
        "terminal_colors:",
        "  normal:",
        f"    black: '{p['ansi'][0]}'",
        f"    red: '{p['ansi'][1]}'",
        f"    green: '{p['ansi'][2]}'",
        f"    yellow: '{p['ansi'][3]}'",
        f"    blue: '{p['ansi'][4]}'",
        f"    magenta: '{p['ansi'][5]}'",
        f"    cyan: '{p['ansi'][6]}'",
        f"    white: '{p['ansi'][7]}'",
        "  bright:",
        f"    black: '{p['ansi'][8]}'",
        f"    red: '{p['ansi'][9]}'",
        f"    green: '{p['ansi'][10]}'",
        f"    yellow: '{p['ansi'][11]}'",
        f"    blue: '{p['ansi'][12]}'",
        f"    magenta: '{p['ansi'][13]}'",
        f"    cyan: '{p['ansi'][14]}'",
        f"    white: '{p['ansi'][15]}'",
    ]
    out = THEMES / f"{NAME}.warp.yaml"
    out.write_text("\n".join(lines) + "\n")
    return out


def gen_wezterm(p):
    names = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    lines = [
        f"# {NAME} — WezTerm color scheme (colors/ directory format)",
        "[colors]",
        f'foreground = "{p["foreground"]}"',
        f'background = "{p["background"]}"',
        f'cursor_bg = "{p["cursor"]["cursor"]}"',
        f'cursor_fg = "{p["cursor"]["text"]}"',
        f'cursor_border = "{p["cursor"]["cursor"]}"',
        f'selection_bg = "{p["selection"]["background"]}"',
        f'selection_fg = "{p["selection"]["foreground"]}"',
        "",
        "[colors.ansi]",
    ]
    for n, c in zip(names, p["ansi"][:8]):
        lines.append(f'{n} = "{c}"')
    lines += ["", "[colors.brights]"]
    for n, c in zip(names, p["ansi"][8:]):
        lines.append(f'{n} = "{c}"')
    out = THEMES / f"{NAME}.wezterm.toml"
    out.write_text("\n".join(lines) + "\n")
    return out


def write_png(path, w, h, rows):
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b""
    for y in range(h):
        raw += b"\x00" + b"".join(struct.pack("BBBB", *rows[y][x]) for x in range(w))
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def _find_mono_font():
    candidates = [
        Path.home() / "Library/Fonts/CaskaydiaCoveNerdFont-Regular.ttf",
        Path.home() / "Library/Fonts/CaskaydiaCoveNerdFontMono-Regular.ttf",
        "/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Menlo.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return str(c)
    return None


def gen_preview(p):
    """Render a terminal-like preview. Uses Pillow when available, else swatches."""
    out = ROOT / "preview.png"
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return _gen_preview_swatches(p, out)

    w, h = 960, 600
    bg = hex_to_rgb_int(p["background"])
    fg = hex_to_rgb_int(p["foreground"])
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    font_path = _find_mono_font()
    font = ImageFont.truetype(font_path, 15) if font_path else ImageFont.load_default()
    small = ImageFont.truetype(font_path, 13) if font_path else font

    # Title bar
    bar = tuple(max(0, c - 12) for c in bg)
    d.rectangle([0, 0, w, 40], fill=bar)
    for i, dot in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([18 + i * 24, 13, 34 + i * 24, 29], fill=dot)
    d.text((w // 2 - 110, 12), "material-design-colors", fill=fg, font=small)

    def line(x, y, spans):
        for text, color in spans:
            d.text((x, y), text, fill=color, font=font)
            x += d.textlength(text, font=font)
        return y + 26

    y = 64
    prompt = p["ansi"][2]
    path_c = p["ansi"][4]
    y = line(24, y, [("~/material-design-colors ", prompt), ("$ ", fg), ("echo $TERM_PROGRAM", path_c)])
    y = line(24, y, [("CMUX / Ghostty · iTerm2 · kitty · Alacritty · Warp · WezTerm", fg)])
    y += 10
    y = line(24, y, [("normal  ", fg)] + [(f"██ ", p["ansi"][i]) for i in range(8)])
    y = line(24, y, [("bright  ", fg)] + [(f"██ ", p["ansi"][i]) for i in range(8, 16)])
    y += 10
    y = line(24, y, [("error   ", fg), ("command not found: foo", p["ansi"][1])])
    y = line(24, y, [("warn    ", fg), ("3 files changed, 12 insertions(+)", p["ansi"][3])])
    y = line(24, y, [("info    ", fg), ("branch ", p["ansi"][6]), ("main", p["ansi"][5]), (" · 2 unpushed", p["ansi"][8])])
    y = line(24, y, [("comment ", p["ansi"][8]), ("# generated from palette.json", p["ansi"][8])])
    y += 10
    # Selection + cursor samples
    sel = hex_to_rgb_int(p["selection"]["background"])
    sel_fg = hex_to_rgb_int(p["selection"]["foreground"])
    d.rectangle([24, y, 24 + int(d.textlength("selected text", font=font)) + 12, y + 24], fill=sel)
    d.text((30, y + 2), "selected text", fill=sel_fg, font=font)
    cx = 24 + int(d.textlength("selected text", font=font)) + 36
    d.text((cx, y + 2), "cursor ", fill=fg, font=font)
    cw = d.textlength("cursor ", font=font)
    cur = hex_to_rgb_int(p["cursor"]["cursor"])
    d.rectangle([cx + cw, y, cx + cw + 12, y + 24], fill=cur)

    img.save(out)
    return out


def _gen_preview_swatches(p, out):
    w, h = 960, 540
    bg = hex_to_rgb_int(p["background"])
    rows = [[bg + (255,)] * w for _ in range(h)]
    margin, gap = 40, 12
    sw = (w - 2 * margin - 7 * gap) // 8
    for band, base in enumerate((0, 8)):
        y0 = 260 + band * (sw + gap)
        for i in range(8):
            col = hex_to_rgb_int(p["ansi"][base + i])
            x0 = margin + i * (sw + gap)
            for y in range(y0, min(y0 + sw, h)):
                for x in range(x0, min(x0 + sw, w)):
                    rows[y][x] = col + (255,)
    write_png(out, w, h, rows)
    return out


def main():
    p = json.loads((ROOT / "palette.json").read_text())
    THEMES.mkdir(exist_ok=True)
    for gen in (gen_itermcolors, gen_ghostty, gen_kitty, gen_alacritty, gen_warp, gen_wezterm, gen_preview):
        out = gen(p)
        print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
