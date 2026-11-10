import json
from dataclasses import asdict
from pathlib import Path

from model import Task


def default_path() -> Path:
    return Path.cwd() / "tasks.json"


class TodoStorage:
    def __init__(self, path: Path | None = None) -> None:
        self.path = default_path() if path is None else path

    def load(self) -> list[Task]:
        try:
            with self.path.open(encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            return []

        def decode(items: object) -> list[Task]:
            if not isinstance(items, list):
                raise ValueError("Expected a list of tasks")
            tasks = []
            for item in items:
                if (not isinstance(item, dict)
                        or not isinstance(item.get("text"), str)
                        or not item["text"].strip()
                        or not isinstance(item.get("done"), bool)):
                    raise ValueError("Invalid task data")
                tasks.append(Task(item["text"], item["done"],
                                  decode(item.get("children", []))))
            return tasks

        return decode(data)

    def save(self, tasks: list[Task]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as file:
            json.dump([asdict(task) for task in tasks], file,
                      ensure_ascii=False, indent=2)
            file.write("\n")
