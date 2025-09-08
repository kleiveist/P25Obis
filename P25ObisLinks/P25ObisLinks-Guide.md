# P25ObisLinks - Vollständiger Benutzerguide

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

## Überblick und Zweck

P25ObisLinks ist ein Python-Skript, das automatisch Index-Markdown-Dateien für Ihre Ordnerstruktur generiert. Es wurde speziell für Obsidian-Vaults entwickelt, kann aber auch für andere Markdown-basierte Wissensmanagementsysteme verwendet werden.

### Hauptfunktionen
- **Automatische Index-Generierung**: Erstellt für jeden Ordner eine entsprechende `.md`-Indexdatei
- **Sichere Aktualisierung**: Bestehender Inhalt wird niemals gelöscht, nur der Links-Bereich wird aktualisiert
- **Rekursive Verarbeitung**: Durchläuft die gesamte Ordnerstruktur automatisch
- **Kategorisierte Links**: Organisiert Inhalte in Folder, Markdown und Files Kategorien
- **Konfigurierbar**: Anpassbare Einstellungen für verschiedene Anwendungsfälle

### Typische Anwendungsfälle
- Obsidian Vault Organisation
- Dokumentations-Websites
- Wissensdatenbanken
- Projekt-Dokumentation
- Digitale Archive

## Installation und Setup

### Voraussetzungen
- Python 3.6 oder höher
- Schreibberechtigung im Zielverzeichnis
- UTF-8 kompatibles System

### Installation
1. **Datei herunterladen**: Speichern Sie `P25ObisLinks.py` in einem beliebigen Verzeichnis
2. **Ausführbar machen** (Linux/Mac):
   ```bash
   chmod +x P25ObisLinks.py
   ```
3. **Python-Pfad prüfen**:
   ```bash
   python3 --version
   ```

### Erste Schritte
1. Navigieren Sie zu Ihrem Zielverzeichnis
2. Führen Sie das Skript aus:
   ```bash
   python3 /pfad/zu/P25ObisLinks.py
   ```
   oder
   ```bash
   ./P25ObisLinks.py  # wenn ausführbar gemacht
   ```

## Grundlegende Verwendung

### Kommandozeilen-Syntax
```bash
python3 P25ObisLinks.py [VERZEICHNIS] [OPTIONEN]
```

### Parameter
- `VERZEICHNIS` (optional): Startverzeichnis für die Verarbeitung
  - Standard: aktuelles Verzeichnis (`.`)
  - Beispiel: `/home/user/mein-vault`

### Optionen
- `--dry-run`: Simulation ohne tatsächliche Änderungen
  - Zeigt an, welche Dateien erstellt/geändert würden
  - Sicher zum Testen

### Einfache Anwendungsbeispiele

#### Aktuelles Verzeichnis verarbeiten
```bash
python3 P25ObisLinks.py
```

#### Spezifisches Verzeichnis verarbeiten
```bash
python3 P25ObisLinks.py /pfad/zu/meinem/vault
```

#### Trockenlauf (Simulation)
```bash
python3 P25ObisLinks.py --dry-run
```

## Konfiguration

### Anpassbare Einstellungen im Skript

Die Konfiguration erfolgt über das `SETTINGS`-Dictionary am Anfang der Datei:

```python
SETTINGS: Dict[str, Any] = {
    "EXCLUDE_FOLDERS": {
        ".git",
        "node_modules", 
        ".venv",
        "__pycache__",
        ".obsidian",
        ".archive",
    },
    "FOLDER_LINK_PREFIX": "",
    "IGNORE_DOT_ITEMS": True,
}
```

### Konfigurationsoptionen im Detail

#### EXCLUDE_FOLDERS
**Zweck**: Ordner, die nicht verarbeitet werden sollen

**Standard-Ausschlüsse**:
- `.git`: Git-Repository-Dateien
- `node_modules`: NPM-Abhängigkeiten
- `.venv`: Python Virtual Environment
- `__pycache__`: Python-Cache-Dateien
- `.obsidian`: Obsidian-Konfiguration
- `.archive`: Archivierte Inhalte

**Anpassung**:
```python
"EXCLUDE_FOLDERS": {
    ".git",
    "temp",
    "backup",
    "drafts",
}
```

#### FOLDER_LINK_PREFIX
**Zweck**: Präfix für Ordner-Links in der #Folder-Sektion

**Standardwert**: `""` (kein Präfix)

