# -*- coding: utf-8 -*-
"""
Stellaris 国家旗帜（flags/）贴图工具。

flag 贴图必须是**真正的 DDS**：把 PNG 改个名成 .dds 是不行的。
本 MOD 实测已知可用的规格（照抄 flags/DOT_SR/DOT_SR_04.dds）：
    未压缩 32bpp BGRA，头部 dwFlags=659463 / dwCaps=4198408，
    pixelformat R=0x00FF0000 G=0x0000FF00 B=0x000000FF A=0xFF000000，
    完整 mip 链（256x256 -> 9 级；24x24 -> 5 级），一路降到 1x1。
尺寸（与原版 / 本 MOD 一致）：
    <分类>/<名>.dds       256x256   （原版也有 128x128 的写法，两者都能用）
    <分类>/map/<名>.dds   256x256   ← 银河地图用，缺了会报 empire_flag.cpp:924
    <分类>/small/<名>.dds  24x24    ← 注意是 24，不是 28

三种用法
--------
1) 用一张图生成一整套（顶层 + map + small）
     python png2flag_dds.py make <源图> <flags/分类目录> <名字>
   例：python png2flag_dds.py make teyvat.png ".../flags/DOT_SR" DOT_SR_09

2) 体检：列出某目录下「不是真 DDS」的文件
     python png2flag_dds.py check <flags 目录 或 分类目录>

3) 批量修复：把「PNG 伪装成 .dds」的旗标重写成真 DDS，
   并补齐缺失的 map/ 与 small/ 副本（原件先备份到 --backup 指定目录）
     python png2flag_dds.py repair <flags 目录> --backup <备份目录>

依赖：Pillow（仅用于解码/缩放，DDS 容器是本文件内手写的）
"""
import argparse
import os
import shutil
import struct
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("需要 Pillow：pip install Pillow")

SIZE_TOP = (256, 256)
SIZE_MAP = (256, 256)
SIZE_SMALL = (24, 24)


# ------------------------------------------------------------------ DDS 写出
def build_dds(im, path):
    """把 PIL 图像写成未压缩 BGRA8 DDS（含完整 mip 链），返回 (mip 级数, 字节数)。"""
    im = im.convert("RGBA")
    w, h = im.size
    levels = [im]
    cw, ch, cur = w, h, im
    while cw > 1 or ch > 1:
        cw, ch = max(1, cw // 2), max(1, ch // 2)
        cur = cur.resize((cw, ch), Image.LANCZOS)
        levels.append(cur)

    hdr = bytearray(128)
    struct.pack_into("<4s", hdr, 0, b"DDS ")
    struct.pack_into("<I", hdr, 4, 124)           # dwSize
    struct.pack_into("<I", hdr, 8, 659463)        # dwFlags
    struct.pack_into("<I", hdr, 12, h)            # dwHeight
    struct.pack_into("<I", hdr, 16, w)            # dwWidth
    struct.pack_into("<I", hdr, 20, w * 4)        # dwPitchOrLinearSize
    struct.pack_into("<I", hdr, 24, 0)            # dwDepth
    struct.pack_into("<I", hdr, 28, len(levels))  # dwMipMapCount
    struct.pack_into("<I", hdr, 76, 32)           # pf.dwSize
    struct.pack_into("<I", hdr, 80, 65)           # pf.dwFlags = ALPHAPIXELS|RGB
    struct.pack_into("<I", hdr, 84, 0)            # pf.dwFourCC (0 = 未压缩)
    struct.pack_into("<I", hdr, 88, 32)           # pf.dwRGBBitCount
    struct.pack_into("<I", hdr, 92, 0x00FF0000)   # R
    struct.pack_into("<I", hdr, 96, 0x0000FF00)   # G
    struct.pack_into("<I", hdr, 100, 0x000000FF)  # B
    struct.pack_into("<I", hdr, 104, 0xFF000000)  # A
    struct.pack_into("<I", hdr, 108, 4198408)     # dwCaps

    buf = bytearray(hdr)
    for lv in levels:
        raw = lv.tobytes()          # RGBA
        bgra = bytearray(raw)
        bgra[0::4] = raw[2::4]      # 写成 BGRA
        bgra[2::4] = raw[0::4]
        buf += bgra

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "wb") as f:
        f.write(bytes(buf))
    return len(levels), len(buf)


def is_real_dds(path):
    try:
        with open(path, "rb") as f:
            return f.read(4) == b"DDS "
    except OSError:
        return False


def is_png(path):
    try:
        with open(path, "rb") as f:
            return f.read(8) == b"\x89PNG\r\n\x1a\n"
    except OSError:
        return False


# ------------------------------------------------------------------ 子命令
def cmd_make(a):
    im = Image.open(a.src)
    base = os.path.join(a.category, a.name + ".dds")
    jobs = [(base, SIZE_TOP)]
    if not a.no_map:
        jobs.append((os.path.join(a.category, "map", a.name + ".dds"), SIZE_MAP))
    if not a.no_small:
        jobs.append((os.path.join(a.category, "small", a.name + ".dds"), SIZE_SMALL))
    for path, size in jobs:
        src = im if im.size == size else im.resize(size, Image.LANCZOS)
        mips, nbytes = build_dds(src, path)
        print("  %-52s %s  mip=%d  %d B" % (os.path.relpath(path, a.category), size, mips, nbytes))


