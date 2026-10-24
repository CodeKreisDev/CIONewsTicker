---
title: 'Artikel aus RSS-Quellen einlesen'
type: 'feature'
created: '10-24-2026'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
context: []
baseline_commit: '89c3267ce2fab1c55a2355bde61df6584e576146'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Es gibt noch keinen Weg, Artikel aus den fünf definierten RSS-Quellen
einzulesen. Ohne Ingestion kann keine Bewertung, Synthese oder Zustellung
stattfinden (Epic-1-Abhängigkeit).

**Approach:** Ein `Artikel`-Aggregate (Domain), ein `IngestionService`
(Application) der alle fünf Quellen über ein `FeedPort`-Interface abfragt,
neue Artikel dedupliziert über eine deterministische ID speichert, und dabei
den Ausfall einzelner Quellen toleriert. Infrastruktur-Implementierungen:
`feedparser`-Adapter für den Feed-Zugriff, SQLite-Repository für die
Persistenz.

## Boundaries & Constraints

**Always:** Domain-Schicht (`Artikel`, `Quelle`, `ArtikelId`, `ArtikelStatus`)
bleibt frei von Infrastruktur-Importen (AD-1, durchgesetzt durch
`test_architecture_boundaries.py`). Repository- und Feed-Zugriff laufen
ausschließlich über Port-Interfaces in `application/ports/` (AD-6). Artikel-IDs
werden deterministisch aus (Quelle, Link) abgeleitet (Architecture Spine
Consistency Conventions). Der Ausfall einer Quelle darf die Verarbeitung der
übrigen Quellen nicht blockieren (FR1). Code-Kommentare/Docstrings und interne
Fehlermeldungen: Englisch (Sprachkonvention aus Story-1.1-Review).

**Never:** Keine LLM-Bewertung/Filterung in dieser Story (folgt in 1.3). Keine
Synthese/Zustellung (folgt in 1.4/1.5). Kein echter Scheduler-Trigger
(APScheduler-Wiring ist einer späteren Story vorbehalten — diese Story liefert
die aufrufbare Ingestion-Logik, nicht deren zeitgesteuerten Trigger). Keine
Deduplizierung über verschiedene Quellen hinweg (nur pro exakter
Quelle+Link-Kombination, per PRD-Assumption bereits entschieden).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|-----------------|
| Alle 5 Quellen liefern | 5 Quellen, je ≥1 neuer Eintrag | Alle neuen Artikel im Zustand EINGEGANGEN gespeichert | N/A |
| Eine Quelle nicht erreichbar | 1 von 5 Quellen liefert Fehler | Übrige 4 Quellen werden trotzdem vollständig verarbeitet; fehlgeschlagene Quelle wird im Ergebnis gemeldet | `FeedNichtErreichbarError` abgefangen, Verarbeitung läuft weiter |
| Bereits bekannter Artikel (gleiche Quelle+Link) | Artikel-ID existiert bereits im Repository | Kein erneutes Anlegen, kein Duplikat (FR2) | N/A |
| Feed-Eintrag ohne Veröffentlichungsdatum | Eintrag ohne `published_parsed` | Fällt auf den Eingangszeitpunkt zurück statt zu crashen | N/A |

</frozen-after-approval>

## Code Map

- `src/cio_info_agent/domain/artikel/quelle.py` -- neu: `Quelle(str, Enum)` mit
  exakt den 5 festen Quellen (CIO_COM, BSI, HAUFE_IMMOBILIEN, PROPMODO, BITKOM) --
  bildet Domino's "feste Konfiguration" als geschlossene Aufzählung ab
- `src/cio_info_agent/domain/artikel/artikel_status.py` -- neu: `ArtikelStatus`-Enum
  mit allen 5 Zuständen aus dem validierten Domänenmodell (EINGEGANGEN, BEWERTET,
  VERWORFEN, QUALIFIZIERT_NICHT_AUSGEWAEHLT, IM_BRIEFING) -- nur EINGEGANGEN wird
  in dieser Story erzeugt
