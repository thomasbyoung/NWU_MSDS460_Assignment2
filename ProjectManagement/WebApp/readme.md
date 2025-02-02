# Project Schedule Solver

A simple web application for project schedule optimization using linear programming. This tool helps visualize task dependencies, calculate project timelines, and estimate costs based on worker allocation.

## Setup

1. Place all files in the same directory:
   - index.html
   - script.js
   - tasks.json

2. Start a local server:
   ```bash
   python -m http.server
   ```

3. Open in your browser:
   ```
   http://localhost:8000
   ```

## Usage

- Select a scenario (Best Case, Expected Case, or Worst Case)
- Click "Solve Schedule" to generate the schedule
- View the Gantt chart and cost breakdown
- Hover over task bars to see detailed timing and cost information

## Task Configuration

Tasks are defined in `tasks.json` with:
- Task dependencies
- Duration estimates
- Worker hour allocations
- Worker costs per hour