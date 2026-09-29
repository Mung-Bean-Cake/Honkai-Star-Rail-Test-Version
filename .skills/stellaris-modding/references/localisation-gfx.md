# 本地化、GFX 与界面

来源：https://stellaris.paradoxwikis.com/Localisation | /Interface_modding

## 一、本地化（localisation/）

### 目录与命名

```
<MOD 根目录>/localisation/
├── english/          （语言子目录可选，仅为整理方便）
│   └── mymod_l_english.yml
├── simp_chinese/
│   └── mymod_l_simp_chinese.yml
└── replace/          ← 覆盖原版 key 专用，最后加载
    └── my_replace_l_simp_chinese.yml
```

**三条铁律**：

1. **编码必须是 UTF-8 带 BOM**。纯 UTF-8（无 BOM）引擎直接不解析。
2. **文件名必须以 `_l_<语言>.yml` 结尾**，否则文件被忽略。
3. **首行必须是 `l_<语言>:`**，且其后每一行都以空格或 tab 开头。

语言代码：`english` `simp_chinese` `french` `german` `spanish` `russian` `polish` `japanese` `korean` `braz_por`。

### 格式

```yaml
l_simp_chinese:
 my_key: "显示文本"
 my_key:0 "冒号后的 0 可省略，仅供官方翻译追踪"
 my_key_tt: "第一行\n第二行"
```

注意：

- key 与 yml 里的 key **必须逐字符一致**（定义文件里写 `my_key`，yml 里也必须 `my_key`）。
- 字符串用英文双引号包裹；字符串内要显示引号需转义 `\"`。
- **下列 Unicode 字符在本地化文件中非法**，会显示成 `?`：
  `„ “ ‚ ‘ – ” ’ … —`（卷引号、破折号、省略号）。用 ASCII 的 `"` `'` `-` `...` 代替。

### 覆盖原版文本

放进 `localisation/replace/` 目录。该目录在所有其他本地化之后加载，**按 key 逐条覆盖**（LIOS per-key），不必复制整个原版文件。

### 颜色码

以 `§` 开头（Windows 小键盘 `ALT+0167`），后跟单个字符，持续到下一个颜色码或 `§!` 复位。

| 码 | 颜色 | 用途 |
|----|------|------|
| `W` | 白 | 外交态度 |
| `T` | 浅灰 | 正文默认色 |
| `g` | 深灰 | 禁用 / 无效 |
| `L` | 褐 / 卡其 | 背景故事、角色扮演文本 |
| `R` | 红 | 负面修正 |
| `S` | 深橙 | 次级高亮 |
| `H` / `K` | 橙 | 重点高亮 |
| `Y` / `I` | 黄 | 次优 / 中性修正 |
| `G` | 绿 | 正面修正 |
| `V` | 深绿 | 事件文本 |
| `E` | 青绿 | 大段文字 |
| `C` | 青 | 概念文本（会生成 tooltip 词条） |
| `B` | 青蓝 | 影响人口的事件效果 |
| `M` | 紫 | 稀有科技 |
| `_` | 品红 | 占位符 |
| `c` | 蓝绿 | 领袖特质 |
| `v` | 灰绿 | 老兵领袖特质 |
| `d` | 棕褐 | 命运特质 |
| `r` | 浅紫 | 知名领袖 |
| `l` | 浅绿 | 传奇领袖 |
| `!` | — | 复位到上一个颜色 |

```
 my_text: "§G+10% 产出§! 但 §R-5 稳定度§!"
```

在 `$` 变量里也可指定颜色：`$AGE|Y$`。

### `$` 变量

用于引用别处定义的字符串或变量：

```
 @my_energy_upkeep = 5
 my_text: "维护费 +$@my_energy_upkeep$"
```

### `£` 图标

插入游戏内图标：`£energy£` `£minerals£` `£unity£` `£influence£` `£alloys£` `£consumer_goods£` `£research£` `£military_power£` `£planetsize£` `£time£` `£blocker£` `£empire£` `£opinion£` 等。

### 方括号命令（Bracket Commands）

格式 `[主作用域.次作用域.取值命令]`：

```
 [Root.GetName]                  # 主作用域名称
 [This.GetName]                  # 当前作用域
 [From.GetName]                  # 调用来源
 [Root.Capital.GetName]          # 首都名
 [Root.Owner.GetName]            # 拥有者名
 [Root.Leader.GetName]           # 领袖名
 [mytarget.GetName]              # event target（本地化里不加 event_target: 前缀）
 [This.GetSpeciesName]
 [Root.GetAdjective]
 [Scope.my_variable]             # 读变量
 [scope.GetDate]
```

- `[[` 转义为单个 `[`。
- 无作用域命令：`GetDate` `GetMidGameDate` `GetLateGameDate` `GetYear` `LastKilledCountryName`。
- 完整列表见游戏生成的 `Stellaris\logs\script_documentation\localizations.log`。
- 在 scripted_effect / trigger 里写 loc 命令需转义：`\\[This.GetName]`。

### 换行与制表

`\n` 换行，`\t` 制表。`$TABBED_NEW_LINE$` 是原版常用的组合（缩进换行）。

### 控制台辅助

```
reload text                     # 重载本地化表
switchlanguage l_simp_chinese   # 切换语言并重载
toggle_string_id                # 显示 StringID 而非文本
```

---

## 二、GFX（贴图注册）

### gfx/ 目录结构

目录层级本身不影响功能，但建议按用途分类：

```
gfx/
├── event_pictures/      事件大图
├── interface/icons/     各类图标（resources/ modifiers/ traits/ ...）
├── models/              3D 模型（ships/ stations/ ...）
├── particles/           粒子
├── portraits/           立绘
├── loadingscreens/      加载界面
├── global_set_UI/       自定义 UI 元素
├── FX/                  .lua 特效与动画
└── animation/
```

