import tkinter as tk
from tkinter import font, messagebox, simpledialog, ttk

from presentation import TaskView, TodoActions


BG = "#f5f4ef"
CARD = "#ffffff"
INK = "#263b34"
MUTED = "#75827b"
ACCENT = "#32765b"
BORDER = "#dedfd7"

# Layout und UI von KI implementiert anhand KI-generiertem UI-Entwurf.
# Leichte Anpassungen an meine Wünsche. Texteingabe oben. Unteraufgabe hinzufügen
# nur wenn Text in Texteingabe steht.
class TodoApp(tk.Frame):
    def __init__(self, root: tk.Tk, commands: TodoActions) -> None:
        super().__init__(root, bg=BG, padx=36, pady=32)
        self.commands = commands
        self.pack(fill="both", expand=True)
        root.configure(bg=BG)
        root.geometry("600x700")
        root.minsize(440, 400)
        family = font.nametofont("TkDefaultFont").actual("family")
        self.body_font = font.Font(family=family, size=14)
        self.done_font = font.Font(family=family, size=14, overstrike=True)
        self.small_font = font.Font(family=family, size=11)
        self.labels = []
        self.actions = []
        self.input_text = tk.StringVar(master=self)
        self.input_text.trace_add("write", self.update_actions)

        # KI-Vorschlag mit Mülltonnen-Schriftzeichen geändert wegen Fehlender
        # Unterstützung meines Fonts. Von KI gemalt.
        self.trash_icon = tk.PhotoImage(master=self, width=24, height=24)
        for rectangle in (
            (9, 3, 15, 5),   # handle
            (4, 6, 20, 8),   # lid
            (6, 9, 8, 21),   # sides and base
            (16, 9, 18, 21),
            (6, 20, 18, 22),
            (10, 10, 11, 18),
            (13, 10, 14, 18),
        ):
            self.trash_icon.put(MUTED, to=rectangle)

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("Task.TCheckbutton", background=CARD, padding=3,
                        indicatorsize=22)
        style.map("Task.TCheckbutton", background=[("active", CARD)])
        style.configure("Todo.Vertical.TScrollbar", background=BORDER,
                        troughcolor=BG, borderwidth=0, arrowsize=18)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        tk.Label(self, text="Todo-App", bg=BG, fg=INK,
                 font=(family, 32, "bold")).grid(row=0, column=0, sticky="w")

        tk.Button(self, text="Save", command=self.save,
                  font=self.small_font, bg=CARD, fg=INK,
                  relief="flat", padx=16, pady=6, cursor="hand2").grid(
                      row=1, column=0, sticky="e", pady=(8, 16))
        composer = tk.Frame(self, bg=BG)
        composer.grid(row=2, column=0, sticky="ew", pady=(0, 28))
        composer.columnconfigure(0, weight=1)
        entry_border = tk.Frame(composer, bg=CARD, highlightthickness=1,
                                highlightbackground=BORDER)
        entry_border.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.entry = tk.Entry(entry_border, textvariable=self.input_text, font=self.body_font, bg=CARD, fg=INK,
                              insertbackground=ACCENT, relief="flat", bd=0,
                              highlightthickness=0, selectbackground="#dcece3")
        self.entry.pack(fill="both", expand=True, padx=16, pady=16)
        self.entry.bind("<Return>", self.add_task)
        self.entry.bind("<FocusIn>", lambda e: entry_border.configure(
            highlightbackground=ACCENT))
        self.entry.bind("<FocusOut>", lambda e: entry_border.configure(
            highlightbackground=BORDER))
        add = tk.Button(composer, text="Add", command=self.add_task,
                        font=(family, 12, "bold"), bg=ACCENT, fg=CARD,
                        activebackground="#265d47", activeforeground=CARD,
                        relief="flat", bd=0, width=6, cursor="hand2",
                        highlightthickness=1, highlightbackground=ACCENT,
                        highlightcolor=INK)
        add.grid(row=0, column=1, sticky="ns")

        list_area = tk.Frame(self, bg=BG)
        list_area.grid(row=3, column=0, sticky="nsew")
        list_area.columnconfigure(0, weight=1)
        list_area.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(list_area, bg=BG, highlightthickness=0,
                                width=1, height=1, yscrollincrement=24)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar = ttk.Scrollbar(list_area, command=self.canvas.yview,
                                       style="Todo.Vertical.TScrollbar")
        self.scrollbar.grid(row=0, column=1, sticky="ns", padx=(8, 0))
        self.scrollbar.grid_remove()
        self.canvas.configure(yscrollcommand=self.update_scrollbar)
        self.rows = tk.Frame(self.canvas, bg=BG)
        self.window = self.canvas.create_window((0, 0), window=self.rows, anchor="nw")
        self.rows.bind("<Configure>", self.update_scroll_region)
        self.canvas.bind("<Configure>", self.resize_rows)
        self.empty = tk.Label(list_area, text="A clear slate.\nAdd your first task above.",
                              font=self.body_font, bg=BG, fg=MUTED, justify="center")
        self.empty.place(relx=0.5, rely=0.35, anchor="center")

        root.bind("<MouseWheel>", self.scroll)
        root.bind("<Button-4>", self.scroll)
        root.bind("<Button-5>", self.scroll)
        self.entry.focus_set()
        self.render_tasks()

    def save(self) -> None:
        try:
            self.commands.save()
        except (OSError, ValueError) as error:
            messagebox.showerror("Could not save tasks", str(error), parent=self)

    def update_scrollbar(self, first: str, last: str) -> None:
        self.scrollbar.set(first, last)
        if float(first) <= 0 and float(last) >= 1:
            self.scrollbar.grid_remove()
        else:
            self.scrollbar.grid()

    def update_scroll_region(self, event: tk.Event | None = None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def resize_rows(self, event: tk.Event) -> None:
        self.canvas.itemconfigure(self.window, width=event.width)
        for label, depth in self.labels:
            label.configure(wraplength=max(40, event.width - 150 - depth * 24))

    def update_actions(self, *_args) -> None:
        adding = self.commands.can_add(self.input_text.get())
        for button in self.actions:
            button.configure(
                text="Add" if adding else "",
                image="" if adding else self.trash_icon,
                bg=ACCENT if adding else CARD,
                fg=CARD if adding else MUTED,
                activebackground="#265d47" if adding else CARD,
                activeforeground=CARD if adding else INK,
                highlightbackground=ACCENT if adding else CARD,
                width=6 if adding else 0,
            )

    def add_task(self, event: tk.Event | None = None,
                 parent: int | None = None) -> None:
        if not self.commands.add(self.input_text.get(), parent):
            return
        self.input_text.set("")
        self.render_tasks()
        self.entry.focus_set()
        if parent is None:
            self.rows.update_idletasks()
            self.canvas.yview_moveto(1)

    def task_action(self, task: TaskView) -> None:
        if self.commands.can_add(self.input_text.get()):
            self.add_task(parent=task.key)
        else:
            self.commands.delete(task.key)
            self.render_tasks()
            self.entry.focus_set()

    def edit_task(self, task: TaskView) -> None:
        text = simpledialog.askstring(
            "Edit task", "Task text:", initialvalue=task.text, parent=self,
        )
        if text is not None and self.commands.rename(task.key, text):
            self.render_tasks()

    def render_tasks(self) -> None:
        self.labels.clear()
        self.actions.clear()
        for widget in self.rows.winfo_children():
            widget.destroy()
        tasks = self.commands.tasks
        if tasks:
            self.empty.place_forget()
        else:
            self.empty.place(relx=0.5, rely=0.35, anchor="center")
        for task in tasks:
            card = tk.Frame(self.rows, bg=CARD, padx=16, pady=16,
                            highlightthickness=1, highlightbackground=BORDER)
            card.pack(fill="x", pady=(0, 12))
            self.render_task(card, task)
        self.update_actions()

    def render_task(self, card: tk.Frame, task: TaskView, depth: int = 0) -> None:
        row = tk.Frame(card, bg=CARD)
        row.pack(fill="x", padx=(depth * 24, 0), pady=(8 if depth else 0, 0))
        done = task.done
        checked = tk.BooleanVar(master=self, value=done)
        label = tk.Label(row, text=task.text, bg=CARD,
                         fg=MUTED if done else INK,
                         font=self.done_font if done else self.body_font,
                         justify="left", anchor="w",
                         wraplength=max(40, self.canvas.winfo_width() - 150 - depth * 24))

        def set_done() -> None:
            self.commands.set_done(task.key, checked.get())
            self.render_tasks()

        button = tk.Button(row, command=lambda: self.task_action(task),
                           font=(self.body_font.actual("family"), 12, "bold"),
                           relief="flat", bd=0, cursor="hand2",
                           highlightthickness=1, highlightcolor=ACCENT, padx=6)
        button.pack(side="right", anchor="n", padx=(10, 0))
        self.actions.append(button)
        ttk.Checkbutton(row, variable=checked, command=set_done,
                        style="Task.TCheckbutton", cursor="hand2").pack(
                            side="left", anchor="n", padx=(0, 10), pady=2)
        label.bind("<Double-Button-1>", lambda event: self.edit_task(task))
        label.pack(side="left", fill="x", expand=True)
        self.labels.append((label, depth))
        for child in task.children:
            self.render_task(card, child, depth + 1)

    def scroll(self, event: tk.Event) -> None:
        if self.rows.winfo_height() <= self.canvas.winfo_height():
            return
        if event.num == 4:
            steps = -1
        elif event.num == 5:
            steps = 1
        elif event.delta:
            steps = -1 if event.delta > 0 else 1
        else:
            return
        self.canvas.yview_scroll(steps, "units")
