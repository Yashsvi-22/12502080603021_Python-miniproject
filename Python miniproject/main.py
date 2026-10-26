
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from database import get_connection


class StudyFlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StudyFlow - Smart Study Planner")
        self.root.geometry("1150x700")
        self.root.minsize(900, 550)

        self.setup_style()
        self.create_interface()
        self.load_dashboard()

    # ---------------- STYLE ----------------

    def setup_style(self):
        style = ttk.Style()

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 22, "bold")
        )
        style.configure(
            "Subtitle.TLabel",
            font=("Segoe UI", 11)
        )
        style.configure(
            "Treeview",
            rowheight=30,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold")
        )

    # ---------------- MAIN INTERFACE ----------------

    def create_interface(self):
        header = ttk.Frame(self.root, padding=20)
        header.pack(fill="x")

        ttk.Label(
            header,
            text="StudyFlow",
            style="Title.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="Your personal smart study planner",
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(4, 0))

        stats = ttk.Frame(header)
        stats.pack(fill="x", pady=(12, 0))

        self.subject_count = ttk.Label(
            stats,
            text="Subjects: 0",
            font=("Segoe UI", 11, "bold")
        )
        self.subject_count.pack(side="left", padx=(0, 25))

        self.pending_count = ttk.Label(
            stats,
            text="Pending Tasks: 0",
            font=("Segoe UI", 11, "bold")
        )
        self.pending_count.pack(side="left", padx=(0, 25))

        self.completed_count = ttk.Label(
            stats,
            text="Completed Tasks: 0",
            font=("Segoe UI", 11, "bold")
        )
        self.completed_count.pack(side="left")

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        self.subject_tab = ttk.Frame(self.tabs, padding=15)
        self.task_tab = ttk.Frame(self.tabs, padding=15)
        self.progress_tab = ttk.Frame(self.tabs, padding=15)

        self.tabs.add(self.subject_tab, text="Dashboard")
        self.tabs.add(self.task_tab, text="Tasks")
        self.tabs.add(self.progress_tab, text="Study Progress")

        self.create_subject_table()
        self.create_task_tab()
        self.create_progress_tab()

    def create_progress_tab(self):
        """Create the study progress chart area."""
        ttk.Label(
            self.progress_tab,
            text="Your Study Progress",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", pady=(0, 10))

        self.progress_figure = Figure(
            figsize=(7, 4),
            dpi=100
        )

        self.progress_axes = self.progress_figure.add_subplot(111)

        self.progress_canvas = FigureCanvasTkAgg(
            self.progress_figure,
            master=self.progress_tab
        )

        self.progress_canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

    # ---------------- DASHBOARD ----------------

    def create_subject_table(self):
        ttk.Label(
            self.subject_tab,
            text="Your Subjects",
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", pady=(0, 12))

        columns = ("id", "subject", "course", "semester")

        self.subject_table = ttk.Treeview(
            self.subject_tab,
            columns=columns,
            show="headings"
        )

        headings = {
            "id": "ID",
            "subject": "Subject Name",
            "course": "Course",
            "semester": "Semester"
        }

        for column, heading in headings.items():
            self.subject_table.heading(column, text=heading)

        self.subject_table.column(
            "id", width=60, anchor="center"
        )
        self.subject_table.column("subject", width=350)
        self.subject_table.column("course", width=220)
        self.subject_table.column(
            "semester", width=100, anchor="center"
        )

        scrollbar = ttk.Scrollbar(
            self.subject_tab,
            orient="vertical",
            command=self.subject_table.yview
        )
        self.subject_table.configure(
            yscrollcommand=scrollbar.set
        )

        self.subject_table.pack(
            side="left", fill="both", expand=True
        )
        scrollbar.pack(side="right", fill="y")

        ttk.Button(
            self.subject_tab,
            text="Refresh Dashboard",
            command=self.load_dashboard
        ).pack(anchor="w", pady=(12, 0))

        
        # Deadline Alerts section
        ttk.Label(
            self.subject_tab,
            text="Deadline Alerts",
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", pady=(20, 8))

        self.alerts_list = tk.Listbox(
            self.subject_tab,
            height=5,
            font=("Segoe UI", 10),
            activestyle="none"
        )
        self.alerts_list.pack(
            fill="x",
            expand=False,
            pady=(0, 10)
        )


    # ---------------- TASK INTERFACE ----------------

    def create_task_tab(self):
        toolbar = ttk.Frame(self.task_tab)
        toolbar.pack(fill="x", pady=(0, 12))

        
        ttk.Button(
            toolbar,
            text="Delete Task",
            command=self.delete_task
        ).pack(side="right", padx=(8, 0))
        
        ttk.Button(
            toolbar,
            text="Edit Task",
            command=self.edit_task
        ).pack(side="right", padx=(8, 0))


        ttk.Label(
            toolbar,
            text="Manage Your Tasks",
            font=("Segoe UI", 15, "bold")
        ).pack(side="left")

        ttk.Button(
            toolbar,
            text="Add Task",
            command=self.open_add_task
        ).pack(side="right", padx=(8, 0))

        ttk.Button(
            toolbar,
            text="Mark Completed",
            command=self.mark_completed
        ).pack(side="right", padx=(8, 0))

        ttk.Button(
            toolbar,
            text="Refresh",
            command=self.load_tasks
        ).pack(side="right", padx=(8, 0))

        columns = (
            "id", "title", "subject", "type",
            "due", "difficulty", "minutes",
            "priority", "status"
        )

        self.task_table = ttk.Treeview(
            self.task_tab,
            columns=columns,
            show="headings"
        )

        headings = {
            "id": "ID",
            "title": "Task Title",
            "subject": "Subject",
            "type": "Type",
            "due": "Due Date",
            "difficulty": "Difficulty",
            "minutes": "Minutes",
            "priority": "Priority",
            "status": "Status"
        }

        widths = {
            "id": 45,
            "title": 190,
            "subject": 175,
            "type": 95,
            "due": 100,
            "difficulty": 80,
            "minutes": 80,
            "priority": 125,
            "status": 100
        }

        for column in columns:
            self.task_table.heading(
                column, text=headings[column]
            )
            self.task_table.column(
                column,
                width=widths[column],
                anchor=(
                    "center"
                    if column in (
                        "id", "due", "difficulty",
                        "minutes", "priority", "status"
                    )
                    else "w"
                )
            )

        scrollbar = ttk.Scrollbar(
            self.task_tab,
            orient="vertical",
            command=self.task_table.yview
        )

        self.task_table.configure(
            yscrollcommand=scrollbar.set
        )

        self.task_table.pack(
            side="left", fill="both", expand=True
        )
        scrollbar.pack(side="right", fill="y")

        # Row colors for task priorities
        self.task_table.tag_configure(
            "High", background="#ffdede"
        )
        self.task_table.tag_configure(
            "High (Overdue)", background="#ffb3b3"
        )
        self.task_table.tag_configure(
            "Medium", background="#fff0cc"
        )
        self.task_table.tag_configure(
            "Low", background="#dff5e1"
        )
        self.task_table.tag_configure(
            "Completed", background="#e6e6e6"
        )

    # ---------------- SMART PRIORITY ----------------

    def get_priority(self, due_date, difficulty, completed):
        if completed:
            return "Completed"

        today = datetime.today().date()
        days_left = (due_date - today).days

        if days_left < 0:
            return "High (Overdue)"

        if days_left <= 2:
            return "High"

        if days_left <= 7 and difficulty >= 4:
            return "High"

        if days_left <= 7 or difficulty >= 4:
            return "Medium"

        return "Low"

    # ---------------- LOAD DASHBOARD ----------------

    def load_dashboard(self):
        connection = get_connection()

        if connection is None:
            messagebox.showerror(
                "Database Error",
                "Could not connect to the StudyFlow database."
            )
            return

        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute("SELECT COUNT(*) FROM subjects")
            total_subjects = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM tasks WHERE completed = FALSE"
            )
            pending_tasks = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM tasks WHERE completed = TRUE"
            )
            completed_tasks = cursor.fetchone()[0]

            self.subject_count.config(
                text=f"Subjects: {total_subjects}"
            )
            self.pending_count.config(
                text=f"Pending Tasks: {pending_tasks}"
            )
            self.completed_count.config(
                text=f"Completed Tasks: {completed_tasks}"
            )

            cursor.execute("""
                SELECT subject_id, subject_name, course, semester
                FROM subjects
                ORDER BY subject_name
            """)

            subjects = cursor.fetchall()

            for item in self.subject_table.get_children():
                self.subject_table.delete(item)

            for subject in subjects:
                self.subject_table.insert(
                    "", "end", values=subject
                )

        except Exception as error:
            messagebox.showerror(
                "Dashboard Error", str(error)
            )

        finally:
            if cursor:
                cursor.close()
            connection.close()

        self.load_tasks()
        self.load_deadline_alerts()
        self.load_progress_chart()



    # ---------------- LOAD TASKS ----------------

    
    # ---------------- DEADLINE ALERTS ----------------

    def load_deadline_alerts(self):
        connection = get_connection()

        if connection is None:
            return

        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT title, due_date
                FROM tasks
                WHERE completed = FALSE
                ORDER BY due_date ASC
            """)

            tasks = cursor.fetchall()
            today = datetime.today().date()

            self.alerts_list.delete(0, tk.END)

            for title, due_date in tasks:
                days_left = (due_date - today).days

                if days_left < 0:
                    message = (
                        f"OVERDUE: {title} "
                        f"({abs(days_left)} day(s) late)"
                    )
                elif days_left == 0:
                    message = f"DUE TODAY: {title}"
                elif days_left <= 3:
                    message = (
                        f"DUE SOON: {title} "
                        f"(in {days_left} day(s))"
                    )
                else:
                    continue

                self.alerts_list.insert(tk.END, message)

            if not self.alerts_list.size():
                self.alerts_list.insert(
                    tk.END,
                    "No urgent deadlines. You're on track!"
                )

        except Exception as error:
            messagebox.showerror(
                "Deadline Alert Error", str(error)
            )

        finally:
            if cursor:
                cursor.close()
            connection.close()


    def load_tasks(self):
        connection = get_connection()

        if connection is None:
            messagebox.showerror(
                "Database Error",
                "Could not connect to the StudyFlow database."
            )
            return

        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    t.task_id,
                    t.title,
                    s.subject_name,
                    t.task_type,
                    t.due_date,
                    t.difficulty,
                    t.estimated_minutes,
                    t.completed
                FROM tasks t
                JOIN subjects s
                    ON t.subject_id = s.subject_id
                ORDER BY t.completed ASC, t.due_date ASC
            """)

            tasks = cursor.fetchall()

            for item in self.task_table.get_children():
                self.task_table.delete(item)

            for task in tasks:
                (
                    task_id, title, subject, task_type,
                    due_date, difficulty, minutes, completed
                ) = task

                priority = self.get_priority(
                    due_date, difficulty, completed
                )

                status = "Completed" if completed else "Pending"

                values = (
                    task_id,
                    title,
                    subject,
                    task_type,
                    due_date,
                    difficulty,
                    minutes,
                    priority,
                    status
                )

                self.task_table.insert(
                    "",
                    "end",
                    values=values,
                    tags=(priority,)
                )

        except Exception as error:
            messagebox.showerror(
                "Task Loading Error", str(error)
            )

        finally:
            if cursor:
                cursor.close()
            connection.close()

    
    def load_progress_chart(self):
        """Display completed and pending tasks."""
        connection = get_connection()

        if connection is None:
            return

        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    SUM(CASE WHEN completed = TRUE THEN 1 ELSE 0 END),
                    SUM(CASE WHEN completed = FALSE THEN 1 ELSE 0 END)
                FROM tasks
            """)

            result = cursor.fetchone()
            completed = result[0] or 0
            pending = result[1] or 0

            self.progress_axes.clear()

            if completed == 0 and pending == 0:
                self.progress_axes.text(
                    0.5, 0.5,
                    "No tasks yet. Add a task to begin!",
                    ha="center",
                    va="center",
                    transform=self.progress_axes.transAxes
                )
                self.progress_axes.set_axis_off()
            else:
                self.progress_axes.set_axis_on()

                self.progress_axes.bar(
                    ["Completed", "Pending"],
                    [completed, pending]
                )

                self.progress_axes.set_title(
                    "Completed vs Pending Tasks"
                )
                self.progress_axes.set_ylabel("Number of Tasks")
                self.progress_axes.set_xlabel("Task Status")
                self.progress_axes.set_xticks([0, 1])
                self.progress_axes.set_xticklabels(["Completed", "Pending"])
                self.progress_axes.tick_params(axis="x", labelsize=10, pad=6)
                self.progress_axes.margins(x=0.2, y=0.15)

                for index, value in enumerate([completed, pending]):
                    self.progress_axes.text(
                        index, value, str(value),
                        ha="center", va="bottom"
                    )

            self.progress_figure.tight_layout(pad=2.0)
            self.progress_canvas.draw()

        except Exception as error:
            messagebox.showerror(
                "Progress Chart Error", str(error)
            )

        finally:
            if cursor:
                cursor.close()
            connection.close()

    # ---------------- EDIT TASK ----------------

    def edit_task(self):
        selected = self.task_table.selection()

        if not selected:
            messagebox.showwarning(
                "Select Task",
                "Please select a task to edit."
            )
            return

        values = self.task_table.item(
            selected[0], "values"
        )

        task_id = values[0]

        connection = get_connection()

        if connection is None:
            messagebox.showerror(
                "Database Error",
                "Could not connect to the database."
            )
            return

        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT t.title, t.subject_id, t.task_type,
                       t.due_date, t.difficulty,
                       t.estimated_minutes
                FROM tasks t
                WHERE t.task_id = %s
            """, (task_id,))

            task = cursor.fetchone()

            cursor.execute("""
                SELECT subject_id, subject_name
                FROM subjects
                ORDER BY subject_name
            """)

            subjects = cursor.fetchall()

        except Exception as error:
            messagebox.showerror("Error", str(error))
            return

        finally:
            if cursor:
                cursor.close()
            connection.close()

        if not task:
            messagebox.showerror(
                "Not Found", "The selected task was not found."
            )
            return

        title, subject_id, task_type, due_date, difficulty, minutes = task

        subject_lookup = {
            name: sid for sid, name in subjects
        }
        subject_names = list(subject_lookup.keys())

        form = tk.Toplevel(self.root)
        form.title("Edit Task")
        form.geometry("430x520")
        form.resizable(False, False)
        form.transient(self.root)
        form.grab_set()

        container = ttk.Frame(form, padding=20)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text="Update Task Details",
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", pady=(0, 12))

        def add_field(label_text, widget):
            ttk.Label(
                container, text=label_text
            ).pack(anchor="w", pady=(5, 3))
            widget.pack(fill="x", pady=(0, 3))

        title_entry = ttk.Entry(container)
        title_entry.insert(0, title)
        add_field("Task Title", title_entry)

        subject_combo = ttk.Combobox(
            container,
            values=subject_names,
            state="readonly"
        )
        current_subject = next(
            (name for name, sid in subject_lookup.items()
             if sid == subject_id),
            subject_names[0] if subject_names else ""
        )
        subject_combo.set(current_subject)
        add_field("Subject", subject_combo)

        type_combo = ttk.Combobox(
            container,
            values=[
                "Assignment", "Exam", "Study",
                "Project", "Revision"
            ],
            state="readonly"
        )
        type_combo.set(task_type)
        add_field("Task Type", type_combo)

        due_entry = ttk.Entry(container)
        due_entry.insert(0, str(due_date))
        add_field("Due Date (YYYY-MM-DD)", due_entry)

        difficulty_combo = ttk.Combobox(
            container,
            values=["1", "2", "3", "4", "5"],
            state="readonly"
        )
        difficulty_combo.set(str(difficulty))
        add_field("Difficulty (1 = Easy, 5 = Hard)", difficulty_combo)

        minutes_entry = ttk.Entry(container)
        minutes_entry.insert(0, str(minutes))
        add_field("Estimated Study Time (minutes)", minutes_entry)

        def save_changes():
            new_title = title_entry.get().strip()

            if not new_title:
                messagebox.showwarning(
                    "Missing Title",
                    "Please enter a task title.",
                    parent=form
                )
                return

            try:
                new_due_date = datetime.strptime(
                    due_entry.get().strip(),
                    "%Y-%m-%d"
                ).date()

                new_difficulty = int(difficulty_combo.get())
                new_minutes = int(minutes_entry.get())

                if new_difficulty not in range(1, 6):
                    raise ValueError(
                        "Difficulty must be between 1 and 5."
                    )

                if new_minutes <= 0:
                    raise ValueError(
                        "Study time must be greater than zero."
                    )

                if not subject_combo.get():
                    raise ValueError("Please select a subject.")

            except ValueError as error:
                messagebox.showerror(
                    "Invalid Input", str(error), parent=form
                )
                return

            conn = get_connection()

            if conn is None:
                messagebox.showerror(
                    "Database Error",
                    "Could not connect to the database.",
                    parent=form
                )
                return

            cur = None

            try:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE tasks
                    SET title = %s,
                        subject_id = %s,
                        task_type = %s,
                        due_date = %s,
                        difficulty = %s,
                        estimated_minutes = %s
                    WHERE task_id = %s
                """, (
                    new_title,
                    subject_lookup[subject_combo.get()],
                    type_combo.get(),
                    new_due_date,
                    new_difficulty,
                    new_minutes,
                    task_id
                ))

                conn.commit()
                form.destroy()
                self.load_dashboard()

                messagebox.showinfo(
                    "Success",
                    "Task updated successfully!"
                )

            except Exception as error:
                conn.rollback()
                messagebox.showerror(
                    "Update Error", str(error), parent=form
                )

            finally:
                if cur:
                    cur.close()
                conn.close()

        ttk.Button(
            container,
            text="Save Changes",
            command=save_changes
        ).pack(fill="x", pady=(12, 0))

    # ---------------- ADD TASK FORM ----------------

    def open_add_task(self):
        connection = get_connection()

        if connection is None:
            messagebox.showerror(
                "Database Error",
                "Could not connect to the database."
            )
            return

        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT subject_id, subject_name
                FROM subjects
                ORDER BY subject_name
            """)

            subjects = cursor.fetchall()

        except Exception as error:
            messagebox.showerror("Error", str(error))
            return

        finally:
            if cursor:
                cursor.close()
            connection.close()

        if not subjects:
            messagebox.showwarning(
                "No Subjects",
                "Please add a subject before creating a task."
            )
            return

        subject_lookup = {
            name: subject_id
            for subject_id, name in subjects
        }

        form = tk.Toplevel(self.root)
        form.title("Add New Task")
        form.geometry("430x500")
        form.resizable(False, False)
        form.transient(self.root)
        form.grab_set()

        container = ttk.Frame(form, padding=20)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text="Create a Task",
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", pady=(0, 12))

        def add_field(label_text, widget):
            ttk.Label(
                container, text=label_text
            ).pack(anchor="w", pady=(5, 3))

            widget.pack(fill="x", pady=(0, 3))

        title_entry = ttk.Entry(container)
        add_field("Task Title", title_entry)

        subject_combo = ttk.Combobox(
            container,
            values=list(subject_lookup.keys()),
            state="readonly"
        )
        subject_combo.current(0)
        add_field("Subject", subject_combo)

        type_combo = ttk.Combobox(
            container,
            values=[
                "Assignment", "Exam", "Study",
                "Project", "Revision"
            ],
            state="readonly"
        )
        type_combo.current(0)
        add_field("Task Type", type_combo)

        due_entry = ttk.Entry(container)
        due_entry.insert(
            0, datetime.today().strftime("%Y-%m-%d")
        )
        add_field("Due Date (YYYY-MM-DD)", due_entry)

        difficulty_combo = ttk.Combobox(
            container,
            values=["1", "2", "3", "4", "5"],
            state="readonly"
        )
        difficulty_combo.set("3")
        add_field("Difficulty (1 = Easy, 5 = Hard)",
                  difficulty_combo)

        minutes_entry = ttk.Entry(container)
        minutes_entry.insert(0, "60")
        add_field("Estimated Study Time (minutes)",
                  minutes_entry)

        def save_task():
            title = title_entry.get().strip()

            if not title:
                messagebox.showwarning(
                    "Missing Title",
                    "Please enter a task title.",
                    parent=form
                )
                return

            try:
                due_date = datetime.strptime(
                    due_entry.get().strip(),
                    "%Y-%m-%d"
                ).date()

                difficulty = int(difficulty_combo.get())
                minutes = int(minutes_entry.get())

                if difficulty not in range(1, 6):
                    raise ValueError(
                        "Difficulty must be between 1 and 5."
                    )

                if minutes <= 0:
                    raise ValueError(
                        "Study time must be greater than zero."
                    )

            except ValueError as error:
                messagebox.showerror(
                    "Invalid Input",
                    f"Check the date, difficulty and study time.\n{error}",
                    parent=form
                )
                return

            connection = get_connection()

            if connection is None:
                messagebox.showerror(
                    "Database Error",
                    "Could not connect to the database.",
                    parent=form
                )
                return

            cursor = None

            try:
                cursor = connection.cursor()

                cursor.execute("""
                    INSERT INTO tasks (
                        subject_id,
                        title,
                        task_type,
                        due_date,
                        difficulty,
                        estimated_minutes
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    subject_lookup[subject_combo.get()],
                    title,
                    type_combo.get(),
                    due_date,
                    difficulty,
                    minutes
                ))

                connection.commit()

                messagebox.showinfo(
                    "Success",
                    "Task saved successfully!",
                    parent=form
                )

                form.destroy()
                self.load_dashboard()

            except Exception as error:
                connection.rollback()

                messagebox.showerror(
                    "Save Error", str(error), parent=form
                )

            finally:
                if cursor:
                    cursor.close()
                connection.close()

        ttk.Button(
            container,
            text="Save Task",
            command=save_task
        ).pack(fill="x", pady=(12, 0))

    
    # ---------------- DELETE TASK ----------------

    def delete_task(self):
        selected = self.task_table.selection()

        if not selected:
            messagebox.showwarning(
                "Select Task",
                "Please select a task from the table first."
            )
            return

        values = self.task_table.item(selected[0], "values")
        task_id = values[0]
        task_title = values[1]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{task_title}'?"
        )

        if not confirm:
            return

        connection = get_connection()

        if connection is None:
            messagebox.showerror(
                "Database Error",
                "Could not connect to the database."
            )
            return

        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM tasks WHERE task_id = %s",
                (task_id,)
            )
            connection.commit()
            self.load_dashboard()

            messagebox.showinfo(
                "Success",
                f"Task '{task_title}' deleted successfully."
            )

        except Exception as error:
            connection.rollback()
            messagebox.showerror(
                "Delete Error",
                str(error)
            )

        finally:
            if cursor:
                cursor.close()
            connection.close()


    # ---------------- MARK TASK COMPLETED ----------------

    def mark_completed(self):
        selected = self.task_table.selection()

        if not selected:
            messagebox.showwarning(
                "Select Task",
                "Please select a task from the table first."
            )
            return

        values = self.task_table.item(
            selected[0], "values"
        )

        task_id = values[0]
        status = values[8]

        if status == "Completed":
            messagebox.showinfo(
                "Already Completed",
                "This task is already completed."
            )
            return

        connection = get_connection()

        if connection is None:
            messagebox.showerror(
                "Database Error",
                "Could not connect to the database."
            )
            return

        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE tasks
                SET completed = TRUE
                WHERE task_id = %s
            """, (task_id,))

            connection.commit()

            self.load_dashboard()

            messagebox.showinfo(
                "Success",
                "Task marked as completed!"
            )

        except Exception as error:
            connection.rollback()

            messagebox.showerror(
                "Update Error", str(error)
            )

        finally:
            if cursor:
                cursor.close()
            connection.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = StudyFlowApp(root)
    root.mainloop()
