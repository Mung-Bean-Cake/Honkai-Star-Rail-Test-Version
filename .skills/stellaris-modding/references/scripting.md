# 脚本语言参考：作用域 / 条件 / 效果 / 事件

来源：https://stellaris.paradoxwikis.com/Scopes | /Conditions | /Effects | /Event_modding

## 一、作用域（Scopes）

游戏内几乎所有对象都有 scope，对象之间是树状层级，全局作用域代表整个游戏。

```
<scope_type> = { ... }   # 花括号内的脚本作用于该对象
```

### 四个系统关键字

| 关键字 | 含义 | 可叠加 |
|--------|------|--------|
| `ROOT` | 脚本的主作用域（事件根对象） | — |
| `THIS` | 当前作用域 | — |
| `PREV` | 上一个作用域 | 最多 4 次：`prevprevprevprev` |
| `FROM` | 调用当前脚本的来源作用域 | 最多 4 次：`fromfrom` |

### 链式写法

用 `.` 连接可简化嵌套，**链式不产生 PREV**：

```
owner.capital_scope.solar_system = { ... }
# 等价于
owner = { capital_scope = { solar_system = { ... } } }

prevprev.prev     # 链式与 PREV 可混用
```

### 常用作用域

| 作用域 | 含义 | 可从何处切换 |
|--------|------|--------------|
| `country` / `owner` / `controller` | 国家 / 拥有者 / 占领者 | fleet, ship, planet, pop, leader, army |
| `space_owner` | 空域的拥有者（未殖民行星无 `owner` 时用它） | planet |
| `planet` / `capital_scope` / `orbit` / `star` | 行星 / 首都 / 绕行对象 / 恒星 | pop, army, starbase |
| `system` / `solar_system` / `galactic_object` / `system_star` | 星系 | planet, country, ship, fleet |
| `fleet` | 舰队 | ship, starbase, leader, army |
| `ship` | 舰船（含星基、防御平台、采矿站） | fleet |
| `pop` / `last_created_pop` / `unhappiest_pop` | 人口 | leader, army, planet, country |
| `leader` / `ruler` / `heir` | 领袖 / 统治者 / 继承人 | country, ship, fleet |
| `species` / `owner_species` | 物种 | country, ship, pop, leader |
| `federation` / `alliance` | 联邦 | country |
| `sector` | 星区 | planet, leader |
| `megastructure` | 巨构（完工后栖息地/环形世界转为 planet） | — |
| `starbase` | 星际基地 | — |
| `army` | 陆军 | ship, country, planet |
| `deposit` | 资源沉积 / 障碍 | — |
| `war` | 战争 | country |
| `pop_faction` | 派系 | — |
| `archaeological_site` | 考古遗址 | — |
| `situation` | 局势 | — |
| `astral_rift` | 星界裂隙（3.14+） | — |

### 迭代器（作用域切换）

这是最容易出错的地方：**同样写 `xxx = { }`，作为效果是迭代器，作为触发器是判断器。**

| 前缀 | 位置 | 行为 |
|------|------|------|
| `every_*` | 效果块 | 对**每一个**对象执行内部效果 |
| `random_*` | 效果块 | 对**随机一个**对象执行内部效果 |
| `any_*` | 条件块 | 只要**任一**对象满足条件就返回 true |
| `count_*` | — | 统计数量（部分场景可用 `count = { }`） |

```
# 效果：给每个陆地行星加建筑
every_owned_planet = {
	limit = { is_planet_class = pc_continental }
	add_building = building_capital_1
}

# 触发器：只要有任意盖亚行星就成立
any_planet_within_border = { is_planet_class = pc_gaia }
```

常用迭代器名：`every_owned_planet` `every_owned_ship` `every_owned_fleet` `every_system_in_galaxy` `every_country` `every_pop` `random_owned_planet` `random_galaxy_planet` `random_rim_system` `any_owned_planet` `any_planet_within_border` `any_neighbor_system`。

### 作用域目标（保存 / 引用）

```
save_event_target_as = my_target            # 本命名空间内可引用
save_global_event_target_as = my_target     # 全局可引用
# 3.5+ 支持带 @scope 后缀：save_event_target_as = whatever@root

event_target:my_target = { ... }            # 引用
clear_global_event_target = my_target       # 清理
```

