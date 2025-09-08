# ObisRenamer - Vollständige Benutzeranleitung

## 📋 Inhaltsverzeichnis
1. [Übersicht](#übersicht)
2. [Installation und Vorbereitung](#installation-und-vorbereitung)
3. [Grundlegende Verwendung](#grundlegende-verwendung)
4. [Konfigurationsdatei verstehen](#konfigurationsdatei-verstehen)
5. [Platzhalter-System](#platzhalter-system)
6. [Praktische Beispiele](#praktische-beispiele)
7. [Erweiterte Features](#erweiterte-features)
8. [Fehlerbehandlung](#fehlerbehandlung)
9. [Best Practices](#best-practices)

---

## 🎯 Übersicht

ObisRenamer ist ein leistungsfähiges Python-Tool zur automatischen Umbenennung von Dateien in komplexen Verzeichnisstrukturen. Es wurde speziell für die Organisation von Lernmaterialien, Dokumenten und Mediendateien entwickelt.

### Hauptfunktionen:
- **Rekursive Umbenennung** nach konfigurierbaren Mustern
- **Ebenen-basierte Logik** (unterschiedliche Regeln je Verzeichnistiefe)
- **Automatische Nummerierung** mit konfigurierbarer Breite
- **Markdown-Dokumentation** für Obsidian
- **Umfangreiche Ausschluss-Filter**
- **Platzhalter-System** für dynamische Benennungen

---

## 🚀 Installation und Vorbereitung

### Systemvoraussetzungen
- Python 3.6 oder höher
- Betriebssystem: Windows, Linux, macOS
- Keine externen Python-Bibliotheken erforderlich (nur Standard-Library)

### Schritt-für-Schritt Installation

#### 1. Python-Installation prüfen
```bash
python --version
# oder
python3 --version
```

#### 2. Dateien vorbereiten
Erstellen Sie in Ihrem Arbeitsverzeichnis:
```
Ihr-Projekt/
├── ObisRenamer.py       # Das Hauptskript
├── ObisRenamer.ini      # Die Konfigurationsdatei
└── Ihre-Dateien/        # Zu bearbeitende Verzeichnisstruktur
```

#### 3. Konfigurationsdatei anpassen
Öffnen Sie `ObisRenamer.ini` und passen Sie sie an Ihre Bedürfnisse an (siehe Konfigurationsabschnitt).

---

## 💻 Grundlegende Verwendung

### Einfachste Ausführung (im aktuellen Verzeichnis)
```bash
python ObisRenamer.py
```

### Mit spezifischem Verzeichnis
```bash
python ObisRenamer.py --root /pfad/zu/ihrem/ordner
```

### Mit alternativer Konfigurationsdatei
```bash
python ObisRenamer.py --config MeineKonfig.ini
```

### Testlauf ohne Änderungen (Dry-Run)
```bash
python ObisRenamer.py --dry
```
**Wichtig:** Immer zuerst mit `--dry` testen!

### Vollständige Befehlssyntax
```bash
python ObisRenamer.py [--root VERZEICHNIS] [--config INI-DATEI] [--dry]
```

---

## ⚙️ Konfigurationsdatei verstehen

### Grundstruktur der ObisRenamer.ini

```ini
; =====================================
; ABSCHNITT 1: Umbenennung-Muster
; =====================================
[patterns]
level1 = %root1%                    ; Dateien in Root/Ordner1/*
level2 = %root2%                    ; Dateien in Root/Ordner1/Ordner2/*
level3 = %root2%-%root3%            ; Kombiniertes Muster
level4 = %root2%-%root3%-%root4%    ; Noch tiefer verschachtelt

; =====================================
; ABSCHNITT 2: Dokumentations-Dateinamen (optional)
; =====================================
[DB]
level1 = Data-%root1%.md
level2 = Data-%root2%%root3B%.md
level3 = Data-%root2%%root3B%.md
level4 = Data-%root2%%root3B%%root4B%%N%.md

; =====================================
; ABSCHNITT 3: Optionen
; =====================================
[options]
numbering_width = 2              ; Breite der Nummerierung (01, 02, ...)
data_name_template = true        ; DB-Templates verwenden (true/false)
use_birthtime = false           ; Erstellungszeit verwenden (wenn verfügbar)

; =====================================
; ABSCHNITT 4: Ausschlüsse
; =====================================
[excludes]
; Komplette Ordner (werden rekursiv ignoriert)
folders =
    .git,
    .venv,
    __pycache__,
    .obsidian,
    node_modules

; Dateitypen (Endungen)
filetypes =
    .md,
    .py,
    .ini,
    .exe

; Einzelne Dateien (exakter Name)
filenames =
    wichtig.docx,
    settings.xlsx
```

---

## 🔤 Platzhalter-System

### Verfügbare Platzhalter für [patterns] und [DB]

| Platzhalter | Beschreibung | Beispiel |
|-------------|--------------|----------|
| `%root%` oder `%folder%` | Name des Start-Root-Verzeichnisses | `SE1` |
| `%root1%` oder `%folder1%` | 1. Ordnerebene ab Root | `BBWL01` |
| `%root2%` oder `%folder2%` | 2. Ordnerebene ab Root | `Skript` |
| `%root3%` oder `%folder3%` | 3. Ordnerebene ab Root | `Lektion1` |
| `%rootNB%` oder `%folderNB%` | Erster Buchstabe der N-ten Ebene | `%root2B%` → `S` |
| `%datum%` | Datum kompakt (YYYYMMDD) | `20250830` |
| `%date%` | Datum formatiert (YYYY-MM-DD) | `2025-08-30` |
| `%wert%` | Alter Dateiname ohne Endung (nur [patterns]) | `Dokument` |
| `%N%` | Letzte Ziffernfolge aus Ordnername | `Lektion3` → `3` |
| `%N%%N%` | Mit Null-Auffüllung | `Lektion3` → `03` |

### Spezielle Platzhalter-Features

#### %N% - Ziffernextraktion
```ini
; Ordnername: "Lektion3"
level3 = Kurs-%N%        ; → Kurs-3-01.pdf
level3 = Kurs-%N%%N%     ; → Kurs-03-01.pdf
level3 = Kurs-%N%%N%%N%  ; → Kurs-003-01.pdf
```

#### %rootNB% - Anfangsbuchstaben
```ini
; Pfad: SE1/BBWL01/Skript/Lektion1
level3 = %root1%%root2B%%root3B%  ; → BBWL01SL-01.pdf
```

---

## 📂 Praktische Beispiele

### Beispiel 1: Einfache Kursstruktur

**Verzeichnisstruktur:**
```
Semester1/
├── BBWL01/
│   ├── alte_datei.pdf
│   └── dokument.docx
└── STAT02/
    ├── übung.xlsx
    └── lösung.pdf
```

**Konfiguration:**
```ini
[patterns]
level1 = %root1%

[options]
numbering_width = 2
```

**Ergebnis nach Ausführung:**
```
Semester1/
├── BBWL01/
│   ├── BBWL01-01.pdf
│   ├── BBWL01-01.docx
│   └── Data-BBWL01.md
└── STAT02/
    ├── STAT02-01.xlsx
    ├── STAT02-01.pdf
    └── Data-STAT02.md
```

### Beispiel 2: Komplexe Hierarchie mit DB-Templates

**Verzeichnisstruktur:**
```
SE1/
└── BBWL01/
    ├── Klausur/
    │   ├── Lösung/
    │   │   └── scan.pdf
    │   └── png1/
    │       └── bild.png
    └── Skript/
        ├── Lektion1/
        │   └── folien.pptx
        └── Lektion2/
            └── übung.docx
```

**Konfiguration:**
```ini
[patterns]
level1 = %root1%
level2 = %root2%
level3 = %root1%-%root3%

[DB]
level1 = Data-%root1%.md
level2 = Data-%root1%%root2B%.md
level3 = Data-%root1%%root2B%%root3B%%N%.md

[options]
data_name_template = true
numbering_width = 2
```

**Ergebnis:**
```
SE1/
└── BBWL01/                         [Data-BBWL01.md]
    ├── Klausur/                    [Data-BBWL01K.md]
    │   ├── Lösung/                 [Data-BBWL01KL.md]
    │   │   └── BBWL01-Lösung-01.pdf
    │   └── png1/                   [Data-BBWL01KP1.md]
    │       └── BBWL01-png1-01.png
    └── Skript/                     [Data-BBWL01S.md]
        ├── Lektion1/               [Data-BBWL01SL1.md]
        │   └── BBWL01-Lektion1-01.pptx
        └── Lektion2/               [Data-BBWL01SL2.md]
            └── BBWL01-Lektion2-01.docx
```

### Beispiel 3: Datum-basierte Benennung

```ini
[patterns]
level1 = %date%-%root1%
level2 = %datum%_%root2%

[options]
use_birthtime = true  ; Nutzt Erstellungszeit wenn verfügbar
```

**Ergebnis:**
```
2025-08-30-BBWL01-01.pdf
20250830_Skript-01.docx
```

---

## 🎨 Erweiterte Features

### 1. Dry-Run Modus (Testlauf)

**Immer zuerst testen:**
```bash
python ObisRenamer.py --dry
```

Zeigt alle geplanten Änderungen ohne sie durchzuführen:
```
[DRY] BBWL01/alte_datei.pdf  ->  BBWL01-01.pdf
[DRY] BBWL01/dokument.docx  ->  BBWL01-01.docx
[DRY] Skript/folien.pptx  ->  Skript-01.pptx
```

### 2. Markdown-Dokumentation für Obsidian

Wenn aktiviert, erstellt ObisRenamer automatisch `.md` Dateien mit Obsidian-Links:

**Data-BBWL01.md:**
```markdown
# Umbenannte Dateien in diesem Verzeichnis

![[BBWL01-01.pdf]]
![[BBWL01-02.docx]]
![[BBWL01-03.png]]
```

**Aktivierung:**
```ini
[options]
data_name_template = true

[DB]
level1 = Data-%root1%.md
level2 = Data-%root2%.md
```

### 3. Intelligente Nummerierung

- **Pro Dateityp:** Jede Endung wird separat nummeriert
- **Pro Ordner:** Zählung beginnt in jedem Ordner neu
- **Konfigurierbare Breite:** 

```ini
[options]
numbering_width = 3  ; → 001, 002, 003...
```

### 4. Kollisionsvermeidung

ObisRenamer verwendet ein zweistufiges Umbenennung-System:
1. Datei → temporärer Name
2. Temporärer Name → Zielname

Dies verhindert Konflikte bei zirkulären Umbenennungen.

### 5. Flexible Ausschluss-Filter

```ini
[excludes]
; Mehrere Schreibweisen unterstützt:
folders = .git, node_modules
folders =
    .git
    node_modules
    
; Mit oder ohne Punkt:
filetypes = .md, py, ini

; Exakte Dateinamen:
filenames = 
    "wichtige datei.docx"
    'settings.xlsx'
```

---

## ⚠️ Fehlerbehandlung

### Häufige Fehler und Lösungen

#### 1. "INI nicht gefunden"
```bash
Fehler: INI nicht gefunden: /pfad/ObisRenamer.ini
```
**Lösung:** Pfad zur INI-Datei angeben:
```bash
python ObisRenamer.py --config ./meine-config.ini
```

#### 2. "Root nicht gefunden"
```bash
Fehler: Root nicht gefunden: /falscher/pfad
```
**Lösung:** Korrekten Pfad verwenden:
```bash
python ObisRenamer.py --root ./mein-ordner
```

#### 3. "Temporärer Name existiert bereits"
**Ursache:** Abgebrochene vorherige Ausführung
**Lösung:** Temporäre Dateien manuell entfernen (beginnen mit `__obis_tmp__`)

#### 4. "Ziel existiert bereits"
**Ursache:** Dateiname-Kollision
**Lösung:** ObisRenamer fügt automatisch `_2`, `_3` etc. an

### Debug-Tipps

1. **Immer mit Dry-Run beginnen:**
   ```bash
   python ObisRenamer.py --dry > test_output.txt
   ```

2. **Backup erstellen:**
   ```bash
   cp -r mein-ordner mein-ordner-backup
   ```

3. **Schrittweise vorgehen:**
   - Erst eine Ebene konfigurieren
   - Testen
   - Weitere Ebenen hinzufügen

---

## 📚 Best Practices

### 1. Vorbereitung
- ✅ **Backup** der Originaldaten erstellen
- ✅ Mit **--dry** Modus testen
- ✅ Klein anfangen (ein Testordner)
- ✅ Konfiguration dokumentieren

### 2. Konfiguration
- ✅ Aussagekräftige Muster verwenden
- ✅ Konsistente Trennzeichen (- oder _)
- ✅ Sinnvolle Nummerierungsbreite wählen
- ✅ Wichtige Dateien ausschließen

### 3. Organisation
```ini
; Gute Struktur:
[patterns]
level1 = %root1%              ; Kurs
level2 = %root1%-%root2%      ; Kurs-Kapitel
level3 = %root1%-%root2%-%N%  ; Kurs-Kapitel-Nummer

; Vermeide:
level1 = %datum%%root1%%root2%%root3%  ; Zu komplex
```

### 4. Workflow-Empfehlung

1. **Analyse:** Verzeichnisstruktur verstehen
   ```bash
   tree -d -L 3 mein-ordner
   ```

2. **Konfiguration:** INI-Datei erstellen

3. **Test:** Dry-Run durchführen
   ```bash
   python ObisRenamer.py --dry --root mein-ordner
   ```

4. **Prüfung:** Output kontrollieren

5. **Ausführung:** Wenn alles passt
   ```bash
   python ObisRenamer.py --root mein-ordner
   ```

6. **Verifikation:** Ergebnis prüfen

### 5. Für Obsidian-Nutzer

```ini
[options]
data_name_template = true

[DB]
; Nutze sprechende Namen:
level1 = Index-%root1%.md
level2 = Übersicht-%root2%.md
level3 = Inhalt-%root3%.md

[excludes]
folders = .obsidian
filetypes = .md  ; Bereits existierende MD-Dateien nicht umbenennen
```

---

## 🔧 Erweiterte Konfigurationsbeispiele

### Beispiel: Foto-Archiv
```ini
[patterns]
level1 = %date%-%root1%  ; 2025-08-30-Urlaub

[options]
use_birthtime = true
numbering_width = 3

[excludes]
filetypes = .raw, .xmp
```

### Beispiel: Projektdokumentation
```ini
[patterns]
level1 = Projekt-%root1%
level2 = %root1%-%root2%
level3 = %root1%-%root2%-v%N%

[DB]
level1 = README-%root1%.md
level2 = Docs-%root2%.md
```

### Beispiel: Mediensammlung
```ini
[patterns]
level1 = %root1%
level2 = %root1%%root2B%%N%%N%

[options]
numbering_width = 4  ; Für große Sammlungen

[excludes]
filetypes = .nfo, .srt, .sub
```

---

## 📝 Zusammenfassung

ObisRenamer ist ein mächtiges Werkzeug für:
- 📁 Strukturierte Dateiorganisation
- 🔄 Konsistente Benennungsschemata
- 📚 Automatische Dokumentation
- 🎯 Batch-Verarbeitung großer Dateimengen

**Goldene Regeln:**
1. Immer Backups machen
2. Immer erst mit --dry testen
3. Klein anfangen, dann erweitern
4. Konfiguration dokumentieren

Mit dieser Anleitung sollten Sie in der Lage sein, ObisRenamer effektiv für Ihre Bedürfnisse einzusetzen!