# 进阶系统速查：星界裂隙 / 局势 / 异常 / 前 FTL 文明 / 虫洞

> 本文件所有结论都在 **Stellaris v4.4.6 (Pegasus)** 上用「原版 `common/` + `events/` 全文检索」与
> `~/Documents/Paradox Interactive/Stellaris/logs/script_documentation/{effects,triggers,scopes,modifiers}.log`
> 双向交叉验证过。**不要凭记忆写这几个系统**——它们的字段语义在 v4.x 里改动过，写错大多**静默失效**。

排查顺序：先查 `logs/script_documentation/effects.log` / `triggers.log` / `scopes.log`（本次启动实时重刷，
比 wiki 准），再用 `grep` 在原版目录里找一个**同类型实例**照抄结构。找不到同类型实例的字段，
一律视为不可靠。

---

## 1. 星界裂隙（Astral Rift，需 Astral Planes DLC）

### 1.1 定义裂隙 `common/astral_rifts/<名字>.txt`

```pdx
my_rift = {
    name = my_rift                 # 本地化键
    randomized = no                # no ⇒ 不进随机抽取池（只能被显式 spawn）
    flags = { my_rift_flag }       # 裂隙旗标，可用 has_astral_rift_flag 查
    event = my_rift.1              # 探索起点事件
    on_roll_failed = {
        standard_astral_rift_on_roll_failed = yes   # 原版现成效果，别自己写
    }
}
```

- **想让裂隙只由自己 spawn**：**不要写 `event_weight`**，并写 `randomized = no`。原版 `riftworld` 就是这种写法。
- 要参与随机抽取才写 `event_weight = { weight = 1 }`。

### 1.2 生成 / 摧毁裂隙（作用域：`galactic_object`）

```pdx
# 在某个星系里生成指定裂隙
my_system = {
    spawn_astral_rift = {
        id = my_rift                # 省略或写 none ⇒ 探索开始时随机抽一个
        orbit_distance = 100
        orbit_angle = 320           # 原版也常用 360
        random_pos = yes            # 与 relative_to / in_place_of 互斥
        init_effect = { set_astral_rift_flag = my_rift_flag }
    }
}
# 摧毁
my_system = { astral_rift = { destroy_astral_rift = this } }
```

- `astral_rift` 作用域由 `galactic_object`（或 `leader`）进入，取「同星系中的那个裂隙」。
- `destroy_astral_rift = <target>` 支持 `all` 作用域，`this` 也合法。

### 1.3 裂隙事件链 `events/*.txt`

```pdx
namespace = my_rift

astral_rift_event = {
    id = my_rift.1
    title = my_rift.1.name
    desc = my_rift.1.desc
    picture = GFX_evt_astral_rift_riftworld
    show_sound = ap_rift_event_0_astral_wonder
    difficulty = 0                 # 原版 @astral_rift_initial_difficulty = 0，直接用 0 即可
    astral_rift = yes
    is_triggered_only = yes

    option = {
        name = my_rift.1.a
        set_astral_rift_flag = my_stage_1
        explorer = {               # explorer = 正在探索的这个国家
            set_country_flag = xxx
        }
        set_next_astral_rift_event = { id = my_rift.2 }
    }
}

astral_rift_event = {
    id = my_rift.2
    # ...
    option = {
        name = my_rift.2.a
        finish_astral_rift = yes   # 作用域 astral_rift，结束探索
    }
}
```

- `explorer` 是裂隙作用域下的关键字，指向"探索它的那个国家"（`scopes.log`: *Scopes from an astral rift to the country whose leader is exploring*）。
- `finish_astral_rift = yes` 不销毁裂隙，只是结束探索；要它消失仍需 `destroy_astral_rift`。
- 想让裂隙**每次探索都从同一张事件图开始**：`event = <首事件>` 即可，无需 register 到 on_action。

### 1.4 相关 on_action 作用域（**全部 `THIS = Country`，不是 ship！**）

