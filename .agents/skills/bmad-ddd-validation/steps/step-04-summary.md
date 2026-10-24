# Step 4: Abschlusszusammenfassung

Vierter und letzter Schritt. Lies die gesamte Datei, bevor du handelst.

## 1. Übersicht

Zeige eine Metrik-Übersicht:

| Metrik | Wert |
|--------|------|
| Analysierte Dokumente | |
| Gestellte Fragen | |
| Durchgeführte Änderungen | |
| Keine Änderung erforderlich | |
| Zur späteren Klärung markiert | |

## 2. Änderungsprotokoll nach Kategorien

Je Kategorie eine Tabelle: `# | Dokument | Vorher (gekürzt) | Nachher (gekürzt) | Begründung`.
Kategorien: Bounded Context, Ubiquitous Language, Aggregate Design, Entities vs. Value
Objects, Domain Events, Beziehungen & Integration.

## 3. Offene Punkte

Tabelle aller offenen Punkte: `# | Frage | Dokument | Notiz | Marker` – mit Marker
`[OFFEN]` oder `[KLÄRUNGSBEDARF]`.

## 4. Empfehlungen

Priorisierte Empfehlungen (Hoch/Mittel/Niedrig) mit betroffenen Dokumenten.

## 5. Nächste Schritte

- [ ] Offene Punkte (`[OFFEN]`) mit der zuständigen Rolle klären
- [ ] Stellen mit `[KLÄRUNGSBEDARF]` nachbearbeiten
- [ ] Validierung nach Änderungen wiederholen (Ziel: weniger Fragen pro Schleife)
- [ ] Bei neuen Erkenntnissen: zurück zu `bmad-ddd-discovery` für tiefere Discovery
- [ ] Abgestimmtes Modell an `bmad-architecture` und `bmad-create-epics-and-stories`
      übergeben

## 6. Dokumente speichern

Stelle sicher, dass alle bestätigten Änderungen in den Dokumenten persistiert und
geänderte Stellen mit `[GEÄNDERT]` markiert sind.
