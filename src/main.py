import tkinter as tk

from controller import TodoController
from model import TodoList
from ui import TodoApp


def main():
    root = tk.Tk()
    root.title("Todo-App")
    root.minsize(240, 180)
    TodoApp(root, TodoController(TodoList()))
    root.mainloop()


if __name__ == "__main__":
    main()
