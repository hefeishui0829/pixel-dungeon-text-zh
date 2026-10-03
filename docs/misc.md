# 战斗日志与世界交互

> 中文为人工翻译; 英文原文来自 pixel-dungeon v1.9.1 源码。「贴图」列给出精灵表名与原始 tile 序号, 与贴图项目 sprites.json 的 `coords[tile]` 一一对应。

## Bones

- `LEVEL` 层数
- `ITEM` 物品

## Char

- **名称**：生物（mob）
- `TXT_HIT` %s 击中了 %s
- `TXT_KILL` %s 杀死了你……
- `TXT_DEFEAT` %s 击败了 %s
- `TXT_YOU_MISSED` %s %s 你的攻击
- `TXT_SMB_MISSED` %s %s %s 的攻击
- `TXT_OUT_OF_PARALYSIS` 疼痛让 %s 从麻痹中惊醒
- `TAG_HP` 当前生命
- `TAG_HT` 生命上限

## Dungeon

- `VERSION` 版本
- `CHALLENGES` 挑战
- `HERO` 英雄
- `GOLD` 金币
- `DEPTH` 深度
- `LEVEL` 等级
- `CHAPTERS` 章节
- `QUESTS` 任务
- `BADGES` 徽章

## GLog

- `TAG` 游戏
- `POSITIVE` ++
- `NEGATIVE` --
- `WARNING` **
- `HIGHLIGHT` @@

## Rankings

- `RECORDS` 记录
- `LATEST` 最近
- `TOTAL` 总计
- `WON` 胜利
- `REASON` 原因
- `WIN` 胜利
- `SCORE` 得分
- `TIER` 档位

## SacrificialFire

- **名称**：献祭之火
- **说明**：这是一个承载着献祭之火的祭坛。在此殒命的生物都将成为献给地牢幽魂的祭品。\n\n或许献祭够多，就能得到回报？
- `TXT_WORTHY` 你的祭品是值得的……
- `TXT_UNWORTHY` 你的祭品不值得……
- `TXT_REWARD` 你的祭品是值得的，而你也是！

## Statistics

- `GOLD` 得分
- `DEEPEST` 最深楼层
- `SLAIN` 击杀敌人数
- `FOOD` 食用食物数
- `ALCHEMY` 调配药水数
- `PIRANHAS` 食人鱼
- `NIGHT` 夜间狩猎
- `ANKHS` 使用安卡数
- `DURATION` 时长
- `AMULET` 已获得护符

## WaterOfAwareness

- **名称**：觉察之井
- **说明**：知识的力量正在从这口井的水里涌出。饮下井中的水将会鉴定所有已装备的物品、探测背包中所有物品的诅咒并揭示本层所有物品的位置。
- `TXT_PROCCED` 你刚喝下一口，就感到知识涌入脑海。现在你对自己的装备了如指掌。你还感知到了本层的所有物品，并知晓了它的一切秘密。

## WaterOfHealth

- **名称**：治疗之井
- **说明**：生命的力量正在从这口井的水里涌出。饮下井中的水可以治疗伤口、解除饥饿并净化所有已装备物品的诅咒。
- `TXT_PROCCED` 你刚喝下一口，就感到伤口完全愈合了。

