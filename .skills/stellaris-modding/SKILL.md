---
name: stellaris-modding
description: 群星（Stellaris）MOD 制作与维护的完整技能。当用户要创建 / 修改 / 调试 / 打包 / 发布 Stellaris MOD，或涉及 .mod 与 descriptor.mod 描述文件、common/ 下的定义文件、events 事件脚本、localisation 本地化 yml、interface 与 gfx 界面贴图、gui 布局、flags 旗帜、portraits 立绘、on_actions、scripted_triggers / scripted_effects、static_modifiers 静态修正、科技 / 飞升天赋 / 法令 / 起源 / 民政 / 舰船部件 / 巨构 / 遗珍等内容时使用。也适用于排查 error.log 报错、MOD 加载顺序冲突（LIOS/FIOS）、本地化乱码或显示 key、事件不触发、MOD 互相覆盖等问题。触发词：群星MOD、Stellaris mod、mod制作、paradox mod、事件脚本、descriptor.mod、localisation、gfx、gui、trigger、effect、scope、飞升、法令、起源、舰船、天灾、修正、创意工坊。
agent_created: true
---

# Stellaris MOD 制作

## 概览

本技能封装 Stellaris（群星）MOD 的完整制作链路：从建立 MOD 骨架、编写定义与事件脚本、本地化、贴图界面，到调试、校验、打包与发布。Stellaris 的 MOD 本质上是一套**镜像游戏安装目录结构的文本脚本 + 资源文件**，引擎按目录名加载，因此「文件放对目录」和「语法正确」比任何编程技巧都重要。

## 何时使用

- 用户要求新建一个 Stellaris MOD，或往现有 MOD 里加内容（事件、科技、飞升、法令、起源、民政、舰船、建筑、区划、领袖、天灾等）。
- 用户给出 `.mod` / `descriptor.mod` / `.yml` / `.txt` / `.gfx` / `.gui` 文件要求解释或修改。
- 用户报告 MOD 不生效、事件不触发、文字显示成 `key_name`、图标缺失、游戏崩溃。
- 用户要发布到 Steam 创意工坊或做兼容性补丁。

## 硬性规则（先看这条，违反必出错）

1. **本地化文件必须是 UTF-8 **带 BOM**。** 纯 UTF-8（无 BOM）Stellaris 无法解析，中文会全部失效。文件名必须以 `_l_<语言>.yml` 结尾，首行必须是 `l_<语言>:`。语言代码：`english` / `simp_chinese` / `french` / `german` / `spanish` / `russian` / `polish` / `japanese` / `korean` / `braz_por`。
2. **目录名镜像游戏原版**：`common/`、`events/`、`gfx/`、`interface/`、`localisation/`（注意是英式 s，不是 z）、`flags/`、`fonts/`、`map/`、`music/`、`prescripted_countries/`、`sound/`。目录名写错 = 文件被完全忽略且不报错。
3. **MOD 必须有两个描述文件**：`…/mod/<名字>.mod`（含 `path`，供启动器定位）和 `…/mod/<名字>/descriptor.mod`（不含 `path`）。两者除 `path` 外内容一致。
4. **`path` 用正斜杠 `/`**，不要用反斜杠。
5. **新建文件优先于覆盖原版文件**。原版文件按 LIOS（Last In, Only Served，后加载的整个文件替换前者）或 FIOS（First In, Only Served，先加载的生效）处理，覆盖原版文件会与其他 MOD 直接冲突。
6. **`namespace` + 数字事件 ID**：事件 id 只能是 `namespace.数字`，**不能含字母**，且前导零会被截断（`x.003` == `x.3`）。
7. **`is_triggered_only = yes` 是默认最佳实践**：让事件只在被显式调用时触发，不参与每日轮询，能显著降低性能开销。
8. **不要用 tab 以外的缩进混排**（Paradox 脚本忽略缩进，但保持可读性）；花括号必须严格配对，注释用 `#`。

## 标准工作流

### 步骤 1｜确认游戏版本与目标

先确认用户游戏版本（`supported_version`，当前主流为 `v4.*`）。事件类型、部分字段在不同大版本间有变（例如 `pop_event` 在 v4.0 起改名为 `pop_group_event`）。版本不匹配时字段会被静默忽略。

### 步骤 2｜生成或定位 MOD 骨架

新 MOD 直接运行脚手架脚本：

```bash
python <skill>/scripts/scaffold_mod.py "MyModName" --version "v4.0.*" --tags Gameplay Events
```

脚本会在 `…/Documents/Paradox Interactive/Stellaris/mod/` 下创建 `<名字>.mod`、`<名字>/descriptor.mod` 与全部常用子目录。也可用 `--out <目录>` 指定任意位置（例如用户已有的 MOD 仓库根目录）。

已有 MOD：先读 `descriptor.mod` 与目录树，**不要重建**，只在既有结构上增删文件。

