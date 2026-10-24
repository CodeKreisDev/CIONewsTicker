---
stepsCompleted: []
status: Entwurf
---

# Domain Discovery: {Name des Bounded Context}

**Durchgeführt am:** {Datum}
**Teilnehmer:** {Namen/Rollen}
**Status:** {Abgeschlossen / Teilweise / Entwurf}

---

## 1. Kontext & Abgrenzung

### 1.1 Zweck

| # | Frage | Antwort |
|---|-------|---------|
| 1.1.1 | Hauptziel | |
| 1.1.2 | Geschäftsproblem | |
| 1.1.3 | Nutznießer | |
| 1.1.4 | Auswirkung bei Ausfall | |

### 1.2 Abgrenzung

| # | Frage | Antwort |
|---|-------|---------|
| 1.2.1 | In Scope | |
| 1.2.2 | Out of Scope | |
| 1.2.3 | Andere Bereiche | |
| 1.2.4 | Graubereiche | |

## 2. Akteure & Rollen

| Rolle | Aufgaben | Berechtigungen |
|-------|----------|----------------|
| | | |

## 3. Ubiquitous Language

| Begriff | Bedeutung | Beispiel |
|---------|-----------|----------|
| | | |

## 4. Daten & Entitäten

| Objekt | Identität? | Wichtige Attribute | Beziehungen |
|--------|-----------|--------------------|-------------|
| | | | |

## 5. Prozesse & Abläufe

| Prozess | Auslöser | Schritte | Ergebnis | Varianten |
|---------|----------|----------|----------|-----------|
| | | | | |

## 6. Geschäftsregeln & Invarianten

| # | Regel | Wann greift sie | Bei Verletzung |
|---|-------|-----------------|----------------|
| R1 | | | |

## 7. Events & Zustandsübergänge

| Event / Zustand | Auslöser | Erlaubte Übergänge | Wer löst aus |
|-----------------|----------|--------------------|--------------|
| | | | |

## 8. Schnittstellen & Abhängigkeiten

| Richtung | Partner | Format | Häufigkeit | Fehlerfall |
|----------|---------|--------|-----------|------------|
| Upstream | | | | |
| Downstream | | | | |

## 9. Berechnungen & Algorithmen

| Berechnung | Eingaben | Ergebnis | Varianten | Konfigurierbar |
|------------|----------|----------|-----------|----------------|
| | | | | |

## 10. Fehler & Ausnahmen

| Fehler | Erkennung | Behandlung | Benachrichtigung | Korrektur |
|--------|-----------|------------|------------------|-----------|
| | | | | |

## 11. Qualität & Validierung

| Mechanismus | Beschreibung |
|-------------|--------------|
| | |

---

## Offene Punkte

| # | Abschnitt | Offene Frage | Ansprechpartner |
|---|-----------|--------------|-----------------|
| 1 | | | |

---

## Erkannte Domänenelemente (Vorschläge)

### Entities
- {Entity}: {Kurzbeschreibung}

### Value Objects
- {VO}: {Kurzbeschreibung}

### Aggregates
- {Aggregate}: enthält {Entity A, VO B}

### Domain Events
- {Event}: tritt ein, wenn …

### Geschäftsregeln
- R1: {Beschreibung}

### Bounded-Context-Beziehungen
- {Partner}: {Upstream/Downstream}, Integration: {Art}

---

## Nächste Schritte

- [ ] Offene Punkte klären mit {Person}
- [ ] Konsistenz prüfen mit `bmad-ddd-validation`
- [ ] Technische Architektur mit `bmad-architecture`
- [ ] User Stories mit `bmad-create-epics-and-stories`

---

**Marker:** `[OFFEN]` = noch zu klären · `[KLÄRUNGSBEDARF]` = Unklarheit ·
`[ANNAHME: ...]` = Annahme getroffen · `[GEÄNDERT]` = durch Validierung geändert