def cmd_check(a):
    bad, missing = [], []
    root = a.path
    cats = [root] if os.path.isdir(os.path.join(root, "map")) else \
           [os.path.join(root, d) for d in sorted(os.listdir(root)) if os.path.isdir(os.path.join(root, d))]
    for cat in cats:
        if not os.path.isdir(cat):
            continue
        names = sorted(n for n in os.listdir(cat)
                       if n.lower().endswith(".dds") and os.path.isfile(os.path.join(cat, n)))
        for n in names:
            p = os.path.join(cat, n)
            if not is_real_dds(p):
                bad.append(p)
            for sub in ("map", "small"):
                sp = os.path.join(cat, sub, n)
                if not os.path.isfile(sp):
                    missing.append(sp)
                elif not is_real_dds(sp):
                    bad.append(sp)
        for f in sorted(os.listdir(cat)):
            if f.lower().endswith(".png"):
                bad.append(os.path.join(cat, f))
    print("不是真 DDS 的文件（%d）：" % len(bad))
    for p in bad:
        print("   %s" % p)
    print("缺失的 map/ 或 small/ 副本（%d）：" % len(missing))
    for p in missing:
        print("   %s" % p)
    return 1 if (bad or missing) else 0


def cmd_repair(a):
    root = a.path
    cats = [root] if os.path.isdir(os.path.join(root, "map")) else \
           [os.path.join(root, d) for d in sorted(os.listdir(root)) if os.path.isdir(os.path.join(root, d))]
    backup = a.backup

    def bak(p):
        if not backup:
            return
        rel = os.path.relpath(p, root)
        dst = os.path.join(backup, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst):
            shutil.copy2(p, dst)

    for cat in cats:
        if not os.path.isdir(cat):
            continue
        # 1) 顶层：PNG -> 真 DDS
        origin = {}
        for n in sorted(os.listdir(cat)):
            p = os.path.join(cat, n)
            if not (os.path.isfile(p) and n.lower().endswith(".dds")):
                continue
            if is_real_dds(p):
                continue
            bak(p)
            origin[n] = p
            im = Image.open(p)
            if im.size != SIZE_TOP:
                im = im.resize(SIZE_TOP, Image.LANCZOS)
            mips, nb = build_dds(im, p)
            print("  顶层重写 %-24s -> %s mip=%d %dB" % (n, SIZE_TOP, mips, nb))
        # 2) map/ 与 small/
        for sub, size in (("map", SIZE_MAP), ("small", SIZE_SMALL)):
            subdir = os.path.join(cat, sub)
            os.makedirs(subdir, exist_ok=True)
            for n in sorted(os.listdir(cat)):
                top = os.path.join(cat, n)
                if not (os.path.isfile(top) and n.lower().endswith(".dds")):
                    continue
                dst = os.path.join(subdir, n)
                if os.path.isfile(dst) and is_real_dds(dst):
                    continue
                if os.path.isfile(dst):
                    bak(dst)
                    src = dst
                    act = "重写"
                else:
                    src = origin.get(n, top)
                    act = "新建"
                im = Image.open(src)
                if im.size != size:
                    im = im.resize(size, Image.LANCZOS)
                mips, nb = build_dds(im, dst)
                print("  %s/%s %-20s -> %s mip=%d %dB" % (sub, act, n, size, mips, nb))
        # 3) 分类目录里残留的 .png：移出 flags/
        for n in sorted(os.listdir(cat)):
            if n.lower().endswith(".png"):
                p = os.path.join(cat, n)
                print("  ! %s 是 .png，会被 empire_flag.cpp:588 拒绝；请移出 flags/" % p)
    print("完成。原文件备份于：%s" % backup if backup else "完成（未备份）")


def main():
    ap = argparse.ArgumentParser(description="Stellaris 旗帜 DDS 工具")
    sub = ap.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("make", help="用一张图生成 顶层+map+small 三件套")
    m.add_argument("src")
    m.add_argument("category", help="flags/ 下的分类目录，例如 .../flags/DOT_SR")
    m.add_argument("name", help="不含扩展名的旗标名，例如 DOT_SR_09")
    m.add_argument("--no-map", action="store_true")
    m.add_argument("--no-small", action="store_true")
    m.set_defaults(func=cmd_make)

    c = sub.add_parser("check", help="体检：列出非真 DDS 的文件与缺失的副本")
    c.add_argument("path")
    c.set_defaults(func=cmd_check)

    r = sub.add_parser("repair", help="批量把 PNG 伪装成 .dds 的旗标修好并补齐副本")
    r.add_argument("path", help="flags/ 目录，或单个分类目录")
    r.add_argument("--backup", default="", help="原文件备份目录")
    r.set_defaults(func=cmd_repair)

    a = ap.parse_args()
    sys.exit(a.func(a) or 0)


if __name__ == "__main__":
    main()
