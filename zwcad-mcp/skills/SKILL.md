---
name: zwcad-mcp-skill
description: ZWCAD 2D 平台与中望机械 — 绘制、查询、标注、块/图层/样式管理、图框/标题栏/BOM/球标等机械能力
version: "0.1.0"
author: "ZWCAD 2D MCP Team"
---

# ZWCAD 2D 建模与制图 Skill

本 Skill 让 AI 通过自然语言操作中望 CAD（ZWCAD）二维图纸与中望机械扩展：绘制实体、查询图面、标注尺寸、管理图层/块/样式，以及机械图框、标题栏、BOM 明细表等。

---

## 环境前提检查（任务开始前必须先做）

本 MCP 经 **Windows COM** 连接本机正在运行的 ZWCAD。每次任务前按 ①②③ 检查，任一不满足则按对应话术告知用户并停止调用工具。

### ① Windows 系统

`os.name != 'nt'` / `sys.platform != 'win32'` 即不满足，直接告知：

> 本 MCP 只支持 Windows 环境，当前系统无法使用。请更换到 Windows 电脑，安装 ZWCAD 后再试。

### ② 已安装中望 CAD（或中望机械 CAD）

检测 `zwcad_get_capabilities(probe_cad=true)` / `zwcad_get_app_info(scope="cad")`；返回 `platform.available=false`、`Connection closed` 或 COM 错误 `-2147221008` 即不满足。

- **未安装**：

> 当前电脑没有安装 ZWCAD，本 MCP 无法使用。请先到这里下载并安装：https://www.zwsoft.cn/product/zwcad
> 装好后：① 打开 ZWCAD 并新建/打开一张 DWG；② 在连接器管理页重连「中望CAD MCP」；③ 回来让我继续。

- **已装未启动**：提示启动 ZWCAD 并打开/新建 DWG，重连后继续。

### ③ 运行依赖 uvx（默认 `uvx zwcad-mcp` 启动）

`uvx --version` 报错**不等于没装**——官方安装器默认落在 `%USERPROFILE%\.local\bin\`，该目录常不在 PATH：

| 检测 | 处置 |
|---|---|
| `uvx --version` 返回版本号 | 就绪 |
| 报错，但常见路径下有 `uvx.exe` | **A｜补 PATH** |
| 命令和常见路径都找不到 `uvx.exe` | **B｜安装 uv** |
| `~/.workbuddy/mcp.json` 有 `zwcad-2d`/`zwcadmech` 等服务（即使 `disabled: true`）且 venv 完整 | **C｜启用本地服务**（最快，不碰 uvx） |

uvx 常见路径：`%USERPROFILE%\.local\bin\uvx.exe`（默认）、`%LOCALAPPDATA%\Programs\uv\uvx.exe`、`C:\Program Files\uv\bin\uvx.exe`。检测：`Test-Path "$env:USERPROFILE\.local\bin\uvx.exe"`

**A｜补 PATH**：先用 `$env:PATH = "<目录>;$env:PATH"; uvx zwcad-mcp` 临时验证，确认后 `[Environment]::SetEnvironmentVariable("Path", $env:Path + ";<目录>", "User")` 永久修复；改完**重启终端与 WorkBuddy**，`where.exe uvx` 返回路径即生效。

**B｜安装 uv**（自带 uvx）：`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"` 或 `winget install --id=astral.sh.uv`；装完重启终端 → 连接器断开重连 → 首次自动拉依赖。启动标志依次：`Installed N packages in Xs` → `INFO: ZWCAD-2D MCP Server 启动中...` → `Starting MCP server ... with transport 'stdio'`；卡 `Resolved` 行多为下载慢，配 `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple`（连接器 `env` 默认已配）。

**C｜启用本地服务**：`cat ~/.workbuddy/mcp.json` 查看，在连接器管理页启用即可。

> 非 `uvx` 启动（如已 pip 装到某 Python 环境）跳过 ③，仅查 ①②。

---

## 工具发现机制（重要）

- MCP 服务启动后，先通过 `tools/list` 获取当前实际暴露的工具、description 和 input schema；运行时结果优先于静态文档。
- 本 Skill 已包含执行任务所需的工作流、能力索引和排障规则；无需读取其他项目文档即可开始工作。
- 调用前检查目标工具的 description 与 input schema，再按当前 schema 传参；不要根据工具名称猜测参数，角度单位一律使用弧度。
- 工具调用失败时优先读取返回的 `error` / `code` / `hint` 字段，并结合「常见错误场景」排查。

### 工具能力索引

以下索引用于按任务定位工具。第三列列出主要输入参数、动作和动作对应的 `params` 字段；具体 schema 仍以运行时 `tools/list` 返回为准。

