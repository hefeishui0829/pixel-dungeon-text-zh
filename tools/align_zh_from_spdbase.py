#!/usr/bin/env python3
"""
把 manual/ 人工译文库尽量对齐到中文分支 (Shattered Pixel Dungeon 官方简体中文)。

做法:
- 解析 SPD 9 大类 *_zh.properties / *_en.properties -> key->(zh,en) 词典
- 遍历 data/zh/manual/*.json 每个 entry (以类名索引):
    * 若 entry 缺 zh / zh 非中文 -> 用 SPD `...<类名小写>.name` 补
    * 若 entry 缺 desc / desc 非中文 -> 用 SPD `...<类名小写>.desc` 补
- 对 all.json 里 need 但 manual 完全没有的条目 (如 buffs 状态效果), 在
  hero-plants-buffs.json 新增 entry
- 最后可选 --build 重跑 build_zh.py 重新生成 data/zh/*.json + docs

用法:
    python3 tools/align_zh_from_spdbase.py --dry-run
    python3 tools/align_zh_from_spdbase.py --write
    python3 tools/align_zh_from_spdbase.py --write --build
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPD_DIR = "/tmp/zhref/spd"
MANUAL_DIR = os.path.join(ROOT, "data/zh/manual")
CATS = ["actors", "items", "journal", "levels", "misc", "plants", "scenes", "ui", "windows"]
# 原版里属于 buffs 但 manual 漏建 entry 的类 (从 all.json 比对得出)
MISSING_BUFFS = ["Bleeding", "Charm", "Shadows", "SnipersMark", "Terror"]


def parse_props(path):
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            out[k.strip()] = v
    return out


def load_spd():
    spd = {}
    for c in CATS:
        zh = parse_props(f"{SPD_DIR}/{c}_zh.properties")
        en = parse_props(f"{SPD_DIR}/{c}_en.properties")
        for k in set(zh) | set(en):
            spd[k] = {"zh": zh.get(k, ""), "en": en.get(k, "")}
    return spd


def find(spd, keyword, suffix):
    low = keyword.lower()
    for k, v in spd.items():
        parts = k.split(".")
        if len(parts) >= 2 and parts[-1] == suffix and parts[-2] == low:
            return v.get("zh", "")
    return None


def is_cn(s):
    return bool(s) and any("\u4e00" <= ch <= "\u9fff" for ch in s)


def main():
    write = "--write" in sys.argv
    do_build = "--build" in sys.argv
    spd = load_spd()

    files = sorted(
        os.path.join(MANUAL_DIR, f)
        for f in os.listdir(MANUAL_DIR) if f.endswith(".json"))
    data = {f: json.load(open(f, encoding="utf-8")) for f in files}
    idx = {}
    for f, d in data.items():
        for k in d:
            idx[k] = f

    changes = []
    for f, d in data.items():
        for cls, entry in d.items():
            if not isinstance(entry, dict):
                continue
            # name
            zh = entry.get("zh")
            if not is_cn(zh):
                m = find(spd, cls, "name")
                if m and m != zh:
                    if write:
                        entry["zh"] = m
                    changes.append((cls, "zh", zh, m))
            # desc
            d0 = entry.get("desc")
            if not is_cn(d0):
                m = find(spd, cls, "desc")
                if m and m != d0:
                    if write:
                        entry["desc"] = m
                    changes.append((cls, "desc", d0, m))

    # 缺失的 buffs 新增到 hero-plants-buffs.json
    new_buff_file = os.path.join(MANUAL_DIR, "hero-plants-buffs.json")
    for cls in MISSING_BUFFS:
        if cls in idx:
            continue
        nm = find(spd, cls, "name")
        ds = find(spd, cls, "desc")
        if not (nm or ds):
            continue
        new_entry = {}
        if nm:
            new_entry["zh"] = nm
        if ds:
            new_entry["desc"] = ds
        if write:
            data[new_buff_file][cls] = new_entry
        changes.append((cls, "NEW", None, new_entry))

    print(f"{'DRY-RUN' if not write else 'WRITE'} 结果: 改动 {len(changes)} 处")
    for cls, kind, old, new in changes[:40]:
        print(f"  {kind:5s} {cls:16s}: {repr(old)} -> {repr(new)}")

    if write:
        for f, d in data.items():
            json.dump(d, open(f, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=2)
        print(f"\n已写回 {len(files)} 个 manual 文件")

    if write and do_build:
        print("\n重跑 build_zh.py ...")
        subprocess.run([sys.executable, os.path.join(HERE, "build_zh.py")],
                       check=True)
        print("build 完成")


if __name__ == "__main__":
    main()
