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

    def test_save_config_valid_json(self):
        """save_config writes valid JSON that can be parsed independently."""
        with patch("omlx.CONFIG_PATH", self.config_path):
            omlx.save_config({"models": ["llama3"]})
        with open(self.config_path, "r") as f:
            data = json.load(f)
        self.assertEqual(data, {"models": ["llama3"]})


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

    def test_add_multiple_models(self):
        """cmd_add can add several different models in sequence."""
        with patch("omlx.CONFIG_PATH", self.config_path):
            omlx.cmd_add(["llama3"])
            omlx.cmd_add(["mistral"])
            omlx.cmd_add(["gemma"])
            config = omlx.load_config()
        models = config.get("models", [])
        self.assertIn("llama3", models)
        self.assertIn("mistral", models)
        self.assertIn("gemma", models)


class TestCmdRemove(unittest.TestCase):
    """Tests for cmd_remove functionality."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.tmpdir, "config.json")

    def test_remove_existing_model(self):
        """cmd_remove removes an existing model from the config."""
        with patch("omlx.CONFIG_PATH", self.config_path):
