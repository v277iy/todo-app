import tkinter as tk
from tkinter import messagebox

from controller import TodoController
from model import TodoList
from ui import TodoApp


def main():
    root = tk.Tk()
    root.title("Todo-App")
    root.minsize(240, 180)
    controller = TodoController(TodoList())
    try:
        controller.load()
    except (OSError, ValueError) as error:
        messagebox.showerror("Could not load tasks", str(error), parent=root)
    TodoApp(root, controller)
    root.mainloop()


if __name__ == "__main__":
    main()