### 步骤 3｜按内容类型写入脚本

先查 `references/content-types.md` 找到对应目录与字段骨架，再动手。**每条新内容都需要三件套**：

1. 定义文件（放 `common/` 或 `events/`）—— 决定逻辑。
2. 本地化（放 `localisation/<语言>/xxx_l_<语言>.yml`）—— 决定显示文本。**忘了写 loc 就会在游戏里看到裸 key**。
3. 图标 / 贴图（放 `gfx/`）并在 `interface/*.gfx` 里注册 sprite —— 否则报 "Did not find an icon"。

### 步骤 4｜校验

写完先跑校验脚本：

```bash
python <skill>/scripts/validate_mod.py <MOD 根目录>
```

它会检查：描述文件字段完整性、yml 的 BOM 与首行、括号配对、事件 id 重复、`GFX_` sprite 引用是否已注册、本地化 key 是否缺失。**修复所有 ERROR 再进游戏**。

### 步骤 5｜游戏内测试与调试

见 `references/debugging-testing.md`。要点：启动参数加 `-debug_mode`，进游戏后用控制台 `debugtooltip` / `observe` / `event <id>` 验证；出错看 `…/Documents/Paradox Interactive/Stellaris/logs/error.log`（用 MOD 前缀搜索）。

### 步骤 6｜打包发布

打包成压缩包供创意工坊或 Paradox Mods 上传。发布前跑 `references/checklists.md` 中的发布清单。

## 脚本语言速记

Stellaris 脚本只有三种基本结构，其余全是字段：

```
# ① 作用域切换：花括号内的语句作用于该对象
owner = { ... }          # 切到拥有者
every_owned_planet = { ... }   # 遍历每个拥有的行星（效果用 every_/random_，触发器用 any_/count_）
root / prev / from / this      # 主作用域 / 上一级 / 调用来源 / 当前作用域

# ② 条件块（触发器）：返回 true/false，常用 AND OR NOT NOR NAND calc_true_if
trigger = { OR = { has_technology = tech_x has_country_flag = flag_y } }

# ③ 效果块：修改游戏状态，用 if/else_if + limit 做分支
immediate = { if = { limit = { is_ai = no } add_modifier = { modifier = my_mod months = 12 } } }
```

关键点：**同一段花括号在不同位置含义完全不同** —— 作为「切换」是作用域，作为「遍历」是迭代器。写法相同，语义由前缀（`every_` / `random_` / `any_` / `count_`）决定。

## 排查：内容被隐藏 / 校验不通过

### 预设国家（`prescripted_countries/`）在帝国设计器里不显示

游戏启动时逐个校验设计，**不通过的直接隐藏**，并在 `error.log` 留下：

```
[select_empire_design_view.cpp:714]: Hiding invalid prescripted empire design 'DOT_SR_humans1':
[select_empire_design_view.cpp:719]:     母星:
无效选择
```

区块名与设计器 UI 一一对应，逐条对照即可定位字段：

| 日志 | 本地化 key | 判定依据 |
|---|---|---|
| `母星: 无效选择` | `EMPIRE_DESIGN_INVALID_PLANET_CLASS` | `planet_class` 的 **`starting_planet = no`**（wiki：*Can players/AI start on this planet class?*）。注意 `initial = yes` 是另一件事：*Can this planet be used to spawn for custom species?* |
| `母星: $NAME$恒星系统初始化不可用。` | `EMPIRE_DESIGN_INVALID_INITIALIZER` | `initializer` 不存在 / 不被允许 |
| `政体&思潮: 无效的政体。` | `GAMESETUP_COUNTRY_GOVERNMENT_TYPE_INVALID` | `authority`/`government`/`civics`/`ethic` 组合不满足各自 `possible`（例：`gov_military_dictatorship` 要求 `is_dictatorial_authority` + `is_militarist`；`auth_dictatorial` 排除平权），**或用了 DLC 门控的国家开关** |
| `城市与房间: 所选舰船外观不可用。` | graphical culture 不可选 | 该外观的 `selectable = { has_xxx = yes }` 不成立（DLC 未拥有），见 `common/graphical_culture/00_graphical_culture.txt` |
| `起源: …需要DLCxxx` | 起源被 DLC 门控 | 原版写法 `playable = { OR = { has_ancrel = yes  host_has_dlc = Federations } }` |
| `英雄过往: 需要DLCxxx` | 领袖特质被 DLC 门控 | `trait_ruler_*` 等 |

排查手法：**对同一个字段做 A/B**（改一处、跑一次、对比日志），比读代码可靠得多。

### `dlc/` 里有文件夹 ≠ 拥有该 DLC

Stellaris 把**全部 DLC 资源随本体一起下发**（`dlc/dlcNNN_xxx/` 都有 `.dlc` + `.zip`），是否拥有只由 Steam 授权决定。因此：

