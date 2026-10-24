# Step 4: Abschluss & Domänenelemente

Vierter und letzter Schritt. Lies die gesamte Datei, bevor du handelst.

## 1. Erkannte Domänenelemente ableiten

Werte das gesamte Interview aus und schlage die DDD-Elemente vor. Dies sind
**Vorschläge** – kennzeichne Unsicheres mit `[ANNAHME: ...]` oder `[KLÄRUNGSBEDARF]`:

- **Entities:** Objekte mit eigener Identität, je Kurzbeschreibung.
- **Value Objects:** Unveränderliche Objekte ohne Identität.
- **Aggregates:** Aggregate Root plus enthaltene Entities/Value Objects.
- **Domain Events:** Ereignisse (Vergangenheitsform), je Auslöser.
- **Geschäftsregeln / Invarianten:** nummeriert (R1, R2, …).
- **Bounded-Context-Beziehungen:** Upstream/Downstream, Integrationsart.

## 2. Offene Punkte zusammenstellen

Sammle alle `[OFFEN]`- und `[KLÄRUNGSBEDARF]`-Marker in einer Tabelle mit Abschnitt,
offener Frage und möglichem Ansprechpartner.

## 3. Ausgabedokument finalisieren

Stelle sicher, dass das Dokument unter `{planning_artifacts}/ddd/domain-discovery-{slug}.md`
vollständig ist: alle Abschnitte, „Erkannte Domänenelemente", „Offene Punkte" und
„Nächste Schritte". Setze `stepsCompleted` auf alle vier Steps und `status` passend
(`Abgeschlossen` / `Teilweise` / `Entwurf`).

## 4. Übergabe empfehlen

Weise den Nutzer auf die sinnvollen nächsten Schritte hin:

- **Konsistenz prüfen** mit dem Skill `bmad-ddd-validation` (prüft das erstellte
  Dokument auf DDD-Konformität und stellt gezielte Gegenfragen).
- **Technische Architektur** mit `bmad-architecture` (Winston).
- **User Stories** mit `bmad-create-epics-and-stories`.

Frage, ob direkt die Validierung (`bmad-ddd-validation`) gestartet werden soll.