**Beispiele**:
```python
# Kein Präfix
"FOLDER_LINK_PREFIX": ""
# Ergebnis: [[Ordnername]]

# Mit Präfix
"FOLDER_LINK_PREFIX": "Data-"
# Ergebnis: [[Data-Ordnername]]
```

#### IGNORE_DOT_ITEMS
**Zweck**: Versteckte Elemente (beginnend mit `.`) ignorieren

**Standardwert**: `True`

**Verhalten**:
- `True`: Versteckte Dateien und Ordner werden ignoriert
- `False`: Versteckte Elemente werden mit verarbeitet

### Erweiterte Konfiguration

#### Eigene Ausschlüsse hinzufügen
```python
# Projektspezifische Ordner ausschließen
"EXCLUDE_FOLDERS": {
    ".git", "node_modules", ".venv", "__pycache__",
    ".obsidian", ".archive",
    "tmp", "build", "dist", "output"
}
```

#### Präfix-Strategien
```python
# Für MOCs (Maps of Content)
"FOLDER_LINK_PREFIX": "MOC-"

# Für Themen-Kategorien
"FOLDER_LINK_PREFIX": "Topic-"

# Für hierarchische Strukturen
"FOLDER_LINK_PREFIX": "Cat-"
```

## Funktionsweise im Detail

### Verarbeitungslogik

#### 1. Verzeichnis-Traversierung
Das Skript durchläuft rekursiv alle Verzeichnisse:
```
Root/
├── Ordner1/        → Ordner1.md erstellen
│   ├── Sub1/       → Sub1.md erstellen
│   └── Sub2/       → Sub2.md erstellen
└── Ordner2/        → Ordner2.md erstellen
```

#### 2. Inhalts-Kategorisierung
Für jeden Ordner werden Inhalte in drei Kategorien sortiert:

**Unterordner** → #Folder Sektion
- Alle direkten Unterordner
- Alphabetisch sortiert
- Als Links formatiert: `[[Präfix+Name]]`

**Markdown-Dateien** → #Markdown Sektion
- Alle `.md`-Dateien im Ordner
- Ausschluss der eigenen Index-Datei
- Als Einbettungen formatiert: `![[Dateiname.md]]`

**Andere Dateien** → #Files Sektion
- Alle Nicht-Markdown-Dateien
- PDF, Bilder, Videos, etc.
- Als Einbettungen formatiert: `![[Dateiname.ext]]`

#### 3. Block-Generierung
Der generierte Block hat folgende Struktur:
```markdown
<!-- AUTOGEN_START -->

---
#Folder
[[Unterordner1]]
[[Unterordner2]]
---
#Markdown
![[Datei1.md]]
![[Datei2.md]]
---
#Files
![[Dokument.pdf]]
![[Bild.png]]
<!-- AUTOGEN_END -->
```

#### 4. Sichere Integration
- **Existierende Datei**: Nur der Bereich zwischen `AUTOGEN_START` und `AUTOGEN_END` wird ersetzt
- **Neue Datei**: Kompletter Block wird erstellt
- **Bestehender Inhalt**: Bleibt vollständig erhalten

### Algorithmus-Details

#### Ordner-Sortierung
```python
# Alphabetische Sortierung (case-insensitive)
sorted(items, key=lambda p: p.name.lower())
```

#### Index-Datei-Benennung
```python
def determine_index_name(dir_name: str) -> str:
    return f"{dir_name}.md"
```

#### Platzhalter-Bereinigung
Das Skript entfernt leere Platzhalter-Links:
```markdown
# Links
[[]]
[[]]
```

## Beispiele und Anwendungsfälle

### Beispiel 1: Einfache Projektstruktur

**Verzeichnisstruktur**:
```
MeinProjekt/
├── Dokumentation/
│   ├── API.md
│   ├── Installation.md
│   └── Handbuch.pdf
├── Code/
│   ├── Frontend/
│   └── Backend/
└── Tests/
    ├── Unit/
    └── Integration/
```

**Generierte MeinProjekt.md**:
```markdown
<!-- AUTOGEN_START -->

---
#Folder
[[Code]]
[[Dokumentation]]
[[Tests]]
<!-- AUTOGEN_END -->
```

**Generierte Dokumentation.md**:
```markdown
<!-- AUTOGEN_START -->

---
#Markdown
![[API.md]]
![[Installation.md]]
---
#Files
![[Handbuch.pdf]]
<!-- AUTOGEN_END -->
```

### Beispiel 2: Obsidian Vault mit Präfix