- **不要**用「`dlc/` 有没有文件夹」判断拥有权，也**不要**用「某 DLC 的静态修正被加载了」判断（内容总是加载，只在运行时被触发器门控）。
- 最准的判据就是**日志本身**：报 `需要DLCxxx` 即未拥有。`dlc/dlcNNN_xxx/dlcNNN.dlc` 内含 `name` / `steam_id` / `pops_id`，可用来对上内部名。
- 想让「只在拥有 DLC 时才有意义」的设计干净消失，照抄原版：`playable = <scripted_trigger>`（如 `playable = has_nomads_dlc`，定义在 `common/scripted_triggers/`）。**不加这道闸，没买的玩家会看到一串「无效」报错**；原版自己的 `humans1`/`humans2` 用的是 `playable = empire_design_never`。
- 界面上带 `missing_dlc_overlay`（`GFX_government_locked_overlay`）的控件就是 DLC 锁定项。例：`interface/customize_species_editors.gui` 里政体区块的 `nomad_toggle`（游牧开关）—— 给国家模板写 `is_nomadic = yes` 而玩家没买 Nomads DLC，结果就是 `政体&思潮: 无效的政体。`

### 游牧（Nomads DLC）体系的坑

`pc_ark`（`common/planet_classes/06_planet_classes_nomads.txt`）是「方舟船体行星」：`district_set = nomad`、`starting_district = district_ark_city`、`single_build_queue = yes`、**`starting_planet = no`**。它只允许在**游牧帝国**里当母星 ⇒ 国家模板必须 `is_nomadic = yes` + `ship_size = science_arkship_tier_1`，而 `is_nomadic` 又受 Nomads DLC 门控。非游牧硬写 `pc_ark` ⇒ `母星: 无效选择`；补上 `is_nomadic` ⇒ 变成 `政体&思潮: 无效的政体`。**这是同一个缺失 DLC 的两副面孔。**

好消息：方舟城区划 `district_ark_city` 的可用性条件只是 `uses_district_set = nomad`（**不是** DLC 检查），所以**自定义的** `district_set = nomad` 星球类在没有 DLC 时也能建方舟城区划。要给非游牧帝国一个方舟式母星，最稳做法是**自己定义星球类**并写 `starting_planet = yes`，而不是借用 `pc_ark`。自定义星球类时 `district_set` 有两条路：
- **`district_set = nomad`**：白拿原版整套方舟区划（含 `slot_ark_reactor` / `slot_ark_basic` / `slot_ark_military` 这些 zone slot，缺了就会「区域造不了」）。代价是自己写的区划必须用 `uses_district_set = nomad` + 国家条件来收窄，否则会漏到原版游牧势力的方舟上。本项目星穹列车/罗浮/仙舟/黑塔都走这条。
- **自定义集合**（`district_set = pc_hunter_hub_set` 式，参考 `pc_hunter_hub`）：干净隔离，但方舟区划与它带来的 zone slot 全部拿不到，得自己补齐。
- 也要注意「方舟是船」：船体侧靠 `ship_sizes/*.txt` 里的 **`carries_colony = pc_X`** 决定殖民地用哪个星球类（原版没有 `planet_class` 字段可写）。改星球类名字时别漏这里。

### 游牧 ⇄ 恒星基地是**硬互斥**（拆脚本闸没用，别白干）

**实测结论（4.4.6 / 2026-09-20）**：把下面 3 道 `potential*` 闸**全拆开**后，建造船的「建造恒星基地」订单**能下达、进度能涨到 99%→100%，然后失败**（基地不生成，`error.log` 里没有任何相关报错）。所以根因在**状态层**、不在脚本层：`is_nomadic = yes` 是引擎级的国家状态，游牧帝国**不许宣称星系**，而恒星基地的唯一作用就是宣称星系。

原版是**两态互转**，本地化里写得明明白白：定居 ⇒ 无主星系里的驿站变恒星基地（`arkship_settle_empire_effects`）；启航 ⇒ 星系里的恒星基地变驿站（`nomad_embarkation_empire_effects`）。官方 Wiki 同样写死："most stations cannot be built by Nomadic empires, but logistic ships can build waystations"、"Waystations are how Nomadic empires exert influence over a system **without claiming it as theirs**"。

脚本层**一共只有这 3 道闸**（对 `common/` + `events/` + `prescripted_countries/` 全量 `grep -rn is_nomadic` 得到，没有第 4 道；`can_build_starbase_around` 只挡 `nomad_settling_in_progress`，所以订单才能开始 —— 这正是「到 100% 才失败」的来源）：

