#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修补「贴图 <-> 文本」对应缺口 (一次性修复, 可重复运行验证)

基于对原项目 watabou/pixel-dungeon v1.9.1 源码的核查结果, 补齐以下缺口:

A. 贴图有 / 文本无: Yog.java 的三个内部类 (Larva / BurningFist / RottingFist)
   原项目有 name ("god's larva" / "burning fist" / "rotting fist") 且
   sprites.json 里有独立图集 (larva / burning_fist / rotting_fist),
   但此前只作为 Yog 的 altNames 存在, 没有独立条目 -> 建为独立条目。
   注: 三者的 description() 均 `return TXT_DESC`, 即共用主类 Yog 的描述,
   所以 desc 置空, 不重复堆三份相同文本。

B. 文本有 / 贴图无: FetidRat / CursePersonification
   它们的 Sprite 类无独立 texture(), 靠继承取父级贴图:
     FetidRatSprite            extends RatSprite    -> rat 图集
     CursePersonificationSprite extends WraithSprite -> wraith 图集
   在 sprite-index 里补上这两条 (标 inheritedFrom, 说明是继承而来)。

C. Yog 英文名错配: 提取脚本取了内部类 RottingFist 的 "rotting fist",
   主类真实 name 是 "Yog-Dzewa" (深层) / "echo of Yog-Dzewa" (浅层)。

D. 有贴图但缺英文原名: DM300 / Goo / Tengu 的 name 是三元表达式
   (`name = cond ? "A" : "B"`), 提取脚本没抓到 -> 取深层分支补上。
   TomeOfMastery 同理 -> "Tome of Mastery"。
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN_MOBS = os.path.join(ROOT, "data", "en", "mobs.json")
EN_ITEMS = os.path.join(ROOT, "data", "en", "items.json")
SPIDX = os.path.join(ROOT, "data", "sprite-index.json")
MAN_MOBS = os.path.join(ROOT, "data", "zh", "manual", "mobs.json")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save(p, d):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def main():
    changed = 0

    # ---------- C + D: 修 en/mobs.json 的 name ----------
    mobs = load(EN_MOBS)
    name_fix = {
        "Yog": "Yog-Dzewa",      # C: 原为内部类 RottingFist 的 "rotting fist"
        "DM300": "DM-300",       # D: 三元表达式, 取深层分支
        "Goo": "Goo",
        "Tengu": "Tengu",
    }
    for r in mobs:
        cls = r.get("class")
        if cls in name_fix and r.get("name") != name_fix[cls]:
            print("  [修 name] %-10s %r -> %r" % (cls, r.get("name"), name_fix[cls]))
            r["name"] = name_fix[cls]
            changed += 1

    # ---------- A: 新增三个 Yog 内部类条目 ----------
    new_mobs = [
        ("Larva", "god's larva", "LarvaSprite"),
        ("BurningFist", "burning fist", "BurningFistSprite"),
        ("RottingFist", "rotting fist", "RottingFistSprite"),
    ]
    have = {r.get("class") for r in mobs}
    for cls, name, sp in new_mobs:
        if cls in have:
            print("  [已存在] %s" % cls)
            continue
        mobs.append({
            "class": cls,
            "name": name,
            "desc": None,
            "spriteClass": sp,
            "note": "Yog.java 内部类; description() 返回主类 Yog 的 TXT_DESC, "
                    "故 desc 置空不重复",
        })
        print("  [新增条目] %-14s name=%-16r spriteClass=%s" % (cls, name, sp))
        changed += 1
    save(EN_MOBS, mobs)

    # ---------- B: sprite-index 补继承型 Sprite ----------
    idx = load(SPIDX)
    m = idx.setdefault("mobs", {})
    inherited = {
        "FetidRatSprite": ("RatSprite",
                           "FetidRatSprite extends RatSprite, 无独立 texture(), "
                           "贴图与 Rat 同源 (rat 图集, 颜色不同)"),
        "CursePersonificationSprite": ("WraithSprite",
                                       "CursePersonificationSprite extends "
                                       "WraithSprite, 无独立 texture(), "
                                       "贴图与 Wraith 同源 (wraith 图集)"),
    }
    for sp, (parent, note) in inherited.items():
        if sp in m:
            print("  [已存在 sprite] %s" % sp)
            continue
        p = m.get(parent)
        if not p:
            print("  [跳过] 父 Sprite 缺失: %s" % parent)
            continue
        m[sp] = {
            "sheet": p["sheet"],
            "tile": p["tile"],
            "gameFrame": p.get("gameFrame", p["tile"]),
            "gameGrid": p.get("gameGrid"),
            "gameCols": p.get("gameCols"),
            "frames": p.get("frames"),
            "inheritedFrom": parent,
            "note": note,
        }
        print("  [补贴图索引] %-28s -> %s tile=%s (继承 %s)"
              % (sp, p["sheet"], p["tile"], parent))
        changed += 1
    save(SPIDX, idx)

    # ---------- A: manual 补三条中文 ----------
    man = load(MAN_MOBS)
    zh_new = {
        "Larva": "神之幼虫",
        "BurningFist": "燃烧之拳",
        "RottingFist": "腐化之拳",
    }
    for k, zh in zh_new.items():
        if man.get(k):
            print("  [manual 已有] %s" % k)
            continue
        man[k] = {"zh": zh}
        print("  [manual 新增] %-14s zh=%s" % (k, zh))
        changed += 1
    save(MAN_MOBS, man)

    # ---------- D: TomeOfMastery 英文名 ----------
    items = load(EN_ITEMS)
    for r in items:
        if r.get("class") == "TomeOfMastery" and not r.get("name"):
            r["name"] = "Tome of Mastery"
            print("  [修 name] %-14s -> %r" % ("TomeOfMastery", r["name"]))
            changed += 1
    save(EN_ITEMS, items)

    print("\n共改动 %d 处" % changed)


if __name__ == "__main__":
    main()
