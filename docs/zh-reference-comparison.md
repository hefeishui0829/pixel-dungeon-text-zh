# 中文分支对照：本项目的文本量对不对得上？

本项目的中文是**从 v1.9.1 源码抠字符串后人工译的**，没有第三方译文可以核对。为了验证"没漏掉整块内容、译名不是自说自话"，拿中文社区里最权威的一套译名做交叉验证。

对照脚本：`tools/compare_zh_reference.py`（可复跑，见文末）。

---

## 1. 找谁对照：候选与取舍

| 候选 | 血缘 | 中文文本 | 结论 |
|---|---|---|---|
| **[Shattered Pixel Dungeon](https://github.com/00-Evan/shattered-pixel-dungeon) 官中** | 原作者 Evan 的重制续作 | 完整，Crowdin 官方维护，`core/src/main/assets/messages/*_zh.properties` 共 **4976 键**，中译率 **99.7%** | ✅ 选它，量级和译名都可参照 |
| [Remixed Dungeon](https://github.com/NYRDS/remixed-dungeon)（NYRDS） | 从原版 PD fork，已大幅魔改 | `GameServices/texts-zh-Hans/` 只有 `badges.txt` + `desc.txt`，合计 **63 行**且无键名 | ❌ 量太小，做不了量级对照 |
| Re-ARranged-Pixel-Dungeon-CN 等国内分支 | 基于 Shattered | 完整，但译名继承自 SPD | ⭕ 与 SPD 同源，不必重复统计 |

一句话：**原版 v1.9.1 在 GitHub 上没有成气候的中文分支**，能拿来做量级参照的只有 SPD 官中。

---

## 2. 量级对比

| | 本项目 (v1.9.1) | Shattered 官中 | 倍数 |
|---|---|---|---|
| 条目/键总数 | **908** 条已译串（335 个类） | **4976** 键 | 5.9× |
| 物品 | 147 类 / 387 串 | 2073 键 | — |
| 怪物 | 34 类 / 74 串 | （actors 1609 键含怪物、Buff、NPC、Blob） | — |
| 徽章 | 64 条 | 212 条 | — |
| 植物 | 9 类 / 19 串 | 67 键 | — |

**5.9 倍不等于我们漏了 83%**。SPD 是重制续作，物品数量本身就是原版的数倍（多了神器、职业护甲、大量新药水卷轴、挑战模式等），而且 SPD 把界面文案拆得极细（每个窗口的每个按钮一个键），原版则是硬编码在 Java 里的字符串常量。两者粒度不同，只能比"类别是否齐全"，不能比绝对条数。

### 同名命中率（看类别齐不齐）

我们 335 个类里，能在 SPD 官中里找到同名条目的 **246 个（73%）**。未命中的 89 个，按原因分三类：

| 原因 | 例子 | 是否缺漏 |
|---|---|---|
| SPD 已删除/未继承的原版内容 | `ArmorKit`、`AutoRepair`、`Bounce`、`CurareDart`、`CursePersonification`、`King`、`Shielded` | 否，SPD 本来就没有 |
| SPD 改名 | `Skeleton`→`遗骸`、`Level/Room` 等关卡类重构 | 否，是重制差异 |
| 我们额外收录的源码常量类 | `Actor`、`Assets`、`Blob`、`Bones`、`ResultDescriptions` | 否，是我们比 SPD 更全的地方 |

按类别看命中率：`npcs 100%`、`buffs 100%`、`plants 89%`、`mobs 85%`、`badges 83%`、`items 71%`、`ui 62%`；`levels/traps/journal/results/misc` 偏低是因为这些类别装的是**源码常量与类名**，不是游戏内可见文案，SPD 里自然对不上。

---

## 3. 术语一致性

只比"内容类"（items / mobs / npcs / plants / hero），徽章在 SPD 里被整体重制过，比译名没有意义。

**137 条可比名称：完全相同 68 条（50%）、相似度 ≥50% 51 条（37%）、措辞不同 18 条（13%）。**

抽样：

| 条目 | 本项目 | SPD 官中 | 判定 |
|---|---|---|---|
| Bandit | 疯狂强盗 | 疯狂强盗 | 一致 |
| Bat | 吸血蝙蝠 | 吸血蝙蝠 | 一致 |
| Blacksmith | 巨魔铁匠 | 巨魔铁匠 | 一致 |
| Boomerang | 回旋镖 | 回旋镖 | 一致 |
| Brute | 豺狼人蛮兵 | 豺狼暴徒 | 高度相似 |
| Albino | 白化巨鼠 | 白化老鼠 | 高度相似 |
| Acidic | 酸液蝎蛛 | 酸液巨蝎 | 高度相似 |
| Ankh | 安卡 | 重生十字架 | 措辞不同 |
| Amulet | 耶诺之护符 | Yendor护符 | 措辞不同 |

那 15% 的差异基本都是 **SPD 重制时改过名字**（安卡→重生十字架、护符改名），或者我们选择了更贴近英文原文的直译。两边都能自圆其说，不是对错问题。

**结论：约 85% 的译名与社区主流说法吻合，属于"能对齐"的水平。**

> **注**：上表"措辞不同 18 条"是 `compare_zh_reference.py` 在**未归一化匹配**（仅 `id.toLowerCase()` 与 SPD `类名` 精确相等才算命中）下的抽样口径，命中集较小。若改用**归一化匹配**（去标点/下划线后比对，覆盖更多同实体异写），`tools/collect_disputes.py` 实际收录的争议条目为 **181 条**（177 措辞不同 + 2 未译有参照 + 2 疑似改名）。完整清单见 [`data/zh/disputed.json`](data/zh/disputed.json) 与 [`docs/disputed-translations.md`](docs/disputed-translations.md)，每条都带 `build_note` 提示构建时如何取舍。

---

## 4. 怎么复跑

```bash
mkdir -p /tmp/spd && cd /tmp/spd
for f in actors items journal levels misc plants scenes ui windows; do
  base="https://raw.githubusercontent.com/00-Evan/shattered-pixel-dungeon/master/core/src/main/assets/messages/$f"
  curl -sL "$base/$f.properties"      -o ${f}_en.properties
  curl -sL "$base/${f}_zh.properties" -o ${f}_zh.properties
done

python3 tools/compare_zh_reference.py --spd /tmp/spd
```

脚本输出四段：A 参照系规模 → B 本项目规模 → C 同名命中率 → D 术语一致性抽样。

---

## 5. 局限（诚实记录）

1. **SPD 不是原版译文的真值**。它是重制续作，物品/怪物都有增删改动，命中率低不代表本项目缺漏，只说明 SPD 改得多。
2. **粒度不同**。SPD 按 UI 元素拆键，我们按 Java 类聚合，条数天然不可直接比。
3. **术语差异不等于错误**。`安卡` vs `重生十字架` 这类是命名风格选择，本项目坚持贴近 v1.9.1 英文原文。
4. **截止时点**：以上数据抓自 Shattered Pixel Dungeon `master` 分支，2026-10-03。SPD 持续更新，数字会变，重跑脚本即可得到当时的值。
