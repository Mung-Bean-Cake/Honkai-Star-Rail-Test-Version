# 调试与测试

来源：https://stellaris.paradoxwikis.com/Modding_tutorial

## 一、日志位置

| 平台 | 路径 |
|------|------|
| Windows | `…\Documents\Paradox Interactive\Stellaris\logs` |
| Linux | `~/.local/share/Paradox Interactive/Stellaris/logs` |
| macOS | `~/Documents/Paradox Interactive/Stellaris/logs` |

关键文件：

- **`error.log`** —— 主要排查对象。脚本语法错误、缺失图标、缺失本地化都会出现在这里。
- **`game.log`** —— 配合 `log` 效果输出自定义调试信息。
- `Stellaris\crashes\` —— 崩溃转储，主要给官方开发者用。

**排查技巧**：在 `error.log` 里直接搜 MOD 前缀（如 `mymod_`）能快速定位到自己的问题行。每条日志形如：

```
[18:22:15][government_civic_type.cpp:185]: Did not find an icon for civic: mymod_civic
```

方括号里是时间与引擎源码位置，冒号后是问题描述。

> **重要**：`error.log` 基于异常捕获，**绝大多数崩溃（CTD）不会在这里留痕**。因此"日志干净"不等于"没有 bug"。

## 二、启动参数（EXE parameters）

给 `stellaris.exe` 加参数（Steam → 右键游戏 → 属性 → 启动选项；或用快捷方式）：

| 参数 | 作用 |
|------|------|
| `-debug_mode` | 开启额外日志 |
| `-debugtooltip` | 进游戏即开启 debugtooltip |
| `-logall` | 允许记录重复字符串（默认只记第一次出现） |
| `-logprefix <前缀>` | 日志文件名加前缀 |
| `-logpostfix <后缀>` | 日志文件名加后缀 |
| `-script_debug` | （基本无用） |

推荐组合：`-debug_mode -logall`

## 三、`log` 效果

```
log = "my_var is now [This.my_var]"
```

写入 `game.log`。**默认相同字符串只输出一次**；循环里输出相同文本时配合 `-logall`，或在字符串里带上递增变量使其每次不同。

注意：在 scripted_effect / trigger 里写 loc 命令要转义成 `\\[This.GetName]`，否则第二次使用起会出错。

## 四、控制台命令

在游戏中按 `~`（或 `` ` ``）打开控制台。控制台接受任意合法脚本，但**必须声明类型前缀**（`trigger` / `effect` / `event`）。

```
trigger OR = { has_civic = mymod_civic has_valid_civic = mymod_civic }
effect owner = { every_owned_ship = { prevprev = { change_variable = { which = n value = 1 } } } }
event my_ns.1
```

作用域：控制台在**当前选中的对象**上执行。选中对象的方式：

- 行星 / 舰队：直接点视图对象。
- 国家：打开政府界面即切到该国家作用域。
- 不可点的对象需要额外作用域操作符。

粘贴多行输入是可行的（虽然显示会错乱，但会正确执行）。

### 高频控制台命令

| 命令 | 作用 |
|------|------|
| `debugtooltip` | 悬停显示对象的 flag / 变量 / id |
| `observe` | 切换到观察者模式（看全图） |
| `debug_yesmen` | AI 永远同意外交 |
| `research_technologies` / `finish_research` | 完成科技 |
| `instant_build` | 瞬间建造 |
| `influence` / `energy` / `minerals` / `alloys` … | 加资源 |
| `event <id>` | 触发事件 |
| `planet_size <n>` | 改行星大小 |
| `survey` | 立即勘测所选星系 |
| `own` | 拥有所选行星 |
| `attackall` | 攻击所有 |
| `script_profiler` | 开始/结束脚本性能分析（3.5+） |
| `reload text` | 重载本地化 |
| `toggle_string_id` | 显示 key 而非文本 |

调试事件时最常用的循环：改脚本 → 控制台 `event my_ns.1` → 看 `error.log`。

## 五、编辑工具

### CWTools（强烈推荐）

VS Code 扩展。提供 Stellaris 脚本的语法高亮、自动补全、跳转、错误检查。

配置要点：在 VS Code 设置里指定 Stellaris 安装目录（设定 `cwtools.localisation` / 游戏路径），它就能基于原版文件提供精准补全。wiki 教程中的截图里可以看到：打开编辑器、打开 MOD 根目录、文件大纲、错误高亮。

### 其他

