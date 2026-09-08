# ZWCAD MCP Server

中望CAD（ZWCAD）自动化 MCP 服务，让大模型通过 MCP 协议直接操控 ZWCAD 平台与中望机械CAD，完成绘图、标注、图层/块/样式管理，以及图框、标题栏、明细表（BOM）等机械操作。

## 功能概览

| 分类       | 工具数 | 说明                                                                                                       |
| ---------- | ------ | ---------------------------------------------------------------------------------------------------------- |
| 绘图       | 3      | `zwcad_draw_entity`（2D）、`zwcad_draw_batch`（批量）、`zwcad_draw_3d_solid`（3D）                         |
| 注释与标注 | 3      | `zwcad_add_annotation`、`zwcad_add_dimension`、`zwcad_insert_block`                                        |
| 实体操作   | 4      | `zwcad_transform_entity`、`zwcad_modify_entity`、`zwcad_get_entity_info`、`zwcad_set_entity_properties`    |
| 对象查询   | 3      | `zwcad_find_object`、`zwcad_get_objects_in_model`、`zwcad_query_dimensions`                                |
| 样式管理   | 1      | `zwcad_manage_style`（图层/线型/文字/标注样式 CRUD）                                                       |
| 视图与布局 | 2      | `zwcad_manage_view`、`zwcad_zoom`                                                                          |
| 文档管理   | 1      | `zwcad_manage_document`                                                                                    |
| 表格操作   | 1      | `zwcad_manage_table`                                                                                       |
| 选择集     | 1      | `zwcad_select_entities`                                                                                    |
| 图块管理   | 1      | `zwcad_manage_block`                                                                                       |
| 系统工具   | 3      | `zwcad_get_variable`、`zwcad_set_variable`、`zwcad_get_app_info`                                           |
| 诊断工具   | 3      | `zwcad_get_capabilities`、`zwcad_diagnose`、`zwcad_mech_diagnose`                                          |
| 标题栏     | 1      | `zwcad_mech_manage_title_block`                                                                            |
| 图框       | 2      | `zwcad_mech_manage_frame`、`zwcad_mech_create_frame`                                                       |
| 明细表     | 2      | `zwcad_mech_manage_bom`、`zwcad_mech_create_partlist`                                                      |
| 机械数据库 | 1      | `zwcad_mech_manage_db`                                                                                     |
| 机械应用   | 4      | `zwcad_mech_doc`、`zwcad_mech_cad_environment_init`、`zwcad_mech_get_balloon`、`zwcad_mech_insert_balloon` |
| 扩展数据   | 3      | `zwcad_manage_dictionary`、`zwcad_manage_xdata`、`zwcad_manage_utility`                                    |

**共计 39 个工具**，按对机械环境的依赖划分为三组：

| 分组           | 数量 | 说明                                                                                          |
| -------------- | ---- | --------------------------------------------------------------------------------------------- |
| ZWCAD 平台工具 | 26   | 不依赖中望机械，只要 ZWCAD 在运行即可使用                                                     |
| 机械扩展工具   | 11   | 上表中的标题栏(1)、图框(2)、明细表(2)、机械数据库(1)、机械应用(4)，以及 `zwcad_mech_diagnose` |
| 统一诊断工具   | 2    | `zwcad_get_capabilities`、`zwcad_diagnose`，同时报告平台与机械状态                            |

机械工具在未连接中望机械或类型库未加载时返回明确错误（详见「类型库依赖矩阵」）。

## 系统要求