| on_action | 作用域 |
|---|---|
| `on_astral_rift_exploration_start` | `THIS = Country`（探索国）/ `FROM = AstralRift` / `FROMFROM = Fleet` |
| `on_astral_rift_exploration_complete` | 同上 |
| `on_astral_rift_pre_event_fire` | 同上 |

在同名 `on_action` 里追加事件是**合并**语义（多文件、同文件多块都会累加），不会覆盖原版。

---

## 2. 局势（Situations）

权威说明：`common/situations/99_README_SITUATIONS.txt`。**动局势前先读它。**

### 2.1 进度条模型（最容易写错的地方）

- 进度条范围是 **[`start_value`, 最后一段 stage 的 `end`]**，向右为完成。
- `start_value` = **最小值（失败端）**，默认 0。
- `initial_progress` = **开局位置**；若小于 `start_value` 会被抬到 `start_value`。
- `progress_direction` = `monodirectional`（默认）/ `bidirectional`。
  - 单向：从 `initial_progress` 涨到终点 = 完成，永远不会"失败"。
  - 双向：向 0/`start_value` 掉 = **失败**（触发 `on_fail`），涨到终点 = **完成**（`on_progress_complete`）。
  - `complete_category` / `fail_category` 只在双向时有效。
- **数值化的"倒计时"局势正确写法**（例：什么都不做 1200 个月后失败）：

```pdx
my_countdown_situation = {
    progress_direction = bidirectional
    start_value = 0            # 左端 = 失败
    initial_progress = 1200    # 开局在正中（条长 2400）
    complete_category = positive
    fail_category = negative

    stages = {
        stage_1 = { icon = GFX_situation_stage_1 end = 1300 }
        stage_2 = { icon = GFX_situation_stage_2 end = 1900 }
        stage_3 = { icon = GFX_situation_stage_3 end = 2400 }   # 右端 = 完成
    }

    monthly_progress = {
        base = -1              # 什么都不做 → 1200 个月掉到 0
        modifier = { desc = ... current_situation_approach = approach_invest   add = 9 }
        modifier = { desc = ... current_situation_approach = approach_contain  add = 1 }
    }
    approach = {
        name = approach_invest
        icon = GFX_situation_approach_research
        resources = { category = situations upkeep = { energy = 40 minerals = 40 alloys = 10 } }
        ai_weight = { base = 100 }
    }
    approach = { name = approach_contain icon = GFX_situation_approach_fist resources = { category = situations upkeep = { energy = 15 } } ai_weight = { base = 10 } }
}
```

> ❌ 反面写法：`start_value = -1200 / initial_progress = 0`。虽然"数值上"也是 1200 个月，
> 但开局位置 = `0 - (-1200) / (300 - (-1200))` = 80%，进度条一开始就贴着完成端，**视觉完全错**，
> 而且 stage 的 `end` 会落在起点左侧导致开局就处于后面的 stage。

### 2.2 字段清单

```pdx
my_situation = {
    picture = GFX_evt_xxx
    category = negative | neutral | positive
    situation_log_category = developments | empire_concerns | urgent_matters | crises | ambitions | astral_rifts
    complete_icon / complete_icon_frame / fail_icon / fail_icon_frame = GFX_situation_*
    potential = { }            # country 作用域；为假时局势会被移除（**不触发 on_abort**）
    abort_trigger = { }        # ⚠️ 语义是「满足即中止」，不是「满足才继续」
    on_start / on_progress_complete / on_fail / on_abort = { }
    permanent = yes/no         # yes ⇒ 到端点也不自动结束
    show_in_outliner = yes/no
    stages = { }               # 每段必须 <key>_desc / 名字本地化；支持 icon / icon_background / end / custom_tooltip
    monthly_progress = { base = 0 modifier = { desc = ... <触发器> add = n } }
    approach = { name = ... icon = ... icon_background = ... default = yes resources = { category = situations upkeep = { ... } } ai_weight = { base = n } }
}
```