- VS Code / Notepad++：编辑时必须能保存为 **UTF-8 with BOM**（Notepad++ 菜单：编码 → 转为 UTF-8-BOM）。
- 图片：`.dds` 建议用 Paint.NET（带 DDS 插件）或 GIMP 处理。

## 六、常见错误对照表

| 现象 | 大概率原因 |
|------|-----------|
| 中文全变数字 / 显示成 `key_name` | 本地化文件不是 UTF-8 **BOM**；或文件名不以 `_l_<语言>` 结尾；或首行不是 `l_<语言>:`；或 key 拼写不一致 |
| `error.log`: `Did not find an icon for ...` | `gfx/interface/icons/<类型>/` 下缺 `.dds`，或文件名与 key 不一致 |
| `error.log`: `Missing localisation for ...` | 忘了写本地化，或本地化文件没被加载（编码/命名问题） |
| 事件完全不触发 | `is_triggered_only = yes` 但没有任何调用方；`trigger` 恒假；`namespace` 与 `id` 不匹配；事件文件被 FIOS 挡掉 |
| 事件 id 报错 / 被当成 `ns.0` | id 里含字母，或前导零写法 |
| 修改无效 | 改了 Workshop 副本；本地与订阅同名同 id 并存（游戏拒绝加载）；文件放错目录 |
| 花括号报错 | 括号不配对；字符串里出现了裸的 `{` `}`；`#` 注释掉了一行开头 |
| 选项不显示 | `option` 的 `trigger` 不满足；可见事件没有 option |
| 图标错位 / 显示别人的图 | sprite 名与其他 MOD 冲突（未加唯一前缀） |
| 数值改不动 | `defines/` 文件名字母序没排到原版文件之前 |
| 崩溃且日志无信息 | 看 `Stellaris\crashes\`，或二分法注释代码定位 |

## 七、性能排查

1. 用 `-debug_mode` 启动，游戏中执行 `script_profiler` 开始记录，玩一段时间后再执行一次输出结果。
2. 重点看事件的轮询量：把能用 `is_triggered_only` 的事件都改掉。
3. 检查 `every_*` 全银河遍历是否都有 `limit`。
4. 检查 `mean_time_to_happen` 事件数量与 `modifier` 条件复杂度。

## 八、测试流程建议

1. **纯脚本改动**：改文件 → 重开游戏（脚本改动必须重开，热重载仅对本地化有效）→ `event <id>` 触发 → 查 `error.log`。
2. **本地化改动**：控制台 `reload text` 可即时生效。
3. **图形改动**：必须重开游戏。
4. **多 MOD 兼容测试**：开一个新存档，只加载目标 MOD 组合，避免旧存档残留状态干扰。
5. **发布前**：用一份全新存档跑一遍完整开局流程。

## 九、从存档反查"游戏里到底发生了什么"（.sav 取证）

脚本闸全都放行了、`error.log` 却干干净净、现象又说不清时，**别再猜脚本，去读存档**。`.sav` 就是个 zip，里面 `meta` + `gamestate`，`gamestate` 是几十 MB 的纯文本，直接字符串检索即可。

```python
import zipfile
d = zipfile.ZipFile(sav_path).read("gamestate").decode("utf-8", "replace")
print(d.count("ship_size=\"starbase_outpost\""))
```

常用检索点：

| 想看什么 | 怎么找 |
|---|---|
| 该局**实际启用的 DLC**（判拥有权） | 顶部的 `required_dlcs=` 列表 |
| 玩家是哪个国家 | `player=` 段里的 `country=<id>`；国家块格式是 `\n\t<id>=\n\t{` |
| 国家身份 | 国家块里的 `is_nomadic=yes` / `government=` / `origin="..."` / `capital=` |
| **某科技是否真的到手** | `tech_status` 段里的 `technology="tech_xxx"`（比看界面可靠得多） |
| 某船型**是否真的存在实例** | `ship_size="<名>"`；注意**设计表里也会出现同名**，通常"出现次数 ≈ 国家数"。要判实例，需在命中点附近再找 `owner=` |
| 正在建造的东西 | `item_mgr` 下的 `buildable_ship` / `buildable_district` / `buildable_colony_ship` + `paying_country` |

实战价值：能直接回答「这个对象到底生成了没有」，避免在脚本层做无用功。例：排查"游牧建恒星基地失败"时，存档里玩家名下 0 个恒星基地实例 ⇒ 已确认订单在**完成阶段**被拒，而不是脚本闸没过。
