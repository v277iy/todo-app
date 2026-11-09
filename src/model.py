from dataclasses import dataclass

@dataclass
class Task:
    text: str
    done: bool = False


class TodoList:
    def __init__(self):
        self.tasks: list[Task] = []

    @staticmethod
    def is_valid_text(text: str) -> bool:
        return bool(text.strip())

    def add(self, text: str) -> Task | None:
        if not self.is_valid_text(text):
            return None
        task = Task(text.strip())
        self.tasks.append(task)
        return task

    def set_done(self, task: Task, done: bool) -> None:
        task.done = done