- `src/cio_info_agent/domain/artikel/artikel_id.py` -- neu: `ArtikelId`
  (frozen dataclass), Factory `von_quelle_und_link(quelle, link)` berechnet
  deterministischen SHA-256-Hash
- `src/cio_info_agent/domain/artikel/artikel.py` -- neu: `Artikel`-Aggregate-Root
  mit Factory `eingegangen(...)`, read-only Properties, kein Setter
- `src/cio_info_agent/application/ports/feed_port.py` -- neu: `FeedEintrag`
  (frozen dataclass), `FeedNichtErreichbarError`, `FeedPort`-Protocol
- `src/cio_info_agent/application/ports/artikel_repository_port.py` -- neu:
  `ArtikelRepositoryPort`-Protocol (`existiert`, `speichere`)
- `src/cio_info_agent/application/services/ingestion_service.py` -- neu:
  `IngestionErgebnis` (frozen dataclass), `IngestionService.ingestiere_alle_quellen()`
  orchestriert alle 5 Quellen, fängt `FeedNichtErreichbarError` pro Quelle ab
- `src/cio_info_agent/infrastructure/feeds/quellen_konfiguration.py` -- neu:
  `QUELLEN_FEED_URLS: dict[Quelle, str]` -- verifizierte URLs (CIO.com, BSI
  CERT-Bund Security Advisories, Propmodo, Bitkom live per Web-Fetch bestätigt
  als valides RSS/XML am 2026-10-24; Haufe Immobilien **unverifiziert** --
  Kommentar im Code markiert dies explizit als vor Produktivbetrieb zu prüfen)
- `src/cio_info_agent/infrastructure/feeds/feedparser_adapter.py` -- neu:
  `FeedparserAdapter` implementiert `FeedPort` via `feedparser.parse(url)`;
  wirft `FeedNichtErreichbarError` bei Netzwerk-/Parse-Fehlern
  (`bozo`-Flag ohne Einträge, oder jede Exception während `parse()`)
- `src/cio_info_agent/infrastructure/persistence/artikel_repository.py` -- neu:
  SQLite-`ArtikelRepository` implementiert `ArtikelRepositoryPort`, legt Tabelle
  `artikel` per `CREATE TABLE IF NOT EXISTS` bei Konstruktion an
- `tests/test_artikel.py`, `tests/test_ingestion_service.py`,
  `tests/test_artikel_repository.py`, `tests/test_feedparser_adapter.py` -- neu

## Tasks & Acceptance

**Execution:**
- [x] `src/cio_info_agent/domain/artikel/quelle.py` -- `Quelle`-Enum -- feste Konfiguration laut Domänenmodell
- [x] `src/cio_info_agent/domain/artikel/artikel_status.py` -- `ArtikelStatus`-Enum -- vollständiges, bereits validiertes Zustandsmodell
- [x] `src/cio_info_agent/domain/artikel/artikel_id.py` -- `ArtikelId` mit deterministischer Ableitung -- erfüllt Dedup-Grundlage (FR2)
- [x] `src/cio_info_agent/domain/artikel/artikel.py` -- `Artikel`-Aggregate -- erfüllt FR1 (Entität im Zustand Eingegangen)
- [x] `src/cio_info_agent/application/ports/feed_port.py` -- `FeedPort`-Protocol -- erzwingt AD-6 (Port-Abstraktion)
- [x] `src/cio_info_agent/application/ports/artikel_repository_port.py` -- Repository-Port -- erzwingt AD-6
- [x] `src/cio_info_agent/application/services/ingestion_service.py` -- Orchestrierung über alle Quellen, Fehlertoleranz, Dedup -- erfüllt FR1, FR2
- [x] `src/cio_info_agent/infrastructure/feeds/quellen_konfiguration.py` -- echte, verifizierte Feed-URLs -- macht das System produktionsfähig
- [x] `src/cio_info_agent/infrastructure/feeds/feedparser_adapter.py` -- `FeedPort`-Implementierung -- erfüllt AD-6
- [x] `src/cio_info_agent/infrastructure/persistence/artikel_repository.py` -- SQLite-Repository -- erfüllt AD-7 (WAL via `create_connection`)
- [x] `tests/test_artikel.py` -- Unit-Tests: Factory, ID-Determinismus (gleiche Quelle+Link ⇒ gleiche ID; unterschiedliche Quelle/Link ⇒ unterschiedliche ID)
- [x] `tests/test_ingestion_service.py` -- Unit-Tests mit Fake-Port/-Repository: alle 5 Quellen, Teilausfall-Toleranz, Dedup über zwei Läufe
- [x] `tests/test_artikel_repository.py` -- Integrationstest gegen echtes SQLite (tmp_path): `speichere` + `existiert` Round-Trip
- [x] `tests/test_feedparser_adapter.py` -- Tests gegen eingebettete RSS-Fixture-Strings (kein Netzwerkzugriff): Erfolgsfall, fehlendes Datum, Parse-Fehler

