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
- 详细工具索引和参数语义见本 Skill 后面的附录，不影响上述发现流程。

---

## 工具能力与参数参考

下表概述各工具支持的功能、动作及参数含义；具体参数以运行时 `tools/list` 返回的 schema 为准。

### 绘图、注释与标注

| 工具 | 作用 | 参数 |
| --- | --- | --- |
| `zwcad_draw_entity` | 绘制：`line` 直线、`circle` 圆、`arc` 圆弧、`ellipse` 椭圆、`lwpolyline` 轻量多段线、`polyline` 多段线、`spline` 样条、`point` 点、`ray` 射线、`xline` 构造线、`mline` 多线、`3d_polyline` 三维多段线。 | `entity_type`：实体类型；`params`：几何数据，直线使用起止点，圆使用圆心和半径，多段线使用 `vertices`；`layer`：目标图层。 |
| `zwcad_draw_batch` | 批量绘制上述二维或三维实体，减少调用次数。 | `entities`：实体列表，每项包含 `entity_type`、`params`，可选单项 `layer`；`layer`：默认图层。 |
| `zwcad_draw_3d_solid` | 绘制：`box` 长方体、`cylinder` 圆柱、`cone` 圆锥、`sphere` 球体、`torus` 圆环、`wedge` 楔体、`3d_face` 三维面。 | `solid_type`：实体类型；`params`：中心点或原点、半径、长度、宽度、高度等几何数据；`layer`：目标图层。 |
| `zwcad_add_annotation` | 添加：`text` 单行文字、`mtext` 多行文字、`leader` 引线、`tolerance` 形位公差、`mleader` 多重引线、`hatch` 填充、`table` 表格。 | `annotation_type`：注释类型；`params`：文字内容、位置、字高、引线点、填充图案或表格行列等；`layer`：目标图层。 |
| `zwcad_add_dimension` | 创建：`aligned` 对齐标注、`rotated` 旋转标注、`diametric` 直径标注、`radial` 半径标注、`angular` 角度标注、`ordinate` 坐标标注。 | `dim_type`：标注类型；`params`：标注点和文字位置，可选公差、配合、前后缀和文字覆盖；`layer`：目标图层。 |
| `zwcad_insert_block` | 在指定位置插入图块引用，并设置缩放、旋转和图层。 | `block_name`：图块定义名；`x,y,z`：插入点；`x_scale,y_scale,z_scale`：三轴缩放；`rotation`：弧度角；`layer`：目标图层。 |

### 实体查询、修改与尺寸查询

| 工具 | 作用 | 参数 |
| --- | --- | --- |
| `zwcad_find_object` | 按句柄或属性条件查找第一个实体。 | `handle`：实体句柄；`object_type`：对象类型；`property_name`：筛选属性名；`property_value`：筛选属性值。 |
| `zwcad_get_objects_in_model` | 获取模型空间全部对象或指定类型对象。 | `object_type`：类型过滤；`limit`：最大返回数量，默认 500。 |
| `zwcad_get_entity_info` | 获取实体属性、几何数据和边界框。 | `handle`、`object_type`、`property_name`、`property_value`：实体定位参数。 |
| `zwcad_set_entity_properties` | 修改图层、颜色、线型、线型比例、线宽和可见性。 | `layer`：图层；`color`：颜色索引；`linetype`：线型；`linetype_scale`：线型比例；`lineweight`：线宽；`visible`：可见性；其余为实体定位参数。 |
| `zwcad_transform_entity` | `copy` 复制、`move` 移动、`rotate` 旋转、`mirror` 镜像、`scale` 缩放、`delete` 删除、`array_polar` 环形阵列、`array_rectangular` 矩形阵列。 | `action`：变换动作；`params`：复制/移动使用起止点，旋转使用基点和角度，镜像使用镜像线两点，缩放使用基点和比例，阵列使用中心/数量/间距；`handle` 或属性组合：目标实体。 |
| `zwcad_modify_entity` | 修改：`circle`、`arc`、`line`、`text`、`mtext`、`polyline`、`spline`、`dimension`；以及 `offset` 偏移、`explode` 分解。 | `entity_type`：修改类型；`params`：半径、圆心、端点、文字、闭合、偏差、公差或偏移距离等；其余为实体定位参数。 |
| `zwcad_query_dimensions` | `summary` 查询尺寸摘要，`full` 查询完整几何、文字和样式信息。 | `detail`：返回详情级别；`layer`：标注图层过滤。 |