### 绘图、注释与标注

| 工具 | 作用 | 主要输入 |
| --- | --- | --- |
| `zwcad_draw_entity` | 创建单个二维实体 | `entity_type`：`line`、`circle`、`arc`、`ellipse`、`lwpolyline`、`polyline`、`spline`、`point`、`ray`、`xline`、`mline`、`3d_polyline`；`params`：几何参数；`layer` |
| `zwcad_draw_batch` | 批量创建多个实体 | `entities`：包含 `entity_type` 和 `params` 的列表；`layer` |
| `zwcad_draw_3d_solid` | 创建基础三维实体 | `solid_type`：`box`、`cylinder`、`cone`、`sphere`、`torus`、`wedge`、`3d_face`；`params`：几何参数；`layer` |
| `zwcad_add_annotation` | 添加文字、引线、填充和表格等注释 | `annotation_type`：`text`、`mtext`、`leader`、`tolerance`、`mleader`、`hatch`、`table`；`params`：注释参数；`layer` |
| `zwcad_add_dimension` | 创建尺寸标注 | `dim_type`：`aligned`、`rotated`、`diametric`、`radial`、`angular`、`ordinate`；`params`：标注几何参数、公差/配合参数；`layer` |
| `zwcad_insert_block` | 在指定位置插入图块引用 | `block_name`、`x`、`y`、`z`、`x_scale`、`y_scale`、`z_scale`、`rotation`、`layer` |

### 实体查询、修改与尺寸查询

| 工具 | 作用 | 主要输入 |
| --- | --- | --- |
| `zwcad_find_object` | 按条件或句柄定位第一个实体 | `handle`，或 `object_type` + `property_name` + `property_value` |
| `zwcad_get_objects_in_model` | 获取模型空间对象列表 | `object_type`：可选类型过滤；`limit`：返回数量上限 |
| `zwcad_get_entity_info` | 获取实体属性、几何数据和边界框 | `handle`，或 `object_type` + `property_name` + `property_value` |
| `zwcad_set_entity_properties` | 修改实体通用属性 | `layer`、`color`、`linetype`、`linetype_scale`、`lineweight`、`visible`；以及实体定位参数 |
| `zwcad_transform_entity` | 执行实体变换 | `action`：`copy`、`move`、`rotate`、`mirror`、`scale`、`delete`、`array_polar`、`array_rectangular`；`params`：动作参数；以及实体定位参数 |
| `zwcad_modify_entity` | 修改实体几何属性 | `entity_type`：`circle`、`arc`、`line`、`text`、`mtext`、`polyline`、`spline`、`dimension`；也支持 `offset`、`explode`；`params`：对应几何参数；以及实体定位参数 |
| `zwcad_query_dimensions` | 批量查询尺寸值、公差、标注文字和样式 | `detail`：`summary` 或 `full`；`layer`：可选图层过滤 |

实体定位统一优先使用 `handle`；没有句柄时使用 `object_type` + `property_name` + `property_value`。

### 样式、视图与文档

| 工具 | 作用 | 主要输入 |
| --- | --- | --- |
| `zwcad_manage_style` | 管理图层、线型、文字样式和标注样式 | `style_type`：`layer`、`linetype`、`textstyle`、`dimstyle`；`action`：`list`、`add`、`set_active`、`set_properties`；`name`、`properties` |
| `zwcad_manage_view` | 管理布局和视图 | `action`：`list_layouts`、`get_active_layout`、`add_layout`、`set_active_layout`、`list_views`、`add_view`、`set_active_space`、`get_active_space`；`name`、`params` |
| `zwcad_zoom` | 控制当前视图范围 | `mode`：`extents`、`all`、`previous`、`window`、`center`、`scale`；`params`：窗口、中心点或比例参数 |
| `zwcad_manage_document` | 管理图纸生命周期、保存、导入导出和打印 | `action`：`new`、`save`、`close`、`info`、`list`、`activate`、`export`、`import`、`plot`、`regen`、`start_undo`、`end_undo`、`wblock`；`params`：动作参数 |
| `zwcad_manage_table` | 操作 CAD 表格 | `action`：`set_cell`、`get_cell`、`insert_rows`、`delete_rows`、`set_column_width`、`set_row_height`、`merge_cells`；`params`：行列和单元格参数；以及实体定位参数 |
| `zwcad_select_entities` | 创建和管理选择集 | `action`：`select`、`by_polygon`、`get_items`、`get_picked`、`list`、`clear`、`delete`；`params`：选择模式、点、过滤器、选择集名称等 |
| `zwcad_manage_block` | 管理图块定义和属性 | `action`：`list`、`info`、`create`、`get_attributes`；`name`、`params`；获取属性时使用实体定位参数 |

