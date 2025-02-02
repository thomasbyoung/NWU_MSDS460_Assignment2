(async function () {
    const scenarioSelect = document.getElementById("scenarioSelect");
    const solveBtn = document.getElementById("solveBtn");
    const resultsDiv = document.getElementById("results");
    const costSummaryDiv = document.getElementById("costSummary");
    const chartCanvas = document.getElementById("ganttChart");
    let tasks = [];
    let preds = {};
    let ganttChart = null;

    // Worker costs per hour
    const WORKER_COSTS = {
        projectManager: 150,
        fullStackDev1: 125,
        fullStackDev2: 125,
        cloudDevops: 140,
        dataEngineer: 135
    };

    try {
        const resp = await fetch("tasks.json");
        if (!resp.ok) {
            throw new Error(`HTTP error! status: ${resp.status}`);
        }
        const json = await resp.json();
        tasks = json.tasks || [];
        preds = json.predecessors || {};

        // Initial solve
        const scenario = scenarioSelect.value;
        solveSchedule(tasks, preds, scenario);
    } catch (err) {
        console.error("Error loading tasks.json:", err);
        resultsDiv.textContent = `Failed to load tasks.json: ${err.message}`;
        return;
    }

    solveBtn.addEventListener("click", () => {
        const scenario = scenarioSelect.value;
        solveSchedule(tasks, preds, scenario);
    });

    function calculateTaskCosts(task, duration) {
        let cost = 0;
        for (const [worker, rate] of Object.entries(WORKER_COSTS)) {
            const hours = task[worker] || 0;
            cost += (hours * rate);
        }
        return cost;
    }

    function solveSchedule(tasks, preds, scenario) {
        const durations = {};
        const taskCosts = {};
        tasks.forEach(t => {
            durations[t.id] = t[scenario] || 0;
            taskCosts[t.id] = calculateTaskCosts(t, durations[t.id]);
        });

        const constraints = {};
        const variables = {};
        tasks.forEach(t => {
            const vName = "S_" + t.id;
            variables[vName] = { cost: 0 };
        });
        variables["Tmax"] = { cost: 1 };

        tasks.forEach(t => {
            const cName = `Fin_${t.id}`;
            const vS = "S_" + t.id;
            if (!constraints[cName]) constraints[cName] = {};
            constraints[cName]["min"] = 0;
            if (!variables["Tmax"][cName]) variables["Tmax"][cName] = 0;
            variables["Tmax"][cName] += 1;
            if (!variables[vS][cName]) variables[vS][cName] = 0;
            variables[vS][cName] -= 1;
            constraints[cName]["min"] = durations[t.id];
        });

        tasks.forEach(t => {
            const tName = "S_" + t.id;
            const pList = preds[t.id] || [];
            pList.forEach(p => {
                const cName = `Pred_${p}_to_${t.id}`;
                if (!constraints[cName]) constraints[cName] = {};
                constraints[cName]["min"] = 0;
                const pName = "S_" + p;
                if (!variables[tName][cName]) variables[tName][cName] = 0;
                variables[tName][cName] += 1;
                if (!variables[pName][cName]) variables[pName][cName] = 0;
                variables[pName][cName] -= 1;
                constraints[cName]["min"] = durations[p];
            });
        });

        tasks.forEach(t => {
            const cName = `NonNeg_${t.id}`;
            if (!constraints[cName]) constraints[cName] = {};
            constraints[cName]["min"] = 0;
            const vS = "S_" + t.id;
            if (!variables[vS][cName]) variables[vS][cName] = 0;
            variables[vS][cName] += 1;
        });

        const lp = {
            optimize: "cost",
            opType: "min",
            constraints: constraints,
            variables: variables
        };

        const results = solver.Solve(lp);
        if (results.feasible) {
            let finishTime = results.Tmax || 0;
            let totalCost = 0;
            let schedule = [];

            tasks.forEach(t => {
                let st = results["S_" + t.id] || 0;
                let ed = st + (durations[t.id] || 0);
                let cost = taskCosts[t.id];
                totalCost += cost;
                schedule.push({
                    id: t.id,
                    start: st,
                    end: ed,
                    description: t.description,
                    cost: cost
                });
            });

            // Sort schedule by start time
            schedule.sort((a, b) => a.start - b.start);

            // Update results display
            resultsDiv.textContent = `${scenario.toUpperCase()} SCENARIO\n`;
            resultsDiv.textContent += `Status: feasible\n`;
            resultsDiv.textContent += `Total Duration: ${finishTime.toFixed(2)} hours\n\n`;

            schedule.forEach(s => {
                resultsDiv.textContent += `Task ${s.id} (${s.description})\n`;
                resultsDiv.textContent += `  Start: ${s.start.toFixed(1)}\n`;
                resultsDiv.textContent += `  End: ${s.end.toFixed(1)}\n`;
                resultsDiv.textContent += `  Cost: $${s.cost.toLocaleString()}\n\n`;
            });

            // Update cost summary
            costSummaryDiv.innerHTML = `
                <h3>Cost Summary</h3>
                <p>Total Project Cost: $${totalCost.toLocaleString()}</p>
                <p>Project Duration: ${finishTime.toFixed(2)} hours</p>
                <p>Average Cost per Hour: $${(totalCost / finishTime).toFixed(2)}</p>
            `;

            drawGanttChart(schedule);
        } else {
            resultsDiv.textContent = `Scenario: ${scenario}\nStatus: infeasible\n`;
            costSummaryDiv.innerHTML = '';
        }
    }

    function drawGanttChart(schedule) {
        if (ganttChart) ganttChart.destroy();

        // Sort by start time for the chart
        schedule.sort((a, b) => a.start - b.start);

        const labels = schedule.map(s => `${s.id}: ${s.description}`);
        const starts = schedule.map(s => s.start);
        const durations = schedule.map(s => (s.end - s.start));

        const ctx = document.getElementById("ganttChart").getContext("2d");
        ganttChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Start Offset',
                        data: starts,
                        backgroundColor: 'rgba(0,0,0,0)',
                        borderWidth: 0
                    },
                    {
                        label: 'Task Duration',
                        data: durations,
                        backgroundColor: 'rgba(54, 162, 235, 0.8)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        stacked: true,
                        title: {
                            display: true,
                            text: 'Time (hours)',
                            font: { size: 14 }
                        }
                    },
                    y: {
                        stacked: true,
                        title: {
                            display: true,
                            text: 'Tasks',
                            font: { size: 14 }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { font: { size: 12 } }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const s = schedule[context.dataIndex];
                                if (context.dataset.label === 'Task Duration') {
                                    return [
                                        `Duration: ${durations[context.dataIndex].toFixed(1)} hours`,
                                        `Cost: $${s.cost.toLocaleString()}`
                                    ];
                                }
                                return '';
                            }
                        }
                    }
                }
            }
        });
    }
})();