也可用 `set_variable` 存变量，在本地化里用 `[scope.var_name]` 读。

### 存在性检查

切换前建议检查，避免静默失败：

```
planet = {
	exists = owner          # 有主才继续
	owner = { ... }
}
```

## 二、条件块（Triggers）

条件返回 true/false，出现在：`trigger`、`limit`、`potential`、`allow`、`visible`、`abort_trigger`、scripted_triggers 等位置。

### 逻辑运算符

| 运算符 | 含义 | 备注 |
|--------|------|------|
| （默认） | 隐式 `AND` | 块内全部为真 |
| `AND` | 全部为真 | 可省略 |
| `OR` | 任一为真 | |
| `NOT` | 取反 | **只接受一条语句** |
| `NOR` | 全部为假才真 | 等价 `NOT = { OR = { ... } }` |
| `NAND` | 不全为真即为真 | 等价 `NOT = { AND = { ... } }` |
| `calc_true_if` | 至少 N 条为真 | `amount >= 3`，可用来实现 XOR |
| `if` / `else_if` / `else` | 条件分支 | 效果块中也有同名结构 |

```
trigger = {
	NOR = { has_ethic = ethic_fanatic_xenophile has_ethic = ethic_militarist }
	calc_true_if = {
		amount >= 3
		leader_class = scientist
		is_researching_area = society
		gender = female
		has_level > 2
	}
}
```

性能技巧：`AND` 里把最可能为假的条件放前面，`OR` 里把最可能为真的放前面（短路求值）。

### 比较运算符

`=` `>` `<` `>=` `<=` `!=`，两种写法都存在：

```
leader_age > 85
opinion = { who = FROM value <= -50 }
check_variable = { which = my_var value >= 10 }
has_resource = { type = minerals amount < 5 }
```

### 高频触发器速查

国家（country）：

```
has_country_flag = my_flag            # 可用 my_flag@from 追踪来源
has_technology = tech_zero_point_power
has_ethic = ethic_fanatic_materialist
has_civic = civic_beacon_of_liberty
has_origin = origin_prosperous_unification
has_edict = crystal_sonar
has_trait = leader_trait_carefree       # 用于领袖；国家层面指主导物种
is_ai = no
has_valid_civic = <civic>
is_at_war = yes
has_federation = yes
num_owned_planets < 5
has_resource = { type = minerals amount < 5 }
has_country_flag / has_global_flag
empire_size < 20
is_country_type = default
has_communications = from
```

行星（planet）：

```
has_building = yes / building_capital_3
has_district = yes / district_mining
is_capital = yes
planet_size < 20
has_planet_flag = my_flag
habitability = { who = PREV value > 0.6 }
is_planet_class = pc_gaia
free_housing > 5
num_pops > 10
```

领袖（leader）：

```
leader_class = scientist / admiral / general / governor / official
has_level > 2
leader_age < 85
is_male = yes
```

### 条件块与效果块的位置差异

同一关键字在不同块里语义不同：

- `planet = { ... }` 出现在**效果块**里 → 切到行星作用域执行效果。
- `planet = { ... }` 出现在**条件块**里 → 在行星作用域里判断条件。
- `if = { limit = { ... } ... }` 只在**效果块**中有效。
- `trigger` / `limit` / `potential` / `allow` 里只能放条件。

## 三、效果块（Effects）

### 流程控制

```
if = {
	limit = { <触发器> }
	<效果>
}
else_if = {
	limit = { <触发器> }
	<效果>
}
else = {
	<效果>
}
break = yes          # 中断当前效果块，阻止后续效果执行
```

（注：官方文档未列出独立 `else`，但引擎实际支持；`while` 循环不通用，需用事件链或 scripted_effects 递推实现。）

### 随机分支

```
random_list = {
	50 = { <效果> }
	20 = { <效果> }
	30 = { <效果> }
}
locked_random_list = { ... }   # 同作用域只随机一次
random_owned_planet = { limit = { ... } <效果> }
```

### 提示与隐藏

```
hidden_effect = { <效果> }        # 执行但不进 tooltip
custom_tooltip = my_loc_key       # tooltip 显示指定本地化
tooltip = { <效果> }              # 只显示 tooltip 效果
log = "debug string"              # 写入 game.log，调试用
```