### 系统与诊断

| 工具 | 作用 | 主要输入 |
| --- | --- | --- |
| `zwcad_get_variable` | 读取系统变量 | `name`，如 `DIMSCALE`、`LTSCALE`、`OSMODE` |
| `zwcad_set_variable` | 写入系统变量 | `name`、`value` |
| `zwcad_get_app_info` | 获取应用和安装环境信息 | `scope`：`cad`、`mech_version`、`mech_cad_path`、`mech_zwm_path`、`mech_style_path`、`mech_about` |
| `zwcad_get_capabilities` | 查看当前产品、连接状态、工具组和活动图纸 | `probe_cad`：是否探测 CAD 连接 |
| `zwcad_diagnose` | 诊断平台和机械后端 | `probe_cad`：是否探测 CAD 连接 |
| `zwcad_mech_diagnose` | 诊断机械扩展和 ZwmToolKit 类型库 | 无输入参数 |

### 机械扩展

| 工具 | 作用 | 主要输入 |
| --- | --- | --- |
| `zwcad_mech_manage_title_block` | 读取、设置和批量更新标题栏 | `action`：`get_info`、`set_field`、`update_batch`、`get_field_count`、`get_field_by_index`；`params`：字段名、字段值或索引 |
| `zwcad_mech_manage_frame` | 查询、切换、更新和刷新图框 | `action`：`list`、`get_info`、`get_count`、`get_name_by_index`、`get_name_by_point`、`get_next_name`、`switch`、`update`、`refresh`；`params`：图框名称、坐标或属性 |
| `zwcad_mech_create_frame` | 创建图幅和图框 | `std_name`、`frame_size_name`、`orientation`、尺寸、比例、样式名称，以及 `have_dhl`、`have_fjl`、`have_btl`、`have_csl`、`have_ggl` 等栏位开关 |
| `zwcad_mech_manage_bom` | 增删改查明细表数据 | `action`：`get_row_count`、`get_row`、`add_row`、`update_row`、`insert_row`、`delete_row`、`set_field`、`get_field`、`get_field_count`、`batch_update`、`refresh`；`params`：行、字段和数据 |
| `zwcad_mech_create_partlist` | 创建明细表实体 | 无输入参数，通过 CAD 命令创建当前图纸明细表 |
| `zwcad_mech_manage_db` | 管理机械数据库 | `action`：`open`、`save`、`close`；`params`：文件路径或保存选项 |
| `zwcad_mech_doc` | 管理机械文档 | `action`：`open`、`new`、`new_named`；`file_path`、`template` |
| `zwcad_mech_cad_environment_init` | 初始化机械 CAD 标准环境 | `std_name`：如 `GB`、`ISO`、`DIN` |
| `zwcad_mech_get_balloon` | 读取球标信息 | `text`：可选球标文字过滤 |
| `zwcad_mech_insert_balloon` | 插入球标 | 箭头位置 `arrow_x/y/z`、标注位置 `symbol_x/y/z`、`text`、`seq_type`、`has_leader`、`mode` |

### 扩展数据与 CAD 工具

| 工具 | 作用 | 主要输入 |
| --- | --- | --- |
| `zwcad_manage_dictionary` | 管理命名对象字典和 XRecord | `action`：`list`、`add`、`get_items`、`add_object`、`get_object`、`remove`、`rename`、`add_xrecord`、`get_xrecord`、`set_xrecord`、`get_entity_dict`、`has_entity_dict`；`params`：字典和条目参数 |
| `zwcad_manage_xdata` | 读写实体扩展数据 | `action`：`list_apps`、`register_app`、`get_xdata`、`set_xdata`、`delete_xdata`；`params`：`handle`、应用名、数据类型和值 |
| `zwcad_manage_utility` | 执行 CAD 通用计算和对象辅助操作 | `action`：`translate_coordinates`、`polar_point`、`angle_to_real`、`angle_to_string`、`real_to_string`、`distance_to_real`、`prompt`、`get_object_id_string`；`params`：点、角度、距离、单位和精度等 |

当用户提出能力需求时，先从上述索引定位工具，再读取该工具的运行时 schema；如果工具未出现在 `tools/list` 中，才判断当前服务版本不具备该能力。

### 参数语义

以下说明解释各工具参数的用途。坐标沿用当前图纸单位，角度统一使用弧度；方括号表示可选字段。

#### 公共参数

- `layer`：目标图层名称，默认使用 `0`。
- `handle`：实体句柄，优先级最高，用于精确定位实体。
- `object_type`：CAD 对象类型，例如 `Line`、`Circle`、`BlockReference`。
- `property_name`：用于筛选实体的属性名，例如 `Layer`、`Color`、`TextString`。
- `property_value`：与 `property_name` 对应的属性值。
- `params`：当前工具动作的详细参数对象，字段随 `action`、`entity_type` 或 `mode` 变化。

