import unittest
from unittest.mock import Mock, patch

from presentation import TaskView
from ui import TodoApp


class TodoAppTests(unittest.TestCase):
    def setUp(self):
        # Exercise callbacks without creating a Tk window.
        self.app = Mock()
        self.app.input_text.get.return_value = "Milk"

    def test_add_task_clears_input_and_refreshes(self):
        self.app.commands.add.return_value = True

        TodoApp.add_task(self.app)

        self.app.commands.add.assert_called_once_with("Milk", None)
        self.app.input_text.set.assert_called_once_with("")
        self.app.render_tasks.assert_called_once_with()
        self.app.entry.focus_set.assert_called_once_with()
        self.app.canvas.yview_moveto.assert_called_once_with(1)

    def test_rejected_task_does_not_change_ui(self):
        self.app.input_text.get.return_value = "   "
        self.app.commands.add.return_value = False

        TodoApp.add_task(self.app)

        self.app.commands.add.assert_called_once_with("   ", None)
        self.app.input_text.set.assert_not_called()
        self.app.render_tasks.assert_not_called()

    def test_task_action_adds_child_when_input_is_valid(self):
        self.app.commands.can_add.return_value = True

        TodoApp.task_action(self.app, TaskView(1, "Shopping", False))

        self.app.commands.can_add.assert_called_once_with("Milk")
        self.app.add_task.assert_called_once_with(parent=1)
        self.app.commands.delete.assert_not_called()

    def test_task_action_deletes_when_input_is_blank(self):
        self.app.input_text.get.return_value = ""
        self.app.commands.can_add.return_value = False

        TodoApp.task_action(self.app, TaskView(1, "Shopping", False))

        self.app.commands.delete.assert_called_once_with(1)
        self.app.render_tasks.assert_called_once_with()
        self.app.add_task.assert_not_called()

    def test_save_delegates_to_controller(self):
        TodoApp.save(self.app)

        self.app.commands.save.assert_called_once_with()

    @patch("ui.messagebox.showerror")
    def test_save_failure_shows_error(self, showerror):
        self.app.commands.save.side_effect = OSError("Disk full")

        TodoApp.save(self.app)

        showerror.assert_called_once_with(
            "Could not save tasks", "Disk full", parent=self.app,
        )