| 位置 | 被锁的东西 | 原写法 |
|---|---|---|
| `common/ship_sizes/00_ship_sizes.txt` → `constructor` | **建造船**（采矿站 / 研究站 / 观测站也全靠它） | `potential_country = { is_nomadic = no ... }` |
| `common/ship_sizes/00_starbases.txt` → `starbase_outpost` | 前哨站（基地 1 级；starport 以上无此锁，只靠科技） | `potential_country = { is_nomadic = no }` |
| `common/technology/00_eng_tech.txt` → `tech_starbase_1..5`、`tech_solar_panel_network`、`tech_space_defense_station_1` | 基地解锁/升级、太阳能板、防御平台 | `potential` + `starting_potential` = `{ is_nomadic = no }` |

游牧的官方替代品是 **`nomads_constructor` / `nomads_engineer_vessel`（后勤船）+ `waystation` 巨构**（`common/megastructures/30_nomad_waystation.txt`，`potential = { is_nomadic = yes }`），巨构 `starbase = starbase_level_waystation_1` → 生成 `starbase_waystation_1/2/3`（`common/ship_sizes/00_waystations.txt`：`is_space_station = yes`、`potential_construction` / `possible_construction = { always = no }` ⇒ **只能由巨构创建，永远不能由建造船造**）。

**结论：靠"拆 `potential` 闸门"永远做不成**（那只是让订单能下）。真要给游牧国家一个基地，四条路：

1. **驿站路线（游牧本命，零改造、立刻可用）**：游牧自带 `tech_waystation_1`（`start_tech = yes`，`potential` / `starting_potential = { is_nomadic = yes }`，并给 `country_starbase_capacity_add = 2`），用后勤船建航站巨构即可。驿站可升级（`starbase_level_waystation_1→2→3`，模块槽 2/4/8，`00_waystations.txt`），能装舰船厂 / 修理坞 / 资源 / 防御模块，相邻驿站自动连成"驿道"。这才是游牧的"恒星基地"。
2. **★ 运行时摘掉游牧身份（推荐；2026-09-20 找到，推翻"必须重写方舟"的旧结论）** —— 原版自己留了开关：

   ```paradox
   # common/scripted_effects/nomads_effects.txt:6
   # 调用方式： set_country_as_nomad_effect = { IS_NOMAD = yes|no }
   set_country_as_nomad_effect = {
       set_country_code_flags = { is_nomadic = $IS_NOMAD$ }
   }
   ```
   **`is_nomadic` 是"国家 code flag"，不是建局时写死的东西** ⇒ **可以在游戏中途改**，方舟不用重写。原版「定居」流程 `arkship_settle_planet_effect`（同文件 4870 行）第一步就是 `set_country_as_nomad_effect = { IS_NOMAD = no }`。
   给玩家一个决策即可，效果照抄原版定居那几步：

   ```paradox
   owner = {
       set_country_as_nomad_effect = { IS_NOMAD = no }      # ★ 核心
       set_resource_converter = none                        # 作战储备 → 常规能量/矿物
       set_faction_properties = { needs_border_access = yes } # 游牧无视国界 → 恢复正常
       give_technology = { tech = tech_starbase_1 message = no }   # 以下 6 个 + 条件补 3/4
       # tech_starbase_2 / tech_space_defense_station_1 / tech_solar_panel_network
       # tech_colonization_1 / tech_mechanized_mining
       if = { limit = { has_technology = tech_waystation_2 } give_technology = { tech = tech_starbase_3 message = no } }
       if = { limit = { has_technology = tech_waystation_3 } give_technology = { tech = tech_starbase_4 message = no } }
       refresh_auto_generated_ship_designs = yes
   }
   ```
   **⚠️ 千万别直接调 `arkship_settle_planet_effect`** —— 它会 `transfer_carrier ... destroy_colony` + `destroy_fleet`，**把方舟彻底销毁变成行星**，玩家的"列车"就没了。要保留方舟只能自己写上面那一小段。
   已落地实例：`common/decisions/zz_Astral_Express_dock.txt`（星穹列车「列车靠站」，`owned_planets_only = yes` + `potential = { owner = { has_origin = ... is_nomadic = yes } }`，单向）。
   反向（定居 → 游牧）原版走 `decision_nomad_embarkation`（`can_embark_trigger`：`is_nomadic = no` + 适应/多面性传统完成），会调 `convert_starbases_into_waystation_effect` 把恒星基地换回驿站。
