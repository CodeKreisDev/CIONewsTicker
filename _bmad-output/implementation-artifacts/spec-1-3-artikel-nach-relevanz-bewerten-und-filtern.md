---
title: 'Artikel nach Relevanz bewerten und filtern'
type: 'feature'
created: '10-24-2026'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
context: []
baseline_commit: 'a783a2e59f1884362517623be30e81a367c769d1'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Eingegangene Artikel (Zustand EINGEGANGEN) werden bisher nicht
nach Relevanz bewertet; ohne Bewertung und Filterung kann keine Synthese
(Story 1.4) entscheiden, welche Artikel in das Briefing gehören.

**Approach:** Ein `ScoringService` (Application) liest alle EINGEGANGEN-Artikel,
bewertet jeden über ein `LLMPort`-Interface (AD-6) mit einem `RelevanzScore`
(1–10), und verwirft Artikel mit Score < 7. Das `Artikel`-Aggregate bekommt
die Zustandsübergänge `bewerte()` (→ BEWERTET) und `verwerfen()` (→ VERWORFEN,
nur erlaubt wenn nicht relevant — R1 als Aggregat-Invariante). Ein
LLM-Fehlschlag bei einem einzelnen Artikel blockiert nicht die Bewertung der
übrigen Artikel.

## Boundaries & Constraints

**Always:** `RelevanzScore` validiert den Wertebereich 1–10 im Konstruktor
(Fail-Fast, ddd-principles.md). `Artikel.verwerfen()` erzwingt R1 selbst (wirft
bei Score ≥ 7) statt dem Aufrufer zu vertrauen. Domain-Schicht bleibt frei von
Infrastruktur-Importen (AD-1, von `test_architecture_boundaries.py` geprüft).
LLM-Zugriff ausschließlich über `LLMPort` (AD-6); konkreter Provider ist
austauschbar. Code/Kommentare: Englisch (Sprachkonvention aus Story 1.1).
Domänen-spezifische Exceptions statt generischer (ddd-principles.md).

**Never:** Keine Synthese/Top-5-Auswahl oder Kategorisierung (folgt in 1.4).
Kein echter, netzwerkbasierter LLM-Aufruf in Tests — nur Fakes/gemockte
Clients. Kein Entfernen von Artikeln aus dem Repository — Verwerfen ist ein
Zustandswechsel, keine Löschung (Nachvollziehbarkeit).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|-----------------|
| Score ≥ 7 | EINGEGANGEN-Artikel, LLM liefert Score 8 | Zustand BEWERTET, bleibt Kandidat | N/A |
| Score < 7 | EINGEGANGEN-Artikel, LLM liefert Score 4 | Zustand BEWERTET → VERWORFEN | N/A |
| LLM nicht erreichbar für einen Artikel | LLM-Aufruf wirft Fehler | Artikel bleibt EINGEGANGEN, übrige Artikel trotzdem bewertet | `LLMNichtErreichbarError` abgefangen, Verarbeitung läuft weiter |
| LLM liefert keinen gültigen Score (z. B. Text statt Zahl) | Antwort nicht als 1–10 parsebar | Artikel bleibt EINGEGANGEN wie bei Nichterreichbarkeit | `LLMAntwortUngueltigError` abgefangen, Verarbeitung läuft weiter |

</frozen-after-approval>

## Code Map

- `src/cio_info_agent/domain/exception/domain_exception.py` -- neu: gemeinsame
  `DomainException`-Basis (nur übergreifend, ddd-principles.md-Konvention)
- `src/cio_info_agent/domain/artikel/relevanz_score.py` -- neu: `RelevanzScore`
  (frozen dataclass), validiert 1–10 im Konstruktor, `ist_relevant()` (≥7, Schwellenwert als Konstante)
- `src/cio_info_agent/domain/artikel/exception/ungueltiger_zustandsuebergang_error.py`
  -- neu: aggregat-spezifische Exception für unerlaubte Zustandsübergänge
- `src/cio_info_agent/domain/artikel/artikel.py` -- ändern: neues Feld
  `relevanz_score: RelevanzScore | None = None`; neue Methoden `bewerte(score)`
  (EINGEGANGEN→BEWERTET) und `verwerfen()` (BEWERTET→VERWORFEN, erzwingt
  Score < 7 selbst)
- `src/cio_info_agent/application/ports/llm_port.py` -- neu: `LLMPort`-Protocol
  (`bewerte_relevanz(titel, beschreibung) -> int`), `LLMNichtErreichbarError`,
  `LLMAntwortUngueltigError`
- `src/cio_info_agent/application/ports/artikel_repository_port.py` -- ändern:
  `lies_alle_mit_status(status)` und `aktualisiere(artikel)` ergänzen
