# 群星（Stellaris）MOD 制作技能 · 完整手册

> 本文件由 `stellaris-modding` 技能的全部内容合并而成，共四部分：
> **第一部分** 技能主文件（SKILL.md）、**第二部分** 七个参考文档、**第三部分** 脚手架脚本（scaffold_mod.py）、**附录** 参考来源。
> 内容整理自 stellaris.paradoxwikis.com 官方 MOD 文档体系（2025–2026 年快照）。

---

## 目录

- **第一部分 技能主文件（SKILL.md）**
  - 参考文件索引
  - 一、开工前必做
  - 二、搭建 MOD 骨架
  - 三、编写内容（通用流程）
  - 四、验证（交付前必须）
  - 五、交付
  - 六、常见任务速查
- **第二部分 参考文档**
  - 2.1 MOD 结构与覆盖规则（mod-structure.md）
  - 2.2 脚本语言（scripting.md）
  - 2.3 事件与 on_actions（events.md）
  - 2.4 内容类型（content-types.md）
  - 2.5 本地化（localisation.md）
  - 2.6 图形与界面资源（media-ui.md）
  - 2.7 工具、调试、测试与发布（tools-debug.md）
- **第三部分 脚手架脚本（scaffold_mod.py）**
- **附录 参考来源**

---

# 第一部分 技能主文件（SKILL.md）

## Frontmatter

```yaml
---
name: stellaris-modding
description: "制作《群星》(Stellaris, Paradox 游戏) MOD 的全流程技能。当用户要求创建、修改、分析或审查群星 MOD 时使用，包括：新建 MOD（科技/建筑/国民理念/起源/事件/异常/决策/法令/传统/特质/职业/星系/预设帝国等）、编写事件与脚本（作用域/触发器/效果/变量/修饰符/scripted effects）、本地化文本、图形与界面资源、调试（error.log/CWTools/控制台命令）、加载顺序与覆盖规则、上传 Steam Workshop。也可用于解释原版 MOD 代码、诊断 MOD 报错与不生效问题。Use for any Stellaris modding task including creating, editing, debugging, or analyzing Paradox Clausewitz script content."
---
```

## 技能正文

本技能把 stellaris.paradoxwikis.com 的 Modding 文档体系整理为可执行的工作流与参考手册。适用对象：创建新 MOD、为已有 MOD 增删内容、解读/修改原版脚本、排查 MOD 失效或报错。

### 参考文件索引（按需读取）

| 文件 | 内容 | 何时读取 |
|---|---|---|
| `references/mod-structure.md` | MOD 目录结构、descriptor、覆盖规则（FIOS/LIOS）、加载顺序、工坊发布 | 搭建 MOD 骨架、排查 MOD 不加载、需要覆盖原版时 |
| `references/scripting.md` | 脚本语言：作用域、触发器、效果、变量、修饰符、scripted 工具、性能 | 编写任何 .txt 脚本前必读（若未读过） |
| `references/events.md` | 事件类型与字段、选项、on_actions、最佳实践 | 创建事件/异常/考古/特殊项目时 |
| `references/content-types.md` | 科技/建筑/区划/决策/法令/政策/传统/特质/职业等定义结构 | 创建具体游戏内容时 |
| `references/localisation.md` | .yml 格式、括号命令、颜色码、`$`/`£` 码、风格指南 | 编写/翻译本地化时 |
| `references/media-ui.md` | gfx、图标、界面、旗帜、字体、音乐、声音 | 需要图片/图标/UI 资源时 |
| `references/tools-debug.md` | 工具链、控制台命令、日志、测试、故障排查、发布 | 测试、查错、上传时 |

### 一、开工前必做

1. **确认目标**：用户想做什么类型的 MOD（新内容 / 修改数值 / 事件剧情 / 图形 UI / 大改）。范围决定文件布局。
2. **确认版本**：目标游戏版本（如 v3.14.*）；`supported_version` 用通配符 `*` 结尾。
3. **检查现场**：若用户提供 MOD 文件/路径，先读取其 descriptor.mod 与目录结构再动手；只改被点名范围。

### 二、搭建 MOD 骨架

首选运行脚手架脚本（自动生成标准目录 + descriptor + 各语言本地化模板）：

```bash
python3 <skill目录>/scripts/scaffold_mod.py "<MOD名>" \
  [--mod-dir <本地MOD目录>] [--supported-version v3.14.*] [--tags "Graphics Economy"]
```

- `--mod-dir` 默认指向当前系统 Paradox Stellaris 本地 MOD 目录（Windows/macOS/Linux 自动识别）。
- 手工搭建时按 2.1 节第 2/3/4 小节：外层 `<name>.mod`（含 `path`）+ 根文件夹内 `descriptor.mod`（不含 `path`）。
- 不修改游戏安装目录文件；所有内容放 MOD 文件夹。

### 三、编写内容（通用流程）

1. 根据内容类型读取 2.4 节（content-types.md）找到对应结构（科技/建筑/国民理念等）。
2. 文件命名：`NN_<mod前缀>_<类型>.txt`，避免覆盖原版文件（除确需覆盖时）。
3. 脚本语法对照 2.2 节（scripting.md）：作用域、触发器、效果、变量。
4. 写事件时对照 2.3 节（events.md）：**所有事件加 `is_triggered_only = yes`**（除非确需轮询）；事件文件首行 `namespace = xxx`。
5. 每个新键补本地化（2.5 节）：至少英文；`.yml` 用 **UTF-8 with BOM**，首行 `l_english:`。
6. 需要图标/图片：按 2.6 节放置 .dds 并注册 sprite。
7. 尽量复用 `scripted_effects` / `scripted_triggers` / `script_values` / `inline_scripts`，减少重复代码。

### 四、验证（交付前必须）

1. **CWTools 校验**：有 VSC 环境时提示用户开启；否则人工检查括号配对、键名、本地化缺失。
2. **日志检查**：让用户启动游戏加载 MOD 后，检查 `logs/error.log` 中与 MOD 前缀相关的条目（如 "Did not find an icon"、"Object key already exists"）。
3. **控制台实测**：用 `debugtooltip` 悬停查看旗标/变量；`run test.txt` 直接执行脚本验证效果；`observe` 长挂机测试事件链；`script_profiler` 查性能。
4. **本地化检查**：`toggle_string_id` + `switchlanguage` 检查键是否齐全。
5. 对照 2.7 节第 7 小节检查清单逐项过。

### 五、交付

- 交付产物：MOD 文件夹路径 + 关键文件清单（descriptor、新增内容文件、本地化、图标），以及安装方法（复制到本地 MOD 目录或用启动器创建后覆盖）。
- 若用户要发布：给出工坊上传步骤（2.1 节第 9 小节）与缩略图要求（thumbnail.png，512×512，<1MB）。
- 说明已验证项与仍存在的风险（如覆盖规则依赖版本、DLC 依赖等）。

### 六、常见任务速查

- **做一个新国民理念/起源** → 2.4 节 §1；图标放 `gfx/interface/icons/governments/civics/<key>.dds`（28×28）。
- **新科技** → 2.4 节 §5；注意 `area/tier/category/prerequisites/weight`；LIOS 可覆盖。
- **新事件 + 弹窗** → 2.3 节；`country_event` + `title/desc/picture/option`；用 on_action 或事件调用触发。
- **改数值（Defines）** → `common/defines/<自定义名>.txt`，必须含所在块名（如 `NGameplay = { … }`），不能叫 00_defines.txt。
- **覆盖原版文本** → `localisation/replace/` 文件夹。
- **覆盖原版事件** → 文件名加 `!!` 前缀。
- **MOD 不加载/冲突** → 2.1 节 §7-8、2.7 节 §5。
- **给已有 MOD 加内容** → 先读 descriptor 和现有文件结构，沿用其前缀与命名风格。

---

# 第二部分 参考文档

## 2.1 MOD 结构与覆盖规则（mod-structure.md）

来源：stellaris.paradoxwikis.com/Modding 与 Modding_tutorial。本节介绍 MOD 的存放位置、目录结构、descriptor 文件、覆盖规则、加载顺序与发布。

### 2.1.1 MOD 文件夹位置

| 系统 | 本地 MOD 路径 |
|---|---|
| Linux | `~/.local/share/Paradox Interactive/Stellaris/mod` |
| Windows | `…\Documents\Paradox Interactive\Stellaris\mod` |
| macOS | `~/Documents/Paradox Interactive/Stellaris/mod` |

- Steam 创意工坊 MOD 存放在 `…\SteamLibrary\SteamApps\workshop\content\281990`（按 Workshop ID 命名）。
- Paradox Mods 下载的 MOD 存放在本地 MOD 目录，名为 `PDX_*MOD_ID*`。
- 日志目录在本地 MOD 目录的旁边：`…/Paradox Interactive/Stellaris/logs`（error.log、game.log）。

**黄金规则：永远不要直接修改游戏安装目录里的文件**（Steam 目录 `steamapps\common\Stellaris`），文件可能被更新无警告覆盖。任何修改都应放进一个 MOD 文件夹。

### 2.1.2 必需的目录结构

每个本地 MOD 由两部分组成：

```
<mod_dir>/<modname>.mod        # 启动器描述文件（含 path=）
<mod_dir>/<modname>/           # MOD 根文件夹（镜像游戏安装目录结构）
    descriptor.mod             # 2.4 之后启动器优先读取的描述文件（不含 path=）
    thumbnail.png              # 缩略图（2.4 后必须叫这个名字）
    common/ events/ localisation/ gfx/ interface/ ...   # 内容
```

- 文件夹与文件名在 macOS / Linux 上区分大小写。
- 用 UTF-8 编码 .mod 和脚本文件；本地化与名字列表文件必须用 **UTF-8 with BOM**。
- 缩进使用 1 个制表符（原版习惯），注释以 `#` 开头。

### 2.1.3 descriptor 文件字段

`modname.mod` 与 `descriptor.mod` 结构相同（类似 Valve Data Format）：