3. **改预设 `is_nomadic = no`**：见下方警告，方舟会废，不推荐。
4. **★ 用脚本效果直接"按"一个恒星基地（2026-09-21 新增，**待游戏内实测**）** —— 不走建造订单，直接调效果：

   ```paradox
   # galactic_object（星系）作用域；root = 国家
   set_surveyed = { surveyed = yes surveyor = root }          # 顺带把星系标成已调查
   if = {
       limit = { NOT = { any_starbase_in_system = { always = yes } } }   # 幂等
       create_starbase = { owner = root  size = starbase_outpost }
   }
   ```

   `create_starbase`（`effects.log` 原文：*"Creates a starbase in orbit of the star of the scoped galactic object"*，
   作用域 `planet` / `galactic_object`）原版自己在用（`events/shroud_events.txt:18465`、
   `events/origin_events_5.txt:1018`、`events/synthetic_dawn_events.txt:1967`），
   **不经过「建造订单 → 检查能否拥有星系」那条链路**，所以**有可能**绕过游牧的状态层限制。
   已落地在 `events/DOTGI_teyvat_events.txt` 开局事件（发现裂隙时顺带建前哨站），
   **尚未游戏内验证**；若实测也失败，就回到第 2 条（摘掉游牧身份）。
   注意原版**没有** `has_starbase` 触发器，判"星系里有没有基地"要用 `any_starbase_in_system = { always = yes }`。

**`custom_starbase` 救不了游牧（2026-09-20 排除，别再试）**：`country_types` 的 `custom_starbase = <舰体>` 注释是 *"if this is set, country will defined ship size for constructed starbases instead of building outposts"*，即**只决定"基地用哪个舰体"**（原版使用者：`starbase_marauder` / `starbase_caravaneer` / `starbase_swarm` / `starbase_exd` / `starbase_ai` / `starbase_gatebuilders` / `starbase_synth_queen`）。它**不改变"拥有星系"这一步**，所以对游牧无效；而且它是**国家类型级**字段，普通帝国共用公共 `default` 类型，加上去会波及所有国家。配套还要写 `common/ship_sizes/` 里的舰体 + `common/starbase_levels/` 里 `ship_size = <舰体>` 的等级块（三件套），成本高、方向错。

<details>
<summary>（仅存档，别再照做）上一版"拆 3 道闸"的写法</summary>

开口子的模式是 `OR = { is_nomadic = no has_origin = <你的起源> }`，三处都改、缺一个就退化成"能造前哨站但升不了级"或"建造船不出现"；改完还要用开局事件 `give_technology` 补 `tech_starbase_1/2`。**实测这只让订单能开始，到 100% 仍失败**——留着是为了以后遇到类似"potential 全放行却做不成"的局面时，能认出这就是"状态层互斥"的信号。
</details>

**必须整块复制原版再改一处**，不能只写要改的那几行 —— 这些块引用了**文件级 `@变量`**：`00_starbases.txt` 顶部的 `@build_block_radius_starbase` / `@starbase_formation_priority` 是文件局部的，新文件里要自己再定义一次；而 `@outpost_*` / `@construction_*` / `@tierNcostN` / `@ai_starbase_types_factor` 定义在 `common/scripted_variables/`，是全局的，直接可用。

**别用「把预设里的 `is_nomadic` 改成 no」来绕**：方舟的全套 `common/starbase_buildings/00_arkship_*.txt`（写死 `is_nomadic = yes`）会跟着失效，方舟自己就废了。

## 新增区划 / 岗位（4.4.6 Zones 体系）

区划 = **定义 + 图标 + 本地化**；岗位同理。完整骨架见 `references/content-types.md#区划-districts`。

### 区划容量（最容易踩的地方）

总容量 = `NUM_DISTRICTS_BASE`(=0) + 行星尺寸 × `NUM_DISTRICTS_FROM_PLANET_SIZE`(=1) + `planet_max_districts_add`（`common/defines/00_defines.txt`）。

- **不写 `is_uncapped`** ⇒ 无独立上限（文档：*If this trigger is empty it will be uncapped*），跟行星总池走。
- 写 `is_uncapped = { <trigger> }` ⇒ 引擎生成 `<区划名>_max_add` / `_max_mult`，由建筑 / 矿床往这两个键上累加（原版 `district_generator` 的写法）。
- 多个区划共享一个上限池：`shared_capacity_modifier = <池名>`。
- 判断「这个名字引擎认没认」的最快办法：跑一次游戏，在 `logs/script_documentation/modifiers.log` 里搜 `district_<名字>_max_add`。**游戏每次启动都会重刷 `script_documentation/`，这是最权威的实时反查源。**

### 岗位给产出，先确认资源合法

```
job_key = {                      # 定义名不带 job_ 前缀；修正名/图标名却都带
	category = specialist
	swappable_data = { default = { condition_string = RULER_JOB_TRIGGER building_icon = building_capital } }
	can_be_automated = no
	tags = { }                    # 空 tags 原版也在用（overlord_propagandist）
	possible_pre_triggers = { has_owner = yes is_being_purged = no is_being_assimilated = no is_sapient = yes }
	possible_precalc = can_fill_specialist_job     # 取值定义在 common/game_rules/00_rules.txt
	resources = { category = planet_jobs_specialist  produces = { ... } upkeep = { ... } }
	weight = { weight = 3000 }    # 越大越优先被填满
}
```

