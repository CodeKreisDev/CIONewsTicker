# DDD- & Clean-Code-Prinzipien (sprachagnostisch)

Grundsätze für domänengetriebene Entwicklung, unabhängig von Programmiersprache,
Framework oder Infrastruktur. Diese Prinzipien werden vom Domain Modeler, vom
Entwickler- und vom Architektur-Agenten als geteilte Leitplanken getragen.

## Taktische DDD-Bausteine

- **Ubiquitous Language:** Eine einheitliche Fachsprache zwischen Fachexperten und
  Entwicklung. Begriffe im Code = Begriffe im Fachgespräch.
- **Bounded Context:** Klar abgegrenzte Kontextgrenzen mit eigener, in sich
  konsistenter Sprache.
- **Entity:** Objekt mit einer Identität, die über die Zeit stabil bleibt.
- **Value Object:** Unveränderliches Objekt ohne eigene Identität, definiert durch
  seine Werte.
- **Aggregate:** Zusammengehörige Objekte mit genau einem Aggregate Root als
  Einstiegspunkt und Hüter der Invarianten.
- **Domain Event:** Fachlich relevantes Ereignis, benannt in der Vergangenheitsform.
- **Repository:** Abstraktion für den Zugriff auf Aggregate, frei von
  Infrastruktur-Details in der Signatur.
- **Domain Service:** Domänenlogik, die zu keiner einzelnen Entität gehört.
- **Application Service:** Orchestriert Use Cases, hält selbst keine Geschäftsregeln.

## Clean Architecture – Schichten & Abhängigkeitsregel

Die Schichten sind konzentrisch; Abhängigkeiten zeigen **immer nach innen** zur Domäne:

| Schicht | Verantwortung |
|---------|---------------|
| **Domain** | Entities, Value Objects, Domain Services, Domain Events, Invarianten |
| **Application** | Application Services, Use Cases, Commands/Queries, Orchestrierung |
| **Infrastructure** | Repository-Implementierungen, externe Adapter, Persistenz |
| **Interfaces** | API/Controller/UI, DTOs, Mapping |

**Regeln:**

- Die Domänenschicht ist **frei von Infrastruktur- und Framework-Abhängigkeiten**.
- Interfaces (Controller/UI) rufen **ausschließlich Application Services** auf –
  niemals direkt Repositories oder Domänen-Objekte mutieren.
- Jede Use-Case-Logik gehört in den Application Service, nicht in den Controller.
- Repositories werden nur in Application Services oder Infrastructure-Klassen genutzt.
- Externe Kontexte werden über **Ports** (Interfaces in der Domäne/Application)
  angebunden, die Infrastruktur liefert die Adapter.

## Anemic Domain Model vermeiden

- Logik, die nur die eigenen Daten eines Objekts verwendet, gehört **in das Objekt**.
- Domain Services nur für Logik, die mehrere Aggregate orchestriert oder
  infrastrukturnah ist.
- Faustregel: Wenn ein Service nur Daten eines Objekts transformiert, verschiebe die
  Methode in das Objekt.

## Aggregate-Grenzen

- Innere Entitäten werden **ausschließlich über den Aggregate Root** verändert –
  externe Klassen rufen nie direkt Methoden auf inneren Entitäten auf.
- Factory-Methoden liefern fachlich **vollständig initialisierte** Aggregate.
- Getter auf innere Sammlungen geben **unveränderliche** Sichten zurück.
- Transaktionsgrenzen folgen den Aggregate-Grenzen: eine Transaktion ändert
  idealerweise genau ein Aggregat.

## Domain Events

- Aggregate publizieren Domain Events; Listener reagieren darauf.
- Jeder Event-Typ hat mindestens einen Konsumenten – Events ohne Listener sind
  toter Code.
- Event-Listener gehören in die Application-Schicht (Orchestrierung), nicht in die
  Domäne.
- Payloads sind vollständig, aber minimal.

## Fehlerbehandlung

- Eine **fachliche Exception-Hierarchie** unter einer gemeinsamen Domain-Exception:
  - Nicht gefundene Entitäten → eigene „NotFound"-Art
  - Geschäftsregel-Verletzungen → eigene „BusinessRule"-Art
  - Validierungsfehler → eigene „Validation"-Art
- **Keine generischen technischen Exceptions in der Domäne** – immer eine sprechende,
  fachliche Unterklasse verwenden.
- **Fail-Fast:** am Eintrittspunkt und im Konstruktor von Value Objects validieren,
  früh mit aussagekräftiger Meldung scheitern.
- Zentrale Fehlerübersetzung an der API-Grenze, mit konsistentem Fehlerformat.

## Validierung & Immutability

- Value Objects validieren ihre Invarianten im Konstruktor und sind unveränderlich.
- Eingaben werden konsequent geprüft; leere oder sinnlose Werte werden abgelehnt.
- Fehlender Wert wird nur dort zugelassen, wo „kein Wert" fachlich definiert ist –
  dann explizit als optionaler Typ, nicht als stiller Null-Durchgriff.

## Benennung

- Namen folgen der Ubiquitous Language – lieber fachlich treffend als technisch kurz.
- Konsistente, projektweit einheitliche Namenskonventionen.
- Toten Code löschen statt als veraltet zu markieren; kein Abwärtskompatibilitäts-
  Ballast ohne klaren Entfernungspfad.

## Tests

- Akzeptanztests in lesbarer Fachsprache, sodass Fachexperten sie validieren können.
- Unit-Tests für Domänenlogik sind Pflicht.
- Integrationstests für Application Services und Repositories.
- Randfälle bewusst testen: fehlende Werte, negative Werte, Rundung, Grenzwerte.

## Prioritäten bei Regelkonflikten

1. Korrekte fachliche Domänenlogik
2. Sicherheit und Stabilität
3. Kleine, nachvollziehbare Änderungen
4. Konsistenz mit der bestehenden Struktur

## DDD-Code-Review-Checkliste (sprachagnostisch)

**Fachlichkeit & Modell**
- [ ] Logik im richtigen Objekt (kein Anemic Domain Model)
- [ ] Ubiquitous Language konsistent verwendet
- [ ] Aggregate-Grenzen eingehalten – innere Entitäten nur über den Root verändert
- [ ] Invarianten explizit durchgesetzt

**Architektur**
- [ ] Domänenschicht frei von Infrastruktur/Framework
- [ ] Controller/UI rufen nur Application Services
- [ ] Use-Case-Logik im Application Service, nicht im Interface-Layer
- [ ] Externe Kontexte nur über Ports/Adapter angebunden

**Events & Fehler**
- [ ] Jeder Domain-Event-Typ hat einen Listener
- [ ] Nur fachliche Exceptions aus der Domäne, keine generischen technischen

**Qualität**
- [ ] Unveränderlichkeit bei Value Objects
- [ ] Sprechende Namen, keine Duplikate
- [ ] Akzeptanz- und Unit-Tests vorhanden, Randfälle abgedeckt, alle grün
