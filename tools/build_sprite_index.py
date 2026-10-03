#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""
建立「游戏对象 -> 贴图坐标」索引, 让文本项目与贴图项目 pixel-dungeon-mi-band 对齐。

三张映射表
    items    物品类 -> items.png    的 tile 索引 (来自 ItemSpriteSheet 常量)
    mobs     怪物类 -> 各自精灵表   (来自 *Sprite 里的 texture(Assets.XXX) + idle 首帧)
    badges   徽章   -> badges.png   的 tile 索引 (来自 Badges.Badge 枚举构造参数)
    plants   植物   -> plants.png / items.png(种子)

索引的语义
    tile 指的是 **游戏内网格中的帧序号**(行主序, 从 0 开始)。

    贴图项目 pixel-dungeon-mi-band 现已按每张精灵表在游戏内的真实网格切图
    (见其 tools/sprite_grid.json; 82 张里只有 8 张是 16x16), 输出的 sprites.json 里
    coords[i] 的 i 同样按该网格的帧序号排列 (空 tile 记为 null,
    内容相同的 tile 指向同一坐标), 所以 `coords[tile]` 就是压缩后图集上这一格的
    左上角坐标 —— 两边天然对齐, 无需换算。

    历史: 贴图项目早期统一按 16x16 切, 本索引曾用"换算成 16x16 等效序号"来打补丁;
    贴图项目修正网格后该换算已移除, 否则会二次错位。

用法
    python3 tools/build_sprite_index.py --src <pd源码src> --out data/sprite-index.json
