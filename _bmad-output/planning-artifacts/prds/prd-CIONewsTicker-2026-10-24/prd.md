---
title: "CIO Info Agent (Real Estate Edition)"
status: final
created: 2026-10-24
updated: 2026-10-24
---

# PRD: CIO Info Agent (Real Estate Edition)
*Working title — confirm.*

## 0. Document Purpose

Dieses PRD richtet sich an den Product Owner (A.F.), den Domain Modeler, den Architekten
und die Entwicklung. Es baut auf dem [Project Brief](../../briefs/brief-CIONewsTicker-2026-10-24/brief.md)
auf und dupliziert dessen Inhalt nicht, sondern übersetzt ihn in testbare funktionale
Anforderungen. Begriffe aus dem Glossar (§3) werden im gesamten Dokument wörtlich
verwendet. Annahmen sind inline mit `[ASSUMPTION]` markiert und in §9 indexiert.

## 1. Vision

Der CIO Info Agent ist ein asynchroner Telegram-Bot, der einem CIO im
Immobilieninvestment-Umfeld jeden Werktag um 07:00 Uhr ein kuratiertes News-Briefing
liefert — statt eines weiteren ungefilterten Feed-Readers ein Ergebnis: 3–5 Artikel,
die durch ein LLM nach Relevanz für die Zielperson bewertet, gefiltert und kategorisiert
wurden. Kritische Warnungen (z. B. vom BSI) sollen so verlässlich ankommen, dass der CIO
sich auf das System verlässt statt auf eigenes manuelles Überfliegen. Der Chat-Befehl
„Deep Dive" erlaubt bei Bedarf sofortigen Tiefeneinstieg in ein Thema.

## 2. Zielnutzer

### 2.1 Jobs To Be Done

- Morgens in unter 2 Minuten wissen, was heute für meine Rolle (Enterprise-IT,
  Immobilien-Assets, ESG, Security) wirklich zählt.
- Mich darauf verlassen können, dass eine kritische Sicherheitswarnung (BSI) nicht in
  der Informationsflut untergeht.
- Themen so aufbereitet bekommen, dass ich sie direkt in eine C-Level-Diskussion
  einbringen kann.
- Bei einem interessanten Thema sofort tiefer einsteigen können, ohne selbst zu suchen.

### 2.2 Non-Users (v1)

Jede weitere Rolle außer dem einen CIO — insbesondere CISO, weitere Führungskräfte oder
Teammitglieder. Das System ist bewusst nicht mandantenfähig (siehe Brief); eine
Mehrbenutzer-Erweiterung ist kein Ziel dieses PRDs.

### 2.3 Key User Journeys

*Leichtgewichtig gehalten — ein Operator, ein Kanal, kein UX-lastiges Produkt.*