**Acceptance Criteria:**
- Given die fünf definierten Quellen, when der Ingestion-Lauf (`ingestiere_alle_quellen`) ausgeführt wird, then werden alle fünf Feeds abgefragt (FR1)
- Given eine der fünf Quellen ist nicht erreichbar, when der Ingestion-Lauf läuft, then werden die übrigen Quellen trotzdem vollständig verarbeitet und die fehlgeschlagene Quelle im Ergebnis gemeldet (FR1, NFR5)
- Given ein neu gefundener Artikel, when er eingelesen wird, then wird er als `Artikel` im Zustand `EINGEGANGEN` gespeichert
- Given ein Artikel-Link, der bereits im Repository existiert, when er erneut im Feed erscheint, then wird er nicht erneut als neuer Artikel angelegt (FR2)

## Implementation Notes

**Review-Runde 1 (Patches angewendet, siehe Review Triage Log):**
- `IngestionService` überspringt jetzt defensiv Einträge ohne Link, bevor die `ArtikelId` berechnet wird (zusätzlich zur Filterung im Adapter).
- `FeedparserAdapter`: fehlender Link führt jetzt zum Überspringen des Eintrags statt zu `link=""` — verhindert ArtikelId-Kollisionen zwischen mehreren linklosen Einträgen derselben Quelle.
- `FeedparserAdapter`: Pro-Eintrag-Konvertierung (inkl. Datumsparsing) läuft jetzt fehlerisoliert — ein kaputtes Datum in einem Eintrag überspringt nur diesen Eintrag statt den gesamten Ingestion-Lauf über alle fünf Quellen crashen zu lassen.
- `FeedparserAdapter`: Netzwerk-Timeout (10s) über `socket.setdefaulttimeout` um den Parse-Aufruf, mit Wiederherstellung im `finally` — verhindert unbegrenztes Blockieren bei einer hängenden Quelle.
- `ArtikelRepository.speichere` fängt jetzt `sqlite3.IntegrityError` ab und behandelt einen doppelten Insert als No-Op — schützt vor einer Race Condition zwischen Batch- und künftigem Listener-Prozess (AD-5).
- `Artikel.__post_init__` validiert jetzt, dass beide Zeitstempel zeitzonenbewusst sind (Fail-Fast gemäß ddd-principles.md) — verhindert stilles UTC-Erraten bei naiven Datetimes.
- Kosmetik: ungenutzter `pytest`-Import in `test_ingestion_service.py` entfernt; `test_feedparser_adapter.py` nutzt jetzt `pytest.raises` statt Try/Except/Else.
- Gesamte Testsuite nach Patches: `uv run pytest -v` → **45 passed** (21 neue Tests + 24 aus Story 1.1).
- Drei Punkte bewusst zurückgestellt → `deferred-work.md`: operatives Logging für fehlgeschlagene Quellen (bereits als PRD-Open-Question/Architektur-Deferred-Item geführt), konfigurierbare Feed-URLs ohne Code-Änderung, DB-Index auf `status`/`quelle` (verfrüht ohne bestehenden Query-Bedarf).
- Cross-Source-Deduplizierung (dieselbe Meldung von zwei Quellen zählt als zwei Artikel) ist kein neuer Fund, sondern eine bereits im PRD getroffene, bewusste Entscheidung (siehe Boundaries & Constraints dieser Spec).

