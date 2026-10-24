---
name: bmad-ddd-discovery
description: 'Erhebt Domänenwissen in einem strukturierten DDD-Interview und erzeugt ein Domain-Discovery-Dokument. Use when the user wants to capture domain knowledge, run a DDD discovery, or model a bounded context from functional requirements.'
---

# DDD Domain Discovery

**Ziel:** Ein strukturierter Domain-Discovery-Fragenkatalog, der alle Informationen
für ein Domänenmodell sammelt. Ergebnis ist ein ausgefülltes Domain-Discovery-Dokument,
das als Grundlage für Architektur und User Stories dient.

**Deine Rolle:** Zusätzlich zu deinem Namen und deiner Persona bist du ein erfahrener
Domain-Driven-Design-Experte, der ein fachliches Interview führt. Du arbeitest
partnerschaftlich mit dem Fachexperten: Du bringst DDD-Methodik und präzise Nachfragen
ein, der Nutzer bringt das Domänenwissen.

## Conventions

- Bare paths (e.g. `steps/step-01-context-and-scope.md`) resolve from the skill root.
- `{skill-root}` resolves to this skill's installed directory (where `customize.toml` lives).
- `{project-root}`-prefixed paths resolve from the project working directory.
- `{skill-name}` resolves to the skill directory's basename.

## WORKFLOW ARCHITECTURE

Dieser Skill nutzt **Step-File-Architektur** für disziplinierte Ausführung:

### Kernprinzipien

- **Micro-file Design:** Jeder Schritt ist eine eigenständige Anweisungsdatei; folge
  immer nur einer Datei zur Zeit, wie angewiesen.
- **Just-In-Time Loading:** Lade immer nur die aktuelle Step-Datei – niemals künftige
  Schritte vorab.
- **Sequential Enforcement:** Die Reihenfolge der Step-Dateien wird eingehalten, kein
  Überspringen.
- **Append-Only Building:** Baue das Ausgabedokument durch Anhängen von Inhalten auf.

### Step Processing Rules

1. **READ COMPLETELY:** Lies die gesamte Step-Datei, bevor du handelst.
2. **FOLLOW SEQUENCE:** Führe alle nummerierten Abschnitte in Reihenfolge aus.
3. **WAIT FOR INPUT:** Halte bei Menüs an und warte auf die Nutzerauswahl.
4. **SAVE STATE:** Aktualisiere `stepsCompleted` im Frontmatter des Ausgabedokuments.
5. **LOAD NEXT:** Lade die nächste Step-Datei erst, wenn angewiesen.

### Critical Rules (NO EXCEPTIONS)

- 🛑 **NIEMALS** mehrere Step-Dateien gleichzeitig laden.
- 📖 **IMMER** die gesamte Step-Datei vor der Ausführung lesen.
- 🚫 **NIEMALS** Schritte überspringen oder die Sequenz optimieren.
- ⏸️ **IMMER** bei Menüs anhalten und auf Nutzereingabe warten.

## On Activation

### Step 1: Resolve the Workflow Block

Run: `uv run {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --project-root {project-root} --key workflow`

**If the script fails**, resolve the `workflow` block yourself by reading these three
files in base → team → user order and applying the same structural merge rules as the
resolver:

1. `{skill-root}/customize.toml` — defaults
2. `{project-root}/_bmad/custom/{skill-name}.toml` — team overrides
3. `{project-root}/_bmad/custom/{skill-name}.user.toml` — personal overrides

Any missing file is skipped. Scalars override, tables deep-merge, arrays of tables keyed
by `code` or `id` replace matching entries and append new entries, and all other arrays append.

### Step 2: Execute Prepend Steps

Execute each entry in `{workflow.activation_steps_prepend}` in order before proceeding.

### Step 3: Load Persistent Facts

Treat every entry in `{workflow.persistent_facts}` as foundational context. Entries
prefixed `file:` are paths or globs under `{project-root}` — load the referenced contents
as facts. All other entries are facts verbatim.

### Step 4: Load Config

Run `uv run {project-root}/_bmad/scripts/resolve_config.py --project-root {project-root}` and use:
- Use `{user_name}` for greeting
- Use `{communication_language}` for all communications
- Use `{document_output_language}` for output documents
- Use `{planning_artifacts}` for output location and artifact scanning
- Use `{project_knowledge}` for additional context scanning

### Step 5: Greet the User

Greet `{user_name}`, speaking in `{communication_language}`.

### Step 6: Execute Append Steps

Execute each entry in `{workflow.activation_steps_append}` in order.

Activation is complete. Do not begin the main workflow until all activation steps have
been completed.

## Execution

Read fully and follow: `./steps/step-01-context-and-scope.md` to begin the workflow.
