from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class TaskView:
    key: int
    text: str
    done: bool


class TodoActions(Protocol):
    @property
    def tasks(self) -> tuple[TaskView, ...]: ...

    def can_add(self, text: str) -> bool: ...

    def add(self, text: str) -> bool: ...

    def set_done(self, key: int, done: bool) -> None: ...
