"""
Verification and Test Suite for Hermes Agent Plugins
Tests import, registration, tool execution, and manifest integrity.
"""

import importlib.util
import json
import os
import sys
import unittest
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HERMES_PLUGINS_DIR = os.path.join(REPO_ROOT, "plugins")

class MockHermesContext:
    def __init__(self):
        self.registered_tools = {}

    def register_tool(self, *args, **kwargs):
        if "name" in kwargs:
            name = kwargs["name"]
            self.registered_tools[name] = kwargs
        elif len(args) >= 2:
            name = args[0]
            self.registered_tools[name] = {"func": args[1]}
        elif len(args) == 1 and isinstance(args[0], str):
            self.registered_tools[args[0]] = {"registered": True}

class TestHermesPlugins(unittest.TestCase):
    def test_cli_bridge_manifests(self):
        p_yaml = os.path.join(HERMES_PLUGINS_DIR, "cli-bridge", "plugin.yaml")
        p_json = os.path.join(HERMES_PLUGINS_DIR, "cli-bridge", "plugin.json")
        self.assertTrue(os.path.exists(p_yaml))
        self.assertTrue(os.path.exists(p_json))
        with open(p_yaml, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            self.assertEqual(data["name"], "cli-bridge")
            self.assertEqual(len(data["provides_tools"]), 7)

    def test_delegation_bridge_manifests(self):
        p_yaml = os.path.join(HERMES_PLUGINS_DIR, "delegation-bridge", "plugin.yaml")
        p_json = os.path.join(HERMES_PLUGINS_DIR, "delegation-bridge", "plugin.json")
        self.assertTrue(os.path.exists(p_yaml))
        self.assertTrue(os.path.exists(p_json))
        with open(p_yaml, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            self.assertEqual(data["name"], "delegation-bridge")
            self.assertEqual(len(data["provides_tools"]), 5)

    def test_subscription_bridge_manifests(self):
        p_yaml = os.path.join(HERMES_PLUGINS_DIR, "subscription-bridge", "plugin.yaml")
        p_json = os.path.join(HERMES_PLUGINS_DIR, "subscription-bridge", "plugin.json")
        self.assertTrue(os.path.exists(p_yaml))
        self.assertTrue(os.path.exists(p_json))
        with open(p_yaml, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            self.assertEqual(data["name"], "subscription-bridge")
            self.assertEqual(len(data["provides_tools"]), 3)

    def test_cli_bridge_registration(self):
        cb_path = os.path.join(HERMES_PLUGINS_DIR, "cli-bridge")
        if "tools" in sys.modules:
            del sys.modules["tools"]
        spec = importlib.util.spec_from_file_location("cb_tools", os.path.join(cb_path, "tools.py"))
        cb_tools = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cb_tools)
        status = cb_tools.list_available_clients()
        self.assertIn("cursor", status)
        self.assertIn("codex", status)
        self.assertIn("antigravity", status)

        spec_init = importlib.util.spec_from_file_location("cb_init", os.path.join(cb_path, "__init__.py"))
        cb_init = importlib.util.module_from_spec(spec_init)
        spec_init.loader.exec_module(cb_init)
        ctx = MockHermesContext()
        cb_init.register(ctx)
        self.assertEqual(len(ctx.registered_tools), 7)
        self.assertIn("run_kimi", ctx.registered_tools)

    def test_delegation_bridge_registration(self):
        del_path = os.path.join(HERMES_PLUGINS_DIR, "delegation-bridge")
        if "tools" in sys.modules:
            del sys.modules["tools"]
        spec = importlib.util.spec_from_file_location("del_init", os.path.join(del_path, "__init__.py"))
        del_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(del_mod)

        ctx = MockHermesContext()
        del_mod.register(ctx)
        self.assertEqual(len(ctx.registered_tools), 5)
        self.assertIn("delegate_task", ctx.registered_tools)
        self.assertIn("review_task", ctx.registered_tools)
        self.assertIn("land_task", ctx.registered_tools)

        # Test implementers listing
        if "tools" in sys.modules:
            del sys.modules["tools"]
        spec_tools = importlib.util.spec_from_file_location("del_tools", os.path.join(del_path, "tools.py"))
        del_tools = importlib.util.module_from_spec(spec_tools)
        spec_tools.loader.exec_module(del_tools)
        imps = del_tools.list_supported_implementers()
        self.assertIn("antigravity", imps)
        self.assertIn("codex", imps)

    def test_subscription_bridge_registration(self):
        sub_path = os.path.join(HERMES_PLUGINS_DIR, "subscription-bridge")
        if "tools" in sys.modules:
            del sys.modules["tools"]
        spec = importlib.util.spec_from_file_location("sub_init", os.path.join(sub_path, "__init__.py"))
        sub_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sub_mod)

        ctx = MockHermesContext()
        sub_mod.register(ctx)
        self.assertEqual(len(ctx.registered_tools), 3)
        self.assertIn("get_subscription_gateway_status", ctx.registered_tools)
        self.assertIn("list_subscription_models", ctx.registered_tools)

if __name__ == "__main__":
    unittest.main()
