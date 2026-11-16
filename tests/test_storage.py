import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from model import Task
from storage import TodoStorage, default_path


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(os.chdir, Path.cwd())
        self.root = Path(self.temp.name)
        os.chdir(self.root)
        env = patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.root)})
        env.start()
        self.addCleanup(env.stop)

    def test_tasks_survive_directory_change(self):
        tasks = [Task("Buy milk")]
        TodoStorage().save(tasks)
        Path("other").mkdir()
        os.chdir("other")
        self.assertEqual(TodoStorage().load(), tasks)

    def test_failed_save_keeps_old_data(self):
        storage = TodoStorage(self.root / "tasks.json")
        tasks = [Task("Buy milk")]
        storage.save(tasks)
        original = storage.path.read_bytes()

        with patch("storage.json.dump", side_effect=OSError("Disk full")):
            with self.assertRaises(OSError):
                storage.save([Task("Buy bread")])

        self.assertEqual(storage.path.read_bytes(), original)