**Konfiguration**:
```python
"FOLDER_LINK_PREFIX": "Data-"
```

**Verzeichnisstruktur**:
```
Vault/
├── Notizen/
│   ├── Daily/
│   ├── Meeting/
│   └── Ideen.md
└── Projekte/
    ├── Projekt-A/
    └── Projekt-B/
```

**Generierte Vault.md**:
```markdown
<!-- AUTOGEN_START -->

---
#Folder
[[Data-Notizen]]
[[Data-Projekte]]
<!-- AUTOGEN_END -->
```

### Beispiel 3: Umfangreiche Wissenssammlung

**Verzeichnisstruktur**:
```
Wiki/
├── BWL/
│   ├── Marketing/
│   ├── Finanzen/
│   ├── Grundlagen.md
│   └── Begriffe.pdf
├── IT/
│   ├── Python/
│   ├── JavaScript/
│   ├── Frameworks/
│   └── Cheatsheet.md
└── Persönlich/
    ├── Ziele.md
    ├── Reflexion.md
    └── Fotos/
        ├── 2023/
        └── 2024/
```

**Generierte IT.md**:
```markdown
<!-- AUTOGEN_START -->

---
#Folder
[[Frameworks]]
[[JavaScript]]
[[Python]]
---
#Markdown
![[Cheatsheet.md]]
<!-- AUTOGEN_END -->
```

### Beispiel 4: Integration mit bestehendem Inhalt

**Bestehende Datei (IT.md)**:
```markdown
# IT Überblick

Hier sammle ich alle IT-bezogenen Informationen.

## Meine Notizen
- Wichtige Erkenntnisse
- Projektideen

## Links zu externen Quellen
- [Python.org](https://python.org)
- [MDN Web Docs](https://developer.mozilla.org)

<!-- AUTOGEN_START -->
<!-- alte automatische Links hier -->
<!-- AUTOGEN_END -->

## Persönliche Bewertungen
Diese Sektion bleibt erhalten.
```

**Nach Ausführung**:
```markdown
# IT Überblick

Hier sammle ich alle IT-bezogenen Informationen.

## Meine Notizen
- Wichtige Erkenntnisse
- Projektideen

## Links zu externen Quellen
- [Python.org](https://python.org)
- [MDN Web Docs](https://developer.mozilla.org)

<!-- AUTOGEN_START -->

---
#Folder
[[Frameworks]]
[[JavaScript]]
[[Python]]
---
#Markdown
![[Cheatsheet.md]]
<!-- AUTOGEN_END -->

## Persönliche Bewertungen
Diese Sektion bleibt erhalten.
```

## Erweiterte Features

### Dry-Run Modus
Der `--dry-run` Parameter ermöglicht sichere Vorschau:

```bash
python3 P25ObisLinks.py --dry-run
```

**Ausgabe**:
```
[DRY] würde schreiben: /home/user/Wiki/Wiki.md
[DRY] würde schreiben: /home/user/Wiki/BWL/BWL.md
[DRY] würde schreiben: /home/user/Wiki/IT/IT.md
[DRY] würde schreiben: /home/user/Wiki/IT/Python/Python.md
```

### Selektive Verarbeitung
Sie können das Skript auf spezifische Unterverzeichnisse anwenden:

```bash
# Nur den IT-Ordner verarbeiten
python3 P25ObisLinks.py /pfad/zu/Wiki/IT

# Nur ein Projekt
python3 P25ObisLinks.py ./MeinProjekt/Dokumentation
```

### Batch-Verarbeitung
Für mehrere getrennte Verzeichnisse:

```bash
#!/bin/bash
# batch_process.sh
for dir in Wiki Projekte Archive; do
    echo "Verarbeite $dir..."
    python3 P25ObisLinks.py ./$dir
done
```

### Integration in Workflows

#### Git Hook (Pre-Commit)
```bash
#!/bin/bash
# .git/hooks/pre-commit
python3 /pfad/zu/P25ObisLinks.py .
git add *.md
```

#### Cron Job (Automatische Updates)
```bash
# Täglich um 2 Uhr morgens
0 2 * * * cd /home/user/vault && python3 /pfad/zu/P25ObisLinks.py . >/dev/null 2>&1
```

