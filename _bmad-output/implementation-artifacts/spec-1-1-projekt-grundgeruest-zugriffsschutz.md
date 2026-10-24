---
title: 'Projekt-Grundgerüst & Zugriffsschutz'
type: 'feature'
created: '10-24-2026'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
context: []
baseline_commit: '5fc99c0072ad654768b9d8bb59d118c1def07fb3'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Es gibt noch keinen Code. Der Bot braucht ein sauberes
Schichten-Grundgerüst gemäß Architektur-Spine, eine initialisierte
SQLite-Verbindung im WAL-Modus und eine Zugriffskontrolle, die ausschließlich auf
die konfigurierte Chat-ID reagiert, bevor fachliche Logik entsteht.

**Approach:** Python-Paket `cio_info_agent` im `src/`-Layout mit den vier Schichten
(`domain`/`application`/`infrastructure`/`interfaces`) anlegen. Konfiguration
ausschließlich über Umgebungsvariablen, eine SQLite-Verbindungsfabrik im WAL-Modus,
und eine Whitelist-Prüfung als reine Entscheidungsfunktion.

## Boundaries & Constraints

**Always:** Domain-Schicht bleibt frei von Infrastruktur-/Framework-Importen (AD-1);
Secrets ausschließlich aus Umgebungsvariablen, nie hartcodiert (AD-8); SQLite läuft
im WAL-Modus (AD-7); Whitelist-Prüfung ist eine eigenständige, testbare Funktion in
`interfaces/`.

**Never:** Keine Ingestion-/Scoring-/Synthese-Logik in dieser Story (folgt ab 1.2);
kein echtes Telegram-Long-Polling oder Scheduler-Wiring in dieser Story (die
Whitelist-Funktion ist pur und unabhängig testbar); keine Hartkodierung von Token
oder Chat-ID.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|-----------------|
| Whitelisted | eingehende Chat-ID == konfigurierte Chat-ID | `is_whitelisted` liefert `True` | N/A |
| Nicht whitelisted | eingehende Chat-ID != konfigurierte Chat-ID | `is_whitelisted` liefert `False` | N/A |
| Fehlende Konfiguration | Pflicht-Umgebungsvariable beim Start nicht gesetzt | Start schlägt fehl | Klare Exception, kein stiller Fallback |

</frozen-after-approval>

## Code Map

- `pyproject.toml` -- neu: Paket `cio_info_agent`, Python ≥3.12, Abhängigkeiten
  `python-telegram-bot>=22.8`, `feedparser>=6.0.14`, `apscheduler>=3.11.3`,
  Dev-Abhängigkeit `pytest`
- `src/cio_info_agent/domain/__init__.py` -- neu, leeres Paket (AD-1 Schichtgrenze)
- `src/cio_info_agent/application/__init__.py` -- neu, leeres Paket
- `src/cio_info_agent/infrastructure/__init__.py`,
  `src/cio_info_agent/infrastructure/persistence/__init__.py` -- neu, leere Pakete
