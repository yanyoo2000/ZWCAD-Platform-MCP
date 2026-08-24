# ZWCAD Platform MCP

通过 MCP 协议控制 ZWCAD 的 Windows 本地服务，可供 WorkBuddy 及其他支持
MCP stdio 的客户端调用。项目提供 26 个 ZWCAD 自动化工具。

## 功能

| 类别 | 工具 |
| --- | --- |
| 2D/3D 绘图 | `draw_entity`, `draw_batch`, `draw_3d_solid` |
| 注释与标注 | `add_annotation`, `add_dimension`, `insert_block` |
| 查询与编辑 | `query_dimensions`, `transform_entity`, `modify_entity`, `get_entity_info`, `set_entity_properties`, `find_object`, `get_objects_in_model` |
| 样式、视图、文档 | `zoom`, `manage_style`, `manage_view`, `manage_document` |
| 表格、选择集、图块 | `manage_table`, `select_entities`, `manage_block` |
| 系统与应用 | `get_variable`, `set_variable`, `get_app_info` |
| 扩展数据与工具 | `manage_dictionary`, `manage_xdata`, `manage_utility` |

## 环境要求

- Windows 10/11
- ZWCAD，启动后至少打开一张 DWG
- Python 3.9 或更高版本
- Python 与 ZWCAD 的位数建议保持一致

安装 Python 时请勾选 `Add Python to PATH`。也可以从命令行执行 `py -3 --version`
确认安装成功。

## 安装

1. 解压项目到固定目录，例如 `D:\Tools\ZWCAD-Platform-MCP`。
2. 双击 `install.bat`。
3. 等待脚本创建 `.venv` 并安装依赖。

## 独立启动测试

1. 启动 ZWCAD 并打开一张测试 DWG。
2. 双击 `start.bat`。
3. 命令窗口保持运行并等待客户端连接属于正常现象；MCP stdio 服务本身没有网页界面。

## 配置 WorkBuddy

打开 `workbuddy-mcp.json`，将其中两处 `D:\\YOUR_PATH` 替换为项目实际所在目录。
例如项目位于 `D:\Tools\ZWCAD-Platform-MCP` 时：

```json
{
  "mcpServers": {
    "zwcad-platform": {
      "command": "D:\\Tools\\ZWCAD-Platform-MCP\\.venv\\Scripts\\python.exe",
      "args": ["D:\\Tools\\ZWCAD-Platform-MCP\\server.py"],
      "env": {"PYTHONUTF8": "1"}
    }
  }
}
```

把 `mcpServers` 配置合并到 WorkBuddy 的 MCP 配置中，保存并重启 WorkBuddy。

## 首次验证

建议在测试 DWG 中依次调用：

1. `get_app_info`
2. `get_objects_in_model(limit=10)`
3. `draw_entity(entity_type="line", params={"x1":0,"y1":0,"x2":100,"y2":0})`
4. `zoom(mode="extents")`

如果第一步连接失败，请确认：

- ZWCAD 已经启动并打开 DWG；
- WorkBuddy 使用的是 `.venv\Scripts\python.exe`；
- WorkBuddy 已在修改配置后完全重启；
- 防病毒软件没有拦截 Python 访问本地 COM 服务。

如果旧版本曾出现 `mbcs codec can't decode bytes`，请使用本项目最新版的
`server.py` 并完全重启 WorkBuddy。服务已让 comtypes 在内存中生成 ZWCAD 接口包装，
避免系统 ANSI 代码页读取生成文件时失败。

## 使用安全

部分工具会直接修改当前图纸。执行删除、关闭文档、覆盖保存或修改系统变量前，
建议先保存备份，并在 WorkBuddy 中要求操作前进行人工确认。

## License

MIT License，详见 `LICENSE`。