#### 参数命名约定

- `x`、`y`、`z`：一个点的三个坐标；`x1,y1,z1` 和 `x2,y2,z2` 通常分别表示起点和终点。
- `center_x`、`center_y`、`center_z`：圆、球、圆柱等对象的中心点；`base_x`、`base_y`、`base_z`：变换操作的基点。
- `arrow_x/y/z`：引线箭头点；`symbol_x/y/z`：标注符号点；`text_x`、`text_y`：标注文字位置。
- `points`：按顺序排列的点列表，通常用于引线、折线或多边形；`vertices`：实体顶点列表；`fit_points`：样条曲线拟合点列表。
- `radius`：半径；`torus_radius`：圆环中心线半径；`tube_radius`：圆环管半径；`height`、`width`、`length`、`depth`：几何尺寸。
- `angle`、`rotation`、`rotation_angle`：旋转或方向角，单位为弧度；`start_angle`、`end_angle`：弧线起止角。
- `scale`、`scale1`、`scale2`：比例因子；`x_scale`、`y_scale`、`z_scale`：三个坐标方向的缩放因子。
- `count`：数量；`index`：从 0 开始的索引；`row` / `col`：表格行列索引；`row_index`：行索引；`field_index`：字段索引。
- `name`：文档、布局、样式、图块或选择集名称，具体含义由工具动作决定；`value`：要写入的字段或系统变量值。
- `text`：文字内容；`height`：文字或几何高度；`width`：文字宽度或几何宽度；`precision`：显示精度；`unit`：单位或角度格式编号。

#### 绘图与标注参数

- `zwcad_draw_entity`
  - `entity_type`：要创建的实体类型。
  - `params`：几何参数。`line` 使用 `x1,y1,x2,y2,[z1,z2]`；`circle` 使用 `center_x,center_y,radius,[center_z]`；`arc` 使用圆心、半径、起止角；`ellipse` 使用主轴端点和半径比；`lwpolyline` / `polyline` / `mline` / `3d_polyline` 使用 `vertices`；`spline` 使用 `fit_points`；`point` 使用 `x,y,[z]`；`ray` / `xline` 使用起点和方向点。`closed` 表示多段线是否闭合。
  - `layer`：新实体所在图层。
- `zwcad_draw_batch`
  - `entities`：实体列表，每项包含 `entity_type`、`params`，可用 `layer` 覆盖外层图层。
  - `layer`：未在单项中指定图层时使用的默认图层。
- `zwcad_draw_3d_solid`
  - `solid_type`：`box`、`cylinder`、`cone`、`sphere`、`torus`、`wedge` 或 `3d_face`。
  - `params`：`box` 使用原点和长宽高；`cylinder` / `cone` 使用中心点、半径和高度；`sphere` 使用中心点和半径；`torus` 使用中心点、圆环半径和管半径；`wedge` 使用中心点和长宽高；`3d_face` 使用 3 或 4 个顶点。
  - `layer`：新实体所在图层。
- `zwcad_add_annotation`
  - `annotation_type`：`text`、`mtext`、`leader`、`tolerance`、`mleader`、`hatch` 或 `table`。
  - `params`：`text` / `mtext` 使用文字、位置、字高和宽度；`leader` / `mleader` 使用 `points` 和文字参数；`tolerance` 使用文字和位置；`hatch` 使用 `pattern_name`、比例和角度；`table` 使用位置、行列数、行高和列宽。
  - `layer`：注释对象所在图层。
- `zwcad_add_dimension`
  - `dim_type`：`aligned`、`rotated`、`diametric`、`radial`、`angular` 或 `ordinate`。
  - `params`：`aligned` / `rotated` 使用两端点和文字位置；`rotated` 还需要 `rotation_angle`；`diametric` 使用弦端点和引线长度；`radial` 使用圆心、弦点和引线长度；`angular` 使用顶点、两条边和文字位置；`ordinate` 使用定义点、引线点和 `use_x_axis`。
  - `params` 中还可使用 `tolerance_display`、`upper_deviation`、`lower_deviation`、`tolerance_precision`、`tolerance_height_scale`、`fit_symbol`、`fit_stacked`、`fit_height_scale`、`text_prefix`、`text_suffix`、`text_override` 设置公差、配合和文字覆盖。
  - `layer`：标注所在图层。
- `zwcad_insert_block`
  - `block_name`：已有图块定义名称。
  - `x,y,z`：插入点坐标，`z` 默认为 0。
  - `x_scale,y_scale,z_scale`：三个方向的缩放比例，默认 1。
  - `rotation`：旋转角度，单位为弧度。
  - `layer`：图块引用所在图层。

