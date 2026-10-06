# -*- coding: utf-8 -*-
"""校验 MOD 的「区划 (district) / 区域槽 (zone_slot) / 区域 (zone)」接线是否正确。

用法：
    python verify_district_zones.py "<MOD 内容根目录>" [--game "<Stellaris 安装目录>"]

    <MOD 内容根目录> = 含有 common/ 的那一层，一般形如
        …/mod/<MOD 名>/            （创意工坊副本则是 …/workshop/content/281990/<id>/）
    --game 省略时自动在常见 Steam 路径里找。

为什么需要这个脚本：
    「星球能进，但区划列表是空的、区域造不了」这类问题**不会在 error.log 里报错**——
    `uses_district_set = S` 在 S 不存在时静默为假，`is_planet_class` 拼错时也静默为假。
    只能靠静态比对发现。典型触发场景见 SKILL.md「常见陷阱」。

检查项（全部 PASS 才算通过）：
  1. common/districts、common/zone_slots、common/zones 下每个文件花括号配平
  2. 每个 `is_planet_class = pc_X` 的 pc_X 都真的被定义过（MOD 或原版）
  3. 每个 `uses_district_set = S` 的 S 都是某个星球类实际在用的集合
     （从 原版 common/planet_classes + MOD common/planet_classes 一起收集）
  4. 区划里引用的每个 `slot_*` 都有定义（MOD 的 common/zone_slots 或原版同名）
  5. 每个 `has_origin = origin_X` 都存在
  6. 【核心】对每个区划：它引用的每个区域槽，在该区划所属星球类上确实会 unlock
     —— 这一条就是「这地方到底能不能盖东西」的直接判据
"""
import os
import re
import sys
import argparse

sys.stdout.reconfigure(encoding="utf-8")

STEAM_GUESSES = [
    r"C:\Program Files (x86)\Steam\steamapps\common\Stellaris",
    r"C:\Program Files\Steam\steamapps\common\Stellaris",
    r"D:\Steam\steamapps\common\Stellaris",
    r"E:\Steam\steamapps\common\Stellaris",
    os.path.expanduser("~/.steam/steam/steamapps/common/Stellaris"),
    os.path.expanduser("~/Library/Application Support/Steam/steamapps/common/Stellaris"),
]


def read(p):
    return open(p, encoding="utf-8", errors="replace").read()


def top_blocks(text):
    """Yield (name, body) for every top-level `name = { ... }` block."""
    out = []
    for m in re.finditer(r"^([a-zA-Z_0-9]+)\s*=\s*\{", text, re.M):
        i = text.find("{", m.start())
        depth, j = 0, i
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append((m.group(1), text[i + 1:j]))
    return out


