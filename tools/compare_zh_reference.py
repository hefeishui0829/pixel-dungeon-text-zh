#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""
外部中文分支对照: 本项目 <-> Shattered Pixel Dungeon 官方简体中文。

为什么要做
    本项目的中文是从 Java 源码里抠字符串再人工译的, 没有第三方译文可对照。
    Shattered Pixel Dungeon (00-Evan/shattered-pixel-dungeon) 有完整的官方
    简体中文, 是中文社区里最权威的一套译名。拿它做交叉验证可以看两件事:
      1. 文本量级: 本项目覆盖的类别是否完整 (漏了哪一整块)
      2. 术语一致性: 同名条目的译名是否和社区主流说法对得上

    注意 SPD 是原版 PD 的重制续作, 内容量远大于 v1.9.1, 命中率低不代表缺漏,
    要看"未命中的是不是 SPD 里本来就没有的原版内容"。

准备语料
    for f in actors items journal levels misc plants scenes ui windows; do
      curl -sL "https://raw.githubusercontent.com/00-Evan/shattered-pixel-dungeon/\
master/core/src/main/assets/messages/$f/$f.properties"     -o ${f}_en.properties
      curl -sL "https://raw.githubusercontent.com/00-Evan/shattered-pixel-dungeon/\
master/core/src/main/assets/messages/$f/${f}_zh.properties" -o ${f}_zh.properties
    done

用法
    python3 tools/compare_zh_reference.py --spd /path/to/properties_dir
