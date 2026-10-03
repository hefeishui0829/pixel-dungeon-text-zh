#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""
把本项目的「文本条目」查成贴图项目 pixel-dungeon-mi-band 里的实际图集坐标。

两边的约定
    本项目的 data/zh/*.json 里, sprite.tile 是 **原始素材 16x16 网格里的序号**(行主序)。
    贴图项目的 sprites.json 里, sheets[sheet].coords 是一个数组,
    coords[i] 与原始序号 i 一一对应(全透明的格子为 null, 内容相同的格子指向同一坐标)。
    所以查表就是 coords[tile] —— 不需要任何换算, 这也是本项目刻意沿用原始序号的原因。

用法
    # 按条目 id 查(默认查三档)
    python3 tools/lookup_sprite.py --band ../pixel-dungeon-band --id Amulet
    python3 tools/lookup_sprite.py --band ../pixel-dungeon-band --id Rat --preset band

    # 直接按图集+序号查
    python3 tools/lookup_sprite.py --band ../pixel-dungeon-band --sheet items --tile 87

    # 导出全部条目的坐标表(供快应用直接内联)
    python3 tools/lookup_sprite.py --band ../pixel-dungeon-band --all -o sprite-map.json
"""

import argparse
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRESETS = ["band-lite", "band", "band-pro"]


def load_band(band_root):
    """读入贴图项目各档 sprites.json"""
    out = {}
    for p in PRESETS:
        f = os.path.join(band_root, "output", p, "sprites.json")
        if os.path.exists(f):
            out[p] = json.load(open(f, encoding="utf-8"))["sheets"]
    if not out:
        raise SystemExit("没找到贴图项目的 sprites.json, 请用 --band 指向 "
                         "pixel-dungeon-mi-band 仓库根目录")
    return out


def lookup(sheets_by_preset, sheet, tile):
    res = {"sheet": sheet, "tile": tile, "presets": {}}
    for preset, sheets in sheets_by_preset.items():
        s = sheets.get(sheet)
        if not s:
            res["presets"][preset] = None
            continue
        coords = s.get("coords") or []
        if tile >= len(coords):
            res["presets"][preset] = None
            continue
        xy = coords[tile]
        res["presets"][preset] = {
            "image": s.get("image"),
            "x": xy[0] if xy else None,
            "y": xy[1] if xy else None,
            "tileWidth": s.get("tileWidth"),
            "tileHeight": s.get("tileHeight"),
            "note": None if xy else "该 tile 全透明, 已在压缩时剔除",
        }
    return res


def iter_entries():
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
                                                   "pixel-dungeon-band"),
                    help="pixel-dungeon-mi-band 仓库路径")
    ap.add_argument("--id", help="条目 id(类名), 如 Amulet / Rat / Dreamweed")
    ap.add_argument("--sheet", help="图集名, 配合 --tile 使用")
    ap.add_argument("--tile", type=int, help="原始 tile 序号")
    ap.add_argument("--preset", help="只看某一档: band-lite / band / band-pro")
    ap.add_argument("--all", action="store_true", help="导出全部条目")
    ap.add_argument("-o", "--out", help="--all 时的输出文件")
    args = ap.parse_args()

    band = load_band(args.band)
    if args.preset:
        band = {args.preset: band[args.preset]} if args.preset in band else band

    if args.all:
        rows = {}
        for cat, r in iter_entries():
            sp = r["sprite"]
            rows[r["id"]] = lookup(band, sp["sheet"], sp["tile"])
            rows[r["id"]]["zh"] = r.get("zh")
        text = json.dumps(rows, ensure_ascii=False, indent=1)
        if args.out:
            open(args.out, "w", encoding="utf-8").write(text)
            print("已写出", args.out, len(rows), "条")
        else:
            print(text)
        return

    if args.sheet is not None and args.tile is not None:
        print(json.dumps(lookup(band, args.sheet, args.tile),
                         ensure_ascii=False, indent=1))
        return

    if args.id:
        for cat, r in iter_entries():
            if r["id"] == args.id:
                sp = r["sprite"]
                res = lookup(band, sp["sheet"], sp["tile"])
                res["zh"] = r.get("zh")
                res["category"] = cat
                print(json.dumps(res, ensure_ascii=False, indent=1))
                return
        raise SystemExit("没找到 id=" + args.id)

    ap.print_help()


if __name__ == "__main__":
    main()
