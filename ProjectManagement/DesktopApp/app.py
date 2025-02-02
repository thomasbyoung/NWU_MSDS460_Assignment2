import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

import pulp
import matplotlib
matplotlib.use("TkAgg")  # Embedding matplotlib in Tk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

JSON_FILE = "tasks.json"

class TaskManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Project Scheduler with Gantt")
        
        # Make the window larger by default: 1400x800
        self.geometry("1400x800")

        # Store scenario choice (best/expected/worst) + last solution
        self.scenario_var = tk.StringVar(value="expected")
        self.last_solution = None  # Will hold start/end times after solving

        # Data structures for tasks
        self.tasks_data = []
        self.predecessors_map = {}

        # Build UI
        self.create_layout()
        self.load_data(JSON_FILE)
        self.populate_treeview()

    # -------------------------- LAYOUT -------------------------- #
    def create_layout(self):
        """Create the main UI layout: top controls, horizontal area (left=tree, right=results),
           and bottom area for Gantt chart."""
        
        # -- Top Frame for scenario selection & Solve button
        top_frame = ttk.Frame(self, padding=5)
        top_frame.pack(side="top", fill="x")
        
        ttk.Label(top_frame, text="Scenario:").pack(side="left", padx=5)
        scenario_combo = ttk.Combobox(
            top_frame, textvariable=self.scenario_var,
            values=["best","expected","worst"], width=10
        )
        scenario_combo.pack(side="left")
        
        solve_btn = ttk.Button(top_frame, text="Solve Schedule", command=self.solve_schedule)
        solve_btn.pack(side="left", padx=10)

        # -- Middle Frame holds the Treeview on the left, and the results on the right
        middle_frame = ttk.Frame(self)
        middle_frame.pack(side="top", fill="both", expand=True)

        # We can use a PanedWindow or just two frames side by side
        left_frame = ttk.Frame(middle_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        right_frame = ttk.Frame(middle_frame, width=350)  # set a width for the results panel
        right_frame.pack(side="right", fill="y", padx=5, pady=5)

        # Treeview in the left_frame
        columns = ("id","description","best","expected","worst",
                   "projectManager","fullStackDev1","fullStackDev2","cloudDevops","dataEngineer")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=100, anchor="center")
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        self.tree.pack(fill="both", expand=True)

        # Results text on the right_frame
        ttk.Label(right_frame, text="Schedule Results:", anchor="w").pack(fill="x")
        self.results_text = tk.Text(right_frame, height=25, wrap="word")
        self.results_text.pack(fill="both", expand=True)

        # -- Bottom Frame for the Gantt Chart
        self.gantt_frame = ttk.Frame(self, padding=5)
        self.gantt_frame.pack(side="bottom", fill="both", expand=False)

    # -------------------------- DATA LOADING -------------------------- #
    def load_data(self, path):
        if not os.path.exists(path):
            messagebox.showerror("File Error", f"Cannot find {path}")
            return
        with open(path, "r") as f:
            data = json.load(f)
        self.tasks_data = data.get("tasks", [])
        self.predecessors_map = data.get("predecessors", {})

    def populate_treeview(self):
        """Insert the loaded tasks into the Treeview."""
        for row_id in self.tree.get_children():
            self.tree.delete(row_id)
        for task in self.tasks_data:
            vals = (
                task.get("id",""),
                task.get("description",""),
                task.get("best",0),
                task.get("expected",0),
                task.get("worst",0),
                task.get("projectManager",0),
                task.get("fullStackDev1",0),
                task.get("fullStackDev2",0),
                task.get("cloudDevops",0),
                task.get("dataEngineer",0)
            )
            self.tree.insert("", tk.END, values=vals)

    # -------------------------- EDITING -------------------------- #
    def on_tree_double_click(self, event):
        """Allow user to edit a cell via a small pop-up."""
        sel = self.tree.focus()
        if not sel:
            return
        column = self.tree.identify_column(event.x)  # e.g. '#1'
        col_index = int(column.replace("#","")) - 1
        old_values = list(self.tree.item(sel, "values"))
        old_val = old_values[col_index]

        edit_win = tk.Toplevel(self)
        edit_win.title("Edit Value")
        tk.Label(edit_win, text=f"Current: {old_val}").pack(pady=5)
        e = ttk.Entry(edit_win)
        e.insert(0, str(old_val))
        e.pack(padx=5, pady=5)

        def save_val():
            new_val = e.get()
            old_values[col_index] = new_val
            self.tree.item(sel, values=old_values)
            edit_win.destroy()

        ttk.Button(edit_win, text="OK", command=save_val).pack(pady=5)

    def gather_data(self):
        """Pull updated data from the Treeview back into a list of dicts."""
        updated = []
        for row_id in self.tree.get_children():
            vals = self.tree.item(row_id, "values")
            # Convert numeric columns to float
            updated.append({
                "id": vals[0],
                "description": vals[1],
                "best": float(vals[2]),
                "expected": float(vals[3]),
                "worst": float(vals[4]),
                "projectManager": float(vals[5]),
                "fullStackDev1": float(vals[6]),
                "fullStackDev2": float(vals[7]),
                "cloudDevops": float(vals[8]),
                "dataEngineer": float(vals[9])
            })
        return updated

    # -------------------------- SOLVING -------------------------- #
    def solve_schedule(self):
        """Build a PuLP model for the chosen scenario, solve, and display results & Gantt."""
        scenario = self.scenario_var.get().lower()
        task_rows = self.gather_data()

        # Construct a map from taskID -> scenario hours
        dur_map = {}
        for t in task_rows:
            dur_map[t["id"]] = t[scenario]

        # Build LP
        model = pulp.LpProblem("ProjectPlan", pulp.LpMinimize)
        S = { t["id"]: pulp.LpVariable(f"S_{t['id']}", lowBound=0) for t in task_rows }
        C = { t["id"]: pulp.LpVariable(f"C_{t['id']}", lowBound=0) for t in task_rows }
        T_max = pulp.LpVariable("T_max", lowBound=0)

        model += T_max, "MinimizeProjectFinish"

        for t in task_rows:
            tid = t["id"]
            d = dur_map[tid]
            model += (C[tid] == S[tid] + d), f"Duration_{tid}"
            model += (C[tid] <= T_max),     f"Bound_{tid}"
            
            # Predecessors
            preds = self.predecessors_map.get(tid, [])
            for p in preds:
                if p in dur_map:  # only constrain if in our known tasks
                    model += (S[tid] >= C[p]), f"Pred_{p}_to_{tid}"

        solver = pulp.PULP_CBC_CMD(msg=False)
        model.solve(solver)
        status = pulp.LpStatus[model.status]
        finish_time = pulp.value(model.objective)

        # Store solution for Gantt
        start_dict = { t["id"]: pulp.value(S[t["id"]]) for t in task_rows }
        end_dict   = { t["id"]: pulp.value(C[t["id"]]) for t in task_rows }
        self.last_solution = {
            "scenario": scenario.capitalize(),
            "status": status,
            "finish_time": finish_time,
            "start_times": start_dict,
            "end_times": end_dict
        }

        # Display textual results on the right
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, f"Scenario: {scenario.capitalize()}\n")
        self.results_text.insert(tk.END, f"Solver Status: {status}\n")
        self.results_text.insert(tk.END, f"Finish Time = {finish_time:.2f} hours\n\n")

        # Sort tasks by alphabetical ID for printing
        for task in sorted(task_rows, key=lambda x: x["id"]):
            tid = task["id"]
            st = start_dict[tid]
            ed = end_dict[tid]
            self.results_text.insert(tk.END, f" Task {tid}: Start={st:.1f}, End={ed:.1f}\n")

        # Generate Gantt at bottom
        self.draw_gantt_chart()

    # -------------------------- GANTT CHART -------------------------- #
    def draw_gantt_chart(self):
        """Draw the Gantt chart in the bottom frame using matplotlib."""
        for widget in self.gantt_frame.winfo_children():
            widget.destroy()  # Clear old chart

        if not self.last_solution:
            return
        
        sol = self.last_solution
        start_map = sol["start_times"]
        end_map = sol["end_times"]
        
        # Sort tasks by ID or start time
        tasks_sorted = sorted(start_map.keys())
        
        fig, ax = plt.subplots(figsize=(12,4), dpi=100)

        # We'll reverse the order so the first is top
        rev_tasks = list(reversed(tasks_sorted))
        for i, t in enumerate(rev_tasks):
            s = start_map[t]
            e = end_map[t]
            dur = e - s
            ax.barh(i, dur, left=s, height=0.4, color="skyblue", edgecolor="black")
            ax.text(s + dur/2, i, f"{t} ({dur:.1f}h)", va="center", ha="center", color="black")

        ax.set_xlabel("Time (hours)")
        ax.set_yticks(range(len(rev_tasks)))
        ax.set_yticklabels(rev_tasks)
        ax.set_title(f"Gantt Chart - {sol['scenario']} Scenario")

        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.gantt_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

# -------------------------- MAIN -------------------------- #
if __name__ == "__main__":
    app = TaskManagerApp()
    app.mainloop()