#### 实体查询与修改参数

- `zwcad_find_object`
  - `handle`：按句柄精确查找。
  - `object_type`：限定对象类型。
  - `property_name`：指定筛选属性。
  - `property_value`：指定属性值。
- `zwcad_get_objects_in_model`
  - `object_type`：可选的对象类型过滤。
  - `limit`：最多返回的对象数量，默认 500。
- `zwcad_get_entity_info`
  - `handle`、`object_type`、`property_name`、`property_value`：实体定位参数。
- `zwcad_set_entity_properties`
  - `layer`：修改实体图层。
  - `color`：修改实体颜色索引。
  - `linetype`：修改实体线型名称。
  - `linetype_scale`：修改实体线型比例。
  - `lineweight`：修改实体线宽。
  - `visible`：设置实体可见性；`false` 表示隐藏，不代表从图纸中删除。
  - `object_type`、`property_name`、`property_value`、`handle`：实体定位参数。
- `zwcad_transform_entity`
  - `action`：`copy`、`move`、`rotate`、`mirror`、`scale`、`delete`、`array_polar` 或 `array_rectangular`。
  - `params`：`copy` / `move` 使用起点和终点；`rotate` 使用基点和角度；`mirror` 使用镜像线两点；`scale` 使用基点和比例；`delete` 不需要额外字段；`array_polar` 使用中心点、数量和填充角；`array_rectangular` 使用行列数、行列间距和可选层间距。
  - `object_type`、`property_name`、`property_value`、`handle`：要变换的实体定位参数。
- `zwcad_modify_entity`
  - `entity_type`：`circle`、`arc`、`line`、`text`、`mtext`、`polyline`、`spline` 或 `dimension`；也支持 `offset`、`explode`。
  - `params`：`circle` / `arc` 使用半径、圆心和角度；`line` 使用起止点；`text` / `mtext` 使用文字、字高、旋转和位置；`polyline` / `spline` 使用闭合、宽度、拟合和切线参数；`dimension` 使用公差和配合参数；`offset` 使用 `distance`；`explode` 不需要额外字段。
  - `object_type`、`property_name`、`property_value`、`handle`：要修改的实体定位参数。
- `zwcad_query_dimensions`
  - `detail`：`summary` 返回摘要，`full` 返回完整几何和文字信息。
  - `layer`：可选的标注图层过滤。

#### 样式、视图、文档和选择集参数

- `zwcad_manage_style`
  - `style_type`：`layer`、`linetype`、`textstyle` 或 `dimstyle`。
  - `action`：`list`、`add`、`set_active` 或 `set_properties`。
  - `name`：样式或图层名称。
  - `properties`：要新增或修改的属性；图层支持 `color`、`linetype`、`on`、`locked`、`freeze`，文字样式支持字体、宽度和倾斜角等属性。
- `zwcad_manage_view`
  - `action`：`list_layouts`、`get_active_layout`、`add_layout`、`set_active_layout`、`list_views`、`add_view`、`set_active_space` 或 `get_active_space`。
  - `name`：布局或视图名称。
  - `params`：创建视图、布局或切换空间所需的参数；`set_active_space` 使用 `space=model|paper`。
- `zwcad_zoom`
  - `mode`：`extents`、`all`、`previous`、`window`、`center` 或 `scale`。
  - `params`：`window` 使用两个角点；`center` 使用中心点和可选放大倍数；`scale` 使用比例和可选比例类型。
- `zwcad_manage_document`
  - `action`：`new`、`save`、`close`、`info`、`list`、`activate`、`export`、`import`、`plot`、`regen`、`start_undo`、`end_undo` 或 `wblock`。
  - `params`：`save` 使用 `file_path`；`close` 使用 `save_changes`；`activate` 使用文档名；`export` / `import` 使用文件名及格式或插入参数；`plot` 使用输出文件和打印配置；`regen` 使用视口范围；`wblock` 使用文件名和可选选择集名称。
- `zwcad_manage_table`
  - `action`：`set_cell`、`get_cell`、`insert_rows`、`delete_rows`、`set_column_width`、`set_row_height` 或 `merge_cells`。
  - `params`：单元格动作使用 `row`、`col`、`text`；行操作使用行索引、数量和高度；列宽使用列索引和宽度；合并使用起止行列。
  - `object_type`、`property_name`、`property_value`、`handle`：表格实体定位参数。
