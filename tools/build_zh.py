#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""
把「英文原文(data/en)」+「手写中文翻译(data/zh/manual)」+「贴图索引(data/sprite-index.json)」
合并成最终数据 data/zh/*.json 与可读文档 docs/*.md, 并统计翻译覆盖率。

为什么分两步
    英文原文由脚本从源码确定性提取, 中文由人工(逐条)翻译。两者分开存放,
    重跑提取脚本不会覆盖译文; 合并步骤可以随时重跑, 也能给出"还剩多少没翻"的清单。

输出
    data/zh/<category>.json   结构化双语数据(含贴图坐标)
    data/zh/all.json          全量合并
    docs/<category>.md        Markdown 表格(中文为主, 附英文原文与贴图坐标)
    data/zh/coverage.json     覆盖率统计与缺失清单

用法
    python3 tools/build_zh.py
"""

import json
import os
import re
import glob
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN_DIR = os.path.join(ROOT, "data", "en")
MANUAL_DIR = os.path.join(ROOT, "data", "zh", "manual")
OUT_DIR = os.path.join(ROOT, "data", "zh")
DOC_DIR = os.path.join(ROOT, "docs")

# 类别 -> 中文标题 / 文档顺序
CAT_TITLES = OrderedDict([
    ("hero", "英雄职业与副职业"),
    ("items", "物品"),
    ("mobs", "怪物"),
    ("npcs", "NPC 与任务对话"),
    ("plants", "植物与种子"),
    ("buffs", "状态效果"),
    ("badges", "徽章"),
    ("levels", "楼层与地形"),
    ("traps", "陷阱与机关"),
    ("journal", "日志条目"),
    ("results", "结算与死因"),
    ("ui", "界面与剧情"),
    ("misc", "战斗日志与世界交互"),
])

# 存档字段名(全小写单词) / 文件名常量之类的"非玩家文本", 不参与统计与展示
FIELD_BLACKLIST = re.compile(
    r"^(?:[a-z][A-Za-z0-9]*|.*\.(?:dat|png|mp3))$")


def load_manual():
    zh = {}
    badges = {}
    for f in sorted(glob.glob(os.path.join(MANUAL_DIR, "*.json"))):
        data = json.load(open(f, encoding="utf-8"))
        if os.path.basename(f) == "badges.json":
            badges.update(data)
        else:
            zh.update(data)
    return zh, badges


def sprite_of(rec, idx):
    """根据记录推导贴图坐标: {sheet, tile}"""
    # 植物: 主图是 plants.png 上的本体, 种子(items.png)另存
    if rec["class"] in idx["plants"] and "tile" in idx["plants"][rec["class"]]:
        return {"sheet": "plants", "tile": idx["plants"][rec["class"]]["tile"]}

    img = rec.get("image", "")
    m = re.match(r"ItemSpriteSheet\.([A-Z_0-9]+)$", img)
    if m and m.group(1) in idx["items"]:
        return {"sheet": "items", "tile": idx["items"][m.group(1)]}

    sp = rec.get("spriteClass", "")
    if sp in idx["mobs"]:
        return {"sheet": idx["mobs"][sp]["sheet"], "tile": idx["mobs"][sp]["tile"]}

    cls = rec["class"]
    if cls in idx["plants"]:
        return {"sheet": "plants", "tile": idx["plants"][cls]["tile"]}
    return None


GROUPS = {
    "weapon/melee": "近战武器", "weapon/missiles": "投掷武器", "weapon": "武器/附魔",
    "armor/glyphs": "护甲印记", "armor": "护甲", "potions": "药水",
    "scrolls": "卷轴", "wands": "法杖", "rings": "戒指", "food": "食物",
    "quest": "任务物品", "bags": "容器", "keys": "钥匙", "weapon/enchantments": "武器附魔",
}


def group_of(rec):
    """从源码路径推断物品子类, 用于在文档里归类"""
    f = rec.get("file", "")
    m = re.search(r"/items/(.+?)/([^/]+)\.java$", f)
    if m:
        key = m.group(1)
        if key == "weapon":
            key = "weapon/melee" if "/melee/" in f else \
                  ("weapon/missiles" if "/missiles/" in f else "weapon")
        return GROUPS.get(key, key)
    return None


def build_items(rows, idx, zh):
    out = []
    for r in rows:
        t = zh.get(r["class"], {})
        sp = sprite_of(r, idx)
        rec = {
            "id": r["class"],
            "group": group_of(r),
            "zh": t.get("zh"),
            "en": r.get("name"),
            "zhDesc": t.get("desc"),
            "enDesc": r.get("desc"),
            "sprite": sp,
            "zhConsts": t.get("consts"),
            "enConsts": {k: v["text"] for k, v in r.get("consts", {}).items()} or None,
        }
        # 物品若同时能定位到种子/其它图集, 额外记录
        if r["class"] in idx["plants"] and "seedTile" in idx["plants"][r["class"]]:
            rec["seedSprite"] = {"sheet": "items",
                                 "tile": idx["plants"][r["class"]]["seedTile"]}
        elif sp and sp["sheet"] == "plants" and re.match(
                r"ItemSpriteSheet\.", r.get("image", "")):
            key = re.sub(r"^ItemSpriteSheet\.", "", r["image"])
            if key in idx["items"]:
                rec["seedSprite"] = {"sheet": "items", "tile": idx["items"][key]}
        out.append(rec)
    return out


def build_simple(rows, idx, zh):
    """怪物/NPC/植物/界面等: 结构与物品一致, 只是贴图来源不同"""
    return build_items(rows, idx, zh)


def build_badges(idx, badges_zh):
    out = []
    for name, info in sorted(idx["badges"].items(), key=lambda kv: kv[1]["tile"]):
        out.append({
            "id": name,
            "zh": badges_zh.get(name),
            "en": info["desc_en"],
            "sprite": {"sheet": "badges", "tile": info["tile"]},
            "meta": info["meta"],
        })
    return out


def count_translated(rec):
    n = 0
    if rec.get("zh"):
        n += 1
    if rec.get("zhDesc"):
        n += 1
    if rec.get("zhConsts"):
        n += len([k for k, v in rec["zhConsts"].items()
                  if v and not FIELD_BLACKLIST.match(str(k))])
    if rec.get("enum"):
        n += len(rec["enum"])
    if rec.get("arrays"):
        n += sum(len(v) for v in rec["arrays"].values())
    return n


def md_escape(s):
    if s is None:
        return ""
    return str(s).replace("|", "\\|").replace("\n", "<br>")


def sprite_cell(sp):
    if not sp:
        return "—"
    return "`%s` #%d" % (sp["sheet"], sp["tile"])


TABLE_CATS = {"items", "mobs", "npcs", "plants", "badges"}


def write_md(cat, rows, path):
    title = CAT_TITLES.get(cat, cat)
    head = ["# %s" % title, "",
            "> 中文为人工翻译; 英文原文来自 pixel-dungeon v1.9.1 源码。"
            "「贴图」列给出精灵表名与原始 tile 序号, 与贴图项目 sprites.json 的 "
            "`coords[tile]` 一一对应。", ""]

    if cat == "badges":
        body = ["| 贴图 | 中文 | 英文原文 |", "|---|---|---|"]
        for r in rows:
            body.append("| %s | %s | %s |" % (
                sprite_cell(r["sprite"]), md_escape(r.get("zh") or "（待补）"),
                md_escape(r.get("en"))))
        open(path, "w", encoding="utf-8").write("\n".join(head + body + [""]))
        return

    if cat in TABLE_CATS:
        body = ["| 中文名 | 中文说明 | 英文原名 | 英文说明 | 贴图 |",
                "|---|---|---|---|---|"]
        for r in rows:
            if not (r.get("zh") or r.get("zhDesc") or r.get("zhConsts")):
                continue
            zh_desc = r.get("zhDesc") or ""
            if r.get("zhConsts"):
                extra = "<br>".join(
                    "`%s` %s" % (k, md_escape(v))
                    for k, v in r["zhConsts"].items()
                    if v and not FIELD_BLACKLIST.match(str(k)))
                zh_desc = (zh_desc + "<br>" + extra).strip("<br>") if zh_desc else extra
            name = r.get("zh") or (r.get("group") and "（%s）" % r["group"]) or "—"
            extra_sprite = ""
            if r.get("seedSprite"):
                extra_sprite = "<br>种子 " + sprite_cell(r["seedSprite"])
            body.append("| %s | %s | %s | %s | %s%s |" % (
                md_escape(name), md_escape(zh_desc) or "—",
                md_escape(r.get("en")) or "—", md_escape(r.get("enDesc")) or "—",
                sprite_cell(r.get("sprite")), extra_sprite))
        open(path, "w", encoding="utf-8").write("\n".join(head + body + [""]))
        return

    # 其余类别(界面/职业/剧情/结算等)按类分节, 常量逐条列出
    body = []
    for r in rows:
        blocks = []
        if r.get("zh") or r.get("en"):
            blocks.append("- **名称**：%s%s" % (
                md_escape(r.get("zh")) or "（待补）",
                "（%s）" % md_escape(r["en"]) if r.get("en") else ""))
        if r.get("zhDesc") or r.get("enDesc"):
            blocks.append("- **说明**：%s" % (
                md_escape(r.get("zhDesc")) or "（待补）"))
            if r.get("enDesc"):
                blocks.append("  - 原文：%s" % md_escape(r["enDesc"]))
        if r.get("enum"):
            for key, val in r["enum"].items():
                z = val.get("zh")
                zs = " / ".join(x for x in (z or []) if x)
                blocks.append("- `%s`：%s" % (key, md_escape(zs) or "（待补）"))
                blocks.append("  - 原文：%s" % md_escape(" / ".join(val["en"])))
        if r.get("arrays"):
            for key, val in r["arrays"].items():
                blocks.append("- **%s**" % key)
                for i, en in enumerate(val["en"]):
                    zl = val.get("zh") or []
                    blocks.append("  - %s%s" % (
                        md_escape(zl[i]) if i < len(zl) and zl[i] else "（待补）",
                        "（%s）" % md_escape(en) if en else ""))
        if r.get("zhConsts"):
            for k, v in r["zhConsts"].items():
                if not v or FIELD_BLACKLIST.match(str(k)):
                    continue
                blocks.append("- `%s` %s" % (k, md_escape(v)))
        if r.get("extra"):
            for k, v in r["extra"].items():
                if re.match(r"^lit\d+$", str(k)):   # 只是源码里的片段, 已在常量中收录
                    continue
                blocks.append("- `%s` %s" % (k, md_escape(v)))
        if not blocks:
            continue
        body.append("## %s" % r["id"])
        body.append("")
        body += blocks
        body.append("")
    open(path, "w", encoding="utf-8").write("\n".join(head + body + [""]))


def write_md_extras(path, en_rows, zh, cat):
    """额外文本(consts 之外的内联/枚举/数组)单独成节"""
    pass


def main():
    idx = json.load(open(os.path.join(ROOT, "data", "sprite-index.json"),
                         encoding="utf-8"))
    zh, badges_zh = load_manual()
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(DOC_DIR, exist_ok=True)

    coverage = {}
    all_rows = OrderedDict()

    for cat, title in CAT_TITLES.items():
        en_path = os.path.join(EN_DIR, cat + ".json")
        if not os.path.exists(en_path):
            continue
        en_rows = json.load(open(en_path, encoding="utf-8"))
        if cat == "badges":
            rows = build_badges(idx, badges_zh)
        else:
            rows = build_simple(en_rows, idx, zh)
            # 枚举/数组/内联文本(职业特长、副职业、剧情章节等)
            for r in en_rows:
                t = zh.get(r["class"], {})
                for row in rows:
                    if row["id"] != r["class"]:
                        continue
                    if r.get("enumEntries") and t.get("enum"):
                        row["enum"] = OrderedDict()
                        for key, info in r["enumEntries"].items():
                            got = t["enum"].get(key)
                            row["enum"][key] = {
                                "en": info["args"],
                                "zh": [got] if isinstance(got, str) else
                                      ([got.get("title"), got.get("desc")]
                                       if isinstance(got, dict) else None),
                            }
                    if r.get("arrays") and t.get("arrays"):
                        row["arrays"] = {
                            k: {"en": v, "zh": t["arrays"].get(k)}
                            for k, v in r["arrays"].items()}
                    if t.get("extra"):
                        row["extra"] = t["extra"]
                    break

        with open(os.path.join(OUT_DIR, cat + ".json"), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        write_md(cat, rows, os.path.join(DOC_DIR, cat + ".md"))

        n_tr = sum(count_translated(r) for r in rows)
        coverage[cat] = {"rows": len(rows), "translatedStrings": n_tr}
        all_rows[cat] = rows

    with open(os.path.join(OUT_DIR, "all.json"), "w", encoding="utf-8") as f:
        json.dump(all_rows, f, ensure_ascii=False, indent=1)

    total = sum(v["translatedStrings"] for v in coverage.values())
    coverage["__total__"] = {"translatedStrings": total}
    with open(os.path.join(OUT_DIR, "coverage.json"), "w", encoding="utf-8") as f:
        json.dump(coverage, f, ensure_ascii=False, indent=1)

    for cat, v in coverage.items():
        if cat == "__total__":
            continue
        print(f"{cat:<10} 条目 {v['rows']:>4}   已译文本 {v['translatedStrings']:>5}")
    print("合计已译文本:", total)


if __name__ == "__main__":
    main()
