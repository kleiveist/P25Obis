---
Datum: '2025-08-30'
Projekt: IUFS
Section: IDBS01-P25ObisDatabase
Task: P25ObisDatabase
Semester: SE1
Courses: IDBS01
tags:
- P25ObisDatabase
- ObisDatabase-Guide
link1: '[[ObisDatabase-Guide]]'
link2: '[[P25ObisDatabase]]'
---

# ObisDatabase - Vollständige Benutzeranleitung
## YAML-Frontmatter Manager für Obsidian

## 📋 Inhaltsverzeichnis
1. [Übersicht](#übersicht)
2. [Installation und Setup](#installation-und-setup)
3. [Grundlegende Verwendung](#grundlegende-verwendung)
4. [Konfigurationsdatei verstehen](#konfigurationsdatei-verstehen)
5. [Das Platzhalter-System](#das-platzhalter-system)
6. [Praktische Beispiele](#praktische-beispiele)
7. [Settings und Modi](#settings-und-modi)
8. [Fortgeschrittene Techniken](#fortgeschrittene-techniken)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## 🎯 Übersicht

ObisDatabase ist ein intelligentes Python-Tool zur automatischen Verwaltung von YAML-Frontmatter in Markdown-Dateien. Es wurde speziell für Obsidian-Nutzer entwickelt, die konsistente Metadaten über große Dokumentensammlungen hinweg benötigen.

### Kernfunktionen:
- **Automatisches Frontmatter-Management** nach konfigurierbaren Vorlagen
- **Dynamische Platzhalter** für Pfade, Daten und Dateinamen
- **Zwei Arbeitsmodi** (strict/merge) für verschiedene Anwendungsfälle
- **Intelligente Pfad-Platzhalter** (aufwärts und abwärts)
- **Konsistenz-Garantie** bei wiederholter Ausführung
- **Flexible Ausschluss-Filter**

### Typische Anwendungsfälle:
- 📚 **Wissensmanagement**: Automatische Kategorisierung von Notizen
- 🎓 **Studienmaterialien**: Semester/Kurs-Zuordnung
- 📂 **Projektdokumentation**: Konsistente Metadaten
- 🏷️ **Tag-Management**: Automatische Tag-Vergabe basierend auf Ordnerstruktur
- 🔗 **Link-Netzwerke**: Automatische Backlinks und Verweise

---

## 🚀 Installation und Setup

### Systemvoraussetzungen
- Python 3.6 oder höher
- PyYAML Bibliothek
- Betriebssystem: Windows, Linux, macOS
- Obsidian (optional, aber empfohlen)

### Schritt-für-Schritt Installation

#### 1. Python prüfen
```bash
python --version
# oder
python3 --version
```

#### 2. PyYAML installieren
```bash
pip install pyyaml
# oder
pip3 install pyyaml
```

#### 3. Dateistruktur einrichten
```
Ihr-Obsidian-Vault/
├── ObisDatabase.py       # Das Hauptskript
├── ObisDatabase.ini      # Die Konfigurationsdatei (oder YAML.ini)
└── Ihre-Notizen/         # Ihre Markdown-Dateien
    ├── Semester1/
    │   ├── BWL01/
    │   └── STAT02/
    └── Semester2/
```

#### 4. Basis-Konfiguration erstellen
Erstellen Sie `ObisDatabase.ini` mit minimalem Inhalt:
```yaml
# Minimale Testkonfiguration
Datum: "%datum%"
Projekt: "Mein Projekt"
tags:
  - Test
```

---

## 💻 Grundlegende Verwendung

### Einfachste Ausführung (im aktuellen Verzeichnis)
```bash
python ObisDatabase.py
```

### Mit spezifischem Startverzeichnis
```bash
python ObisDatabase.py --root /pfad/zu/ihrem/vault
```

### Typischer Workflow

1. **Backup erstellen** (immer!)
   ```bash
   cp -r mein-vault mein-vault-backup
   ```

2. **Konfiguration anpassen**
   - Öffnen Sie `ObisDatabase.ini`
   - Definieren Sie Ihre Frontmatter-Struktur

3. **Testlauf in kleinem Bereich**
   ```bash
   python ObisDatabase.py --root ./test-ordner
   ```

4. **Ergebnis prüfen**
   - Öffnen Sie einige .md Dateien
   - Kontrollieren Sie das Frontmatter

5. **Vollständige Ausführung**
   ```bash
   python ObisDatabase.py --root ./
   ```

### Ausgabe verstehen
```
[OK]   aktualisiert: Semester1/BWL01/Notiz1.md
[OK]   aktualisiert: Semester1/BWL01/Notiz2.md
[SKIP] unverändert: Semester1/README.md
...
Fertig. Dateien gesamt: 25, geändert: 18.
```

---

## ⚙️ Konfigurationsdatei verstehen

### Grundstruktur der ObisDatabase.ini

```yaml
# =====================================
# STEUERUNG (Settings)
# =====================================
_settings:
  key_mode: strict              # strict oder merge
  keep_extra_keys: []           # Keys die trotz strict behalten werden
  base_root: "Wiki"             # Optional: Anker-Ordner
  scope_under_base_root: true   # Optional: nur unter Anker arbeiten
  exclude_folders:
    - .git
    - node_modules
    - .obsidian
    - .archive

# =====================================
# FRONTMATTER-VORLAGE
# =====================================
# Reihenfolge hier = Reihenfolge in .md Dateien!

Datum: "%datum%"               # Erstellungsdatum der Datei
Projekt: "IUFS"                # Fester Wert
Task: ""                       # Leerer String
Semester: "%root0%"            # Name des Start-Roots
Section: "%root1%"             # Erste Unterebene
Courses: "%data%"              # Dateiname ohne .md

Prio: "%wert%"                 # Vorhandenen Wert behalten
Status: "Open"                 # Fester Status
Status_: 🟠                    # Icon-Status

Text: "text"                   # Fester Text

tags:                          # Listen sind möglich
  - "IUFS"
  - "timetable"
  - "%root1%"                  # Dynamischer Tag
  - "%data%"                   # Dateiname als Tag
  
link: "[[%root1%]]"            # Obsidian-Link
link1: "[[%data%]]"            # Link zur Datei selbst
```

### Wichtige Regeln

1. **Unterstriche für Settings**: Alle Keys mit `_` am Anfang sind Einstellungen
2. **Reihenfolge matters**: Die Reihenfolge in der INI bestimmt die Reihenfolge im Frontmatter
3. **YAML-Syntax**: Beachten Sie korrekte YAML-Einrückung bei Listen und Maps
4. **Kommentare**: Mit `#` können Sie Erklärungen hinzufügen

---

## 🔤 Das Platzhalter-System

### Übersicht aller Platzhalter

| Platzhalter | Beschreibung | Beispiel bei Pfad `Vault/SE1/BWL01/Klausur/notiz.md` |
|-------------|--------------|--------------------------------------------------|
| **Datei-bezogen** | | |
| `%data%` | Dateiname ohne .md | `notiz` |
| `%datum%` oder `%date%` | Erstellungsdatum (YYYY-MM-DD) | `2025-08-30` |
| **Abwärts vom Root** | | |
| `%root0%` oder `%folder%` | Start-Root Name | `Vault` |
| `%root1%` | 1. Ordner unter Root | `SE1` |
| `%root2%` | 2. Ordner unter Root | `BWL01` |
| `%root3%` | 3. Ordner unter Root | `Klausur` |
| **Aufwärts von Datei** | | |
| `%folder0%` | Direkter Elternordner | `Klausur` |
| `%folder1%` | 1 Ebene über Datei | `BWL01` |
| `%folder2%` | 2 Ebenen über Datei | `SE1` |
| `%folder3%` | 3 Ebenen über Datei | `Vault` |
| **Spezielle Werte** | | |
| `%wert%` | Vorhandenen Wert behalten | (behält existierenden Wert) |
| `=leer=` | Leerer String/Element entfernen | `""` oder Element weg |

### Root vs. Folder - Der Unterschied

#### %rootN% - Vom Start abwärts (Stabil)
```
Vault/                 ← %root0% (Start-Root)
└── SE1/               ← %root1%
    └── BWL01/         ← %root2%
        └── Klausur/   ← %root3%
            └── notiz.md
```
**Vorteil**: Immer gleiche Bedeutung, egal wo die Datei liegt

#### %folderN% - Von Datei aufwärts (Relativ)
```
Vault/                 ← %folder3%
└── SE1/               ← %folder2%
    └── BWL01/         ← %folder1%
        └── Klausur/   ← %folder0% (Elternordner)
            └── notiz.md
```
**Vorteil**: Funktioniert unabhängig von der Gesamtstruktur

### Spezialverhalten

#### %wert% - Intelligente Wertbeibehaltung
```yaml
# Vorher in notiz.md:
---
Prio: hoch
Status: In Arbeit
---

# ObisDatabase.ini:
Prio: "%wert%"     # → bleibt "hoch"
Status: "Open"     # → wird zu "Open"
Neu: "%wert%"      # → Feld wird NICHT angelegt (da nicht vorhanden)
```

#### =leer= - Kontext-abhängig
```yaml
# In Mappings → Leerer String:
Task: "=leer="     # → Task: ""

# In Listen → Element entfernen:
tags:
  - Tag1
  - "=leer="       # → Dieses Element wird entfernt
  - Tag2           # → Resultat: nur [Tag1, Tag2]
```

### Fallback-Mechanismen

**Zu hohe Indizes:**
- `%root99%` bei nur 3 Ebenen → fällt zurück auf `%root0%`
- `%folder99%` bei nur 2 Ebenen → fällt zurück auf `%folder0%`

---

## 📂 Praktische Beispiele

### Beispiel 1: Einfache Studienorganisation

**Struktur:**
```
Studium/
├── ObisDatabase.ini
├── SE1/
│   ├── BWL01/
│   │   └── Zusammenfassung.md
│   └── STAT02/
│       └── Übungen.md
└── SE2/
    └── PROG01/
        └── Projekt.md
```

**ObisDatabase.ini:**
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

**Ergebnis in SE1/BWL01/Zusammenfassung.md:**
```yaml
---
Datum: '2025-08-30'
Semester: SE1
Kurs: BWL01
Typ: Zusammenfassung
tags:
  - SE1
  - BWL01
link: "[[BWL01-Index]]"
---
```

### Beispiel 2: Projektmanagement mit Status

**ObisDatabase.ini:**
```yaml
_settings:
  key_mode: strict
  keep_extra_keys: ["custom-*"]

Projekt: "%root1%"
Task: "%data%"
Status: "%wert%"          # Behält vorhandenen Status
Prio: "mittel"            # Default-Priorität
Erstellt: "%datum%"
Tags:
  - "projekt-%root1%"
  - "%folder0%"
Verantwortlich: "=leer="  # Leeres Feld für spätere Zuweisung
```

### Beispiel 3: Komplexe Wissensstruktur mit Anker

**Struktur:**
```
Obsidian-Vault/
├── Privat/
├── Wiki/              ← Anker-Punkt
│   ├── Technik/
│   │   ├── Python/
│   │   │   └── Basics.md
│   │   └── JavaScript/
│   └── Management/
└── Archiv/
```

**ObisDatabase.ini:**
```yaml
_settings:
  base_root: "Wiki"           # Anker setzen
  scope_under_base_root: true # Nur Wiki-Bereich bearbeiten

Bereich: "%root1%"            # "Technik" oder "Management"
Thema: "%root2%"              # "Python", "JavaScript", etc.
Artikel: "%data%"
Pfad: "%root1%/%root2%/%data%"
Tags:
  - "wiki"
  - "%root1%"
  - "%root2%"
Backlink: "[[Wiki-Index]]"
Status: "published"
```

### Beispiel 4: Aufgabenverwaltung mit Icons

```yaml
# Für Aufgaben-Tracking
Datum: "%datum%"
Projekt: "IUFS"
Task: "%data%"
Priorität: "%wert%"

# Status mit Icons
Status_Text: "%wert%"
Status_Icon: "%wert%"

# Automatische Kategorisierung
Kategorie: "%folder1%"
Unterkategorie: "%folder0%"

# Verknüpfungen
tags:
  - "task"
  - "%folder1%"
  - "%folder0%"
links:
  parent: "[[%folder1%-Übersicht]]"
  index: "[[Task-Index]]"
```

---

## ⚙️ Settings und Modi

### key_mode: strict vs. merge

#### strict Mode (Default)
```yaml
_settings:
  key_mode: strict
```
- ✅ **NUR** in INI definierte Keys bleiben
- ❌ Alle anderen Keys werden **entfernt**
- ✅ Ausnahme: Keys in `keep_extra_keys`
- **Verwendung**: Wenn Sie vollständige Kontrolle wollen

**Beispiel strict:**
```yaml
# Vorher in .md:
---
Datum: 2024-01-01
Autor: Max          # ← wird entfernt!
Titel: Test
---

# Nach strict (nur Datum in INI):
---
Datum: 2025-08-30
---
```

#### merge Mode
```yaml
_settings:
  key_mode: merge
```
- ✅ INI-Keys überschreiben gleichnamige
- ✅ Andere vorhandene Keys **bleiben erhalten**
- ✅ Neue Keys werden hinzugefügt
- **Verwendung**: Wenn Sie bestehende Daten ergänzen wollen

**Beispiel merge:**
```yaml
# Vorher in .md:
---
Datum: 2024-01-01
Autor: Max          # ← bleibt erhalten!
---

# Nach merge (Datum in INI):
---
Datum: 2025-08-30
Autor: Max          # ← noch da!
---
```

### keep_extra_keys - Whitelist für strict

```yaml
_settings:
  key_mode: strict
  keep_extra_keys:
    - "author"           # Exakter Key
    - "custom-*"         # Wildcard: custom-1, custom-abc, etc.
    - "obsidian_*"       # Alle Obsidian-spezifischen
    - "priority"         # Noch ein exakter Key
```

### exclude_folders - Ordner überspringen

```yaml
_settings:
  exclude_folders:
    - .git               # Versionskontrolle
    - .obsidian          # Obsidian-Konfiguration
    - node_modules       # Node.js Pakete
    - .archive           # Archivierte Inhalte
    - "*-backup"         # Alle Backup-Ordner
    - "temp*"            # Temporäre Ordner
```

### base_root & scope_under_base_root

```yaml
_settings:
  base_root: "Wiki"              # Neue Root-Referenz
  scope_under_base_root: true    # NUR Wiki bearbeiten
```

**Effekt:**
- `%root0%` bezieht sich jetzt auf "Wiki" (nicht mehr Vault-Root)
- `%root1%` ist der erste Ordner unter Wiki
- Mit `scope_under_base_root: true` werden NUR Dateien unter Wiki bearbeitet

---

## 🎨 Fortgeschrittene Techniken

### 1. Bedingte Werte mit %wert%

```yaml
# Smart Defaults - nur setzen wenn nicht vorhanden
Status: "%wert%"
Priorität: "%wert%"

# Erzwingt Update bei jedem Lauf
Zuletzt_Aktualisiert: "%datum%"

# Hybrid - Default nur wenn leer
Autor: "%wert%"
```

### 2. Dynamische Tag-Systeme

```yaml
tags:
  # Hierarchische Tags
  - "%root1%"
  - "%root1%/%root2%"
  - "%root1%/%root2%/%folder0%"
  
  # Typ-basierte Tags
  - "typ-%data%"
  
  # Konditionale Tags
  - "%wert%"  # Behält existierende Custom-Tags
```

### 3. Automatische Verlinkung

```yaml
# Breadcrumb-Navigation
navigation:
  up: "[[%folder1%-Index]]"
  current: "[[%folder0%-Übersicht]]"
  root: "[[%root0%-Home]]"

# MOC (Map of Content) Links
moc_links:
  - "[[%root1%-MOC]]"
  - "[[%root2%-MOC]]"
```

### 4. Metadaten-Templates nach Dateityp

**Unterschiedliche INIs für verschiedene Bereiche:**

```bash
# Struktur
Vault/
├── Projekte/
│   ├── ObisDatabase.ini  # Projekt-spezifisch
│   └── ...
├── Wiki/
│   ├── YAML.ini          # Wiki-spezifisch
│   └── ...
└── Journal/
    ├── ObisDatabase.ini  # Journal-spezifisch
    └── ...

# Ausführung pro Bereich
python ObisDatabase.py --root ./Projekte
python ObisDatabase.py --root ./Wiki
python ObisDatabase.py --root ./Journal
```

### 5. Datum-basierte Organisation

```yaml
# Für Journal/Tagebuch
Datum: "%datum%"
Jahr: "%datum%"           # Wird zu YYYY-MM-DD (nachbearbeiten nötig)
Wochentag: "%wert%"       # Manuell ergänzen
Kalenderwoche: "%wert%"
Tags:
  - "journal"
  - "jahr-%datum%"       # jahr-2025-08-30 (nachbearbeiten)
```

### 6. Kombination mit ObisRenamer

**Workflow:**
1. Erst ObisRenamer für Dateiumbenennung
2. Dann ObisDatabase für Frontmatter

```bash
# Schritt 1: Dateien umbenennen
python ObisRenamer.py --root ./Studium

# Schritt 2: Frontmatter aktualisieren
python ObisDatabase.py --root ./Studium
```

---

## ⚠️ Troubleshooting

### Häufige Probleme und Lösungen

#### Problem 1: "PyYAML nicht installiert"
```
[FEHLER] PyYAML nicht installiert
```
**Lösung:**
```bash
pip install pyyaml
# oder bei Rechteproblemen:
pip install --user pyyaml
```

#### Problem 2: "Keine Konfigurationsdatei gefunden"
```
[FEHLER] Keine Konfigurationsdatei gefunden (ObisDatabase.ini oder YAML.ini)
```
**Lösung:**
- Datei im richtigen Verzeichnis erstellen
- Oder mit --root den richtigen Pfad angeben

#### Problem 3: Frontmatter wird nicht erkannt
**Symptome:** Dateien werden als "unverändert" übersprungen

**Mögliche Ursachen:**
1. Kein gültiges YAML-Frontmatter vorhanden
2. Frontmatter nicht mit `---` umschlossen
3. Syntaxfehler im bestehenden Frontmatter

**Lösung:**
```markdown
---
# Korrektes Format
key: value
---

Inhalt der Datei...
```

#### Problem 4: Unerwartete Werte in Platzhaltern
**Debug-Strategie:**
```yaml
# Test-INI zum Debugging
Debug_Root0: "%root0%"
Debug_Root1: "%root1%"
Debug_Folder0: "%folder0%"
Debug_Folder1: "%folder1%"
Debug_Data: "%data%"
```

#### Problem 5: Encoding-Probleme (Umlaute)
**Symptome:** Umlaute werden falsch dargestellt

**Lösung:**
- Sicherstellen dass alle Dateien UTF-8 kodiert sind
- Editor auf UTF-8 einstellen
- Python mit UTF-8 ausführen

### Performance-Probleme

**Bei vielen Dateien (>1000):**

1. **Exclude-Folders nutzen:**
```yaml
_settings:
  exclude_folders:
    - .git
    - node_modules
    - archive
    - backup
```

2. **Bereichsweise arbeiten:**
```bash
# Statt ganzer Vault:
python ObisDatabase.py --root ./Vault/Bereich1
python ObisDatabase.py --root ./Vault/Bereich2
```

3. **Scope einschränken:**
```yaml
_settings:
  base_root: "Arbeitsbereich"
  scope_under_base_root: true
```

---

## 📚 Best Practices

### 1. Sicherheit

#### Immer Backup!
```bash
# Vor jeder Ausführung:
cp -r mein-vault mein-vault-$(date +%Y%m%d)

# Oder mit Git:
git add . && git commit -m "Vor ObisDatabase"
```

#### Schrittweise vorgehen
1. Klein anfangen (ein Testordner)
2. Konfiguration prüfen
3. Erweitern
4. Vollständig ausführen

### 2. Organisations-Strategien

#### Konsistente Ordnerstruktur
```
Vault/
├── 01-Projekte/
│   ├── Projekt-A/
│   └── Projekt-B/
├── 02-Wissen/
│   ├── Technik/
│   └── Management/
└── 03-Archiv/
```

#### Sinnvolle Platzhalter-Verwendung
```yaml
# GUT - Klar und wartbar:
Bereich: "%root1%"
Thema: "%root2%"
Dokument: "%data%"

# SCHLECHT - Verwirrend:
x: "%folder3%"
y: "%root2%"
z: "%folder1%"
```

### 3. Obsidian-Integration

#### Dataview-kompatible Felder
```yaml
# Für Dataview-Queries optimiert
status: "active"          # Einfache Werte für WHERE
priority: 3                # Zahlen für Sortierung
due_date: "2025-09-01"    # ISO-Daten für Zeitvergleiche
tags:                      # Arrays für Contains-Queries
  - projekt
  - wichtig
```

#### Template-Kompatibilität
```yaml
# Felder die Obsidian-Templates nutzen können
template: "%wert%"         # Template-Name beibehalten
created: "%datum%"         # Erstellungsdatum
modified: "%wert%"         # Für manuelles Update
```

### 4. Wartbarkeit

#### Dokumentierte Konfiguration
```yaml
# ObisDatabase.ini mit Kommentaren

# === METADATEN ===
# Automatisch gesetzt bei jeder Ausführung
Datum: "%datum%"           # Erstellungsdatum der Datei
Vault: "%root0%"           # Vault-Name für Multi-Vault-Setup

# === KLASSIFIKATION ===
# Basierend auf Ordnerstruktur
Bereich: "%root1%"         # Hauptbereich (Projekte/Wissen/etc)
Kategorie: "%root2%"       # Unterkategorie
```

#### Versionierung
```yaml
# Versions-Tracking
schema_version: "2.0"      # Bei Änderungen erhöhen
last_updated: "%datum%"    # Wann zuletzt verarbeitet
```

### 5. Häufige Muster

#### Für Zettelkasten
```yaml
id: "%datum%-%data%"
title: "%data%"
tags:
  - "zettel"
  - "%root1%"
references: []
backlinks: []
status: "permanent"
```

#### Für Projektmanagement
```yaml
projekt: "%root1%"
phase: "%folder0%"
task: "%data%"
status: "open"
priority: 2
assigned: ""
deadline: ""
```

#### Für Wissensdatenbank
```yaml
domain: "%root1%"
topic: "%root2%"
subtopic: "%folder0%"
article: "%data%"
tags:
  - "wiki"
  - "%root1%"
  - "%root2%"
verified: false
last_review: "%datum%"
```

---

## 🎯 Zusammenfassung

### Die wichtigsten Befehle

```bash
# Grundausführung
python ObisDatabase.py

# Mit spezifischem Root
python ObisDatabase.py --root /pfad/zum/vault

# Test in Unterordner
python ObisDatabase.py --root ./test
```

### Die wichtigsten Platzhalter

| Platzhalter | Verwendung |
|-------------|------------|
| `%datum%` | Erstellungsdatum |
| `%data%` | Dateiname |
| `%root1%`, `%root2%` | Ordner von oben |
| `%folder0%`, `%folder1%` | Ordner von unten |
| `%wert%` | Wert beibehalten |

### Die wichtigsten Settings

```yaml
_settings:
  key_mode: strict        # oder merge
  keep_extra_keys: []     # Whitelist für strict
  exclude_folders: []     # Ausschlüsse
```

### Goldene Regeln

1. **Immer Backup machen** vor der Ausführung
2. **Klein anfangen**, dann erweitern
3. **Dokumentieren** Sie Ihre Konfiguration
4. **Testen** Sie in einem Unterordner
5. **Konsistent bleiben** bei der Struktur

Mit ObisDatabase haben Sie ein mächtiges Werkzeug zur Hand, um Ihre Markdown-Dateien systematisch und konsistent zu verwalten. Die Kombination aus flexiblen Platzhaltern und strikter Konfiguration ermöglicht es, auch große Dokumentensammlungen effizient zu organisieren!