# MOD 结构与加载机制

来源：https://stellaris.paradoxwikis.com/Modding

## 一、MOD 存放位置

| 平台 | 路径 |
|------|------|
| Windows | `…\Documents\Paradox Interactive\Stellaris\mod` |
| Linux | `~/.local/share/Paradox Interactive/Stellaris/mod` |
| macOS | `~/Documents/Paradox Interactive/Stellaris/mod` |
| Steam 创意工坊订阅 | `…\SteamLibrary\steamapps\workshop\content\281990`（按 Workshop ID 命名，**不要直接改，会被覆盖**） |
| Paradox Mods | 上述 mod 文件夹内，命名 `PDX_<MOD_ID>` |

`281990` 是 Stellaris 的 Steam AppID。

## 二、描述文件（必备两个）

```
…\Documents\Paradox Interactive\Stellaris\mod\MyMod.mod        ← 含 path
…\Documents\Paradox Interactive\Stellaris\mod\MyMod\descriptor.mod  ← 不含 path
```

`MyMod.mod` 示例：

```
version="1.0"
tags={
	"Gameplay"
	"Events"
}
name="My Mod"
supported_version="v4.0.*"
path="mod/MyMod"
remote_file_id="1234567890"
```

`descriptor.mod` 完全相同，只是删掉 `path` 行。

### 字段说明

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | 是 | MOD 名称，启动器中显示 |
| `path` | 仅 `.mod` 需要 | 指向 mod 目录，**用正斜杠 `/`**；可用相对（`mod/MyMod`）或绝对路径 |
| `version` | 否 | 启动器显示的版本号，纯展示，与游戏逻辑无关 |
| `supported_version` | 推荐 | 如 `v4.0.*`；支持通配符。**仅是视觉提示，不影响加载** |
| `tags` | 否 | 最多 10 个；创意工坊分类用 |
| `dependencies` | 否 | 依赖的其他 MOD，用于强制加载顺序 |
| `picture` | 否 | 缩略图；2.4+ 必须命名为 `thumbnail.png` |
| `remote_file_id` | 否 | 创意工坊 ID，仅在已上传后存在 |

常用 tags：`Gameplay` `Balance` `Events` `Graphics` `Economy` `Sound` `Translation` `Species` `Leaders` `Technologies` `Spaceships` `Loading Screen` `Overhaul` `Utilities` `Fixes` `Buildings` `Map`。

### 缩略图

放在 mod 根目录（与 `descriptor.mod` 同级）。2.4 之后的新启动器只认 `thumbnail.png`（支持 PNG / JPEG）。

## 三、目录职责总表

MOD 根目录内直接镜像游戏安装目录：

| 目录 | 职责 | 主要文件类型 |
|------|------|--------------|
| `common/` | **绝大部分游戏内容定义**（科技、飞升、法令、建筑、区划、舰船、领袖、天灾、修正、脚本宏等） | `.txt` |
| `events/` | 事件脚本 | `.txt` |
| `localisation/` | 本地化文本（注意英式拼写 s） | `.yml` |
| `gfx/` | 贴图、模型、粒子、立绘、图标 | `.dds` `.mesh` `.asset` `.particle` |
| `interface/` | UI 布局与 sprite 注册 | `.gfx` `.gui` |
| `flags/` | 国家旗帜 | `.dds` + `colors.txt` |
| `fonts/` | 字体 | `fonts.asset` + 字体文件 |
| `map/` | 银河生成、预设星系 | `galaxy/` `setup_scenarios/` |
| `music/` | 音乐 | `.ogg` + `songs.asset` |
| `sound/` | 音效 | `.wav` `.asset` |
| `prescripted_countries/` | 预设国家 | `.txt` |

`common/` 下的常见子目录（实际 MOD 中高频出现）：