#### VS Code Task
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Update Index Files",
            "type": "shell",
            "command": "python3",
            "args": ["/pfad/zu/P25ObisLinks.py", "."],
            "group": "build",
            "presentation": {
                "panel": "new"
            }
        }
    ]
}
```

## Troubleshooting

### Häufige Probleme und Lösungen

#### Problem: "Permission denied"
**Ursache**: Keine Schreibberechtigung im Zielverzeichnis
**Lösung**:
```bash
# Berechtigung prüfen
ls -la
# Berechtigung ändern
chmod 755 /pfad/zum/verzeichnis
```

#### Problem: "Encoding-Fehler"
**Ursache**: Nicht-UTF-8-Zeichen in Dateinamen oder Inhalten
**Lösung**:
```python
# Im Skript nach Bedarf anpassen
with open(file, 'r', encoding='utf-8', errors='ignore') as f:
```

#### Problem: Unerwartete Ordner werden verarbeitet
**Ursache**: Ausschluss-Konfiguration nicht korrekt
**Lösung**:
```python
"EXCLUDE_FOLDERS": {
    # Alle unerwünschten Ordner hinzufügen
    ".git", "temp", "cache", "unerwünschter_ordner"
}
```

#### Problem: Links funktionieren in Obsidian nicht
**Ursache**: 
- Falsche Präfix-Konfiguration
- Dateinamen mit Sonderzeichen
- Leerzeichen in Dateinamen

**Lösungen**:
```python
# Präfix überprüfen
"FOLDER_LINK_PREFIX": ""  # oder gewünschter Präfix

# Für Dateinamen mit Leerzeichen:
# Obsidian behandelt diese automatisch korrekt
```

#### Problem: Bestehender Inhalt wird überschrieben
**Ursache**: Fehlende oder falsche AUTOGEN-Marker
**Überprüfung**:
```markdown
<!-- Suchen Sie nach diesen Markern in Ihren Dateien -->
<!-- AUTOGEN_START -->
<!-- AUTOGEN_END -->
```

**Wiederherstellung**:
- Git: `git checkout HEAD -- datei.md`
- Backup: Vorherige Version wiederherstellen

#### Problem: Skript läuft sehr langsam
**Ursachen**: 
- Große Anzahl von Dateien
- Langsame Festplatte
- Tiefe Ordnerstruktur

**Optimierungen**:
```python
# Mehr Ordner ausschließen
"EXCLUDE_FOLDERS": {
    ".git", "node_modules", ".venv", "__pycache__",
    ".obsidian", ".archive",
    "temp", "cache", "logs", "build", "dist"
}

# Versteckte Elemente ignorieren
"IGNORE_DOT_ITEMS": True
```

### Debug-Techniken

#### Verbose Output
Fügen Sie Debug-Prints hinzu:
```python
def process_dir(dir_path: Path, excluded: set):
    print(f"DEBUG: Processing {dir_path}")
    subs, mds, files = list_immediate(dir_path, excluded)
    print(f"DEBUG: Found {len(subs)} subdirs, {len(mds)} md files, {len(files)} other files")
```

#### Schritt-für-Schritt-Verarbeitung
```bash
# Nur ein Verzeichnis testen
python3 P25ObisLinks.py ./TestOrdner

# Mit Dry-Run beginnen
python3 P25ObisLinks.py ./TestOrdner --dry-run
```

### Fehlerbehandlung erweitern
Für robustere Verarbeitung können Sie das Skript erweitern:

```python
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_process_dir(dir_path: Path, excluded: set):
    try:
        process_dir(dir_path, excluded)
    except Exception as e:
        logger.error(f"Error processing {dir_path}: {e}")
        # Weiter mit nächstem Verzeichnis
```

## Best Practices

### Vorbereitung

#### 1. Backup erstellen
```bash
# Git-Repository initialisieren
git init
git add .
git commit -m "Before P25ObisLinks"

# Oder einfaches Backup
cp -r MeinVault MeinVault_backup
```

#### 2. Testlauf durchführen
```bash
# Immer zuerst mit --dry-run testen
python3 P25ObisLinks.py --dry-run
```

#### 3. Klein anfangen
```bash
# Erst einen Unterordner testen
python3 P25ObisLinks.py ./TestOrdner
```

### Konfiguration optimieren

#### 1. Projektspezifische Ausschlüsse
```python
# Für Entwicklungsprojekte
"EXCLUDE_FOLDERS": {
    ".git", "node_modules", ".venv", "__pycache__",
    "build", "dist", "target", ".idea", ".vscode"
}

# Für Dokumentation
"EXCLUDE_FOLDERS": {
    ".git", "temp", "drafts", "archive", "old"
}