- `src/cio_info_agent/application/services/scoring_service.py` -- neu:
  `ScoringErgebnis` (Zähler bewertet/verworfen/fehlgeschlagen),
  `ScoringService.bewerte_und_filtere_alle()`
- `src/cio_info_agent/infrastructure/persistence/artikel_repository.py` --
  ändern: `lies_alle_mit_status` (SELECT by status) und `aktualisiere` (UPDATE
  by id, inkl. `relevanz_score`-Spalte) implementieren; Schema um Spalte
  `relevanz_score` (nullable INTEGER) erweitern
- `src/cio_info_agent/infrastructure/llm/openai_llm_adapter.py` -- neu:
  `LLMPort`-Implementierung via `openai`-SDK, Modell `gpt-5.6-luna` (Default,
  Architecture-Spine-Empfehlung), Prompt mit CIO-Immobilien-Persona, robustes
  Parsing der Zahl 1–10 aus der Antwort
- `pyproject.toml` -- ändern: Abhängigkeit `openai` ergänzen
- `tests/test_relevanz_score.py`, `tests/test_artikel_bewerten.py`,
  `tests/test_scoring_service.py`, `tests/test_openai_llm_adapter.py` -- neu

## Tasks & Acceptance

**Execution:**
- [x] `src/cio_info_agent/domain/exception/domain_exception.py` -- gemeinsame Basis-Exception -- erfüllt ddd-principles.md
- [x] `src/cio_info_agent/domain/artikel/relevanz_score.py` -- `RelevanzScore`-VO mit Wertebereichsprüfung -- erfüllt FR3
- [x] `src/cio_info_agent/domain/artikel/exception/ungueltiger_zustandsuebergang_error.py` -- aggregat-spezifische Exception
- [x] `src/cio_info_agent/domain/artikel/artikel.py` -- `bewerte()`/`verwerfen()` mit erzwungener R1-Invariante -- erfüllt FR3, FR4
- [x] `src/cio_info_agent/application/ports/llm_port.py` -- `LLMPort`-Protocol -- erzwingt AD-6
- [x] `src/cio_info_agent/application/ports/artikel_repository_port.py` -- Repository-Port erweitert
- [x] `src/cio_info_agent/application/services/scoring_service.py` -- Orchestrierung, Pro-Artikel-Fehlertoleranz -- erfüllt FR3, FR4
- [x] `src/cio_info_agent/infrastructure/persistence/artikel_repository.py` -- Schema-Erweiterung + neue Methoden
- [x] `src/cio_info_agent/infrastructure/llm/openai_llm_adapter.py` -- echte Provider-Implementierung
- [x] `pyproject.toml` -- `openai`-Abhängigkeit
- [x] `tests/test_relevanz_score.py` -- Wertebereich 1–10, Grenzfälle, `ist_relevant()`
- [x] `tests/test_artikel_bewerten.py` -- Zustandsübergänge, R1-Invariante wird vom Aggregate erzwungen
- [x] `tests/test_scoring_service.py` -- Fake-LLM/-Repository: Score≥7 bleibt Kandidat, Score<7 wird verworfen, LLM-Fehlschlag blockiert nicht die übrigen Artikel
- [x] `tests/test_openai_llm_adapter.py` -- gemockter Client: Prompt-Konstruktion, Parsing gültiger/ungültiger Antworten, Fehler-Wrapping

**Acceptance Criteria:**
- Given ein Artikel im Zustand EINGEGANGEN, when die Bewertung läuft, then erhält er einen Relevanz-Score zwischen 1 und 10 und wechselt zu BEWERTET (FR3)
- Given ein bewerteter Artikel mit Score < 7, when die Filterung läuft, then wechselt er zu VERWORFEN und erscheint nie im Briefing (FR4)
- Given ein bewerteter Artikel mit Score ≥ 7, when die Filterung läuft, then bleibt er Kandidat (Zustand BEWERTET)
- Given die Bewertung eines Artikels schlägt fehl (LLM nicht erreichbar oder ungültige Antwort), when der Lauf weiterläuft, then werden die übrigen Artikel trotzdem bewertet

## Implementation Notes

