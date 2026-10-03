# 像素地牢 中文文本库（pixel-dungeon-text-zh）

把 [Pixel Dungeon](https://github.com/watabou/pixel-dungeon) v1.9.1（GPL-3.0）里
**散落在 505 个 Java 源文件中的游戏文本**提取出来，人工翻译成简体中文，
并与姊妹项目 **[pixel-dungeon-mi-band](https://github.com/hefeishui0829/pixel-dungeon-mi-band)**
（小米手环 Vela 快应用低精度贴图）的图集坐标**一一对应**。

> 姊妹项目解决「图怎么塞进手环」，本项目解决「图旁边该显示什么字」。
> 两者用同一套 (图集名, tile 序号) 寻址，可以拼起来直接做一个中文版的手环小游戏。

## 为什么需要这个项目

Pixel Dungeon 的文本**不在** `res/values/strings.xml` 里（那个文件只有一句 app_name），
而是硬编码在 Java 类的字符串常量与方法返回值中：

```java
// items/DewVial.java
name = "dew vial";
private static final String TXT_FULL = "Your dew vial is full!";
public String desc() { return "You can store excess dew ..."; }
```

所以这里写了一个确定性的静态提取器（`tools/extract_text.py`），
对源码做词法级去注释 → 解析字符串拼接 → 按目录分类，任何人重跑都得到同一份数据；
中文翻译单独放在 `data/zh/manual/`，重跑提取不会覆盖译文。

## 数据长什么样

```json
{
  "id": "Amulet",
  "zh": "耶诺之护符",
  "en": "Amulet of Yendor",
  "zhDesc": "耶诺之护符是已知最强大的神器，其来源不明……",
  "enDesc": "The Amulet of Yendor is the most powerful known artifact ...",
  "sprite": { "sheet": "items", "tile": 87 }
}
```

`sprite.tile` 是**该精灵表在游戏内网格中的帧序号**（行主序），
正好是贴图项目 `sprites.json` 里 `coords` 数组的下标 —— 不需要任何换算。

> 注意不是统一的 16×16 序号：游戏内 82 张精灵表只有 8 张是标准 16×16，
> 其余各有网格（`piranha` 12×16、`scorpio` 18×17、`rat` 16×15 …）。
> 贴图项目按各自的真实网格切图（见其 `tools/sprite_grid.json`），
> 所以这里的序号直接就是 `coords` 下标。

## 内容一览

| 类别 | 条目 | 说明 |
|---|---|---|
| items | 147 | 物品：武器/护甲/附魔/印记/药水/卷轴/法杖/戒指/食物/任务品/容器/钥匙 |
| mobs | 34 | 怪物与 Boss（含 Goo、Tengu、DM-300、矮人国王、Yog-Dzewa） |
| npcs | 9 | NPC 与任务对话（悲伤幽灵三分支、巨魔铁匠、小恶魔、老法杖匠、鼠王等） |
| plants | 9 | 植物与种子 |
| buffs | 10 | 状态效果提示 |
| badges | 64 | 徽章名与解锁条件 |
| hero | 4 | 4 个职业 × 特长说明 + 8 个副职业 |
| ui | 29 | 界面文本 + **WndStory 五章剧情**（下水道/监狱/洞窟/矮人都城/恶魔殿堂） |
| levels / traps / journal / results / misc | 29 | 楼层、陷阱、日志、14 条死因、战斗与世界交互 |
| **合计** | **335 个类 / 844 条已译文本** | 其中 173 条带贴图坐标 |

文本量是否够、译名是否靠谱，跟社区主流中文分支做过交叉验证：[docs/zh-reference-comparison.md](docs/zh-reference-comparison.md)。结论：类别齐全无缺块，123 条可比名称中 **85% 与 Shattered 官方简体中文吻合**（44% 完全相同、41% 高度相似），差异集中在 SPD 重制改名过的条目。

## 目录结构

```
data/en/            英文原文(脚本提取, 可复现)
data/zh/manual/     中文译文(人工维护)
data/zh/*.json      合并后的双语数据(含贴图坐标), 机器生成
data/zh/all.json    全量合并
data/sprite-index.json   类名 -> (图集, tile) 索引
data/sprite-map.json     全部 173 条的三档压缩图集坐标
docs/*.md           按类别的可读文档
tools/              提取 / 合并 / 查表 / 校验脚本
```

## 用法

```bash
# 1. 从像素地牢源码提取英文文本
python3 tools/extract_text.py --src <pd>/src --out data/en

# 2. 生成贴图索引(需要贴图项目提供图集原始尺寸)
python3 tools/build_sprite_index.py --src <pd>/src --out data/sprite-index.json

# 3. 合并英文 + 中文 + 贴图, 产出 data/zh 与 docs
python3 tools/build_zh.py

# 4. 查某个条目在压缩图集上的坐标
python3 tools/lookup_sprite.py --band ../pixel-dungeon-band --id Amulet

# 5. 自检: 给出的坐标在压缩图集上是否真的有像素
python3 tools/verify_mapping.py --preset band
```

第 5 步当前结果：三档均为 **173 条有像素、0 空 tile、0 异常**。

## 与贴图项目的对应关系

| 本项目 | 贴图项目 |
|---|---|
| `sprite.sheet`（如 `items`、`rat`） | `output/<档位>/<sheet>.png` |
| `sprite.tile`（游戏内网格帧序号） | `sprites.json → sheets[sheet].coords[tile]` |
| `data/sprite-map.json` | 三档 `{image, x, y, tileWidth, tileHeight}` 直接可用 |

三档 tile 尺寸：`band-lite` 8px、`band` 12px（推荐）、`band-pro` 16px。
对应小米手环 9/10（192×490、212×520）与 8/9 Pro（336×480）。

## 已知偏差（诚实记录）

1. **动态描述文本带占位符**：如 `"%s of affection"`、`"seed of {plantName}"`，
   中文保留了同样的占位符，运行时按游戏逻辑填充即可。
2. **非 16×16 网格的图集**：游戏内 82 张精灵表只有 8 张是标准 16×16。
   贴图项目**曾经**统一按 16×16 切，导致这些图集动画帧整体错位；该问题已修正
   （改为按 `sprite_grid.json` 里各自的游戏网格切），本索引也随之改为直接记录
   游戏内帧序号，`sprite-index.json` 中的 `gameGrid` 字段供核对。
3. **低 alpha 残影格**：`piranha.png` 第 0/1 格是食人鱼的水下半透明阴影
   （alpha 峰值仅 76），标准二值化阈值 128 下会被整格判空。
   贴图管线现改为"标准阈值变全空时退回低阈值 (32)"的双阈值策略，
   这两格已找回（验证结果 173 条全部有像素）。代价是它们会被存成不透明实色，
   而非原来的半透明。

## 许可

- 游戏文本与其提取产物：沿用上游 **GPL-3.0**（见 `LICENSE`）。
- `tools/` 下的脚本本身以 **MIT** 发布（它们不引用任何 GPL 素材，素材路径由命令行参数传入）。
- 中文译文基于上游英文文本翻译，同样以 GPL-3.0 共享。

## 来源

- 上游仓库：https://github.com/watabou/pixel-dungeon（commit `ca458a2`，v1.9.1）
- 贴图项目：https://github.com/hefeishui0829/pixel-dungeon-mi-band
- 官方文档归档：https://github.com/hefeishui0829/xiaomi-vela-docs

详见 [SOURCES.md](SOURCES.md)。