| 字段 | 必需 | 说明 | 示例 |
|---|---|---|---|
| `name` | 是 | MOD 显示名 | `name="My Stellaris Mod"` |
| `path` | 外层 .mod 必需；descriptor.mod 中忽略 | 指向 MOD 根文件夹，绝对路径或相对 Stellaris 目录；**必须用 `/` 正斜杠** | `path="mod/MyStellarisMod"` |
| `dependencies` | 否 | 声明在哪些 MOD 之后加载（用于子 MOD / 兼容补丁） | `dependencies={ "othermod" }` |
| `picture` | 否 | 工坊缩略图；2.4 后必须固定为 `thumbnail.png` | `picture="thumbnail.png"` |
| `tags` | 否 | 工坊标签，最多 10 个，含空格要加引号；使用预定义标签否则可能无法上传 Paradox Mods | `tags={ "Graphics" "Economy" }` |
| `version` | 否 | MOD 自身版本（任意字符串，显示用） | `version="v4.5"` |
| `supported_version` | 推荐 | 支持的**游戏**版本；末位可用 `*` 通配 | `supported_version="v3.14.*"` |
| `remote_file_id` | 否 | 启动器自动写入的工坊 ID，忽略 | `remote_file_id="1234567890"` |

```text
name="SomeMod"
path="mod/SomeMod"
dependencies={ "othermod" }
tags={ "Graphics" "Economy" "Overhaul" }
picture="thumbnail.png"
supported_version="v3.14.*"
```

### 2.1.4 创建 MOD

两种方式：

1. **启动器创建**：启动器 → Mods 标签页 → Mod Tools → Create a Mod → 填写信息 → 自动生成目录。创建成功后在新窗口可上传/更新。
2. **手动创建**：
   - 在本地 MOD 目录放 `<modname>.mod`（含 path）；
   - 创建 `<modname>/` 根文件夹，内含 `descriptor.mod`（不含 path）。
   - 提示：可在资源管理器地址栏直接粘贴 `%USERPROFILE%\Documents\Paradox Interactive\Stellaris\mod\`。

### 2.1.5 缩略图

- 尺寸至少 512×512，文件 < 1MB，否则无法上传。
- 2.4 后必须命名为 `thumbnail.png`（PNG/JPEG 均支持，但 2.4 启动器要求 PNG）。
- 更新流程：关闭启动器 → 确认 `picture="thumbnail.png"` → 放入图片 → 启动启动器并更新 MOD。

### 2.1.6 游戏目录结构与常见内容文件夹

MOD 必须镜像游戏安装目录结构（`SteamLibrary\steamapps\common\Stellaris\`）。最常改动的：

| 目录 | 内容 |
|---|---|
| `common/` | 大部分游戏数据与规则（科技、建筑、决策、法令、特质、事件触发注册等） |
| `events/` | 事件定义（含 namespace） |
| `localisation/` + `localisation_synced/` | 玩家可见文本（.yml） |
| `gfx/` | 图形资源（图标、事件图、旗帜、模型） |
| `interface/` | UI 定义（.gui 视觉逻辑、.gfx 图像-变量映射） |
| `flags/` | 旗帜图片（.dds）与 `colors.txt` |
| `fonts/` | `fonts.asset` 字体设置 |
| `map/` | 星系设置（galaxy、setup_scenarios） |
| `music/` | 音乐（.ogg、songs.asset） |
| `prescripted_countries/` | 预设国家（.txt） |
| `sound/` | 声音（.asset、.wav） |

`common/` 下的具体子目录（科技/建筑/决策等）及覆盖方式详见 2.4 节。

### 2.1.7 覆盖规则（Overwrite & Load Order）

同名键在不同文件中的处理方式由"加载顺序"决定。文件按**文件名 ASCII 码顺序**加载；同名文件按启动器显示顺序。

- **FIOS（First In, Only Served）**：第一个加载的生效，后续同名键报错被忽略。事件文件即 FIOS。
- **LIOS（Last In, Only Served）**：最后一个加载的生效，可覆盖原版（最常见，如科技、建筑、决策、法令、国民理念）。
- **DUPL（Duplicates）**：允许重复存在（如特质 traits、名字列表 name_lists 必须整个文件替换）。
- **NO**：无法单独覆盖，只能整文件替换。

常见文件的覆盖方式（摘自 wiki 覆盖表，随版本可能有变）：

| common/ 下文件 | 覆盖方式 | 说明 |
|---|---|---|
| anomalies | LIOS | 错误日志显示 "Object key already exists" |
| armies / buildings / districts / pop_jobs | LIOS (v3.3+) | v3.3 前单独覆盖会破坏自动生成的修饰符 |
| component_templates | FIOS | 舰船组件 |
| defines | LIOS | 必须连同所在的块名一起写，如 `NGameplay = { POLICY_YEARS = 10 }` |
| decisions / edicts / policies / technologies | LIOS | 科技若缺少 potential 块会继承被覆盖科技的 potential |
| ethics | LIOS | 建议整文件覆盖（多个 ethics 文件会导致自动生成损坏） |
| event_chains | FIOS | |
| governments / civics | LIOS | authorities 为 FIOS |
| on_actions | 不能修改已有条目 | 新条目会与同名条目合并；加载顺序从上到下 |
| scripted_effects / scripted_triggers | LIOS | |
| scripted_loc | FIOS | 可用 `name = key` 覆盖 |
| section_templates | 不能覆盖 | 已用舰船会删除 |
| traits | 整文件覆盖 ONLY | |
| name_lists | DUPL | 需整个文件替换 |

**事件覆盖**：事件是 FIOS，要覆盖原版事件且不整文件替换时，文件名必须按 UTF-8 顺序排在原版之后，通常给文件名加 `!!` 前缀，如 `!!vanilla_override_event.txt`。

**本地化覆盖**：本地化是 LIOS。在 `localisation/replace/` 文件夹中的文件在所有本地化之后加载，按 key 覆盖（推荐做法）。

### 2.1.8 MOD 加载顺序（Launcher Load Order）

- 列表顶部的 MOD 先加载；下方的 MOD 通常可覆盖上方（若允许）。
- 以 `~` 开头的 MOD 排在列表最顶部；以 `!` 开头的排向底部。
- 兼容补丁放在其所修补的 MOD 之下；子 MOD 放在主 MOD 之下。
- 推荐的通用顺序：非官方补丁 → 玩法 MOD → 子 MOD/补丁 → UI MOD → UI 补丁 → 通用补丁。
- 多人在线要求所有玩家 MOD 列表与顺序一致。

### 2.1.9 上传与更新（Steam Workshop / Paradox Mods）

- 启动器 Mod Tools → Upload a Mod → 选择 MOD → 选择站点 → 填描述 → Upload。
- 上传时填写的描述会**替换**工坊页面现有描述（\*号提示）。
- 若本地同时存在已上传版本对应的 .mod 文件，订阅的上传版本可能无法工作。
- 遵循 "Rules for User Made Mods and Edits of PDS games" 与 EULA：使用 DLC 独占特性的 MOD 必须锁定在 DLC 之后（如 Nemesis 的间谍行动需保留 Nemesis 检查）。

---

## 2.2 脚本语言（scripting.md）

来源：stellaris.paradoxwikis.com/Dynamic_modding、Scopes、Variables、Conditions、Effects、Modifiers。
这是 Paradox Clausewitz 引擎的脚本语言：`键 = 值`，用 `{}` 组织块，`#` 注释。

### 2.2.1 语言总览

- 脚本语言不区分"基础语法"与"游戏特定结构"：`switch` 流程控制与 `any_playable_country` 迭代同属"触发器/条件"；`create_rebels` 与 `while` 同属"效果"。
- `=` 同时用于布尔比较、赋值、作用域切换、触发条件与激活效果：

```
capital_scope = {                        # 切换到国家首都星球的作用域
	every_deposit = {                    # 遍历星球上每个资源点
		limit = {                        # 检查条件
			category = deposit_cat_blockers
		}
		remove_deposit = yes             # 激活效果
	} }
```

- 数值可用 `@变量名` 引用（文件内或 scripted_variables 全局）；数学表达式可用 `@[...]` 内联（见下）。

### 2.2.2 作用域（Scopes）

大多数游戏对象都提供一个作用域。作用域写在 `<scope_type> = { }` 中，块内脚本针对该对象执行，例如 `pop = { unemploy_pop = yes }`。

#### 系统作用域

| 关键字 | 含义 |
|---|---|
| `this` | 当前作用域 |
| `prev` / `prevprev` …（最多 4 个） | 上一个作用域（可重复到 prevprevprevprev） |
| `from` / `fromfrom` …（最多 4 个） | 调用当前脚本的源头作用域（如事件链中被调用方的上层） |
| `root` | 脚本的主作用域（事件触发所在对象）；在 scripted effects/triggers 中 root 不一定等于 this |

on_action 常覆盖这些作用域：例如 `on_ship_disabled` 中 this=被摧毁的船，from=摧毁它的船。原版 `00_on_actions.txt` 注释有详细说明。

#### 作用域切换（Scope Change）

- 用 `owner = { … }`、`capital_scope = { … }` 等关系键切换（关系表见 wiki Scopes 页；常见：country 的 `owner / controller / overlord / subject / leader / ruler / capital_scope / home_planet / species / owner_species / alliance / federation`；planet 的 `solar_system / owner / controller / starbase / sector / star / orbit`；pop 的 `owner / planet / home_planet / species`）。
- **点链式**：`owner.capital_scope.solar_system = { … }` 等价于 `owner = { capital_scope = { solar_system = { … } } }`（不产生新 prev）。
- **exists 检查**：切换到可能不存在的对象前先检查，否则脚本失败并写入 error.log：

```
planet = { exists = owner owner = { … } }
```

- 条件迭代 `any_xxx = { … }` 与效果迭代 `every_xxx / random_xxx = { … }` 会隐式切换作用域：花括号内脚本在子对象作用域执行。

#### 事件目标（Event Targets）

- `save_event_target_as = <name>`（namespace 内可用）或 `save_global_event_target_as = <name>`（全局）。
- 引用：`event_target:<name> = { … }`；本地化中直接写 `[<name>.GetName]`。
- 用完清除：`clear_global_event_target = <name>`。
- 支持动态目标名（v3.5+）：`save_event_target_as = something@root`，检查用 `event_target:something@root`。

#### 常用作用域类型