- **UJ-1. Der CIO startet seinen Tag mit dem Briefing.** Der CIO öffnet werktags um
  07:00 Uhr Telegram und liest das kategorisierte Briefing („Real Estate & ESG" /
  „Enterprise IT & Cyber") in unter 2 Minuten. **Edge case:** Erreicht kein Artikel den
  Relevanz-Schwellenwert oder schlagen alle Feeds fehl, erhält der CIO stattdessen eine
  explizite „Kein relevantes Briefing heute"-Nachricht (realisiert FR-7) — nie Stille.
- **UJ-2. Der CIO vertieft ein Thema per Deep Dive.** Der CIO sendet `"Deep Dive
  [Link/Thema]"` zu einem Artikel aus dem aktuellen Tages-Briefing (per Link oder
  Referenz) und erhält eine detaillierte Zusammenfassung der Quelle. **Edge case:** Ist
  die Quelle nicht abrufbar (Paywall, 404, Timeout), antwortet der Bot mit einer klaren
  Fehlermeldung statt zu schweigen (realisiert FR-9).

## 3. Glossar

- **Artikel** — ein einzelner über RSS abgerufener News-Beitrag einer Quelle.
- **Quelle** — einer der fünf fest definierten RSS-Feeds (CIO.com, BSI, Haufe
  Immobilien, Propmodo, Bitkom Presse-Feed).
- **Relevanz-Score** — vom LLM vergebene Zahl 1–10, die die Relevanz eines Artikels für
  die Zielperson „CIO im Immobiliensektor" ausdrückt.
- **Schwellenwert** — der Score-Grenzwert 7; Artikel darunter werden verworfen.
- **Briefing** — das tägliche, kategorisierte Markdown-Dokument aus den Top-Artikeln,
  zugestellt per Telegram.
- **Kategorie** — „Real Estate & ESG" oder „Enterprise IT & Cyber"; jedem Artikel im
  Briefing eindeutig zugeordnet.
- **Deep Dive** — der interaktive Chat-Befehl, der eine vertiefte Zusammenfassung einer
  einzelnen Quelle liefert.
- **Whitelisting** — die Beschränkung des Bots auf genau eine konfigurierte
  Telegram-Chat-ID.
- **Dedup-Fenster** — der 24-Stunden-Zeitraum, innerhalb dessen ein Artikel nicht
  erneut gemeldet werden darf.

## 4. Features

### 4.1 Ingestion

**Beschreibung:** Das System ruft einmal täglich, nachts gegen 04:00 Uhr, die RSS-Feeds
der fünf definierten Quellen ab und bereitet neue Artikel für die Bewertung vor.
`[ASSUMPTION]` Die genaue Uhrzeit (04:00) ist ein Richtwert aus dem Ursprungsdokument,
keine harte Vorgabe.

#### FR-1: Täglicher Feed-Abruf

Das System ruft 1× täglich die RSS-Feeds aller fünf definierten Quellen ab.

**Consequences (testable):**
- Alle fünf Quellen werden bei jedem Lauf angefragt, unabhängig davon, ob eine Quelle
  beim letzten Lauf fehlgeschlagen ist.
- Ein Fehlschlag einer einzelnen Quelle blockiert nicht den Abruf der übrigen Quellen.

#### FR-2: Deduplizierung über 24 Stunden

Das System darf keinen Artikel erneut melden, der innerhalb der letzten 24 Stunden
bereits im Briefing enthalten war.

**Consequences (testable):**
- Ein Artikel, der gestern im Briefing war, erscheint heute nicht erneut, selbst wenn
  er weiterhin im Feed der Quelle steht.
- Ein inhaltlich identischer Artikel von zwei verschiedenen Quellen gilt
  `[ASSUMPTION]` als zwei separate Artikel (keine inhaltliche Deduplizierung über
  Quellen hinweg im MVP) — nur die Mehrfachmeldung derselben Quelle/desselben Links
  wird verhindert.

### 4.2 AI-Scoring & Filterung

**Beschreibung:** Jeder neu abgerufene Artikel wird von einem LLM anhand der Zielperson
„CIO im Immobiliensektor" bewertet; nur Artikel über dem Schwellenwert gelangen in die
Synthese.

#### FR-3: Relevanz-Scoring

Das System bewertet jeden abgerufenen Artikel auf einer Skala von 1–10 hinsichtlich
seiner Relevanz für die Ziel-Persona.

**Consequences (testable):**
- Jeder Artikel erhält genau einen Relevanz-Score vor der Filterung.
- Die Bewertungskriterien berücksichtigen die in §2.1 genannten Themenfelder
  (Enterprise-IT, Immobilien-Assets, ESG, PropTech, Security).

#### FR-4: Filterung nach Schwellenwert

Artikel mit einem Relevanz-Score unter 7 werden automatisch verworfen und erscheinen
nicht im Briefing.

**Consequences (testable):**
- Kein Artikel mit Score < 7 erscheint jemals im zugestellten Briefing.
- Verworfene Artikel werden nicht dauerhaft gespeichert `[ASSUMPTION]` — es sei denn,
  Architektur/Betrieb verlangt sie für Debugging/Audit (offene Frage, siehe §8).

### 4.3 Synthese & Zustellung (Daily Briefing)

**Beschreibung:** Aus den gefilterten Top-Artikeln erstellt das LLM ein kurzes,
kategorisiertes Markdown-Briefing und stellt es werktags pünktlich zu. Realisiert UJ-1.

#### FR-5: Kategorisierte Synthese

Das System fasst die Top-Artikel (max. 5) in einem Markdown-Briefing zusammen,
kategorisiert in „Real Estate & ESG" und „Enterprise IT & Cyber".

**Consequences (testable):**
- Jeder Artikel im Briefing ist genau einer der beiden Kategorien zugeordnet.
- Das Briefing enthält zwischen 3 und 5 Artikeln, sofern mindestens 3 Artikel den
  Schwellenwert erreichen.

#### FR-6: Pünktliche Zustellung

Das System stellt das Briefing werktags (Montag–Freitag) um 07:00 Uhr per Telegram an
die whitelistete Chat-ID zu.

**Consequences (testable):**
- An Samstagen, Sonntagen und `[ASSUMPTION]` Feiertagen (nicht im Ursprungsdokument
  spezifiziert, als Open Question in §8 markiert) wird kein Briefing verschickt.
- Die Zustellung erfolgt bis spätestens 07:00 Uhr Ortszeit.

#### FR-7: Explizite Information bei leerem Ergebnis

Erreicht an einem Tag kein Artikel den Schwellenwert, oder schlagen alle Feeds fehl,
sendet das System eine explizite „Kein relevantes Briefing heute"-Nachricht statt gar
keine Nachricht zu senden.

**Consequences (testable):**
- Der CIO erhält an jedem Werktag um 07:00 Uhr entweder ein Briefing (FR-6) oder eine
  explizite Leer-Nachricht — niemals Stille.
- Die Leer-Nachricht unterscheidet sich erkennbar von einem Systemausfall (z. B. durch
  klaren Hinweistext), damit der CIO nicht fälschlich einen Fehler vermutet.

**Feature-specific NFRs:**
- Diese Garantie ist zentral für das Vertrauens-Versprechen aus dem Brief
  ("nichts Kritisches wird übersehen") und darf durch keine spätere Optimierung
  unterlaufen werden (siehe Counter-Metrik SM-C1).

### 4.4 Interaktivität (Deep Dive)

**Beschreibung:** Der Bot reagiert auf einen expliziten Chat-Befehl mit einer vertieften
Zusammenfassung einer Quelle. Realisiert UJ-2.

#### FR-8: Deep-Dive-Befehl

Der CIO kann per Chat-Befehl `"Deep Dive [Link/Thema]"` eine detaillierte
Zusammenfassung eines Artikels aus dem **aktuellen Tages-Briefing** anfordern — entweder
durch Einfügen des Artikel-Links oder durch Referenzierung des Artikels aus dem
Briefing (z. B. per Nummer/Titel).

**Consequences (testable):**
- Der Befehl funktioniert für jeden Artikel, der im aktuellen Tages-Briefing enthalten
  ist, unabhängig davon, ob per Link oder per Referenz (Nummer/Titel) angesprochen.
- Die Antwort ist eine eigenständige, tiefere Zusammenfassung — keine bloße Wiederholung
  des Briefing-Eintrags.

**Out of Scope:**
- Keine Umgehung von Paywalls (siehe Guardrails, §Constraints).
- **Kein freies Themen-/Stichwort-basiertes Deep Dive außerhalb des Tages-Briefings** —
  eine LLM-Websuche zu einem beliebigen, nicht im Briefing enthaltenen Thema ist explizit
  nicht Teil des MVP (bewusste Entscheidung, hält Kosten und Komplexität niedrig).
- Externe, vom CIO frei eingefügte Links ohne Bezug zum Tages-Briefing werden im MVP
  nicht unterstützt.

#### FR-9: Fehlerrückmeldung bei nicht abrufbarer Quelle

Ist die beim Deep Dive angefragte Quelle nicht abrufbar (Paywall, 404, Timeout),
antwortet der Bot mit einer klaren, verständlichen Fehlermeldung.

**Consequences (testable):**
- Der CIO erhält innerhalb einer angemessenen Zeit `[ASSUMPTION]` eine Antwort — nie
  dauerhaftes Schweigen des Bots.
- Die Fehlermeldung benennt den Grund so weit erkennbar (z. B. "Quelle nicht
  erreichbar" vs. "Inhalt hinter Paywall").

### 4.5 Zugriffskontrolle

**Beschreibung:** Der Bot ist exklusiv für den einen CIO nutzbar.

#### FR-10: Chat-ID-Whitelisting

Das System verarbeitet ausschließlich Nachrichten von der konfigurierten,
whitelisteten Telegram-Chat-ID; Nachrichten von anderen Absendern werden ignoriert.

**Consequences (testable):**
- Eine Nachricht von einer nicht whitelisteten Chat-ID erzeugt keine Bot-Reaktion
  `[ASSUMPTION: stilles Ignorieren statt Fehlermeldung, um keine Rückschlüsse auf die
  Existenz/Konfiguration des Bots zuzulassen]`.
- Es existiert zu jedem Zeitpunkt genau eine whitelistete Chat-ID (siehe Brief:
  Single-User-Entscheidung).

## 5. Non-Goals (Explicit)

- Kein Web-Dashboard, keine mobile App — Telegram ist der einzige Kanal.
- Keine Mehrbenutzer- oder Mandantenfähigkeit (bewusste Architekturentscheidung).
- Keine Umgehung von Paywalls — ausschließlich öffentliche RSS-Feeds und offene APIs.
- Kein interner Unternehmenskontext als LLM-Input — der Agent arbeitet ausschließlich
  auf Basis externer, öffentlicher News.
- Keine zusätzlichen Quellen über die fünf definierten hinaus im MVP.
- Kein Abruf vergangener Briefings auf Zuruf im MVP (siehe Open Question §8.1).

## 6. MVP Scope

### 6.1 In Scope

- Täglicher automatisierter RSS-Abruf der fünf definierten Quellen (FR-1).
- Deduplizierung über ein 24-Stunden-Fenster (FR-2).
- LLM-Relevanz-Scoring und Filterung bei Schwellenwert 7 (FR-3, FR-4).
- Kategorisierte Markdown-Synthese (FR-5).
- Pünktliche Werktags-Zustellung 07:00 Uhr inkl. expliziter Leer-Nachricht (FR-6, FR-7).
- Interaktiver Deep-Dive-Befehl inkl. Fehlerrückmeldung (FR-8, FR-9).
- Chat-ID-Whitelisting (FR-10).

### 6.2 Out of Scope for MVP

- Mehrbenutzerfähigkeit / weitere Rollen — bewusst dauerhaft ausgeschlossen, keine
  v2-Planung (siehe Brief).
- Abruf vergangener Briefings, manueller "Jetzt aktualisieren"-Befehl — potenzielle v2
  Erweiterung `[NOTE FOR PM]`, siehe Open Questions.
- Erweiterung der Quellenliste über die fünf definierten hinaus — v2, abhängig von
  Nutzungserfahrung.
- Feiertagskalender-Logik für die Zustellung — v2, siehe Open Question §8.2.

## 7. Success Metrics

**Primary**
- **SM-1**: Pünktlichkeit — Briefing oder Leer-Nachricht (FR-7) trifft werktags bis
  07:00 Uhr ein. Ziel: 100 %. Validates FR-6, FR-7.
- **SM-2**: Relevanz-Trefferquote — CIO bewertet subjektiv ≥ 80 % der gelieferten
  Artikel als tatsächlich relevant. Validates FR-3, FR-4, FR-5.
- **SM-3**: Null verpasste kritische Alarme (insb. BSI) im Beobachtungszeitraum.
  Validates FR-3, FR-4.

**Secondary**
- **SM-4**: Kostendisziplin — Betriebskosten (LLM-API + Hosting) bleiben dauerhaft
  unter 20 €/Monat. Validates Constraints/Guardrails (Cost).

**Counter-metrics (do not optimize)**
- **SM-C1**: Anteil der Tage mit „Kein relevantes Briefing heute"-Nachricht (FR-7) darf
  nicht durch Hochregulieren des Schwellenwerts künstlich niedrig gehalten werden, wenn
  dadurch tatsächlich relevante Artikel verworfen werden. Counterbalances SM-2, SM-3 —
  ein Scoring, das nie „kein Briefing" meldet, ist verdächtig, kein Erfolg.

## 8. Open Questions

1. Soll der CIO ein vergangenes Briefing nachträglich abrufen können (z. B. "zeig mir
   Montag")? *(Kandidat für v2, siehe §6.2.)*
2. Soll es einen manuellen "Jetzt aktualisieren"-Befehl unabhängig vom 07:00-Zeitplan
   geben? *(Kandidat für v2.)*
3. Gilt die 07:00-Uhr-Zustellung auch an (regionalen) Feiertagen, oder pausiert das
   System dann? *(Betrifft FR-6.)*
4. Werden verworfene (Score < 7) Artikel für Debugging/Audit-Zwecke dennoch
   gespeichert? *(Betrifft FR-4, ggf. Datenhaltungs-/Architekturfrage.)*
5. Konkreter LLM-Provider, Kostenmodell und Hosting-Plattform → Architektur-Phase
   (Winston), nicht Teil dieses PRDs.
6. Monitoring-/Alerting-Konzept bei wiederholten Feed-Ausfällen → Architektur-Phase.
7. Herkunft und Verwaltung von Telegram-Bot-Token und Chat-ID (Secrets-Handling) →
   Architektur-Phase.

## 9. Assumptions Index

- §4.1 FR-1 — Abrufzeit „ca. 04:00 Uhr" ist Richtwert, keine harte Vorgabe.
- §4.1 FR-2 — Keine inhaltliche Cross-Quellen-Deduplizierung im MVP, nur pro
  Quelle/Link.
- §4.2 FR-4 — Verworfene Artikel werden standardmäßig nicht dauerhaft gespeichert.
- §4.3 FR-6 — Feiertagslogik nicht spezifiziert, als Open Question geführt.
- §4.4 FR-8 — Deep Dive ist auf Artikel des aktuellen Tages-Briefings beschränkt (per
  Link oder Referenz); freies Themen-basiertes Deep Dive ist bewusst Out of Scope
  (bestätigte Entscheidung, keine Annahme mehr).
- §4.4 FR-9 — "Angemessene Zeit" für Fehlerrückmeldung nicht quantifiziert.
- §4.5 FR-10 — Nicht-whitelistete Absender werden still ignoriert, nicht mit
  Fehlermeldung beantwortet.

---

## Constraints and Guardrails

**Cost**
- Harte Obergrenze: Betriebskosten (LLM-API + Hosting) dürfen 20 €/Monat nicht
  überschreiten (SM-4). `[NOTE FOR PM]` Bei LLM-Preisänderungen oder steigendem
  Artikelvolumen erneut prüfen.

**Privacy**
- Der Agent erhält keinerlei internen Unternehmenskontext als LLM-Input. Er arbeitet
  ausschließlich auf Basis extern-öffentlicher News (RSS-Feeds, offene APIs).

**Security**
- Zugriff ausschließlich über die whitelistete Telegram-Chat-ID (FR-10).
- Keine Umgehung von Paywalls oder technischen Zugriffsbeschränkungen der Quellen.

## Cross-Cutting NFRs

- **Zuverlässigkeit:** Keine doppelten Nachrichten innerhalb von 24 Stunden (FR-2);
  niemals Stille statt einer erwarteten täglichen Nachricht (FR-6, FR-7).
- **Robustheit gegenüber Quellenausfällen:** Der Ausfall einzelner Feeds darf weder den
  gesamten Lauf blockieren noch unbemerkt bleiben (FR-1, FR-7).
- **Kostenkontrolle:** siehe Guardrails oben; technische Umsetzung (Budget-Caps,
  Modellwahl) ist Architektur-Thema.
