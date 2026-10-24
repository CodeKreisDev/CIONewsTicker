# Step 1: Kontext, Akteure & Fachsprache

Dies ist der erste von vier Schritten. Lies die gesamte Datei, bevor du handelst.

## Verhaltensregeln (gelten in allen Schritten)

- Arbeite **Abschnitt für Abschnitt** durch.
- Stelle pro Durchgang **maximal 3–5 Fragen** zu einem Themenbereich.
- Fasse nach jeder Antwort kurz zusammen, was du verstanden hast.
- **Frage gezielt nach**, wenn eine Antwort vage ist („meistens", „normalerweise"),
  Fachbegriffe undefiniert bleiben, Geschäftsregeln ohne Bedingung genannt werden,
  Prozessschritte angedeutet, Ausnahmen unerwähnt oder Verantwortlichkeiten unklar sind.
  Beispiele: „Du hast X erwähnt – was genau passiert dabei?", „Was bedeutet [Begriff]
  in eurem Kontext?", „Gibt es Ausnahmen von dieser Regel?", „Wer ist konkret
  verantwortlich?", „Kannst du ein konkretes Beispiel geben?"
- Markiere offene Fragen mit `[OFFEN]`, Unklarheiten mit `[KLÄRUNGSBEDARF]`, Annahmen
  mit `[ANNAHME: ...]`.
- Bevor du den Schritt abschließt: Erkenntnisse zusammenfassen, dokumentierte Antworten
  im Tabellenformat zeigen, fragen „Ist das so korrekt? Fehlt etwas Wichtiges?" – erst
  nach Bestätigung weiter.

## 0. Einstieg

Falls noch nicht geklärt, frage:
1. Für welchen Bounded Context / Fachbereich führen wir das Interview durch?
2. Wie viel Zeit steht zur Verfügung? (für die Tiefe)
3. Gibt es bestehende Dokumentation, die du kennen solltest?

Lege das Ausgabedokument an unter `{planning_artifacts}/ddd/domain-discovery-{slug}.md`
auf Basis von `{workflow.discovery_template}` (Fallback: `templates/domain-discovery-template.md`
relativ zum Skill-Root). Setze `stepsCompleted: []` im Frontmatter.

## Abschnitt 1: Kontext & Abgrenzung

**1.1 Zweck**
- Was ist das Hauptziel dieses Bereichs? Was soll erreicht werden?
- Welches Geschäftsproblem wird gelöst?
- Wer profitiert vom Ergebnis?
- Was passiert, wenn dieser Bereich nicht funktioniert?

**1.2 Abgrenzung**
- Was gehört definitiv zu diesem Bereich?
- Was gehört explizit NICHT dazu?
- Welche Aufgaben übernehmen andere Bereiche/Systeme?
- Gibt es Graubereiche mit unklarer Zugehörigkeit?

## Abschnitt 2: Akteure & Rollen

- Wer arbeitet aktiv mit diesem Bereich? (Rollen, nicht Personen)
- Wer löst Aktionen aus? Wer trifft Entscheidungen?
- Wer gibt frei / genehmigt? Wer hat nur lesenden Zugriff?
- Gibt es externe Akteure?
- Welche Berechtigungen/Kompetenzen haben die Rollen?

## Abschnitt 3: Ubiquitous Language (Fachsprache)

**3.1 Zentrale Begriffe**
- Welche Fachbegriffe werden täglich verwendet?
- Gibt es Begriffe, die intern anders verwendet werden als extern?
- Welche Abkürzungen gibt es, was bedeuten sie?
- Welche Begriffe werden häufig verwechselt?

**3.2 Begriffsklärung** (je Begriff)
- Interne Bezeichnung, genaue Bedeutung, Beispiel.

## Abschluss Step 1

1. Fasse Abschnitte 1–3 zusammen und zeige die Antworten als Tabellen.
2. Hänge das Ergebnis an das Ausgabedokument an.
3. Aktualisiere `stepsCompleted` um `step-01`.
4. Nach Bestätigung: Lade `./step-02-model-and-rules.md`.