实体定位统一优先使用 `handle`；没有句柄时使用 `object_type` + `property_name` + `property_value`。

### 样式、视图与文档

| 工具 | 作用 | 参数 |
| --- | --- | --- |
| `zwcad_manage_style` | `list` 列出样式、`add` 新增样式、`set_active` 设置当前样式、`set_properties` 修改样式。支持图层、线型、文字样式和标注样式。 | `style_type`：样式类型；`action`：动作；`name`：样式名；`properties`：颜色、线型、开关、字体、宽度等属性。 |
| `zwcad_manage_view` | `list_layouts`、`get_active_layout`、`add_layout`、`set_active_layout` 管理布局；`list_views`、`add_view` 管理视图；`set_active_space`、`get_active_space` 切换或读取模型/图纸空间。 | `action`：视图动作；`name`：布局或视图名；`params`：空间、视图范围等参数。 |
| `zwcad_zoom` | `extents` 全图范围、`all` 全部对象、`previous` 上一次视图、`window` 窗口范围、`center` 中心缩放、`scale` 比例缩放。 | `mode`：缩放模式；`params`：窗口角点、中心点、放大倍数或比例类型。 |
| `zwcad_manage_document` | `new` 新建、`save` 保存、`close` 关闭、`info` 信息、`list` 列表、`activate` 激活、`export` 导出、`import` 导入、`plot` 打印、`regen` 重生成、`start_undo` / `end_undo` 撤销组、`wblock` 写块。 | `action`：文档动作；`params`：文件路径、文档名、格式、打印配置、视口范围或选择集名。 |
| `zwcad_manage_table` | `set_cell` / `get_cell` 设置或读取单元格、`insert_rows` / `delete_rows` 插入或删除行、`set_column_width` 设置列宽、`set_row_height` 设置行高、`merge_cells` 合并单元格。 | `action`：表格动作；`params`：行列索引、文本、数量、宽高或合并范围；其余为表格实体定位参数。 |
| `zwcad_select_entities` | `select` 窗口/交叉/全部选择、`by_polygon` 多边形选择、`get_items` 读取选择集、`get_picked` 读取当前拾取集、`list` 列出选择集、`clear` 清空、`delete` 删除选择集。 | `action`：选择集动作；`params`：模式、坐标点、选择集名、最大数量、过滤器和是否返回对象；`filter`：类型、图层、颜色、线型、可见性等条件。 |
| `zwcad_manage_block` | `list` 列出图块、`info` 查看定义、`create` 创建定义、`get_attributes` 读取图块引用属性。 | `action`：图块动作；`name`：图块名；`params`：原点和详情开关；获取属性时使用实体定位参数。 |

### 系统与诊断

| 工具 | 作用 | 参数 |
| --- | --- | --- |
| `zwcad_get_variable` | 读取系统变量值。 | `name`：变量名，例如 `DIMSCALE`、`LTSCALE`、`OSMODE`。 |
| `zwcad_set_variable` | 写入系统变量值。 | `name`：变量名；`value`：新值。 |
| `zwcad_get_app_info` | `cad` 获取 ZWCAD 版本/路径/窗口；`mech_version` 获取机械版本；`mech_cad_path` 获取机械安装路径；`mech_zwm_path` 获取类型库路径；`mech_style_path` 获取样式路径；`mech_about` 获取机械信息。 | `scope`：信息范围。 |
| `zwcad_get_capabilities` | 探测当前产品、连接状态、工具组和活动图纸。 | `probe_cad`：是否实际连接并探测 CAD。 |
| `zwcad_diagnose` | 诊断平台和机械后端，返回错误和修复建议。 | `probe_cad`：是否探测 CAD 连接。 |
| `zwcad_mech_diagnose` | 探测机械应用、数据库、标题栏和 ZwmToolKit 类型库。 | 无输入参数。 |

### 机械扩展