"""

import argparse
import json
import os
import re

INT_CONST = re.compile(
    r"public\s+static\s+final\s+int\s+([A-Z_][A-Z0-9_]*)\s*=\s*(-?\d+)\s*;")
STR_CONST = re.compile(
    r"public\s+static\s+final\s+String\s+([A-Z_][A-Z0-9_]*)\s*=\s*\"([^\"]+)\"\s*;")


def read(path):
    return open(path, encoding="utf-8", errors="ignore").read()


def parse_simple_map(src, pattern, cast=str):
    out = {}
    for m in pattern.finditer(src):
        out[m.group(1)] = cast(m.group(2))
    return out


def build_items(src_dir):
    """物品 -> items.png tile 索引"""
    p = os.path.join(src_dir, "com/watabou/pixeldungeon/sprites/ItemSpriteSheet.java")
    return parse_simple_map(read(p), INT_CONST, int)


def build_assets(src_dir):
    """Assets 常量 -> 图集文件名"""
    p = os.path.join(src_dir, "com/watabou/pixeldungeon/Assets.java")
    return parse_simple_map(read(p), STR_CONST)


def build_mobs(src_dir, assets, sizes):
    """怪物/NPC 类 -> {sheet, tile} (sheet 名即贴图项目的图集名, tile = idle 动画首帧)

    重要 (2024 修正)
    --------------
    游戏内并非所有精灵表都用 16x16 网格: rat.png 是 TextureFilm(16, 15)、
    scorpio.png 是 (18, 17)、piranha.png 是 (12, 16) 等, 82 张里只有 8 张是标准 16x16。

    早期贴图项目统一按 16x16 切图, 这会让所有非标准网格的图集在游戏里整体错位
    (例如 piranha 每帧累积偏移 4px)。本索引当时用"换算成 16x16 等效序号"来打补丁。

    贴图项目修正后已改为按游戏内真实网格切 (见 tools/sprite_grid.json),
    因此这里不再换算 —— tile 直接就是游戏内帧序号, 与 sprites.json 的
    coords[frame] 一一对应, 无需任何转换。
    """
    sp_dir = os.path.join(src_dir, "com/watabou/pixeldungeon/sprites")
    out = {}
    for fn in sorted(os.listdir(sp_dir)):
        if not fn.endswith("Sprite.java"):
            continue
        cls = fn[:-5]
        src = read(os.path.join(sp_dir, fn))
        m = re.search(r"texture\(\s*Assets\.([A-Z_][A-Z0-9_]*)\s*\)", src)
        if not m:
            continue
        sheet = assets.get(m.group(1), "").replace(".png", "")
        if not sheet:
            continue
        # TextureFilm( texture, w, h ) —— 记录网格尺寸, 便于核对
        tf = re.search(r"new\s+TextureFilm\(\s*texture\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", src)
        gw, gh = (int(tf.group(1)), int(tf.group(2))) if tf else (16, 16)
        # idle 动画首帧
        idle = re.search(r"idle\.frames\(\s*frames\s*,\s*(\d+)", src)
        first = int(idle.group(1)) if idle else 0

        src_w = sizes.get(sheet, [None])[0]
        game_cols = (src_w // gw) if src_w else 16

        out[cls] = {
            "sheet": sheet,
            "tile": first,          # 游戏内网格序号, 与贴图项目 coords 直接对应
            "gameFrame": first,
            "gameGrid": [gw, gh],
            "gameCols": game_cols,
        }
        # 记录全部动画帧, 方便手环端直接做逐帧动画
        frames = {}
        for anim in ("idle", "run", "attack", "die", "zap", "operate"):
            am = re.search(anim + r"\.frames\(\s*frames\s*,\s*([\d,\s]+)\)", src)
            if am:
                frames[anim] = [int(x) for x in re.findall(r"\d+", am.group(1))]
        if frames:
            out[cls]["frames"] = frames
    return out


def build_badges(src_dir):
    """徽章 -> {desc_en, image}  image 即 badges.png 的 tile 索引"""
    p = os.path.join(src_dir, "com/watabou/pixeldungeon/Badges.java")
    src = read(p)
    body = src[src.index("public static enum Badge"):]
    body = body[: body.index("private Badge()")]
    out = {}
    for m in re.finditer(
            r"^\s*([A-Z][A-Z0-9_]*)\s*\(\s*\"([^\"]*)\"\s*,\s*(-?\d+)(?:\s*,\s*(true|false))?\s*\)",
            body, re.M):
        out[m.group(1)] = {
            "desc_en": m.group(2),
            "tile": int(m.group(3)),
            "meta": m.group(4) == "true",
        }
    return out


def build_plants(src_dir):
    """植物 -> plants.png tile (本体) 与 items.png tile (种子)"""
    p_dir = os.path.join(src_dir, "com/watabou/pixeldungeon/plants")
    out = {}
    items = build_items(src_dir)
    for fn in sorted(os.listdir(p_dir)):
        if not fn.endswith(".java") or fn == "Plant.java":
            continue
        cls = fn[:-5]
        src = read(os.path.join(p_dir, fn))
        im = re.search(r"^\s*image\s*=\s*(\d+)\s*;", src, re.M)
        seed = re.search(r"image\s*=\s*ItemSpriteSheet\.([A-Z_][A-Z0-9_]*)", src)
        rec = {}
        if im:
            rec["tile"] = int(im.group(1))
        if seed and seed.group(1) in items:
            rec["seedTile"] = items[seed.group(1)]
        if rec:
            out[cls] = rec
    return out


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(root, ".pd-src", "src"))
    ap.add_argument("--out", default=os.path.join(root, "data", "sprite-index.json"))
    ap.add_argument("--sprites",
                    default=os.path.join(os.path.dirname(root),
                                         "pixel-dungeon-band", "output", "band",
                                         "sprites.json"),
                    help="贴图项目的 sprites.json, 用于读取各图集原始尺寸")
    args = ap.parse_args()

    assets = build_assets(args.src)
    sizes = {}
    if os.path.exists(args.sprites):
        sp = json.load(open(args.sprites, encoding="utf-8"))
        sizes = {k: v.get("sourceSize", [None]) for k, v in sp["sheets"].items()}
    index = {
        "note": "tile = 原始素材 16x16 网格中的序号(行主序)。"
                "与 pixel-dungeon-mi-band 的 sprites.json -> sheets[sheet].coords[tile] 一一对应。"
                "gameFrame 是游戏源码里的动画帧序号, gameGrid 是源码使用的网格尺寸; "
                "两者不一致时(如 rat 的 16x15)已做换算, offsetPx 记录换算后的像素偏差。",
        "items": build_items(args.src),
        "mobs": build_mobs(args.src, assets, sizes),
        "badges": build_badges(args.src),
        "plants": build_plants(args.src),
        "assets": assets,
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    print("物品索引", len(index["items"]), " 怪物索引", len(index["mobs"]),
          " 徽章", len(index["badges"]), " 植物", len(index["plants"]))
    print("->", args.out)


if __name__ == "__main__":
    main()
