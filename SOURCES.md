# 来源与许可说明

## 文本来源

| 来源 | 内容 | 许可 |
|---|---|---|
| [watabou/pixel-dungeon](https://github.com/watabou/pixel-dungeon) @ `ca458a2` (v1.9.1) | 全部英文游戏文本（物品/怪物/NPC/剧情/界面/结算） | GPL-3.0 |
| 本项目人工翻译 | 简体中文译文 | GPL-3.0（译本随原作） |

Pixel Dungeon 版权归 Oleg Dolya（Watabou）所有，代码与文本以 GPL-3.0 发布。
本项目**只做提取与翻译，不修改游戏逻辑**，并保留全部英文原文以便对照与核对。

## 提取方式

`tools/extract_text.py` 对源码做静态分析：

1. 字符级去注释（不误伤字符串里的 `//` 与 `http://`）；
2. 解析 `"a" + "b" + CONST` 形式的拼接，标识符保留为 `{CONST}` 占位而不擅自内联；
3. 提取 `name = "..."`、`description() / info() / desc()` 的返回值、
   `static final String` 常量、`String[]` 数组、`enum` 常量参数；
4. 对 `windows/` 与 `scenes/` 目录额外收集内联字面量（窗口里直接写在 `new XXX("...")` 中的文本）。

刻意**不收录**：注释、import、日志 tag、文件名/音效名常量、存档字段名。
后者（如 `pos`、`level`、`items.png`）在生成文档时被过滤，不算进翻译覆盖率。

## 与贴图项目的一致性

贴图坐标全部来自源码自身的常量（`ItemSpriteSheet`、`Assets`、`*Sprite` 的
`TextureFilm`、`Badges.Badge` 的构造参数、植物的 `image` 字段），
而不是人工对照图片数的结果 —— 因此不会数错。

`tools/verify_mapping.py` 会打开贴图项目压缩后的 PNG，
按算出的坐标切出那一格并检查是否真的有像素，作为回归自检。

## 中文译文的口径

- 术语尽量统一：Potion→药水、Scroll→卷轴、Wand→法杖、Ring→戒指、Glyph→印记、
  Enchantment→附魔、Dew→露水、Ankh→安卡、Amulet of Yendor→耶诺之护符。
- 职业：Warrior→勇士、Mage→法师、Rogue→盗贼、Huntress→女猎手；
  副职业：Gladiator→角斗士、Berserker→狂战士、Warlock→术士、Battlemage→战斗法师、
  Assassin→刺客、Freerunner→疾行者、Sniper→狙击手、Warden→守望者。
- 怪物与物品的译名参考了中文玩家社区的常见叫法，同时保留英文原名以便检索。
- 剧情文本（WndStory 五章）为完整翻译，未做删节。

## 许可摘要

- 数据与译文：GPL-3.0。
- `tools/` 脚本：MIT（脚本本身不内含任何 GPL 素材，素材路径由命令行参数给出）。
- 如果你要把这些文本用于闭源项目，请先确认 GPL-3.0 的传染性要求，
  或只使用不受版权保护的部分（如纯名称列表）。