## Spec Change Log

## Review Triage Log

**Review-Layer:** Blind Hunter (12 Funde), Edge Case Hunter (3 Funde, JSON), Verification Gap (1 ausführlicher, verifizierter Fund + 1 Notiz).

| # | Fund (Quelle) | Verdikt | Begründung |
|---|----------------|---------|------------|
| 1 | Fehlender/leerer Link führt zu ArtikelId-Kollision; neue Artikel werden still verworfen (Blind Hunter + Edge Case Hunter + Verification Gap — alle drei unabhängig) | **high** | Verifiziert durch Code-Lesen und Nachbau: `getattr(entry, "link", "")` lässt zwei linklose Einträge auf dieselbe Hash-ID kollabieren; der zweite erscheint fälschlich als bereits bekannt. Verification-Gap-Layer hat dies sogar empirisch gegen den tatsächlichen `feedparser`-Rückgabewert nachgewiesen. Behoben durch Skip statt Default in Adapter + Application-Service (doppelte Absicherung). |
| 2 | Pro-Eintrag-Exception (z. B. kaputtes Datum) lief außerhalb des Try/Except und hätte den gesamten Lauf über alle 5 Quellen zum Absturz gebracht (Verification Gap, als „claim" gegen die Intent-Formulierung geprüft) | **high** | Verifiziert: die List Comprehension über `geparst.entries` lag außerhalb des `try`-Blocks. Das widerspricht FR1 direkt (ein Fehler sollte höchstens eine Quelle betreffen, hier hätte er alle fünf betroffen). Behoben durch fehlerisolierte Pro-Eintrag-Konvertierung. |
| 3 | `feedparser.parse()` ohne Timeout — hängende Quelle blockiert Ingestion unbegrenzt (Blind Hunter) | **medium** | Verifiziert: keine Timeout-Angabe im ursprünglichen Aufruf. Realistisches Produktionsrisiko bei öffentlichen Feeds. Behoben via `socket.setdefaulttimeout`. |
| 4 | Kein Test für den Fall „bozo=True, aber Einträge vorhanden" trotz expliziter Erwähnung in der eigenen Docstring (Blind Hunter) | **low** | Verifiziert: Lücke bestätigt. Test ergänzt und empirisch gegen eine echte `&`-Verletzung verifiziert (grün). |
| 5 | `ArtikelRepository.speichere` ohne Schutz vor `sqlite3.IntegrityError` bei gleichzeitigem Insert zweier Prozesse (Blind Hunter + Verification Gap, als Notiz) | **medium** | Verifiziert gegen die Architektur-Spine: AD-5/AD-7 verpflichten explizit auf Mehrprozess-Zugriff auf dieselbe Datei. Fix ist trivial (Try/Except, kein neues Public-Surface) — jetzt behoben statt zurückgestellt. |
| 6 | Fehlgeschlagene Quellen werden nirgends geloggt/gemeldet (Blind Hunter) | **defer** | Bereits als offener Punkt in PRD §8 und Architecture Spine „Deferred" geführt (Monitoring-Konzept). Kein neuer Fund, keine Logging-Infrastruktur existiert bisher im Projekt. |
| 7 | Cross-Source-Deduplizierung nicht adressiert (Blind Hunter) | **false** | Bereits explizit als Nicht-Ziel in dieser Spec dokumentiert (Boundaries & Constraints, „Never"-Abschnitt) — keine übersehene Lücke, sondern eine bereits getroffene PRD-Entscheidung. |
| 8 | Ungenutzter `pytest`-Import in `test_ingestion_service.py` (Blind Hunter) | **low** | Verifiziert, trivial behoben. |
| 9 | `test_feedparser_adapter.py` nutzt Try/Except/Else statt `pytest.raises` (Blind Hunter) | **low** | Verifiziert, trivial behoben (Konsistenz mit Projektkonvention). |
| 10 | Keine Umgebungsvariablen-basierte Override-Möglichkeit für Feed-URLs (Blind Hunter) | **defer** | Nicht Teil des Spec-Umfangs; Konfigurierbarkeit wurde nicht angefordert. Als Verbesserungsvorschlag zurückgestellt. |
| 11 | Kein DB-Index auf `quelle`/`status` für künftige Scoring-Abfragen (Blind Hunter) | **defer** | Verfrüht — der Abfragebedarf entsteht erst in Story 1.3; Index jetzt zu ergänzen wäre spekulativ (Rule of Three). |
| 12 | `_parse_iso` erzwingt stillschweigend UTC bei naivem Datetime beim Lesen; `speichere` validiert Zeitzonen-Bewusstsein nicht beim Schreiben (Blind Hunter) | **medium** | Verifiziert. Statt nur im Repository zu patchen, wurde die Invariante dort durchgesetzt, wo sie laut ddd-principles.md hingehört: im Aggregate-Konstruktor (`Artikel.__post_init__`). `_parse_iso` bleibt als zusätzliche Absicherung beim Lesen bestehen. |

## Design Notes

- `Quelle` als geschlossenes `str, Enum` statt freiem Value Object: bildet
  Domino's "feste Konfiguration von 5 Quellen" präziser ab als ein generisches
  VO mit Name+URL -- die URL ist eine Infrastruktur-Zugriffsdetail, keine
  Domänen-Eigenschaft, und lebt daher bewusst getrennt in
  `infrastructure/feeds/quellen_konfiguration.py` (AD-1-Grenze).
- Dedup-Strategie: Existenzprüfung per deterministischer `ArtikelId` --
  permanent, nicht zeitlich befristet auf 24 Stunden. Das ist eine bewusste
  Vereinfachung: "niemals doppelt melden" ist eine strengere Obermenge von
  "nicht innerhalb von 24 Stunden doppelt melden" (PRD NFR4) und erfüllt die
  Anforderung, ohne ein Wiedereinlass-Fenster zu bauen, das niemand
  angefordert hat.
- Domain Event `ArtikelEingegangen` aus Domino's Modell wird in dieser Story
  bewusst NICHT implementiert: ddd-principles.md verlangt, dass jeder
  Event-Typ einen Konsumenten hat ("Events ohne Listener sind toter Code").
  Es existiert noch kein Listener-Bedarf; das Event wird nachgeholt, sobald
  eine Story tatsächlich darauf reagieren muss.
- Fehlerbehandlung bei Quellenausfall: Try/Except liegt im
  `IngestionService` (Application-Schicht), nicht versteckt im Adapter --
  macht das Resilienzverhalten (FR1) direkt am Use-Case-Orchestrator sichtbar
  und testbar (Fake-Port kann gezielt für eine Quelle einen Fehler simulieren).
- Feed-URLs wurden per Web-Fetch verifiziert (CIO.com, BSI CERT-Bund,
  Propmodo, Bitkom liefern bestätigt valides RSS). Haufe Immobilien konnte
  nicht verifiziert werden (mehrere Kandidaten-URLs lieferten 404) -- bewusst
  als niedrigschwelliges, leicht korrigierbares Konfigurationsdetail markiert
  statt den Implementierungsfortschritt zu blockieren; der Ausfall dieser
  einen Quelle wird durch FR1's Resilienzmechanismus ohnehin abgefangen.

## Verification

**Commands:**
- `uv run pytest -v` -- expected: alle Tests grün (0 Failures), inkl. der
  bestehenden 24 Tests aus Story 1.1
