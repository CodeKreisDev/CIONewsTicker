# Step 3: Schnittstellen, Berechnungen, Fehler & Qualität

Dritter von vier Schritten. Lies die gesamte Datei, bevor du handelst. Es gelten die
Verhaltensregeln aus Step 1.

## Abschnitt 8: Schnittstellen & Abhängigkeiten

**8.1 Eingehende Abhängigkeiten (Upstream)**
- Von welchen Bereichen/Systemen werden Daten empfangen? In welchem Format?
- Wie oft werden Daten geliefert? (Echtzeit, periodisch, on-demand)
- Was passiert, wenn eine Quelle nicht liefert?

**8.2 Ausgehende Abhängigkeiten (Downstream)**
- Wer braucht die Ergebnisse? In welcher Form werden sie bereitgestellt?
- Gibt es Zeitvorgaben oder Zusagen (SLAs) für die Bereitstellung?

## Abschnitt 9: Berechnungen & Algorithmen

- Welche Berechnungen/Formeln werden durchgeführt?
- Was sind Eingabewerte, was ist das Ergebnis?
- Gibt es mehrere Berechnungsvarianten?
- Wer definiert die Logik (fachlich/verbindlich)? Ist sie konfigurierbar?

## Abschnitt 10: Fehler & Ausnahmen

- Was kann schiefgehen? Wie werden Fehler erkannt und behandelt?
- Wer wird bei Fehlern benachrichtigt?
- Gibt es manuelle Korrekturmöglichkeiten? Müssen Korrekturen begründet werden?

## Abschnitt 11: Qualität & Validierung

- Wie wird die Qualität der Ergebnisse sichergestellt?
- Gibt es Plausibilitätsprüfungen? Gibt es ein Mehr-Augen-Prinzip?
- Wie wird Nachvollziehbarkeit gewährleistet? (Audit Trail)

## Abschluss Step 3

1. Fasse Abschnitte 8–11 zusammen und zeige die Antworten als Tabellen.
2. Hänge das Ergebnis an das Ausgabedokument an.
3. Aktualisiere `stepsCompleted` um `step-03`.
4. Nach Bestätigung: Lade `./step-04-finalize.md`.
