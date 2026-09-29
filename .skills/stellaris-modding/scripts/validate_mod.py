#!/usr/bin/env python3
"""Lint a Stellaris mod folder for the mistakes that actually bite.

Checks performed:
  * descriptor.mod / <name>.mod presence, required fields, path slash style
  * folder naming (localisation vs localization)
  * localisation files: UTF-8 BOM, `_l_<lang>.yml` naming, `l_<lang>:` header,
    illegal unicode characters, duplicate keys
  * script files: brace balance, event id format, duplicate top-level event ids,
    missing namespace declarations
  * event localisation: title/desc keys referenced by an event must be defined
  * GFX_ sprite references with no matching registration in interface/*.gfx

Only true top-level event definitions are treated as events; nested
`country_event = { id = ... }` calls inside another event are not.

Usage:
    python validate_mod.py <path-to-mod-root-or-descriptor>
Exit code is 1 when any ERROR is reported, otherwise 0.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

LANGS = ["english", "simp_chinese", "french", "german", "spanish", "russian",
         "polish", "japanese", "korean", "braz_por"]

ILLEGAL_LOC_CHARS = {
    "\u201e": "U+201E", "\u201c": "U+201C", "\u201a": "U+201A",
    "\u2018": "U+2018", "\u2013": "U+2013", "\u201d": "U+201D",
    "\u2019": "U+2019", "\u2026": "U+2026", "\u2014": "U+2014",
}

TEXT_DIRS = ("common", "events")

ERRORS: list[str] = []
WARNINGS: list[str] = []
INFOS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


def info(msg: str) -> None:
    INFOS.append(msg)


# ---------------------------------------------------------------- tokenising

def strip_comments(text: str) -> str:
    """Remove # comments but keep quoted strings intact."""
    out = []
    in_str = False
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
            continue
        if c == "#":
            while i < n and text[i] != "\n":
                i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def strip_strings(text: str) -> str:
    """Blank out quoted string contents, preserving positions and newlines."""
    out = list(text)
    in_str = False
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if in_str:
            if c == "\\" and i + 1 < n:
                if text[i] != "\n":
                    out[i] = " "
                if text[i + 1] != "\n":
                    out[i + 1] = " "
                i += 2
                continue
            if c == '"':
                in_str = False
            elif c != "\n":
                out[i] = " "
            i += 1
            continue
        if c == '"':
            in_str = True
        i += 1
    return "".join(out)


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def depth_map(bare: str) -> list[int]:
    """Return brace depth *before* each character."""
    depths = [0] * len(bare)
    d = 0
    for i, ch in enumerate(bare):
        depths[i] = d
        if ch == "{":
            d += 1
        elif ch == "}":
            d = max(0, d - 1)
    return depths


# ------------------------------------------------------------------- checks

def check_descriptor(root: Path, rel: str) -> None:
    desc = root / "descriptor.mod"
    if not desc.exists():
        err(f"{rel}/descriptor.mod is missing")
    else:
        raw = desc.read_text(encoding="utf-8", errors="replace")
        if not re.search(r'\bname\s*=\s*"', raw):
            err(f"{rel}/descriptor.mod has no name field")
        if "supported_version" not in raw:
            warn(f"{rel}/descriptor.mod has no supported_version "
                 f"(players will see an 'outdated' warning)")
        if "version" not in raw:
            info(f"{rel}/descriptor.mod has no version field")

    outer = root.parent / f"{root.name}.mod"
    if not outer.exists():
        for cand in root.parent.glob("*.mod"):
            if f'"{root.name}"' in cand.read_text(encoding="utf-8",
                                                  errors="replace"):
                outer = cand
                break
    if not outer.exists():
        warn("no sibling <name>.mod found next to "
             f"{rel}/ (the launcher needs it to locate the mod)")
    else:
        raw2 = outer.read_text(encoding="utf-8", errors="replace")
        if "path" not in raw2:
            err(f"{outer.name} has no path field")
        else:
            m = re.search(r'path\s*=\s*"([^"]*)"', raw2)
            if m and "\\" in m.group(1):
                err(f"{outer.name}: path uses backslashes - use forward "
                    f"slashes instead: {m.group(1)}")

    if (root / "localization").exists():
        err(f"{rel}/localization exists - Stellaris expects 'localisation' "
            f"(British spelling)")


