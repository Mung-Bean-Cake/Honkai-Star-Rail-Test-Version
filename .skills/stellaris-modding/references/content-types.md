# 内容类型骨架速查

按「放哪个目录 → 字段怎么写」组织。所有 key 都建议加 MOD 前缀（如 `mymod_`）避免与他人冲突。

---

## 科技 technology/

`common/technology/xxx.txt`

```
tech_my_laser_1 = {
	area = physics                 # physics / society / engineering
	tier = 2                       # 0-5
	category = { particle_physics } # 子分类，可多个
	cost = 2000
	weight = 100
	prerequisites = { "tech_lasers_3" }
	potential = {                   # 是否可以出现
		is_regular_empire = yes
		NOT = { has_technology = tech_my_laser_2 }
	}
	weight_modifier = {
		modifier = {
			factor = 2
			has_trait = trait_my_genius
		}
	}
	ai_weight = { factor = 1 }
	prereqfor_desc = { ship = { title = "TECH_UNLOCK_..." desc = "..." } }
	unlock = {
		building = building_my_thing
		ship_component = my_component
		# 常见：building / ship_component / army / component_set / tradition_category
	}
	start_tech = no                 # yes 则开局即解锁
	is_rare = no                    # yes 则标为稀有（紫色）
}
```

本地化 key：`tech_my_laser_1`（名称）与 `tech_my_laser_1_desc`（描述）。

---

## 飞升天赋 ascension_perks/

```
ap_my_perk = {
	potential = {
		has_ascension_perk = ap_technological_singularity_researching   # 前置（可选）
	}
	possible = {                    # 可选门槛，不满足则显示但不可点
		has_tradition = tr_discovery_finish
	}
	# 奖励二选一：modifier 或 on_enabled
	modifier = {
		country_research_speed_mult = 0.1
	}
	# 或
	on_enabled = {
		country_event = { id = my_ns.10 }
	}
	ai_weight = { factor = 5 }
}
```

---

## 法令 edicts/

```
my_edict = {
	length = -1                     # -1 永久，1/10/... 为持续天数
	icon = GFX_edict_type_policy    # 或用自定义 sprite
	resources = {
		category = edicts
		cost = { unity = 10 }
		upkeep = { unity = 2 multiplier = value:edict_size_effect }
	}
	potential = { is_ai = no }
	allow = { }
	modifier = {
		country_resource_unity_mult = 0.1
		ship_weapon_damage = 0.25
	}
	ai_weight = { factor = 0 }      # 0 = AI 不会用
}
```

`length = -1` 表示常驻（无限期）。

---

## 决议 decisions/

```
my_decision = {
	icon = GFX_decision_icon_x
	resources = {
		category = decisions
		cost = { influence = 100 }
	}
	potential = { is_ai = no }
	allow = { has_resource = { type = alloys amount >= 500 } }
	effect = {
		add_resource = { resource = alloys amount = -500 }
		add_modifier = { modifier = my_mod months = 24 }
	}
	ai_weight = { factor = 0 }
}
```

---

## 建筑 buildings/

```
building_my_factory = {
	base_buildtime = 480
	category = building_capital        # 决定所在区划/类别
	capital = no                       # yes 表示首都专属
	building_sets = { building_set_my }
	# 4.0+ 常见：所在区域 zone
	# zone = zone_generator
	potential = { }
	allow = { }
	produced_resources = { minerals = 5 }
	upkeep_resources = { energy = 2 }
	job_my_job = { }                   # 提供的岗位
	country_modifier = { }             # 作用于国家的修正
	planet_modifier = { }              # 作用于行星的修正
	triggered_planet_modifier = {      # 条件化修正
		potential = { }
		planet_stability_add = 5
	}
	prerequisites = { tech_my_tech }
	destroyed_pops_reduction = ...
}
```

---

## 区划 districts/

> 权威字段表在游戏里：`<游戏根>/common/districts/00_DOCUMENTATION.txt`，比 wiki 准。4.4.x 的区划已经不是 `unit_amount` / `max_tier` / `zones = { 1 = ... }` 那套写法。

