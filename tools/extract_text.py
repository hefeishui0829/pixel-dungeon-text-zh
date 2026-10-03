#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""
Pixel Dungeon (v1.9.1, GPL-3.0) 源码 -> 结构化游戏文本 JSON (英文原文)
================================================================================

为什么需要这个脚本
    pixel-dungeon 的文本不是放在 res/values/strings.xml 里, 而是硬编码在 505 个
    Java 类的字符串常量与方法中(name = "..." / description() / info() / TXT_XXX)。
    手工摘录不可靠也不可复现, 所以这里做一次确定性的静态提取, 任何人重跑都能得到
    同一份数据。

提取什么
    1. name = "..."                     物品/怪物/植物名(实例初始化块内)
    2. description() / info() / desc()  玩家可见的说明文本(方法内 return 拼接串)
    3. static final String TXT_XXX      提示/日志/对话/UI 文本
    4. image = ItemSpriteSheet.XXX      贴图索引(用于和贴图项目对齐)

不提取什么
    注释、import、日志 tag、文件名常量、纯数字/颜色/路径字面量 —— 这些不是游戏文本。

拼接串的处理
    Java 里长文本写成 "a" + "b" 的多行拼接; 遇到标识符(如 TXT_FOO)则保留为
    {TXT_FOO} 占位, 便于人工核对组成关系, 不擅自内联。

用法
    python3 tools/extract_text.py --src <pd源码目录> --out data/en