- `zwcad_select_entities`
  - `action`：`select`、`by_polygon`、`get_items`、`get_picked`、`list`、`clear` 或 `delete`。
  - `params`：`select` 使用选择模式和窗口坐标；`by_polygon` 使用多边形模式和 `points`；查询动作使用选择集名称和最大数量；选择动作可附带 `filter`、`return_items`。
  - `filter`：支持 `entity_type`、`dimstyle`、`layer`、`color`、`linetype`、`textstyle`、`block_name`、`visible`、`space` 等 DXF 条件。
- `zwcad_manage_block`
  - `action`：`list`、`info`、`create` 或 `get_attributes`。
  - `name`：图块定义名称；`create` 和 `info` 需要使用。
  - `params`：创建图块时可使用 `x`、`y`、`z` 原点，列表查询可用 `detail`。
  - `object_type`、`property_name`、`property_value`、`handle`：获取图块引用属性时的实体定位参数。

#### 系统与诊断参数

- `zwcad_get_variable`：`name` 是系统变量名称，例如 `DIMSCALE`、`LTSCALE`、`OSMODE`。
- `zwcad_set_variable`：`name` 是系统变量名称，`value` 是要写入的值。
- `zwcad_get_app_info`：`scope` 选择信息范围：`cad`、`mech_version`、`mech_cad_path`、`mech_zwm_path`、`mech_style_path` 或 `mech_about`。
- `zwcad_get_capabilities`：`probe_cad` 控制是否实际探测当前 CAD 连接。
- `zwcad_diagnose`：`probe_cad` 控制是否在诊断中探测 CAD 连接。
- `zwcad_mech_diagnose`：无输入参数，执行机械应用、数据库、标题栏和类型库探测。

#### 机械扩展参数

- `zwcad_mech_manage_title_block`
  - `action`：`get_info`、`set_field`、`update_batch`、`get_field_count` 或 `get_field_by_index`。
  - `params`：`set_field` 使用 `field_name`、`value`；`update_batch` 使用 `fields` 字典；`get_field_by_index` 使用 `index`。
- `zwcad_mech_manage_frame`
  - `action`：`list`、`get_info`、`get_count`、`get_name_by_index`、`get_name_by_point`、`get_next_name`、`switch`、`update` 或 `refresh`。
  - `params`：按动作使用 `index`、`x,y,[z]`、`frame_name`，或图框的宽高、方向、比例和样式属性。
- `zwcad_mech_create_frame`
  - `std_name`：制图标准，例如 `GB`、`ISO`、`DIN`。
  - `frame_size_name`：图幅名称，例如 `A3`。
  - `orientation`：`landscape` 或 `portrait`。
  - `width`、`height`：自定义图框宽高，默认由图幅配置决定。
  - `scale1`、`scale2`：图框比例参数。
  - `title_style_name`、`bom_style_name`、`dhl_style_name`、`fjl_style_name`、`csl_style_name`、`ggl_style_name`、`frame_style_name`：标题栏、明细表、附加栏和图框样式名称。
  - `have_dhl`、`have_fjl`、`have_btl`、`have_csl`、`have_ggl`：是否创建对应栏位。
- `zwcad_mech_manage_bom`
  - `action`：`get_row_count`、`get_row`、`add_row`、`update_row`、`insert_row`、`delete_row`、`set_field`、`get_field`、`get_field_count`、`batch_update` 或 `refresh`。
  - `params`：行操作使用 `row_index` 或 `index`；新增和更新使用 `data`；字段操作使用 `field_key` 或 `field_index`；批量更新使用 `rows`。
- `zwcad_mech_create_partlist`：无输入参数，在当前图纸中通过机械 CAD 命令创建明细表实体。
- `zwcad_mech_manage_db`
  - `action`：`open`、`save` 或 `close`。
  - `params`：`open` 使用可选 `file_path`；`save` 使用可选保存标志。BOM、标题栏和图框修改后的 DWG 保存应使用文档工具。
- `zwcad_mech_doc`
  - `action`：`open`、`new` 或 `new_named`。
  - `file_path`：打开或新建文档的文件路径。
  - `template`：`new_named` 使用的模板名称或路径。
- `zwcad_mech_cad_environment_init`：`std_name` 是要初始化的 CAD 标准，例如 `GB`、`ISO`、`DIN`。
- `zwcad_mech_get_balloon`：`text` 是可选的球标文字或序号过滤条件。
- `zwcad_mech_insert_balloon`
  - `arrow_x`、`arrow_y`、`arrow_z`：引线箭头位置。
  - `symbol_x`、`symbol_y`、`symbol_z`：球标符号位置。
  - `text`：球标显示文字。
  - `seq_type`：序号类型，取值 0-6。
  - `has_leader`：是否绘制引线。
  - `mode`：机械 CAD 球标插入模式。

#### 扩展数据与 CAD 工具参数

