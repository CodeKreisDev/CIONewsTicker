---
status: final
stepsCompleted: [step-01, step-02, step-03]
inputDocuments: ['_bmad-output/planning-artifacts/prds/prd-CIONewsTicker-2026-10-24/prd.md', '_bmad-output/planning-artifacts/architecture/architecture-CIONewsTicker-2026-10-24/ARCHITECTURE-SPINE.md', '_bmad-output/planning-artifacts/ddd/domain-discovery-cio-info-agent.md']
---

# CIONewsTicker (CIO Info Agent) - Epic Breakdown

## Overview

Dieses Dokument zerlegt die Anforderungen aus PRD, Domänenmodell und
Architektur-Spine in umsetzbare Epics und User Stories.

## Requirements Inventory

### Functional Requirements

- FR1: Das System ruft 1× täglich die RSS-Feeds aller fünf definierten Quellen ab.
- FR2: Das System darf keinen Artikel erneut melden, der innerhalb der letzten 24 Stunden bereits im Briefing enthalten war.
- FR3: Das System bewertet jeden abgerufenen Artikel auf einer Skala von 1–10 hinsichtlich seiner Relevanz für die Ziel-Persona.
- FR4: Artikel mit einem Relevanz-Score unter 7 werden automatisch verworfen und erscheinen nicht im Briefing.
- FR5: Das System fasst die Top-Artikel (max. 5) in einem Markdown-Briefing zusammen, kategorisiert in „Real Estate & ESG" und „Enterprise IT & Cyber".
- FR6: Das System stellt das Briefing werktags (Montag–Freitag) um 07:00 Uhr per Telegram an die whitelistete Chat-ID zu.
- FR7: Erreicht an einem Tag kein Artikel den Schwellenwert, oder schlagen alle Feeds fehl, sendet das System eine explizite „Kein relevantes Briefing heute"-Nachricht statt gar keine Nachricht zu senden.
- FR8: Der CIO kann per Chat-Befehl „Deep Dive [Link/Thema]" eine detaillierte Zusammenfassung eines Artikels aus dem aktuellen Tages-Briefing anfordern (per Link oder Referenz).
- FR9: Ist die beim Deep Dive angefragte Quelle nicht abrufbar (Paywall, 404, Timeout), antwortet der Bot mit einer klaren, verständlichen Fehlermeldung.
- FR10: Das System verarbeitet ausschließlich Nachrichten von der konfigurierten, whitelisteten Telegram-Chat-ID; Nachrichten von anderen Absendern werden ignoriert.

### NonFunctional Requirements

- NFR1 (Cost): Betriebskosten (LLM-API + Hosting) dürfen 20 €/Monat nicht überschreiten.
- NFR2 (Privacy): Der Agent erhält keinerlei internen Unternehmenskontext als LLM-Input — ausschließlich externe, öffentliche News.
- NFR3 (Security): Zugriff ausschließlich über die whitelistete Telegram-Chat-ID; keine Umgehung von Paywalls oder technischen Zugriffsbeschränkungen.
- NFR4 (Reliability): Keine doppelten Nachrichten innerhalb von 24 Stunden; niemals Stille statt einer erwarteten täglichen Nachricht.
- NFR5 (Robustheit): Der Ausfall einzelner Feeds darf weder den gesamten Lauf blockieren noch unbemerkt bleiben.
- NFR6 (Kostenkontrolle): LLM-Anbindung muss über ein austauschbares Port-Interface laufen (Architektur AD-6), damit Modellwahl ohne Domänenänderung anpassbar bleibt.

### Additional Requirements

*(aus Architecture Spine abgeleitet)*

