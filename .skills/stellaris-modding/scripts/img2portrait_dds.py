# -*- coding: utf-8 -*-
"""
把一张普通图片转换成 Stellaris MOD 领袖肖像贴图。

目标规格（与本 MOD 现有肖像完全一致）：
    496 x 380  DXT3  ARGB  with full mip chain (9 levels)

用法：
    python img2portrait_dds.py <输入图片> <输出.dds> [选项]

常用选项：
    --size 496x380     目标尺寸（默认 496x380）
    --anchor 0.12      垂直裁切锚点，0=顶部 1=底部。肖像一般取上半身，默认 0.12
    --no-mip           只写第 0 级 mip

依赖：Pillow（仅用于解码/缩放，DXT3 编码是本文件内纯 Python 实现）
"""
import argparse
import os
import struct
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("需要 Pillow：pip install Pillow")


# ---------------------------------------------------------------- 缩放 / 裁切
def cover_resize(img, tw, th, anchor=0.12):
    """等比放大填满目标框，再裁切（水平居中，垂直按 anchor 偏上）。"""
    sw, sh = img.size
    scale = max(tw / float(sw), th / float(sh))
    nw, nh = max(1, int(round(sw * scale))), max(1, int(round(sh * scale)))
    img = img.resize((nw, nh), Image.LANCZOS)

    left = (nw - tw) // 2
    top = int(round((nh - th) * anchor))
    top = max(0, min(nh - th, top))
    return img.crop((left, top, left + tw, top + th))