- `zwcad_manage_dictionary`
  - `action`：`list`、`add`、`get_items`、`add_object`、`get_object`、`remove`、`rename`、`add_xrecord`、`get_xrecord`、`set_xrecord`、`get_entity_dict` 或 `has_entity_dict`。
  - `params`：按动作使用 `name`、`dict_name`、`keyword`、`object_name`、`old_name`、`new_name`、`handle`、`data_types`、`data_values`。
- `zwcad_manage_xdata`
  - `action`：`list_apps`、`register_app`、`get_xdata`、`set_xdata` 或 `delete_xdata`。
  - `params`：使用 `handle`、`app_name`、`data_types`、`data_values`；写入时 `data_types[0]` 应为 1001，`data_values[0]` 应为已注册应用名。
- `zwcad_manage_utility`
  - `action`：`translate_coordinates`、`polar_point`、`angle_to_real`、`angle_to_string`、`real_to_string`、`distance_to_real`、`prompt` 或 `get_object_id_string`。
  - `params`：坐标转换使用 `point`、`from_system`、`to_system`、`displacement`；极坐标使用 `point`、`angle`、`distance`；角度和距离转换使用字符串、单位和精度；对象 ID 查询使用 `handle`、`hex`。

---

## 进程与文档安全约束（必须遵守）

- **严禁自行强行关闭 ZWCAD 进程**：未经用户同意，不得以任何方式终止 ZWCAD 进程。
- **破坏性操作必须先确认**：删除实体、覆盖保存、关闭文档、替换插件、修改系统变量等写操作会直接改变当前 DWG，**执行前必须向用户说明并征得同意**，必要时提示先备份图纸。
- **单活动实例**：同一时间只操作一个 ZWCAD 系列实例。多开后 COM 可能连接非预期窗口，操作前先调用 `zwcad_get_capabilities(probe_cad=true)` 确认活动产品与图纸。

---

## 工作流原则（按序执行）

1. **环境与开画前探测**：先按上文「环境前提检查」确认 ①Windows 平台、②已安装 ZWCAD 且打开 DWG、③uvx 可用；再调用 `zwcad_get_capabilities(probe_cad=true)` 确认活动产品、图纸、已挂载工具组；`zwcad_get_app_info(scope="cad")` 验证平台 COM。
2. **先查询后操作**：绘图、标注、变换、样式管理等操作前，先用对应查询工具确认目标实体、名称与参数，避免盲目调用；同批绘制用 `zwcad_draw_batch` 一次提交，减少交互轮次。
3. **机械流程**：机械诊断 → 初始化标准 → 建图框 → 填标题栏 → 球标/BOM，按此顺序执行。
4. **排障**：`zwcad_diagnose(probe_cad=true)` 获取平台/机械连接状态与修复建议。

> 绘图、标注、变换、样式管理等工具的参数与枚举值可能随版本演进；调用前通过 `tools/list` 及目标工具的 description 与 input schema 获取最新定义。

---

## 常见错误场景

| 错误场景           | 表现                                                                                            | 解决方案                                                                                                                                    |
| ------------------ | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 非 Windows 系统    | 运行环境为 macOS/Linux，工具全部不可用                                                          | 直接告知用户"本 MCP 只支持 Windows"并停止操作，详见「环境前提检查 ①」                                                                     |
| 未安装 ZWCAD       | 探测不到 CAD 实例：`platform.available=false` / `Connection closed`                            | 直接告知用户下载安装 ZWCAD：https://www.zwsoft.cn/product/zwcad ，装好打开 DWG 后再重连，详见「环境前提检查 ②」                            |
| uvx 不在 PATH      | `uvx --version` 报错，但常见路径下能找到 `uvx.exe`                                                | **不要重装**，补 PATH 后重启终端与 WorkBuddy，见「③ A」                                                                                |
| uv 未安装          | 命令和常见路径都找不到 `uvx.exe`                                                                  | 一键装 uv（自带 uvx）后重连，见「③ B」                                                                                                   |
| 已有本地 MCP 服务  | `~/.workbuddy/mcp.json` 中服务已配置但 `disabled: true`，venv 完整                                | 连接器管理页启用即可绕开 uvx，见「③ C」                                                                                                  |
| 未启动/未打开图纸  | `Connection closed`、COM 初始化错误（-2147221008）                                              | 启动 ZWCAD 并打开 DWG，重启 MCP                                                                                                             |
| 机械工具失败       | `MECHANICAL_NOT_AVAILABLE` / `TYPELIB_NOT_LOADED`                                               | 调用 `zwcad_mech_diagnose` 获取逐项探测结果与修复建议；必要时设置 `PYZWCADMECH_TLB_PATH` |
| 机械类型库解析失败 | `TYPELIB_NOT_LOADED`，`typelib_error` 含 `-2147312566`（`0x80029C4A`）「加载类型库/DLL 时出错」 | 按下方「机械类型库加载失败（-2147312566）的处置」分步处理，多数情况在第 1~3 步内解决                                                        |
| 首次拉取依赖失败   | `uvx` 下载慢、超时或网络错误                                                                    | 配置 `UV_DEFAULT_INDEX` 指向国内镜像（如 `https://pypi.tuna.tsinghua.edu.cn/simple`）后重启客户端                                           |
| 中文乱码           | `mbcs codec can't decode bytes`                                                                 | 确认使用本项目 server（`PYTHONUTF8=1`）并完全重启 WorkBuddy                                                                                 |
| 操作错窗口         | 多开时改到非预期图纸                                                                            | 关闭其他 ZWCAD 实例，仅保留目标产品后重连，并重新执行环境探测                                        |
| 实体找不到         | 返回空结果                                                                                      | 先用 `zwcad_get_objects_in_model` 确认真实 object_type/handle，再过滤                                                                       |
| 参数不匹配         | `缺少参数` 错误                                                                                 | 对照工具 description 补全必填字段；角度用弧度                                                                                               |
| 机械样式缺失       | 图框/标题栏操作报 XML 解析错误                                                                  | 用 `zwcad_get_app_info(scope="mech_style_path")` 查询本机实际样式路径，并确认对应标准（如 GB）的样式文件存在 |