country（帝国/国家）、sector、galactic_object（星系）、megastructure、ambient_object（兴趣点）、planet（含星球/恒星/小行星/居住站/环世界，凡是 pop 能住的就是）、deposit、army、pop、pop_faction、species、leader、fleet、ship、starbase、war、federation、first_contact、espionage_operation、situation、archaeological_site、global。
判断当前类型：`is_scope_type = <type>`。

### 2.2.3 条件 / 触发器（Conditions / Triggers）

- 返回 yes/no 的语句，必须在一个作用域内求值。
- 逻辑组合：`AND = { }`（默认同块并列即 AND）、`OR = { }`、`NOT = { }`、`NOR = { }`。
- 数值比较：`num_pops > 10`、`years_passed < 50`（years_passed 总是全局作用域）。
- 迭代条件 `any_xxx = { … }`：只要存在任一匹配对象即返回 yes，块内脚本在子作用域执行。带 `count` 的如 `count_owned_planet = { limit = { num_pops > 10 } }` 返回数量。
- 常用：`has_ethic / has_civic / has_authority / has_technology / has_country_flag / has_global_flag / is_planet_class / is_scope_type / num_pops / exists / is_variable_set / check_variable / check_variable_arithmetic / has_communications / is_hostile / is_ship_class / has_trait / has_owner / is_ai`。
- **pre_triggers**（planet/pop/system/starbase/leader 事件专用）：事件触发前快速排除的"快速触发器"，性能关键。如：

```
pre_triggers = {
	has_owner = yes
	is_capital = no
	is_occupied_flag = no
}
```

### 2.2.4 效果（Effects / Commands）

- 改变游戏状态的语句，必须在一个作用域内执行。
- 迭代效果：`every_xxx = { … }` 对全部对象执行；`random_xxx = { … }` 对随机一个对象执行；可用 `limit = { … }` 限定范围。例如 `every_owned_planet = { limit = { is_planet_class = pc_continental } … }`。
- 流程控制：`if = { limit = { … } … }` / `else = { … }`、`while = { count = N … }`、`switch = { trigger = … }`、`random_list = { 100 = { … } 50 = { … } }`（加权随机执行）。
- 常用效果：`set_<scope>_flag / remove_<scope>_flag / set_timed_<scope>_flag = { flag = xxx days = N }`、`add_resource = { energy = 100 }`、`add_monthly_resource_mult = { resource = unity value = 1 }`、`set_variable / change_variable`、`create_fleet / create_ship / create_leader / create_army`、`delete_fleet = { target = this kill_leader = no }`、`set_location = { target = … }`、`assign_leader = last_created_leader`、`add_modifier = { modifier = xxx days = 360 multiplier = N }`、`fire_event = { id = xxx days = N random = N }`（或 `country_event = { id = … }`）、`set_owner = prev`、`shift_ethic`、`random_rim_system = { … }`、`set_species_homeworld`、`log = "text"`（写 game.log）、`save_event_target_as`、`trigger_event` 等。
- 完整列表见 wiki Effects 页与社区整理的 "List of Stellaris triggers, modifiers and effects"（GitHub）。

### 2.2.5 变量（Variables）

变量绑定在作用域上并持久存在。作用域：megastructure planet country ship pop fleet galactic_object leader army ambient_object species pop_faction war federation starbase deposit sector archaeological_site first_contact spy_network espionage_operation espionage_asset。

- 设置：`set_variable = { which = star_temperature value = @G2V_star_temperature }`
- 运算：`change_variable / subtract_variable / multiply_variable / divide_variable / modulo_variable = { which = <var> value = <数值|变量|作用域.变量|trigger:xx> }`
- 清零：`clear_variable = <string>`
- 检查：`check_variable = { which = <var> value <=> <…> }`；带运算的检查 `check_variable_arithmetic = { which = <var> add = 5 value > 10 }`；`is_variable_set = <var>`（变量未初始化时游戏会报错，先检查）。
- 复制：v3.1+ 用点作用域 `set_variable = { which = var1 value = owner.capital_scope.my_var }`。
- 导出：`export_trigger_value_to_variable = { trigger = fleet_power variable = x rounded = yes }`、`export_modifier_to_variable = { modifier = pop_growth_speed_reduction variable = x }`、`export_resource_income_to_variable = { resource = energy variable = x }`、`export_resource_stockpile_to_variable = { … }`、`get_galaxy_setup_value = { which = x setting = num_empires }`、`set_variable_to_random_value = { which = x min = -100 max = 100 rounded = yes }`（v3.6+）。
- 取整：`round_variable / floor_variable / ceiling_variable = <string>`、`round_variable_to_closest`。
- 使用位置：数值比较的触发器/效果、while 的 count、`add_modifier` 的 multiplier、资源表 `multiplier`、ai_chance 的 add/factor、有序脚本列表（按变量排序取国家）、本地化 `[This.my_var]`。

### 2.2.6 修饰符（Modifiers）

修饰符改变其所附着对象的属性（与 flag 不同——flag 只是存在/不存在）。写法：`modifier = { country_unity_produces_mult = 0.15 }`。`multiplier` 参数（v3.0+）可乘数值：`add_modifier = { modifier = soul_diet1 multiplier = 6 days = 360 }`。

#### Scripted Modifiers（v3.4+，common/scripted_modifiers/）

定义在 `common/scripted_modifiers/`，本身不做任何事，需要在别处手动赋予效果（如触发修饰符或资源表里 `mult = modifier:my_modifier`）。可用设置：

- `icon`：`gfx/interface/icons/modifiers` 下的文件名（不含 .dds），默认 `"mod_" + key`
- `percentage = yes/no`：是否显示为百分比
- `min_mult`、`max_decimals`（默认 2）、`good`（正数绿色/负数红色）、`neutral`（黄色）、`hidden`、`no_diff`、`cap_zero_to_one`、`localize_with_value_key`（loc 键需含 `$VALUE$`）
- `category`：修饰符读取层级。取值：all, pop, ship, station, fleet, country, army, leader, planet, component, pop_faction(勿用), deposit, megastructure, habitability, starbase, economic_unit, system, trade, federation, espionage。应设为层级最低的适用对象（country 最顶 → planet 中间 → pop 最底）。

```
pop_job_trade_mult = {
	icon = mod_trade_value_mult
	percentage = yes
	good = yes
	category = pop
}
```

### 2.2.7 Flags（布尔标记）

- 可用作用域：leader, planet, country, fleet, ship, species, pop, pop_faction, federation, galactic_object, megastructure, espionage_operation, global。
- 设置/清除：`set_<scope>_flag = <name>`、`set_timed_<scope>_flag = { flag = <name> days = <int> }`、`remove_<scope>_flag = <name>`。
- 检查：`has_<scope>_flag = <name>`。
- 动态旗标（v2.3+）：`@` + 作用域（leader/country/title），如 `from = { set_leader_flag = is_friend_of_@root }`，检查 `has_leader_flag = is_friend_of_@from`。

### 2.2.8 脚本化工具（Scripted Systems）

#### Scripted Effects（common/scripted_effects/）

一段可复用的效果块，可带参数（`$PARAM$` 占位）：

```
# 定义
example_scripted_effect = {
	while = {
		count = $COUNT$
		shift_ethic = ethic_$ETHIC$
	}
}
# 调用
example_scripted_effect = { ETHIC = materialist COUNT = 2 }
```

- 参数条件块：`[[homeworld] set_species_homeworld = event_target:tempHomeworld]`（仅当传入参数时执行）；`[[!homeworld] …]` 反向。默认值：`$STAGE|1$`。
- 内联数学 `@\[ … ]`：仅第一个被正确求值；可用 `+ - * /`；要用多个则拆成多个 scripted effect 互相调用，或把表达式放进引号作为参数传给其他效果。
- 括号本地化（v3.4+）：在 scripted effect 中 `variable_string = "\\[origin_imperial_species.GetAdj]"`（双反斜杠）或省略方括号。

#### Scripted Triggers（common/scripted_triggers/）

可复用条件块，同样支持参数。`example_scripted_trigger = { has_ethic = ethic_$ETHIC$ … }`，调用 `example_scripted_trigger = yes`；带参数的触发不能写成 `= no`，要放 `NOT = { … }` 里。

#### Scripted Localisation（common/scripted_loc/）

动态文本选择器：

```
defined_text = {
	name = GetAuthorityName
	text = { trigger = { has_authority = auth_democratic } localization_key = auth_democratic }
	text = { trigger = { has_authority = auth_oligarchic } localization_key = auth_oligarchic }
}
```

本地化中用 `[<scope>.GetAuthorityName]` 调用。scripted_loc 内部不能再使用括号命令（会原样打印）。

#### Scripted Variables（common/scripted_variables/）

跨文件共享的 `@` 变量：`@example = 2`，任意文件可用 `@example`。文件**必须以空行或注释行结尾**。文件内局部 `@` 变量只在本文件有效。

#### Script Values（common/script_values/，v3.3+）

按需计算的数值：`value:example_value`。支持 base/add/subtract/factor/mult/multiply/divide/modulo/round_to/max/min/pow/round/ceiling/floor/abs/square/square_root，以及 `modifier = {}`（按触发器条件应用）、`complex_trigger_modifier = { trigger = count_owned_planet trigger_scope = owner parameters = { limit = { num_pops > 10 } } mode = add mult = 5 }`。支持参数：`value:my_value|PARAM1|value1|`。**注意性能**——不要在频繁检查的触发器中滥用。

#### Inline Scripts（common/inline_scripts/，v3.5+）

一个文件一段脚本，`inline_script = "子路径/文件名"` 展开到调用处（可用于非 effect/trigger 块，如外交文本）。一个文件只能有一个 inline script；文件名（不含扩展名）用于引用；支持参数：

```
inline_script = {
	script = test_basic_policy
	KEY = test_1
	MODIFIER_A = evermore_science
}
```

注意事项：并非所有位置都支持 inline_script（报 "unexpected token" 即不支持）；不能在列表项内使用；注释行中的 `$PARAM$` 也会被替换（小心多行参数导致报错）。

### 2.2.9 性能与最佳实践（脚本层面）