- **`abort_trigger` 是"中止条件"**。写成 `abort_trigger = { exists = owner }` 会**立刻中止**（因为恒为真）；
  永远不要中止就干脆不写这个字段。
- 局势作用域里 `owner` = 承载该局势的国家（`scopes.log` 支持从 `situation` 取 `owner`）。
- 相关效果/触发器（均在 **situation** 作用域）：`add_situation_progress = n`、`set_situation_progress = n`、
  `set_situation_flag`、`has_situation_flag`、`is_situation_type`、`current_situation_approach`、`destroy_situation = this`。
  在**国家**作用域遍历：`any_situation` / `every_situation` / `random_situation`。
- 开启：`start_situation = { type = <key> }`（国家作用域）。
- 本地化必需键：`<key>`（标题）、`<key>_type`、`<key>_desc`、`<key>_monthly_change_tooltip`；stage 名与 `_desc` 可选。
- 图标：`GFX_situation_stage_1..3`、`GFX_situation_stage_frame_{blue,green,red}`、
  `GFX_situation_approach_{research,fist,shrug}`、`GFX_situation_approach_bg_{green,yellow,red}`、
  `GFX_situation_outcome_{positive,negative,unknown,meh}`、`GFX_situation_outcome_frame_{green,red,blue}`。

---

## 3. 异常现象（Anomalies）

### 3.1 定义分类 `common/anomalies/*.txt`

**仅由脚本投放**的异常照抄原版 `ASTRAL_SCAR_CAT` 写法：

```pdx
MY_CAT = {
    desc = my_cat_desc              # 或 "<key>_desc" 形式
    picture = GFX_evt_xxx
    level = 1..8                    # 原版取值范围
    spawn_chance = { base = 0 }     # base = 0 ⇒ 永不随机生成
    max_once_global = yes           # 全局只允许存在一个
    on_success = my_ns.210          # 必须是 ship_event！见下
}
```

### 3.2 投放与作用域

```pdx
# 行星作用域
some_planet = { add_anomaly = { category = MY_CAT } }   # 可选 target = target:country 指定归属国
```

- **`on_success = <事件>` 投出的是 `ship_event`**（已核过原版全部 `on_success` 目标均为 `ship_event`）。
  作用域：`ROOT = Ship`（科考船）/ `FROM = Planet` / `owner = Country`。
  事件里写 `location = from`、`owner = { ... }`。
- `prevent_anomaly = yes`（行星效果，禁用**随机**异常生成）与 `add_anomaly` 在语义上是两件事，
  但**如果这颗星必须是脚本异常的唯一载体，稳妥做法是不要给它加 `prevent_anomaly`**，免得被连带挡掉。
  初始器级还有一个 `prevent_anomalies = yes`（注意复数），同样是禁随机生成。

---

## 4. 前 FTL 原始文明（Pre-FTL / Primitive）

**标准流水线**（`common/scripted_effects/pre_ftl_scripted_effects.txt` 里 `generate_pre_ftls_on_planet` 即此结构）：

```pdx
create_species = {
    name = "MY_SPECIES_KEY"
    plural = "MY_SPECIES_PLURAL_KEY"
    class = MY_SPECIES_CLASS
    portrait = my_portrait_id
    homeworld = event_target:my_planet
    traits = { trait = "trait_my_bonus" }
    sapient = yes
    namelist = random
    effect = { save_global_event_target_as = my_species }
}

create_country = {
    name = "MY_COUNTRY_KEY"
    adjective = "MY_COUNTRY_ADJ_KEY"
    authority = random
    civics = random
    species = last_created_species
    ethos = { ethic = ethic_fanatic_spiritualist ethic = ethic_xenophile }
    flag = random
    graphical_culture = MY_GFX_CULTURE          # 可选
    city_graphical_culture = MY_GFX_CULTURE     # 可选
    origin = "origin_default_pre_ftl"
    type = primitive
    day_zero_contact = no
    effect = {
        save_global_event_target_as = my_country
        set_country_flag = machine_age          # 时代旗标
        set_pre_ftl_age = machine_age           # 时代的建筑/人口分支
    }
}

# ⚠️ 必须在行星作用域调用，且紧接着调用（它依赖 last_created_country / last_created_species）
event_target:my_planet = {
    setup_pre_ftl_planet = yes       # set_owner = last_created_country + set_capital + 按时代铺建筑与人口
    pre_ftl_clean_up_effect = yes    # 原版配套收尾（subterranean / mechanists 特判）
    add_anomaly = { category = MY_CAT }
    add_modifier = { modifier = my_modifier days = -1 }
}

# 给领袖起名/换肖像（原始文明也有 ruler）
last_created_country = {
    if = { limit = { exists = ruler } ruler = { set_name = "NAME_X" set_gender = female change_leader_portrait = my_portrait } }
}
```

