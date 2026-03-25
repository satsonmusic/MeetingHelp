# 🤝 Meeting Excellence Toolkit (MeetingHelp)

> **Stop Meeting Theater. Start Execution.** An automated agenda and execution loop engine designed to eliminate "orphaned follow-ups" and drive measurable program momentum.

In high-growth organizations, the "Meeting Tax" is the most expensive hidden cost. **MeetingHelp** is a high-discipline operational tool that automates the loop between agenda-setting, decision-capture, and action-follow-through. By programmatically generating executive-ready agendas from open risks and overdue milestones, it ensures every meeting is focused on results, not updates.

## 🚀 Key Features

* **Automated Agenda Generation:** Dynamically pulls from `risks.csv`, `decisions.csv`, and `actions.csv` to build a prioritized, time-boxed meeting agenda.
* **Execution Roll-Forward:** Automatically identifies overdue action items and open decisions, ensuring they are front-and-center in the next sync until resolved.
* **Dynamic Data Mapping:** Uses Python type reflection (`dataclasses` + `type hints`) to synchronize disparate tracking logs into a unified execution framework.
* **Zero-Dependency Architecture:** Built entirely on the Python 3.12 Standard Library for maximum portability across restricted corporate environments.

## 🛠️ Tech Stack

* **Language:** Python 3.12 (Standard Library)
* **Core Modules:** `dataclasses`, `argparse`, `pathlib`, `csv`
* **Output:** Markdown Agenda & Follow-up Artifacts

## ⚙️ How to Run

### 1. Clone the Repository
```bash
git clone https://github.com/satsonmusic/MeetingHelp.git
cd MeetingHelp
```

### 2. Set Up Python Environment
Ensure Python 3.12+ is installed. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Prepare Your Data Files
Create three CSV files in the project directory:

- **risks.csv** - Open risks and blockers
- **decisions.csv** - Pending decisions requiring action
- **actions.csv** - Action items with due dates

### 4. Run MeetingHelp
```bash
python meetinghelp.py
```

This will generate:
- `agenda.md` - Prioritized meeting agenda
- `follow_ups.md` - Action tracking and accountability log