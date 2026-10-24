---
stepsCompleted: [step-01, step-02, step-03, step-04]
status: Abgeschlossen
---

# Domain Discovery: CIO Info Agent (Real Estate Edition)

**Durchgeführt am:** 2026-10-24
**Teilnehmer:** A.F. (Product Owner), Domino (Domain Modeler)
**Status:** Teilweise (Abschnitte 1–3 aus Brief/PRD abgeleitet, Rest folgt)

**Quelle:** Diese Discovery wurde nicht als Live-Interview geführt, sondern aus dem
bereits finalisierten [Brief](../briefs/brief-CIONewsTicker-2026-10-24/brief.md) und
[PRD](../prds/prd-CIONewsTicker-2026-10-24/prd.md) abgeleitet. Abschnitte, in denen das
PRD keine Aussage trifft, sind als `[OFFEN]` markiert.

---

## 1. Kontext & Abgrenzung

### 1.1 Zweck

| # | Frage | Antwort |
|---|-------|---------|
| 1.1.1 | Hauptziel | Täglich automatisiert ein relevanzgefiltertes, kategorisiertes News-Briefing für den CIO liefern. |
| 1.1.2 | Geschäftsproblem | Information Overload; Risiko, dass kritische Warnungen (z. B. BSI) in der Informationsflut untergehen. |
| 1.1.3 | Nutznießer | Ausschließlich der eine CIO (Single-User, bewusste Entscheidung). |
| 1.1.4 | Auswirkung bei Ausfall | CIO erhält kein Briefing und muss auf manuelle Recherche zurückfallen; im schlimmsten Fall wird eine kritische Sicherheitswarnung verpasst. FR-7 (explizite „Kein Briefing heute"-Nachricht) mindert dieses Risiko bereits teilweise ab, indem Stille von einem erkannten Leerergebnis unterschieden wird. |

### 1.2 Abgrenzung

| # | Frage | Antwort |
|---|-------|---------|
| 1.2.1 | In Scope | RSS-Ingestion der 5 definierten Quellen, LLM-Scoring/Filterung (Schwellenwert 7), kategorisierte Synthese, pünktliche Werktags-Zustellung, Deep Dive auf Artikel des Tages-Briefings, Chat-ID-Whitelisting. |
| 1.2.2 | Out of Scope | Mehrbenutzerfähigkeit, Paywall-Umgehung, interner Unternehmenskontext als LLM-Input, freies themenbasiertes Deep Dive außerhalb des Tages-Briefings, zusätzliche Quellen (v1). |
| 1.2.3 | Andere Bereiche | Keine — der Agent arbeitet vollständig autark auf Basis externer, öffentlicher Daten; es gibt keine Integration mit internen Unternehmenssystemen. |
| 1.2.4 | Graubereiche | Feiertagslogik bei der Zustellung `[OFFEN]`; ob verworfene (Score < 7) Artikel für Audit-Zwecke gespeichert werden `[OFFEN]` — beides bereits im PRD als offene Punkte geführt. |

---

## 2. Akteure & Rollen

| Rolle | Aufgaben | Berechtigungen |
|-------|----------|----------------|
| **CIO** | Empfängt das tägliche Briefing; löst per Chat-Befehl einen Deep Dive zu einem Artikel des aktuellen Briefings aus. | Einzige whitelistete Chat-ID; einziger aktiver Nutzer des Systems. |
| **Scheduler/Ingestion-Prozess** | Kein menschlicher Akteur, aber fachlich relevant: löst nächtlich den Ingestion- und Scoring-Lauf automatisch aus. | Systemintern, keine Nutzerinteraktion. |
| **Externe Quelle** (CIO.com, BSI, Haufe Immobilien, Propmodo, Bitkom Presse-Feed) | Liefert passiv RSS-Feed-Inhalte. | Rein lesender, einseitiger Datenfluss — keine Rückmeldung an die Quelle. |

`[OFFEN]` Es gibt keine Freigabe-, Genehmigungs- oder Mehr-Augen-Rolle — weder im Brief
noch im PRD vorgesehen. Falls fachlich gewünscht (z. B. Vier-Augen-Prinzip bei
Deep-Dive-Ergebnissen), wäre das ein neuer Akteur und nachträglich zu ergänzen.

---

## 3. Ubiquitous Language

*Übernommen wörtlich aus PRD §3 (Glossar), als verbindliche Fachsprache für Domänenmodell,
Architektur und Code:*

| Begriff | Bedeutung | Beispiel |
|---------|-----------|----------|
| **Artikel** | Ein einzelner über RSS abgerufener News-Beitrag einer Quelle. | Ein CIO.com-Beitrag über eine neue EU-Regulierung. |
| **Quelle** | Einer der fünf fest definierten RSS-Feeds. | BSI-Presse-Feed. |
| **Relevanz-Score** | Vom LLM vergebene Zahl 1–10, Relevanz für die Zielperson. | Score 8 für einen BSI-Sicherheitshinweis. |
| **Schwellenwert** | Score-Grenzwert 7; darunter wird verworfen. | Artikel mit Score 6 erscheint nicht im Briefing. |
| **Briefing** | Das tägliche, kategorisierte Markdown-Dokument aus den Top-Artikeln. | Das Dokument, das der CIO um 07:00 Uhr erhält. |
| **Kategorie** | „Real Estate & ESG" oder „Enterprise IT & Cyber". | Ein PropTech-Artikel → „Real Estate & ESG". |
| **Deep Dive** | Interaktiver Befehl für eine vertiefte Zusammenfassung eines Briefing-Artikels. | `"Deep Dive 2"` für Artikel Nr. 2 im heutigen Briefing. |
| **Whitelisting** | Beschränkung des Bots auf genau eine Telegram-Chat-ID. | Nachrichten von anderen Chat-IDs werden ignoriert. |
| **Dedup-Fenster** | 24-Stunden-Zeitraum, in dem ein Artikel nicht erneut gemeldet wird. | Ein gestern gemeldeter Artikel erscheint heute nicht erneut. |

`[GEÄNDERT]` Geklärt: **Ein** Begriff „Artikel" mit Zustandsübergängen
(Eingegangen → Bewertet → Verworfen/ImBriefing) statt zweier getrennter Begriffe —
siehe `ArtikelStatus` in Abschnitt 7.

---

## 4. Daten & Entitäten

### 4.1 Zentrale Objekte

| Objekt | Identität? | Wichtige Attribute | Beziehungen |
|--------|-----------|--------------------|-------------|
| **Artikel** | Ja (eindeutige ID, z. B. abgeleitet aus Quelle+Link) | Titel, Link, Quelle, VeröffentlichtAm, EingegangenAm, RelevanzScore (nach Bewertung), Kategorie (nach Auswahl), ArtikelStatus | Gehört zu genau einer Quelle; kann in einem Briefing referenziert werden |
| **Briefing** | Ja (Identität = Versanddatum, ein Briefing pro Werktag) | VersandZeitpunkt, VersandStatus, Liste referenzierter Artikel-IDs (max. 5) | Referenziert 0–5 Artikel; referenziert nicht deren internen Zustand, nur die ID |
| **Quelle** | `[GEÄNDERT]` Value Object (feste Konfiguration von 5 Quellen) — bestätigt durch Validierung; Feed-Gesundheits-Tracking ist bewusst kein Domänenkonzept, sondern Architektur-/Monitoring-Thema | Name, FeedURL | Liefert Artikel |
| **Whitelist-Chat-ID** | Nein (Value Object, genau ein konfigurierter Wert) | Chat-ID | Bestimmt Zugriff auf das gesamte System |
| **DeepDiveAnfrage** | `[ANNAHME]` kein eigenständiges, persistiertes Aggregat — kurzlebiger Vorgang, referenziert einen Artikel aus dem aktuellen Briefing | Angefragter Artikel, Zeitpunkt | Bezieht sich auf genau einen Artikel im aktuellen Briefing |

**Aggregat-Kandidaten:** `Artikel` und `Briefing` sind zwei getrennte Aggregate Roots —
`Briefing` referenziert `Artikel` nur über dessen ID (nie direkte Mutation), da
`Artikel` einen eigenen, über Tage hinweg nachverfolgten Lebenszyklus hat (relevant für
das Dedup-Fenster, das Tage-übergreifend prüft).

### 4.2 Datenherkunft

Ausschließlich die RSS-Feeds der fünf definierten Quellen — keine manuelle Eingabe,
keine widersprüchlichen Quellen mit Prioritätskonflikt (jeder Artikel stammt eindeutig
aus genau einer Quelle).

### 4.3 Datenlebenszyklus

Das 24-Stunden-Dedup-Fenster verlangt, dass `Artikel` mindestens so lange nachverfolgt
werden, wie ein erneuter Ingestion-Lauf stattfindet. `[OFFEN]` Ob Artikel darüber
hinaus dauerhaft aufbewahrt werden (insbesondere verworfene, Score < 7, für
Audit-Zwecke), ist eine bereits im PRD offen geführte Frage (→ Architektur-Phase).

---

## 5. Prozesse & Abläufe

### 5.1 Hauptprozess

Zwei zeitlich getrennte Abläufe pro Werktag: der nächtliche Ingestion/Scoring/Synthese-Lauf
(ca. 04:00 Uhr) und die Zustellung (07:00 Uhr).

### 5.2 Prozessschritte

| Schritt | Wer | Was | Output |
|---------|-----|-----|--------|
| 1. Ingestion | System/Scheduler | Ruft alle 5 Feeds ab; neue Links werden als `Artikel` im Status „Eingegangen" angelegt; bereits in den letzten 24h gemeldete Links werden nicht erneut angelegt (Dedup, R2). | Menge neuer „Eingegangen"-Artikel |
| 2. Scoring | Domain Service (LLM-gestützt) | Bewertet jeden „Eingegangen"-Artikel, setzt `RelevanzScore`, Zustandswechsel zu „Bewertet". | Bewertete Artikel |
| 3. Filterung | Domain Service | Artikel mit Score < 7 → Zustand „Verworfen" (R1). | Kandidatenmenge (Score ≥ 7) |
| 4. Synthese | Domain Service | Wählt bis zu 5 Top-Artikel aus der Kandidatenmenge, ordnet jedem eine Kategorie zu, erstellt das `Briefing`-Aggregat für den Tag; gewählte Artikel → Zustand „ImBriefing" (R4). | `Briefing` (Entwurf) |
| 5. Zustellung | Application Service | Sendet um 07:00 Uhr entweder das Briefing oder — falls keine Kandidaten vorhanden — eine explizite Leer-Nachricht (R3); markiert `Briefing` als „Versendet". | Telegram-Nachricht an CIO |

### 5.3 Prozessvarianten

- **Normalfall:** 3–5 Artikel im Briefing.
- **Leerfall (FR-7):** keine Kandidaten → explizite Leer-Nachricht statt Stille.
- **Teilausfall:** eine einzelne Quelle liefert nicht → Ingestion der übrigen Quellen läuft unbeeinflusst weiter (FR-1); wirkt sich nur auf die Menge neuer Artikel aus.

---

## 6. Geschäftsregeln & Invarianten

| # | Regel | Wann greift sie | Bei Verletzung |
|---|-------|-----------------|----------------|
| R1 | Ein Artikel mit `RelevanzScore` < 7 darf niemals im Briefing erscheinen. | Bei der Filterung (Schritt 3). | Artikel bleibt im Zustand „Verworfen", wird nie referenziert. |
| R2 | Ein Artikel darf innerhalb des 24h-Dedup-Fensters nicht zweimal gemeldet werden. | Bei der Ingestion (Schritt 1). | Kein neuer Artikel-Datensatz; bestehender wird nicht erneut berücksichtigt. |
| R3 | Jeden Werktag erfolgt um 07:00 Uhr entweder ein Briefing (3–5 Artikel) oder eine explizite Leer-Nachricht — nie Stille. | Bei der Zustellung (Schritt 5). | Verletzung = Vertrauensbruch (siehe Brief); muss durch Monitoring erkannt werden. |
| R4 | Jeder Artikel im Briefing ist genau einer Kategorie zugeordnet. | Bei der Synthese (Schritt 4). | Briefing gilt als unvollständig/inkonsistent. |
| R5 | Deep Dive ist ausschließlich auf Artikel des aktuellen Tages-Briefings anwendbar — kein freies Themen-Deep-Dive. | Bei jeder Deep-Dive-Anfrage. | Anfrage wird mit Hinweis abgelehnt, dass nur Briefing-Artikel unterstützt werden. |
| R6 | Nur die whitelistete Chat-ID darf Nachrichten/Befehle auslösen. | Bei jeder eingehenden Nachricht. | Nachricht wird ignoriert (keine Reaktion). |
| R7 | `[OFFEN]` Werktage schließen Feiertage nicht automatisch aus. | Bei der Zustellung. | Bis zur Klärung gilt Mo–Fr ohne Feiertagsausnahme als Default. |
| R8 | Top-5-Auswahl sortiert primär nach `RelevanzScore` absteigend; bei Gleichstand gewinnt der neuere Artikel (`EingegangenAm` später). | Bei der Synthese (Schritt 4). | Deterministische Auswahl auch bei Score-Gleichstand sichergestellt. |

---

## 7. Events & Zustandsübergänge

### 7.1 Fachliche Ereignisse

| Event | Auslöser |
|-------|----------|
| `ArtikelEingegangen` | Neuer Artikel wurde bei der Ingestion angelegt. |
| `ArtikelBewertet` | LLM hat einen `RelevanzScore` vergeben. |
| `ArtikelVerworfen` | Score lag unter dem Schwellenwert. |
| `BriefingErstellt` | Top-Artikel für den Tag wurden ausgewählt und kategorisiert. |
| `BriefingVersendet` | Zustellung an den CIO ist erfolgt (Normal- oder Leerfall). |
| `DeepDiveAngefragt` / `DeepDiveBeantwortet` | CIO sendet Deep-Dive-Befehl / Antwort wurde generiert. |

### 7.2 Zustände (`ArtikelStatus`)

```
Eingegangen → Bewertet → Verworfen
                      ↘ QualifiziertNichtAusgewählt
                      ↘ ImBriefing
```

- **Eingegangen → Bewertet:** automatisch durch den Scoring-Prozess.
- **Bewertet → Verworfen:** automatisch, wenn `RelevanzScore` < 7.
- **Bewertet → QualifiziertNichtAusgewählt:** automatisch, wenn Score ≥ 7, der Artikel
  aber bei der Top-5-Auswahl nicht berücksichtigt wird (mehr als 5 Artikel qualifiziert
  an diesem Tag). `[GEÄNDERT]` Durch Validierung ergänzt — unterscheidet fachlich klar
  von „nie relevant gewesen" (`Verworfen`).
- **Bewertet → ImBriefing:** automatisch, wenn Score ≥ 7 **und** der Artikel bei der
  Top-5-Auswahl berücksichtigt wird.

---

## 8. Schnittstellen & Abhängigkeiten

| Richtung | Partner | Format | Häufigkeit | Fehlerfall |
|----------|---------|--------|-----------|------------|
| Upstream | CIO.com, BSI, Haufe Immobilien, Propmodo, Bitkom Presse-Feed | RSS | 1×/Tag (nächtlich) | Einzelne Quelle fällt aus → übrige Quellen unbeeinflusst (FR-1); Monitoring-Konzept noch offen (PRD §8). |
| Downstream | CIO (Telegram) | Markdown-Nachricht | 1×/Werktag (07:00 Uhr) + ad-hoc bei Deep Dive | Zustellung schlägt fehl → `[OFFEN]`, kein Fallback-Kanal spezifiziert (siehe Brief-Risiken). |

## 9. Berechnungen & Algorithmen

| Berechnung | Eingaben | Ergebnis | Varianten | Konfigurierbar |
|------------|----------|----------|-----------|----------------|
| Relevanz-Scoring | Artikeltext, Zielpersona-Beschreibung | `RelevanzScore` (1–10) | Keine Varianten spezifiziert | `[OFFEN]` Bewertungs-Prompt/-Kriterien sind Architektur-/Implementierungsdetail |
| Top-5-Auswahl | Kandidatenmenge (Score ≥ 7) | Bis zu 5 ausgewählte Artikel | Höchste Scores zuerst; bei Gleichstand gewinnt der neuere Artikel (`[GEÄNDERT]` durch Validierung festgelegt, R8) | Nein im MVP |

## 10. Fehler & Ausnahmen

| Fehler | Erkennung | Behandlung | Benachrichtigung | Korrektur |
|--------|-----------|------------|------------------|-----------|
| Quelle nicht erreichbar | Abruf schlägt fehl | Übrige Quellen laufen weiter (FR-1) | `[OFFEN]` Monitoring-Konzept (PRD §8) | — |
| Keine Kandidaten über Schwellenwert | Nach Filterung leer | Explizite Leer-Nachricht statt Stille (FR-7, R3) | Direkt an CIO | — |
| Deep-Dive-Quelle nicht abrufbar | Abruf schlägt fehl (Paywall/404/Timeout) | Klare Fehlermeldung an CIO (FR-9) | Direkt an CIO | — |
| Nachricht von nicht-whitelisteter Chat-ID | Chat-ID-Vergleich | Nachricht wird ignoriert (R6) | Keine | — |

## 11. Qualität & Validierung

| Mechanismus | Beschreibung |
|-------------|--------------|
| Vertrauens-Invariante (R3) | Garantiert tägliche Rückmeldung (Briefing oder Leer-Nachricht) als Qualitätsversprechen. |
| Counter-Metrik (PRD SM-C1) | Verhindert, dass der Schwellenwert so hoch reguliert wird, dass „kein Briefing" zum Dauerzustand wird. |
| `[OFFEN]` Audit Trail | Ob verworfene Artikel und Scoring-Entscheidungen nachvollziehbar gespeichert werden, ist offen (PRD §8). |

---

## Offene Punkte

| # | Abschnitt | Offene Frage | Ansprechpartner |
|---|-----------|--------------|-----------------|
| 1 | 4.3, 11 | Audit-/Historisierungs-Anforderung für verworfene Artikel (bereits PRD-Open-Question, keine DDD-Modellfrage). | Architektur-Phase |

---

## Erkannte Domänenelemente (Vorschläge)

### Entities (Aggregate Roots)
- **Artikel**: eigener Lebenszyklus über `ArtikelStatus` (Eingegangen → Bewertet →
  Verworfen / QualifiziertNichtAusgewählt / ImBriefing), eigene Identität, über Tage
  hinweg nachverfolgt (Dedup).
- **Briefing**: eigene Identität (Versanddatum), referenziert `Artikel` nur über ID.

### Value Objects
- **RelevanzScore**: Ganzzahl 1–10 mit Invariante (Wertebereich).
- **Kategorie**: Enum „Real Estate & ESG" / „Enterprise IT & Cyber".
- **Quelle**: Name + FeedURL, feste Konfiguration (bestätigt durch Validierung als
  Value Object, nicht Entity).
- **ChatId** (Whitelist): einzelner konfigurierter Wert.

### Domain Events
- `ArtikelEingegangen`, `ArtikelBewertet`, `ArtikelVerworfen`, `BriefingErstellt`,
  `BriefingVersendet`, `DeepDiveAngefragt`, `DeepDiveBeantwortet`.

### Geschäftsregeln
- R1–R8 (siehe Abschnitt 6).

### Bounded-Context-Beziehungen
- Keine ausgehenden/eingehenden Bounded Contexts im eigentlichen DDD-Sinn — alle
  Upstream-Quellen sind externe, öffentliche Systeme ohne gemeinsames Domänenmodell
  (Anti-Corruption-Layer-Charakter beim Einlesen externer RSS-Formate ist naheliegend,
  aber Architektur-Thema).

---

## Nächste Schritte

- [x] Abschnitt 1–3 (Kontext, Akteure, Fachsprache)
- [x] Abschnitt 4–7 (Daten/Entitäten, Prozesse, Geschäftsregeln, Events)
- [x] Abschnitt 8–11 (Schnittstellen, Berechnungen, Fehler, Qualität)
- [x] Erkannte Domänenelemente abgeleitet
- [x] Konsistenz geprüft mit `bmad-ddd-validation` (2026-10-24) — 3 von 3 Punkten geklärt
- [ ] Technische Architektur mit `bmad-architecture` (Winston)
