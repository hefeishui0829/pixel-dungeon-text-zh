#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""
收集「与中文分支(Shattered Pixel Dungeon 官方简体中文)存在分歧」的译文,
产出一份带注释的争议清单 data/zh/disputed.json, 供构建者按实际项目取舍。

为什么单独收集
    本项目译文取自 watabou/pixel-dungeon v1.9.1 源码, 与 SPD 官方简中
    在「是否重制命名 / 译名风格」上常有出入。这些出入不是"漏译", 而是
    "两套译法都合理, 但彼此不同"。把它们原样覆盖掉会丢失本项目视角,
    直接忽略又会让构建者不知道有别的译法可选。

    故: 凡是「本项目已译 ⇄ 官中存在差异」或「本项目未译但官中有权威译」
    的条目, 一律收进 disputed.json, 每条标上:
      - type:          分歧类型
      - ours:          本项目当前译文(可能为 null)
      - reference:     SPD 官方简中(参照系)
      - reason:        为什么会不一致
      - build_note:    "构建时请二选一" 的明确提示

输出
    data/zh/disputed.json            结构化争议清单(可被 build_zh.py 注入主数据)
    docs/disputed-translations.md    人读版汇总

用法
    python3 tools/collect_disputes.py [--spd /path/to/properties]
    (默认 SPD 目录 = /tmp/zhref/spd)