def braces_ok(text):
    depth = 0
    for ch in text:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def find_game_root(explicit):
    if explicit:
        return explicit
    for c in STEAM_GUESSES:
        if os.path.isdir(os.path.join(c, "common")):
            return c
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mod_root", help="含 common/ 的 MOD 内容根目录")
    ap.add_argument("--game", default=None, help="Stellaris 安装目录（含 common/）")
    a = ap.parse_args()

    MOD = os.path.abspath(a.mod_root)
    GAME = find_game_root(a.game)
    if not os.path.isdir(os.path.join(MOD, "common")):
        print("ERROR: %s 下没有 common/，请传 MOD 内容根目录" % MOD)
        return 2
    mod_dirs = os.path.join(MOD, "common")
    game_dirs = os.path.join(GAME, "common") if GAME else None
    if game_dirs:
        print("game root : %s" % GAME)
    else:
        print("WARN: 未找到游戏安装目录，原版 planet_classes / zone_slots 将不参与校验")
    print("mod root  : %s" % MOD)

    ok = True

    def chk(cond, label, extra=""):
        nonlocal ok
        ok = ok and bool(cond)
        print("%s  %s %s" % ("PASS" if cond else "FAIL", label, extra))

    def list_txt(d):
        if not d or not os.path.isdir(d):
            return []
        return [f for f in os.listdir(d) if f.endswith(".txt")]

    # ---------- collect definitions ----------
    planet_classes = {}          # class name -> district_set
    for root in filter(None, (game_dirs, mod_dirs)):
        d = os.path.join(root, "planet_classes")
        for f in list_txt(d):
            for name, body in top_blocks(read(os.path.join(d, f))):
                m = re.search(r"district_set\s*=\s*([a-zA-Z_0-9]+)", body)
                if m:
                    planet_classes[name] = m.group(1)
    used_sets = set(planet_classes.values())

    zone_slots = {}
    for f in list_txt(os.path.join(mod_dirs, "zone_slots")):
        for name, body in top_blocks(read(os.path.join(mod_dirs, "zone_slots", f))):
            zone_slots[name] = body

    vanilla_slots = set()
    for f in list_txt(os.path.join(game_dirs, "zone_slots") if game_dirs else None):
        for name, _ in top_blocks(read(os.path.join(game_dirs, "zone_slots", f))):
            vanilla_slots.add(name)

    origins = set()
    for sub in ("governments/civics", "governments"):
        for f in list_txt(os.path.join(mod_dirs, sub)):
            origins |= set(re.findall(r"^(origin_[a-zA-Z_0-9]+)\s*=\s*\{",
                                      read(os.path.join(mod_dirs, sub, f)), re.M))

    print("planet classes found: %d | district sets in use: %s" %
          (len(planet_classes), sorted(used_sets)))
    print("zone slots defined by mod: %s" % sorted(zone_slots))
    print()

    # ---------- 1. braces ----------
    for sub in ("districts", "zone_slots", "zones"):
        d = os.path.join(mod_dirs, sub)
        bad = [f for f in list_txt(d) if not braces_ok(read(os.path.join(d, f)))]
        chk(not bad, "braces balanced in common/%s" % sub, bad[:8])

    # ---------- 2..6 per district ----------
    districts = {}
    for f in list_txt(os.path.join(mod_dirs, "districts")):
        for name, body in top_blocks(read(os.path.join(mod_dirs, "districts", f))):
            districts[name] = body

    bad_class, bad_set, bad_slot, bad_origin, unlock_gap = [], [], [], [], []
    for name, body in districts.items():
        cls = re.findall(r"is_planet_class\s*=\s*([a-zA-Z_0-9]+)", body)
        sts = re.findall(r"uses_district_set\s*=\s*([a-zA-Z_0-9]+)", body)
        sls = re.findall(r"^\s+(slot_[a-zA-Z_0-9]+)", body, re.M)
        ors = re.findall(r"has_origin\s*=\s*([a-zA-Z_0-9]+)", body)

        for c in cls:
            if c not in planet_classes:
                bad_class.append("%s -> %s" % (name, c))
        for s in sts:
            if s not in used_sets:
                bad_set.append("%s -> %s" % (name, s))
        for s in sls:
            if s not in zone_slots and s not in vanilla_slots:
                bad_slot.append("%s -> %s" % (name, s))
        for o in ors:
            if o not in origins:
                bad_origin.append("%s -> %s" % (name, o))

        # 6. 该区划的每个槽位，在它自己的星球类上会不会 unlock？
        for c in cls:
            pset = planet_classes.get(c)
            for s in sls:
                body_slot = zone_slots.get(s)
                if body_slot is None:
                    continue                      # 原版槽位：交给游戏处理
                un = re.search(r"unlock\s*=\s*\{", body_slot)
                unblock = body_slot[un.start():] if un else ""
                hop = re.findall(r"is_planet_class\s*=\s*([a-zA-Z_0-9]+)", unblock)
                hset = re.findall(r"uses_district_set\s*=\s*([a-zA-Z_0-9]+)", unblock)
                if c in hop or (pset and pset in hset):
                    continue
                unlock_gap.append("%s (%s) slot %s not unlocked" % (name, c, s))

    chk(not bad_class, "every is_planet_class names a known planet class", bad_class[:8])
    chk(not bad_set, "every uses_district_set is a set some planet actually has", bad_set[:8])
    chk(not bad_slot, "every district slot_* is defined", bad_slot[:8])
    chk(not bad_origin, "every has_origin target exists", bad_origin[:8])
    chk(not unlock_gap, "every district's zone slots unlock on its planet class", unlock_gap[:8])

    # ---------- 附：district 里写了 zone 专属的键会解析报错 ----------
    zone_only = []
    for f in list_txt(os.path.join(mod_dirs, "districts")):
        txt = read(os.path.join(mod_dirs, "districts", f))
        for m in re.finditer(r"is_capped_by_modifier", txt):
            ln = txt[:m.start()].count("\n") + 1
            zone_only.append("%s:%d" % (f, ln))
    chk(not zone_only,
        "no zone-only key (is_capped_by_modifier) inside common/districts",
        zone_only[:8])

    print()
    print("district count: %d | mod zone slots: %d" % (len(districts), len(zone_slots)))
    print("RESULT:", "ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
