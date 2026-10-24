# Step 2: Daten, Prozesse, Geschäftsregeln & Events

Zweiter von vier Schritten. Lies die gesamte Datei, bevor du handelst. Es gelten die
Verhaltensregeln aus Step 1 (max. 3–5 Fragen pro Durchgang, zusammenfassen, nachfragen,
Marker, Bestätigung vor Abschluss).

## Abschnitt 4: Daten & Entitäten

**4.1 Zentrale Objekte**
- Was sind die wichtigsten „Dinge", mit denen gearbeitet wird?
- Welche davon haben eine eigene Identität (ID, Nummer)?
- Welche sind nur Eigenschaften/Attribute anderer?
- Was gehört immer zusammen? (Aggregate) Was kann unabhängig existieren?

**4.2 Datenherkunft**
- Woher kommen die Daten? (Systeme, manuelle Eingabe, Schnittstellen)
- Was ist manuell vs. automatisch? Gibt es Quellen unterschiedlicher Qualität?
- Was passiert bei widersprüchlichen Daten aus verschiedenen Quellen?

**4.3 Datenlebenszyklus**
- Wie lange werden Daten aufbewahrt? Was passiert mit alten Daten?
- Gibt es historische Daten, die nachvollziehbar sein müssen?

## Abschnitt 5: Prozesse & Abläufe

**5.1 Hauptprozess**
- Typischer Ablauf von Anfang bis Ende? Auslöser/Trigger? Endergebnis? Typische Dauer?

**5.2 Prozessschritte** (je Schritt)
- Wer führt ihn aus? Was wird getan? Was ist der Output?

**5.3 Prozessvarianten**
- Welche Varianten gibt es, was unterscheidet sie, wann greift welche?
- Gibt es Sonderfälle? Wie werden sie behandelt?

## Abschnitt 6: Geschäftsregeln & Invarianten

**6.1 Fachliche Regeln**
- Was MUSS immer gelten? (Invarianten) Was darf NIEMALS passieren?
- Welche Bedingungen müssen vor X erfüllt sein? Gibt es Grenz-/Schwellenwerte, Limits?

**6.2 Regelkatalog** (je Regel)
- Wie lautet die Regel? Wann greift sie? Was passiert bei Verletzung?

**6.3 Vorgaben & Compliance** (falls zutreffend)
- Welche verbindlichen Vorgaben müssen beachtet werden?
- Aus welchen Quellen stammen sie? Gibt es Ermessensspielräume?

## Abschnitt 7: Events & Zustandsübergänge

**7.1 Fachliche Ereignisse**
- Was sind wichtige Ereignisse? Was löst sie aus?
- Wer muss informiert werden? Welche Folgeprozesse werden angestoßen?

**7.2 Zustände**
- Welche Zustände kann ein Objekt haben?
- Welche Übergänge sind erlaubt, welche verboten?
- Wer darf welchen Übergang auslösen?

## Abschluss Step 2

1. Fasse Abschnitte 4–7 zusammen und zeige die Antworten als Tabellen.
2. Hänge das Ergebnis an das Ausgabedokument an.
3. Aktualisiere `stepsCompleted` um `step-02`.
4. Nach Bestätigung: Lade `./step-03-interfaces-and-quality.md`.
