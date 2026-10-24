- source_spec: `_bmad-output/implementation-artifacts/spec-1-1-projekt-grundgeruest-zugriffsschutz.md`
  summary: Audit-/Logging-Spur für akzeptierte und abgelehnte Zugriffsversuche in `is_whitelisted` ergänzen, sobald ein echter Telegram-Message-Handler existiert.
  evidence: Review-Fund BH-7 (Story 1.1): `is_whitelisted` ist bewusst eine pure Funktion ohne Seiteneffekte; Logging gehört in den aufrufenden Handler, der erst mit der echten Long-Polling-Verdrahtung entsteht (nicht Teil von Story 1.1).
- source_spec: `_bmad-output/implementation-artifacts/spec-1-2-artikel-aus-rss-quellen-einlesen.md`
  summary: Operatives Logging/Monitoring für dauerhaft fehlschlagende Quellen (z. B. die unverifizierte Haufe-Immobilien-URL) ergänzen.
  evidence: Review-Fund Story 1.2: `IngestionErgebnis.fehlgeschlagene_quellen` wird aktuell an den Aufrufer zurückgegeben, aber nirgends geloggt/gemeldet. Deckt sich mit PRD §8 Open Question 7 und dem bereits in der Architecture Spine geführten "Monitoring/Alerting"-Deferred-Item — keine neue Entscheidung, nur ein weiterer Beleg für den Bedarf.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-2-artikel-aus-rss-quellen-einlesen.md`
  summary: Feed-URLs konfigurierbar machen (z. B. Umgebungsvariablen-Override), damit ein Fix für die unverifizierte Haufe-Immobilien-URL keinen Code-Redeploy braucht.
  evidence: Review-Fund Story 1.2 (Blind Hunter): aktuell sind alle fünf Feed-URLs in `quellen_konfiguration.py` hartcodiert. Nicht Teil des ursprünglichen Scopes, aber eine sinnvolle Betriebsverbesserung.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-2-artikel-aus-rss-quellen-einlesen.md`
  summary: Datenbank-Index auf `artikel.status` und `artikel.quelle` ergänzen, sobald Story 1.3 (Scoring) tatsächlich nach Status filtert.
  evidence: Review-Fund Story 1.2 (Blind Hunter): noch kein Code fragt nach Status/Quelle; ein Index jetzt wäre spekulativ (Rule of Three, siehe Architecture Spine Prinzipien).
- source_spec: `_bmad-output/implementation-artifacts/spec-1-3-artikel-nach-relevanz-bewerten-und-filtern.md`
  summary: Schema-Migrationsstrategie (z. B. ALTER TABLE statt nur CREATE TABLE IF NOT EXISTS) einführen, bevor das System erstmals echt produktiv betrieben wird.
  evidence: Review-Fund Story 1.3 (Blind Hunter): neue Spalten (`beschreibung`, `relevanz_score`) würden eine bereits bestehende, abweichend strukturierte Datenbank nicht migrieren. Aktuell ohne Schaden, da noch keine echte Produktivbereitstellung existiert.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-3-artikel-nach-relevanz-bewerten-und-filtern.md`
  summary: Retry-Limit bzw. Dead-Letter-Mechanismus für Artikel einführen, deren Scoring dauerhaft fehlschlägt (bleiben sonst für immer im Zustand EINGEGANGEN und werden bei jedem Lauf erneut kostenpflichtig angefragt).
  evidence: Review-Fund Story 1.3 (Blind Hunter): kein Retry-Limit vorhanden. Eigenständiges Scope (Retry-/Circuit-Breaker-Policy-Design), über diese Story hinausgehend.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-3-artikel-nach-relevanz-bewerten-und-filtern.md`
  summary: Optimistic-Concurrency-Control für `ArtikelRepository.aktualisiere` ergänzen (z. B. WHERE-status-Guard + Konfliktbehandlung), sobald ein zweiter Prozess (künftiger Telegram-Listener) tatsächlich gleichzeitig Artikel-Zustände schreibt.
  evidence: Review-Fund Story 1.3 (Edge Case Hunter): aktuell existiert noch kein zweiter schreibender Prozess (Listener noch nicht verdrahtet); volle Optimistic-Concurrency-Control wäre aktuell spekulativer Mehraufwand ohne realen Bedarf (Rule of Three). Die einfachere Existenzprüfung (Fail-Fast bei nicht existierender ID) wurde bereits ergänzt.
