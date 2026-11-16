import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from controller import TodoController
from model import TodoList
from storage import TodoStorage


class TodoControllerTests(unittest.TestCase):
    def test_deleted_tasks_stay_deleted_after_reload(self):
        with TemporaryDirectory() as directory:
            storage = TodoStorage(Path(directory) / "tasks.json")
            controller = TodoController(TodoList(), storage)
            controller.add("Buy milk")
            controller.save()
            self.assertEqual(len(storage.load()), 1)

            controller.delete(controller.tasks[0].key)
            self.assertEqual(controller.tasks, ())
            controller.save()

            restarted = TodoController(TodoList(), storage)
            restarted.load()
            self.assertEqual(restarted.tasks, ())