贴图格式：Stellaris 用 `.dds`（DXT5 / BC3）。图标建议 2 的幂尺寸、带 mipmap。

### 在 interface/*.gfx 注册 sprite

```gfx
spriteTypes = {
	spriteType = {
		name = "GFX_my_eventpicture_1"
		texturefile = "gfx/event_pictures/my_event_1.dds"
	}
	spriteType = {
		name = "GFX_my_icon"
		textureFile = "gfx/interface/icons/my_icon.dds"
	}
	spriteType = {
		name = "GFX_my_frames"
		texturefile = "gfx/interface/my_atlas.dds"
		noOfFrames = 12          # 图集帧数
	}
}
```

| 属性 | 必需 | 说明 |
|------|------|------|
| `name` | 是 | 全局唯一，约定 `GFX_<mod>_<name>` |
| `texturefile` / `textureFile` | 是 | 相对游戏根目录的路径 |
| `noOfFrames` | 否 | 图集帧数，默认 0 |
| `effectFile` | 否 | 附加 .lua 特效，如 `gfx/FX/buttonstate_onlydisable.lua` |

**sprite 名必须全局唯一**，冲突会导致显示错乱。

### 事件图

1. 图片放 `gfx/event_pictures/my_event.dds`。
2. 在 `interface/my.gfx` 注册 `name = "GFX_my_event"`。
3. 事件里引用：`picture = GFX_my_event`。

### 领袖立绘

`gfx/portraits/` 下放 `.dds`，并需要在对应 `.asset` / `gfx` 中声明 portrait entity。整套立绘通常需要多个情绪状态图，建议直接改造原版或现成 MOD 的目录。

### 旗帜 flags/

- 结构是 `flags/<分类>/<名>.dds`；`<分类>` 就是 `emblem` 定义里 `icon.category` 的取值，
  要在设计器里显示还得有本地化键 `FLAG_CATEGORY_<分类>`（原版只在 english 里写了这些键）。
- 每个旗标要三份同名文件：`<分类>/<名>.dds`（256×256）、`<分类>/map/<名>.dds`（256×256，银河地图用）、
  `<分类>/small/<名>.dds`（**24×24**）。缺 `map/` 报 `empire_flag.cpp:924`。
- **必须是真正的 DDS**（未压缩 32bpp BGRA、带完整 mip 链）；把 PNG 改后缀成 `.dds` 不行，
  把 `.png` 留在分类目录里会报 `empire_flag.cpp:588: invalid file`。
  用 `scripts/png2flag_dds.py` 生成/体检/批量修复。
- 颜色名取自 `flags/colors.txt`（299 个键，如 `white` `black` `ochre_brown` `intense_blue`）。
  旗标图案本身已上色时，`colors` 第一位写 `"white"` 表示不染色。
- `flags/<分类>/usage.txt`：`random = no` 阻止 AI 随机选用，`show_in_designer = yes` 允许玩家选用。
- 详细写法（emblem 定义块、`create_country` 与 `change_country_flag` 的差异）见
  `references/advanced-systems.md` §5.6。

---

## 三、GUI 界面（interface/*.gui）

所有元素必须包在 `guiTypes = { }` 内。

### containerWindowType（容器）

```gfx
containerWindowType = {
	name = "my_container"
	position = { x = 10 y = 10 }
	size = { width = 200 height = 200 }
	margin = { top = 5 bottom = 5 left = 5 right = 5 }
	verticalScrollbar = "right_vertical_slider"
	background = {
		name = "background"
		spriteType = "GFX_tiles_dark_area_cut_8"
		alwaysTransparent = yes
	}
	### 内容
}
```

### buttonType / effectButtonType（按钮）

```gfx
buttonType = {
	name = "my_button"
	spriteType = "GFX_standard_button_116_34"
	position = { x = 10 y = 10 }
	buttonFont = "cg_16b"
	buttonText = "MY_BUTTON_LOC"
	pdx_tooltip = "MY_BUTTON_TOOLTIP_LOC"
}
```

> 自定义按钮要执行脚本动作时用 `effectButtonType`；普通 `buttonType` 多与原版硬编码动作绑定。

### instantTextBoxType（文本）

```gfx
instantTextBoxType = {
	name = "my_text"
	font = "cg_16b"
	text = "MY_LOC_KEY"          # 必须是有效本地化引用
	position = { x = 40 y = 0 }
	maxWidth = 250
	maxHeight = 40
	fixedSize = yes
	format = center
	vertical_alignment = center
	# 动态文本：text = "[Root.GetName]"
}
```

### 引用 sprite

在任何元素的 `spriteType`（或 `quadTextureSprite`）里填 `.gfx` 中注册的 `name`。

### 把自定义 GUI 挂到事件上

事件里写：

```
country_event = {
	id = my_ns.1
	custom_gui = my_window_ui
	custom_gui_option = my_window_ui_option
	option = { name = my_option ... }
}
```

`.gui` 中对应的容器需要给 `window` 起与 `custom_gui` 相同的名字。

### 修改原版界面的注意点

- 修改现有元素属性通常安全；**删除或重排预定义元素可能导致崩溃**。
- `interface/` 是 LIOS：想改原版某个 `.gui` 里的一个控件，最稳的是把整个文件复制过来再改，但务必评估与其他 MOD 的冲突。

---

## 四、字体（fonts/）

- `fonts/fonts.asset` 定义字体族与字号。
- 新增字体需放字体文件并在 `fonts.asset` 中注册。
- **中文字体是中文 MOD 的刚需**：原版对部分生僻字的支持有限，替换/追加字体可解决缺字方块问题。
