#!/usr/bin/env python3
"""Render the custom DDD module into the IDE skill trees.

Source of truth : _bmad/custom/ddd/
Targets         : .agents/skills/, .claude/skills/, .github/agents/,
                  _bmad/_config/skill-manifest.csv, _bmad/_config/bmad-help.csv

Idempotent: safe to re-run after a BMAD install/update to re-apply the custom
DDD agent and skills into the installer-managed trees.

Usage:
    python _bmad/custom/ddd/render-ddd.py
    python _bmad/custom/ddd/render-ddd.py --check   # verify only, no writes
"""
from __future__ import annotations

import csv
import io
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC = PROJECT_ROOT / "_bmad" / "custom" / "ddd"
IDE_TREES = [
    PROJECT_ROOT / ".agents" / "skills",
    PROJECT_ROOT / ".claude" / "skills",
]
GITHUB_AGENTS = PROJECT_ROOT / ".github" / "agents"
SKILL_MANIFEST = PROJECT_ROOT / "_bmad" / "_config" / "skill-manifest.csv"
HELP_MANIFEST = PROJECT_ROOT / "_bmad" / "_config" / "bmad-help.csv"

# (source directory, rendered skill-folder name, kind)
UNITS = [
    (SRC / "agents" / "bmad-agent-ddd", "bmad-agent-ddd", "agent"),
    (SRC / "skills" / "bmad-ddd-discovery", "bmad-ddd-discovery", "skill"),
    (SRC / "skills" / "bmad-ddd-validation", "bmad-ddd-validation", "skill"),
]

AGENT_DESC = (
    "Domain-Driven Design expert and domain modeler. Use when the user asks to "
    "talk to Domino or requests the DDD expert / domain modeler."
)
DISCOVERY_DESC = (
    "Erhebt Domaenenwissen in einem strukturierten DDD-Interview und erzeugt ein "
    "Domain-Discovery-Dokument."
)
VALIDATION_DESC = (
    "Prueft bestehende DDD-Dokumente auf Konsistenz und DDD-Konformitaet in einem "
    "strukturierten Frage-Antwort-Dialog und verfeinert sie."
)

SKILL_MANIFEST_ROWS = [
    ("bmad-agent-ddd", "bmad-agent-ddd", AGENT_DESC, "custom",
     "_bmad/custom/ddd/agents/bmad-agent-ddd/SKILL.md"),
    ("bmad-ddd-discovery", "bmad-ddd-discovery", DISCOVERY_DESC, "custom",
     "_bmad/custom/ddd/skills/bmad-ddd-discovery/SKILL.md"),
    ("bmad-ddd-validation", "bmad-ddd-validation", VALIDATION_DESC, "custom",
     "_bmad/custom/ddd/skills/bmad-ddd-validation/SKILL.md"),
]

HELP_ROWS = [
    ("DDD (custom)", "bmad-ddd-discovery", "DDD Domain Discovery", "DD",
     DISCOVERY_DESC, "", "", "plan", "", "bmad-ddd-validation", "false",
     "planning_artifacts", "domain discovery"),
    ("DDD (custom)", "bmad-ddd-validation", "DDD Validation", "DV",
     VALIDATION_DESC, "", "", "plan", "bmad-ddd-discovery", "", "false",
     "planning_artifacts", "validated domain docs"),
]

FORWARDER = """---
description: {desc}
---

LOAD the FULL {{project-root}}/.agents/skills/bmad-agent-ddd/SKILL.md, READ its entire contents and follow its directions exactly!
"""


def log(msg: str) -> None:
    print(f"[render-ddd] {msg}")


def copy_units(check: bool) -> list[str]:
    problems: list[str] = []
    for src_dir, folder, _kind in UNITS:
        if not src_dir.is_dir():
            problems.append(f"missing source: {src_dir}")
            continue
        for tree in IDE_TREES:
            dest = tree / folder
            if check:
                if not (dest / "SKILL.md").is_file():
                    problems.append(f"missing rendered skill: {dest}")
                continue
            if dest.exists():
                shutil.rmtree(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src_dir, dest)
            log(f"rendered {folder} -> {dest}")
    return problems


def write_forwarder(check: bool) -> list[str]:
    target = GITHUB_AGENTS / "bmad-agent-ddd.agent.md"
    content = FORWARDER.format(desc=AGENT_DESC)
    if check:
        if not target.is_file():
            return [f"missing forwarder: {target}"]
        return []
    GITHUB_AGENTS.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    log(f"wrote forwarder -> {target}")
    return []


def ensure_csv_rows(path: Path, key_cols: tuple[int, ...], rows: list[tuple],
                    check: bool) -> list[str]:
    if not path.is_file():
        return [f"missing manifest: {path}"]
    with path.open(newline="", encoding="utf-8") as fh:
        existing = list(csv.reader(fh))
    if not existing:
        return [f"empty manifest: {path}"]
    header, body = existing[0], existing[1:]
    present = {tuple(r[i] for i in key_cols) for r in body if len(r) > max(key_cols)}
    missing = [r for r in rows if tuple(r[i] for i in key_cols) not in present]
    if check:
        if missing:
            return [f"missing {len(missing)} row(s) in {path.name}"]
        return []
    if not missing:
        log(f"{path.name}: all rows present")
        return []
    text = path.read_text(encoding="utf-8")
    needs_newline = bool(text) and not text.endswith("\n")
    buf = io.StringIO()
    writer = csv.writer(buf, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    for r in missing:
        writer.writerow(r)
    with path.open("a", newline="", encoding="utf-8") as fh:
        if needs_newline:
            fh.write("\n")
        fh.write(buf.getvalue())
    log(f"{path.name}: appended {len(missing)} row(s)")
    return []


def main() -> int:
    check = "--check" in sys.argv
    problems: list[str] = []
    problems += copy_units(check)
    problems += write_forwarder(check)
    problems += ensure_csv_rows(SKILL_MANIFEST, (0,), SKILL_MANIFEST_ROWS, check)
    problems += ensure_csv_rows(HELP_MANIFEST, (0, 1), HELP_ROWS, check)

    if problems:
        log("PROBLEMS:")
        for p in problems:
            log(f"  - {p}")
        return 1
    log("check OK" if check else "render complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