- 时代可选值：`stone_age` / `bronze_age` / `iron_age` / `late_medieval_age` / `renaissance_age` /
  `steam_age` / `industrial_age` / `machine_age` / `atomic_age` / `early_space_age`（各分支在
  `setup_pre_ftl_planet` 里，`machine_age` 在 `pre_ftl_scripted_effects.txt:1043`）。
- `set_pre_ftl_age = <age>` 是独立效果，对非前 FTL 国家什么都不做。

### 4.1 让原始文明"觉醒"成为正常帝国：`achieve_ftl_effect`

```pdx
event_target:my_country = {
    achieve_ftl_effect = yes
    set_name = "MY_COUNTRY_KEY"                  # 见下方副作用
    founder_species = { set_graphical_culture = MY_GFX_CULTURE }
    ruler = { set_name = "NAME_X" set_gender = female change_leader_portrait = my_portrait }
    establish_communications_no_message = root
    set_subject_of = { who = root preset = preset_vassal allow_instant_negotiation = yes }
}
```

**`achieve_ftl_effect`（`pre_ftl_scripted_effects.txt:3087`，无参数）的副作用必须知道：**

1. `remove_country_flag = early_space_age`、`set_country_type = default`、`set_origin = origin_default`
   （若原本是 `origin_default_pre_ftl`）、`change_government = { authority = random civics = random }`。
2. **`set_name = random`** —— 国名会被随机化，想在剧情里保留自定义国名必须**在效果之后**重新 `set_name`。
3. **`set_species_graphical_culture = yes`** —— 内部按 `is_species_class` 分支，遇到非原版物种类会落到
   `default = mammalian_01`，**会覆盖自定义 graphical_culture**。必须事后
   `founder_species = { set_graphical_culture = <你的文化> }` 修正（`founder_species` 是国家→建国物种作用域）。
4. 首都 `clear_blockers` + `remove_all_buildings` + `generate_start_buildings_and_districts`，
   并连发 `game_start.70/71/72`（议会/总督），可能重建领袖 —— 所以**命名领袖的操作要放在效果之后**。
5. 结束时给一笔按 `years_passed` 放大的资源、科考船、建造船。

---

## 5. 虫洞 / 星门 等 Bypass

```pdx
# galactic_object 作用域
spawn_natural_wormhole = {
    bypass_type = wormhole            # 或 sealed_wormhole
    random_pos = yes                  # 或 orbit_distance / orbit_angle；或 in_place_of = <目标>
}
link_wormholes = event_target:other_system    # 把本星系的虫洞连到目标星系的虫洞
```

- `has_natural_wormhole = yes` 判断星系是否已有虫洞（用来做幂等）。
- 国家作用域：`add_seen_bypass_type = wormhole` 让帝国"见过"该类型；虫洞稳定化科技是
  `tech_wormhole_stabilization`（`give_technology = { tech = tech_wormhole_stabilization message = no }`）。
- 天然虫洞的图形是引擎自带的，**不需要自己写 `interface/*.gfx`**。

### 5.1 强制「调查星系」+（按需）「建立恒星基地」（游牧帝国的破局点）