"""

import argparse
import difflib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OURS = os.path.join(ROOT, "data", "zh", "all.json")
DEFAULT_SPD = "/tmp/zhref/spd"

# 只比对「内容类」, 徽章/成就在 SPD 里被整体重制, 拿来比译名无意义
CONTENT_CATS = ("items", "mobs", "npcs", "plants", "hero", "buffs")
BASES = ["actors", "items", "journal", "levels", "misc",
         "plants", "scenes", "ui", "windows"]

REF_SOURCE = "Shattered Pixel Dungeon 官方简体中文 (00-Evan/shattered-pixel-dungeon@master)"
HAN = re.compile(r"[一-鿿]")


def parse(path):
    d, buf = {}, ""
    if not os.path.exists(path):
        return d
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.endswith("\\"):
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


def norm(s):
    """类名归一: 去标点/下划线, 转小写, 便于跨项目匹配"""
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def build_spd_index(spd_dir):
    name, desc = {}, {}
    for b in BASES:
        zh = parse(os.path.join(spd_dir, f"{b}_zh.properties"))
        for k, v in zh.items():
            parts = k.split(".")
            if len(parts) < 2:
                continue
            cls = parts[-2].replace("$", ".").split(".")[-1]
            nc = norm(cls)
            suf = parts[-1]
            if suf in ("name", "title") and is_zh(v):
                name.setdefault(nc, v)
            elif suf in ("desc", "info", "desc_long") and is_zh(v):
                desc.setdefault(nc, v)
    return name, desc


def make_entry(cat, rid, field, etype, ours, ref_value, reason):
    return {
        "id": rid,
        "category": cat,
        "field": field,
        "type": etype,
        "ours": ours,
        "reference": {"source": REF_SOURCE, "value": ref_value},
        "reason": reason,
        "build_note": (
            "构建时请二选一: 采用本项目译法 [%s] 或 采用 SPD 官方译法 [%s]。"
            "二者差异源于 SPD 重制命名 / 译名风格不同, 并非本项目漏译; "
            "最终以你的实际构建项目为准决定是否采用本条目。"
            % (ours if ours is not None else "（本项目未译）", ref_value)
        ),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spd", default=DEFAULT_SPD, help="SPD *.properties 目录")
    args = ap.parse_args()

    ours = json.load(open(OURS, encoding="utf-8"))
    spd_name, spd_desc = build_spd_index(args.spd)

    # 每个类别里 SPD 的归一类名集合(用于近邻改名检测)
    spd_by_cat = {}
    for b, cat in [("items", "items"), ("actors", "mobs"),
                   ("actors", "npcs"), ("actors", "hero"),
                   ("actors", "buffs"), ("plants", "plants")]:
        zh = parse(os.path.join(args.spd, f"{b}_zh.properties"))
        for k in zh:
            parts = k.split(".")
            if len(parts) < 2:
                continue
            cls = parts[-2].replace("$", ".").split(".")[-1]
            spd_by_cat.setdefault(cat, set()).add(norm(cls))

    entries = []
    for cat, rows in ours.items():
        if cat not in CONTENT_CATS:
            continue
        pool = spd_by_cat.get(cat, set())
        for r in rows:
            rid = r["id"]
            nc = norm(rid)
            rn = spd_name.get(nc)
            rd = spd_desc.get(nc)
            on = r.get("zh")
            od = r.get("zhDesc")

            if on and rn and on != rn:
                entries.append(make_entry(
                    cat, rid, "zh", "wording_mismatch", on, rn,
                    "本项目已译, 但与 SPD 官方简中措辞不同(重制命名/译名风格差异)"))
            elif (not on) and rn:
                entries.append(make_entry(
                    cat, rid, "zh", "untranslated_has_ref", None, rn,
                    "本项目该项未译, SPD 官方简中有权威译, 构建者可考虑直接采用"))

            if od and rd and od != rd:
                entries.append(make_entry(
                    cat, rid, "zhDesc", "wording_mismatch", od, rd,
                    "本项目已有说明译文, 但与 SPD 官方简中说明不一致"))

            # 近邻改名检测: 本项目 id 在 SPD 中无精确匹配, 但有极相似的类名
            if nc not in pool and on and rn is None:
                near = difflib.get_close_matches(nc, pool, n=1, cutoff=0.82)
                if near:
                    # 找该近邻对应的 SPD 名
                    cand = None
                    for b in BASES:
                        zh = parse(os.path.join(args.spd, f"{b}_zh.properties"))
                        for k, v in zh.items():
                            p = k.split(".")
                            if len(p) < 2:
                                continue
                            c = p[-2].replace("$", ".").split(".")[-1]
                            if norm(c) == near[0] and p[-1] in ("name", "title"):
                                cand = v
                                break
                        if cand:
                            break
                    if cand and cand != on:
                        entries.append(make_entry(
                            cat, rid, "zh", "possibly_renamed", on, cand,
                            "本项目 id 在 SPD 中无精确对应, 但存在极相似类名[%s], "
                            "疑似 SPD 改名; 下方 reference 为 SPD 侧的译法参考" % near[0]))

    meta = {
        "purpose": (
            "收录本项目译文与 Shattered Pixel Dungeon 官方简体中文存在分歧的条目。"
            "这些分歧通常不是漏译, 而是两套译法都合理但彼此不同(命名重制/译名风格)。"
            "构建者应按自己的实际项目决定采用哪一侧, 本文件仅作对照与提示。"),
        "how_to_use": (
            "1) 读取本文件的 entries 列表; 2) 对每个 type 做对应处理: "
            "wording_mismatch=二选一或融合; untranslated_has_ref=可直接采用 reference; "
            "possibly_renamed=核对 SPD 是否改了类名后决定; "
            "3) build_zh.py 已把这些条目以 `disputed` 字段注入 data/zh/*.json 与 all.json, "
            "下游构建可直接读取, 无需再次解析本文件。"),
        "reference_source": REF_SOURCE,
        "generated_by": "tools/collect_disputes.py",
        "count": len(entries),
    }
    out = {"_meta": meta, "entries": entries}
    odir = os.path.join(ROOT, "data", "zh")
    os.makedirs(odir, exist_ok=True)
    with open(os.path.join(odir, "disputed.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # 人读版
    doc = ["# 争议译文对照（本项目 ⇄ SPD 官方简体中文）", "",
           "> 本文件由 `tools/collect_disputes.py` 自动生成，列出本项目译文与 "
           "Shattered Pixel Dungeon 官方简体中文**存在分歧**的条目。", "",
           f"> 参照系：{REF_SOURCE}", "",
           "> **重要**：这些分歧通常不是漏译，而是两套译法都合理但彼此不同"
           "（命名重制 / 译名风格差异）。构建者应按实际项目决定采用哪一侧。", "",
           f"共收录 **{len(entries)}** 条争议。", "",
           "## 类型说明", "",
           "- `wording_mismatch`：本项目已译，但与 SPD 措辞不同，二选一或融合。",
           "- `untranslated_has_ref`：本项目未译，SPD 有权威译，可直接采用。",
           "- `possibly_renamed`：本项目 id 在 SPD 中无精确对应，疑似改名，请核对。",
           "", "## 条目", "",
           "| 类别 | id | 字段 | 类型 | 本项目 | SPD 官方 | 处理建议 |",
           "|---|---|---|---|---|---|---|"]
    for e in entries:
        ours_s = e["ours"] if e["ours"] is not None else "（未译）"
        doc.append("| %s | `%s` | %s | %s | %s | %s | %s |" % (
            e["category"], e["id"], e["field"], e["type"],
            ours_s, e["reference"]["value"], e["reason"]))
    with open(os.path.join(ROOT, "docs", "disputed-translations.md"),
              "w", encoding="utf-8") as f:
        f.write("\n".join(doc) + "\n")

    # 终端摘要(便于复跑核对)
    from collections import Counter
    c = Counter(e["type"] for e in entries)
    print("争议条目总数:", len(entries))
    for k, v in c.most_common():
        print("  %-22s %d" % (k, v))
    print("已写入 data/zh/disputed.json 与 docs/disputed-translations.md")


if __name__ == "__main__":
    main()