**「某资源能不能被某类岗位产出」别靠猜、别只翻 wiki**：引擎会为每个 `(经济类别, 资源)` 组合生成 `<类别>_<资源>_produces_mult`。在 `modifiers.log` 里搜这个键：
- 存在 ⇒ 该资源能在该类别下 `produces`（含 `influence`：`planet_jobs_specialist_influence_produces_mult` 确实存在 ⇒ 岗位能产影响力）。
- 不存在 ⇒ 大概率不合法。
- 顺带能从这份清单里**反推出全游戏可产出资源全集**（`advanced_logic` / `astral_threads` / `biomass` / `menace` 等 DLC 资源也在此列，给没买 DLC 的玩家写这些键要谨慎）。

给岗位：区划的 `planet_modifier = { job_<key>_add = 200 }`；岗位优先级用 `weight.weight` 竞争。

### 图标不用注册

`gfx/interface/icons/jobs/job_<岗位key>.dds` → `GFX_job_<岗位key>`；`gfx/interface/icons/districts/<区划名>.dds` → `GFX_<区划名>`。**拷一张现成 `.dds` 改名即可先用**，格式尺寸直接继承，不写任何 `.gfx`。

### 岗位本地化的 10 个 key（少一个就裸 key）

`job_<k>` / `job_<k>_plural` / `job_<k>_desc` / `job_<k>_icon`(=`"£job_<k>£"`) / `job_<k>_with_icon` / `job_<k>_plural_with_icon` / `mod_job_<k>_add` / `mod_job_<k>_per_pop` / `mod_job_<k>_per_pop_short`；区划 3 个：`<区划名>` / `_desc` / `_plural`。
`_per_pop_short` 里要写**字面 `\n`**，不是真换行。

### 改 `.yml` / `.txt` 必须保持编码与行尾

原版与多数 MOD 的脚本文件是 **UTF-8 BOM + CRLF**（个别纯 LF）。用脚本插入 / 追加时：读 `decode('utf-8-sig')` 并记住 BOM；内部统一 `\n`，写回前 `replace('\n', nl)`，再把 BOM 存回去。`Edit` 工具插入的是 `\n`，往 CRLF 文件里塞会得到混排行尾 —— 要稳就用脚本（本机现成：`C:\Users\XIANGZIYUAN\stellariswiki\append_txt.py`）。

### 批量做一套「肖像档案」（编号制，与 Herta_Space_Station / Belobog 同级）

大型 MOD 往往**只有一个 `species_class`**（本项目：`Star_Rail`），下面平级挂着若干 **`portrait_set`**——`Herta_Space_Station` / `Belobog` / `Xianzhou_Alliance` / `Penacony` / `Amphoreus` / `Astral_Express` / `Stellaron_Hunters` / `Interastral_Peace_Corporation`。这些在帝国设计器里表现为同一个物种类下的「肖像档案」，**共用同一批 `graphical_culture` / `move_pop_sound_effect` 等物种类设定**。想让一套新立绘（原神等）也这样接入，就照下面三处同步：

1. `gfx/portraits/portraits/<档案>.txt`
   `portraits = { <key> = { texturefile = "…/<key>.dds" } }` + `portrait_groups = { "<档案名>" = { … } }`。
   **`game_setup` / `species` / `pop_group` / `leader` / `ruler` 五个 scope 都要列全肖像**，只列一部分会导致该场景下选不到别的肖像（既有档案都是五个 scope 各抄一份完整清单）。
2. `common/portrait_sets/<文件>.txt`
   `<档案名> = { species_class = <物种类名> portraits = { <档案名> } }`
3. `common/portrait_categories/<文件>.txt` 里把 `<档案名>` 加进对应分类的 `sets` 列表 —— **漏了这一步档案就不出现在帝国设计器**（`species_classes` 已不能写 portraits，`portrait_categories` 才是设计器入口）。

⚠️ **别为每个档案新建 `species_class`**：那会让帝国设计器多出一个独立物种类，且丢掉物种档案上的 `graphical_culture`（本项目是 `DOT_SR_humanoid_01`）等设定，模型/城市外观都会错。

一键生成：`scripts/gen_portrait_archive.py`（见下表）。它按 `<prefix>_<三位数字>.dds` 扫描贴图目录、生成上述 1+2、可选同步 3 与本地化编号键。**贴图文件名里的空格和括号要先去干净**（`GI_Portrait (12).dds` → `genshin_012.dds`），带空格的路径在打包与解析时是隐患。

### 加一个具名角色当领袖（肖像 + 特质 + create_leader）——四件套

场景：给事件生成的舰船配一个有名字的指挥官（本项目实例：风魔龙 `DOT_SR_Dvalin.001` 造出 `Dvalin_General`，配原神·刻晴）。

