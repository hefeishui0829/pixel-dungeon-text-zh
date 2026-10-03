#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""
自校验: 本项目给出的 (sheet, tile) 在贴图项目压缩后的图集上是否真的有像素。

为什么需要
    两边仓库是独立演进的, 最怕的就是"索引对上了、图却是空的"。
    这里直接打开 pixel-dungeon-mi-band/output/<preset>/<sheet>.png,
    按 sprites.json 给的坐标切出那一格, 统计不透明像素占比。
    全透明 => 说明映射错了(或者该 tile 本来就是空的, 已被剔除)。

用法
    python3 tools/verify_mapping.py                      # 校验全部条目(band 档)
    python3 tools/verify_mapping.py --preset band-lite    # 校验某一档
"""

import argparse
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def entries():
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "zh", "*.json"))):
        cat = os.path.basename(f)[:-5]
        if cat in ("all", "coverage"):
            continue
        for r in json.load(open(f, encoding="utf-8")):
            if r.get("sprite"):
                yield cat, r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--band", default=os.path.join(os.path.dirname(ROOT),
                                                   "pixel-dungeon-band"))
    ap.add_argument("--preset", default="band")
    args = ap.parse_args()

    out_dir = os.path.join(args.band, "output", args.preset)
    sprites = json.load(open(os.path.join(out_dir, "sprites.json"),
                             encoding="utf-8"))["sheets"]
    cache = {}

    def img_of(sheet):
        if sheet not in cache:
            info = sprites.get(sheet, {})
            path = os.path.join(out_dir, info.get("image") or "")
            cache[sheet] = (Image.open(path).convert("RGBA"), info) \
                if info.get("image") and os.path.exists(path) else (None, info)
        return cache[sheet]

    ok = bad = empty = 0
    problems = []
    for cat, r in entries():
        sp = r["sprite"]
        sheet, tile = sp["sheet"], sp["tile"]
        info = sprites.get(sheet)
        if not info or tile >= len(info["coords"]):
            problems.append((cat, r["id"], "图集或序号不存在"))
            bad += 1
            continue
        xy = info["coords"][tile]
        if xy is None:
            empty += 1
            continue
        im, _ = img_of(sheet)
        if im is None:
            problems.append((cat, r["id"], "找不到图集文件"))
            bad += 1
            continue
        tw, th = info["tileWidth"], info["tileHeight"]
        crop = im.crop((xy[0], xy[1], xy[0] + tw, xy[1] + th))
        a = np.asarray(crop)[..., 3]
        if (a > 0).mean() < 0.01:
            problems.append((cat, r["id"], "切出的格子几乎全透明"))
            bad += 1
        else:
            ok += 1

    print(f"档位 {args.preset}: 有像素 {ok}   空 tile(已剔除) {empty}   异常 {bad}")
    for p in problems[:20]:
        print("  !", p)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
