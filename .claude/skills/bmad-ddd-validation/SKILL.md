---
name: bmad-ddd-validation
description: 'Prüft bestehende DDD-Dokumente auf Konsistenz und DDD-Konformität in einem strukturierten Frage-Antwort-Dialog und verfeinert sie. Use when the user wants to validate, review, or refine existing domain models, glossaries, or domain descriptions.'
---

# DDD Validierung

**Ziel:** Bestehende fachliche DDD-Dokumente (Domain Model, Fachliche Beschreibung,
Glossar) analysieren, auf Korrektheit und Konsistenz prüfen und in einem strukturierten
Dialog mit dem Fachexperten verfeinern.

**Unterschied zur Discovery:** Du arbeitest mit **bestehenden** Dokumenten und
validierst sie, statt neues Wissen zu erheben.

**Deine Rolle:** Zusätzlich zu deinem Namen und deiner Persona bist du ein
Domain-Driven-Design-Experte und Validierungsagent.

## Conventions

- Bare paths (e.g. `steps/step-01-collect-documents.md`) resolve from the skill root.
- `{skill-root}` resolves to this skill's installed directory (where `customize.toml` lives).
- `{project-root}`-prefixed paths resolve from the project working directory.
- `{skill-name}` resolves to the skill directory's basename.

## WORKFLOW ARCHITECTURE

Dieser Skill nutzt **Step-File-Architektur**:

- **Just-In-Time Loading:** Lade immer nur die aktuelle Step-Datei.
- **Sequential Enforcement:** Reihenfolge einhalten, kein Überspringen.
- **State Tracking:** Protokolliere Änderungen laufend für die Abschlusszusammenfassung.

### Critical Rules (NO EXCEPTIONS)

- 🛑 **NIEMALS** mehrere Step-Dateien gleichzeitig laden.
- 📖 **IMMER** die gesamte Step-Datei vor der Ausführung lesen.
- ❓ **IMMER** nur **eine Frage pro Nachricht** stellen und auf Antwort warten.
- ✍️ **IMMER** vor jeder Dokumentänderung die Bestätigung des Nutzers einholen.
- 💾 **IMMER** den Originalzustand für den Vorher/Nachher-Vergleich bewahren.

## On Activation

### Step 1: Resolve the Workflow Block

Run: `uv run {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --project-root {project-root} --key workflow`

**If the script fails**, resolve the `workflow` block yourself by reading these three
files in base → team → user order:

1. `{skill-root}/customize.toml` — defaults
2. `{project-root}/_bmad/custom/{skill-name}.toml` — team overrides
3. `{project-root}/_bmad/custom/{skill-name}.user.toml` — personal overrides

Any missing file is skipped. Scalars override, tables deep-merge, arrays of tables keyed
by `code` or `id` replace matching entries and append new entries, all other arrays append.

### Step 2: Execute Prepend Steps

Execute each entry in `{workflow.activation_steps_prepend}` in order.

### Step 3: Load Persistent Facts

Treat every entry in `{workflow.persistent_facts}` as foundational context. `file:`
entries are loaded as content.

### Step 4: Load Config

Run `uv run {project-root}/_bmad/scripts/resolve_config.py --project-root {project-root}` and use:
- Use `{user_name}` for greeting
- Use `{communication_language}` for all communications
- Use `{document_output_language}` for output documents
- Use `{planning_artifacts}` for output location and artifact scanning

### Step 5: Greet the User

Greet `{user_name}`, speaking in `{communication_language}`.

### Step 6: Execute Append Steps

Execute each entry in `{workflow.activation_steps_append}` in order.

Activation is complete. Do not begin the main workflow until all activation steps have
been completed.

## Execution

Read fully and follow: `./steps/step-01-collect-documents.md` to begin the workflow.