def check_localisation(root: Path) -> set[str]:
    defined: dict[str, set[str]] = defaultdict(set)
    replace_keys: set[str] = set()
    loc_dir = root / "localisation"
    if not loc_dir.exists():
        warn(f"{root.name}/localisation does not exist")
        return set()

    unindented: dict[str, tuple[int, list[tuple[int, str]]]] = {}
    bad_chars: dict[tuple[str, str], int] = defaultdict(int)
    dup_keys: dict[str, list[tuple[str, int]]] = defaultdict(list)

    for yml in sorted(loc_dir.rglob("*.yml")):
        rel = yml.relative_to(root).as_posix()
        data = yml.read_bytes()
        text = data.decode("utf-8-sig", errors="replace")
        in_replace = "replace" in yml.relative_to(loc_dir).parts[:-1]

        if not data.startswith(b"\xef\xbb\xbf"):
            err(f"{rel}: missing UTF-8 BOM - Stellaris will not parse this file")

        first = text.split("\n", 1)[0].strip()
        m = re.match(r"^_?l_([a-z_]+)\s*:", first)
        if not m:
            err(f"{rel}: first line must be 'l_<language>:' "
                f"(found: {first[:40]!r})")
            lang = None
        else:
            lang = m.group(1).strip("_")
            if lang not in LANGS:
                warn(f"{rel}: unknown language code '{lang}'")

        fm = re.match(r"^(.*?)_l_([a-z_]+)\.yml$", yml.name)
        if not fm:
            err(f"{rel}: filename must end in '_l_<language>.yml'")
        elif lang and fm.group(2).strip("_") != lang:
            err(f"{rel}: filename language '{fm.group(2)}' does not match "
                f"header 'l_{lang}:'")

        bad_char_lines: list[tuple[int, str]] = []
        n_unindented = 0
        for lineno, line in enumerate(text.splitlines()[1:], start=2):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if not line[0].isspace():
                n_unindented += 1
                if n_unindented <= 2:
                    bad_char_lines.append((lineno, line[:70]))
                continue
            km = re.match(r'\s+([A-Za-z0-9_.\-]+)\s*:\s*\d*\s*"', line)
            if not km:
                if ":" in line:
                    km2 = re.match(r"\s*([A-Za-z0-9_.\-]+)\s*:\s*\d*\s*", line)
                    if not km2:
                        warn(f"{rel}:{lineno}: line does not look like "
                             f"`key: \"value\"`")
                continue
            key = km.group(1)
            if lang:
                if in_replace:
                    replace_keys.add(key)
                elif key not in replace_keys:
                    if key in defined[lang]:
                        dup_keys[rel].append((key, lineno))
                    defined[lang].add(key)
            for ch in line:
                if ch in ILLEGAL_LOC_CHARS:
                    bad_chars[(rel, ILLEGAL_LOC_CHARS[ch])] += 1

        if n_unindented:
            unindented[rel] = (n_unindented, bad_char_lines)

    for (rel, cp), count in sorted(bad_chars.items(),
                                   key=lambda kv: -kv[1]):
        warn(f"{rel}: {count} occurrence(s) of the illegal unicode character "
             f"{cp} - it renders as '?' in game; replace with an ASCII "
             f"equivalent")

    for rel, rows in dup_keys.items():
        sample = ", ".join(f"'{k}'(L{ln})" for k, ln in rows[:3])
        more = f" and {len(rows) - 3} more" if len(rows) > 3 else ""
        warn(f"{rel}: {len(rows)} duplicate localisation key(s) in the same "
             f"file: {sample}{more}")

    if unindented:
        total = sum(v[0] for v in unindented.values())
        warn(f"{total} localisation line(s) across {len(unindented)} file(s) "
             f"are not indented. The engine usually tolerates this, but the "
             f"documented format requires each entry to start with whitespace.")
        for rel, (n, samples) in list(unindented.items())[:3]:
            for lineno, txt in samples:
                warn(f"    {rel}:{lineno}: {txt.strip()[:60]}")
            if n > len(samples):
                warn(f"    {rel}: ... and {n - len(samples)} more")

    keys = set(defined.get("english", set()))
    keys |= defined.get("simp_chinese", set())
    return keys


