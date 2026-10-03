# 中文文档索引

按游戏内容分类的中文文本（含英文原文对照与贴图坐标）。所有 Markdown 由
`tools/build_zh.py` 从 `data/zh/*.json` 自动生成，请勿手改；改数据后重跑脚本即可。

| 文档 | 内容 | 条目 |
|---|---|---|
| [hero.md](hero.md) | 英雄职业、职业特长、副职业 | 4 个文件（含 4 职业 × 5~6 条特长 + 8 副职业） |
| [items.md](items.md) | 全部物品：武器/护甲/药水/卷轴/法杖/戒指/食物/任务品/容器/钥匙 | 147 |
| [mobs.md](mobs.md) | 怪物（含 Boss）名称与图鉴描述 | 34 |
| [npcs.md](npcs.md) | NPC 与任务对话（悲伤幽灵/铁匠/小恶魔/法杖匠/鼠王等） | 9 |
| [plants.md](plants.md) | 植物与种子 | 9 |
| [buffs.md](buffs.md) | 状态效果的提示文本 | 10 |
| [badges.md](badges.md) | 徽章名称与解锁条件 | 64 |
| [levels.md](levels.md) | 楼层/地形相关文本 | 8 |
| [traps.md](traps.md) | 陷阱与机关（深渊、告示牌、炼金锅） | 3 |
| [journal.md](journal.md) | 日志条目（各类井、献祭室、炼金锅、NPC） | 2（11 个条目） |
| [results.md](results.md) | 结算与死因描述 | 1（14 条） |
| [ui.md](ui.md) | 界面文本 + 章节剧情（WndStory 五章） | 29 |
| [misc.md](misc.md) | 战斗日志、世界交互（井、献祭之火） | 15 |

## 怎么读「贴图」列

`items #87` 表示：**图集 `items.png`，原始 16×16 网格中的第 87 格**（行主序，从 0 开始）。

贴图项目 [pixel-dungeon-mi-band](https://github.com/hefeishui0829/pixel-dungeon-mi-band)
输出的 `sprites.json` 里，`sheets.items.coords` 是一个数组，其下标与这个原始序号一一对应：

```js
const xy = sprites.sheets.items.coords[87];   // 例如 band 档 -> [36, 48]
// CSS: background-position: -36px -48px
```

不想自己查的话，用本项目的脚本：

```bash
python3 tools/lookup_sprite.py --band ../pixel-dungeon-band --id Amulet
```

它会同时给出 `band-lite` / `band` / `band-pro` 三档的坐标。`data/sprite-map.json`
是全部 173 个带贴图条目的坐标总表，可直接内联进快应用。

## 翻译状态

844 条已译文本；存档字段名、文件名常量等技术字段不翻译（它们不是玩家可见文本）。