```
district_my_district = {
	base_buildtime = 480
	icon = district_my_district                   # 可省略（默认找同名图标），也可显式指定 sprite 名
	custom_gui = planet_district_entry_width_1    # N=1/2/3 控制 UI 宽度；也可填自定义 .gui 模板名
	# is_uncapped = { <trigger> }                 # 不写 = 无独立上限（跟行星总池）
	# shared_capacity_modifier = district_my_pool # 与同类区划共享同一个上限池

	zone_slots = {                                # 区划内部的区域槽；每个 slot 必须在该星球类上 unlock
		slot_city_government
		slot_my_slot
	}

	show_on_uncolonized = { }                     # 未殖民行星（殖民预览）上是否展示
	potential = { uses_district_set = <集合名> }   # 能否存在于该行星；**归属判定必须用 uses_district_set，不要用 is_planet_class**（见下）
	allow = { }                                   # 能否被建造
	destroy_trigger = { }
	on_built = { }                               # 行星作用域

	resources = {
		category = planet_districts              # 经济类别，见 common/economic_categories/
		produces = { trade = 2 unity = 1 }
		cost = { minerals = 800 alloys = 50 }
		upkeep = { energy = 1.5 minerals = 0.5 }
	}
	planet_modifier = {                           # 行星修正；岗位就在这里发
		planet_housing_add = 1000
		job_my_job_add = 200
	}
	triggered_planet_modifier = { potential = { } modifier = { } }

	convert_to = { district_city }                # 失效时转换目标（可选）
	conversion_ratio = 1

	ai_weight = { weight = 10000 }
	expansion_planner = yes                       # 是否出现在扩张规划器
	exempt_from_ai_planet_specialization = yes
}
```

### 归属判定：`uses_district_set`，不是 `is_planet_class`（实测结论）

区划「属于哪个星球」是**一对约定**，两边必须同名：

- 星球类里写 `district_set = X`
- 区划里写 `uses_district_set = X`（它是**触发器**，可放在 `potential` / `allow` / `show_on_uncolonized`，行星/船/殖民地作用域）

`common/districts/` 下**没有** `district_set` 字段，`uses_district_set` 也不是区划字段——它纯粹靠触发器反查星球类上的那个标签。原版 147 个区划里 **122 个**用这种写法。

**不要把 `is_planet_class = pc_X` 当成区划归属条件。** 原版**没有任何一个**区划用它；本项目实测在方舟上也**不生效**：同一个方舟行星上，原版那 4 张用 `uses_district_set = nomad` 的区划（居住甲板/反应堆阵列/方舟甲板/军械工程）正常显示并可建造，而模组 6 张写 `is_planet_class = pc_train` 的车厢**一张都不出现**，`error.log` 里还一片安静（只有贴图告警）。这类静默失效极难查，别踩第二次。

推论：**改了星球类的 `district_set` 就必须同步改所有引用它的 `uses_district_set`**（区划、`zone_slots` 的 `unlock`、`show_on_uncolonized`、`scripted_triggers`），否则整片内容静默消失。反查命令：

```bash
grep -rn "uses_district_set = <旧集合名>" <模组>/
```

**容量公式**：`NUM_DISTRICTS_BASE` + 行星尺寸 × `NUM_DISTRICTS_FROM_PLANET_SIZE` + `planet_max_districts_add`（见 `common/defines/00_defines.txt`）。不写 `is_uncapped` 就是无独立上限；写了则由建筑 / 矿床对 `<区划名>_max_add` / `_max_mult` 累加。跑一次游戏后在 `logs/script_documentation/modifiers.log` 搜 `district_<区划名>_max_add`，即可确认引擎认不认这个名字。

---

## 岗位 pop_jobs/

```
my_job = {                          # 定义名不带 job_ 前缀（修正名 / 图标名却都带）
	category = specialist              # ruler / specialist / worker / complex_drone / simple_drone ...
	swappable_data = {
		default = {
			condition_string = RULER_JOB_TRIGGER
			building_icon = building_capital
		}
	}
	can_be_automated = no
	tags = { }                         # 见 common/job_tags/；空 tags 原版也在用

	possible_pre_triggers = {
		has_owner = yes
		is_being_purged = no
		is_being_assimilated = no
		is_sapient = yes
	}
	possible_precalc = can_fill_specialist_job   # 取值定义在 common/game_rules/00_rules.txt

	resources = {
		category = planet_jobs_specialist          # 经济类别，见 common/economic_categories/
		produces = { energy = 5 unity = 2 influence = 0.15 }
		upkeep = { food = 1 consumer_goods = 1 }
	}
	planet_modifier = { planet_stability_add = 0.01 }
	country_modifier = { country_naval_cap_add = 5 }
	weight = { weight = 3000 }          # 越大越优先被填满
}
```