**Review-Runde 1 (Patches angewendet, siehe Review Triage Log):**
- `OpenAILLMAdapter`: leere `choices`-Liste löst jetzt `LLMAntwortUngueltigError` statt eines ungeschützten `IndexError` aus, der zuvor den gesamten Scoring-Lauf für alle Artikel abgebrochen hätte (analog zum entsprechenden Fund aus Story 1.2).
- `OpenAILLMAdapter`: Zahlenerkennung überarbeitet (`_SKALA_PATTERN`/`_ZAHL_PATTERN` mit Lookaround) — erkennt jetzt "X/10" gezielt, lehnt Dezimalzahlen (z. B. „7.5") ab statt sie stillschweigend zu kürzen, und verwechselt eingebettete fremde Ziffern (z. B. „GPT-4") nicht mehr mit dem eigentlichen Score.
- `RelevanzScore` wirft jetzt die domänenspezifische `UngueltigerRelevanzScoreError` (Unterklasse von `DomainException`) statt eines generischen `ValueError` — konsistent mit der ddd-principles.md-Konvention.
- `ScoringService`: nur noch ein `aktualisiere()`-Aufruf pro Artikel (vorher zwei beim Verwerfen); Catch-Klausel präzisiert auf die tatsächlich erwarteten Fehlertypen statt eines breiten `ValueError`.
- `ArtikelRepository.aktualisiere` erzwingt jetzt Fail-Fast (wirft `ValueError`), wenn die Artikel-ID nicht existiert, statt still zu No-Op'en.
- Testlücken geschlossen: echter SQLite-Round-Trip für `aktualisiere`/`lies_alle_mit_status` inkl. `beschreibung`/`relevanz_score`; `FeedparserAdapter`-Beschreibungs-Extraktion; `IngestionService`-Beschreibung-Propagation.
- Gesamte Testsuite nach Patches: `uv run pytest -v` → **81 passed** (36 neue + 45 aus Story 1.1/1.2).
- Drei Punkte bewusst zurückgestellt → `deferred-work.md`: Schema-Migrationsstrategie vor echtem Produktivbetrieb, Retry-Limit/Dead-Letter für dauerhaft fehlschlagende Artikel, Optimistic-Concurrency-Control für `aktualisiere()` bei echtem Mehrprozess-Zugriff.
- Zwei Funde als **false** zurückgewiesen: `uv.lock` war bereits korrekt synchronisiert (nur aus dem Review-Diff ausgeschlossen, um Lock-File-Rauschen zu vermeiden); keine Stray-Blank-Line in `artikel_repository_port.py`.

## Spec Change Log

## Review Triage Log

**Review-Layer:** Blind Hunter (10 Funde), Edge Case Hunter (6 Funde, JSON), Verification Gap (3 ausführliche Funde + 1 Notiz).