"""

import argparse
import json
import os
import re
from collections import OrderedDict

# --------------------------------------------------------------------------- #
# 1. 词法: 去掉注释(不误伤字符串里的 // 与 http://)
# --------------------------------------------------------------------------- #

def strip_comments(src: str) -> str:
    out = []
    i, n = 0, len(src)
    state = None  # None / 'str' / 'chr' / 'line' / 'block'
    while i < n:
        c = src[i]
        nxt = src[i + 1] if i + 1 < n else ""
        if state is None:
            if c == '"':
                state = 'str'; out.append(c)
            elif c == "'":
                state = 'chr'; out.append(c)
            elif c == "/" and nxt == "/":
                state = 'line'; i += 2; continue
            elif c == "/" and nxt == "*":
                state = 'block'; i += 2; continue
            else:
                out.append(c)
        elif state == 'str':
            out.append(c)
            if c == "\\":
                if i + 1 < n:
                    out.append(src[i + 1]); i += 2; continue
            elif c == '"':
                state = None
        elif state == 'chr':
            out.append(c)
            if c == "\\":
                if i + 1 < n:
                    out.append(src[i + 1]); i += 2; continue
            elif c == "'":
                state = None
        elif state == 'line':
            if c == "\n":
                state = None; out.append(c)
        elif state == 'block':
            if c == "*" and nxt == "/":
                state = None; i += 2; continue
        i += 1
    return "".join(out)


# --------------------------------------------------------------------------- #
# 2. 字符串拼接表达式解析
# --------------------------------------------------------------------------- #

IDENT = re.compile(r"[A-Za-z_$][A-Za-z0-9_$.]*")
STR = re.compile(r'"((?:[^"\\]|\\.)*)"')


def unescape(s: str) -> str:
    return (s.replace("\\n", "\n").replace("\\t", "\t")
             .replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\"))


def parse_concat(expr: str):
    """
    解析 "a" + "b" + SOME_CONST 这类拼接表达式。
    返回 (文本, 引用列表): 文本中标识符拼成 {IDENT}。
    """
    parts, refs = [], []
    pos = 0
    while pos < len(expr):
        m = STR.match(expr, pos)
        if m:
            parts.append(unescape(m.group(1)))
            pos = m.end()
            continue
        m = IDENT.match(expr, pos)
        if m:
            name = m.group(0)
            if name not in ("null", "true", "false"):
                parts.append("{%s}" % name)
                refs.append(name)
            pos = m.end()
            continue
        pos += 1  # + 号 / 空格 / 括号等
    return "".join(parts), refs


def find_method_body(src: str, method: str):
    """找到 `public String method() {` 的方法体(用花括号配对)。"""
    m = re.search(r"(?:public|protected|private)?\s*(?:static\s+)?"
                  r"(?:final\s+)?String\s+" + re.escape(method) + r"\s*\([^)]*\)\s*\{", src)
    if not m:
        return None
    i = src.index("{", m.start())
    depth, j = 0, i
    while j < len(src):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return src[i + 1: j]
        j += 1
    return None


def returns_in(body: str):
    """收集方法体中所有 return <expr>; 的拼接结果。"""
    out = []
    for m in re.finditer(r"\breturn\b", body):
        i = m.end()
        # 到分号结束(忽略括号内分号几乎不会出现在字符串拼接里)
        semi = body.find(";", i)
        if semi == -1:
            continue
        expr = body[i:semi]
        # 跳过 return 后紧跟方法调用的情况(如 return super.desc())
        if not STR.search(expr) and not re.search(r"\+\s*", expr):
            continue
        txt, refs = parse_concat(expr)
        if txt.strip():
            out.append((txt.strip(), refs))
    return out


# --------------------------------------------------------------------------- #
# 3. 单文件提取
# --------------------------------------------------------------------------- #

CONST_RE = re.compile(
    r"(?:public|protected|private)\s+static\s+(?:final\s+)?String\s+"
    r"([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*(.*?);", re.S)
# String[] 数组常量: 职业特长之类的一条条短句
ARRAY_RE = re.compile(
    r"(?:public|protected|private)\s+static\s+(?:final\s+)?String\[\]\s+"
    r"([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*\{(.*?)\}\s*;", re.S)
# enum 常量带字符串参数: 徽章 / 副职业 / 英雄职业
ENUM_RE = re.compile(r"\b([A-Z][A-Z0-9_]*)\s*\(([^()]*)\)", re.M)
NAME_RE = re.compile(r"(?<![\w.])name\s*=\s*(.*?);", re.S)
PLANTNAME_RE = re.compile(r"(?<![\w.])plantName\s*=\s*\"([^\"]+)\"")
IMAGE_RE = re.compile(r"(?<![\w.])image\s*=\s*([A-Za-z_$][A-Za-z0-9_$.]*)\s*;")
SPRITE_RE = re.compile(r"spriteClass\s*=\s*([A-Za-z0-9_$]+)\.class")


def extract_file(path: str):
    raw = open(path, encoding="utf-8", errors="ignore").read()
    code = strip_comments(raw)
    cls = os.path.basename(path)[:-5]

    rec = {"class": cls, "file": path.replace("\\", "/")}

    # 名称
    names = []
    for m in NAME_RE.finditer(code):
        txt, _ = parse_concat(m.group(1))
        txt = txt.strip()
        if txt and not txt.startswith("{"):
            names.append(txt)
    if names:
        rec["name"] = names[0]
        if len(names) > 1:
            rec["altNames"] = names[1:]

    # 说明文本
    descs = []
    for meth in ("description", "info", "desc", "text", "getText", "hint"):
        body = find_method_body(code, meth)
        if not body:
            continue
        for txt, refs in returns_in(body):
            if meth == "desc" and txt in descs:
                continue
            descs.append(txt)
        if descs:
            break
    if descs:
        rec["desc"] = max(descs, key=len) if len(descs) > 1 else descs[0]
        if len(descs) > 1:
            rec["altDescs"] = [d for d in descs if d != rec["desc"]]

    # 植物名 (Plant 子类里的 plantName)
    m = PLANTNAME_RE.search(code)
    if m:
        rec["plantName"] = m.group(1)

    # String[] 数组常量 (职业特长等的短句列表)
    arrays = OrderedDict()
    for m in ARRAY_RE.finditer(code):
        items = []
        for sm in STR.finditer(m.group(2)):
            v = unescape(sm.group(1)).strip()
            if v:
                items.append(v)
        if items:
            arrays[m.group(1)] = items
    if arrays:
        rec["arrays"] = arrays

    # enum 常量 (徽章/副职业/英雄职业的标题与描述)
    em = re.search(r"\benum\s+[A-Za-z_$][A-Za-z0-9_$]*\s*\{", code)
    if em:
        # enum 块到配对右花括号
        i = code.index("{", em.start())
        depth, j = 0, i
        while j < len(code):
            if code[j] == "{":
                depth += 1
            elif code[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        block = code[i + 1: j]
        # 只取字段声明之前的常量区
        cut = re.search(r"\b(?:public|private|protected)\s+(?:static\s+)?[A-Za-z]", block)
        if cut:
            block = block[: cut.start()]
        entries = OrderedDict()
        for m in ENUM_RE.finditer(block):
            args = [unescape(x) for x in STR.findall(m.group(2))]
            if not args:
                continue
            entries[m.group(1)] = {
                "args": args,
                "nums": [int(x) for x in re.findall(r"(?<![\w.])-?\d+", m.group(2))],
            }
        if entries:
            rec["enumEntries"] = entries

    # 内联字符串字面量 (窗口/场景里直接写在 add(new ...("...")) 中的文本)
    if "/windows/" in path.replace("\\", "/") or "/scenes/" in path.replace("\\", "/"):
        lits, seen = [], set()
        known = {rec.get("name"), rec.get("desc")} | \
                {v["text"] for v in rec.get("consts", {}).values()}
        for m in STR.finditer(code):
            v = unescape(m.group(1)).strip().replace("\n", " ")
            if len(v) < 12 or " " not in v or v in seen or v in known:
                continue
            if v.endswith(".png") or v.endswith(".dat") or v.startswith("com."):
                continue
            seen.add(v)
            lits.append(v)
        if lits:
            rec["literals"] = lits

    # 贴图
    m = IMAGE_RE.search(code)
    if m:
        rec["image"] = m.group(1)
    m = SPRITE_RE.search(code)
    if m:
        rec["spriteClass"] = m.group(1)

    # 常量文本
    consts = OrderedDict()
    for m in CONST_RE.finditer(code):
        key = m.group(1)
        txt, refs = parse_concat(m.group(2))
        txt = txt.strip()
        if not txt:
            continue
        consts[key] = {"text": txt, "refs": refs}
    if consts:
        rec["consts"] = consts

    return rec


# --------------------------------------------------------------------------- #
# 4. 分类
# --------------------------------------------------------------------------- #

def classify(path: str):
    p = path.replace("\\", "/")
    if "/items/" in p:
        return "items"
    if "/plants/" in p:
        return "plants"
    if "/actors/mobs/npcs/" in p:
        return "npcs"
    if "/actors/mobs/" in p:
        return "mobs"
    if "/actors/buffs/" in p:
        return "buffs"
    if "/levels/" in p and "/painters/" not in p and "/features/" not in p:
        return "levels"
    if "/levels/features/" in p or "/levels/traps/" in p:
        return "traps"
    if p.endswith("Badges.java"):
        return "badges"
    if p.endswith("ResultDescriptions.java"):
        return "results"
    if p.endswith("Journal.java"):
        return "journal"
    if p.endswith("HeroClass.java") or "/actors/hero/" in p:
        return "hero"
    if "/scenes/" in p or "/windows/" in p or "/ui/" in p:
        return "ui"
    if "/effects/" in p or "/mechanics/" in p:
        return "mechanics"
    return "misc"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    ap = argparse.ArgumentParser(description="从 Pixel Dungeon 源码提取游戏文本")
    ap.add_argument("--src", default=os.path.join(root, ".pd-src", "src"),
                    help="pixel-dungeon 源码 src 目录")
    ap.add_argument("--out", default=os.path.join(root, "data", "en"))
    args = ap.parse_args()

    groups = OrderedDict()
    n_files = 0
    for dirpath, _, files in os.walk(args.src):
        for fn in sorted(files):
            if not fn.endswith(".java"):
                continue
            path = os.path.join(dirpath, fn)
            rec = extract_file(path)
            if len(rec) <= 2:  # 只有 class/file, 没有文本
                continue
            cat = classify(path)
            groups.setdefault(cat, []).append(rec)
            n_files += 1

    os.makedirs(args.out, exist_ok=True)
    index = {}
    for cat, recs in sorted(groups.items()):
        recs.sort(key=lambda r: r["class"])
        out = os.path.join(args.out, cat + ".json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(recs, f, ensure_ascii=False, indent=1)
        n_str = sum(
            (1 if r.get("desc") else 0) + (1 if r.get("name") else 0) +
            len(r.get("consts", {})) for r in recs)
        index[cat] = {"file": cat + ".json", "classes": len(recs), "strings": n_str}
        print(f"{cat:<12} 类 {len(recs):>4}   文本条目 {n_str:>5}")

    with open(os.path.join(args.out, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    print(f"\n共扫描出文本类 {n_files} 个 -> {args.out}")


if __name__ == "__main__":
    main()
