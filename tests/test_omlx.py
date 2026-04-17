"""Tests for omlx.py core functionality."""

import json
import os
import tempfile
import unittest
from unittest.mock import patch

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import omlx


class TestConfig(unittest.TestCase):
    """Tests for config load/save operations."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.tmpdir, "config.json")

    def test_load_config_missing_file(self):
        """load_config returns empty dict when file does not exist."""
        with patch("omlx.CONFIG_PATH", self.config_path):
            config = omlx.load_config()
        self.assertEqual(config, {})

    def test_save_and_load_config(self):
        """Saved config can be loaded back correctly."""
        data = {"models": ["llama3", "mistral"]}
        with patch("omlx.CONFIG_PATH", self.config_path):
            omlx.save_config(data)
            loaded = omlx.load_config()
        self.assertEqual(loaded, data)

    def test_save_config_creates_file(self):
        """save_config creates the config file if it does not exist."""
        with patch("omlx.CONFIG_PATH", self.config_path):
            omlx.save_config({"key": "value"})
        self.assertTrue(os.path.exists(self.config_path))


class TestCmdAdd(unittest.TestCase):
    """Tests for cmd_add functionality."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.tmpdir, "config.json")

    def test_add_model(self):
        """cmd_add adds a model to the config."""
        with patch("omlx.CONFIG_PATH", self.config_path):
            omlx.cmd_add(["llama3"])
            config = omlx.load_config()
        self.assertIn("llama3", config.get("models", []))

    def test_add_duplicate_model(self):
        """cmd_add does not add duplicate models."""
        with patch("omlx.CONFIG_PATH", self.config_path):
            omlx.cmd_add(["llama3"])
            omlx.cmd_add(["llama3"])
            config = omlx.load_config()
        self.assertEqual(config.get("models", []).count("llama3"), 1)


class TestCmdRemove(unittest.TestCase):
    """Tests for cmd_remove functionality."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.tmpdir, "config.json")

    def test_remove_existing_model(self):
        """cmd_remove removes an existing model from the config."""
        with patch("omlx.CONFIG_PATH", self.config_path):
            omlx.cmd_add(["mistral"])
            omlx.cmd_remove(["mistral"])
            config = omlx.load_config()
        self.assertNotIn("mistral", config.get("models", []))

    def test_remove_nonexistent_model(self):
        """cmd_remove handles removal of a model that is not in the list."""
        with patch("omlx.CONFIG_PATH", self.config_path):
            # Should not raise
            try:
                omlx.cmd_remove(["nonexistent"])
            except Exception as e:
                self.fail(f"cmd_remove raised unexpectedly: {e}")


class TestCmdList(unittest.TestCase):
    """Tests for cmd_list functionality."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.tmpdir, "config.json")

    def test_list_empty(self):
        """cmd_list runs without error when no models are configured."""
        with patch("omlx.CONFIG_PATH", self.config_path):
            try:
                omlx.cmd_list([])
            except Exception as e:
                self.fail(f"cmd_list raised unexpectedly: {e}")

    def test_list_with_models(self):
        """cmd_list runs without error when models are present."""
        with patch("omlx.CONFIG_PATH", self.config_path):
            omlx.cmd_add(["gemma"])
            try:
                omlx.cmd_list([])
            except Exception as e:
                self.fail(f"cmd_list raised unexpectedly: {e}")


if __name__ == "__main__":
    unittest.main()
