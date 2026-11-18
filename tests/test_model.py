import unittest

from model import Task, TodoList

# Selbst Implementiert
class TodoListTests(unittest.TestCase):
    def setUp(self):
        self.todos = TodoList()

    def test_add_trims_text_and_supports_children(self):
        parent = self.todos.add("  Shopping  ")
        child = self.todos.add("  Milk  ", parent)

        self.assertEqual(parent.text, "Shopping")
        self.assertEqual(child.text, "Milk")
        self.assertFalse(child.done)
        self.assertEqual(self.todos.tasks, [parent])
        self.assertEqual(parent.children, [child])

    def test_blank_text_is_rejected(self):
        for text in ("", " \t\n "):
            self.assertFalse(self.todos.is_valid_text(text))
            self.assertIsNone(self.todos.add(text))
        self.assertEqual(self.todos.tasks, [])

    def test_parent_completion_does_not_change_child_state(self):
        parent = self.todos.add("Shopping")
        child = self.todos.add("Milk", parent)

        self.todos.set_done(parent, True)
        self.assertTrue(self.todos.is_done(child))
        self.assertFalse(child.done)

        self.todos.set_done(parent, False)
        self.assertFalse(self.todos.is_done(child))

        self.todos.set_done(child, True)
        self.assertTrue(self.todos.is_done(child))
        self.assertFalse(self.todos.is_done(parent))

    def test_delete_child_then_parent_keeps_other_tasks(self):
        parent = self.todos.add("Shopping")
        child = self.todos.add("Milk", parent)
        other = self.todos.add("Read")

        self.todos.delete(child)
        self.assertEqual(parent.children, [])
        self.assertEqual(self.todos.tasks, [parent, other])

        self.todos.delete(parent)
        self.assertEqual(self.todos.tasks, [other])

    def test_tasks_do_not_share_children(self):
        first = Task("Shopping")
        second = Task("Read")
        first.children.append(Task("Milk"))

        self.assertEqual(second.children, [])