> 工具返回的 `error` / `code` / `hint` 三字段是排障的权威信息；表中未覆盖的错误码同样按这三字段排查，并以工具 description 为准。

### 机械类型库加载失败的处置

**场景**：机械工具（图框/标题栏/明细表等）返回 `TYPELIB_NOT_LOADED`；`zwcad_mech_diagnose` 显示 `typelib_loaded: false`、`typelib_error` 含 `-2147312566`（`0x80029C4A`）「加载类型库/DLL 时出错」。按顺序处置：

1. **确认产品环境（多数在此解决）**：已装与 ZWCAD 版本匹配的中望机械、已完整启动并打开至少一张 DWG；近期卸载/升级/移动过组件的，以管理员身份执行**修复安装**，确保 `ZwmToolKit` 正确注册。
2. **核对类型库路径**：依赖 `ZwmToolKit.tlb`，默认在 `C:\Program Files\ZWSOFT\ZWCAD Mechanical <版本> Chs\Zwcadm\ZwmToolKit.tlb`；自动定位失败则把实际路径设为 `PYZWCADMECH_TLB_PATH` 并**完全重启 MCP 连接器**（须重建服务进程，仅重开客户端无效）。
3. **诊断与验证**：`zwcad_mech_diagnose` 复查 `typelib_loaded` / `typelib_source` / `typelib_error`。
4. **解析器容错（前 3 步仍失败时）**：comtypes 默认"一错即弃"——遇到个别无法从当前环境解析的引用就中止整份类型库加载，与产品功能无关：
   - **定位环境**：`wmic process` / 任务管理器确认 MCP **实际加载的 Python 环境路径**；`uvx` 启动时缓存目录可能并存**多个同名虚拟环境**，补丁与清缓存都必须落在 MCP 实际加载的那个，否则"改完重启仍失败"。
   - **打补丁**：该环境 `comtypes/tools/tlbparser.py` 中，把 `ParseInterface` / `ParseCoClass` 内读取基类类型的调用（`GetRefTypeOfImplType` / `GetRefTypeInfo`）包进 try/except，失败则告警跳过（**改前先备份**）。
   - **清缓存**：删除 `comtypes/gen` 下残留的 `_*.py` / `_*.pyc`，否则旧缓存被再次导入。若重生成时报 `mbcs codec can't decode bytes`，把同环境 `comtypes/tools/codegenerator/codegenerator.py` 生成文件头的编码声明由 `mbcs` 改为 `utf-8` 后重试。
   - **彻底重连**：断开→重连 MCP 重建进程。服务端会缓存首次加载失败状态，仅刷新客户端或重开应用不生效。
   - 此为运行环境级临时规避，升级 comtypes / 重装环境 / 换机后需重新应用。

---

## 最佳实践

- **修改优先于重建**：能用 `zwcad_transform_entity` / `zwcad_modify_entity` 就不删了重画。
- **单位与弧度**：坐标沿用当前图纸单位；角度一律弧度。
- **样式走 XML**：标准/标题栏/BOM/图框样式名来自本机 `styles/*.xml`，可用 `zwcad_mech_manage_*` 查询后使用。

> 探测先行、先查询后操作、写入需确认等约定已并入「工作流原则」与「进程与文档安全约束」；工具能力以运行时 `tools/list` 返回为准。