### 高频效果速查

国家：

```
set_country_flag = my_flag
set_global_flag = my_global_flag
clear_country_flag = my_flag
add_resource = { resource = energy amount = 500 }   # 视版本，另有 add_monthly_resource_mult / clear_resources
give_technology = { tech = tech_desert_colonization message = yes }
add_modifier = { modifier = my_static_modifier months = 12 }
set_variable = { which = my_var value = 1 }
change_variable = { which = my_var value = 1 }
add_opinion_modifier = { modifier = my_op who = FROM }
country_event = { id = my_ns.1 days = 30 random = 30 }
create_fleet = { name = "My Fleet" effect = { set_owner = ROOT set_location = capital_scope } }
set_country_flag / set_timed_country_flag = { flag = x days = 365 }
```

行星 / 舰队 / 通用：

```
set_owner = <目标>
set_controller = <目标>
add_building = building_capital_1
add_building = { district = district_x zone = zone_y building = building_z }   # 4.0+ 区划内建筑
add_district = district_mining
add_blocker = { type = tb_quicksand }
remove_deposit = <key>
change_pc = pc_gaia
create_pop = { species = owner_species ethos = owner size = 1 }
add_modifier = { modifier = <key> days = 365 }
destroy_fleet = <目标>
set_star_flag = my_flag
set_planet_flag = my_flag
```

事件触发：

```
country_event = { id = ns.1 }                       # 在当前国家作用域触发
random_galaxy_planet = { planet_event = { id = ns.2 } }
country_event = { id = ns.3 days = 200 random = 100 }   # 延迟 200～300 天
country_event = { id = ns.4 days = 30 scopes = { from = fromfrom } }   # 3.0+ 覆盖调用作用域
fire_on_action = { on_action = my_on_action scopes = { from = THIS } } # 3.0+
```

延迟事件只在**执行前**检查条件，入队时不检查。

## 四、事件（Events）

### 文件结构

```
namespace = my_ns          # 放文件顶部（最佳实践）
                           # 一个文件可有多个 namespace

country_event = {
	id = my_ns.1           # 只能是 namespace.数字，不能含字母
	title = my_ns.1.name
	desc = my_ns.1.desc
	picture = GFX_evt_robot_assembly_plant
	is_triggered_only = yes
	trigger = { ... }
	immediate = { ... }
	option = { ... }
}
```

### 事件类型

| 类型 | 作用域 | 备注 |
|------|--------|------|
| `country_event` | 帝国 | 最常用 |
| `planet_event` | 行星 | |
| `fleet_event` | 舰队 | |
| `ship_event` | 舰船 | |
| `pop_group_event` | 人口 | **v4.0 起由 `pop_event` 改名** |
| `leader_event` | 领袖 | |
| `system_event` | 星系 | 3.0+ |
| `starbase_event` | 星际基地 | 3.0+ |
| `situation_event` | 局势 | |
| `pop_faction_event` | 派系 | |

### 关键字段

| 字段 | 说明 |
|------|------|
| `hide_window = yes` | 隐藏窗口，无需 title/desc；用于幕后逻辑 |
| `is_triggered_only = yes` | **不参与每日轮询**，只能被显式调用。强烈推荐 |
| `fire_only_once = yes` | 仍轮询，但只触发一次 |
| `trigger = { }` | 触发条件 |
| `immediate = { }` | 触发瞬间执行的效果；隐藏事件通常只需要这个 |
| `after = { }` | `option` 的**同级**字段，不论选哪个选项都执行（类似 finally） |
| `abort_trigger` / `abort_effect` | 条件成立时事件取消（消失），可定义取消时的效果 |
| `mean_time_to_happen` | MTTH 平均触发时间；**官方因性能问题不再推荐滥用** |
| `picture` | 事件图，用 `GFX_` sprite 名 |
| `custom_gui` / `custom_gui_option` | 绑定自定义 GUI 布局 |
| `diplomatic = yes` | 外交类事件样式 |
| `is_dialog_only` | 选项仅作对话展示 |

### MTTH 示例

```
mean_time_to_happen = {
	years = 100
	modifier = {
		factor = 0.1          # 平均时间缩到 10 年
		has_technology = tech_x
	}
}
```