游牧（`is_nomadic = yes`）在引擎层不允许宣称/拥有星系，用工程船下建造订单只会走到 100% 然后失败，
`error.log` 里什么都不留。**但脚本效果可以直接把这两件事按上去：**

```pdx
# galactic_object（星系）作用域
set_surveyed = { surveyed = yes surveyor = root }        # 也可 surveyed = no

# ⚠️ 恒星基地要按设计决定，不要顺手加也不要顺手砍：
#    · 想要「该星系立刻归我」→ 加上（本项目的 DOTGI 提瓦特裂隙就要求发现当天建基地）；
#    · 想让该星系保持孤立/中立、留给别人 → 只写 set_surveyed；
#    · 用户只说「完成调查」时，先确认要不要基地，别默认加或默认不加。
if = {
    limit = { NOT = { any_starbase_in_system = { always = yes } } }   # 幂等：已有基地就别重复建
    create_starbase = {
        owner = root
        size = starbase_outpost                          # 或 starbase_starport / starbase_starhold ...
    }
}
```

- `set_surveyed` 支持 `galactic_object` / `planet` / `astral_rift` 三种作用域；`surveyor` = 接受调查结果的国家。
- `create_starbase` 支持 `galactic_object` / `planet`；字段为
  `owner` / `size` / `design` / `module`（可重复）/ `building`（可重复）/ `effect = { ... }`。
  原版用例：`events/shroud_events.txt`、`events/origin_events_5.txt`、`events/synthetic_dawn_events.txt`。
- 星系里"有没有恒星基地"用 `any_starbase_in_system = { <triggers> }`（`galactic_object`）——
  原版**没有**叫 `has_starbase` 的触发器，用 `always = yes` 当占位触发器即可。
- 星系作用域的 `set_visited = <country>` 给"访问过"的低强度情报（国家作用域）。

### 5.2 让一个新生国家当附庸 / 朝贡国

```pdx
# 当前 scope = 附属国；who = 宗主
set_subject_of = {
    who = root                       # 宗主
    preset = preset_vassal           # 或 preset_tributary / preset_protectorate / preset_scion ...
    allow_instant_negotiation = yes  # 立即生效，不走外交弹窗
}
```

- 常用 preset：`preset_vassal`、`preset_tributary`（朝贡国：纳贡但内政外交独立）、
  `preset_protectorate`（原版前 FTL 觉醒用它）、`preset_satrapy`、`preset_subsidiary`、`preset_scion`。
- **附庸 ≠ 吞并**：对方依旧是独立国家，依旧拥有自己的首都星球。
  想在事件里给玩家"附庸 / 朝贡"二选一，就把 `set_subject_of` 分别放进两个 `option`
  （`option = { name = X custom_tooltip = Y <effects> }`，原版支持 option 里写 `custom_tooltip`，
  见 `events/anomaly_events_1.txt:1632`）。
- 觉醒一个前 FTL 国家后再附庸，正确顺序：`achieve_ftl_effect = yes` → 修回国名/肖像文化 →
  `establish_communications_no_message = root` → `set_subject_of = { who = root ... }`。

### 5.3 直接配发科技

```pdx
give_technology = { tech = tech_rift_sphere message = no }           # 探索星界裂隙的前置科技
give_technology = { tech = tech_wormhole_stabilization message = no }
add_seen_bypass_type = wormhole                                       # 让帝国"见过"虫洞
```

- `tech_rift_sphere`（`common/technology/00_astral_planes_tech.txt`）的
  `potential = { has_astral_planes_dlc = yes }`，给之前先 `limit = { has_astral_planes_dlc = yes }` 更干净。
- 能不能过虫洞看的是 `common/bypass/00_bypasses.txt` 里该 bypass 的 `prerequisites`
  （`wormhole` 与 `starlit_wormhole` 都是 `tech_wormhole_stabilization`）。

### 5.4 ⚠️ 用脚本批量改 `.yml` 的最大坑