1. **肖像贴图** `gfx/models/portraits/<组>/<id>.dds`
   规格必须和 MOD 现有一致 —— 本项目实测 **496×380 / DXT3 / 9 级 mip / 252256 字节**。
   转换：`python scripts/img2portrait_dds.py 输入.png 输出.dds --size 496x380 --anchor 0.12`
   （纯 Python + Pillow，脚本内自带 DXT3 编码与 mip 链；`--anchor` 是垂直裁切锚点，半身像取 0.1~0.15 偏上。）
   图片没到位时**先 cp 一张现有人物 dds 改名占位**，别让贴图缺失。
2. **注册肖像** `gfx/portraits/portraits/<物种类>.txt`
   `portraits = { <id> = { texturefile = "…" } }`，并把 `<id>` 加进对应 `portrait_groups` 的 `game_setup.add.portraits` 列表。列表在文件里通常出现 **5 次**（不同 scope），用脚本按行定位插入，别用整串替换。
3. **特质** `common/traits/*.txt`：本项目走内联脚本
   `inline_script = { script = trait/hsr_icons ICON = "GFX_xxx" CLASS = commander RARITY = paragon COUNCIL = yes TIER = 1 }` + `councilor_modifier` + `leader_class = { commander }` + `initial = no` `randomized = no`。图标要在 `interface/*.gfx` 里注册 `spriteType`。
4. **造人并上岗**（事件 `immediate` 内）：
   `create_species`（`portrait = <id>`、`immortal = yes`）→ `save_event_target_as` →
   `create_leader { class = commander species = event_target:<sp> name = "NAME_xxx" skill = 5 gender = female tier = leader_tier_legendary immortal = yes skip_background_generation = yes custom_description = … custom_catch_phrase = … hide_age = yes randomize_traits = no effect = { set_leader_flag = legendary_leader / leader_death_events_blocked / immune_to_negative_traits … remove_all_positive_traits = yes add_trait = <特质> save_global_event_target_as = … } }` →
   `event_target:<舰队> = { assign_leader = event_target:<领袖> }`
   ⚠️ 即使写了 `randomize_traits = no`，原版生成流程仍可能多塞一个特质（MOD 注释里叫「特质黑箱」），照惯例先 `remove_all_positive_traits = yes` 再 `add_trait`。

本地化 key：`NAME_xxx`、`<特质>`、`<特质>_desc`、`custom_description` / `custom_catch_phrase` 指向的 key。**yml 值里不能出现裸 `"`**，用 `「」` 代替，否则整行解析崩掉。

## 资源索引

| 文件 | 何时读 |
|------|--------|
| `references/mod-structure.md` | 建立骨架、描述文件字段、加载顺序、LIOS/FIOS 覆盖规则、目录职责总表 |
| `references/scripting.md` | 作用域 / 触发器 / 效果 / 变量 / 事件 / on_actions / scripted_effects 的详细语法 |
| `references/content-types.md` | 具体内容骨架：科技、飞升、法令、起源、民政、建筑、区划、舰船、领袖、天灾、巨构、考古、遗珍等 |
| `references/localisation-gfx.md` | 本地化格式、颜色码、方括号命令、gfx sprite、gui 布局、事件图、旗帜、立绘 |
| `references/advanced-systems.md` | **星界裂隙 / 局势（含双向进度条与倒计时）/ 异常现象 / 前 FTL 原始文明与 `achieve_ftl_effect` / 虫洞 bypass / 运行时生成孤立星系 / 各 on_action 的真实作用域**——这几个系统字段语义在 v4.x 改动过且**写错静默失效**，动手前必读 |
| `references/debugging-testing.md` | 日志位置、控制台命令、启动参数、CWTools、常见报错对照 |
| `references/checklists.md` | 发布前检查清单、性能与兼容性最佳实践 |
| `scripts/scaffold_mod.py` | 生成标准 MOD 骨架 |
| `scripts/validate_mod.py` | 校验 MOD 结构与语法错误 |
| `scripts/verify_district_zones.py` | 排查「区划列表为空 / 区域槽不解锁 / 造不了建筑」：静态比对 district ↔ zone_slot ↔ zone ↔ planet_class 的接线 |
| `scripts/verify_content_refs.py` | 排查**静默失效的引用**：`d_*` / `building_*` / `district_*` / `tech_*` / `trait_*` / `civic_*` / `origin_*` / `job_*` / `pc_*` / `ethic_*` / `GFX_*` / 贴图路径 / 本地化键 是否存在（game+mod 合并视图） |
| `scripts/img2portrait_dds.py` | 任意图片 → Stellaris 肖像 dds（496×380 / DXT3 / 全 mip 链），需 Pillow |
| `scripts/png2flag_dds.py` | 国家旗帜 dds 工具：`make` 一张图生成 顶层+`map/`+`small/` 三件套、`check` 体检（列出「PNG 改后缀伪装成 .dds」与缺失副本）、`repair` 批量修复。需 Pillow |
| `scripts/gen_portrait_archive.py` | 把一个贴图目录批量做成「肖像档案」：生成 `portraits` + `portrait_groups`（5 个 scope）、`portrait_sets` 条目，可选追加 `portrait_categories` 与本地化编号键 |