- 默认事件每天对所有对象轮询；**务必给事件加 `is_triggered_only = yes`**，或使用 gatekeeper 事件（轮询但带快速失败触发器）+ on_action 触发。
- MTTH 性能差，原版已逐渐弃用，改用带随机延迟的事件（`country_event = { id = x days = 200 random = 100 }`）。
- pre_triggers 用于快速排除目标，避免完整 trigger 开销。
- 作用域切换前用 `exists` 检查；尽量用点链式减少嵌套。
- `script_profiler`（v3.5+）控制台命令可测量脚本性能。
- 复用代码优先用 scripted effects/triggers/inline scripts；大 MOD 建议用 Git 管理。

---

## 2.3 事件与 on_actions（events.md）

来源：stellaris.paradoxwikis.com/Event_modding、On_actions、Modding_tutorial。

### 2.3.1 事件类型

| 类型 | 作用域 | 说明 |
|---|---|---|
| `event` | 全局 | 整个游戏 |
| `country_event` | 国家 | 一个帝国 |
| `planet_event` | 星球 | |
| `fleet_event` | 舰队 | |
| `ship_event` | 舰船 | |
| `pop_faction_event` | 派系 | |
| `pop_group_event` | 人口组 | v4.0 起（原 pop_event） |
| `observer_event` | 观察者 | 仅开发用（observe 控制台命令） |
| `system_event` | 星系/银河对象 | v3.0+ |
| `starbase_event` | 星堡 | v3.0+ |
| `leader_event` | 领袖 | v3.0+ |
| `espionage_operation_event` | 间谍行动 | v3.0+ |
| `first_contact_event` | 首次接触 | v3.0+ |
| `situation_event` | 局势 | v3.3+ |
| `agreement_event` | 附庸协议 | v3.4+ |

### 2.3.2 基本结构

每个事件文件的**顶部必须有 `namespace = xxx`**。事件 ID = namespace.数字，如 `tutmod.1`。ID 不能含字母；前导 0 会被截断（namespace.003 = namespace.3）；namespace 最长约 100 字符。

```text
namespace = tutmod

country_event = {
	id = tutmod.1
	hide_window = yes          # 不弹窗（服务型事件必用）
	is_triggered_only = yes    # 只在被显式调用时触发（性能关键）
	fire_only_once = yes       # 成功触发一次后从检查列表移除
	trigger = {                # 条件；不满足则不触发
		NOT = { has_global_flag = tutmod_installed }
	}
	immediate = {              # 触发即刻执行的效果
		set_global_flag = tutmod_installed
	}
}
```

**字段速查**（可见事件）：

- `id`：唯一 ID（必填）
- `title = "loc_key"`：标题（可见事件必填）
- `desc = "loc_key"` 或 `desc = { text = … trigger = { … } }`：描述（可见事件必填）；多个 desc 随机选一，可条件化
- `picture = GFX_evt_xxx`：事件图（interface/xxx.gfx 定义）；可条件化 `picture = { picture = … trigger = { … } }`
- `location = from`：玩家可跳转的对象（如事件发生星球）
- `show_sound = event_xxx_sound`：音效
- `hide_window = yes`：不弹窗，title/desc 可省略
- `diplomatic = yes`：外交通信样式（首次接触用）；配合 `custom_gui / custom_gui_option / picture_event_data`
- `is_triggered_only = yes`：不轮询，必须由其他事件/效果/on_action 调用
- `fire_only_once = yes`：触发一次后不再检查
- `mean_time_to_happen = { months/days/years = N modifier = { factor = 0.1 … } }`：平均随机延迟（性能差，尽量别用）
- `pre_triggers = { … }`：快速排除触发器（planet/pop/system/starbase/leader 事件）
- `trigger = { … }`：触发条件
- `immediate = { … }`：弹窗出现前立即执行的效果
- `option = { … }`：选项（可见事件至少一个）
- `after = { … }`：无论选哪个选项都执行（finally 块）
- `abort_trigger / abort_effect`：条件满足时事件取消（暂停时不判定）
- `auto_opens = yes`：强制弹窗（即使用户关闭了弹窗）
- `trackable = yes`：启用自动追踪（需要 location）
- `base = <event_id>`（v3.4+）：事件继承，配合 `desc_clear / option_clear / picture_clear / show_sound_clear` 覆盖

### 2.3.3 触发方式

1. **轮询**：默认每天对所有匹配对象检查（性能昂贵，避免）。用 `is_triggered_only = yes` 或 `mean_time_to_happen` 或 `fire_only_once` 缓解。
2. **从其他事件/效果调用**：
   - `country_event = { id = crisis.2000 days = 400 random = 400 }`（随机延迟 400–800 天）
   - `random_galaxy_planet = { planet_event = { id = my_planet_event.1 } }`
   - v3.0+ 可覆盖调用作用域：`country_event = { id = x scopes = { from = fromfrom } }`
3. **on_action 注册**（最常见）：

```
# common/on_actions/<modname>_on_actions.txt
on_game_start_country = {
	events = {
		tutmod.1
		tutmod.2
	}
}
```

- 多个事件按注册顺序触发；多文件按文件名 ASCII 顺序。
- 每个 on_action 触发时：对 `events = {}` 中每个事件排除 trigger 为假的，全部触发；对 `random_events = {}` 中每个事件排除假的、加权随机触发一个（random_events 不支持权重修饰，但事件自身可带 `weight_multiplier = {}`）。
- v3.0+ 可自定义 on_action：`fire_on_action = { on_action = <string> scopes = { from = X fromfrom = Y } }`。

### 2.3.4 常用 on_action（原版，节选）

| 名称 | 作用域/说明 |
|---|---|
| `on_game_start` / `on_game_start_country` | 游戏开始（无/国家作用域） |
| `on_monthly_pulse` / `on_yearly_pulse` / `on_bi_yearly_pulse` / `on_five_year_pulse` / `on_decade_pulse` / `on_mid_game_pulse` / `on_late_game_pulse` | 全局周期脉冲 |
| `on_monthly_pulse_country` / `on_yearly_pulse_country` 等 | 国家周期脉冲（仅 has_pulse_events = yes 的国家类型，堕落/觉醒帝国不收） |
| `on_first_contact` | 两个帝国发现彼此（this=帝国1, from=帝国2, fromfromfrom=星系） |
| `on_colonization_started` / `on_colonized` / `on_colony_destroyed` | 殖民（星球作用域） |
| `on_survey` / `on_planet_surveyed` / `on_system_survey` | 调查（船/星球作用域） |
| `on_entering_system_first_time` / `on_entering_system` / `on_entering_system_fleet` | 进入星系（船/舰队） |
| `on_entering_war` | 开战（this=国家, from=敌方战争领袖） |
| `on_ship_destroyed_victim / _perp`、`on_fleet_destroyed_victim / _perp`、`on_space_battle_won / _lost` | 战斗事件 |
| `on_ground_combat_started`、`on_planet_attackers_win / _lose`、`on_planet_defenders_win / _lose` | 地面战斗 |
| `on_terraforming_begun` / `on_terraforming_complete` / `on_planet_class_changed` | 地形改造 |
| `on_uplift_completion` | 启蒙完成 |
| `on_pop_enslaved` | 奴役 |
| `on_ship_disabled` | 舰船瘫痪（this=船, from=瘫痪者） |

完整列表见 wiki On actions 页（约 200+ 个，含各种局势、危机、间谍、联邦、人口、领袖事件）。

### 2.3.5 选项（Options）

```text
option = {
	name = "loc_key"                 # 必填；也支持 name = { trigger = {…} text = "loc_key" }
	trigger = { … }                  # 不满足则不显示
	exclusive_trigger = { … }        # 满足则禁用其他所有选项
	allow = { … }                    # 不满足则显示但不可选（窗口打开时判定一次）
	default_hide_option = yes        # 按 Cancel 时默认选中此项（不是隐藏！）
	icon = …                         # 可选图标 sprite
	sound = …                        # 选择时播放的音效
	# 效果直接写在选项体内；游戏自动生成 tooltip
	custom_tooltip = "loc_key"       # 额外自定义提示
	hidden_effect = { … }            # 不生成 tooltip 的效果
	ai_chance = { factor = 100 modifier = { factor = 0 … } }   # AI 加权决策
}
```

外交事件选项（`diplomatic = yes`）额外支持：`response_text`（本地化键）、`is_dialog_only = yes`（仅文本响应）、`custom_gui`、`custom_gui_option`。

### 2.3.6 条件描述（Conditional Description）

```text
desc = {
	trigger = { owner = { NOT = { has_authority = auth_machine_intelligence } } }
	text = colony.182.desc
}
desc = {
	trigger = { owner = { has_authority = auth_machine_intelligence } }
	text = colony.182.desc.mach
}
```

- 多个匹配时随机显示一个；都不匹配则显示第一个。
- 单个 desc 内也可用 `text = {…} / success_text = {…} / fail_text = {…}` 组合动态文本（基于触发器真假，可叠加多条）。

### 2.3.7 最佳实践

- **性能**：绝大部分事件应为 `hide_window = yes` + `is_triggered_only = yes`；服务型事件（隐藏）做设置工作，再调用可见事件——隐藏事件调用可见事件的模式极为常见，因为 immediate 的效果可能需要至少一个 tick 才生效（内部缓存）。
- 用 gatekeeper 事件（轮询但带快速失败 pre_triggers）+ on_action 组合启动事件链。
- 覆盖原版事件：文件名加 `!!` 前缀（FIOS 规则）。
- 事件间作用域：明确注释每个事件的 this/root/from 含义。
- 事件链状态用 `begin_event_chain = { event_chain = "xxx_chain" target = ROOT }`、`create_point_of_interest = { id = … location = … }`。

### 2.3.8 调试

- `debugtooltip` 控制台命令 + 悬停可查看事件 ID/旗标/变量。
- `log = "xxx"` 效果写入 game.log。
- 空事件框 Bug：语法错误（花括号不匹配）会让后续事件"空心化"，每天弹出空 OK 框。用 debugtooltip 悬停 OK 按钮找事件 ID，检查 MOD 是否过期（可尝试 FirePrince 的 Python 工具修复过时语法）。

---