| # | Fund (Quelle) | Verdikt | Begründung |
|---|----------------|---------|------------|
| 1 | Leere `choices`-Liste führt zu ungeschütztem `IndexError`, der den gesamten Lauf crasht (Edge Case Hunter, als „claim" gegen FR3/FR4-Resilienz verifiziert) | **high** | Verifiziert: `antwort.choices[0]` lag außerhalb jeder Fehlerbehandlung. Realistischer Trigger (z. B. OpenAI Content-Filtering liefert leere `choices`). Direktes Analogon zum entsprechenden Fund aus Story 1.2. Behoben durch expliziten Guard. |
| 2 | Zahlenerkennung per `\d+` matcht die erste Ziffernfolge irgendwo im Text, nicht „die erste eigenständige Zahl" wie im Kommentar behauptet; Dezimalzahlen werden still gekürzt (Blind Hunter + Edge Case Hunter, konvergierend) | **medium** | Verifiziert und empirisch mit einem neuen Test nachgewiesen (`"GPT-4 rates this 9/10"` hätte fälschlich „4" statt „9" extrahiert). Behoben durch Lookaround-Pattern mit expliziter „X/10"-Erkennung und Dezimal-Ablehnung. |
| 3 | `RelevanzScore` wirft generischen `ValueError` statt einer `DomainException`-Unterklasse, entgegen der im Projekt dokumentierten Konvention (Edge Case Hunter, hohe Konfidenz, zitiert die eigene Docstring-Konvention) | **medium** | Verifiziert gegen `domain_exception.py`: die Ausnahme dort ist explizit nur für Artikels Zeitzonen-Prüfung vorgesehen, nicht für `RelevanzScore`. Neue `UngueltigerRelevanzScoreError` ergänzt. |
| 4 | `ScoringService`: zwei `aktualisiere()`-Aufrufe pro verworfenem Artikel statt einem (Blind Hunter + Verification Gap, konvergierend) | **low** | Verifiziert, funktional unschädlich aber unnötiger Doppel-Write. Behoben durch Umstrukturierung auf genau einen Aufruf pro Zweig. |
| 5 | `except (..., ValueError)` in `ScoringService` zu breit — hätte unbeabsichtigt fremde `ValueError`s verschluckt (Blind Hunter) | **medium** | Verifiziert. Durch Fund #3 (neue spezifische Exception) gleichzeitig behoben: Catch-Klausel jetzt auf `UngueltigerRelevanzScoreError` statt generischem `ValueError` präzisiert. |
| 6 | `ArtikelRepository.aktualisiere` führt ein blindes UPDATE ohne Existenzprüfung aus — No-Op bei nicht existierender ID bleibt unbemerkt (Blind Hunter) | **medium** | Verifiziert. Behoben durch `rowcount`-Prüfung mit Fail-Fast `ValueError`. |
| 7 | Schema-Erweiterung (`CREATE TABLE IF NOT EXISTS`) migriert keine bereits bestehende Datenbank (Blind Hunter) | **defer** | Verifiziert als reales Architektur-Thema, aber ohne aktuellen Schaden: Es existiert noch keine echte Produktivbereitstellung dieses Systems. Zurückgestellt bis vor dem ersten echten Deployment. |
| 8 | Fehlende SQLite-Integrationstests für `aktualisiere`/`lies_alle_mit_status` sowie für `beschreibung`-Extraktion/-Propagation (Verification Gap, 3 Funde + Blind Hunter #9/#10, konvergierend) | **medium** | Verifiziert — alle vier Lücken bestätigt durch Code-/Test-Lektüre. Alle vier Tests ergänzt und grün. |
| 9 | Kein Retry-Limit/Dead-Letter für dauerhaft fehlschlagende Artikel — bleibt für immer `EINGEGANGEN`, wird bei jedem Lauf erneut (kostenpflichtig) angefragt (Blind Hunter) | **defer** | Reale Betriebsfrage, aber eigenständiges Scope (Retry-/Circuit-Breaker-Policy), über diese Story hinausgehend. Zurückgestellt. |
| 10 | Kein Schutz vor gleichzeitigem Update durch einen künftigen parallelen Prozess (Optimistic Concurrency Control) bei `aktualisiere` (Edge Case Hunter, als „claim" gegen AD-5 geprüft) | **defer** | Verifiziert als reale Lücke, aber aktuell ohne Angreifer: Es existiert noch kein zweiter Prozess, der `Artikel` schreibt (Telegram-Listener noch nicht verdrahtet). Volle Optimistic-Concurrency-Control wäre an dieser Stelle spekulativer Mehraufwand ohne aktuellen Bedarf (Rule of Three). Die einfachere, bereits behobene Lücke (#6, Existenzprüfung) deckt den realistischeren Fehlerfall ab. |
| 11 | `uv.lock` sei nicht Teil des Diffs (Blind Hunter) | **false** | Widerlegt: `uv.lock` war korrekt gestaged und committed; lediglich aus dem an die Reviewer übergebenen Diff bewusst ausgeschlossen, um Lock-File-Rauschen zu vermeiden. |
| 12 | Angebliche Stray-Leerzeile in `artikel_repository_port.py` (Blind Hunter) | **false** | Widerlegt: Datei direkt geprüft, keine überzählige Leerzeile gefunden. |

## Design Notes

- **Neues Feld `beschreibung` auf `FeedEintrag`/`Artikel`:** RSS-`<description>`
  wird von `feedparser` bereits automatisch geparst und verbessert die
  Scoring-Qualität erheblich gegenüber reinem Titel-Scoring, ohne zusätzliche
  Komplexität. Wird als optionales Feld nachgezogen (kein Bruch bestehender
  Aufrufer, da mit Default `""`).
- `RelevanzScore.ist_relevant()` kapselt den Schwellenwert 7 (R1) als
  Domänenwissen im Value Object statt als magische Zahl im Application-Code.
- `Artikel.verwerfen()` erzwingt die Invariante R1 selbst (wirft
  `UngueltigerZustandsuebergangError`, wenn Score ≥ 7): ein Aufrufer kann die
  Regel nicht versehentlich umgehen, selbst wenn er es versucht.
- LLM-Fehlerresilienz pro Artikel (nicht nur pro Quelle wie in FR1) ist eine
  bewusste Erweiterung des Robustheits-Prinzips (NFR5) auf den Scoring-Schritt
  -- ein einzelner API-Fehler/eine einzelne Fehlantwort darf nicht den
  gesamten Lauf gefährden.
- Modellwahl `gpt-5.6-luna` folgt der in der Architecture Spine (AD-6)
  dokumentierten Kostenempfehlung; austauschbar ohne Code-Änderung außerhalb
  von `infrastructure/llm/`.
- Tests gegen den OpenAI-Adapter mocken den SDK-Client vollständig (keine
  Netzwerkabhängigkeit, kein API-Key nötig, kein Kostenanfall) -- konsistent
  mit der bereits etablierten Teststrategie aus Story 1.2.

## Verification

**Commands:**
- `uv run pytest -v` -- expected: alle Tests grün (0 Failures), inkl. der
  bestehenden 45 Tests aus Story 1.1/1.2