| 工具 | 作用 | 参数 |
| --- | --- | --- |
| `zwcad_mech_manage_title_block` | `get_info` 读取全部字段、`set_field` 设置字段、`update_batch` 批量更新、`get_field_count` 读取字段数、`get_field_by_index` 按索引读取字段。 | `action`：标题栏动作；`params`：`field_name` 字段名、`value` 字段值、`fields` 批量字段、`index` 字段索引。 |
| `zwcad_mech_manage_frame` | `list` 列出图框、`get_info` 读取信息、`get_count` 统计数量、`get_name_by_index` / `get_name_by_point` / `get_next_name` 查询名称、`switch` 切换、`update` 更新、`refresh` 刷新。 | `action`：图框动作；`params`：索引、坐标、`frame_name`、宽高、方向、比例和样式属性。 |
| `zwcad_mech_create_frame` | 创建指定标准、图幅、方向和栏位的图框。 | `std_name`：标准；`frame_size_name`：图幅；`orientation`：方向；`width,height`：自定义尺寸；`scale1,scale2`：比例；各 `*_style_name`：样式；各 `have_*`：栏位开关。 |
| `zwcad_mech_manage_bom` | `get_row_count` 统计、`get_row` 读取、`add_row` 新增、`update_row` 更新、`insert_row` 插入、`delete_row` 删除、`set_field` 设置字段、`get_field` 读取字段、`get_field_count` 统计字段、`batch_update` 批量更新、`refresh` 刷新。 | `action`：BOM 动作；`params`：`row_index` / `index` 行索引、`data` 行数据、`field_key` / `field_index` 字段定位、`rows` 批量数据。 |
| `zwcad_mech_create_partlist` | 在当前图纸中创建明细表实体。 | 无输入参数。 |
| `zwcad_mech_manage_db` | `open` 打开数据库、`save` 保存数据库、`close` 关闭数据库。 | `action`：数据库动作；`params`：`file_path` 文件路径或保存选项。 |
| `zwcad_mech_doc` | `open` 打开、`new` 新建、`new_named` 按名称或模板新建机械文档。 | `action`：文档动作；`file_path`：文件路径；`template`：模板路径或名称。 |
| `zwcad_mech_cad_environment_init` | 按指定标准初始化机械 CAD 环境。 | `std_name`：标准名，例如 `GB`、`ISO`、`DIN`。 |
| `zwcad_mech_get_balloon` | 按文字条件读取球标信息。 | `text`：可选球标文字或序号过滤条件。 |
| `zwcad_mech_insert_balloon` | 在指定位置插入球标，可带引线并设置序号类型。 | `arrow_x/y/z`：箭头位置；`symbol_x/y/z`：球标位置；`text`：显示文字；`seq_type`：序号类型；`has_leader`：是否带引线；`mode`：插入模式。 |

### 扩展数据与 CAD 工具

| 工具 | 作用 | 参数 |
| --- | --- | --- |
| `zwcad_manage_dictionary` | `list` 列出字典、`add` 创建字典、`get_items` 读取条目、`add_object` / `get_object` / `remove` 管理对象、`rename` 重命名、`add_xrecord` / `get_xrecord` / `set_xrecord` 管理 XRecord、`get_entity_dict` / `has_entity_dict` 查询实体字典。 | `action`：字典动作；`params`：`name`、`dict_name`、`keyword`、`object_name`、`old_name`、`new_name`、`handle`、`data_types`、`data_values`。 |
| `zwcad_manage_xdata` | `list_apps` 列出应用、`register_app` 注册应用、`get_xdata` 读取、`set_xdata` 写入、`delete_xdata` 删除扩展数据。 | `action`：XData 动作；`params`：`handle` 实体句柄、`app_name` 应用名、`data_types` 类型码、`data_values` 数据值。 |
| `zwcad_manage_utility` | `translate_coordinates` 坐标转换、`polar_point` 极坐标计算、`angle_to_real` / `angle_to_string` 角度转换、`real_to_string` / `distance_to_real` 数值转换、`prompt` 输出提示、`get_object_id_string` 获取对象 ID。 | `action`：工具动作；`params`：点、坐标系、角度、距离、单位、精度、提示文本、句柄和十六进制选项。 |

当用户提出能力需求时，先从本附录定位工具，再读取该工具的运行时 schema；如果工具未出现在 `tools/list` 中，才判断当前服务版本不具备该能力。


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