## 2.4 内容类型（content-types.md）

来源：stellaris.paradoxwikis.com/Government_modding、Technology_modding、Buildings、Decisions、Edicts 等及原版文件。所有内容文件放在 `common/<类型>/` 下，文件名任意（建议 `NN_<mod前缀>_<类型>.txt`），同目录文件全部加载。带 `potential / possible / random_weight` 的模式适用于多数定义。

### 2.4.1 国民理念（Civics）与起源（Origins）

位置：`common/governments/civics/`。起源就是带 `is_origin = yes` 的国民理念。**不要用 `00_civics.txt` 这种原版文件名**（会整文件覆盖），用 `00_MODNAME_civics.txt`。

```text
civic_beacon_of_liberty = {
	potential = {                     # 可选此理念的前提（不满足则隐藏/无效）
		ethics = { NOT = { value = ethic_gestalt_consciousness } }
		authority = { NOT = { value = auth_corporate } }
	}
	possible = {                      # 有效选择条件（不满足则灰显+生成需求提示）
		authority = { value = auth_democratic }
		ethics = {
			OR = { value = ethic_egalitarian value = ethic_fanatic_egalitarian }
			NOR = { value = ethic_xenophobe value = ethic_fanatic_xenophobe }
		}
	}
	random_weight = { base = 5 }      # 随机帝国生成权重（默认 1）
	modifier = {                      # 直接加给帝国的修饰符
		country_unity_produces_mult = 0.15
	}
	description = "loc_key_effects"   # 效果描述（可选，显示在修饰符 tooltip 前）
}
```

字段（Civics / Origins 通用）：`is_origin = yes`（起源专用）、`playable`（全局作用域条件，隐藏 DLC 内容）、`icon`（默认 `gfx/interface/icons/governments/civics/xxx.dds`，28×28）、`picture`（起源在帝国创建界面的图）、`starting_colony`（改变初始殖民星球类型）、`habitability_preference`（改变主物种气候偏好）、`potential / possible`、`pickable_at_start`（是否新建帝国时可选）、`modification = no`（开局后不可增删）、`random_weight`、`modifier`、`description`、`traits = { trait = trait_xxx }`（附加主物种特质）。

起源额外可用：`starting_system` 相关事件/初始化器。随机生成的 AI 帝国若使用你的起源/政体而无对应名字列表，可能无名字甚至崩溃——新政府类型必须配套 `common/random_names/` 中的随机名。

### 2.4.2 政体类型（Governments）

位置：`common/governments/`。字段：`ruler_title / ruler_title_female`（本地化键）、`heir_title`、`use_regnal_names`、`dynastic_last_names`、`should_force_rename`（AI 改制后强制重命名）、`possible`（国家作用域条件）、`weight`（多个政体符合时取权重最高）、`leader_class`（选举制）、`election_candidates = { modifier = { add = N … } }`。

### 2.4.3 权威（Authorities）

位置：`common/governments/authorities/`。字段：`playable`（全局条件）、`possible`（兼容条件，用"特殊需求语法"，见下）、`random_weight`、`election_type = democratic/oligarchic`、`re_election_allowed = yes/no`、`has_heir = yes/no`（君主制）、`can_have_emergency_elections`、`max_election_candidates`、`election_term_years / election_term_variance`、`uses_mandates`、`has_agendas`、`tags = { }`、`country_modifier = { }`、`traits = { }`、`can_reform`、`has_factions`、`localization_postfix`。

### 2.4.4 特殊需求语法（Special Requirement Syntax）

用于权威/理念/起源的 potential/possible：以 `ethic = xxx` 形式检查某伦理是否满足（多伦理 OR 并列），`authority = { value = auth_xxx }`，以及 `country_type / species_class` 等：

```
potential = {
	ethic = ethic_spiritualist            # 拥有任一列出的伦理即满足
	ethic = ethic_fanatic_spiritualist
	authority = { value = auth_imperial } # 与上表 AND
}
```

注意：该语法与常规触发器逻辑运算符不同，不要混用 `OR = { value = … }` 之外的复杂结构（详见 wiki Government modding 页）。

### 2.4.5 科技（Technologies）

位置：`common/technology/`（主文件）、`common/technology/category/`（研究类别）、`common/technology/tier/`（科技层级）。LIOS 覆盖，可单键覆盖原版；**覆盖科技若缺少 potential 块会继承被覆盖科技的 potential**（通常建议显式写）。

```text
tech_example_reactor = {
	cost = 1000                         # 研究成本（基础值会乘规模系数）
	area = engineering                  # physics / society / engineering
	tier = 2                            # 科技层级（决定出现时间）
	category = { energy_manipulation }  # 所属类别
	prerequisites = { tech_xxx }        # 前置科技
	start_tech = no
	prereqfor_desc = "loc_key"
	potential = {                       # 是否可出现在研究池
		has_technology = tech_xxx
	}
	weight = {                          # 研究池出现权重
		base = 100
		modifier = { factor = 1.5 has_ethic = ethic_materialist }
	}
	ai_weight = { base = 100 }          # AI 研究偏好
	modifier = {                        # 研究完成后获得的常驻修饰符
		ship_shield_add = 10
	}
	show_tech_unlocked = { tech_yyy }   # 解锁列表展示
}
```

类别文件（`common/technology/category/`）定义 `category = { cost_multiplier = 1.0 icon = "GFX_tech_category_xxx" }`；层级文件（tier）定义 `tier = { cost_multiplier = 1.0 upkeep_multiplier = 1.0 }`（cost_multiplier 逐层叠加）。`start_tech = yes` 开局拥有。`area = society` 等。

### 2.4.6 建筑（Buildings）

位置：`common/buildings/`。LIOS 覆盖。基础结构：

```text
building_example_lab = {
	base_build_time = 240
	base_cost = { minerals = 200 }
	category = "research"                 # 建筑分类（economic_categories 定义）
	prerequisites = { tech_xxx }          # 科技前置（可空）
	potential = { … }                     # 能否出现在建筑列表
	possible = { … }                      # 能否被建造
	shows_amount = yes
	planet_modifier = {                   # 行星级修饰符
		planet_researchers_produces_mult = 0.10
	}
	resources = {
		category = planet_buildings
		upkeep = { energy = 2 }
	}
	upgrades_to = building_example_lab_2  # 升级目标
	require_slot = yes / no
}
```

v3.3+ 可单键覆盖（此前破坏自动生成修饰符）。常用字段：`base_build_time / base_cost / cost`、`category`、`prerequisites`、`potential / possible`、`planet_modifier / country_modifier / pop_modifier`、`resources`、`upgrades_to`、`starting = yes`（开局自带）、`special_build = yes`、`can_build = no`、`is_capped_by_tech = yes`（数量受科技上限）、`has_shown_planet_modifier` 等。

### 2.4.7 区划（Districts）

位置：`common/districts/`。结构类似建筑：

```text
district_example_generator = {
	planet_modifier = {
		district_generator_energy_produces_mult = 0.10
	}
	resources = {
		category = colony_districts
		production = { energy = 6 }
	}
}
```

常用字段：`category`（colony_districts）、`planet_modifier`、`resources`、`allows_jobs = { job_xxx }`（通过 job 产生岗位）、`requires_planet_flag`、`max_by_planet_class`、`capped_by_technology`、`is_city_district = yes`（城市区划扩张建筑槽）、`district_limit`、`prerequisites`。区划建筑槽受 `zone_slots`（v4.0+）影响。

### 2.4.8 行星决策（Decisions）

位置：`common/decisions/`。LIOS 覆盖。

```text
decision_example = {
	icon = "GFX_decision_type_xxx"
	potential = { is_planet_class = pc_continental }
	possible = { owner = { has_technology = tech_xxx } }
	days_remove = 30                      # 生效天数（可选）
	show_messages = yes
	allow = { … }                         # 显示但不可选的条件
	custom_tooltip = "loc_key"
	effect = {
		owner = { add_resource = { influence = 100 } }
	}
	ai_weight = { base = 10 }
	hidden_effect = { … }                 # 不生成 tooltip 的效果
}
```

常用字段：`icon`、`potential`（显示前提）、`possible`（可执行前提）、`allow`、`days_remove`（限时生效）、`effect / hidden_effect`、`ai_weight`、`show_messages`、`custom_tooltip`、`can_use_only_once`（v4.x 加入）。决策在星球视图/右键菜单显示，执行效果写在 effect。

### 2.4.9 法令（Edicts）

位置：`common/edicts/`。结构：

```text
edict_example = {
	potential = { … }
	possible = { … }
	cost = { influence = 200 }            # 或 resources = { category = edicts upkeep = { unity = 10 } }
	length = 3600                         # 持续天数；@EdictPerpetual 为永久
	modifier = {                          # 生效期间修饰符
		country_energy_produces_mult = 0.10
	}
	icon = "GFX_edict_type_policy"
}
```

常用：`potential / possible / cost / length / modifier / icon / ai_weight / resources = { category = edicts upkeep = { unity = 10 } }`。永久法令用 `@EdictPerpetual`。

### 2.4.10 政策（Policies）

位置：`common/policies/`。定义政策选项，玩家选择其一：

```text
policy_example = {
	potential = { has_technology = tech_xxx }
	option = {
		name = "policy_example_a"
		on_enabled = { … }                # 选择时效果
		on_disabled = { … }
		modifier = { … }
	}
	option = { name = "policy_example_b" … }
}
```

### 2.4.11 传统树（Traditions）与飞升天赋（Ascension Perks）

- 传统树：`common/tradition_categories/`（树定义 + 图标 + AI 权重）+ `common/traditions/`（树内每个传统：`adoption = { … }`、`finisher = { … }`、`unlock = { … }`、`tradition = { … }`）。
- 飞升天赋：`common/ascension_perks/`：`potential / possible / modifier / custom_tooltip / ai_weight`，可 `hidden = yes`。

### 2.4.12 特质（Traits）