- **操作系统**：Windows 10/11 x64
- **CAD 软件**：[中望CAD](https://www.zwsoft.cn/) 或 [中望机械CAD](https://www.zwsoft.cn/product/zwcad/mfg) 已安装并运行，且至少打开一张 DWG
- **Python**：3.10+；使用 `uvx` 免安装方式则无需手动准备 Python（会自动拉取）
- **机械工具**：需要中望机械CAD 及其匹配版本的 `ZwmToolKit`
- **位数**：Python 与 CAD 位数建议一致

## 快速开始

### 1. 启动中望CAD（或中望机械CAD）

确保中望CAD（或中望机械CAD）已启动并打开了一张 DWG 文件。机械工具还需中望机械CAD 及匹配版本的 `ZwmToolKit`。

### 2. 安装 MCP 服务（可选）

可选步骤，仅在需要固定版本或离线部署时执行。

使用本服务**无需先安装本包**：MCP 客户端通过 `uvx zwcad-mcp` 启动服务，`uvx` 会在启动时自动准备 Python 环境、创建隔离环境并拉取全部依赖（等价于 npm 世界的 `npx`）。前置条件：本机装有 [uv](https://docs.astral.sh/uv/getting-started/installation/)。

仅当需要固定版本或离线部署时，才将本包安装到本机 Python：

```bash
pip install zwcad-mcp
```

验证安装：

```bash
python -c "import importlib.metadata as m; print(m.version('zwcad-mcp'))"
```

### 3. 配置 MCP 客户端

本项目是标准 MCP 服务（stdio），任意支持 MCP 协议的客户端均可接入。各客户端使用同一份配置，只是配置文件位置不同：

```json
{
  "mcpServers": {
    "zwcad": {
      "command": "uvx",
      "args": ["zwcad-mcp"],
      "env": {
        "PYTHONUTF8": "1",
        "UV_DEFAULT_INDEX": "https://pypi.tuna.tsinghua.edu.cn/simple"
      }
    }
  }
}
```

上面的配置采用免安装方式（由 `uvx` 启动）：`UV_DEFAULT_INDEX` 指定国内镜像以加速依赖下载，网络可直连 PyPI 官方源时可删除该行。若已按步骤 2 执行了 pip 安装，可将 `command` 改为 `"zwcad-mcp"` 并删除 `args` 一行。

#### Cursor

写入项目内 `.cursor/mcp.json` 或全局 `~/.cursor/mcp.json`，重启 Cursor 后生效。

#### Claude Desktop

写入 `%APPDATA%\Claude\claude_desktop_config.json`，重启 Claude Desktop 后生效。

#### WorkBuddy

写入 WorkBuddy 的 MCP 配置文件，重启后生效。

#### 其他客户端

任意支持 MCP stdio 的客户端均可接入：命令为 `uvx zwcad-mcp`（已执行 pip 安装时可用 `zwcad-mcp`），并建议设置环境变量 `PYTHONUTF8=1`。

### 4. 验证接入

在客户端中让 AI 调用 `zwcad_get_capabilities`：能返回 ZWCAD 版本与工具组清单即表示接入成功。若失败，调用 `zwcad_diagnose`（机械问题用 `zwcad_mech_diagnose`）查看逐项探测结果与修复建议。

> 本服务为 stdio 模式，正常使用时由 MCP 客户端自动拉起，无需手动启动。如需排查启动阶段的问题，可在命令行执行 `zwcad-mcp`（等价的本地方式：`python src/server.py`）。

## 工具详细说明

### 绘图工具

| 工具                  | 说明                           | entity_type / solid_type                                                                                                |
| --------------------- | ------------------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| `zwcad_draw_entity`   | 绘制2D实体                     | `line`, `circle`, `arc`, `ellipse`, `lwpolyline`, `polyline`, `spline`, `point`, `ray`, `xline`, `mline`, `3d_polyline` |
| `zwcad_draw_batch`    | 批量绘制多个实体，减少交互轮次 | `entities` 为 dict 列表，每项含 `entity_type` 与 `params`，可选 `layer`                                                 |
| `zwcad_draw_3d_solid` | 绘制3D实体                     | `box`, `cylinder`, `cone`, `sphere`, `torus`, `wedge`, `3d_face`                                                        |

### 注释与标注

| 工具                   | 说明                          | annotation_type / dim_type                                          |
| ---------------------- | ----------------------------- | ------------------------------------------------------------------- |
| `zwcad_add_annotation` | 添加注释对象                  | `text`, `mtext`, `leader`, `tolerance`, `mleader`, `hatch`, `table` |
| `zwcad_add_dimension`  | 添加标注（支持公差/配合代号） | `aligned`, `rotated`, `diametric`, `radial`, `angular`, `ordinate`  |
| `zwcad_insert_block`   | 在指定位置插入图块            | `rotation` 为弧度                                                   |

**标注公差与配合**（`zwcad_add_dimension` 与 `zwcad_modify_entity(entity_type="dimension")` 通用，均放在 `params` 中，可选）：

| 参数                                            | 说明                                                                                                |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `tolerance_display`                             | 公差显示方式：`none`\|`symmetrical`(对称)\|`deviation`(偏差)\|`limits`(极限)\|`basic`(基本)，或 0-4 |
| `upper_deviation` / `lower_deviation`           | 上/下偏差（带符号，如 `0.021` / `-0.05`）                                                           |
| `tolerance_precision`                           | 公差小数位数 0-8                                                                                    |
| `tolerance_height_scale`                        | 公差字高系数（GB 常用 0.7）                                                                         |
| `fit_symbol`                                    | 配合代号，如 `"H7"`、`"H7/g6"`（含 `/` 或 `^` 时默认堆叠为分数显示）                                |
| `fit_stacked` / `fit_height_scale`              | 配合代号是否堆叠（默认 `True`）/ 字高系数（默认 0.7）                                               |
| `text_prefix` / `text_suffix` / `text_override` | 标注文字前缀/后缀/替代（`<>` 表示测量值）                                                           |

示例：直径50H7孔 → `zwcad_add_dimension(dim_type="diametric", params={..., "fit_symbol": "H7"})`；
50(+0.021/0)偏差 → `params={..., "tolerance_display": "deviation", "upper_deviation": 0.021, "lower_deviation": 0}`；
已有标注补公差 → `zwcad_modify_entity(entity_type="dimension", handle="A3F", params={"tolerance_display": "limits", ...})`。

### 实体操作

| 工具                          | 说明                                       | action / entity_type                                                                             |
| ----------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| `zwcad_transform_entity`      | 实体变换                                   | `copy`, `move`, `rotate`, `mirror`, `scale`, `delete`, `array_polar`, `array_rectangular`        |
| `zwcad_modify_entity`         | 修改实体几何属性（含标注公差/配合）        | `circle`, `arc`, `line`, `text`, `mtext`, `polyline`, `spline`, `dimension`, `offset`, `explode` |
| `zwcad_get_entity_info`       | 获取实体详细信息（属性、几何数据、边界框） | -                                                                                                |
| `zwcad_set_entity_properties` | 设置实体通用属性（图层/颜色/线型等）       | -                                                                                                |

> 实体定位方式统一：`handle`（优先，O(1)）或 `object_type` + `property_name` + `property_value`。

### 对象查询

| 工具                         | 说明                                                                                                                 |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `zwcad_find_object`          | 按类型/属性/句柄查找对象                                                                                             |
| `zwcad_get_objects_in_model` | 获取模型空间对象列表（`object_type` 可选过滤，`limit` 默认 500）                                                     |
| `zwcad_query_dimensions`     | 快速查询所有标注（尺寸值/公差/文字覆盖等）；原生 DXF 过滤，远快于逐个迭代；`detail=summary\|full`，可按 `layer` 过滤 |

### 样式管理

| 工具                 | 说明                         | style_type × action                                                                                             |
| -------------------- | ---------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `zwcad_manage_style` | 图层/线型/文字/标注样式 CRUD | style_type: `layer`, `linetype`, `textstyle`, `dimstyle`; action: `list`, `add`, `set_active`, `set_properties` |

### 视图、布局与缩放

| 工具                | 说明          | action / mode                                                                                                        |
| ------------------- | ------------- | -------------------------------------------------------------------------------------------------------------------- |
| `zwcad_manage_view` | 布局/视图管理 | `list_layouts`, `get_active_layout`, `add_layout`, `set_active_layout`, `list_views`, `add_view`, `set_active_space` |
| `zwcad_zoom`        | 视图缩放      | `extents`, `all`, `window`, `center`, `scale`, `previous`                                                            |

### 文档管理

| 工具                    | 说明                              | action                                                                                                                      |
| ----------------------- | --------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `zwcad_manage_document` | 文档新建/保存/关闭/导入/导出/打印 | `new`, `save`, `close`, `info`, `list`, `activate`, `export`, `import`, `plot`, `regen`, `start_undo`, `end_undo`, `wblock` |

### 表格、选择集与图块

| 工具                    | 说明                                                                                                                              |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `zwcad_manage_table`    | 表格单元格/行/列操作（`set_cell`, `get_cell`, `insert_rows`, `delete_rows`, `set_column_width`, `set_row_height`, `merge_cells`） |
| `zwcad_select_entities` | 选择集操作（窗口/交叉/多边形/过滤器选择）                                                                                         |
| `zwcad_manage_block`    | 图块定义/信息/属性管理（`list`, `info`, `create`, `get_attributes`）                                                              |

### 系统工具

| 工具                                        | 说明                                                                                                                                 |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `zwcad_get_variable` / `zwcad_set_variable` | 读写系统变量（如 `DIMSCALE`, `LTSCALE`, `OSMODE`）                                                                                   |
| `zwcad_get_app_info`                        | 获取应用信息。scope: `cad`（ZWCAD版本/路径/窗口）、`mech_version`、`mech_cad_path`、`mech_zwm_path`、`mech_style_path`、`mech_about` |

### 诊断工具

| 工具                     | 说明                                                                                                                                                                          |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `zwcad_get_capabilities` | 查看当前可用的产品、连接状态、工具组和活动图纸                                                                                                                                |
| `zwcad_diagnose`         | 诊断平台和机械后端，并给出不修改系统的排障建议                                                                                                                                |
| `zwcad_mech_diagnose`    | 诊断机械模块连接与 ZwmToolKit 类型库加载状态。逐项探测：类型库加载、ZWCAD 应用、ZwmApp、ZwmDb、标题栏获取，返回各探测项状态与修复建议。每次调用自动重置连接缓存以获取最新状态 |

### 标题栏

| 工具                            | 说明                     | action                                                                           |
| ------------------------------- | ------------------------ | -------------------------------------------------------------------------------- |
| `zwcad_mech_manage_title_block` | 标题栏读取/设置/批量更新 | `get_info`, `set_field`, `update_batch`, `get_field_count`, `get_field_by_index` |

> ⚠️ 此工具依赖 ZwmToolKit 类型库，类型库未加载时将快速返回 `TYPELIB_NOT_LOADED` 错误。

### 图框

| 工具                      | 说明                                               | action                                                                                                                                     |
| ------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `zwcad_mech_manage_frame` | 图框查询/切换/更新/刷新                            | `list`, `get_info`, `get_count`, `get_name_by_index`, `get_name_by_point`, `get_next_name`, `switch`, `update`, `refresh`                  |
| `zwcad_mech_create_frame` | 新建图幅/图框（所有参数可选，默认从 XML 配置读取） | `std_name`（如 `GB`）、`frame_size_name`（如 `A3`）、`orientation: landscape\|portrait`；`have_*`: 各栏开关(`dhl`/`fjl`/`btl`/`csl`/`ggl`) |

> ⚠️ `zwcad_mech_create_frame` 以及 `zwcad_mech_manage_frame` 的 `get_info`/`update` 操作依赖类型库；`list`/`get_count`/`switch`/`refresh` 等操作不依赖类型库，在类型库未加载时仍可使用。

### 明细表（BOM）

| 工具                         | 说明           | action                                                                                                                                                  |
| ---------------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `zwcad_mech_manage_bom`      | 明细表增删改查 | `get_row_count`, `get_row`, `add_row`, `update_row`, `insert_row`, `delete_row`, `set_field`, `get_field`, `get_field_count`, `batch_update`, `refresh` |
| `zwcad_mech_create_partlist` | 创建明细表实体 | 发送 `_.ZwmPartlist` 命令                                                                                                                               |

> ⚠️ 除 `refresh` 外的所有操作依赖类型库。`refresh` 不依赖类型库，在类型库未加载时仍可使用。
>
> 💡 **BOM 持久化说明**：修改 BOM 数据后，`update_row`/`set_field`/`batch_update` 等操作会自动将更改写入 DWG 图纸。请勿在 BOM 修改后调用 `zwcad_mech_manage_db` 的 `save` 操作，`save` 会从图纸重载数据导致修改丢失。

### 机械模块

| 工具                              | 说明                                                                                                                    |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `zwcad_mech_manage_db`            | 机械数据库操作。action: `open`/`save`/`close`                                                                           |
| `zwcad_mech_doc`                  | 机械文档操作。action: `open`/`new`/`new_named`                                                                          |
| `zwcad_mech_cad_environment_init` | 初始化 CAD 标准环境（GB, ISO, DIN 等）                                                                                  |
| `zwcad_mech_get_balloon`          | 获取球标对象用于零件编号标注                                                                                            |
| `zwcad_mech_insert_balloon`       | 插入球标（零件序号标注），通过 LISP 命令 `Zwm_BalloonInsert` 实现。参数：箭头/符号位置、文字、序号类型(0-6)、是否带引线 |

> 以上工具不依赖类型库，在类型库未加载时仍可通过 late binding 正常工作。

### 扩展数据

| 工具                      | 说明                                   | action                                                                                                           |
| ------------------------- | -------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `zwcad_manage_dictionary` | 命名对象字典与 XRecord 管理            | `list`, `add`, `get_items`, `add_object`, `get_object`, `remove`, `rename`, `add_xrecord`, `get_xrecord`         |
| `zwcad_manage_xdata`      | 实体扩展数据(XData)读写                | `list_apps`, `register_app`, `get_xdata`, `set_xdata`, `delete_xdata`                                            |
| `zwcad_manage_utility`    | CAD 工具方法（坐标转换/角度/距离计算） | `translate_coordinates`, `polar_point`, `angle_to_real`, `angle_to_string`, `real_to_string`, `distance_to_real` |

## ZwmToolKit 类型库加载机制

机械模块（标题栏/明细表/图框等）依赖 `ZwmToolKit.tlb` 类型库。`pyzwcadmech.api` 采用 **5 级回退策略** 加载类型库，确保在各种安装环境下都能成功加载：

| 优先级 | 策略          | 说明                                                                                                      |
| ------ | ------------- | --------------------------------------------------------------------------------------------------------- |
| 1      | 文件系统 glob | 在 `C:\Program Files\ZWSOFT\ZWCAD Mechanical*\Zwcadm\` 下搜索 `ZwmToolKit*.tlb`，按版本年份排序优先选最新 |
| 2      | 环境变量      | 读取 `PYZWCADMECH_TLB_PATH` 环境变量指向的 `.tlb` 文件                                                    |
| 3      | 本地路径      | 搜索当前工作目录和包目录下的 `ZwmToolKit.tlb`                                                             |
| 4      | 预生成模块    | 复用已生成的 `comtypes.gen.ZwmToolKitLib` 模块（如预加载生成的）                                          |
| 5      | GUID 注册表   | 按类型库 GUID `{2F671C10-669F-11E7-91B7-BC5FF42AC839}` 从 Windows 注册表加载                              |

### server.py 预加载

`src/server.py`（MCP Server 主程序，入口见「快速开始」第 3 步）在导入时按上述 GUID 调用 `comtypes.client.GetModule` 预加载类型库。预加载成功时，后续 `pyzwcadmech.api` 即使文件搜索失败，也能通过策略 4 复用已生成的模块；同时将 `comtypes.client.gen_dir` 置空，使 COM 包装仅在内存中生成，避免某些中文版类型库触发 comtypes 的 mbcs 磁盘缓存解码错误。

### 运行时重试

如果类型库在 import 时加载失败（例如 ZWCAD 尚未启动），`ZwCADMech.zwm_app` 属性在首次访问时会自动调用 `reload_typelib()` 重试加载。也可通过 `zwcad_mech_diagnose` 工具触发重新诊断。

### 环境变量配置

如果类型库无法自动加载（如自定义安装路径），可在 MCP 配置中设置 `PYZWCADMECH_TLB_PATH` 环境变量，指向实际的 `ZwmToolKit.tlb`：

```json
{
  "mcpServers": {
    "zwcad": {
      "command": "uvx",
      "args": ["zwcad-mcp"],
      "env": {
        "PYTHONUTF8": "1",
        "PYZWCADMECH_TLB_PATH": "C:\\Program Files\\ZWSOFT\\<中望机械安装目录>\\Zwcadm\\ZwmToolKit.tlb"
      }
    }
  }
}
```

> 路径中的安装目录名随版本变化（形如 `ZWCAD Mechanical <年份> Chs`），请按本机实际安装目录填写；可用 `zwcad_get_app_info(scope="mech_zwm_path")` 查询真实路径。

### 类型库依赖矩阵

| 工具                                                                                                                                   | 类型库未加载时 | 说明                           |
| -------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ------------------------------ |
| `zwcad_mech_manage_title_block`                                                                                                        | ❌ 不可用      | 返回 `TYPELIB_NOT_LOADED` 错误 |
| `zwcad_mech_create_frame`                                                                                                              | ❌ 不可用      | 返回 `TYPELIB_NOT_LOADED` 错误 |
| `zwcad_mech_manage_bom`（除 refresh）                                                                                                  | ❌ 不可用      | 返回错误并附带修复提示         |
| `zwcad_mech_manage_frame`（get_info/update）                                                                                           | ❌ 不可用      | 返回错误并附带修复提示         |
| `zwcad_mech_manage_bom`（refresh）                                                                                                     | ✅ 可用        | 通过 late binding 工作         |
| `zwcad_mech_manage_frame`（list/switch/refresh 等）                                                                                    | ✅ 可用        | 通过 late binding 工作         |
| `zwcad_mech_manage_db` / `zwcad_mech_doc` / `zwcad_mech_cad_environment_init` / `zwcad_mech_get_balloon` / `zwcad_mech_insert_balloon` | ✅ 可用        | 通过 late binding 工作         |
| `zwcad_get_app_info`（mech\_\* scope）                                                                                                 | ✅ 可用        | 通过 late binding 工作         |
| 所有 pyzwcad 基础工具（绘图/标注/变换/查询等）                                                                                         | ✅ 可用        | 完全不依赖类型库               |

## 示例：通过 AI 创建图框

在 Cursor / Claude Desktop / WorkBuddy 中，告诉 AI：

> "在中望机械CAD中，创建一个A3横向图框，GB标准，包含标题栏和附加栏"

AI 会自动调用 `zwcad_mech_create_frame` 工具：

```python
zwcad_mech_create_frame(
    frame_size_name="A3",
    orientation="landscape",
    std_name="GB",
    have_btl=True,
    have_fjl=True
)
```

## 项目结构

### 安装后的内容（wheel / sdist）

```
server.py                 # MCP Server 主程序（39 个工具）
hatch_info.py             # 剖面线边界环提取（COM + LISP 回退）
README.md
LICENSE
THIRD_PARTY_NOTICES.md
```

## 架构

```
AI 客户端（Cursor / Claude Desktop / WorkBuddy / 任意 MCP 客户端）
        │
        │ MCP 协议（stdio, JSON-RPC）
        ▼
   FastMCP Server（入口: src/server.py, 39 个工具）
        │
        ├── pyzwcad ──────► ZWCAD.Application COM API（平台绘图/标注/变换/查询）
        │                   └── 不依赖类型库，始终可用
        │
        └── pyzwcadmech ──► ZwmToolKit COM API（机械功能）
                │
                ├── 类型库加载（5级回退策略）
                │   ├── 1. 文件 glob（版本感知排序）
                │   ├── 2. PYZWCADMECH_TLB_PATH 环境变量
                │   ├── 3. 本地路径
                │   ├── 4. 预生成 comtypes.gen 模块
                │   └── 5. GUID 注册表加载
                │
                ├── ZwmApp ──── 应用层（版本/路径/文档操作）── 不依赖类型库
                ├── ZwmDb ──── 数据库层（打开/保存/图框管理）
                │   ├── open_file/save/close/switch_frame ── 不依赖类型库
                │   ├── get_title() ──► ZwmTitle ── 依赖类型库
                │   ├── get_bom() ────► ZwmBom ─── 依赖类型库
                │   └── get_frame() ──► ZwmFrame ─ 依赖类型库
                │
                └── 运行时重试: zwm_app 属性在 ZWM=None 时自动调用 reload_typelib()

   连接缓存: get_cad_connection() 缓存 (ZwCAD, ZwCADMech) 实例，自动处理失效重连
   诊断工具: zwcad_diagnose / zwcad_mech_diagnose 每次调用自动重置连接缓存，逐项探测
```

## 重要说明

1. **ZWCAD 必须运行**：所有工具调用都要求 ZWCAD（或中望机械CAD）已启动并打开了 DWG 文件。

2. **单活动实例策略**：同一时间只操作一个 ZWCAD 系列实例。多个 ZWCAD/机械实例并存时，Windows COM 可能连接到非预期实例。

3. **样式文件路径**：`zwcad_mech_create_frame` 工具从 XML 配置文件读取默认样式，路径形如 `C:\Users\Public\Documents\ZWSoft\zwcadm\<版本>\<语言>\styles`（`<版本>` 与 `<语言>` 取决于本机安装的中望机械版本，例如 2026 版简体中文为 `2026\zh-CN`）

4. **类型库加载**：机械模块（标题栏/明细表/图框）依赖 ZwmToolKit 类型库。正常安装环境下会自动加载；如遇加载失败，可使用 `zwcad_mech_diagnose` 工具诊断，或设置 `PYZWCADMECH_TLB_PATH` 环境变量指向 `ZwmToolKit.tlb` 文件。

5. **连接缓存**：MCP Server 会缓存 CAD 连接实例以提高性能。`zwcad_diagnose` / `zwcad_mech_diagnose` 工具每次调用会自动重置缓存以获取最新状态。

6. **写入操作需人工确认**：删除实体、覆盖保存、关闭文档、替换插件、修改系统变量等写操作会直接改变当前 DWG，调用前请先备份图纸。

## 依赖

以下依赖由 `pip install zwcad-mcp` 或 `uvx zwcad-mcp` 自动安装，无需手动处理：

- [pyzwcad](https://pypi.org/project/pyzwcad/) - ZWCAD Python COM 封装
- [pyzwcadmech](https://pypi.org/project/pyzwcadmech/) >=0.3.0 - 中望机械 Python COM 封装
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP 协议服务框架
- [comtypes](https://github.com/enthought/comtypes) - COM 类型库加载与接口调用
- [pywin32](https://github.com/mhammond/pywin32) - Windows COM 初始化支持

第三方组件的许可声明见随包提供的 `THIRD_PARTY_NOTICES.md`。

## License

本项目采用 MIT 许可，详见 [LICENSE](LICENSE)。
