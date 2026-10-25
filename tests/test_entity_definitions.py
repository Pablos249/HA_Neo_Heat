"""Static checks for entity mappings without importing Home Assistant."""
import ast
from pathlib import Path
import unittest


BASE = Path(__file__).resolve().parents[1] / "custom_components" / "neoheat"


def literal_assignment(path, name):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError(f"Missing {name} in {path}")


class EntityDefinitionTests(unittest.TestCase):
    def test_sensor_offsets_are_unique_per_frame_type(self):
        fields = literal_assignment(BASE / "sensor.py", "FIELDS")
        keys = [(kind, offset) for kind, offset, *_ in fields]
        self.assertEqual(len(keys), len(set(keys)))

    def test_requested_runtime_entities_are_present(self):
        fields = literal_assignment(BASE / "sensor.py", "FIELDS")
        keys = {(kind, offset) for kind, offset, *_ in fields}
        self.assertTrue({(1, 99), (1, 183), (1, 187), (1, 191)} <= keys)

    def test_three_pump_binary_sensors_are_mapped(self):
        pumps = literal_assignment(BASE / "binary_sensor.py", "PUMPS")
        self.assertEqual([offset for offset, _ in pumps], [151, 155, 159])

    def test_operating_mode_codes(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("neoheat_const_test", BASE / "const.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.decode_operating_mode(0), "Stop")
        self.assertEqual(module.decode_operating_mode(5), "DHW")
        self.assertEqual(module.decode_operating_mode(10), "Central heating")
        self.assertIsNone(module.decode_operating_mode(2))


if __name__ == "__main__":
    unittest.main()