- 物种特质与领袖特质：`common/traits/`。**整文件覆盖 ONLY**（DUPL/NO），不能用单独文件加新特质——必须替换整个 vanilla traits 文件或追加时小心。
- 结构：`trait_xxx = { cost = 2 modification = yes possible = { … } initial = no randomized = yes species_potential = { … } country_potential = { … } modifier = { … } leader_potential = { … } leader_modifier = { … } category = { … } icon = "GFX_trait_xxx" }`。
- v4.0+：`common/trait_tags/` 可分组特质；`common/species_archetypes/` 分配特质点与特质集。

### 2.4.13 职业（Jobs）

位置：`common/pop_jobs/`。v3.3+ 可单键覆盖。结构：`job_xxx = { possible_pre_triggers = { … } possible = { … } resources = { category = planet_jobs production = { energy = 4 } upkeep = { food = 2 } } category = worker/specialist/ruler … }`。岗位修饰符类别由 `common/economic_categories/` 定义（job 分类决定哪些修饰符适用）。

### 2.4.14 其他常见类型

| 类型 | 位置 | 备注 |
|---|---|---|
| 星系/恒星初始化器 | `common/solar_system_initializers/` | FIOS；预定义星系、生成国家/殖民地/舰队 |
| 特殊项目 | `common/special_projects/` | FIOS；`project = { … possible = { … } }` |
| 考古站点 | `common/archaeological_site_types/` | `archaeological_site_type = { … }` |
| 异常 | `common/anomalies/` | LIOS；`anomaly_xxx = { … spawn_chance … }` |
| 起源国/预设帝国 | `prescripted_countries/` | `.txt` 预置国家 |
| 圣物 | `common/relics/` | `relic_xxx = { … }` |
| 决议/社区 | `common/resolutions/`、`common/galactic_focuses/` | 银河社区 |
| 巨构 | `common/megastructures/` | `megastructure_xxx = { … }` |
| 事件链图 | `common/event_chains/` | FIOS；`event_chain = { … }` |
| 星际基地建筑/模块 | `common/starbase_buildings/`、`common/starbase_modules/` | `starbase_building_xxx = { … }` |
| 舰船 | `common/ship_sizes/`、`common/component_templates/`、`common/section_templates/` | 船体/组件/段模板（section 不可覆盖） |
| 静态修饰符 | `common/static_modifiers/` | `static_modifier_xxx = { … }` |

### 2.4.15 AI 权重与平衡

- 多数定义支持 `ai_weight = { base = N modifier = { factor = X … } }`。
- 随机生成权重 `random_weight = { base = N modifier = { factor = X … } }`：两理念权重相同则 50:50；45+50 对比 5 时约 5% 概率。
- 权重用 base（基础分）+ modifier（factor 乘算 / add 加算）组织，不要写死单一数值。
- AI 预算（`common/ai_budget/`）、经济计划（`common/economic_plans/`）控制 AI 资源分配；玩法 MOD 需兼顾，否则 AI 不会用你的内容。

---

## 2.5 本地化（localisation.md）

来源：stellaris.paradoxwikis.com/Localisation_modding、Modding_tutorial。

### 2.5.1 文件规则

- 位置：MOD 根文件夹下的 `localisation/`（**带 s**，不是 localization）。
- 命名：`<文件名>_l_<语言>.yml`，如 `mymod_l_english.yml`；不以 `_l_<语言>` 结尾不会被读取。
- 编码：**必须 UTF-8 with BOM**（普通 UTF-8 会被拒绝解析）。VSCode/Notepad++ 可另存为带 BOM；最稳妥是复制原版 yml 再改。
- 首行必须是 `l_<语言>:`，如 `l_english:`。支持语言：`braz_por, english, french, german, japanese, korean, polish, russian, simp_chinese, spanish`。
- 每条键前必须有空白（空格或 tab）。冒号后的数字（原版如 `key:0 "text"`）可省略，仅供 Paradox 翻译追踪用。
- 字符串用引号包裹；引号内显示引号用 `\"`。
- 无效 Unicode 字符（会显示为 ?）：`„ “ ‚ ‘ – ” ’ … —`。

```
l_english:
 tutmod_civic: "Semper Exploro"
 tutmod_civic_desc: "This society prioritised scientific exploration."
 tutmod_civic_effects: "Start with a $science$ and assigned $scientist$."
```

**没有回退语言机制**：缺失本地化时直接显示原始键名（如 `tutmod_civic`）。因此惯例是：把英文文件复制到所有语言文件夹，改首行语言声明。可借 `$键名$` 引用其他键，只需翻译一次。

### 2.5.2 覆盖原版文本

在 `localisation/` 下建 `replace/` 文件夹；其中的文件在所有本地化之后加载（LIOS），按 key 覆盖——不需要整文件替换。同名 yml 也会整文件覆盖原版（不推荐，除非几乎全改）。

### 2.5.3 控制台命令

- `reload text`：重载本地化表（改错字后不用重启）。
- `switchlanguage english`（或 `switchlanguage l_english`）：切换语言并重载。
- `toggle_string_id`：显示 StringID 代替本地化文本。

### 2.5.4 括号命令（Bracket Commands / Scoped Localisation）

格式：`[<主作用域>.<次级作用域>.<文本获取>]`，以 `.` 分隔。

- 主作用域：`Root`（事件 root）、`This`（当前作用域）、`From`（调用者，可 From.From）、`Prev`、事件目标标签（直接写名字，如 `[mytarget.GetName]`）、外交消息的 `Actor / Recipient / Third_party`。
- 次级作用域（部分）：`Capital`（`[Root.Capital.GetName]`）、`Leader`、`Owner`、`System`、`Planet`、`Species`、`MainAttacker / MainDefender`（战争）、`Solar_System` 等。
- 文本获取（部分）：`GetName / GetAdj / GetAdjective / GetHomeWorldName / GetLeaderName / GetRulerName / GetRulerTitle / GetHeirName / GetHeirTitle / GetOwnerName / GetControllerName / GetClassName / GetPlanetClass / GetSpeciesName / GetSpeciesAdj / GetSpeciesClass / GetFleetName / GetEngineer / GetEngineerPlural / GetScientist / GetScientistPlural / GetLinguists / GetResearchers / GetTerraformer(Plural) / GetHasHave / GetIsAre / GetSheHe / GetHerHim / GetHerHis / GetWasWere / GetAge / GetAAnPlanetClass / GetNamePlural` 等（完整列表见 wiki 或 `logs/script_documentation/localizations.log`）。
- 无作用域命令：`GetDate / GetMidGameDate / GetLateGameDate / GetYear / LastKilledCountryName`。
- 变量与日期：`[Scope.my_variable]`、`[Scope.my_date_flag]`（v3.1+）。
- 转义：`[[` 显示字面 `[`；在 scripted effect/trigger 中用括号命令须写成 `\\[This.GetName]`（双反斜杠）。
- scripted_loc 内部不能再使用括号命令。

### 2.5.5 颜色码

以 `§` 开头 + 颜色字符，`§!` 恢复默认：

| 码 | 颜色 | 用途 |
|---|---|---|
| W | 白 | 外交态度 |
| T | 浅灰 | 标准正文 |
| g | 深灰 | 禁用 |
| L | 棕/卡其 | 背景故事 |
| P | 浅脏粉 | 攻击性文本高亮 |
| R | 红 | 负面修饰符 |
| H / K | 橙 | 高亮 |
| Y / I | 黄 | 中性/次优修饰符 |
| G | 绿 | 正面修饰符 |
| V | 深绿 | 事件文本 |
| E | 青 | 大段文本 |
| C | 青色 | 概念文本（生成 tooltip） |
| B | 蓝青 | 影响 pop 的事件效果 |
| M | 紫 | 稀有科技 |
| _ | 品红 | 占位符 |
| c / v / d / r / l | 领袖特质等级色 | |

示例：`$AGE|Y$` 将变量着色为黄色。Windows 输入 `§`：ALT+0167。

### 2.5.6 `$` 码（键引用）

`$键名$` 引用其他本地化键（原版或 MOD 的），例如 `"Upkeep by +$@cyborg_energy_upkeep$"`、`"Start with a $science$"`。`@变量` 也可引用。

### 2.5.7 数字格式化

`$VALUE|*x$` 保留 x 位小数：`$EXAMPLE|*0$` → 100；`$EXAMPLE|*1$` → 100.0。

### 2.5.8 `£` 码（图标）

`£energy£ £minerals£ £food£ £influence£ £stability£ £unity£ £alloys£ £trade_value£ £physics£ £society£ £engineering£ £pops£ £happiness£ £opinion£ £military_power£ £time£ £planetsize£` 等。多帧图标：`£leader_skill|3£`。自定义文本图标：把 16×16 的 .dds 放 `gfx/interface/icons/text_icons/`，在 `interface/` 下建 .gfx 定义 spriteType（`name = "GFX_text_xxx"`），本地化中用 `£xxx£`（去掉 GFX_text_ 前缀）。

### 2.5.9 斜杠码

- `\n` 换行、`\t` 制表、`\"` 字面引号。

### 2.5.10 风格指南（与原版融合）

| 位置 | 大小写 | 标点 | 字符上限 | 示例 |
|---|---|---|---|---|
| 事件名 | Title Case | 无 | 50 | "Exotic Woodwind" |
| 事件描述 | Sentence case | 标准 | 2000 | … |
| 事件选项 | Sentence case | 句末标点 | 70 | "Let us be careful." |
| 特质/修饰符/建筑名 | Title Case | 无 | 30 | "Very Strong" |
| 特质/建筑描述 | Sentence case | 标准 | 200 | … |
| UI 按钮 | Sentence/Title | 无 | 视 UI | "Withdraw" |

### 2.5.11 为多种语言准备

- CWTools 可生成缺失本地化键列表：右键 → Command Palette → "Generate missing loc for all files"。
- 惯例：英文为准，其他语言复制英文（改首行）。玩家非英文语言下缺键会看到原始键名。
- `$键$` 引用词形变化：最适合名词主格；跨语言可能语法不完美，属正常现象。

---

## 2.6 图形与界面资源（media-ui.md）

来源：stellaris.paradoxwikis.com/Modding（Game structure 段）、Interface、Icons、Flags、Fonts、Music、Sound、Event pictures。

### 2.6.1 图形资源总览（gfx/）