Stellaris 的 yml 里要的是**字面的两个字符** `\n`。用 Python 写的时候写成 `'...\n...'`
会变成一个**真正的换行**，把一行拆成多行、并把 CRLF 弄成 LF 混排（游戏只解析第一行，后面全丢）。
**必须写 `'\\n'`**（或用 `r'...'`）。写完立即断言：

```python
assert raw.count(b"\n") == raw.count(b"\r\n")        # 没有 LF 混排
assert all(l.rstrip().endswith('"') for l in text.split("\n") if l.strip() and not l.lstrip().startswith(("#", "l_")))
```

### 5.5 ⚠️ 原版会悄悄把你的行星判给别人（`action.85`「混合归属星系」）

原版 `events/on_action_events_1.txt` 里有一条隐性规则链：`action.85` → `action.86` → `action.87/88`。

- **规则**：若某行星的拥有者是 `default` / `fallen_empire` / `awakened_fallen_empire` 类型，
  而**该行星所在星系的恒星基地属于另一个同类国家**（且双方不在战争中），
  这颗行星会被**直接判给恒星基地所有者**（`action.86` 里就一句 `set_owner = starbase.owner`），
  并给双方各发一条通知（`action.88.desc`：*"我们已获得了[星球]的行政控制权……如今我们控制了[星系]星系的恒星基地"*）。
- **最大的坑**：判定**只看「恒星基地所有者」，完全不看宗主/附庸关系** ——
  哪怕目标国是你的附庸，只要基地是你的，它的母星照样会被判给你。
- **`primitive` 类型不受影响**：所以前 FTL 土著的母星在你建了基地之后依然安全；
  但它一旦 `achieve_ftl_effect` 变成 `default`，下一轮就可能被划走 ——
  **故障总是延迟出现，测试时极容易漏掉。**
- 想让某个新生国家保住母星，**唯一可靠做法是让它拥有自己母星系的恒星基地**：

```pdx
# 新生国家作用域内（必须在 achieve_ftl_effect 之后调用）
event_target:my_system = {
    every_starbase_in_system = {
        limit = { NOT = { owner = { is_same_value = event_target:my_country } } }
        set_owner = event_target:my_country          # set_owner 支持 starbase 作用域
    }
}
```

- `every_starbase_in_system` 的作用域是 `galactic_object`（星系）；
  `set_owner` 的 Supported Scopes 明确包含 `starbase`（`effects.log:45`）。
- 只要**行星所有者 == 星系恒星基地所有者**，`action.85` 就不会触发，母星永久安全；
  顺带这也让玩家无法再在该星系建基地。
- 反过来：想让"帝国占着基地、土著留着行星"，在 vanilla 规则下**不可能长期共存** ——
  只能二选一（要么基地归土著，要么行星归帝国）。

---

### 5.6 给国家设置旗帜（emblem）：两种写法，别混用

旗帜（视觉国徽）**不是** `set_country_flag`（那是布尔标记），它由 **emblem 定义块**决定：

```pdx
# 运行时（create_country / change_country_flag）都只接受「内联块」或字面量 random
flag = {                      # create_country 的参数
# change_country_flag = {     # 运行时改旗的效果，结构完全相同
    icon       = { category = "DOT_SR"      file = "DOT_SR_03.dds" }   # category = flags/ 下的子文件夹
    background = { category = "backgrounds" file = "00_solid.dds"  }
    colors     = { "white" "black" "null" "null" }                     # 颜色名取自 flags/colors.txt
}
```

**坑 1：`common/prescripted_flags/` 的键在运行时无效。**
`empire_hsr_10 = { flags = { ... } }` 这类键只服务于主菜单 pre-scripted 帝国
（`prescripted_countries/*.txt`）；而且即便在那些文件里，真正出图的也是旁边的
**`empire_flag = { … }`** 块，`flag = empire_*` 只是老写法（原版很多条目根本不写）。
运行时 `create_country { flag = empire_xxx }` 引擎**静默忽略**，`error.log` 里什么都不留。
✅ 原版运行时建国的全部写法都是内联块，连最接近"造一个前 FTL 土著"的场景也是：
`pre_ftl_scripted_effects.txt:506 / 601 / 756`（`create_very_early/early/late_pre_ftl_empire`），
另有 `flag = random`（`events/astral_rifts_1_events.txt:3840`）。