### option 完整参数

```
option = {
	name = my_ns.1.a              # 本地化 key 或 OK 之类内置
	trigger = { ... }             # 不满足则选项不显示
	exclusive_trigger = { ... }   # 满足则禁用其他选项
	allow = { ... }               # 显示但置灰
	custom_tooltip = my_ns.1.a.tt
	tooltip = { <效果> }          # 只显示 tooltip
	hidden_effect = { ... }       # 执行但不显示在 tooltip（常放 set_flag）
	ai_chance = { factor = 0 modifier = { factor = 2 <条件> } }
	is_dialog_only = yes
	response_text = my_ns.1.desc
	default_hide_option = yes
}
```

**可见事件必须至少有一个 option**（哪怕只有 `name = OK`）。

### 触发其他事件

```
# 简单
random_galaxy_planet = { planet_event = { id = my_ns.2 } }

# 延迟（放在 option 的 hidden_effect 里）
option = {
	name = my_ns.1.b
	hidden_effect = {
		country_event = { id = my_ns.3 days = 400 random = 400 }
	}
}
```

## 五、On Actions（事件钩子）

把事件挂到游戏行为上。自建文件放 `common/on_actions/`，**文件与 on_action 名都应用 MOD 前缀避免冲突**（原版在同目录 `00_on_actions.txt`）。

```
# common/on_actions/zz_my_on_actions.txt
on_game_start = {
	events = {
		my_ns.1
	}
}

on_colonization_complete = {
	random_events = {
		100 = my_ns.5
		0 = my_ns.6        # 权重 0 表示不随机触发
	}
}
```

注册的事件必须写 `is_triggered_only = yes`。

也可在脚本里主动触发：

```
fire_on_action = { on_action = my_custom_on_action scopes = { from = THIS fromfrom = PREV } }
```

## 六、可复用宏

| 目录 | 用途 | 调用方式 |
|------|------|----------|
| `common/scripted_triggers/` | 复用条件 | `<name> = yes`（作为触发器） |
| `common/scripted_effects/` | 复用效果 | `<name> = yes`（作为效果） |
| `common/scripted_variables/` | 全局常量 | `@my_var` 引用 |
| `common/inline_scripts/` | 参数化内联片段 | `inline_script = { script = xxx ARG = yyy }` |
| `common/scripted_loc/` | 复用本地化字符串 | 在 loc 中用 `[<name>]` |

```
# scripted_triggers
my_is_strong_empire = {
	empire_size > 50
	num_owned_planets > 8
}
# 调用
trigger = { my_is_strong_empire = yes }
```

```
# scripted_variables
@my_cost = 500
@my_mult = 1.5
# 调用
cost = { unity = @my_cost }
```

```
# inline_scripts
inline_script = {
	script = my_script
	MY_PARAM = 10
}
```

> 注意：`scripted_loc` 内部**不能再使用方括号命令**（写了会原样打印）。在 scripted_effect / trigger 里写 loc 命令需转义为 `\\[This.GetName]`。

## 七、变量（Variables）

```
set_variable = { which = my_var value = 10 }
change_variable = { which = my_var value = -3 }
set_variable = { which = my_var value = { value = scope:other.variable } }   # 取其他作用域变量
check_variable = { which = my_var value >= 5 }
multiply_variable / divide_variable / round_variable
```

读取：`[scope.my_var]`（本地化）或 `value:my_var` / `variable:my_var`（脚本参数）。

局部变量（3.x+）：`set_local_variable` / `local_var:`，作用域是当前脚本块。

## 八、性能与最佳实践

1. **能不轮询就不轮询**：优先 `is_triggered_only = yes` + on_action，而不是 `mean_time_to_happen`。
2. **尽量少用 `every_*` 全银河遍历**，加 `limit` 缩小范围。
3. `AND` 中把最可能为假的条件前置，`OR` 中把最可能为真的前置。
4. 用 `NOR` / `NAND` 替代嵌套 `NOT`，减少求值层数。
5. 复杂逻辑抽成 `scripted_triggers` / `scripted_effects`，可读性和复用性都更好。
6. 用 `-debug_mode` 启动 + `script_profiler` 控制台命令定位性能瓶颈。
