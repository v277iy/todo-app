import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from model import Task
from storage import TodoStorage, default_path

# Selbst Implementiert nach überarbeiteter Spezifikation der Implementation
class TodoStorageTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "todo-app" / "tasks.json"
        self.storage = TodoStorage(self.path)

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(self.storage.load(), [])

    def test_save_and_load_nested_tasks(self):
        tasks = [Task("Einkäufe", children=[Task("Milk", done=True)])]
        self.storage.save(tasks)

        self.assertEqual(self.storage.load(), tasks)

        self.storage.save([Task("Read")])
        self.assertEqual(self.storage.load(), [Task("Read")])

    def test_invalid_data_is_rejected(self):
        self.path.parent.mkdir()
        for data in ('not json', '{}', '[{"text": "", "done": false}]'):
            with self.subTest(data=data):
                self.path.write_text(data, encoding="utf-8")
                with self.assertRaises(ValueError):
                    self.storage.load()

    def test_truncated_save_is_rejected_without_changing_file(self):
        self.storage.save([Task("Buy milk")])
        damaged = self.path.read_bytes()[:-2]
        self.path.write_bytes(damaged)

        with self.assertRaises(ValueError):
            self.storage.load()

        self.assertEqual(self.path.read_bytes(), damaged)

    def test_default_path_uses_xdg_config_home(self):
        config = self.path.parent
        with patch.dict("os.environ", {"XDG_CONFIG_HOME": str(config)}):
            self.assertEqual(default_path(), config / "todo-app" / "tasks.json")

    def test_default_path_falls_back_to_home(self):
        home = self.path.parent.parent
        for xdg in ({}, {"XDG_CONFIG_HOME": ""}):
            with self.subTest(xdg=xdg):
                with patch.dict(os.environ, {"HOME": str(home), **xdg}, clear=True):
                    self.assertEqual(default_path(), home / ".config" / "todo-app" / "tasks.json")

    def test_tasks_survive_directory_change(self):
        self.addCleanup(os.chdir, Path.cwd())
        root = self.path.parent.parent
        other = root / "other"
        other.mkdir()
        tasks = [Task("Buy milk")]

        with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(root / "config")}):
            os.chdir(root)
            TodoStorage().save(tasks)
            os.chdir(other)
            self.assertEqual(TodoStorage().load(), tasks)

    def test_failed_save_keeps_old_data(self):
        self.storage.save([Task("Buy milk")])
        original = self.path.read_bytes()

        for target in ("storage.json.dump", "storage.Path.replace"):
            with self.subTest(target=target):
                with patch(target, side_effect=OSError("Save failed")):
                    with self.assertRaises(OSError):
                        self.storage.save([Task("Buy bread")])

                self.assertEqual(self.path.read_bytes(), original)
                self.assertEqual(list(self.path.parent.iterdir()), [self.path])

