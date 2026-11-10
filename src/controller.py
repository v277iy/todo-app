from model import Task, TodoList
from presentation import TaskView


class TodoController:
    def __init__(self, model: TodoList) -> None:
        self.model = model

    def _find(self, key: int) -> Task:
        def walk(tasks: list[Task]):
            for task in tasks:
                yield task
                yield from walk(task.children)

        for task in walk(self.model.tasks):
            if id(task) == key:
                return task
        raise KeyError(key)

    @property
    def tasks(self) -> tuple[TaskView, ...]:
        def snapshot(task: Task) -> TaskView:
            return TaskView(
                key=id(task),
                text=task.text,
                done=task.done,
                children=tuple(snapshot(child) for child in task.children),
            )

        return tuple(snapshot(task) for task in self.model.tasks)

    def can_add(self, text: str) -> bool:
        return self.model.is_valid_text(text)

    def add(self, text: str, parent: int | None = None) -> bool:
        task = None if parent is None else self._find(parent)
        return self.model.add(text, task) is not None

    def delete(self, key: int) -> None:
        self.model.delete(self._find(key))

    def set_done(self, key: int, done: bool) -> None:
        self.model.set_done(self._find(key), done)
