import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "src" / "zwcad2d" / "server.py"


class Zwcad2DServerStaticTests(unittest.TestCase):
    def test_server_is_valid_python(self):
        source = SERVER.read_text(encoding="utf-8-sig")
        ast.parse(source)

    def test_expected_local_tools_are_registered(self):
        source = SERVER.read_text(encoding="utf-8-sig")
        tree = ast.parse(source)
        tools = set()
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                if (
                    isinstance(decorator, ast.Attribute)
                    and isinstance(decorator.value, ast.Name)
                    and decorator.value.id == "mcp"
                    and decorator.attr == "tool"
                ):
                    tools.add(node.name)

        expected = {
            "zwcad_draw_entity", "zwcad_draw_batch", "zwcad_draw_3d_solid",
            "zwcad_add_annotation", "zwcad_add_dimension", "zwcad_query_dimensions",
            "zwcad_insert_block", "zwcad_transform_entity", "zwcad_modify_entity",
            "zwcad_get_entity_info", "zwcad_set_entity_properties", "zwcad_find_object",
            "zwcad_get_objects_in_model", "zwcad_zoom", "zwcad_manage_style",
            "zwcad_manage_view", "zwcad_manage_document", "zwcad_manage_table",
            "zwcad_select_entities", "zwcad_manage_block", "zwcad_get_variable",
            "zwcad_set_variable", "zwcad_get_app_info", "zwcad_manage_dictionary",
            "zwcad_manage_xdata", "zwcad_manage_utility", "zwcad_mech_diagnose",
            "zwcad_mech_manage_title_block", "zwcad_mech_manage_frame",
            "zwcad_mech_manage_bom", "zwcad_mech_create_partlist",
            "zwcad_mech_manage_db", "zwcad_mech_doc",
            "zwcad_mech_cad_environment_init", "zwcad_mech_get_balloon",
            "zwcad_mech_insert_balloon", "zwcad_mech_create_frame",
            "zwcad_get_capabilities", "zwcad_diagnose",
        }
        self.assertEqual(expected, tools)
        self.assertEqual(39, len(tools))

    def test_external_binaries_are_not_bundled(self):
        forbidden = {".exe", ".zrx", ".dll"}
        bundled = [
            path for path in ROOT.rglob("*")
            if ".venv" not in path.parts and path.suffix.lower() in forbidden
        ]
        self.assertEqual([], bundled)


if __name__ == "__main__":
    unittest.main()
