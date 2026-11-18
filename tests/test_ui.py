import unittest
from unittest.mock import Mock, patch

from presentation import TaskView
from ui import TodoApp

# KI Implementiert
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

    @patch("ui.simpledialog.askstring", return_value="Bread")
    def test_edit_task(self, askstring):
        TodoApp.edit_task(self.app, TaskView(1, "Milk", False))

        askstring.assert_called_once_with(
            "Edit task", "Task text:", initialvalue="Milk", parent=self.app,
        )
        self.app.commands.rename.assert_called_once_with(1, "Bread")
        self.app.render_tasks.assert_called_once_with()

    @patch("ui.simpledialog.askstring", return_value=None)
    def test_cancel_edit(self, askstring):
        TodoApp.edit_task(self.app, TaskView(1, "Milk", False))

        self.app.commands.rename.assert_not_called()
        self.app.render_tasks.assert_not_called()

    @patch("ui.simpledialog.askstring", return_value="   ")
    def test_rejected_edit(self, askstring):
        self.app.commands.rename.return_value = False
        TodoApp.edit_task(self.app, TaskView(1, "Milk", False))

        self.app.render_tasks.assert_not_called()

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
