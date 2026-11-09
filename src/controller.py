from model import Task, TodoList
from presentation import TaskView


class TodoController:
    def __init__(self, model: TodoList) -> None:
        self.model = model

    def _find(self, key: int) -> Task:
        for task in self.model.tasks:
            if id(task) == key:
                return task
        raise KeyError(key)

    @property
    def tasks(self) -> tuple[TaskView, ...]:
        return tuple(
            TaskView(key=id(task), text=task.text, done=task.done)
            for task in self.model.tasks
        )

    def can_add(self, text: str) -> bool:
        return self.model.is_valid_text(text)

    def add(self, text: str) -> bool:
        return self.model.add(text) is not None

    def set_done(self, key: int, done: bool) -> None:
        self.model.set_done(self._find(key), done)