**坑 2：`achieve_ftl_effect` 会把旗帜随机重掷。**
`common/scripted_effects/pre_ftl_scripted_effects.txt:3087` 的 `achieve_ftl_effect` 内部：
`change_country_flag = random`（:3101）、`set_name = random`（:3107）、
`change_government = { authority = random civics = random }`（:3103）。
⇒ 原始文明一觉醒，旗、名、政体全部被随机化。想让新国家保持自己的旗/名，
**必须在 `achieve_ftl_effect` 之后手动改回来**（`set_name` + `change_country_flag = { … }`）。

**坑 3：`.dds` 必须是「真正的 DDS」，把 PNG 改个后缀不算。**
`empire_flag.cpp:918 / :924` 的 `could not find …-sized texture` 只做**文件存在性**检查，
所以一个内容是 PNG 的 `.dds` 不会在这两行报错，但引擎取纹理时拿不到数据。
（2026-09-21 实测：某 MOD 的 `flags/DOT_SR/` 里 9 个旗标有 6 个其实是 256×256 的 PNG 改名。）
而 `.png` 直接扔在分类目录里会报
`empire_flag.cpp:588: invalid file [<分类>/<名>.png]. Please use .dds texture files
or text files callaed usage.txt only`。

**贴图规格**（照抄同目录下已知可用的那一个最省事）：

| 路径 | 尺寸 | 用途 |
|---|---|---|
| `flags/<分类>/<名>.dds` | 256×256（原版也有 128×128 的写法，两者都能用） | 设计器与常规显示 |
| `flags/<分类>/map/<名>.dds` | 256×256 | 银河地图；缺了报 `empire_flag.cpp:924` |
| `flags/<分类>/small/<名>.dds` | **24×24**（不是 28） | 小图标 |

内容格式：**未压缩 32bpp BGRA**。`pf.dwFlags = 65`（ALPHAPIXELS|RGB）、
`pf.dwRGBBitCount = 32`、`pf.dwFourCC = 0`、R/G/B/A 掩码依次为
`0x00FF0000 / 0x0000FF00 / 0x000000FF / 0xFF000000`、
`dwMipMapCount` 取到 1×1 的完整链（256×256 → 9 级、24×24 → 5 级）。
本项目可直接对照的样板是 `flags/DOT_SR/DOT_SR_04.dds`
（`dwFlags = 659463`、`dwCaps = 4198408`、256×256 共 349652 字节）。
工具：`scripts/png2flag_dds.py`，三种用法——
`make <源图> <分类目录> <名>` 生成三件套、`check <目录>` 体检、
`repair <目录> --backup <备份目录>` 批量把 PNG 伪装的 `.dds` 修好并补齐副本。

另外两点：`flags/<分类>/usage.txt` 里写 `random = no` + `show_in_designer = yes`
可防止 AI 随机挑到这组旗（原版 `human/usage.txt` 就是这个组合）；
分类名要靠本地化键 `FLAG_CATEGORY_<分类文件夹名>` 才在设计器里有名字，
键名规则见原版 `localisation/english/main_1_l_english.yml:3315` 的注释，
但**原版只在 english 里写了这些键**，MOD 自己的分类要自己补到每种语言，否则非英文界面显示裸 key。

---

## 6. 运行时生成孤立星系（只能靠 bypass 抵达）

原版最成熟的参数组（`common/scripted_effects/01_start_of_game_effects.txt` 的
`origin_unplugged_machine_legacy_periphery_system_init` 就是这一组，可直接照抄）：