def make_mips(rgba, tw, th, with_mip=True):
    """生成 mip 链：[(w, h, bytes(RGBA)), ...]，尺寸降到 1x1 为止。"""
    levels = [(tw, th, rgba)]
    if not with_mip:
        return levels
    w, h, data = tw, th, rgba
    while w > 1 or h > 1:
        nw, nh = max(1, w // 2), max(1, h // 2)
        out = bytearray(nw * nh * 4)
        xr = w / float(nw)
        yr = h / float(nh)
        for y in range(nh):
            y0 = int(y * yr)
            y1 = max(y0 + 1, min(h, int((y + 1) * yr)))
            for x in range(nw):
                x0 = int(x * xr)
                x1 = max(x0 + 1, min(w, int((x + 1) * xr)))
                r = g = b = a = 0
                n = 0
                for yy in range(y0, y1):
                    base = (yy * w) * 4
                    for xx in range(x0, x1):
                        i = base + xx * 4
                        r += data[i]
                        g += data[i + 1]
                        b += data[i + 2]
                        a += data[i + 3]
                        n += 1
                o = (y * nw + x) * 4
                out[o] = r // n
                out[o + 1] = g // n
                out[o + 2] = b // n
                out[o + 3] = a // n
        levels.append((nw, nh, bytes(out)))
        w, h, data = nw, nh, bytes(out)
    return levels


# ---------------------------------------------------------------- DXT3 编码
def _rgb565(r, g, b):
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


def _from565(c):
    r = ((c >> 11) & 0x1F) << 3
    g = ((c >> 5) & 0x3F) << 2
    b = (c & 0x1F) << 3
    return (r | (r >> 5), g | (g >> 6), b | (b >> 5))


def encode_dxt3(w, h, data):
    """data: bytes, 每像素 4 字节 RGBA，长度 w*h*4。返回 DXT3 字节串。"""
    out = bytearray()
    bx = (w + 3) // 4
    by = (h + 3) // 4

    for byi in range(by):
        for bxi in range(bx):
            px = []
            for y in range(4):
                yy = byi * 4 + y
                for x in range(4):
                    xx = bxi * 4 + x
                    if xx < w and yy < h:
                        i = (yy * w + xx) * 4
                        px.append((data[i], data[i + 1], data[i + 2], data[i + 3]))
                    else:
                        px.append((0, 0, 0, 0))

            # --- alpha (8 bytes, 每字节两个像素, 低 nibble 在前)
            for k in range(8):
                a0 = px[k * 2][3] >> 4
                a1 = px[k * 2 + 1][3] >> 4
                out.append((a1 << 4) | a0)

            # --- color endpoints：RGB 包围盒
            rs = [p[0] for p in px]
            gs = [p[1] for p in px]
            bs = [p[2] for p in px]
            c0 = _rgb565(min(rs), min(gs), min(bs))
            c1 = _rgb565(max(rs), max(gs), max(bs))
            p0 = _from565(c0)
            p1 = _from565(c1)
            p2 = ((2 * p0[0] + p1[0]) // 3, (2 * p0[1] + p1[1]) // 3, (2 * p0[2] + p1[2]) // 3)
            p3 = ((p0[0] + 2 * p1[0]) // 3, (p0[1] + 2 * p1[1]) // 3, (p0[2] + 2 * p1[2]) // 3)
            pal = (p0, p1, p2, p3)

            out += struct.pack('<HH', c0, c1)

            # --- 2bit indices, 每字节 4 像素, LSB = 第一个像素
            for row in range(4):
                byte = 0
                for col in range(4):
                    r, g, b, _a = px[row * 4 + col]
                    best, bd = 0, None
                    for idx, pc in enumerate(pal):
                        d = (r - pc[0]) ** 2 + (g - pc[1]) ** 2 + (b - pc[2]) ** 2
                        if bd is None or d < bd:
                            bd, best = d, idx
                    byte |= best << (col * 2)
                out.append(byte)

    return bytes(out)


# ---------------------------------------------------------------- DDS 容器
def write_dds(path, levels):
    w, h, _ = levels[0]
    # DDS_HEADER
    flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x20000 | 0x80000  # CAPS|HEIGHT|WIDTH|PIXELFORMAT|MIPMAPCOUNT|LINEARSIZE
    fourcc = b'DXT3'
    header = bytearray()
    header += b'DDS '
    header += struct.pack('<I', 124)
    header += struct.pack('<I', flags)
    header += struct.pack('<II', h, w)
    # 主图 linear size：按 4x4 块 * 16 字节
    blocks = ((w + 3) // 4) * ((h + 3) // 4)
    header += struct.pack('<I', blocks * 16)
    header += struct.pack('<I', 0)          # depth
    header += struct.pack('<I', len(levels))  # mip count
    header += b'\x00' * 44                  # reserved / caps 之前
    # DDS_PIXELFORMAT (32 bytes)
    pf = bytearray()
    pf += struct.pack('<I', 32)
    pf += struct.pack('<I', 0x4)            # DDPF_FOURCC
    pf += fourcc
    pf += struct.pack('<I', 0)              # RGBBitCount
    pf += struct.pack('<I', 0) * 4          # masks
    header += pf
    # DDS_HEADER_CAPS
    header += struct.pack('<I', 0x1000 | 0x8 | 0x400000)  # TEXTURE | MIPMAP | COMPLEX
    header += struct.pack('<I', 0) * 4

    assert len(header) == 4 + 124, len(header)

    with open(path, 'wb') as fh:
        fh.write(header)
        for lw, lh, ldata in levels:
            fh.write(encode_dxt3(lw, lh, ldata))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--size', default='496x380')
    ap.add_argument('--anchor', type=float, default=0.12)
    ap.add_argument('--no-mip', action='store_true')
    a = ap.parse_args()

    tw, th = (int(v) for v in a.size.lower().split('x'))
    img = Image.open(a.src)
    img = img.convert('RGBA')
    img = cover_resize(img, tw, th, a.anchor)
    rgba = img.tobytes()
    levels = make_mips(rgba, tw, th, not a.no_mip)
    write_dds(a.dst, levels)
    print('OK  %s -> %s  %dx%d  DXT3  mips=%d  %d bytes' % (
        os.path.basename(a.src), a.dst, tw, th, len(levels), os.path.getsize(a.dst)))


if __name__ == '__main__':
    main()