"""

import argparse
import difflib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OURS = os.path.join(ROOT, "data", "zh", "all.json")
BASES = ["actors", "items", "journal", "levels", "misc",
         "plants", "scenes", "ui", "windows"]

# 本项目类别 -> SPD 里去找同名的文件
CAT2SPD = {
    "hero": ["actors"], "items": ["items"], "mobs": ["actors"], "npcs": ["actors"],
    "buffs": ["actors"], "plants": ["plants"], "levels": ["levels"],
    "journal": ["journal"], "ui": ["ui", "scenes", "windows"],
    "misc": ["misc", "scenes", "windows"], "badges": ["misc", "journal"],
    "traps": ["levels"], "results": ["misc"],
}

HAN = re.compile(r"[一-鿿]")


def parse(path):
    d, buf = {}, ""
    if not os.path.exists(path):
        return d
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.endswith("\\"):          # properties 续行
                buf += line[:-1]
                continue
            buf += line
            if not buf.strip() or buf.lstrip().startswith("#"):
                buf = ""
                continue
            if "=" in buf:
                k, v = buf.split("=", 1)
                d[k.strip()] = v.strip()
            buf = ""
    return d


def is_zh(s):
    return bool(HAN.search(s or ""))


def cls_of(key):
    """items.armor.curses.antientropy.name → antientropy"""
    return key.split(".")[-2].replace("$", ".").split(".")[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spd", required=True, help="放 *_en/*_zh.properties 的目录")
    ap.add_argument("--sample", type=int, default=14, help="术语抽样条数")
    args = ap.parse_args()

    spd = {}
    print("=" * 78)
    print("A. Shattered Pixel Dungeon 官方简体中文 (参照系)")
    print("=" * 78)
    print(f"{'文件':<12}{'键数(en)':>9}{'键数(zh)':>9}{'中文率':>9}")
    tot_e = tot_z = 0
    for b in BASES:
        en = parse(os.path.join(args.spd, f"{b}_en.properties"))
        zh = parse(os.path.join(args.spd, f"{b}_zh.properties"))
        if not en:
            print(f"{b:<12}{'缺失':>9}")
            continue
        spd[b] = (en, zh)
        n = sum(1 for k in en if is_zh(zh.get(k, "")))
        tot_e += len(en)
        tot_z += n
        print(f"{b:<12}{len(en):>9}{len(zh):>9}{n / len(en) * 100:>8.1f}%")
    print(f"{'合计':<12}{tot_e:>9}{tot_z:>9}{tot_z / max(1, tot_e) * 100:>8.1f}%")

    ours = json.load(open(OURS, encoding="utf-8"))
    print()
    print("=" * 78)
    print("B. 本项目 (watabou/pixel-dungeon v1.9.1 全量文本)")
    print("=" * 78)
    print(f"{'类别':<10}{'类数':>6}{'已译串':>8}{'带贴图':>8}")
    tot_r = tot_s = tot_p = 0
    for cat, rows in ours.items():
        s = sum((1 if r.get("zh") else 0) + (1 if r.get("zhDesc") else 0)
                + len(r.get("zhConsts") or {}) for r in rows)
        p = sum(1 for r in rows if r.get("sprite"))
        tot_r += len(rows); tot_s += s; tot_p += p
        print(f"{cat:<10}{len(rows):>6}{s:>8}{p:>8}")
    print(f"{'合计':<10}{tot_r:>6}{tot_s:>8}{tot_p:>8}")

    print()
    print("=" * 78)
    print("C. 同名条目命中率 (未命中多为 SPD 已重制/删除的原版内容)")
    print("=" * 78)
    print(f"{'类别':<10}{'本类':>6}{'命中':>6}{'命中率':>8}   未命中示例")
    pool = {}
    for b in BASES:
        en, zh = spd.get(b, ({}, {}))
        for k in en:
            pool.setdefault(cls_of(k), []).append((k, zh.get(k, "")))
    hit_total = 0
    for cat, rows in ours.items():
        hit, miss = 0, []
        for r in rows:
            if r["id"].lower() in pool:
                hit += 1
            else:
                miss.append(r["id"])
        hit_total += hit
        print(f"{cat:<10}{len(rows):>6}{hit:>6}{hit / max(1, len(rows)) * 100:>7.0f}%   "
              + ",".join(miss[:4]))
    print(f"{'合计':<10}{tot_r:>6}{hit_total:>6}{hit_total / tot_r * 100:>7.0f}%")

    print()
    print("=" * 78)
    print("D. 术语一致性 (同名条目, 本项目译名 vs SPD 官中)")
    print("=" * 78)
    # 只统计"内容类"条目: 徽章/成就在 SPD 里已被整体重制, 拿来比译名没有意义
    CONTENT_CATS = ("items", "mobs", "npcs", "plants", "hero")
    by_id = {r["id"].lower(): r
             for cat, rows in ours.items() if cat in CONTENT_CATS
             for r in rows}
    print(f"{'条目':<14}{'本项目':<22}{'SPD 官中':<22}判定")
    shown = 0
    for cls in sorted(pool):
        if shown >= args.sample:
            break
        r = by_id.get(cls)
        if not r or not r.get("zh"):
            continue
        spdname = ""
        for k, zh in pool[cls]:
            if k.endswith(".name") or k.endswith(".title"):
                spdname = zh
                break
        if not spdname:
            continue
        a, b = r["zh"], spdname
        tag = ("一致" if a == b else
               "高度相似" if set(a) & set(b) and abs(len(a) - len(b)) <= 2
               else "措辞不同")
        print(f"{r['id']:<14}{a:<22}{b:<22}{tag}")
        shown += 1

    same = sim = total = 0
    for cls, entries in pool.items():
        r = by_id.get(cls)
        if not r or not r.get("zh"):
            continue
        for k, zh in entries:
            if (k.endswith(".name") or k.endswith(".title")) and zh:
                total += 1
                ratio = difflib.SequenceMatcher(None, r["zh"], zh).ratio()
                if ratio == 1:
                    same += 1
                elif ratio >= 0.5:
                    sim += 1
                break
    print()
    print(f"可比名称 {total} 条: 完全相同 {same} ({same / max(1, total) * 100:.0f}%), "
          f"相似度≥50% {sim} ({sim / max(1, total) * 100:.0f}%), "
          f"其余 {total - same - sim} ({'SPD 重制命名/译名风格差异'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
