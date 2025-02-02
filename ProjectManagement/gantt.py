import pulp
import matplotlib.pyplot as plt


TASKS = [
    "A","B","C","D1","D2","D3","D4","D5","D6","D7","D8","E","F","G","H"
]
PREDECESSORS = {
    "A": [],       "B": [],
    "C": ["A"],    "D1": ["A"],
    "D2": ["D1"],  "D3": ["D1"],
    "D4": ["D2","D3"],  "D5": ["D4"], "D6": ["D4"],
    "D7": ["D6"],       "D8": ["D5","D7"],
    "E": ["B","C"],      "F": ["D8","E"],
    "G": ["A","D8"],     "H": ["F","G"]
}

DURATIONS_BEST = {
    "A":4, "B":2, "C":6,  "D1":6, "D2":8,  "D3":8,  
    "D4":16,"D5":4,"D6":6,"D7":8, "D8":4,
    "E":6,  "F":4, "G":4, "H":4
}
DURATIONS_EXPECTED = {
    "A":8,  "B":6,  "C":10, "D1":10,"D2":12,"D3":12,
    "D4":24,"D5":12,"D6":24,"D7":12,"D8":8,
    "E":12, "F":8,  "G":8,  "H":8
}
DURATIONS_WORST = {
    "A":12,"B":10,"C":16,"D1":15,"D2":18,"D3":18,
    "D4":40,"D5":18,"D6":40,"D7":20,"D8":12,
    "E":18,"F":12,"G":12,"H":12
}

def solve_schedule(tasks, predecessors, durations, label):
    model = pulp.LpProblem(f"LP_{label}", pulp.LpMinimize)
    S = {t: pulp.LpVariable(f"S_{t}", lowBound=0) for t in tasks}
    C = {t: pulp.LpVariable(f"C_{t}", lowBound=0) for t in tasks}
    T_max = pulp.LpVariable("T_max", lowBound=0)
    model += T_max, "MinimizeProjectFinish"
    for t in tasks:
        model += (C[t] == S[t] + durations[t]), f"Duration_{t}"
        model += (C[t] <= T_max),               f"Bound_{t}"
        for p in predecessors.get(t, []):
            model += (S[t] >= C[p]),           f"Pred_{p}_to_{t}"
    solver = pulp.PULP_CBC_CMD(msg=False)
    model.solve(solver)
    status = pulp.LpStatus[model.status]
    finish_time = pulp.value(model.objective)
    starts = {t: pulp.value(S[t]) for t in tasks}
    ends   = {t: pulp.value(C[t]) for t in tasks}
    print(f"----- {label} SCENARIO -----")
    print(f"Status: {status}, Finish Time = {finish_time:.2f}\n")
    for t in sorted(tasks):
        print(f" Task {t}: Start={starts[t]:.1f}, End={ends[t]:.1f}, Duration={durations[t]}")
    print()

    return starts, ends, finish_time

def plot_gantt(tasks, starts, ends, title="Gantt Chart"):
    fig, ax = plt.subplots(figsize=(8, 5))
    ordered_tasks = list(reversed(sorted(tasks)))
    
    for i, t in enumerate(ordered_tasks):
        s = starts[t]
        e = ends[t]
        dur = e - s
        ax.barh(i, dur, left=s, color="skyblue", edgecolor="black", height=0.4)
        ax.text(s + dur/2, i, f"{t} ({dur:.1f}h)", va="center", ha="center")
    
    ax.set_yticks(range(len(ordered_tasks)))
    ax.set_yticklabels(ordered_tasks)
    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("Tasks")
    ax.set_title(title)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    best_starts, best_ends, best_finish = solve_schedule(TASKS, PREDECESSORS, DURATIONS_BEST, "BestCase")
    exp_starts, exp_ends, exp_finish   = solve_schedule(TASKS, PREDECESSORS, DURATIONS_EXPECTED, "ExpectedCase")
    worst_starts, worst_ends, worst_finish = solve_schedule(TASKS, PREDECESSORS, DURATIONS_WORST, "WorstCase")
    
    plot_gantt(TASKS, best_starts, best_ends, title="Best-Case Gantt")
    plot_gantt(TASKS, exp_starts, exp_ends,   title="Expected-Case Gantt")
    plot_gantt(TASKS, worst_starts, worst_ends, title="Worst-Case Gantt")