- Kein Starter-Template vorgesehen — Projekt wird als schlanke Python-Codebasis nach dem in der Spine definierten Schichten-Layout (`domain/application/infrastructure/interfaces`) aufgesetzt (Epic 1, Story 1).
- Laufzeitumgebung: Python 3.15, Bibliotheken `python-telegram-bot` 22.8, `feedparser` 6.0.14, `APScheduler` 3.11.3 (AD-3).
- Telegram-Anbindung ausschließlich über Long Polling, kein Webhook (AD-4).
- Deployment auf einer einzelnen, durchgehend laufenden VPS; Batch-Lauf (Scheduler) und Telegram-Listener als getrennte Prozesse auf demselben Host (AD-5).
- Persistenz über eingebettetes SQLite im WAL-Modus, mit kurzen Transaktionen wegen gleichzeitigen Zugriffs durch Batch- und Listener-Prozess (AD-7).
- LLM-Anbindung über `LLMPort`-Interface in `application/ports/`; Adapter-Implementierung in `infrastructure/llm/` (AD-6).
- Secrets (Telegram-Token, LLM-API-Key) ausschließlich über Umgebungsvariablen/Secret-Store, nie im Code oder Log (AD-8).
- Aggregate-Grenzen: `Artikel` und `Briefing` sind getrennte Aggregate Roots; `Briefing` referenziert `Artikel` nur über ID (AD-2, aus Domino's Domänenmodell).

### UX Design Requirements

Nicht zutreffend — das System hat keine grafische Benutzeroberfläche; Telegram-Chat ist
der einzige Interaktionskanal und bereits vollständig über FR6–FR10 spezifiziert.

### FR Coverage Map

| FR | Epic |
|----|------|
| FR1 (Feed-Abruf) | Epic 1 |
| FR2 (Dedup) | Epic 1 |
| FR3 (Scoring) | Epic 1 |
| FR4 (Filterung) | Epic 1 |
| FR5 (Synthese) | Epic 1 |
| FR6 (Zustellung) | Epic 1 |
| FR7 (Leer-Nachricht) | Epic 1 |
| FR8 (Deep Dive) | Epic 2 |
| FR9 (Deep-Dive-Fehlerrückmeldung) | Epic 2 |
| FR10 (Whitelisting) | Epic 1 (foundational — Epic 1 ist ohne Zugriffsschutz nicht sicher betreibbar) |
| NFR1–NFR6 | Cross-cutting, beide Epics |

## Epic List

1. **Epic 1: Tägliches kuratiertes Briefing** — Projekt-Grundgerüst, Zugriffsschutz, vollautomatisierte Ingestion → Scoring → Synthese → Zustellung inkl. Leer-Nachricht-Garantie. Deckt FR1–FR7, FR10.
2. **Epic 2: Deep Dive auf Briefing-Artikel** — interaktive Vertiefung einzelner Artikel des aktuellen Briefings inkl. Fehlerrückmeldung. Deckt FR8, FR9. Baut auf Epic 1 auf (Telegram-Listener, Artikel-Persistenz), Epic 1 funktioniert vollständig auch ohne Epic 2.

## Epic 1: Tägliches kuratiertes Briefing

Der CIO erhält werktags um 07:00 Uhr automatisiert ein relevanzgefiltertes, nach
„Real Estate & ESG" und „Enterprise IT & Cyber" kategorisiertes News-Briefing per
Telegram — oder, falls nichts Relevantes gefunden wurde, eine explizite
„Kein Briefing heute"-Nachricht statt Stille. Nur die eine whitelistete Chat-ID kann
mit dem Bot interagieren; alle anderen Nachrichten werden ignoriert.

### Story 1.1: Projekt-Grundgerüst & Zugriffsschutz

Als CIO
möchte ich, dass der Bot von Anfang an nur auf meine Nachrichten reagiert,
damit kein Unbefugter das System nutzen oder Informationen darüber erhalten kann.

**Acceptance Criteria:**

**Given** eine Nachricht von der konfigurierten, whitelisteten Chat-ID
**When** der Bot sie empfängt
**Then** verarbeitet er sie weiter (FR10)

**Given** eine Nachricht von einer anderen Chat-ID
**When** der Bot sie empfängt
**Then** ignoriert er sie vollständig, ohne zu antworten (FR10)

**Given** das Projekt wird gestartet
**When** der Prozess hochfährt
**Then** ist die Schichtenstruktur (`domain`/`application`/`infrastructure`/`interfaces`) gemäß Architektur-Spine angelegt und SQLite im WAL-Modus initialisiert (AD-3, AD-7)
**And** Telegram-Bot-Token und LLM-API-Key werden ausschließlich aus Umgebungsvariablen gelesen, nie hartcodiert (AD-8)

### Story 1.2: Artikel aus RSS-Quellen einlesen

Als CIO
möchte ich, dass das System täglich automatisch alle relevanten Nachrichtenquellen abruft,
damit ich mich nicht manuell durch mehrere Feeds hangeln muss.

**Acceptance Criteria:**

**Given** die fünf definierten Quellen (CIO.com, BSI, Haufe Immobilien, Propmodo, Bitkom)
**When** der nächtliche Ingestion-Lauf startet
**Then** werden alle fünf Feeds abgerufen (FR1)

**Given** eine der fünf Quellen ist nicht erreichbar
**When** der Ingestion-Lauf läuft
**Then** werden die übrigen Quellen trotzdem vollständig verarbeitet (FR1, NFR5)

**Given** ein neu gefundener Artikel
**When** er eingelesen wird
**Then** wird er als `Artikel` im Zustand „Eingegangen" gespeichert

**Given** ein Artikel-Link, der bereits innerhalb der letzten 24 Stunden gemeldet wurde
**When** er erneut im Feed erscheint
**Then** wird er nicht erneut als neuer Artikel angelegt (FR2)

### Story 1.3: Artikel nach Relevanz bewerten und filtern

Als CIO
möchte ich, dass nur wirklich relevante Artikel für mich weiterverarbeitet werden,
damit ich nicht durch Nebensächliches abgelenkt werde.

**Acceptance Criteria:**

**Given** ein Artikel im Zustand „Eingegangen"
**When** die Bewertung läuft
**Then** erhält er einen Relevanz-Score zwischen 1 und 10 und wechselt zu „Bewertet" (FR3)

**Given** ein bewerteter Artikel mit Score kleiner 7
**When** die Filterung läuft
**Then** wechselt er in den Zustand „Verworfen" und erscheint nie im Briefing (FR4)

**Given** ein bewerteter Artikel mit Score 7 oder höher
**When** die Filterung läuft
**Then** gilt er als Kandidat für das Briefing
**And** die Bewertung erfolgt über das `LLMPort`-Interface, sodass der konkrete Anbieter austauschbar bleibt (AD-6)

### Story 1.4: Kategorisiertes Tages-Briefing erstellen und zustellen

Als CIO
möchte ich werktags um 07:00 Uhr ein fertiges, kategorisiertes Briefing erhalten,
damit ich in unter 2 Minuten weiß, was heute zählt.

**Acceptance Criteria:**

**Given** mindestens 3 Kandidaten-Artikel (Score ≥ 7)
**When** die Synthese läuft
**Then** werden bis zu 5 davon ausgewählt (höchster Score zuerst, bei Gleichstand der neuere Artikel, R8) und je einer Kategorie „Real Estate & ESG" oder „Enterprise IT & Cyber" zugeordnet (FR5)

**Given** mehr als 5 Kandidaten an einem Tag
**When** die Top-5-Auswahl läuft
**Then** wechseln die nicht ausgewählten Kandidaten in den Zustand „QualifiziertNichtAusgewählt" statt „Verworfen"

**Given** ein fertiges Briefing
**When** es 07:00 Uhr an einem Werktag ist
**Then** wird es an die whitelistete Chat-ID gesendet (FR6)

**Given** es ist Samstag oder Sonntag
**When** die Zustellungszeit erreicht wird
**Then** wird kein Briefing versendet (FR6)

### Story 1.5: Explizite Information bei leerem Ergebnis

Als CIO
möchte ich auch dann eine klare Nachricht bekommen, wenn es nichts Relevantes gibt,
damit ich Stille niemals mit einem Systemausfall verwechsle.

**Acceptance Criteria:**

**Given** an einem Werktag erreicht kein Artikel den Schwellenwert
**When** die Zustellungszeit (07:00 Uhr) erreicht wird
**Then** erhalte ich eine explizite „Kein relevantes Briefing heute"-Nachricht (FR7)

**Given** alle fünf Quellen sind in der Nacht ausgefallen
**When** die Zustellungszeit erreicht wird
**Then** erhalte ich ebenfalls die explizite Leer-Nachricht statt Stille (FR7, NFR4)
**And** die Leer-Nachricht unterscheidet sich im Wortlaut klar erkennbar von einem Fehler/Ausfall

## Epic 2: Deep Dive auf Briefing-Artikel

Der CIO kann zu jedem Artikel im aktuellen Tages-Briefing per Chat-Befehl
„Deep Dive [Link/Thema]" eine vertiefte Zusammenfassung der Quelle anfordern. Ist die
Quelle nicht abrufbar, erhält er eine klare, verständliche Fehlermeldung statt
Schweigen.

### Story 2.1: Deep Dive auf Briefing-Artikel anfordern

Als CIO
möchte ich zu einem Artikel aus meinem heutigen Briefing sofort eine vertiefte Zusammenfassung anfordern können,
damit ich bei Interesse nicht selbst recherchieren muss.

**Acceptance Criteria:**

**Given** ein Artikel ist Teil des aktuellen Tages-Briefings
**When** ich „Deep Dive [Link oder Referenz]" sende
**Then** erhalte ich eine eigenständige, vertiefte Zusammenfassung der Quelle (FR8)

**Given** ich referenziere den Artikel per Nummer/Titel aus dem Briefing
**When** ich den Deep-Dive-Befehl sende
**Then** wird der richtige Artikel eindeutig identifiziert (FR8)

**Given** ich sende „Deep Dive" zu einem Thema, das nicht Teil des aktuellen Briefings ist
**When** der Bot die Anfrage verarbeitet
**Then** lehnt er sie mit einem Hinweis ab, dass nur Briefing-Artikel unterstützt werden (FR8 Out of Scope, R5)

### Story 2.2: Fehlerrückmeldung bei nicht abrufbarer Quelle

Als CIO
möchte ich eine klare Fehlermeldung bekommen, wenn eine Deep-Dive-Quelle nicht abrufbar ist,
damit ich nicht auf eine Antwort warte, die nie kommt.

**Acceptance Criteria:**

**Given** die angefragte Quelle liegt hinter einer Paywall
**When** der Deep Dive ausgeführt wird
**Then** antwortet der Bot mit einer verständlichen Fehlermeldung, die den Grund benennt (FR9)

**Given** die angefragte Quelle liefert einen 404 oder Timeout
**When** der Deep Dive ausgeführt wird
**Then** antwortet der Bot ebenfalls mit einer klaren Fehlermeldung statt zu schweigen (FR9)