def check_scripts(root: Path) -> dict:
    ns_decl: dict[Path, set[str]] = {}
    event_defs: dict[str, tuple[str, int]] = {}
    referenced_keys: dict[str, tuple[str, int]] = {}
    event_loc_checks: list[tuple[str, str, str, int]] = []
    duplicate_rows: int = 0

    for sub in TEXT_DIRS:
        d = root / sub
        if not d.exists():
            continue
        for txt in sorted(d.rglob("*.txt")):
            rel = txt.relative_to(root).as_posix()
            raw = txt.read_text(encoding="utf-8", errors="replace")
            nocmt = strip_comments(raw)
            bare = strip_strings(nocmt)
            depths = depth_map(bare)

            # ---- brace balance
            depth, last_open, bad = 0, 1, False
            for i, ch in enumerate(bare):
                if ch == "{":
                    if depth == 0:
                        last_open = line_of(bare, i)
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth < 0:
                        err(f"{rel}:{line_of(bare, i)}: unmatched closing brace")
                        bad = True
                        break
            if not bad and depth != 0:
                err(f"{rel}: {depth} unclosed brace(s); last block opened on "
                    f"line {last_open}")

            nss = set(re.findall(r"\bnamespace\s*=\s*([A-Za-z_]\w*)", nocmt))
            if nss:
                ns_decl[txt] = nss

            # ---- top-level event definitions only
            if sub == "events":
                for m in re.finditer(r"\b(\w*_event)\s*=\s*\{", nocmt):
                    if depths[m.start()] != 0:
                        continue  # nested call, not a definition
                    start = nocmt.index("{", m.end() - 1)
                    d2, end = 0, len(bare) - 1
                    for j in range(start, len(bare)):
                        if bare[j] == "{":
                            d2 += 1
                        elif bare[j] == "}":
                            d2 -= 1
                            if d2 == 0:
                                end = j
                                break
                    block = nocmt[start:end]
                    idm = re.search(r'\bid\s*=\s*"?([A-Za-z_]\w*\.\d+)"?', block)
                    if not idm:
                        continue
                    eid = idm.group(1)
                    lineno = line_of(nocmt, m.start())
                    if eid in event_defs:
                        duplicate_rows += 1
                        if duplicate_rows <= 15:
                            prev = event_defs[eid]
                            err(f"{rel}:{lineno}: duplicate event id '{eid}' "
                                f"(also defined in {prev[0]}:{prev[1]})")
                    else:
                        event_defs[eid] = (rel, lineno)
                    ns = eid.split(".")[0]
                    if nss and ns not in nss:
                        warn(f"{rel}:{lineno}: event id namespace '{ns}' is "
                             f"not declared in this file "
                             f"(declared: {', '.join(sorted(nss))})")

                    has_hidden = re.search(r"\bhide_window\s*=\s*yes", block)
                    for field in ("title", "desc"):
                        fm2 = re.search(
                            rf"(?<![\w.]){field}\s*=\s*"
                            r'"?([A-Za-z_][\w.\-]*)"?', block)
                        if fm2:
                            event_loc_checks.append(
                                (eid, field, fm2.group(1), lineno, rel))
                        elif not has_hidden:
                            warn(f"{rel}:{lineno}: event '{eid}' has no "
                                 f"'{field}' and no hide_window = yes")

            # ---- referenced loc keys
            for m in re.finditer(
                    r'\b(?:title|desc|custom_tooltip|response_text)\s*=\s*'
                    r'"?([A-Za-z_][\w.\-]*)', nocmt):
                referenced_keys.setdefault(m.group(1),
                                           (rel, line_of(nocmt, m.start())))
            for m in re.finditer(r'\bname\s*=\s*([A-Za-z_][\w.\-]*)', nocmt):
                if m.group(1) not in ("yes", "no"):
                    referenced_keys.setdefault(
                        m.group(1), (rel, line_of(nocmt, m.start())))

    if duplicate_rows > 15:
        info(f"... plus {duplicate_rows - 15} more duplicate event id(s)")

    return {
        "event_defs": event_defs,
        "referenced_keys": referenced_keys,
        "event_loc_checks": event_loc_checks,
    }


