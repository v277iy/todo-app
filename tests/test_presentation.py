import unittest
from dataclasses import FrozenInstanceError

from presentation import TaskView


class TaskViewTests(unittest.TestCase):
    def test_view_fields_and_default_children(self):
        view = TaskView(1, "Read", False)

        self.assertEqual(view.key, 1)
        self.assertEqual(view.text, "Read")
        self.assertFalse(view.done)
        self.assertEqual(view.children, ())

    def test_views_are_read_only(self):
        view = TaskView(1, "Read", False)

        with self.assertRaises(FrozenInstanceError):
            view.done = True