```pdx
capital_scope = {                       # 或任意 galactic_object
    solar_system = {
        spawn_system = {
            min_distance = 6
            max_distance = 6
            max_jumps = 0               # 0 跳 = 不靠近已有航道网络
            hyperlane = no              # 不自动连航道 ⇒ 成为孤立星系
            min_orientation_angle = 90
            max_orientation_angle = 90
            is_discovered = no          # 可选：未探明，进入时才揭开
            initializer = MY_SYSTEM_INIT
        }
        last_created_system = {
            save_global_event_target_as = my_system
            set_star_flag = my_star_flag
            random_system_planet = {
                limit = { has_planet_flag = my_planet_flag }
                save_global_event_target_as = my_planet
            }
        }
    }
}
```

- `spawn_system` 本身**不加航道**，所以 `hyperlane = no` 就是"孤立"；`max_jumps = 0` 限制跳跃距离。
- 也可用 `spawn_system = { ... effect = { ... } }` 子块接住新星系（原版 toxoids 事件即此写法）。
- 想让生成点"靠近首都"就用小 `distance` + 固定 `orientation_angle`；`min_distance`/`max_distance` 单位是
  0–100 的距离量（原版常见 6 / 10 / 20 / 30 / 40 等），**同值即精确指定**。

### 6.1 系统初始器（`common/solar_system_initializers/`）

- 想要**只能被脚本 spawn、不参与随机生成**：`usage = misc_system_init` 会参与随机；
  **完全不写 `usage`** ⇒ 只会被显式调用（`example.txt` 明确说明）。
  若给了 `usage = x` 又不想随机出现，加 `usage_odds = { base = 0 }`。
- 星系级 `prevent_anomalies = yes`（复数）禁随机异常；行星级效果是 `prevent_anomaly = yes`（单数）。
- 恒星写成 `planet = { class = star orbit_distance = 0 size = 30 }`，星系 `class = "rl_standard_stars"` 或具体星类 `sc_g`。

---

## 7. on_action 作用域速查（易错）

| on_action | 作用域 |
|---|---|
| `on_game_start_country` | `THIS = Country`（比 `on_game_start` 晚，首都/舰队已就绪，**推荐用来生成开局内容**） |
| `on_entering_system_first_time` | **`ROOT = Ship` / `FROM = System` / `owner = Country`**（部分原版事件也用 `fromfrom = Country`） |
| `on_system_survey` | `Root = Country` / `From = System` / `FromFrom = Fleet` |

⚠️ **`on_entering_system_first_time` 注册的事件必须是 `ship_event`。**
本次已用脚本枚举原版该 on_action 下全部 **41 个**已注册事件，**100% 是 `ship_event`**——
写成 `country_event` 会静默不触发。同理，注册到某个 on_action 之前，**先去原版 `common/on_actions/00_on_actions.txt`
找到该 on_action 的注册表，数一数里面事件的事件类型**，照着写就绝不会错。

---

## 8. 物种 / 肖像（v4.x）

- **`common/species_classes/*.txt` 已不支持 `portraits` 键**。肖像必须在 `common/portrait_sets/*.txt` 里
  按 `species_class` 指派：

```pdx
MySet = {
    species_class = MY_CLASS
    portraits = { "portrait_a" "portrait_b" }        # 条件版用 conditional_portraits = { randomizable = ... playable = ... portraits = { } }
}
```

- 但**不登记 `common/portrait_categories/` 也能正常使用**——`create_species { portrait = X }` 与
  `change_leader_portrait = X` 都会工作，只是该物种集不会出现在帝国设计器里。
  想出现，就把肖像集名加进对应 category 的 `sets = { }` 列表（会改动既有文件）。
- 简单 `texturefile` 型肖像定义在 `gfx/portraits/portraits/*.txt` 的 `portraits = { <id> = { texturefile = "..." } }`，
  并把 id 加进同文件 `portrait_groups` 的各个子块（`game_setup` / `species` / `pop_group` / `leader` / `ruler`）。
- 肖像 dds 规格：本 MOD 统一 **496×380 / DXT3 / 9 级 mip**。