def check_gfx(root: Path) -> None:
    iface = root / "interface"
    if not iface.exists():
        return
    defined: set[str] = set()
    for gfx in iface.rglob("*.gfx"):
        defined |= set(re.findall(
            r'\bname\s*=\s*"?(GFX_[A-Za-z0-9_.\-]+)"?',
            strip_comments(gfx.read_text(encoding="utf-8", errors="replace"))))

    used: dict[str, str] = {}
    for sub in ("interface", "common", "events", "prescripted_countries"):
        d = root / sub
        if not d.exists():
            continue
        for f in d.rglob("*"):
            if f.suffix not in (".gui", ".gfx", ".txt"):
                continue
            raw = strip_comments(f.read_text(encoding="utf-8",
                                             errors="replace"))
            for m in re.finditer(r"GFX_[A-Za-z0-9_.\-]+", raw):
                used.setdefault(m.group(0), f.relative_to(root).as_posix())

    missing = {k: v for k, v in used.items() if k not in defined}
    if missing:
        info(f"{len(missing)} GFX_ sprite reference(s) are not registered in "
             f"interface/*.gfx (fine if they are vanilla sprites):")
        for k, v in list(missing.items())[:20]:
            info(f"    {k}  <- {v}")
        if len(missing) > 20:
            info(f"    ... and {len(missing) - 20} more")


def check_event_loc(data: dict, loc_keys: set[str]) -> None:
    if not loc_keys:
        return
    seen: set[str] = set()
    missing: list[tuple[str, str, str, int, str]] = []
    for eid, field, key, lineno, rel in data["event_loc_checks"]:
        if key in loc_keys:
            continue
        sig = f"{eid}:{field}"
        if sig in seen:
            continue
        seen.add(sig)
        missing.append((eid, field, key, lineno, rel))
    if missing:
        warn(f"{len(missing)} event title/desc key(s) are referenced but not "
             f"defined in this mod's localisation:")
        for eid, field, key, lineno, rel in missing[:20]:
            warn(f"    {rel}:{lineno}: event '{eid}' -> {field} = {key}")
        if len(missing) > 20:
            info(f"    ... and {len(missing) - 20} more")


def check_unused_refs(data: dict, loc_keys: set[str]) -> None:
    if not loc_keys:
        return
    unresolved: list[tuple[str, str, int]] = []
    for key, (rel, lineno) in data["referenced_keys"].items():
        if key in loc_keys or "." in key or key.startswith("GFX_"):
            continue
        unresolved.append((key, rel, lineno))
    if unresolved:
        info(f"{len(unresolved)} referenced loc key(s) are not defined in this "
             f"mod's localisation (likely vanilla keys):")
        for key, rel, lineno in unresolved[:20]:
            info(f"    {key}  <- {rel}:{lineno}")
        if len(unresolved) > 20:
            info(f"    ... and {len(unresolved) - 20} more")


# --------------------------------------------------------------------- main

def resolve_root(arg: str) -> Path:
    p = Path(arg).expanduser().resolve()
    if p.is_file():
        p = p.parent
    if (p / "descriptor.mod").exists():
        return p
    if p.is_dir():
        cands = [d for d in p.iterdir()
                 if d.is_dir() and (d / "descriptor.mod").exists()]
        if len(cands) == 1:
            return cands[0]
    return p


def emit(label: str, rows: list[str], limit: int) -> None:
    if not rows:
        return
    shown = rows if limit <= 0 else rows[:limit]
    for row in shown:
        print(f"{label}{row}")
    if limit > 0 and len(rows) > limit:
        print(f"{label}... and {len(rows) - limit} more {label.strip().lower()}(s)")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Lint a Stellaris mod folder.")
    ap.add_argument("path", help="Mod root (folder containing descriptor.mod)")
    ap.add_argument("--max", type=int, default=40,
                    help="Max lines printed per severity (0 = unlimited)")
    args = ap.parse_args()

    root = resolve_root(args.path)
    print(f"Validating: {root}\n")

    check_descriptor(root, root.name)
    loc_keys = check_localisation(root)
    data = check_scripts(root)
    check_event_loc(data, loc_keys)
    check_unused_refs(data, loc_keys)
    check_gfx(root)

    emit("ERROR   ", ERRORS, args.max)
    emit("WARN    ", WARNINGS, args.max)
    emit("INFO    ", INFOS, args.max)

    print(f"\n{len(ERRORS)} error(s), {len(WARNINGS)} warning(s), "
          f"{len(INFOS)} info.")
    if ERRORS:
        print("\nFix the ERRORs before launching the game.")
        sys.exit(1)


if __name__ == "__main__":
    main()
