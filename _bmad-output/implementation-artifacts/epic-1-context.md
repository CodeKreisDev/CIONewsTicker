# Epic 1 Context: Tägliches kuratiertes Briefing

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Epic 1 liefert dem einzigen CIO an jedem Werktag bis 07:00 Uhr ein kompaktes, relevanzgefiltertes Telegram-Briefing aus den fünf festgelegten öffentlichen RSS-Quellen. Die Pipeline ingestiert, dedupliziert, bewertet, filtert, kategorisiert und synthetisiert Nachrichten; wenn keine relevanten Artikel verfügbar sind oder alle Feeds ausfallen, wird stattdessen ausdrücklich „Kein relevantes Briefing heute“ gesendet. Der Bot reagiert ausschließlich auf die konfigurierte Chat-ID, damit das zentrale Versprechen — in unter zwei Minuten zu wissen, was zählt, ohne kritische Warnungen zu übersehen — zuverlässig und geschützt erfüllt wird.

## Stories

- Story 1.1: Projekt-Grundgerüst & Zugriffsschutz
- Story 1.2: Artikel aus RSS-Quellen einlesen
- Story 1.3: Artikel nach Relevanz bewerten und filtern
- Story 1.4: Kategorisiertes Tages-Briefing erstellen und zustellen
- Story 1.5: Explizite Information bei leerem Ergebnis

## Requirements & Constraints

- Ein nächtlicher Lauf ruft alle fünf Quellen (CIO.com, BSI, Haufe Immobilien, Propmodo, Bitkom) einmal ab. Der Ausfall einer Quelle darf die Verarbeitung der übrigen Quellen nicht blockieren und muss erkennbar bleiben.
- Neue Artikel werden als `Artikel` mit Zustand „Eingegangen“ verarbeitet. Derselbe Quellen-Link darf innerhalb des 24-Stunden-Dedup-Fensters nicht erneut gemeldet werden; eine inhaltliche Deduplizierung über verschiedene Quellen ist im MVP nicht erforderlich.
- Jeder eingegangene Artikel erhält durch die LLM-Bewertung einen Relevanz-Score von 1–10 für die Persona CIO im Immobiliensektor. Scores unter 7 werden verworfen und dürfen nicht im Briefing erscheinen.
- Die Synthese erstellt ein Markdown-Briefing mit höchstens fünf Artikeln. Jeder Artikel gehört genau einer Kategorie: „Real Estate & ESG“ oder „Enterprise IT & Cyber“. Auswahl erfolgt nach Score absteigend, bei Gleichstand nach neuerem Artikel; qualifizierte, nicht ausgewählte Artikel bleiben fachlich von verworfenen Artikeln unterscheidbar.
- Montag bis Freitag wird um 07:00 Uhr Ortszeit (MVP: `Europe/Berlin`) entweder das Briefing oder eine klar erkennbare Leer-Nachricht an genau eine whitelistete Telegram-Chat-ID gesendet. Wochenenden senden nicht; Feiertagslogik ist nicht Bestandteil des MVP.
- Betriebskosten bleiben unter 20 €/Monat. LLM-Eingaben enthalten ausschließlich externe, öffentliche News — keinen internen Unternehmenskontext — und umgehen weder Paywalls noch technische Zugriffsbeschränkungen. Es darf nie stille Nichterfüllung an einem erwarteten Werktag geben.

## Technical Decisions

- Schlanke Python-3.15-Codebasis ohne Starter-Template in den Schichten `domain` → `application` → `infrastructure`/`interfaces`. Die Domäne kennt weder Frameworks noch Infrastruktur; Interfaces rufen ausschließlich Application-Use-Cases auf.
- Verwendet werden `python-telegram-bot` 22.8, `feedparser` 6.0.14, APScheduler 3.11.3 und eingebettetes SQLite. Telegram läuft ausschließlich über Long Polling. Batch/Scheduler und Listener sind getrennte Prozesse auf einer einzelnen dauerhaft laufenden VPS.
- SQLite läuft im WAL-Modus. Repository-Ports liegen in Domain/Application, Implementierungen in `infrastructure/persistence`; Transaktionen bleiben kurz und werden pro Zugriff abgeschlossen, weil beide Prozesse dieselbe Datei nutzen.
- Scoring und Synthese werden über das austauschbare `LLMPort` in `application/ports/` angebunden; Provider-Adapter liegen in `infrastructure/llm/`. Telegram-, Feed- und Scheduler-Adapter bleiben ebenfalls hinter Ports bzw. Infrastrukturgrenzen.
- `Artikel` und `Briefing` sind getrennte Aggregate Roots. Das Briefing referenziert Artikel ausschließlich über IDs; Zustandsänderungen erfolgen nur über Aggregate-Methoden. Artikel-IDs werden deterministisch aus Quelle und Link abgeleitet.
- Telegram-Token, LLM-API-Key, Chat-ID und sonstige Konfiguration kommen ausschließlich aus Umgebungsvariablen oder einem Host-Secret-Store und werden weder committed noch geloggt. Interne Zeiten werden in UTC/ISO 8601 gespeichert; strukturierte Logs dürfen keine sensiblen Daten enthalten.

## UX & Interaction Patterns

Telegram ist der einzige Kanal und der CIO der einzige Nutzer. Das Briefing wird als kurzes Markdown-Dokument mit den beiden festen Kategorieüberschriften zugestellt und soll in unter zwei Minuten erfassbar sein. Eine Leer-Nachricht muss als bewusstes Ergebnis erkennbar sein, nicht wie ein Systemfehler. Eingehende Nachrichten von jeder anderen Chat-ID werden still ignoriert, ohne Antwort oder Hinweis auf die Bot-Konfiguration.

## Cross-Story Dependencies

- Story 1.1 schafft Schichten, Konfiguration, SQLite/WAL und Whitelisting als Grundlage für alle weiteren Stories.
- Story 1.2 liefert deduplizierte Artikel im Zustand „Eingegangen“; Story 1.3 bewertet und filtert diese. Story 1.4 synthetisiert die verbleibenden Kandidaten und nutzt die Zustellungsinfrastruktur. Story 1.5 verwendet denselben Scheduler- und Telegram-Zustellpfad und ist der alternative Ausgang, wenn keine Kandidaten vorhanden sind.
- Epic 2 setzt auf dem Telegram-Listener und der Artikel-/Briefing-Persistenz aus Epic 1 auf, ist aber für die vollständige Funktion dieses Epics nicht erforderlich.
