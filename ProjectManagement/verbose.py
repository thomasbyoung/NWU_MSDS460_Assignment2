import pulp 


all_tasks = [
    "A",   # Describe product
    "B",   # Develop marketing strategy
    "C",   # Design brochure
    "D1",  # Requirements analysis
    "D2",  # Software design
    "D3",  # System design
    "D4",  # Coding
    "D5",  # Write documentation
    "D6",  # Unit testing
    "D7",  # System testing
    "D8",  # Package deliverables
    "E",   # Survey potential market
    "F",   # Develop pricing plan
    "G",   # Develop implementation plan
    "H"    # Write client proposal
]

predecessors_map = {
    "A":  [],               # A has no predecessor
    "B":  [],               # B has no predecessor
    "C":  ["A"],            # C depends on A
    "D1": ["A"],            # D1 depends on A
    "D2": ["D1"],           # D2 depends on D1
    "D3": ["D1"],           # D3 depends on D1
    "D4": ["D2", "D3"],     # D4 depends on D2, D3
    "D5": ["D4"],           # D5 depends on D4
    "D6": ["D4"],           # D6 depends on D4
    "D7": ["D6"],           # D7 depends on D6
    "D8": ["D5", "D7"],     # D8 depends on D5, D7
    "E":  ["B", "C"],       # E depends on B, C
    "F":  ["D8", "E"],      # F depends on D8, E
    "G":  ["A", "D8"],      # G depends on A, D8
    "H":  ["F", "G"]        # H depends on F, G
}

durations_best = {
    "A":  4, "B":  2, "C":  6,
    "D1": 6, "D2":  8, "D3":  8,
    "D4":16, "D5":  4, "D6":  6,
    "D7": 8, "D8":  4, "E":   6,
    "F":  4, "G":   4, "H":   4
}

durations_expected = {
    "A":  8, "B":  6, "C": 10,
    "D1":10, "D2": 12, "D3": 12,
    "D4":24, "D5": 12, "D6": 24,
    "D7":12, "D8":  8, "E":  12,
    "F":  8, "G":   8, "H":   8
}

durations_worst = {
    "A": 12, "B": 10, "C": 16,
    "D1":15, "D2": 18, "D3": 18,
    "D4":40, "D5": 18, "D6": 40,
    "D7":20, "D8": 12, "E":  18,
    "F": 12, "G":  12, "H":  12
}

def solve_scenario(task_list, pred_map, durations_dict, scenario_label):
    print("====================================================")
    print(f"BUILDING LINEAR PROGRAM FOR SCENARIO: {scenario_label}")
    print("====================================================\n")
    
    lp_problem = pulp.LpProblem(f"Project_{scenario_label}", pulp.LpMinimize)
    
    S = {} 
    C = {}  
    
    for task_id in task_list:
        S[task_id] = pulp.LpVariable(
            f"S_{task_id}",  
            lowBound=0,      
            cat=pulp.LpContinuous 
        )
        
        C[task_id] = pulp.LpVariable(
            f"C_{task_id}",
            lowBound=0,
            cat=pulp.LpContinuous
        )
    
    T_max = pulp.LpVariable("T_max", lowBound=0, cat=pulp.LpContinuous)

    lp_problem += T_max, "Minimize_Overall_Project_Time"
    
    for task_id in task_list:
        task_duration = durations_dict[task_id] 
        lp_problem += (
            C[task_id] == S[task_id] + task_duration,
            f"CompletionDef_{task_id}"
        )

        lp_problem += (
            C[task_id] <= T_max,
            f"UpperBound_{task_id}"
        )
        
        
        if task_id in pred_map:
            for p in pred_map[task_id]:
                lp_problem += (
                    S[task_id] >= C[p],
                    f"Pred_{p}_to_{task_id}"
                )

    solver = pulp.PULP_CBC_CMD(msg=False)  
    lp_problem.solve(solver)
    
    solve_status = pulp.LpStatus[lp_problem.status]
    objective_value = pulp.value(lp_problem.objective) 
    solution_start_times = {}
    solution_completion_times = {}
    
    for task_id in task_list:
        solution_start_times[task_id] = pulp.value(S[task_id])
        solution_completion_times[task_id] = pulp.value(C[task_id])
    print(f"Scenario: {scenario_label}")
    print(f"Solver Status: {solve_status}")
    print(f"Minimum Project Finish Time (T_max) = {objective_value:.2f} hours\n")
    print("Detailed Task Schedule:")
    for t_id in sorted(task_list):
        s_val = solution_start_times[t_id]
        c_val = solution_completion_times[t_id]
        dur_used = durations_dict[t_id]
        print(
            f"  Task {t_id}: Duration={dur_used}  "
            f"Start={s_val:.2f},  Completion={c_val:.2f}"
        )
    print("")
    return {
        "status": solve_status,
        "T_max": objective_value,
        "start_times": solution_start_times,
        "completion_times": solution_completion_times
    }



best_results = solve_scenario(all_tasks, predecessors_map, durations_best, "BestCase")
expected_results = solve_scenario(all_tasks, predecessors_map, durations_expected, "ExpectedCase")
worst_results = solve_scenario(all_tasks, predecessors_map, durations_worst, "WorstCase")


###############################################################################
# STEP 4 (OPTIONAL): FURTHER SENSITIVITY ANALYSIS
###############################################################################

# If you want to explore how small changes to any one task's duration might
# alter the schedule or critical path, you can:
#
# 1) Copy one of the durations dicts. For example, let's tweak the best case
#    to see what happens if "D4" (Coding) is 20 hours instead of 16.
#
#    Example:
#       alt_best_durations = durations_best.copy()
#       alt_best_durations["D4"] = 20
#
# 2) Then call solve_scenario() again with alt_best_durations:
#       alt_results = solve_scenario(all_tasks, predecessors_map, alt_best_durations, "AltBestCase")
#
# 3) Compare alt_results["T_max"] with best_results["T_max"] to see if the
#    minimal finishing time changed significantly. If "D4" was on the critical
#    path already, you might see a direct increase in T_max. If it wasn't,
#    T_max might remain the same, indicating concurrency or slack in that task.
#
# This is how you can manually exercise sensitivity analysis within the same
# framework, purely by adjusting the input data for the tasks.
#
# End of script.