```
common/
├── achievement/            achievements.txt
├── agreement_presets/      协议预设
├── alerts.txt              警报
├── ambient_objects/        环境物体（如恒星站、空间站实体）
├── anomalies/              异常现象
├── archaeological_site_types/  考古站点
├── armies/                 陆军
├── ascension_perks/        飞升天赋
├── buildings/              建筑
├── button_effects/         按钮效果（UI 按钮绑定的脚本）
├── bypass/                 星门 / 虫洞等捷径
├── colony_types/           殖民地类型
├── component_sets/         武器/部件套装（图标集）
├── component_templates/    舰船部件具体数值
├── council_agendas/        议会议程
├── country_types/          国家类型（普通/堕落/天灾等）
├── decisions/              帝国决议
├── defines/                引擎常量覆盖
├── deposits/               星球资源沉积 / 障碍
├── districts/              区划
├── economic_categories/    经济分类
├── edicts/                 法令
├── event_chains/           事件链
├── federation_laws/        联邦法律
├── federation_perks/       联邦专精
├── federation_types/       联邦类型
├── game_concepts/          游戏概念（生成 tooltip 词条）
├── game_rules/             游戏规则
├── global_ship_designs/    预设舰船设计
├── governments/            政体与 civics（民政）
├── graphical_culture/      图形文化（舰船/建筑外观分组）
├── inline_scripts/         内联脚本宏
├── megastructures/         巨构
├── message_types/          消息类型
├── name_lists/             随机名称表
├── notification_modifiers/ 通知类修正
├── on_actions/             事件钩子
├── opinion_modifiers/      外交观点修正
├── planet_classes/         星球类型
├── planet_modifiers/       行星修正
├── pop_categories/         人口类别
├── renewable_deposits/
├── scripted_effects/       可复用效果宏
├── scripted_loc/           可复用本地化
├── scripted_triggers/      可复用条件宏
├── scripted_variables/     脚本变量（@var）
├── sector_types/
├── ship_sizes/             舰船尺寸（船体值、槽位数）
├── solar_system_initializers/  星系初始生成器
├── special_projects/       特殊项目
├── species_classes/        物种大类
├── species_names/
├── species_rights/
├── starbase_buildings/
├── starbase_modules/
├── star_classes/           恒星类型
├── static_modifiers/       静态修正
├── strategic_resources/    战略资源
├── technology/             科技（注意是 technology 单数文件夹名）
├── tradition_categories/   传统树分类
├── traditions/             传统
├── traits/                 物种 / 领袖特质
├── triggers.txt
├── war_goals/
└── ...
```

> 具体某个版本有哪些子目录，最可靠的做法是直接看游戏安装目录 `…\Steam\steamapps\common\Stellaris\common\`。

## 四、覆盖机制：LIOS 与 FIOS

Stellaris 有两种文件级覆盖策略：

- **LIOS（Last In, Only Served）** —— 后加载的同名文件**整体替换**先加载的。适用于 `common/` 多数文件、`localisation/`、`interface/`、`fonts/`。
- **FIOS（First In, Only Served）** —— 先加载的同名文件生效，后者被忽略。适用于 `events/` 等。

关键结论：

1. 覆盖是**按文件**而非按条目（本地化例外，见下）。想改原版文件里的**一条**内容，就得把**整个文件**复制过来改，代价极大。
2. 因此**永远优先新建独立文件**（例如 `00_MyMod_buildings.txt`），利用"同名对象后定义者覆盖"的对象级规则，而不是覆盖文件。
3. **本地化是唯一支持条目级覆盖的地方**：把 yml 放进 `localisation/replace/` 子目录，它会在所有其他本地化之后加载，按 key 逐条覆盖（LIOS per-key）。

### 加载顺序（Mod load order）

启动器按 MOD 在列表中的顺序加载，下方覆盖上方。要点：

- 补丁类 / 兼容性 MOD 应排在**被补丁的 MOD 之后**（即列表更靠下）。
- 用 `dependencies` 字段声明依赖可强制顺序。
- 同名本地化 key 冲突时，最后一个加载的生效。

### 与 Workshop 冲突

若同一个 MOD 同时以「本地 MOD」和「创意工坊订阅」两种形式存在，游戏会拒绝加载。排查时删掉其中一个。

## 五、对象级覆盖（真正的日常手段）

Paradox 游戏的核心是：**新文件里定义一个已存在的 key，就会覆盖原版对象**。这比覆盖文件安全得多。

```
# 新建 common/buildings/zz_MyMod_override.txt
building_capital_1 = {
	# 重写你要改的字段
	max_level = 2
}
```

但要注意：**这是整对象替换**，未写出的字段会回落到引擎默认值而非原版值。所以覆盖一个复杂对象时，最稳的做法是把原版定义整段复制过来再改。

## 六、`defines/` —— 改引擎常量

`common/defines/` 下的文件可以覆盖引擎硬编码常量（如 `POP_GROWTH_BASE`、`FLEET_SIZE_BASE`）。写法：

```
# common/defines/MyMod_defines.txt
NGameplay = {
	POP_GROWTH_BASE = 3.0
}
```

文件名需按字母序排在原版文件之前才能覆盖成功（例如 `00_MyMod_defines.txt`）。