# Für Obsidian Vaults
"EXCLUDE_FOLDERS": {
    ".obsidian", ".git", ".archive", "templates"
}
```

#### 2. Sinnvolle Präfixe
```python
# Für MOC-Struktur
"FOLDER_LINK_PREFIX": "MOC-"

# Für kategorisierte Struktur  
"FOLDER_LINK_PREFIX": "Cat-"

# Für hierarchische Tags
"FOLDER_LINK_PREFIX": ""  # Kein Präfix für einfache Links
```

### Wartung und Updates

#### 1. Regelmäßige Ausführung
```bash
# Wöchentliches Cron-Job
0 9 * * 1 cd /home/user/vault && python3 /pfad/zu/P25ObisLinks.py . >> /var/log/p25obislinks.log 2>&1
```

#### 2. Versionskontrolle
```bash
# Nach jeder Ausführung committen
python3 P25ObisLinks.py .
git add *.md
git commit -m "Update index files $(date)"
```

#### 3. Monitoring
```bash
#!/bin/bash
# monitor_changes.sh
before=$(find . -name "*.md" -exec wc -l {} + | tail -1)
python3 P25ObisLinks.py .
after=$(find . -name "*.md" -exec wc -l {} + | tail -1)
echo "Lines changed: $((after - before))"
```

### Ordnerstruktur-Design

#### 1. Konsistente Benennung
```
# Gut: Einheitliche Benennung
Marketing/
├── Strategien/
├── Kampagnen/
└── Analytics/

# Schlecht: Inkonsistente Benennung  
Marketing/
├── marketing_strategies/
├── Campaign-Ideas/
└── data & analytics/
```

#### 2. Logische Hierarchie
```
# Gut: Klare Hierarchie
Wiki/
├── Fachbereiche/
│   ├── IT/
│   ├── Marketing/
│   └── Finanzen/
├── Projekte/
│   ├── Aktuell/
│   └── Archiv/
└── Persönlich/
    ├── Ziele/
    └── Reflexion/

# Schlecht: Flache, unorganisierte Struktur
Wiki/
├── IT-Stuff/
├── Random-Thoughts/
├── Project-A-Notes/
├── Project-B-Ideas/
├── Marketing-Things/
└── Finance-Random/
```

#### 3. Index-Datei-Strategie
```markdown
<!-- Gute Index-Datei: Eigener Inhalt + Auto-Links -->
# IT Überblick

## Meine Schwerpunkte
- Python-Entwicklung
- Web-Technologien
- DevOps

## Aktuelle Projekte  
- [[Projekt-A]]
- [[Projekt-B]]

<!-- AUTOGEN_START -->
# Auto-generierte Links hier
<!-- AUTOGEN_END -->

