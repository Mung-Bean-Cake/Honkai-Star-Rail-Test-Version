#!/usr/bin/env python3
"""Scaffold a Stellaris mod skeleton.

Creates the two descriptor files (the .mod in the Paradox mod dir and the
descriptor.mod inside the mod folder) plus the standard mirrored directory
tree, a starter event file and matching localisation (written as UTF-8-BOM,
which Stellaris requires).

Usage:
    python scaffold_mod.py "My Mod" [--out DIR] [--version 1.0]
                          [--supported "v4.0.*"] [--tags Gameplay Events]
                          [--prefix mymod] [--no-sample]
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

DEFAULT_TAGS = ["Gameplay"]

COMMON_SUBDIRS = [
    "buildings",
    "decisions",
    "edicts",
    "governments/civics",
    "governments/origins",
    "megastructures",
    "on_actions",
    "scripted_effects",
    "scripted_triggers",
    "scripted_variables",
    "ship_sizes",
    "static_modifiers",
    "technology",
    "traits",
]

TOP_DIRS = [
    "common",
    "events",
    "gfx/event_pictures",
    "gfx/interface/icons",
    "interface",
    "localisation/english",
    "localisation/simp_chinese",
    "flags",
    "sound",
    "music",
    "prescripted_countries",
]

DESCRIPTOR_TEMPLATE = """version="{version}"
tags={{
{tags}
}}
name="{name}"
supported_version="{supported}"
{path_line}"""


def build_descriptor(name: str, version: str, supported: str, tags: list[str],
                     path: str | None) -> str:
    tag_block = "\n".join(f'\t"{t}"' for t in tags)
    path_line = f'path="{path}"' if path else ""
    return DESCRIPTOR_TEMPLATE.format(
        version=version,
        tags=tag_block,
        name=name,
        supported=supported,
        path_line=path_line,
    ).rstrip() + "\n"


def write_bom(path: Path, text: str) -> None:
    """Write text as UTF-8 with BOM (required by Stellaris localisation)."""
    path.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))


def scaffold(name: str, out_dir: Path, version: str, supported: str,
             tags: list[str], prefix: str, sample: bool) -> Path:
    mod_root = out_dir / name
    if mod_root.exists():
        print(f"ERROR: {mod_root} already exists. Refusing to overwrite.",
              file=sys.stderr)
        sys.exit(1)

    for d in TOP_DIRS:
        (mod_root / d).mkdir(parents=True, exist_ok=True)
    for d in COMMON_SUBDIRS:
        (mod_root / "common" / d).mkdir(parents=True, exist_ok=True)

    # descriptor.mod inside the mod folder (no path line)
    (mod_root / "descriptor.mod").write_text(
        build_descriptor(name, version, supported, tags, None), encoding="utf-8")

    # <name>.mod sitting next to the mod folder (has the path line)
    outer = out_dir / f"{name}.mod"
    outer.write_text(
        build_descriptor(name, version, supported, tags, f"mod/{name}"),
        encoding="utf-8")

    if sample:
        write_sample(mod_root, prefix, name)

    return mod_root


def write_sample(mod_root: Path, prefix: str, name: str) -> None:
    ns = prefix

    event_text = f"""# {name} - starter event file
# Delete this file when you start writing real content.

namespace = {ns}

# Triggered-only hidden event: the recommended default pattern.
country_event = {{
\tid = {ns}.1
\thide_window = yes
\tis_triggered_only = yes
\ttrigger = {{
\t\thas_country_flag = {ns}_started
\t}}
\timmediate = {{
\t\tlog = "{prefix}: starter event fired"
\t}}
}}

# Visible event with a picture and a single option.
country_event = {{
\tid = {ns}.2
\ttitle = {ns}.2.name
\tdesc = {ns}.2.desc
\t# picture = GFX_evt_my_picture     # register this sprite in interface/*.gfx
\tis_triggered_only = yes
\timmediate = {{
\t\tset_country_flag = {ns}_started
\t}}
\toption = {{
\t\tname = {ns}.2.a
\t\tadd_modifier = {{
\t\t\tmodifier = {ns}_starter_modifier
\t\t\tmonths = 12
\t\t}}
\t}}
}}
"""
    (mod_root / "events" / f"{prefix}_events.txt").write_text(
        event_text, encoding="utf-8")

    modifier_text = f"""# {name} - static modifiers