| 目录 | 内容 |
|---|---|
| `gfx/interface/icons/` | 全部游戏图标（按功能分子目录，如 `governments/civics/`、`modifiers/`、`text_icons/`、`buildings/`、`technologies/`、`decisions/`、`edicts/`） |
| `gfx/event_pictures/` | 事件图片 |
| `gfx/interface/flags/` | 旗帜图像蒙版 |
| `gfx/portraits/`、`gfx/models/`、`gfx/models/portraits/` | 立绘与 3D 模型（.mesh） |
| `gfx/fonts/` | 字体文件 |
| `gfx/FX/`、`gfx/particles/`、`gfx/projectiles/`、`gfx/worldgfx/` | 特效/粒子/弹道/世界图形 |
| `gfx/loadingscreens/` | 加载画面 |
| `gfx/cursors/`、`gfx/arrows/`、`gfx/keyicons/` | 光标/箭头/按键图标 |

- 图标格式：**.dds**（DirectDraw Surface）。常用工具：GIMP、Paint.NET（需 dds 插件）、SageThumbs（资源管理器预览 .dds）。
- 常见尺寸：国民理念图标 28×28；文本图标 16×16；modifiers 图标 `mod_xxx.dds`。
- 用 .gfx 文件（位于 `interface/`）把图像注册为 sprite 供代码引用：

```
spriteTypes = {
	spriteType = {
		name = "GFX_evt_example"
		texturefile = "gfx/event_pictures/example.dds"
	}
}
```

`name` 以 `GFX_` 开头是惯例。事件图片/自定义图标都需这样注册。事件图引用：`picture = GFX_evt_example`。

### 2.6.2 界面（interface/）

- `*.gui`：界面视觉逻辑（按钮、面板、窗口布局）。
- `*.gfx`：把图像文件映射为界面变量（spriteType）。
- 界面是 LIOS 覆盖；UI MOD 常见做法是整体替换或高优先级文件覆盖。
- 自定义事件窗口：`custom_gui = "窗口名"` 指向 .gui 中定义的窗口；外交事件可配 `custom_gui_option`。
- 常见子目录：`interface/buttons/`、`interface/event_window/`、`interface/outliner/`、`interface/topbar/`、`interface/ship_designer/`、`interface/tech_view/`、`interface/planetview/`、`interface/diplomacy/`、`interface/main/`、`interface/system/` 等。
- 加载顺序：UI MOD 放玩法 MOD 之后、UI 补丁之前；UI 子 MOD 在 UI 主 MOD 之下。

### 2.6.3 旗帜（flags/）

- `flags/*.dds`：旗帜图案文件；`flags/colors.txt`：可用颜色与随机组合。
- 自制旗帜：制作 .dds（RGB，带 alpha 通道作为蒙版），在 colors.txt 的对应分类下注册颜色组合。

### 2.6.4 字体（fonts/）

- `fonts/fonts.asset`：定义游戏使用的字体（映射 ttf 到字体名、大小）。
- 字体是 LIOS 覆盖。中文 MOD 常需要补充中文字体以避免缺字。

### 2.6.5 音乐（music/）

- `music/*.ogg`：音乐文件；`music/songs.asset`：把音乐映射为代码名并设置播放音量；`music/songs.txt`：播放权重等。
- 自定义音乐：放 .ogg 到 `music/`，在 songs.asset 注册 `song = { name = "xxx" file = "xxx.ogg" … }`。

### 2.6.6 声音（sound/）

- `sound/*.asset`：定义声音事件（event），`sound/*.wav`：声音文件。
- 事件中引用：`show_sound = event_xxx_sound`；选项 `sound = …`。

### 2.6.7 立绘（Portraits）与模型（Models）

- 立绘：`gfx/models/portraits/`（.mesh + 贴图）；`gfx/portraits/` 引用逻辑。物种类别（`common/species_classes/`）分配立绘与图形文化。
- 3D 模型：Clausewitz Maya Exporter（官方）、IO PDX Mesh（Blender/Maya 插件）、Spaceship Generator（Blender 程序化飞船）。
- 船体皮肤：`common/graphical_culture/`。

### 2.6.8 界面相关常见问题

- 图标缺失：error.log 出现 "Did not find an icon for xxx" —— 在正确目录放置 .dds（如理念图标 `gfx/interface/icons/governments/civics/xxx.dds`）。
- 本地化图标 `£xxx£` 不显示：确认 sprite 已注册且名字前缀正确（`GFX_text_` + 去掉前缀引用）。
- .gui 语法错误通常导致整个界面无法加载（检查括号匹配、UTF-8 编码）。
- 缩略图 `thumbnail.png` 512×512、<1MB，2.4 后固定文件名。

---

## 2.7 工具、调试、测试与发布（tools-debug.md）

来源：stellaris.paradoxwikis.com/Modding（Tools & utilities / Advanced tips）、Modding_tutorial（Logs & Debugging）。

### 2.7.1 推荐工具

| 工具 | 用途 |
|---|---|
| Visual Studio Code / VSCodium / Sublime Text / Notepad++ | 文本编辑（括号折叠、多文件搜索） |
| **CWTools**（VSC 扩展） | Paradox 语法校验、自动补全、缺失本地化键列表、自动格式化 |
| Paradox Syntax Highlighting（VSC 扩展） | 语法高亮 |
| IntelliJ IDEA + Paradox Language Support 插件 | 更智能的 IDE 方案 |
| WinMerge / L13 Diff（VSC 扩展） | 文件夹对比/合并（更新原版文件到新版补丁） |
| Irony Mod Manager | 启动器替代品 + 冲突解决（Conflict Solver 需按加载顺序重跑） |
| Git + GitHub/GitLab | 版本管理、协作（Modding Git Guide 有 HOI4 示例但原理通用） |
| GIMP / Paint.NET / SageThumbs | 图像编辑 / .dds 预览 |
| 7-Zip | 归档 |
| Stellaris Galaxy Generator / Static Galaxy Generator | 星系生成器 |
| IO PDX Mesh / Clausewitz Maya Exporter / Spaceship Generator | 3D 模型 |
| Random Empire Generator | 随机帝国生成 |

工作流建议：VSC + CWTools 写脚本；WinMerge 或 Git 管理版本；Irony 管理加载顺序与冲突。

### 2.7.2 控制台命令（测试用）

游戏中按 `~` 打开控制台。控制台接受任何合法脚本（trigger / effect / event），在当前选中对象的作用域执行（选中帝国请打开政府界面）。

| 命令 | 说明 |
|---|---|
| `observe` | 观察者模式（不操控任何国家，可长时间挂机测试） |
| `run <文件名>.txt` | 执行 Documents 目录下文本中的脚本（玩家作用域）；改脚本后重跑即可，无需重启 |
| `debugtooltip` | 悬停对象显示旗标、变量、事件 ID |
| `reload text`（旧 `reloadloc`） | 重载本地化表 |
| `switchlanguage <lang>` | 切换语言 |
| `toggle_string_id` | 显示 StringID |
| `script_profiler` | 两次调用（开始/结束）输出脚本性能报告（v3.5+） |
| `help` | 列出常用命令 |
| `event <id>`、`trigger …`、`effect …` | 直接触发事件 / 执行条件 / 执行效果 |

测试脚本示例（选中目标星球）：
`effect owner = { every_owned_ship = { prevprev = { change_variable = { which = tutmod_var_num_ships value = 1 } } } }`

### 2.7.3 日志与调试

- 日志位置：`…/Paradox Interactive/Stellaris/logs/`（`error.log`、`game.log`）。
- `log = "text"` 效果把字符串写入 game.log（所有作用域可用）。**默认只输出相同字符串的首次出现**——循环内要拼接递增变量，或启动参数 `-logall`。
- `error.log` 用异常捕获机制：约 90% 的崩溃（CTD）不会记录相关内容；崩溃数据在 `Stellaris/crashes/`（主要供开发者）。
- 常见 error.log 条目：`Did not find an icon for civic: xxx`（缺图标）、`Object key already exists`（同名键，多数 LIOS 情况无害）、`Variable name taken` 等。
- 启动参数（stellaris.exe）：`-debug_mode`（更多日志）、`-debugtooltip`（开局启用调试提示）、`-logprefix / -logpostfix`（日志文件名前后缀）、`-logall`（重复字符串也记录）、`-script_debug`。

### 2.7.4 测试流程

1. 用 `run` 脚本或控制台直接验证 trigger/effect 逻辑。
2. `observe` 模式长挂机验证事件链与 AI 行为。
3. 检查 error.log 中与 MOD 前缀相关的条目。
4. 性能：`script_profiler`。
5. 多语言：`switchlanguage` + `toggle_string_id` 检查缺失键。
6. 用 CWTools 全文件校验语法与缺失本地化。

### 2.7.5 故障排查（Troubleshooting）

- MOD 不出现在启动器：检查 `launcher-v2.sqlite` 中 `dirPath` / `status`；或删除 Paradox 启动器数据库（先备份）并 Reload installed mods。
- 本地与工坊同时存在同一 MOD 时游戏拒绝加载：删除其一（含 `Stellaris/mod/*.mod`）。
- 多人在线：所有人 MOD 列表与加载顺序必须一致。
- MOD 文件夹路径含非 ASCII 字符可能导致问题。
- 防病毒可能静默拦截启动器；OneDrive 空间满/断连也会影响。
- 校验游戏完整性（Steam → 属性 → 本地文件 → 验证）——但验证不检查安装目录中额外文件。
- 核弹级重置（Purging all mods）：退出游戏与启动器 → 退订所有 MOD → 退出 Steam → 删除 `workshop/content/281990` 内容 → 删除 `dlc_load.json`、`launcher-v2.sqlite`、settings.txt 中 `last_mods={ }` → 重启 Steam → 重开启动器 → 重新订阅等待下载完成。

### 2.7.6 发布（Steam Workshop）

- 上传：启动器 Mod Tools → Upload a Mod → 选 MOD → 选站点 → 填描述 → Upload；更新走同样流程（描述会替换工坊页面描述）。
- 缩略图：`thumbnail.png`，512×512 以上，<1MB。
- tags 最多 10 个；非预定义标签可能无法上传 Paradox Mods。
- 用 DLC 独占内容必须保留 DLC 检查（如 Nemesis 间谍行动）。
- 上传后验证：工坊页面正常显示缩略图、描述、版本、标签；多人测试确保无 checksum 问题。

