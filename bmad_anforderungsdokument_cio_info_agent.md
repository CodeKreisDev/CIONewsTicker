# BMAD Anforderungsdokument: CIO Info Agent (Real Estate Edition)

## Phase 1: Analysis (Output: Project Brief)
*Zweck: Definition der Problemstellung und der Kernlösung durch den „Analyst“-Agenten.*

* **Projektvision:** Ein KI-gestützter asynchroner Telegram-Bot, der dem Information Overload entgegenwirkt, indem er täglich relevante IT-, Security- und PropTech-News für einen CIO im Immobilieninvestment filtert und zusammenfasst.
* **Zielgruppe:** Der CIO (Fokus: Enterprise IT, Immobilien-Assets, ESG-Regulierung, PropTech-Trends, Datensicherheit).
* **Wertversprechen:** Spart täglich 30–45 Minuten Recherchezeit, stellt sicher, dass kritische Alarme (z.B. BSI) nicht übersehen werden, und bereitet Themen für C-Level-Diskussionen auf.

---

## Phase 2: Planning (Output: Product Requirements Document - PRD)
*Zweck: Übersetzung des Briefings in konkrete funktionale Anforderungen durch den „Product Manager (PM)“-Agenten.*

### 2.1 Ziele & MVP-Constraints (Minimum Viable Product)
* **MVP-Ziel:** Vollautomatisiertes, tägliches Telegram-Briefing (Montag bis Freitag, 07:00 Uhr) mit den 3 bis 5 relevantesten Artikeln.
* **Constraints:**
  * Betriebskosten (LLM API + Hosting) dürfen 20 € pro Monat nicht überschreiten.
  * Das System verarbeitet ausschließlich öffentliche RSS-Feeds und offene APIs (Umgehung von harten Paywalls ist ausgeschlossen).

### 2.2 Functional Requirements (Funktionale Anforderungen)
* **Ingestion:** Das System muss 1x täglich (z. B. 04:00 Uhr nachts) RSS-Feeds der vordefinierten Quellen (CIO.com, BSI, Haufe Immobilien, Propmodo, Bitkom Presse-Feed) abrufen.
* **AI-Scoring:** Ein LLM (z. B. GPT-4o oder Claude) muss jeden abgerufenen Artikel lesen und auf einer Skala von 1–10 auf Relevanz für die Ziel-Persona (CIO im Immobiliensektor) bewerten.
* **Filterung:** Alle Artikel mit einem Relevanz-Score unter 7 werden automatisch verworfen.
* **Synthese:** Das LLM erstellt aus den Top-Artikeln ein kurzes, prägnantes Markdown-Briefing (Kategorisierung in „Real Estate & ESG“ und „Enterprise IT & Cyber“).
* **Interaktivität:** Der Bot muss auf den Chat-Befehl `"Deep Dive [Link/Thema]"` reagieren und eine detaillierte Zusammenfassung der angefragten Quelle zurückgeben.

### 2.3 Non-Functional Requirements (Nicht-funktionale Anforderungen)
* **Zuverlässigkeit:** Keine doppelten Nachrichten; News der letzten 24 Stunden dürfen nicht mehrfach gemeldet werden.
* **Sicherheit:** Der Agent darf keine internen Unternehmensdaten als Kontext erhalten. Er agiert rein auf Basis externer News. Der Telegram-Bot muss auf die Chat-ID des CIOs beschränkt (Whitelisting) werden.

---