{ns}_starter_modifier = {{
\tcountry_research_speed_mult = 0.05
\tpop_happiness = 0.05
}}
"""
    (mod_root / "common" / "static_modifiers" / f"{prefix}_modifiers.txt").write_text(
        modifier_text, encoding="utf-8")

    on_action_text = f"""# {name} - on_action hooks
# Keep the on_action names unique to avoid clashing with other mods.

on_game_start_country = {{
\tevents = {{
\t\t{ns}.1
\t}}
}}
"""
    (mod_root / "common" / "on_actions" / f"zz_{prefix}_on_actions.txt").write_text(
        on_action_text, encoding="utf-8")

    loc_en = f"""l_english:
 {ns}.2.name: "{name} - Example Event"
 {ns}.2.desc: "This is a placeholder description. Replace it with real text."
 {ns}.2.a: "Acknowledge"
 {ns}_starter_modifier: "Starter Bonus"
 {ns}_starter_modifier_desc: "A small bonus applied by the example event."
"""
    write_bom(mod_root / "localisation" / "english" / f"{prefix}_l_english.yml", loc_en)

    loc_sc = f"""l_simp_chinese:
 {ns}.2.name: "{name} - 示例事件"
 {ns}.2.desc: "这是一段占位描述，请替换为正式文本。"
 {ns}.2.a: "已阅"
 {ns}_starter_modifier: "启动物修正"
 {ns}_starter_modifier_desc: "由示例事件施加的小幅加成。"
"""
    write_bom(mod_root / "localisation" / "simp_chinese" / f"{prefix}_l_simp_chinese.yml", loc_sc)

    readme = f"""# {name}

Stellaris mod. Edit `descriptor.mod` and `{name}.mod` to keep metadata in sync.

## Layout
- `common/`  - game object definitions (tech, buildings, edicts, ...)
- `events/`  - event scripts
- `gfx/`     - textures, models
- `interface/` - .gfx sprite registration and .gui layouts
- `localisation/english/`, `localisation/simp_chinese/` - text (UTF-8 BOM!)
- `flags/`, `sound/`, `music/`, `prescripted_countries/`

## Reminder
Every new localisation file must:
1. be encoded UTF-8 **with BOM**
2. end in `_l_<language>.yml`
3. start with `l_<language>:`
"""
    (mod_root / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Scaffold a Stellaris mod skeleton.")
    ap.add_argument("name", help="Mod name (also used as the folder name)")
    ap.add_argument("--out", default=None,
                    help="Output directory. Defaults to "
                         "%%USERPROFILE%%/Documents/Paradox Interactive/Stellaris/mod")
    ap.add_argument("--version", default="0.1", help="Mod version string")
    ap.add_argument("--supported", default="v4.0.*",
                    help='Target game version, e.g. "v4.0.*"')
    ap.add_argument("--tags", nargs="*", default=DEFAULT_TAGS,
                    help="Workshop tags (max 10)")
    ap.add_argument("--prefix", default=None,
                    help="Script key prefix. Defaults to a slug of the name")
    ap.add_argument("--no-sample", action="store_true",
                    help="Create an empty skeleton without sample content")
    args = ap.parse_args()

    if len(args.tags) > 10:
        print("ERROR: at most 10 tags are allowed.", file=sys.stderr)
        sys.exit(1)

    if args.out:
        out_dir = Path(args.out).expanduser().resolve()
    else:
        out_dir = (Path.home() / "Documents" / "Paradox Interactive"
                   / "Stellaris" / "mod")

    prefix = args.prefix or "".join(
        c.lower() for c in args.name if c.isalnum()) or "mymod"

    mod_root = scaffold(args.name, out_dir, args.version, args.supported,
                        args.tags, prefix, not args.no_sample)

    print(f"Created mod skeleton at: {mod_root}")
    print(f"Descriptor (.mod) at:    {out_dir / (args.name + '.mod')}")
    print(f"Script prefix in use:    {prefix}")
    print()
    print("Next steps:")
    print("  1. Drop a thumbnail.png into the mod root.")
    print("  2. Write content under common/ and events/.")
    print("  3. Add matching localisation under localisation/<lang>/.")
    print("  4. Run: python validate_mod.py \"" + str(mod_root) + "\"")


if __name__ == "__main__":
    main()