### 2.7.7 编码与规范检查清单

- [ ] 脚本与 .mod 文件：UTF-8（无 BOM）
- [ ] 本地化 .yml 与 name_lists：UTF-8 **with BOM**
- [ ] 文件名不与原版冲突（用 MOD 专属前缀，如 `00_mymod_civics.txt`）
- [ ] 事件文件首行有 namespace；事件都有 `is_triggered_only = yes`（除非确需轮询）
- [ ] 每个新键都有对应语言的本地化（至少英文）
- [ ] 图标/图片已注册并放在正确目录
- [ ] descriptor 字段正确（name/path/supported_version/tags）
- [ ] error.log 无本 MOD 相关报错
- [ ] 缩略图满足尺寸与体积要求

---

# 第三部分 脚手架脚本（scaffold_mod.py）

一键生成标准 Stellaris MOD 目录结构 + descriptor + 10 种语言本地化模板（UTF-8 BOM）。用法：

```bash
python3 scaffold_mod.py "<MOD名>" [--mod-dir <本地MOD目录>] [--supported-version v3.14.*] [--tags "Graphics Economy"]
```

```python
#!/usr/bin/env python3
"""Scaffold a new Stellaris mod folder structure.

Generates the standard directory layout the Stellaris launcher expects:

    <stellaris_mod_dir>/<modname>.mod          <- launcher descriptor (has path=)
    <stellaris_mod_dir>/<modname>/descriptor.mod <- in-mod metadata (no path=)
    <stellaris_mod_dir>/<modname>/common/
    <stellaris_mod_dir>/<modname>/events/
    <stellaris_mod_dir>/<modname>/localisation/english/
    ... (more folders listed in --folders)

Usage:
    python3 scaffold_mod.py <modname> [--mod-dir PATH] [--supported-version v3.14.*]
                             [--tags "Tag1 Tag2"] [--desc "Short description"]

Default --mod-dir is the platform Stellaris mod folder:
  Windows: %USERPROFILE%\\Documents\\Paradox Interactive\\Stellaris\\mod
  Linux:   ~/.local/share/Paradox Interactive/Stellaris/mod
  macOS:   ~/Documents/Paradox Interactive/Stellaris/mod

Rules implemented (from the Stellaris modding wiki):
  - .mod / descriptor.mod use plain UTF-8.
  - localisation .yml files are written as UTF-8 WITH BOM (Stellaris requires it).
  - Localisation file names end with _l_<language>.yml and start with l_<language>:.
  - Folder and file names are case-sensitive on macOS/Linux.
"""
import argparse
import os
import sys
import textwrap

DEFAULT_FOLDERS = [
    "common/agendas",
    "common/anomalies",
    "common/ascension_perks",
    "common/bombardment_stances",
    "common/buildings",
    "common/casus_belli",
    "common/civics",  # NOTE: civics live in common/governments/civics; kept for docs only
    "common/colony_types",
    "common/decisions",
    "common/defines",
    "common/deposits",
    "common/diplo_phrases",
    "common/districts",
    "common/edicts",
    "common/event_chains",
    "common/governments",
    "common/governments/authorities",
    "common/governments/civics",
    "common/megastructures",
    "common/name_lists",
    "common/on_actions",
    "common/policies",
    "common/pop_faction_types",
    "common/pop_jobs",
    "common/scripted_effects",
    "common/scripted_loc",
    "common/scripted_triggers",
    "common/scripted_variables",
    "common/script_values",
    "common/section_templates",
    "common/ship_behaviors",
    "common/ship_sizes",
    "common/solar_system_initializers",
    "common/special_projects",
    "common/static_modifiers",
    "common/technology",
    "common/technology/category",
    "common/technology/tier",
    "common/traditions",
    "common/traits",
    "common/war_goals",
    "events",
    "flags",
    "gfx/interface/icons",
    "interface",
    "localisation",
    "localisation/english",
    "localisation/simp_chinese",
    "map",
    "prescripted_countries",
    "sound",
]

LANGUAGE_HEADERS = {
    "english": "l_english:",
    "simp_chinese": "l_simp_chinese:",
    "braz_por": "l_braz_por:",
    "french": "l_french:",
    "german": "l_german:",
    "japanese": "l_japanese:",
    "korean": "l_korean:",
    "polish": "l_polish:",
    "russian": "l_russian:",
    "spanish": "l_spanish:",
}


def default_mod_dir():
    if sys.platform == "win32":
        return os.path.join(os.environ.get("USERPROFILE", ""), "Documents",
                            "Paradox Interactive", "Stellaris", "mod")
    home = os.path.expanduser("~")
    if sys.platform == "darwin":
        return os.path.join(home, "Documents", "Paradox Interactive", "Stellaris", "mod")
    return os.path.join(home, ".local", "share", "Paradox Interactive", "Stellaris", "mod")


def write_utf8_bom(path, content):
    with open(path, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(content)


def write_utf8(path, content):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def sanitize(name):
    """Mod names must be filesystem-safe; spaces replaced by underscores."""
    return name.strip().replace(" ", "_")


def main():
    parser = argparse.ArgumentParser(description="Scaffold a Stellaris mod folder")
    parser.add_argument("modname", help="Mod display name, e.g. MyStellarisMod")
    parser.add_argument("--mod-dir", default=None,
                        help="Directory that holds local mods (where <modname>.mod lives)")
    parser.add_argument("--supported-version", default="v3.14.*",
                        help="supported_version string, e.g. v3.14.*")
    parser.add_argument("--tags", default="",
                        help="Space separated workshop tags, e.g. 'Graphics Economy'")
    parser.add_argument("--folders", default=None,
                        help="Comma separated extra folders to create")
    args = parser.parse_args()

    modname = sanitize(args.modname)
    if not modname:
        print("ERROR: modname must be non-empty", file=sys.stderr)
        sys.exit(1)

    mod_dir = args.mod_dir or default_mod_dir()
    os.makedirs(mod_dir, exist_ok=True)
    root = os.path.join(mod_dir, modname)

    # <modname>.mod (launcher descriptor, contains path=)
    outer_lines = [
        f'name="{modname}"',
        f'path="mod/{modname}"',
    ]
    if args.tags:
        outer_lines.append("tags={")
        outer_lines += [f'\t"{t}"' for t in args.tags.split()]
        outer_lines.append("}")
    outer_lines.append(f'supported_version="{args.supported_version}"')
    outer_mod = "\n".join(outer_lines) + "\n"

    # descriptor.mod (in-mod metadata, no path=)
    inner_lines = [f'name="{modname}"']
    if args.tags:
        inner_lines.append("tags={")
        inner_lines += [f'\t"{t}"' for t in args.tags.split()]
        inner_lines.append("}")
    inner_lines.append(f'supported_version="{args.supported_version}"')
    inner_desc = "\n".join(inner_lines) + "\n"

    folders = DEFAULT_FOLDERS + ([f.strip() for f in args.folders.split(",") if f.strip()]
                                 if args.folders else [])
    for folder in folders:
        os.makedirs(os.path.join(root, folder), exist_ok=True)

    write_utf8(os.path.join(mod_dir, f"{modname}.mod"), outer_mod)
    write_utf8(os.path.join(root, "descriptor.mod"), inner_desc)

    # Localisation templates (UTF-8 with BOM!)
    loc_key = f"{modname}_"
    for lang, header in LANGUAGE_HEADERS.items():
        lang_dir = os.path.join(root, "localisation", lang)
        os.makedirs(lang_dir, exist_ok=True)
        write_utf8_bom(
            os.path.join(root, "localisation", lang, f"{modname}_l_{lang}.yml"),
            f"{header}\n {loc_key}example: \"Example text\"\n {loc_key}example_desc: \"Example description.\"\n",
        )

    # Events template with namespace
    ns = modname.lower()
    write_utf8(
        os.path.join(root, "events", f"{modname}_events.txt"),
        textwrap.dedent(f"""\
            # {modname} events. Namespace must be unique across all mods.
            namespace = {ns}

            country_event = {{
                id = {ns}.1
                hide_window = yes
                is_triggered_only = yes
                trigger = {{
                    # conditions go here
                }}
                immediate = {{
                    # effects go here
                }}
            }}
            """),
    )

    # on_actions template
    write_utf8(
        os.path.join(root, "common/on_actions", f"{modname}_on_actions.txt"),
        textwrap.dedent(f"""\
            # Register events to game events. Events fired here should be is_triggered_only.
            on_game_start_country = {{
                events = {{
                    {ns}.1
                }}
            }}
            """),
    )

    print(f"Created mod '{modname}' in: {mod_dir}")
    print(f"  {modname}.mod")
    print(f"  {modname}/descriptor.mod")
    print(f"  {len(folders)} content folders")
    print(f"  localisation templates for {len(LANGUAGE_HEADERS)} languages (UTF-8 BOM)")
    print("\nNext: edit files under the mod folder, add a thumbnail.png (512x512, <1MB),")
    print("and enable the mod in the Paradox Launcher.")


if __name__ == "__main__":
    main()
```

---

# 附录 参考来源

本手册内容整理自 stellaris.paradoxwikis.com 的以下页面（页面版本以 2025–2026 年快照为准，随游戏版本更新可能变化，关键字段以游戏原版文件为准）：

- https://stellaris.paradoxwikis.com/Modding
- https://stellaris.paradoxwikis.com/Modding_tutorial
- https://stellaris.paradoxwikis.com/Dynamic_modding
- https://stellaris.paradoxwikis.com/Event_modding
- https://stellaris.paradoxwikis.com/Localisation_modding
- https://stellaris.paradoxwikis.com/Scopes
- https://stellaris.paradoxwikis.com/Variables
- https://stellaris.paradoxwikis.com/On_actions
- https://stellaris.paradoxwikis.com/Government_modding
- https://stellaris.paradoxwikis.com/Defines

相关社区资源：Stellaris Modding Den Discord、Stellaris Modding Subreddit、"List of Stellaris triggers, modifiers and effects"（GitHub）、CWTools（VSC 扩展）。
