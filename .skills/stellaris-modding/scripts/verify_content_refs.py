#!/usr/bin/env python3
"""Check that every *referenced* content key in a Stellaris mod actually exists.

`validate_mod.py` lints structure and syntax. This script answers the other half of
the question: "did I reference something that isn't there?" -- the failure mode that
is **silent** in game (no crash, no error.log line, the content simply never appears).

What it verifies, across the mod's `common/` and `events/`:

  * `d_<name>`            -> defined in game/mod `common/deposits/`
  * `building_<name>`     -> defined in `common/buildings/`
  * `district_<name>`     -> defined in `common/districts/`
  * `tech_<name>`         -> defined in `common/technology/`
  * `trait_<name>`        -> defined in `common/traits/`
  * `civic_<name>`        -> defined in `common/governments/civics/`
  * `origin_<name>`       -> defined in `common/governments/civics/`
  * `job_<name>`          -> defined in `common/pop_jobs/`
  * `pc_<name>`           -> defined in `common/planet_classes/`
  * `GFX_<name>`          -> a spriteType `name = "GFX_..."` in any `interface/**/*.gfx`
  * `icon = "gfx/...dds"` / `texturefile = "gfx/..."`  -> file exists on disk
  * loc keys referenced via title/desc/name/text/custom_tooltip/fail_text/tooltip
    -> defined in any `localisation/**/*.yml` of game+mod

The game install path is auto-detected from, in order:
  1. `--game <path>`
  2. the `path` field of the mod's `<name>.mod` descriptor, walking up to the
     `steamapps/common/Stellaris` root
  3. the `STELLARIS_PATH` environment variable

Usage:
    python verify_content_refs.py <mod-root> [--game <stellaris-root>] [--quiet]

Exit code 1 if anything is missing.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- helpers

MOD_ROOTS = ("common", "events")
GAME_SUBDIRS = {
    "d_": "common/deposits",
    "building_": "common/buildings",
    "district_": "common/districts",
    "tech_": "common/technology",
    "trait_": "common/traits",
    "civic_": "common/governments/civics",
    "origin_": "common/governments/civics",
    "job_": "common/pop_jobs",
    "pc_": "common/planet_classes",
    "ethic_": "common/ethics",
}

MISSING: dict[str, set[str]] = {}
CHECKED = 0


def note(kind: str, key: str) -> None:
    MISSING.setdefault(kind, set()).add(key)


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8-sig", errors="ignore")
    except OSError:
        return ""


def strip_comments(text: str) -> str:
    return re.sub(r"#[^\n]*", "", text)


def strip_brackets(text: str) -> str:
    """Drop data-function calls (`[Root.GetName]`) so they are not mistaken for
    localisation keys."""
    return re.sub(r"\[[^\]]*\]", "", text)


def iter_script_files(mod: Path):
    for sub in MOD_ROOTS:
        base = mod / sub
        if not base.is_dir():
            continue
        for p in base.rglob("*.txt"):
            yield p


# ---------------------------------------------------------------- databases

def build_definition_index(game: Path, mod: Path) -> dict[str, set[str]]:
    """Collect every defined key, per prefix, from game + mod."""
    idx: dict[str, set[str]] = {k: set() for k in GAME_SUBDIRS}
    for root in (game, mod):
        for prefix, sub in GAME_SUBDIRS.items():
            d = root / sub
            if not d.is_dir():
                continue
            for f in d.rglob("*.txt"):
                t = strip_comments(read_text(f))
                for m in re.finditer(r"(?m)^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{", t):
                    idx[prefix].add(m.group(1))
                # technology entries are also declared as `name = { ... }` inside
                # `technology = { ... }` in some versions; capture `key = {` anyway
    return idx


def build_gfx_index(game: Path, mod: Path) -> set[str]:
    keys: set[str] = set()
    for root in (game, mod):
        for d in (root / "interface", root / "gfx"):
            if not d.is_dir():
                continue
            for f in d.rglob("*.gfx"):
                t = read_text(f)
                keys |= set(re.findall(r'name\s*=\s*"(GFX_[A-Za-z0-9_]+)"', t))
                keys |= set(re.findall(r'name\s*=\s*(GFX_[A-Za-z0-9_]+)', t))
        for f in (root / "gfx").rglob("*.asset"):
            t = read_text(f)
            keys |= set(re.findall(r'name\s*=\s*"(GFX_[A-Za-z0-9_]+)"', t))
    return keys


def build_loc_index(game: Path, mod: Path) -> set[str]:
    keys: set[str] = set()
    for root in (game, mod):
        d = root / "localisation"
        if not d.is_dir():
            continue
        for f in d.rglob("*.yml"):
            t = read_text(f)
            keys |= set(
                re.findall(r'(?m)^\s*([A-Za-z0-9_.\-]+)\s*:\s*\d*\s*"', t)
            )
    return keys


# ---------------------------------------------------------------- checks

LOC_FIELDS = ("title", "desc", "name", "text", "fail_text", "tooltip",
              "custom_tooltip", "text", "response_text", "location")


def check_references(mod: Path, game: Path, idx, gfx, loc) -> None:
    global CHECKED
    token_re = re.compile(r"\b(" + "|".join(re.escape(p) for p in GAME_SUBDIRS) + r")[A-Za-z0-9_]*\b")
    gfx_re = re.compile(r"\bGFX_[A-Za-z0-9_]+\b")
    path_re = re.compile(r'(?:icon|texturefile|picture|sprite)\s*=\s*"([^"]+\.(?:dds|tga|png))"')
    loc_field_re = re.compile(
        r'(?m)^\s*(?:' + "|".join(LOC_FIELDS) + r')\s*=\s*"?([A-Za-z0-9_.\-]+)"?\s*$'
    )

    for f in iter_script_files(mod):
        raw = read_text(f)
        txt = strip_brackets(strip_comments(raw))

        for tok in set(token_re.findall(txt)):
            CHECKED += 1
            prefix = next(p for p in GAME_SUBDIRS if tok.startswith(p))
            if tok == prefix:          # bare prefix such as `trait_`, not a key
                continue
            if tok not in idx[prefix]:
                note(f"{prefix}* (定义于 {GAME_SUBDIRS[prefix]})", tok)

        for g in set(gfx_re.findall(txt)):
            CHECKED += 1
            if g not in gfx:
                note("GFX_* (interface/*.gfx)", g)

        for rel_path in set(path_re.findall(txt)):
            CHECKED += 1
            # gfx paths resolve against the merged virtual filesystem: mod first,
            # then the base-game install.
            cand = [mod / rel_path, game / rel_path, Path(rel_path)]
            if not any(c.exists() for c in cand):
                note("资源文件路径", rel_path)

        for key in set(loc_field_re.findall(txt)):
            # skip pure numbers / scope keywords / engine constants
            if key.isdigit() or key in ("random", "this", "root", "prev", "from",
                                        "yes", "no", "none"):
                continue
            # Only report keys that are *shaped* like localisation keys. Many
            # `name = X` fields legitimately hold non-loc identifiers (ship name
            # list entries such as L_GUN_01, design names, etc.), so the filter
            # is deliberately narrow: event keys (ns.123.field), NAME_* keys, and
            # keys carrying a conventional localisation suffix.
            LOOKS_LOC = (
                key.startswith("NAME_")
                or "." in key
                or key.endswith(("_tt", "_desc", "_tooltip", "_name", "_type",
                                 "_outcome", "_plural", "_adj", "_response"))
            )
            if not LOOKS_LOC:
                continue
            if re.fullmatch(r"[a-z_]+_event", key):
                continue
            CHECKED += 1
            if key not in loc:
                note("本地化键", key)


# ---------------------------------------------------------------- entry

def find_game_root(mod: Path, explicit: str | None) -> Path | None:
    if explicit:
        return Path(explicit)
    env = os.environ.get("STELLARIS_PATH")
    if env:
        return Path(env)
    # walk up from the mod folder looking for a sibling "Stellaris" install
    for anc in mod.resolve().parents:
        cand = anc / "Stellaris"
        if (cand / "common").is_dir():
            return cand
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mod_root")
    ap.add_argument("--game", default=None)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    mod = Path(a.mod_root)
    if not mod.is_dir():
        print(f"not a directory: {mod}", file=sys.stderr)
        return 1

    game = find_game_root(mod, a.game)
    if game is None or not (game / "common").is_dir():
        print("could not locate the Stellaris install; pass --game <path>", file=sys.stderr)
        return 1
    if not a.quiet:
        print(f"mod : {mod}\ngame: {game}\n")

    idx = build_definition_index(game, mod)
    gfx = build_gfx_index(game, mod)
    loc = build_loc_index(game, mod)
    if not a.quiet:
        print(f"indexed: " + ", ".join(f"{k}={len(v)}" for k, v in idx.items()))
        print(f"         GFX={len(gfx)}  loc={len(loc)}\n")

    check_references(mod, game, idx, gfx, loc)

    total = sum(len(v) for v in MISSING.values())
    if not total:
        print(f"OK — {CHECKED} references checked, none missing.")
        return 0

    for kind in sorted(MISSING):
        keys = sorted(MISSING[kind])
        print(f"[MISSING] {kind}  ({len(keys)})")
        for k in keys[:60]:
            print(f"    {k}")
        if len(keys) > 60:
            print(f"    ... and {len(keys) - 60} more")
    print(f"\n{total} missing reference(s) out of {CHECKED} checked.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
