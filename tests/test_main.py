import unittest
from unittest.mock import patch

from main import main

# Selbst Implementiert
class MainTests(unittest.TestCase):
    @patch("main.TodoApp")
    @patch("main.TodoController")
    @patch("main.tk.Tk")
    def test_startup_loads_tasks_and_runs_ui(self, tk, controller, app):
        main()

        controller.return_value.load.assert_called_once_with()
        app.assert_called_once_with(tk.return_value, controller.return_value)
        tk.return_value.mainloop.assert_called_once_with()

    @patch("main.messagebox.showerror")
    @patch("main.TodoApp")
    @patch("main.TodoController")
    @patch("main.tk.Tk")
    def test_load_failure_shows_error_and_still_runs_ui(
        self, tk, controller, app, showerror,
    ):
        controller.return_value.load.side_effect = ValueError("Invalid task data")

        main()

        showerror.assert_called_once_with(
            "Could not load tasks", "Invalid task data", parent=tk.return_value,
        )
        app.assert_called_once_with(tk.return_value, controller.return_value)
        tk.return_value.mainloop.assert_called_once_with()
