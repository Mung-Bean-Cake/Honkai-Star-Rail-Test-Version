#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gen_portrait_archive.py — 从一个贴图目录批量生成「编号制」肖像档案（portrait_group）。

适用场景
    你有一批角色立绘 dds（500x380 规格），想做成和原版/大 MOD 里
    `Herta_Space_Station` / `Belobog` 那样的「肖像档案」：
      * 与同物种档案（species_class）同级，只是 portrait_group 不同
      * 肖像 key 用编号（genshin_001…），不强行和角色名对应
    典型输入：`gfx/models/portraits/DOT_GI/genshin_001.dds`

产出（全部 UTF-8 无 BOM + CRLF，符合 Clausewitz MOD 约定）
    1. gfx/portraits/portraits/<Out>.txt
         portraits = { <prefix>_001 = { texturefile = "<texdir>/<prefix>_001.dds" } … }
         portrait_groups = { "<Group>" = { default … game_setup/species/pop_group/leader/ruler } }
    2. common/portrait_sets/<Out>_sets.txt
         <Group> = { species_class = <SpeciesClass> portraits = { <Group> } }
    3. 可选：把编号肖像的本地化键写进 localisation/<lang>/<Out>_l_<lang>.yml

必须做的一步（本脚本不做，手动）：
    把 <Group> 追加进 common/portrait_categories/ 里对应分类的 sets 列表，
    否则档案不会出现在帝国设计器。

用法
    python gen_portrait_archive.py <mod_root> \
        --tex-dir gfx/models/portraits/DOT_GI \
        --prefix genshin --group Genshin --species-class Star_Rail \
        --out DOTGI_genshin \
        --cats common/portrait_categories/SR_portrait_categories.txt \
        --cat-entry Star_Rail \
        --loc localisation/simp_chinese/DOTGI_teyvat_l_simp_chinese.yml "原神立绘" \
              localisation/english/DOTGI_teyvat_l_english.yml "Genshin Portrait"

    追加 --dry-run 只打印统计，不写文件。

约定
    * 贴图文件名须为 <prefix>_<三位数字>.dds（脚本按数字排序，缺号自动跳过）
    * 每个 portrait_group 的五个作用域（game_setup/species/pop_group/leader/ruler）
      都列全部肖像 —— 只列部分会导致该场景下选不到别的肖像
    * 肖像 key 必须同时出现在 portraits 块与至少一个 portrait_group 里，
      否则 create_species(portrait=…) / change_leader_portrait 会静默失败
