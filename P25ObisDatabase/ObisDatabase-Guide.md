# ObisDatabase – Technischer Leitfaden (Überarbeitet)

> YAML‑Frontmatter‑Manager für Markdown/Obsidian. Fokus: konsistente Metadaten, deterministische Ausgabe, skalierbar für große Vaults/Repos.

---

## Inhaltsverzeichnis
1. [Überblick und Zweck](#überblick-und-zweck)
2. [Installation und Setup](#installation-und-setup)
3. [Grundlegende Verwendung](#grundlegende-verwendung)
4. [Konfiguration](#konfiguration)
5. [Funktionsweise im Detail](#funktionsweise-im-detail)
6. [Beispiele und Anwendungsfälle](#beispiele-und-anwendungsfälle)
7. [Erweiterte Features](#erweiterte-features)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [FAQ](#faq)

---

## 1. Überblick und Zweck

### 1.1 Zielsetzung
- Automatisches Erstellen/Aktualisieren von YAML‑Frontmatter in `.md`‑Dateien.
- Strenge Reihenfolge und deterministische Werte über Templates.
- Skalierbarkeit für große Verzeichnisbäume mit Ausschlüssen und Anker‑Scope.

### 1.2 Kernfunktionen
- Rekursives Durchlaufen eines Wurzelverzeichnisses (`--root`).
- Laden einer YAML/INI‑Vorlage aus einer von mehreren Konfigurationsdateien.
- Platzhalter‑System für Pfade, Dateinamen und Datum (%rootN%, %folderN%, %data%, %datum%).
- Zwei Zusammenführungsmodi: `strict` (Default) und `merge`.
- Behalten vorhandener Werte via `%wert%`.
- Leereinträge und Listenelement‑Entfernung über `=leer=`.
- Selektive Verarbeitung (Anker `base_root`, `scope_under_base_root`).
- Exklusionsfilter für Ordner (mit Globs, z. B. `.git`, `node_modules`, `.obsidian`).

### 1.3 Abgrenzung
- Kein Rename/Move von Dateien (nur Frontmatter‑Manipulation).
- Kein Dry‑Run; Änderungen werden direkt geschrieben (Backup empfohlen).
- Fokus auf UTF‑8, Unix‑Zeilenenden (LF); Quoting über YAML.

### 1.4 Typische Einsatzszenarien
- Einheitliche Projektdokumentation (Projekt/Task/Semester/Kurs‑Metadaten).
- Studien/Lehr‑Vaults mit hierarchischer Ordnerlogik.
- Wissensdatenbanken/Wiki‑Bereiche mit stabilem Anker.
- Zettelkasten mit reproduzierbarem Feldschema/IDs.

### 1.5 Ergebnisqualität
- Idempotent: erneuter Lauf liefert identisches Frontmatter (bei unveränderten Dateien/Konfigurationen).
- Reihenfolge der Felder exakt gemäß Vorlage.
- Unicode‑sicher (YAML mit `allow_unicode: true`).

---

## 2. Installation und Setup

### 2.1 Voraussetzungen
- Python ≥ 3.8 (empfohlen; funktioniert ab 3.6).
- Paket: `PyYAML`.
- Zugriff auf Dateisystem (Lesen/Schreiben in Vault/Repo).

### 2.2 Installation prüfen
```bash
python --version
python -c "import sys; print(sys.version)"
```

### 2.3 Abhängigkeit installieren
```bash
pip install pyyaml
# oder nutzerspezifisch
pip install --user pyyaml
```

### 2.4 Projektstruktur (Beispiel)
```
Vault/
├─ ObisDatabase.py
├─ ObisDatabase.ini                 # oder YAML.ini etc. (siehe 4.2)
├─ SE1/
│  ├─ BWL01/
│  │  └─ Notiz1.md
│  └─ STAT02/
│     └─ Übung1.md
└─ SE2/
   └─ PROG01/
      └─ Projekt.md
```

### 2.5 Rechte & Encoding
- Stelle sicher, dass Schreibrechte bestehen.
- Dateien sind UTF‑8; Editor entsprechend konfigurieren.

### 2.6 Backup (dringend empfohlen)
```bash
cp -r Vault Vault-backup-$(date +%Y%m%d)
# oder mit Git
git add . && git commit -m "Backup vor ObisDatabase"
```

---

## 3. Grundlegende Verwendung

### 3.1 Standardlauf (aktuelles Verzeichnis)
```bash
python ObisDatabase.py
```

### 3.2 Mit explizitem Root
```bash
python ObisDatabase.py --root /pfad/zu/Vault
```

### 3.3 Typischer Workflow
1. Backup anlegen.
2. Konfiguration erstellen/anpassen (siehe Abschnitt 4).
3. Testlauf auf kleinem Unterbaum (z. B. `./SE1/BWL01`).
4. Stichproben prüfen (Frontmatter, Reihenfolge, Werte).
5. Vollständiger Lauf am Wurzelpfad.

### 3.4 Konsolen‑Ausgabe interpretieren
```
[OK]   aktualisiert: SE1/BWL01/Notiz1.md
[SKIP] unverändert:  SE1/README.md
...
Fertig. Dateien gesamt: 25, geändert: 18.
```
- `[OK] aktualisiert`: Frontmatter wurde geschrieben/geändert.
- `[SKIP] unverändert`: Datei hatte bereits identisches Ziel‑Frontmatter.
- Zusammenfassung: Gesamtanzahl und geänderte Dateien.

### 3.5 Idempotenz
- Mehrfacher Lauf mit gleicher Vorlage und unveränderten Dateien erzeugt keine weiteren Änderungen.

### 3.6 Grenzen
- Nur `.md`‑Dateien (rekursiv via `rglob("*.md")`).
- Frontmatter muss mit `---` beginnen; Abschluss `---` oder `...`.

---

## 4. Konfiguration

### 4.1 Dateiinhalt: Zwei Bereiche
- **Steuerung (_settings):** Verhalten des Skripts (Modus, Anker, Excludes…).
- **Vorlage (Top‑Level‑Keys ohne führenden Unterstrich):** Ziel‑Frontmatter in exakter Reihenfolge.

### 4.2 Mögliche Konfigurationsdateien (Erkennungsreihenfolge)
- `ObisDatabase.ini`
- `ObisDatabase-Timetable.ini`
- `ObisDatabase-Klausur.ini`
- `ObisDatabase-Skript.ini`
- `YAML.ini`
> Erste gefundene Datei im `--root` wird verwendet.

### 4.3 Beispiel‑Minimalvorlage
```yaml
# Minimal
_settings:
  key_mode: strict
Datum: "%datum%"
Projekt: "IUFS"
tags:
  - "Test"
```

### 4.4 Settings im Detail
- `key_mode: strict|merge`
  - `strict`: Nur Template‑Keys werden im Ergebnis geführt (Whitelist via `keep_extra_keys`).
  - `merge`: Template überschreibt gleichnamige Keys; sonstige vorhandene Keys bleiben und werden angehängt.
- `keep_extra_keys: [Globs]` (nur in `strict` wirksam)
  - z. B. `["author", "custom-*", "obsidian_*"]`.
- `base_root: "<Ordnername>"`
  - Setzt einen Anker innerhalb des Baums; `%root0%` referenziert dann diesen Ordner.
- `scope_under_base_root: true|false`
  - `true`: Verarbeite nur Dateien **unterhalb** des Ankers.
- `exclude_folders: [Liste|Globs]`
  - Ordnernamen, die rekursiv ignoriert werden (z. B. `.git`, `.venv`, `node_modules`).

### 4.5 Vorlage (Frontmatter‑Schema)
- Alle **Top‑Level‑Keys ohne `_`** werden in das Frontmatter geschrieben.
- Reihenfolge in der Datei = Reihenfolge in den `.md`‑Zieldateien.
- Werte können Literale (Text/Zahl/Bool), Listen oder Maps sein.

### 4.6 Platzhalter
- `%datum%` / `%date%`: Erstellungsdatum der Datei (YYYY‑MM‑DD; OS‑spezifischer Fallback, siehe 5.6).
- `%data%`: Dateiname ohne Erweiterung.
- `%root0%` (`%folder%`): Name des Start‑Roots (oder Anker, wenn gesetzt).
- `%rootN%` (N≥1): N‑ter Unterordner **vom Root/Anker nach unten**.
- `%folder0%`: Elternordner der Datei.
- `%folderN%` (N≥1): N Ebenen **von der Datei nach oben**.
- `%wert%`: vorhandenen Wert behalten (bei Nichtvorhandensein wird **kein** Feld erzeugt).
- `=leer=`: Mapping‑Feld → leerer String; in Listen → Element entfernen.

### 4.7 Beispiel „Skript.ini“ (kompakt)
```yaml
_settings:
  key_mode: strict
  exclude_folders: [".git", "node_modules", ".venv", "__pycache__", ".obsidian", ".archive", "AWorkbook", "Klausur", "Wiki", "settings", "template"]
Datum: "%datum%"
Projekt: "IUFS"
Section: "DLBWPPDBM01-%root1%"
Task: "%root2%"
Semester: "SE1"
Courses: "DLBWPPDBM01"
Prio: "%wert%"
Stratus: "%wert%"
Stratus_: "%wert%"
Text: "%wert%"
tags:
  - "%root1%"
  - "%data%"
link1: "[[%data%]]"
link2: "[[%root0%-%root1%]]"
```

---

## 5. Funktionsweise im Detail

### 5.1 High‑Level‑Ablauf
1. Root ermitteln (`--root` oder `cwd`).
2. Konfiguration laden (erste existierende Datei aus 4.2).
3. `Settings` parsen; Template ohne `_` extrahieren.
4. Dateien rekursiv finden (`*.md`), per Excludes filtern.
5. Pro Datei: Frontmatter splitten → existierende Daten + Body.
6. Platzhalter auf Template anwenden (Kontext: Pfadebenen, Datum, Dateiname).
7. Ergebnis mit existierenden Daten zusammenführen (Modus `strict|merge`, Whitelist).
8. Frontmatter dumpen (`---` + YAML + `---` + Body); bei Änderungen Datei schreiben.
9. Fortschritt/Zusammenfassung ausgeben.

### 5.2 Frontmatter‑Parsing
- Erkennung nur, wenn Datei mit `---` beginnt.
- Ende bei `---` oder `...` auf einer eigenen Zeile.
- Ungültiges YAML wird defensiv als leeres Dict behandelt.

### 5.3 YAML‑Serialisierung
- `allow_unicode: true` → UTF‑8 sicher.
- `sort_keys: false` → Reihenfolge bleibt wie in Vorlage.
- `default_flow_style: false` → Block‑YAML (lesbar, diff‑freundlich).

### 5.4 Pfadkontext berechnen
- **Aufwärts:** `compute_folder_levels_up()` erzeugt Liste `[folder0, folder1, ...]` beginnend beim Elternordner der Datei nach oben.
- **Abwärts:** `compute_root_parts_down(base, md_parent)` liefert Teile von `base` → `md_parent` (`root1`, `root2`, …). `root0 = base.name`.
- **Anker:** `base_root` bestimmt `base`. Ist `scope_under_base_root: true` und kein Anker im Pfad → Datei wird übersprungen.

### 5.5 Platzhalterersetzung (Details)
- `%datum%`/`%date%`: einmalige Substitution pro Feld.
- `%data%`: Dateiname ohne `.md`.
- `%folder%` und `%root0%`: Alias auf Start‑Root/Anker.
- `%folderN%` (N≥0): Index zu groß → Fallback auf `%folder0%`.
- `%rootN%` (N≥0): Index 0 → `%root0%`; Index zu groß oder keine `root_parts_down` → `%root0%`.
- `=leer=`: in Mappings → `""`; in Listen → Element entfällt.
- `%wert%`:
  - In Mappings: existierender Wert bleibt, andernfalls *kein* Feld.
  - In Listen: mehrdeutig → Element wird **nicht** geschrieben (übersprungen).

### 5.6 Datumsquelle (OS‑spezifisch)
- Bevorzugt: `st_birthtime` (macOS/Windows) → Erstellungsdatum.
- Fallback: `st_mtime` (Linux) → letzter Änderungszeitpunkt des Inhalts.
- Ausgabeformat: ISO‑Datum (`YYYY‑MM‑DD`).

### 5.7 Merge‑Strategie
- `strict`:
  - Resultat enthält **nur** Template‑Keys.
  - Zusätzliche existierende Keys bleiben **nur**, wenn `keep_extra_keys` passt.
- `merge`:
  - Template‑Keys überschreiben gleichnamige.
  - Alle übrigen existierenden Keys werden unten angehängt (Originalreihenfolge).

### 5.8 Exklusionslogik
- Jeder Elternordnername wird gegen die Muster in `exclude_folders` geprüft (fnmatch/Globs).
- Treffer → Datei wird nicht verarbeitet.

### 5.9 I/O und Newlines
- Lesen/Schreiben mit UTF‑8, `newline="\n"`.
- Body bleibt unangetastet (nur Frontmatter wird ersetzt/gesetzt).

### 5.10 CLI und Exit‑Verhalten
- `--root PATH` optional (Standard: `cwd`).
- Kein Dry‑Run; bei fehlender Konfigurationsdatei: Exit mit Fehler.
- YAML‑Parsingfehler in Konfiguration → Fehlerausgabe; Skript beendet sich.

---

## 6. Beispiele und Anwendungsfälle

### 6.1 Studienorganisation (SE/Kurs/Typ)
**Struktur**
```
Studium/
├─ ObisDatabase.ini
├─ SE1/
│  ├─ BWL01/
│  │  └─ Zusammenfassung.md
│  └─ STAT02/
│     └─ Übung.md
└─ SE2/
   └─ PROG01/
      └─ Projekt.md
```
**Vorlage**
```yaml
Datum: "%datum%"
Semester: "%root1%"
Kurs: "%root2%"
Typ: "%data%"
tags:
  - "%root1%"
  - "%root2%"
link: "[[%root2%-Index]]"
```
**Ergebnis (SE1/BWL01/Zusammenfassung.md)**
```yaml
---
Datum: '2025-09-08'
Semester: SE1
Kurs: BWL01
Typ: Zusammenfassung
tags:
  - SE1
  - BWL01
link: "[[BWL01-Index]]"
---
```

### 6.2 Projekt‑Backlog mit Status/Prio
**Vorlage**
```yaml
_settings:
  key_mode: strict
  keep_extra_keys: ["custom-*"]
Projekt: "%root1%"
Task: "%data%"
Status: "%wert%"
Prio: "mittel"
Erstellt: "%datum%"
Tags:
  - "projekt-%root1%"
  - "%folder0%"
Verantwortlich: "=leer="
```

### 6.3 Wiki mit Anker (stabile Pfadreferenzen)
**Struktur**
```
Vault/
├─ Wiki/               ← Anker
│  ├─ Technik/
│  │  ├─ Python/
│  │  │  └─ Basics.md
│  │  └─ JS/
│  └─ Management/
└─ Privat/
```
**Vorlage**
```yaml
_settings:
  base_root: "Wiki"
  scope_under_base_root: true
Bereich: "%root1%"
Thema: "%root2%"
Artikel: "%data%"
Pfad: "%root1%/%root2%/%data%"
tags:
  - "wiki"
  - "%root1%"
  - "%root2%"
Backlink: "[[Wiki-Index]]"
Status: "published"
```

### 6.4 Zettelkasten/Notizen (ID‑Schema)
```yaml
id: "%datum%-%data%"
title: "%data%"
tags: ["zettel", "%root1%"]
status: "permanent"
references: []
backlinks: []
```

### 6.5 Aufgaben mit Icon‑Status
```yaml
Datum: "%datum%"
Projekt: "IUFS"
Task: "%data%"
Status_Text: "%wert%"
Status_Icon: "%wert%"
Kategorie: "%folder1%"
Unterkategorie: "%folder0%"
tags: ["task", "%folder1%", "%folder0%"]
links:
  parent: "[[%folder1%-Übersicht]]"
  index:  "[[Task-Index]]"
```

### 6.6 Attribute (feste Reihenfolge, UI‑geeignet)
```yaml
Datum: "%datum%"
Projekt: "IUFS"
Section: "%root1%-%root2%"
Task: "%data%"
Semester: "%root1%"
Courses: "%root2%"
Prio: "%wert%"
Stratus: "%wert%"
Stratus_: "%wert%"
Text: "%wert%"
```

---

## 7. Erweiterte Features

### 7.1 Anker‑Logik (`base_root`)
- Suche vom Dateipfad **aufwärts** nach einem Ordner mit genau diesem Namen.
- Wird gefunden, dient er als `base` → `%root0% = anchor.name`.
- `scope_under_base_root: true` → Nur Dateien **unter** dem Anker werden verarbeitet; alle anderen werden übersprungen.

### 7.2 Platzhalter‑Fallbacks
- `%rootN%` außerhalb der Tiefe → `%root0%`.
- `%folderN%` außerhalb der Tiefe → `%folder0%`.

### 7.3 `%wert%` – Regeln
- In Mappings: behält vorhandenen Wert; wenn nicht vorhanden → Feld **nicht** erzeugen.
- In Listen: uneindeutig → Element wird ignoriert (kein Eintrag).

### 7.4 `=leer=` – Kontextabhängigkeit
- In Mappings → `""` (leerer String).
- In Listen → Element entfällt (nützlich für Platzhalter in Template‑Listen).

### 7.5 Excludes (fnmatch)
- Muster matchen gegen **irgendeinen** Ordnernamen im Pfad (Elternkette).
- Verwende Globs: `temp*`, `*-backup`, etc.

### 7.6 YAML‑Dump‑Eigenschaften
- Reproduzierbare Reihenfolge, Blockstil, Unicode‑sicher.
- Gut diff‑bar in Git.

### 7.7 Performancehinweise
- I/O‑gebunden; Hauptkosten: Lesen/Schreiben + YAML‑(De)Serialisierung.
- Reduziere Suchraum via `exclude_folders` und/oder Anker‑Scope.
- Segmentiere große Vaults in Teilaufrufe (`--root` auf Unterpfade).

### 7.8 Integrationen/Kompatibilität
- Obsidian Dataview: einfache, flache Schlüssel bevorzugen; ISO‑Daten für Filter/SORT.
- Obsidian Links: `[[...]]` in Strings einsetzbar; Platzhalter innerhalb der Linktexte erlaubt.

### 7.9 Windows/macOS/Linux
- Pfade via `pathlib`; Zeilenenden `\n` → konsistent über Plattformen.
- Datum: `birthtime` (wo verfügbar), sonst `mtime`.

---

## 8. Troubleshooting

### 8.1 „PyYAML nicht installiert“
**Symptom**
```
[FEHLER] PyYAML nicht installiert. Bitte ausführen: pip install pyyaml
```
**Lösung**
```bash
pip install pyyaml
# bei Policy‑Einschränkungen
pip install --user pyyaml
```

### 8.2 „Keine Konfigurationsdatei gefunden“
**Symptom**
```
[FEHLER] Keine Konfigurationsdatei gefunden (ObisDatabase.ini oder ... YAML.ini) in <root>
```
**Prüfen**
- Liegt eine der Dateien aus 4.2 im Root?
- Stimmt `--root`?

### 8.3 Frontmatter wird nicht erkannt
**Ursachen**
- Datei beginnt nicht mit `---`.
- Abschlusszeile (`---` oder `...`) fehlt.
- Vorangehende Leerzeichen/Zeilen vor `---`.
**Fix**
```md
---
key: value
---
Inhalt…
```

### 8.4 YAML‑Syntaxfehler in Konfiguration
**Symptom**
- Parser‑Fehler; Programm beendet sich.
**Fix**
- Einrückungen prüfen (2 Leerzeichen, keine Tabs in YAML).
- Strings ggf. quoten.

### 8.5 Unerwartete Platzhalterwerte
**Vorgehen**
- Debug‑Keys temporär ins Template aufnehmen:
```yaml
Debug_Root0: "%root0%"
Debug_Root1: "%root1%"
Debug_Folder0: "%folder0%"
Debug_Folder1: "%folder1%"
Debug_Data: "%data%"
```

### 8.6 Encoding/Diakritika
- Sicherstellen: Editor/Repo auf UTF‑8.
- Windows‑Shell ggf. auf UTF‑8 stellen (`chcp 65001`).

### 8.7 Massive Rewrites unerwartet
- Prüfe `key_mode`. `strict` entfernt alle nicht im Template gelisteten Keys (außer Whitelist).
- Prüfe Whitelist‑Muster.

### 8.8 Performance
- Excludes ergänzen.
- Scope einschränken (`base_root` + `scope_under_base_root`).
- Große Bäume in Teilbereichen ausführen.

### 8.9 Datumsdifferenzen zwischen OS
- macOS/Windows: Erstellungsdatum.
- Linux: Änderungsdatum (Inhalt) – kann bei Kopieren variieren.

### 8.10 Bekannte Limitierungen
- Kein Dry‑Run/`--check`.
- Keine parallele Verarbeitung (bewusst I/O‑einfach gehalten).

---

## 9. Best Practices

### 9.1 Sicherheit & Nachvollziehbarkeit
- Vor jedem Lauf: Backup oder Git‑Commit.
- Nach jedem Lauf: diff prüfen (z. B. `git diff`).

### 9.2 Template‑Design
- Flache, sprechende Schlüssel (Dataview‑freundlich).
- ISO‑Daten, numerische Prioritäten, Bool‑Flags für Filter.
- Reihenfolge logisch gruppieren (Metadaten → Klassifikation → Links/Tags).

### 9.3 Platzhalter klar nutzen
- `%rootN%` für **stabile** Hierarchiereferenzen (vom Anker/Root nach unten).
- `%folderN%` für **relative** Bezüge (von der Datei nach oben).
- `%wert%` nur dort, wo bestehende Inhalte beibehalten werden sollen.
- `=leer=` gezielt einsetzen (leere Felder oder Listenbereinigung).

### 9.4 Strukturdisziplin
```
Vault/
├─ 01-Projekte/
├─ 02-Wissen/
└─ 03-Archiv/
```
- Tiefe und Benennung standardisieren → weniger Sonderfälle.

### 9.5 Whitelist konservativ
- `keep_extra_keys` minimal halten; vermeidet „schleichende“ Schemazuwächse.

### 9.6 Versionskennzeichen
- `schema_version` im Frontmatter pflegen (manuelle Erhöhung bei Template‑Änderungen).

### 9.7 Einsatz mit anderen Tools
- Erst Umbenennen/Strukturieren (z. B. Renamer), dann Frontmatter setzen.

### 9.8 Testgetriebene Einführung
- Pilot‑Ordner wählen, Template iterieren, dann Vault‑weit ausrollen.

### 9.9 Dokumentation der Vorlage
- Kommentare im Template erklären jeden Key und dessen Herkunft.

### 9.10 Review‑Zyklen
- Regelmäßig `last_updated: %datum%` setzen (wenn gewünscht), um Review‑Listen zu erzeugen.

---

## 10. FAQ

### F1: Welche Konfigurationsdatei wird genutzt?
- Die erste vorhandene in der Reihenfolge: `ObisDatabase.ini`, `ObisDatabase-Timetable.ini`, `ObisDatabase-Klausur.ini`, `ObisDatabase-Skript.ini`, `YAML.ini`.

### F2: Was macht `key_mode: strict` vs. `merge`?
- `strict`: Ergebnis enthält exakt die Template‑Keys; andere werden entfernt (außer Whitelist).
- `merge`: Template überschreibt Gleichnamige; alle anderen vorhandenen Keys bleiben erhalten.

### F3: Wie setze ich einen stabilen Referenzpunkt im Baum?
- Mit `base_root: "Wiki"`. Dann ist `%root0% = "Wiki"`; `%root1%` ist der erste Unterordner darunter.

### F4: Nur einen Bereich verarbeiten?
- `scope_under_base_root: true` zusammen mit `base_root` aktivieren.

### F5: Wofür sind `%rootN%` und `%folderN%`?
- `%rootN%`: vom Start‑Root/Anker **abwärts** (stabil je Struktur).
- `%folderN%`: von der Datei **aufwärts** (relativ zur Dateitiefe).

### F6: Was passiert bei zu großem Index?
- `%rootN%` → Fallback `%root0%`; `%folderN%` → Fallback `%folder0%`.

### F7: Wie behalte ich existierende Werte?
- `%wert%` in Mappings nutzt vorhandene Werte; existiert der Key nicht, wird er nicht angelegt.

### F8: Warum wirkt `%wert%` nicht in Listen?
- In Listen ist die Bedeutung uneindeutig → Eintrag wird übersprungen.

### F9: Wie entferne ich Listenelemente?
- Trage `=leer=` an Stelle des Elements ein → Element entfällt im Ergebnisliste.

### F10: Wie erzeuge ich leere Felder?
- In Mappings `=leer=` → leerer String `""`.

### F11: Wie verhindere ich Bearbeitung bestimmter Ordner?
- `exclude_folders` mit Namen oder Globs befüllen (z. B. `.git`, `.obsidian`, `*-backup`).

### F12: Werden Nicht‑Markdowns verarbeitet?
- Nein, nur Dateien mit Endung `.md`.

### F13: Welche Newlines/Encoding?
- UTF‑8, `\n` (Unix‑Zeilenende).

### F14: Woher kommt das Datum?
- OS‑abhängig: `birthtime` (macOS/Windows), sonst `mtime` (Linux). Format `YYYY‑MM‑DD`.

### F15: Entfernt `strict` wirklich alle unbekannten Keys?
- Ja, außer sie matchen `keep_extra_keys` (Whitelist).

### F16: Kann ich mehrere Vorlagen pro Vault nutzen?
- Ja, pro Unterbereich eigene Datei; starte das Skript mehrfach mit unterschiedlichen `--root` Pfaden oder lege pro Bereich eine passende Konfigurationsdatei und starte im jeweiligen Bereich.

### F17: Gilt die Reihenfolge der Keys?
- Ja. Die Reihenfolge im Template bestimmt die Reihenfolge im Frontmatter.

### F18: Greift das Tool Obsidian‑spezifische Felder an?
- Nur, wenn sie im Template stehen oder `strict` ohne Whitelist läuft. Sonst bleiben sie unberührt (in `merge`) oder via Whitelist (in `strict`).

### F19: Kann ich Links mit Platzhaltern bauen?
- Ja, z. B. `"[[%root2%-Index]]"` oder `"[[%data%]]"`.

### F20: Wie teste ich sicher?
- Kopie eines Unterordners anlegen, Template daran testen, diffs prüfen, dann Vault‑weit ausrollen.

---

### Anhang A – Schnellreferenz Platzhalter
- `%datum%`, `%date%` → Erstellungsdatum.
- `%data%` → Dateiname ohne `.md`.
- `%root0%` / `%folder%` → Start‑Root/Ankername.
- `%root1%`, `%root2%`, … → Pfadteile ab Root/Anker **nach unten**.
- `%folder0%`, `%folder1%`, … → Pfadteile **nach oben** von der Datei aus.
- `%wert%` → vorhandenen Wert behalten (nur Mappings).
- `=leer=` → Mapping: leerer String; Liste: Element entfällt.

### Anhang B – Template‑Skeleton (leer)
```yaml
_settings:
  key_mode: strict
  keep_extra_keys: []
  exclude_folders: [".git", ".obsidian", "node_modules", ".venv", "__pycache__"]
# --- Frontmatter‑Vorlage ---
Datum: "%datum%"
Projekt: ""
Section: ""
Task: ""
Semester: ""
Courses: ""
Prio: "%wert%"
Stratus: "%wert%"
Stratus_: "%wert%"
Text: "%wert%"
tags: []
link1: ""
link2: ""
```

### Anhang C – Debug‑Vorlage
```yaml
Debug_Root0: "%root0%"
Debug_Root1: "%root1%"
Debug_Root2: "%root2%"
Debug_Folder0: "%folder0%"
Debug_Folder1: "%folder1%"
Debug_Data: "%data%"
```

