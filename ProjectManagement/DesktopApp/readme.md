# Project Schedule Desktop App

A desktop application for project schedule optimization using linear programming, built with Python and Tkinter. Features an interactive UI with editable task list, scenario analysis, and Gantt chart visualization.

## Requirements

```bash
pip install pulp matplotlib
```

## Setup

1. Place these files in the same directory:
   - app.py
   - tasks.json

2. Run the application:
   ```bash
   python app.py
   ```

## Features

- Interactive task list with editable fields (double-click to edit)
- Three scenario options: Best, Expected, and Worst case
- Real-time schedule optimization using PuLP solver
- Visual Gantt chart representation
- Detailed results panel showing task timings

## Task Configuration

Tasks are defined in `tasks.json` with:
- Task dependencies
- Duration estimates (best/expected/worst)
- Resource allocation for different roles:
  - Project Manager
  - Full Stack Developers
  - Cloud DevOps
  - Data Engineer