- **资源名合法性**：引擎为每个 `(经济类别, 资源)` 组合生成 `<类别>_<资源>_produces_mult`。跑一次游戏后到 `logs/script_documentation/modifiers.log` 搜 `<你的类别>_<资源>_produces_mult` —— 在，就说明该资源能在该类别下产出（`influence` 就是这样确认合法的；反过来也能从这份清单反推出全游戏可产出资源全集，含 `advanced_logic` / `astral_threads` / `biomass` / `menace` 等 DLC 资源，给没买 DLC 的玩家写这些键要谨慎）。
- **图标**：`gfx/interface/icons/jobs/job_<岗位key>.dds` 自动注册为 `GFX_job_<岗位key>`，不用写 `.gfx`。
- **本地化**：`job_<k>` / `_plural` / `_desc` / `_icon`(=`"£job_<k>£"`) / `_with_icon` / `_plural_with_icon` / `mod_job_<k>_add` / `mod_job_<k>_per_pop` / `mod_job_<k>_per_pop_short`；`_per_pop_short` 里要用**字面 `\n`**，不是真换行。
- **给岗位**：由区划 / 建筑的 `planet_modifier = { job_<key>_add = N }` 提供。

---

## 静态修正 static_modifiers/

```
my_static_modifier = {
	icon = "gfx/interface/icons/modifiers/mod_my.dds"
	icon_frame = 1
	country_resource_energy_mult = 0.1
	pop_happiness = 0.05
	custom_tooltip = my_static_modifier_tt
	show_only_custom_tooltip = no
}
```

应用方式：

```
add_modifier = { modifier = my_static_modifier months = 12 }
add_modifier = { modifier = my_static_modifier }          # 永久
```

也可被任意 modifier 块以 key 引用：`my_static_modifier = 1.5`（等于把内部数值乘 1.5）。

**本地化 key 必须叫 `my_static_modifier`**，图标放 `gfx/interface/icons/modifiers/`。

> 自动生成类修正需加 `mod_` 前缀：例如 economic category 生成的修正本地化为 `mod_<name>`。

---

## 物种特质 traits/

```
trait_my_trait = {
	cost = 2
	potential = { }
	allowed_archetypes = { BIOLOGICAL }    # BIOLOGICAL / MACHINE / ROBOT / LITHOID ...
	modifier = {
		pop_growth_speed = 0.1
	}
	icon = "gfx/interface/icons/traits/my_trait.dds"
	random_weight = { base = 4 }
	incompatible = { trait_slow_breeders }
}
```

领袖特质：

```
leader_trait_my_leader = {
	cost = 1
	leader_trait = yes
	modifier = { country_research_speed_mult = 0.05 }
	icon = "gfx/interface/icons/traits/leader/..."
}
```

---

## 民政 / 政体 governments/

`common/governments/civics/xxx.txt`

```
civic_my_civic = {
	potential = {
		ethics = { value = ethic_fanatic_materialist }   # 需要特定思潮
	}
	possible = { }
	random_weight = { base = 4 }
	modifier = {
		country_research_speed_mult = 0.1
	}
	# 或
	on_enabled = { ... }
	triggered_country_modifier = {
		potential = { has_technology = tech_x }
		country_research_speed_mult = 0.05
	}
}
```

---

## 起源 origins/

`common/governments/origins/xxx.txt`（部分版本在 `common/governments/`）

```
origin_my_origin = {
	is_origin = yes
	potential = { }
	possible = { has_valid_civic = ... }
	random_weight = { base = 0 }
	# 开局效果
	on_game_start = {
		country_event = { id = my_ns.100 }
	}
	starting_system = my_system_initializer     # 可选：替换开局星系
	modifier = { }
}
```

---

## 传统 traditions/ 与 tradition_categories/

```
# common/tradition_categories/
tradition_my_tree = {
	name = "TRADITION_TREE_MY"
	tradition_desc = "..."
	icon = "gfx/interface/icons/tradition_trees/my.dds"
	color = { 100 200 255 }
	potential = { }
	area = society                 # physics / society / engineering
	adopt = { modifier = { ... } }
	finish = { modifier = { ... } }
}

# common/traditions/
tradition_my_1 = {
	tradition_category = tradition_my_tree
	slot = 1
	# 或 prerequisites = { tradition_my_0 }
	modifier = { }
}
```

---

## 舰船尺寸 ship_sizes/

```
my_ship_size = {
	ship_size_group = my_group          # 需在 ship_size_groups 中定义
	is_space_station = no
	max_hitpoints = 800
	combat_max_hitpoints = 800
	speed = 160
	acceleration = 0.3
	rotation_speed = 0.1
	ship_construction_type = starbase_shipyard
	equipment_slots = { ... }
	component_slot = {                  # 槽位
		name = "MY_LARGE_1"
		size = large
		slot_type = weapon
		}
	resources = { category = ships cost = { alloys = 200 } upkeep = { energy = 3 } }
	icon_frame = 1
	sprite = "my_ship_entity"           # 指向 gfx/models 中的实体
	prerequisites = { tech_my_ship_tech }
}
```