## 常见陷阱

- **本地化不生效**：99% 是编码不是 UTF-8 BOM，或文件名不以 `_l_<语言>` 结尾，或首行不是 `l_<语言>:`。
- **事件不触发**：`is_triggered_only = yes` 却没写调用方；或 `trigger` 条件永假；或 namespace 与 id 不匹配。
- **文字显示成 key**：本地化 key 拼写不一致（定义文件里的 key 与 yml 里的 key 必须逐字符相同）。
- **改了半天没反应**：改的是 Workshop 订阅的 MOD 副本而不是 `…/Documents/Paradox Interactive/Stellaris/mod/` 下的本地 MOD；或本地 MOD 与 Workshop 同名同 id 同时存在（游戏会拒绝加载）。
- **两个 MOD 打架**：双方都覆盖了同一个原版文件。解法是把各自内容放进独立新文件。
- **写 on_action 之前必须核对作用域**：把事件注册进某个 on_action 之前，先去原版
  `common/on_actions/00_on_actions.txt` 找到该 on_action 的注册表，**看它注册的事件是什么类型、用了哪些 scope
  关键字**，照着写。实测踩过的坑：`on_entering_system_first_time` 下 41 个原版事件 **100% 是 `ship_event`**
  （`ROOT = Ship` / `FROM = System` / `owner = Country`）；写成 `country_event` 会**静默不触发**。
- **局势的 `start_value` 是"进度条最小值/失败端"，不是起点**；`abort_trigger` 是**"满足即中止"**。
  细节与正确写法见 `references/advanced-systems.md`。
- **星球能进但区划列表是空的、区域造不了**：这类**静默失效**（`error.log` 里一片安静），几乎都是可用性条件永远为假。触发过两种：
  - 判定键引用了**已经不存在的集合**：例如为规避崩溃把某星球类的 `district_set` 换成原版 `nomad` 之后，区划里那句 `uses_district_set = 原来的自定义集合` 就永远匹配不上。**规避崩溃类的改动必须全局搜一遍旧键的所有引用**（`uses_district_set` / `unlock` / `potential` / `show_on_uncolonized`）。
  - **区划归属必须写 `uses_district_set = <星球类上那个 district_set 名>`，不要写 `is_planet_class = pc_X`。** 原版 147 个区划里 122 个用前者、**0 个**用后者；本项目实测：同一方舟上原版 `uses_district_set = nomad` 的 4 张卡正常，模组 `is_planet_class = pc_train` 的 6 张车厢一张不显示且无报错。`district_set`/`uses_district_set` 是一对，改一边必须全局搜另一边。

  - **本质（记住这条就不会走弯路）**：星球能列出哪些区划，靠「区划的 `uses_district_set`」与「星球类的 `district_set`」**字符串匹配**。`district_set = <string>` 是**任意字符串、不需要任何定义文件**（原版注释：*"Use any string here, for use in the uses_district_set trigger for easy compatibility"*）。只写 `is_planet_class` 的区划**永远进不了建造列表**（本项目 6 张车厢实测一张不显示且无报错，唯一能看到的那张是 `starting_district` 预建的）。
  - **「让某星球类别用原版那一套区划」的正解 = 直接换 `district_set`**，两步：① 星球类 `district_set = nomad` → `district_set = <自己的集合名>`；② 自己要保留的区划把 `potential` / `show_on_uncolonized` 改成 `uses_district_set = <同一个名字>`。**不要去复制原版区划再加 `NOT = { is_planet_class = ... }` 排除** —— 600 行、难维护、还容易漏改。
  - 换集合前的连带检查（本项目已验证）：原版 **zone / zone_sets / building / starbase_building 全都不读 `uses_district_set`**，所以区域和建筑不受影响；只需检查 MOD 自己的 `common/zone_slots/*.txt` 里 `unlock` 是否还匹配（本项目的 `slot_pc_herta` 同时写了 `uses_district_set = nomad` 和 `is_planet_class = pc_train`，后者能兜住）。
  - 三层必须打通：**星球类有区划 → 区划出现在列表 → 区划引用的每个 zone_slot 在该星球类上 unlock → 槽位里的 zone 允许该建筑**。缺一层就是空的。用 `scripts/verify_district_zones.py` 一次性查完。
- **`is_capped_by_modifier` 写进 district 会报错**：它是 **zone 专属键**，写在 `common/districts/*.txt` 里会刷一屏 `Unexpected token: is_capped_by_modifier`（虽然不一定直接崩，但说明该块的键合法范围搞混了）。
- **顺手清理旧日志再测**：`error.log` 是追加的，上次运行的报错会留在里面，容易误判「改了没用」。排查前先确认日志时间戳，或在改完后清空再跑一次。
