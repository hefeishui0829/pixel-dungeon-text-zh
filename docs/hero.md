# 英雄职业与副职业

> 中文为人工翻译; 英文原文来自 pixel-dungeon v1.9.1 源码。「贴图」列给出精灵表名与原始 tile 序号, 与贴图项目 sprites.json 的 `coords[tile]` 一一对应。

## Belongings

- **名称**：背包（backpack）
- `WEAPON` 武器
- `ARMOR` 护甲
- `RING1` 戒指一
- `RING2` 戒指二

## Hero

- **名称**：你（you）
- `TXT_LEAVE` 没人能随随便便离开像素地牢。
- `TXT_LEVEL_UP` 升级了！
- `TXT_NEW_LEVEL` 欢迎来到等级 %d！你现在更健壮、也更专注。命中敌人与闪避攻击都变得更容易了。
- `TXT_YOU_NOW_HAVE` 你现在拥有 %s
- `TXT_SOMETHING_ELSE` 这里还有别的东西
- `TXT_LOCKED_CHEST` 这个箱子上锁了，你没有匹配的钥匙
- `TXT_LOCKED_DOOR` 你没有匹配的钥匙
- `TXT_NOTICED_SMTH` 你注意到了什么
- `TXT_WAIT` ……
- `TXT_SEARCH` 搜索
- `ATTACK` 攻击技能
- `DEFENSE` 防御技能
- `STRENGTH` 力量
- `LEVEL` 等级
- `EXPERIENCE` 经验

## HeroClass

- `WARRIOR`：勇士
  - 原文：warrior
- `MAGE`：法师
  - 原文：mage
- `ROGUE`：盗贼
  - 原文：rogue
- `HUNTRESS`：女猎手
  - 原文：huntress
- **WAR_PERKS**
  - 勇士初始拥有 11 点力量。（Warriors start with 11 points of Strength.）
  - 勇士开局自带一把独特的短剑。这把剑日后可以「重铸」，用来升级另一把近战武器。（Warriors start with a unique short sword. This sword can be later "reforged" to upgrade another melee weapon.）
  - 勇士不擅长投掷武器。（Warriors are less proficient with missile weapons.）
  - 勇士吃下任何食物都会回复一些生命。（Any piece of food restores some health when eaten.）
  - 力量药水从一开始就是已鉴定状态。（Potions of Strength are identified from the beginning.）
- **MAG_PERKS**
  - 法师开局自带一支独特的魔法飞弹法杖。这支法杖日后可以「分解附魔」，用来升级另一支法杖。（Mages start with a unique Wand of Magic Missile. This wand can be later "disenchanted" to upgrade another wand.）
  - 法师的法杖充能速度更快。（Mages recharge their wands faster.）
  - 法师吃下任意食物时，会为背包中所有法杖各恢复 1 点充能。（When eaten, any piece of food restores 1 charge for all wands in the inventory.）
  - 法师可以把法杖当作近战武器使用。（Mages can use wands as a melee weapon.）
  - 鉴定卷轴从一开始就是已鉴定状态。（Scrolls of Identify are identified from the beginning.）
- **ROG_PERKS**
  - 盗贼开局自带一枚暗影之戒+1。（Rogues start with a Ring of Shadows+1.）
  - 盗贼在装备戒指时即可鉴定其类型。（Rogues identify a type of a ring on equipping it.）
  - 盗贼精通轻甲，穿着轻甲时闪避更高。（Rogues are proficient with light armor, dodging better while wearing one.）
  - 盗贼擅长发现暗门与陷阱。（Rogues are proficient in detecting hidden doors and traps.）
  - 盗贼能更久地不吃东西。（Rogues can go without food longer.）
  - 魔法地图卷轴从一开始就是已鉴定状态。（Scrolls of Magic Mapping are identified from the beginning.）
- **HUN_PERKS**
  - 女猎手初始拥有 15 点生命。（Huntresses start with 15 points of Health.）
  - 女猎手开局自带一把独特的可升级回旋镖。（Huntresses start with a unique upgradeable boomerang.）
  - 女猎手精通投掷武器，力量过剩时还会获得额外伤害加成。（Huntresses are proficient with missile weapons and get a damage bonus for excessive strength when using them.）
  - 女猎手从露水中获得更多生命回复。（Huntresses gain more health from dewdrops.）
  - 女猎手能感知邻近的怪物，即使它们躲在障碍物后面。（Huntresses sense neighbouring monsters even if they are hidden behind obstacles.）

## HeroSubClass

- `GLADIATOR`：角斗士 / 用近战武器成功命中后，_角斗士_可以开始连击，此后每一次成功命中都会造成更高的伤害。
  - 原文：gladiator / A successful attack with a melee weapon allows the _Gladiator_ to start a combo,  / in which every next successful hit inflicts more damage.
- `BERSERKER`：狂战士 / 身受重伤时，_狂战士_会进入狂怒状态，大幅提升伤害输出。
  - 原文：berserker / When severely wounded, the _Berserker_ enters a state of wild fury  / significantly increasing his damage output.
- `WARLOCK`：术士 / 击杀敌人后，_术士_会吞噬其灵魂，以此治愈伤口并缓解饥饿。
  - 原文：warlock / After killing an enemy the _Warlock_ consumes its soul.  / It heals his wounds and satisfies his hunger.
- `BATTLEMAGE`：战斗法师 / 手持法杖作战时，_战斗法师_会根据当前充能数造成额外伤害。每次成功命中都会为这支法杖恢复 1 点充能。
  - 原文：battlemage / When fighting with a wand in his hands, the _Battlemage_ inflicts additional damage depending  / on the current number of charges. Every successful hit restores 1 charge to this wand.
- `ASSASSIN`：刺客 / 发动偷袭时，_刺客_会对目标造成额外伤害。
  - 原文：assassin / When performing a surprise attack, the _Assassin_ inflicts additional damage to his target.
- `FREERUNNER`：疾行者 / _疾行者_的移动速度几乎是大多数怪物的两倍。奔跑时他更难被击中。为此他必须轻装，且不能处于饥饿状态。
  - 原文：freerunner / The _Freerunner_ can move almost twice faster, than most of the monsters. When he  / is running, the Freerunner is much harder to hit. For that he must be unencumbered and not starving.
- `SNIPER`：狙击手 / _狙击手_能发现敌人护甲上的弱点，使用投掷武器时可有效无视护甲。
  - 原文：sniper / _Snipers_ are able to detect weak points in an enemy's armor,  / effectively ignoring it when using a missile weapon.
- `WARDEN`：守望者 / 与大自然之力的紧密联系让_守望者_能够从植物上采集露水与种子。此外，踩倒高草会赋予她们一个临时护甲增益。
  - 原文：warden / Having a strong connection with forces of nature gives _Wardens_ an ability to gather dewdrops and  / seeds from plants. Also trampling a high grass grants them a temporary armor buff.
- `SUBCLASS` 副职业