"""

from __future__ import annotations

import argparse
import os
import re
import sys

HEADER = """\
# ============================================================
#  自动生成，勿手改 —— 由 gen_portrait_archive.py 生成
#  贴图目录：{texdir}
#  肖像组：{group}（species_class = {spc}）
#  规格应为 496x380 / DXT3 / 9 级 mip / 252256 字节
#  增删图片后重跑脚本即可。
# ============================================================
"""


def read_text(path: str) -> str:
    return open(path, "rb").read().decode("utf-8-sig")


def write_crlf(path: str, text: str, bom: bool = False) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    nl = text.replace("\r\n", "\n").replace("\n", "\r\n")
    data = (b"\xef\xbb\xbf" if bom else b"") + nl.encode("utf-8")
    open(path, "wb").write(data)


def scan_textures(tex_dir: str, prefix: str) -> list[str]:
    """按 <prefix>_<数字>.dds 扫描，返回排序后的肖像 key 列表。"""
    pat = re.compile(re.escape(prefix) + r"_(\d+)\.dds$", re.I)
    found: list[tuple[int, str]] = []
    for name in os.listdir(tex_dir):
        m = pat.search(name)
        if m:
            found.append((int(m.group(1)), name))
    if not found:
        raise SystemExit(f"[!] {tex_dir} 下没有 {prefix}_<数字>.dds")
    found.sort()
    keys = [f"{prefix}_{n:03d}" for n, _ in found]
    nums = [n for n, _ in found]
    missing = [n for n in range(1, max(nums) + 1) if n not in nums]
    print(f"[i] 贴图 {len(keys)} 张，序号 {min(nums)}–{max(nums)}，缺号 {missing or '无'}")
    return keys


def build_portrait_file(texdir: str, group: str, spc: str, keys: list[str]) -> str:
    L = ["", HEADER.format(texdir=texdir, group=group, spc=spc).rstrip(), "", "portraits = {"]
    for k in keys:
        L.append(f'\t{k} = {{ texturefile = "{texdir}/{k}.dds" }}')
    L += ["}", "", "portrait_groups = {", "", f'\t"{group}" = {{', f"\t\tdefault = {keys[0]}"]
    for scope in ("game_setup", "species", "pop_group", "leader", "ruler"):
        L += [f"\t\t{scope} = {{", "\t\t\tadd = {", "\t\t\t\tportraits = {"]
        L += [f"\t\t\t\t\t{k}" for k in keys]
        L += ["\t\t\t\t}", "\t\t\t}", "\t\t}"]
    L += ["\t}", "}", ""]
    return "\n".join(L)


def build_set_file(group: str, spc: str) -> str:
    return "\n".join([
        "",
        "# ============================================================",
        "#  肖像集：把肖像档案挂到所属物种档案（species_class）下",
        "#  4.4.x 中 species_classes 已不支持 portraits 键，必须在此指派。",
        "# ============================================================",
        "",
        f"{group} = {{",
        f"\tspecies_class = {spc}",
        "\tportraits = {",
        f"\t\t{group}",
        "\t}",
        "}",
        "",
    ])


def patch_category(path: str, cat: str, group: str) -> bool:
    """把 group 追加进 portrait_categories 里 cat 分类的 sets 列表。"""
    if not os.path.exists(path):
        return False
    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    t = raw.decode("utf-8-sig")
    m = re.search(r"(?m)^\s*%s\s*=\s*\{" % re.escape(cat), t)
    if not m:
        print(f"[!] {os.path.basename(path)} 里找不到分类 {cat}")
        return False
    i = t.index("{", m.start())
    d, j = 0, i
    while j < len(t):
        if t[j] == "{":
            d += 1
        elif t[j] == "}":
            d -= 1
            if d == 0:
                break
        j += 1
    block = t[i:j]
    if re.search(r"(?m)^\s*%s\s*$" % re.escape(group), block):
        print(f"[=] {cat} 里已有 {group}")
        return False
    sets = re.search(r"(?m)^(\s*)sets\s*=\s*\{", block)
    if not sets:
        # 分类不是用 sets 键（少见），直接在末尾插入
        new_block = block.rstrip()[:-1].rstrip() + f"\n\t\t{group}\n\t}}"
    else:
        k = block.index("{", sets.start())
        d2, q = 0, k
        while q < len(block):
            if block[q] == "{":
                d2 += 1
            elif block[q] == "}":
                d2 -= 1
                if d2 == 0:
                    break
            q += 1
        inner = block[k + 1:q]
        new_inner = inner.rstrip() + f"\n\t\t{group}\n\t"
        new_block = block[:k + 1] + new_inner + block[q:]
    write_crlf(path, t[:i] + new_block + t[j:], bom=bom)
    print(f"[+] {os.path.basename(path)}: {cat} += {group}")
    return True


def patch_localisation(path: str, prefix: str, label: str, keys: list[str]) -> None:
    """写入/替换编号肖像的本地化键（保留 BOM + CRLF）。"""
    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    lines = raw.decode("utf-8-sig").replace("\r\n", "\n").split("\n")
    pat = re.compile(r"^\s*%s_\d+:0\s" % re.escape(prefix))
    idx = [i for i, l in enumerate(lines) if pat.match(l)]
    new = [f' {k}:0 "{label} {k.rsplit("_", 1)[1]}"' for k in keys]
    if idx:
        start = idx[0]
        if start and lines[start - 1].strip().startswith("# ----------"):
            start -= 1
        new = [f' # ---------- {label}（编号制，由 gen_portrait_archive.py 生成） ----------'] + new
        lines[start:idx[-1] + 1] = new
    else:
        lines += [""] + new
    write_crlf(path, "\n".join(lines), bom=bom)
    print(f"[+] {os.path.basename(path)}: {len(keys)} 个 {prefix}_NNN 键")


def main() -> None:
    ap = argparse.ArgumentParser(description="批量生成编号制肖像档案")
    ap.add_argument("mod_root")
    ap.add_argument("--tex-dir", required=True, help="相对 MOD 根目录的贴图目录")
    ap.add_argument("--prefix", required=True, help="贴图/肖像 key 前缀，如 genshin")
    ap.add_argument("--group", required=True, help="肖像组名（显示在帝国设计器里），如 Genshin")
    ap.add_argument("--species-class", required=True, help="所属物种档案，如 Star_Rail")
    ap.add_argument("--out", required=True, help="输出基名，如 DOTGI_genshin")
    ap.add_argument("--cats", help="要追加的 portrait_categories 文件（相对路径）")
    ap.add_argument("--cat-entry", help="分类名（sets 列表所在的那一项）")
    ap.add_argument("--loc", nargs=2, action="append", default=[],
                    metavar=("YML", "LABEL"), help="本地化文件 + 显示名前缀，可重复")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    mod = os.path.abspath(a.mod_root)
    tex_abs = os.path.join(mod, a.tex_dir)
    if not os.path.isdir(tex_abs):
        sys.exit(f"[!] 贴图目录不存在：{tex_abs}")

    keys = scan_textures(tex_abs, a.prefix)
    if a.dry_run:
        print(f"[dry-run] 将生成 {len(keys)} 个肖像 key：{keys[0]} … {keys[-1]}")
        return

    write_crlf(os.path.join(mod, "gfx/portraits/portraits", a.out + ".txt"),
               build_portrait_file(a.tex_dir, a.group, a.species_class, keys))
    print(f"[+] gfx/portraits/portraits/{a.out}.txt")

    write_crlf(os.path.join(mod, "common/portrait_sets", a.out + "_sets.txt"),
               build_set_file(a.group, a.species_class))
    print(f"[+] common/portrait_sets/{a.out}_sets.txt")

    if a.cats and a.cat_entry:
        patch_category(os.path.join(mod, a.cats), a.cat_entry, a.group)

    for yml, label in a.loc:
        patch_localisation(os.path.join(mod, yml), a.prefix, label, keys)

    # 一致性自检
    bad = [k for k in keys if not os.path.exists(os.path.join(tex_abs, k + ".dds"))]
    print(f"[✓] 完成：{len(keys)} 张，贴图缺失 {bad or '无'}")
    if not (a.cats and a.cat_entry):
        print(f"[!] 记得把 {a.group} 追加进 portrait_categories 的 sets，"
              f"否则档案不会出现在帝国设计器（可用 --cats/--cat-entry 自动完成）")


if __name__ == "__main__":
    main()