配套还需要：`common/ship_size_groups`、`gfx/models/ships/` 下的 `.mesh` / `.asset` / `.gfx`、`interface/` 里的 sprite 定义。**舰船是 MOD 里最重的部分**，建议直接复制现成 MOD 或原版文件改造。

---

## 舰船部件 component_templates/

```
my_weapon_1 = {
	slot = large
	size = large
	type = weapon
	icon = "gfx/interface/icons/ship_parts/..."
	component_set = my_component_set       # 需在 component_sets/ 定义
	icon_frame = 1
	power = -30
	cost = { alloys = 50 }
	damage = { min = 20 max = 40 }
	windup = { min = 1 max = 2 }
	cooldown = { min = 3 max = 4 }
	accuracy = 0.75
	tracking = 0.3
	health = 200
	prerequisites = { tech_my_weapon_tech }
	ai_weight = { weight = 10 }
	tags = { weapon_type_energy }
}
```

`common/component_sets/` 中的套装定义图标与命名：

```
my_component_set = {
	key = "my_weapon_1"
	icon = "GFX_ship_part_laser_1"
	icon_frame = 1
	prerequisites = { "tech_my_weapon_tech" }
}
```

---

## 巨构 megastructures/

```
my_megastructure = {
	build_cost = { alloys = 5000 influence = 100 }
	build_time = 1800
	upgrade_from = { }                 # 前置阶段（多级巨构用列表）
	upgrade_to = { my_megastructure_2 }
	resource_cost = { }
	placement_rules = { planet_possible = { ... } }
	potential = { }
	# 效果
	country_modifier = { }
	station_modifier = { }
	on_build_start / on_build_complete = { }
	prerequisites = { tech_mega_engineering }
	type = ring_world
}
```

---

## 异常 anomaly 与考古考古遗址

```
# common/anomalies/my_anomalies.txt
my_anomaly_category = { ... }      # 分类

my_anomaly = {
	level = 3
	desc = my_anomaly_desc
	on_success_or_fail = ...
	# 由 events/ 中的事件执行实际逻辑
}

# common/archaeological_site_types/
my_arch_site = {
	potential = { is_planet_class = pc_desert }
	stages = { 1 2 3 4 }
	stage_1 = { ... }
}
```

---

## 特殊项目 special_projects/

```
my_special_project = {
	cost = 100
	trigger = { ... }
	on_success = { country_event = { id = my_ns.50 } }
	on_fail = { }
	requirements = { }
	event_scope = planet
}
```

---

## 天灾 crisis / country_types

`common/country_types/` 定义特殊势力类型：

```
my_crisis_country = {
	icon = "gfx/interface/icons/country_types/my.dds"
	country_type = crisis          # default / fallen_empire / crisis 等
	ship_prefix = "MY"
	has_federation = no
	potential = { }
	on_government_change = { }
}
```

天灾通常还需要：`common/on_actions/` 里的触发钩子、`events/` 里的阶段事件、`common/solar_system_initializers/` 的出生星系、`common/game_rules/` 的规则开关。

---

## 帝国预设 / 星系初始生成

```
# common/solar_system_initializers/
my_system_init = {
	name = "My System"
	class = "rl_standard_stars"
	init_effect = {
		# 用效果生成星球
		create_system = ...
	}
}
```

```
# prescripted_countries/
my_country = {
	name = "My Country"
	adjective = "My"
	spawn_as_fallen = no
	flags = { }
	country_type = default
	government = gov_my
	origin = origin_my_origin
	ethics = { ethic_fanatic_materialist ethic_xenophile }
	civics = { civic_my_civic }
	authority = auth_democratic
	planet_name = "My Homeworld"
	planet_class = pc_continental
	initializer = my_system_init
}
```

---

## 名称表 name_lists/

```
my_name_list = {
	randomized = no
	ship_names = { ... }
	planet_names = { ... }
	army_names = { ... }
	fleet_names = { ... }
}
```

---

## 通用建议

1. **新内容一律加 MOD 唯一前缀**，key 冲突是 MOD 互斥的头号原因。
2. **每个 key 都要本地化**，否则游戏里显示裸 key。
3. **图标缺失不报错但很难看**：`gfx/interface/icons/<类型>/` 下放同名 `.dds`，并在 `interface/*.gfx` 注册 sprite。
4. **不确定字段时，去游戏安装目录抄原版对应文件**——这是最快也最可靠的做法。原版文件在 `…\Steam\steamapps\common\Stellaris\common\`。
