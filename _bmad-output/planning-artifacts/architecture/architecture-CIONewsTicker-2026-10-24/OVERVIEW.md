# Architektur-Übersicht: CIO Info Agent (Real Estate Edition)

*Lesbares Begleitdokument zur [ARCHITECTURE-SPINE.md](./ARCHITECTURE-SPINE.md). Die Spine
ist die knappe, verbindliche Quelle der Wahrheit; dieses Dokument erklärt die
Entscheidungen und ihre Begründung für den menschlichen Nachleser.*

## Warum diese Architektur?

Das System ist bewusst klein gehalten: ein Einzelnutzer, ein Kanal (Telegram), ein
hartes Kostenlimit (20 €/Monat), kein Anspruch auf Skalierung. Die Architektur folgt
Winstons Prinzip „Boring Technology für Stabilität" — jede Entscheidung wählt die
unaufregendste Option, die den Job zuverlässig macht.

## Die wichtigsten Entscheidungen im Klartext

### Python statt Node.js

Beide Sprachen hätten funktioniert. Python gewinnt, weil die drei zentralen Bausteine
(RSS-Parsing, Telegram-Bot-Framework, Scheduling) dort besonders ausgereift und gut
dokumentiert sind, und weil ein Einzelentwickler von einem einheitlichen, gut
unterstützten Ökosystem profitiert. Verifizierte aktuelle Versionen (Stand 2026-10-24):
Python 3.15.1, `python-telegram-bot` 22.8, `feedparser` 6.0.14, `APScheduler` 3.11.3.

### Long Polling statt Webhook

Ein Webhook würde einen öffentlich erreichbaren HTTPS-Endpunkt verlangen — TLS-Zertifikat,
Domain, Registrierung bei Telegram. Long Polling braucht nichts davon: Der Bot baut
ausgehende Verbindungen auf, ist von außen unsichtbar. Für ein Single-User-System mit
Chat-ID-Whitelisting ist das nicht nur einfacher, sondern auch sicherer — es gibt
schlicht keinen eingehenden Angriffsvektor.

### Eine einzelne VPS statt Serverless

Serverless (z. B. Cloud Functions) wäre bei diesem Traffic-Volumen vermutlich sogar
etwas günstiger. Aber: Die Deep-Dive-Interaktivität + Long Polling brauchen einen
durchgehend laufenden Prozess — das passt nicht gut zu klassischem Serverless (das für
kurzlebige, ereignisgetriebene Aufrufe gedacht ist). Eine kleine Dauer-VM (z. B. Hetzner
CX22-Klasse, verifiziert ~4,49–5,39 €/Monat) vereint nächtlichen Batch-Lauf und
Long-Polling-Listener in einem Prozess, ohne Mehrfach-Deployment, ohne Webhook-Komplexität.
Das lässt bei 20 €/Monat Gesamtbudget komfortabel ~15 € für LLM-Kosten übrig.

### LLM-Anbindung als austauschbarer Port

Welcher LLM-Anbieter konkret verwendet wird, ist bewusst **kein** architektonisch
bindender Entscheid — das Original-Anforderungsdokument nannte „GPT-4o oder Claude" nur
beispielhaft. Die Architektur bindet nur: Scoring und Deep-Dive laufen über ein
`LLMPort`-Interface; welcher Adapter dahinter steckt, ist austauschbar. Als
Kostenrichtwert dient ein günstiges Small-Tier-Modell (vergleichbar GPT-5.6 Luna,
~0,20 $/1,20 $ je Mio. Token) — bei diesem Tagesvolumen fallen dafür nur Cent-Beträge
pro Tag an.

### SQLite statt verwalteter Datenbank

Für Artikel-Zustand, Dedup-Fenster und Briefing-Historie reicht eine eingebettete
SQLite-Datei vollkommen aus — ein separater, kostenpflichtiger Datenbank-Dienst wäre
bei diesem Datenvolumen unverhältnismäßig.

## Was absichtlich offen bleibt

Diese Punkte sind keine vergessenen Entscheidungen, sondern bewusst in die Zukunft
verschoben, bis echte Nutzungserfahrung eine Richtung nahelegt:

- Ob verworfene Artikel für ein Audit aufbewahrt werden.
- Wie mit Feiertagen bei der Zustellung umgegangen wird.
- Ein dediziertes Monitoring-/Alerting-Konzept für Feed-Ausfälle (Start: einfaches
  Logging).
- Manueller Refresh-Befehl und Abruf vergangener Briefings (v2-Kandidaten).
- Mehrbenutzerfähigkeit — bewusst **kein** Architektur-Pfad vorgesehen, siehe
  Single-User-Entscheidung im Brief.

## Wie die Schichten zusammenspielen

```
interfaces  →  application  →  domain
                    ↑
infrastructure ─────┘  (implementiert Ports, die domain/application definieren)
```

Die Domäne (`Artikel`, `Briefing`, Geschäftsregeln) weiß nichts von Python-Telegram-Bot,
SQLite oder dem LLM-Provider. Diese Details leben ausschließlich in `infrastructure/`
und werden über Port-Interfaces angebunden — ein Wechsel des LLM-Anbieters oder der
Datenbank berührt niemals die fachliche Logik.

## Nächste Schritte

1. `bmad-create-epics-and-stories` — Epics und User Stories aus PRD + dieser Spine ableiten.
2. `bmad-sprint-planning` — Implementierungsreihenfolge festlegen.
3. `bmad-build` (Amelia) — TDD-Implementierung je Story, mit den DDD-Prinzipien und
   dieser Spine als Leitplanken.
