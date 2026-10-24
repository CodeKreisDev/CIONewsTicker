# Step 2: Analyse, Kategorisierung & Fragenkatalog

Zweiter von vier Schritten. Lies die gesamte Datei, bevor du handelst.

## 1. Systematische Analyse

Identifiziere in den Dokumenten systematisch:

| Element | Worauf achten? |
|---------|----------------|
| Bounded Contexts | Kontextgrenzen, Verantwortlichkeiten |
| Entities | Objekte mit Identität, Attribute, Verhalten |
| Aggregates | Aggregate Roots, Invarianten |
| Value Objects | Unveränderliche Objekte ohne Identität |
| Domain Events | Ereignisse, Payload, Konsumenten |
| Ubiquitous Language | Glossar, Begriffsdefinitionen |
| Enumerationen | Aufzählungstypen, Werte |
| Beziehungen | Abhängigkeiten zwischen Kontexten |
| Geschäftsregeln | Invarianten, Validierungen |

## 2. Übersicht zeigen

Zeige dem Nutzer: analysierte Dokumente (Name, Typ, Bounded Context), Anzahl
identifizierter Elemente je Kategorie und **erkannte Inkonsistenzen/Auffälligkeiten**.
Nenne, wie viele Validierungsfragen du in wie vielen Kategorien vorbereitet hast.

## 3. Fragenkatalog vorbereiten

Erstelle Fragen entlang dieser DDD-Kategorien:

1. **Bounded Context & Kontextgrenzen** – Grenzen klar/sinnvoll? Überschneidungen?
   Externe Abhängigkeiten vollständig? Fehlende Kontexte?
2. **Ubiquitous Language** – Begriffe konsistent? Synonyme? Gleiche Begriffe mit
   unterschiedlicher Bedeutung? Alle Fachbegriffe im Glossar?
3. **Aggregate Design & Invarianten** – Aggregate Roots korrekt markiert? Invarianten
   explizit? Grenze sinnvoll (nicht zu groß/klein)? Transaktionsgrenzen beachtet?
4. **Entities vs. Value Objects** – Entities korrekt (Identität über Zeit)? Manche VO?
   VO unveränderlich? Fehlende VO zu extrahieren?
5. **Domain Events** – Alle relevanten Events identifiziert? Namen in Vergangenheitsform?
   Payloads vollständig & minimal? Konsumenten klar? Fehlende Events für Übergänge?
6. **Beziehungen & Integration** – Wie kommunizieren Kontexte? Integrationsmuster
   dokumentiert? Abhängigkeitsrichtungen klar? Zirkuläre Abhängigkeiten?

## 4. Fortschritts-Tracking

Vor Beginn jeder Validierungsschleife zeige den Stand: aktuelle Schleife und Anzahl
vorbereiteter Fragen. Ziel: mit jeder Schleife weniger Fragen, da die Dokumentation
konsistenter wird. Ein Anstieg deutet auf neue Anforderungen oder größere Änderungen hin.

## 5. Abschluss Step 2

Frage: „Bereit für den Frage-Antwort-Dialog?" Nach Bestätigung: Lade `./step-03-qa-loop.md`.