## Externe Ressourcen
- [Python.org](https://python.org)
- [MDN](https://developer.mozilla.org)
```

### Performance-Optimierung

#### 1. Ausschluss-Optimierung
```python
# Große Ordner ausschließen
"EXCLUDE_FOLDERS": {
    ".git", "node_modules", ".venv", "__pycache__",
    "cache", "tmp", "temp", "logs", "backup",
    "media", "images", "videos"  # Große Medien-Ordner
}
```

#### 2. Selektive Verarbeitung
```bash
# Statt des ganzen Vaults nur geänderte Bereiche
python3 P25ObisLinks.py ./Projekte/Aktuell
python3 P25ObisLinks.py ./Wiki/IT
```

#### 3. Parallelisierung (Erweitert)
Für sehr große Strukturen könnte eine parallele Version sinnvoll sein:

```python
from concurrent.futures import ThreadPoolExecutor
import threading

def parallel_walk(root: Path, excluded: set, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for dirpath, dirnames, filenames in os.walk(root):
            p = Path(dirpath)
            if should_process(p, excluded):
                future = executor.submit(process_dir, p, excluded)
                futures.append(future)
        
        # Warten auf Completion
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Error: {e}")
```

## FAQ

### Allgemeine Fragen

**Q: Kann ich das Skript auf Windows verwenden?**
A: Ja, Python läuft auf Windows. Verwenden Sie `python` statt `python3`:
```cmd
python P25ObisLinks.py
```

**Q: Funktioniert das Skript mit anderen Markdown-Editoren außer Obsidian?**
A: Ja, das Skript generiert Standard-Markdown-Links. Die Funktionalität hängt vom Editor ab:
- **Obsidian**: Vollständige Unterstützung für `[[]]` Links und `![[]]` Einbettungen
- **Typora**: Unterstützt `[[]]` Links teilweise  
- **Mark Text**: Zeigt Links als Text an
- **VS Code**: Mit entsprechenden Extensions funktionsfähig

**Q: Was passiert wenn ich eine Index-Datei manuell lösche?**
A: Beim nächsten Ausführen wird sie neu erstellt. Bestehende Links von anderen Dateien bleiben erhalten.

**Q: Kann ich das Skript automatisch bei Dateiänderungen ausführen lassen?**
A: Ja, mit File-Watching-Tools:
```bash
# Mit inotifywait (Linux)
inotifywait -m -r -e create,delete,move . | while read; do
    python3 P25ObisLinks.py .
done

# Mit fswatch (macOS)
fswatch -o . | xargs -n1 -I{} python3 P25ObisLinks.py .
```

### Konfigurationsfragen

**Q: Wie ändere ich die Sortierreihenfolge?**
A: Modifizieren Sie die `list_immediate` Funktion:
```python
# Nach Datum sortieren (neuste zuerst)
subs = sorted([d for d in path.iterdir()
               if d.is_dir() and not is_hidden(d) and d.name not in excluded],
              key=lambda p: p.stat().st_mtime, reverse=True)

# Nach Größe sortieren
subs = sorted([d for d in path.iterdir()
               if d.is_dir() and not is_hidden(d) and d.name not in excluded],
              key=lambda p: sum(f.stat().st_size for f in p.rglob('*')))
```

**Q: Kann ich verschiedene Präfixe für verschiedene Ordnerebenen verwenden?**
A: Das erfordert eine Anpassung des Skripts:
```python
def get_prefix_for_level(level: int) -> str:
    prefixes = ["", "L1-", "L2-", "L3-"]
    return prefixes[min(level, len(prefixes)-1)]
```

**Q: Wie kann ich bestimmte Dateitypen ausschließen?**
A: Erweitern Sie die Filterlogik:
```python
EXCLUDE_EXTENSIONS = {".tmp", ".bak", ".DS_Store"}

def should_include_file(file_path: Path) -> bool:
    return file_path.suffix.lower() not in EXCLUDE_EXTENSIONS
```

### Fehlerbehebung

**Q: Das Skript überschreibt meinen manuell geschriebenen Links-Bereich**
A: Stellen Sie sicher, dass Ihr manueller Bereich nicht zwischen `<!-- AUTOGEN_START -->` und `<!-- AUTOGEN_END -->` steht. Nur dieser Bereich wird ersetzt.

**Q: Manche Ordner werden nicht verarbeitet obwohl sie nicht in EXCLUDE_FOLDERS stehen**
A: Überprüfen Sie:
- Versteckte Ordner (beginnen mit `.`) werden standardmäßig ignoriert
- Rechtschreibung in der Ausschluss-Liste
- Berechtigugen für den Ordner

**Q: Die generierten Links funktionieren nicht in Obsidian**
A: Mögliche Ursachen:
- Leerzeichen in Dateinamen (sollte funktionieren)
- Sonderzeichen in Dateinamen
- Falsche Präfix-Konfiguration
- Datei existiert nicht mehr

**Q: Das Skript läuft in einer Endlosschleife**
A: Das passiert bei zirkulären Symlinks. Fügen Sie Symlink-Behandlung hinzu:
```python
def safe_walk(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        # Symlinks aus dirnames entfernen
        dirnames[:] = [d for d in dirnames if not (Path(dirpath) / d).is_symlink()]
```

### Erweiterte Anwendungen

**Q: Kann ich eigene Sektionen hinzufügen?**
A: Ja, modifizieren Sie die `build_block` Funktion:
```python
# Eigene Sektion für Bilder
image_files = [f for f in other_files if f.suffix.lower() in {'.png', '.jpg', '.gif'}]
if image_files:
    parts.append("\n---\n#Images")
    parts.extend([f"![[{f.name}]]" for f in image_files])

# Eigene Sektion für PDFs  
pdf_files = [f for f in other_files if f.suffix.lower() == '.pdf']
if pdf_files:
    parts.append("\n---\n#PDFs")
    parts.extend([f"![[{f.name}]]" for f in pdf_files])
```

**Q: Wie kann ich Metadaten zu den Links hinzufügen?**
A: Erweitern Sie die Link-Generierung:
```python
# Mit Dateigröße
for f in md_files:
    size = f.stat().st_size
    size_str = f"({size} bytes)" if size < 1024 else f"({size//1024}KB)"
    md_lines.append(f"![[{f.name}]] {size