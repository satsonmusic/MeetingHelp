import csv
import argparse
from dataclasses import dataclass, fields
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Optional, Any, get_type_hints

DATE_FMT = "%Y-%m-%d"

# --- 1. CONFIGURATION & PATHS ---

def _lab_root() -> Path:
    """Portable: Automatically finds the folder where this script is located."""
    return Path(__file__).parent.resolve()

def _resolve_io_path(p: str) -> Path:
    path = Path(p)
    if path.is_absolute():
        return path
    return (_lab_root() / path).resolve()

# --- 2. DATA MODELS ---

@dataclass
class Decision:
    program: str
    workstream: str
    title: str
    decider: str
    status: str
    deadline: Optional[date]
    last_update: Optional[date]
    context: str

@dataclass
class ActionItem:
    program: str
    workstream: str
    description: str
    owner: str
    status: str
    due_date: Optional[date]
    last_update: Optional[date]
    next_checkpoint: Optional[date]
    notes: str

@dataclass
class RiskItem:
    program: str
    workstream: str
    description: str
    owner: str
    severity: str
    status: str
    next_step: str
    next_checkpoint: Optional[date]

# --- 3. UTILS & LOADING ---

def parse_date(s: str) -> Optional[date]:
    s = (s or "").strip()
    if not s: return None
    try:
        return datetime.strptime(s, DATE_FMT).date()
    except ValueError:
        return None

def fmt_date(d: Optional[date]) -> str:
    return d.isoformat() if d else "—"

def is_open(s: str) -> bool:
    """Determines if a status represents an active item."""
    return (s or "").strip().lower() in {"open", "in progress", "pending", "active"}

def is_done(s: str) -> bool:
    """Determines if a status represents a completed item."""
    return (s or "").strip().lower() in {"done", "closed", "complete", "mitigated"}

def overdue(d: Optional[date], today: date) -> bool:
    return d is not None and d < today

def due_soon(d: Optional[date], today: date, window_days: int) -> bool:
    return d is not None and today <= d <= (today + timedelta(days=window_days))

def load_records(path: Path, cls: Any) -> List[Any]:
    """Dynamic record loader using Python Type Reflection."""
    if not path.exists():
        print(f"!!! [Missing File]: Could not find {path.name}")
        return []

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if not rows: return []
        
        # Validate headers
        csv_headers = set(reader.fieldnames or [])
        expected_fields = {f.name for f in fields(cls)}
        missing = expected_fields - csv_headers
        if missing:
            print(f"!!! [Column Error] {path.name} is missing: {missing}")

        hints = get_type_hints(cls)
        records = []
        for r in rows:
            data = {}
            for f_name, f_type in hints.items():
                val = (r.get(f_name) or "").strip()
                # If the type hint is a date, parse it
                if "date" in str(f_type).lower():
                    data[f_name] = parse_date(val)
                else:
                    data[f_name] = val
            records.append(cls(**data))
        return records

# --- 4. MARKDOWN GENERATORS ---

def agenda_md(meeting_title: str, today: date, decisions: List[Decision], actions: List[ActionItem], risks: List[RiskItem], due_soon_days: int) -> str:
    lines = [
        f"# {meeting_title}", 
        "", 
        f"Date: {today.isoformat()}", 
        "Attendees: ", 
        "Timebox: 60m", 
        "", 
        "## 1) Critical Decisions Needed",
        "---"
    ]
    
    open_dec = sorted([d for d in decisions if is_open(d.status)], key=lambda x: x.deadline or date.max)
    if not open_dec:
        lines.append("- No pending decisions found.")
    else:
        for d in open_dec:
            flag = "**(OVERDUE)**" if overdue(d.deadline, today) else "*(DUE SOON)*" if due_soon(d.deadline, today, due_soon_days) else ""
            lines.append(f"- **{d.program} / {d.workstream}**: {d.title} (Deadline: {fmt_date(d.deadline)}) {flag}")
            if d.context: lines.append(f"  - Context: {d.context}")

    lines.append("\n## 2) Top Blockers & Risks")
    lines.append("---")
    r_open = [r for r in risks if not is_done(r.status)]
    if not r_open:
        lines.append("- No active blockers recorded.")
    else:
        for r in r_open[:5]:
            lines.append(f"- [{r.severity.upper()}] {r.program} / {r.workstream}: {r.description} (Owner: {r.owner})")

    lines.append("\n## 3) Action Items (Overdue/Due Soon)")
    lines.append("---")
    a_flagged = [a for a in actions if not is_done(a.status) and (overdue(a.due_date, today) or due_soon(a.due_date, today, due_soon_days))]
    if not a_flagged:
        lines.append("- All tracked actions are healthy.")
    else:
        for a in a_flagged:
            status_flag = "**(OVERDUE)**" if overdue(a.due_date, today) else "*(DUE SOON)*"
            lines.append(f"- {a.description} (Owner: {a.owner}) — Due: {fmt_date(a.due_date)} {status_flag}")

    lines.append("\n## 4) Discussion & New Business")
    lines.append("- (Item 1)")
    lines.append("- (Item 2)")

    return "\n".join(lines)

def followup_md(meeting_title: str, today: date) -> str:
    lines = [
        f"# Follow-up — {meeting_title}",
        "",
        f"Date: {today.isoformat()}",
        "",
        "## Summary",
        "- High-level meeting outcome goes here.",
        "",
        "## New Decisions Made",
        "- [DECISION]: Describe the choice, decider, and rationale.",
        "",
        "## New Action Items",
        "- [ACTION]: Description | Owner | Due Date",
        "",
        "## Next Steps",
        "- Focus for the next sprint/checkpoint."
    ]
    return "\n".join(lines)

# --- 5. MAIN EXECUTION ---

def main() -> None:
    p = argparse.ArgumentParser(description="Meeting Excellence Toolkit")
    p.add_argument("--decisions", default="decisions.csv")
    p.add_argument("--actions", default="actions.csv")
    p.add_argument("--risks", default="risks.csv")
    p.add_argument("--title", default="Weekly Program Sync")
    p.add_argument("--out-agenda", default="agenda.md")
    p.add_argument("--out-followup", default="followup.md")
    
    args, _ = p.parse_known_args()
    today = date.today()

    # Data Load
    decisions = load_records(_resolve_io_path(args.decisions), Decision)
    actions   = load_records(_resolve_io_path(args.actions), ActionItem)
    risks     = load_records(_resolve_io_path(args.risks), RiskItem)

    # Artifact Generation
    agenda = agenda_md(args.title, today, decisions, actions, risks, 7)
    followup = followup_md(args.title, today)

    # File Writing
    for content, filename in [(agenda, args.out_agenda), (followup, args.out_followup)]:
        out_path = _resolve_io_path(filename)
        out_path.parent.mkdir(parents=True, exist_ok=True) 
        out_path.write_text(content, encoding="utf-8")
        print(f"--- SUCCESS: Created {out_path.name} ---")

if __name__ == "__main__":
    main()