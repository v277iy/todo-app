from dataclasses import dataclass, field

# KI-Entwurf für Klasse übernommen. Aufgaben werden als Dataclass modelliert.
# Struktur passt zu meinen Anforderungen.
@dataclass
class Task:
    text: str
    done: bool = False
    children: list["Task"] = field(default_factory=list)


class TodoList:
    def __init__(self):
        self.tasks: list[Task] = []

    @staticmethod
    def is_valid_text(text: str) -> bool:
        # Selbst Implementiert. Die Eingabe von Text muss mit `strip()`
        # bereinigt werden. Reine Space Eingaben sind invalide.
        return bool(text.strip())

    def add(self, text: str, parent: Task | None = None) -> Task | None:
        if not self.is_valid_text(text):
            return None
        task = Task(text.strip())
        target = self.tasks if parent is None else parent.children
        target.append(task)
        return task

    def rename(self, task: Task, text: str) -> bool:
        if not self.is_valid_text(text):
            return False
        task.text = text.strip()
        return True

    def set_done(self, task: Task, done: bool) -> None:
        task.done = done

    def is_done(self, task: Task) -> bool:
        """Completion includes ancestors without changing a task's own state."""
        # KI-Entwurf angepasst. Unteraufgaben sind fertig wenn Oberaufgabe fertig ist.
        # Unteraufgabe behalten ihren vorherigen Status bei Änderung der Oberaufgabe.
        def find(tasks: list[Task], inherited: bool) -> bool | None:
            for existing in tasks:
                done = inherited or existing.done
                if existing is task:
                    return done
                result = find(existing.children, done)
                if result is not None:
                    return result
            return None

        result = find(self.tasks, False)
        return task.done if result is None else result

    def delete(self, task: Task) -> None:
        def remove(tasks: list[Task]) -> bool:
            for index, existing in enumerate(tasks):
                if existing is task:
                    del tasks[index]
                    return True
                if remove(existing.children):
                    return True
            return False

        remove(self.tasks)