- `src/cio_info_agent/infrastructure/config.py` -- neu: `AppConfig`-Dataclass liest
  `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `LLM_API_KEY` aus Umgebungsvariablen
- `src/cio_info_agent/infrastructure/persistence/connection.py` -- neu:
  `create_connection(db_path)` öffnet SQLite, setzt `PRAGMA journal_mode=WAL`
- `src/cio_info_agent/interfaces/__init__.py`,
  `src/cio_info_agent/interfaces/telegram_bot/__init__.py` -- neu, leere Pakete
- `src/cio_info_agent/interfaces/telegram_bot/access_control.py` -- neu:
  `is_whitelisted(incoming_chat_id, configured_chat_id) -> bool`
- `tests/test_config.py`, `tests/test_connection.py`, `tests/test_access_control.py`
  -- neu

## Tasks & Acceptance

**Execution:**
- [x] `pyproject.toml` -- Paket, Python-Version, Laufzeit- und Dev-Abhängigkeiten anlegen -- fixiert die Laufzeitbasis gemäß Architektur-Spine (AD-3)
- [x] `src/cio_info_agent/{domain,application,infrastructure,interfaces}/__init__.py` -- Schichten-Skelett anlegen -- etabliert die Struktur für alle folgenden Stories (AD-1)
- [x] `src/cio_info_agent/infrastructure/config.py` -- `AppConfig` mit Fail-Fast bei fehlendem Pflichtwert -- erzwingt AD-8
- [x] `src/cio_info_agent/infrastructure/persistence/connection.py` -- `create_connection` mit WAL-Modus -- erfüllt AD-7
- [x] `src/cio_info_agent/interfaces/telegram_bot/access_control.py` -- `is_whitelisted` -- erfüllt FR10
- [x] `tests/test_config.py` -- Unit-Test: fehlende Pflichtvariable löst klare Exception aus
- [x] `tests/test_connection.py` -- Unit-Test: Verbindung hat WAL-Modus aktiv
- [x] `tests/test_access_control.py` -- Unit-Test: `is_whitelisted` exakt wahr nur bei Übereinstimmung

**Acceptance Criteria:**
- Given eine Nachricht von der konfigurierten, whitelisteten Chat-ID, when der Bot sie empfängt, then verarbeitet er sie weiter (FR10)
- Given eine Nachricht von einer anderen Chat-ID, when der Bot sie empfängt, then ignoriert er sie vollständig, ohne zu antworten (FR10)
- Given das Projekt wird gestartet, when der Prozess hochfährt, then ist die Schichtenstruktur angelegt und SQLite im WAL-Modus initialisiert (AD-3, AD-7)
- Given Telegram-Token oder LLM-Key fehlen als Umgebungsvariable, when die Konfiguration geladen wird, then schlägt der Start mit einer klaren Fehlermeldung fehl (AD-8)

## Implementation Notes

- `pyproject.toml` nutzt `hatchling` als Build-Backend für das `src/`-Layout.
- `AppConfig` ist als `frozen=True` Dataclass implementiert (Immutability, konsistent mit DDD-Prinzipien).
- `is_whitelisted` akzeptiert `str | int` und vergleicht über `str(...)`, damit Telegram-Chat-IDs unabhängig vom Eingabetyp korrekt verglichen werden.
- `.gitignore` um `.venv/`, `*.egg-info/`, `.pytest_cache/` und SQLite-WAL-Laufzeitdateien ergänzt.
- Verifiziert: `uv run pytest -q` → 9 passed (unabhängig durch den Build-Orchestrator erneut bestätigt).

**Review-Runde 1 (Patches angewendet, siehe Review Triage Log):**
- `AppConfig`-Felder tragen jetzt `field(repr=False)` — Secrets erscheinen nie in `repr()`/Logs/Tracebacks.
- `_require_env` lehnt jetzt auch Whitespace-only-Werte ab (`.strip()`-Prüfung).
- `MissingConfigError`-Meldung auf Englisch umgestellt (siehe neue Sprachkonvention unten).
- `create_connection` legt das übergeordnete Verzeichnis jetzt automatisch an und prüft das `PRAGMA journal_mode`-Ergebnis aktiv (neue `WalModeUnavailableError` bei Fehlschlag).
- `is_whitelisted` lehnt `None` für beide Argumente explizit ab (vorher hätte `None == None` fälschlich Zugriff gewährt).
- Neuer Test `tests/test_architecture_boundaries.py` erzwingt AD-1 (Domain frei von Infrastruktur-Importen) automatisiert.
- `README.md` (Projekt-Root) mit Setup-Anleitung und Umgebungsvariablen-Dokumentation ergänzt.
- Gesamte Testsuite nach Patches: `uv run pytest -v` → **24 passed**.
- BH-7 (Audit-Logging für Zugriffsentscheidungen) bewusst zurückgestellt → `deferred-work.md`, da außerhalb des Scopes dieser Story (pure Funktion, echter Handler fehlt noch).
- Sprachkonvention (Code → Englisch, CIO-seitiger Text → Deutsch) per Winston+Domino-Konsultation geklärt und in `ARCHITECTURE-SPINE.md` Consistency Conventions nachgetragen.

## Spec Change Log

## Review Triage Log

## Review Triage Log

**Review-Layer:** Blind Hunter (11 Funde), Edge Case Hunter (5 Funde, JSON), Verification Gap (keine Funde).

| # | Fund (Quelle) | Verdikt | Begründung |
|---|----------------|---------|------------|
| 1 | `AppConfig` Default-`__repr__` gibt Secrets im Klartext aus (BH) | **high** | Verifiziert: `@dataclass(frozen=True)` ohne `repr=False`-Felder — jeder `print(config)`/Traceback leakt Token/Key. Verletzt AD-8 sinngemäß (Secrets dürfen nicht geloggt werden). |
| 2 | `_require_env` akzeptiert Whitespace-only-Werte (`"   "`) als gültig (EC-1) | **medium** | Verifiziert: `if not value` prüft nicht `.strip()`. Verletzt ddd-principles.md ("leere oder sinnlose Werte werden abgelehnt"). |
| 3 | `create_connection` legt übergeordnetes Verzeichnis nicht an (BH) | **medium** | Verifiziert: `sqlite3.connect` wirft `OperationalError`, wenn das Datenverzeichnis beim ersten echten Produktionslauf noch nicht existiert. |
| 4 | `PRAGMA journal_mode=WAL`-Ergebnis wird nicht geprüft (BH, EC-3, dupliziert) | **low** | Verifiziert: Rückgabe wird verworfen. Seltener Trigger (nur bei Dateisystemen ohne WAL-Unterstützung), aber verletzt AD-7 still. |
| 5 | `sqlite3.connect`-Fehler nicht in eigene Exception gewrappt (EC-2) | **low → zurückgewiesen** | Durch Fix #3 (Verzeichnis anlegen) entfällt der realistische Haupttrigger; verbleibende Fälle (Rechte, Sperre) liefern bereits eine hinreichend klare `sqlite3.Error`. |
| 6 | `is_whitelisted` behandelt `None`/`None` als Übereinstimmung; Typumwandlungs-Randfälle ungetestet (BH-8 + verifizierte Ergänzung) | **medium** | Verifiziert durch Nachdenken: `str(None) == str(None)` → `True` — eine Zugriffskontrolle, die bei doppeltem `None` fälschlich Zugriff gewährt. |
| 7 | Leerstring-Zweig von `_require_env` ungetestet (BH-9) | **low** | Verifiziert: identischer Code-Pfad wie fehlende Variable, aber nicht separat durch einen Test abgedeckt. |
| 8 | Keine automatisierte Prüfung der Schichtengrenze (AD-1: Domain frei von Infrastruktur) (BH-11, Teil) | **medium** | Verifiziert: kein Test verhindert künftig einen versehentlichen Infrastruktur-Import in `domain/`. Jetzt, solange die Schicht leer ist, am einfachsten abzusichern. |
| 9 | Deutsch/Englisch-Mix: `MissingConfigError`-Meldung Deutsch, alles andere Englisch (BH-5) | **medium** | Verifiziert. Cross-cutting Konvention fehlte bisher im Projekt. Per Winston+Domino-Konsultation geklärt (siehe Design Notes) und in der Architecture Spine nachgetragen. |
| 10 | Kein README, keine Projektmetadaten (BH-10) | **low** | Verifiziert: fehlt vollständig. Jeder neue Mitwirkende trifft diese Lücke sofort beim Setup-Versuch. |
| 11 | Kein `[project.scripts]`-Entry-Point, keine `pytest`-ini-Optionen (BH-6) | **false** | Widerlegt: `uv run pytest` installiert das Paket per `uv sync` automatisch editable, Tests laufen nachweislich grün (9 passed). Ein Entry-Point ist für diese Story explizit out of scope (siehe Design Notes: kein echtes Long-Polling/Scheduler-Wiring). |
| 12 | Keine Logging-/Audit-Spur für `is_whitelisted`-Entscheidungen (BH-7) | **defer** | `is_whitelisted` ist bewusst als pure Funktion ohne Seiteneffekte spezifiziert (Design Notes). Logging gehört in den künftigen echten Message-Handler, nicht in diese Story. |
| 13 | Claim: AC impliziere bereits aktive Message-Filterung (EC-4) | **false** | AC beschreibt die Entscheidungsfunktion, nicht einen laufenden Listener — Scope bewusst auf diese Story begrenzt (Design Notes). |
| 14 | Claim: AC impliziere DB-Initialisierung beim Prozessstart (EC-5) | **false** | Gleiche Begründung wie #13 — Scheduler-/Prozess-Wiring ist explizit einer späteren Story vorbehalten. |

## Design Notes

- `src/`-Layout statt flachem Top-Level-Paket, um Importpfad-Fallstricke zu
  vermeiden -- Implementierungsdetail, konsistent mit AD-3.
- `pytest` als Testframework -- Standardwahl, passt zu "Boring Technology".
  BDD/Gherkin-Akzeptanztests sind sinnvoll ab der ersten Story mit sichtbarem
  Nutzerverhalten (z. B. 1.4/1.5), nicht in dieser rein infrastrukturellen Story.
- Diese Story verdrahtet absichtlich kein echtes Telegram-Long-Polling oder
  APScheduler-Jobs -- `is_whitelisted` ist eine pure Funktion, unabhängig testbar.
  Die echte Verdrahtung folgt mit den Stories, die eingehende Nachrichten bzw.
  Zustellung tatsächlich verarbeiten.
- **Sprachkonvention (per Party-Konsultation Winston + Domino, Review-Runde 1):**
  Code-Kommentare/Docstrings und interne/Ops-seitige Fehlermeldungen → Englisch
  (deutsche Domänen-Begriffe wie `Artikel`/`Briefing` bleiben als Bezeichner
  erlaubt). Nutzerseitiger Text, der tatsächlich an den CIO per Telegram geht
  (Briefing-Text, Deep-Dive-Antworten, "Kein Briefing heute") → Deutsch. In die
  Architecture Spine als Konvention übernommen.

## Verification

**Commands:**
- `uv run pytest` -- expected: alle Tests grün (0 Failures)
