import json
import os
from dataclasses import asdict
from pathlib import Path
from tempfile import NamedTemporaryFile

from model import Task

# Speicherpfad manuell gewählt.
def default_path() -> Path:
    config = Path(os.environ.get("XDG_CONFIG_HOME", ""))
    if not config.is_absolute():
        config = Path.home() / ".config"
    return config / "todo-app" / "tasks.json"

# KI-Lösung übernommen nach überarbeitetem Prompt mit Spezifikation für Verhalten.
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
        # Replace only after writing succeeds, so a failed save keeps the old file.
        temporary = None
        try:
            with NamedTemporaryFile(mode="w", encoding="utf-8",
                                    dir=self.path.parent, delete=False) as file:
                temporary = Path(file.name)
                json.dump([asdict(task) for task in tasks], file,
                          ensure_ascii=False, indent=2)
                file.write("\n")
            temporary.replace(self.path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
