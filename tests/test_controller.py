import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock

from controller import TodoController
from model import Task, TodoList
from presentation import TaskView
from storage import TodoStorage


class TodoControllerTests(unittest.TestCase):
    def setUp(self):
        self.model = TodoList()
        self.storage = Mock(spec=TodoStorage)
        self.controller = TodoController(self.model, self.storage)

    def test_add_and_read_nested_task_views(self):
        self.assertTrue(self.controller.can_add("Shopping"))
        self.assertTrue(self.controller.add("Shopping"))
        parent = self.model.tasks[0]
        self.assertTrue(self.controller.add("Milk", id(parent)))
        child = parent.children[0]
        self.controller.set_done(id(parent), True)

        self.assertEqual(self.controller.tasks, (
            TaskView(id(parent), "Shopping", True, (
                TaskView(id(child), "Milk", True),
            )),
        ))

    def test_blank_tasks_are_rejected(self):
        self.assertFalse(self.controller.can_add("   "))
        self.assertFalse(self.controller.add("   "))
        self.assertEqual(self.controller.tasks, ())

    def test_complete_and_delete_child_by_key(self):
        parent = self.model.add("Shopping")
        child = self.model.add("Milk", parent)

        self.controller.set_done(id(child), True)
        self.assertTrue(child.done)
        self.assertFalse(parent.done)

        self.controller.delete(id(child))
        self.assertEqual(parent.children, [])
        self.assertEqual(self.model.tasks, [parent])

    def test_load_and_save_tasks(self):
        tasks = [Task("Read", done=True)]
        self.storage.load.return_value = tasks

        self.controller.load()
        self.assertEqual(self.model.tasks, tasks)
        self.storage.load.assert_called_once_with()

        self.controller.save()
        self.storage.save.assert_called_once_with(tasks)

    def test_saving_empty_list_removes_previous_tasks(self):
        with TemporaryDirectory() as directory:
            controller = TodoController(
                TodoList(), TodoStorage(Path(directory) / "tasks.json")
            )
            controller.add("Buy milk")
            controller.save()
            controller.load()
            self.assertEqual(len(controller.tasks), 1)

            controller.delete(controller.tasks[0].key)
            controller.save()
            controller.load()
            self.assertEqual(controller.tasks, ())
