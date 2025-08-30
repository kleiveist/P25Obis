# YAML Frontmatter Manager

Ein Python-Tool zur automatischen Verwaltung von YAML-Frontmatter in Markdown-Dateien basierend auf einer konfigurierbaren Template-Datei.

## 🚀 Features

- **Template-basiert**: Definiere dein YAML-Frontmatter einmal in `YAML.ini`
- **Dynamische Platzhalter**: Automatische Ersetzung von Ordnernamen, Datum und mehr
- **Konsistente Reihenfolge**: Die Position in der Template-Datei bestimmt die Ausgabereihenfolge
- **Flexible Modi**: Strict-Modus für vollständige Kontrolle oder Merge-Modus für Kompatibilität
- **Rekursive Verarbeitung**: Durchsucht automatisch alle Unterordner
- **Whitelist-Unterstützung**: Behalte bestimmte Felder auch im Strict-Modus

## 📋 Voraussetzungen

- Python 3.7+
- PyYAML

```bash
pip install pyyaml
```

## 🛠 Installation

1. Repository klonen:
```bash
git clone https://github.com/username/yaml-frontmatter-manager.git
cd yaml-frontmatter-manager
```

2. Dependencies installieren:
```bash
pip install -r requirements.txt
```

## 📖 Verwendung

### Grundlegende Verwendung

1. Erstelle eine `YAML.ini` Datei in deinem Projektverzeichnis
2. Führe das Skript aus:

```bash
python yaml_manager.py
```

Das Skript verarbeitet automatisch alle `.md` Dateien im aktuellen Verzeichnis und allen Unterordnern.

### Erweiterte Optionen

```bash
# Bestimmtes Verzeichnis als Root verwenden
python yaml_manager.py --root /path/to/your/markdown/files

# Dry-run (zeigt Änderungen ohne sie durchzuführen)
python yaml_manager.py --dry-run

# Verbose Output
python yaml_manager.py --verbose
```

## 📄 YAML.ini Konfiguration

### Basis-Template

```yaml
# Grundlegende Metadaten (Reihenfolge bestimmt Ausgabe!)
Datum: %datum%
Projekt: MeinProjekt
field: %folder0%
tags:
  - %folder1%
  - Wiki
  - =leer=

# Settings (optional)
*settings:
  key_mode: strict
  keep_extra_keys: ["rank", "custom-*"]
  exclude_folders: [".git", ".obsidian", "node_modules"]
```

### Verfügbare Platzhalter

#### Pfad-Platzhalter
| Platzhalter | Beschreibung |
|-------------|--------------|
| `%data%` | Name der aktuellen Datei |
| `%folder%` | Root-Verzeichnis (wo Skript ausgeführt wird) |
| `%folder0%` | Direkter Elternordner der .md-Datei |
| `%folder1%`, `%folder2%`, ... | N Ebenen über der .md-Datei |
| `%root0%`, `%root1%`, ... | Pfad vom Start-Root nach unten |

#### Spezielle Platzhalter
| Platzhalter          | Beschreibung                  |
| -------------------- | ----------------------------- |
| `%datum%` / `%date%` | Erstellungsdatum (YYYY-MM-DD) |
| `%wert%`             | Vorhandenen Wert beibehalten  |
| `=leer=`             | Leeren String setzen          |

#### Ordnerstruktur-Beispiel

```
C:\Projekte\Wiki\           ← %folder% (Skript-Root)
├── YAML.ini
├── Universität\            ← %folder2% (von test.md aus)
│   └── BWL\                ← %folder1% (von test.md aus)
│       └── Klausuren\      ← %folder0% (von test.md aus)
│           └── test.md
```

### Settings-Konfiguration

#### key_mode
- **`strict`** (Standard): Nur Template-Keys werden geschrieben, andere werden entfernt
- **`merge`**: Template überschreibt vorhandene Keys, zusätzliche Keys bleiben erhalten

#### keep_extra_keys (nur bei strict)
Liste von Keys oder Glob-Patterns, die trotz strict-Modus beibehalten werden:

```yaml
*settings:
  keep_extra_keys:
    - rank              # Exakter Key-Name
    - custom-*          # Alle Keys mit Präfix "custom-"
    - obsidian_*        # Alle Keys mit Präfix "obsidian_"
```

#### exclude_folders
Ordner, die bei der Verarbeitung übersprungen werden:

```yaml
*settings:
  exclude_folders: [".git", "node_modules", ".obsidian", ".venv"]
```

## 📁 Beispiel-Workflow

### Vorher
```markdown
---
rank: Altwert
custom_field: BehaltenWert
---

# Meine Notiz
Inhalt...
```

### YAML.ini
```yaml
Datum: %date%
Projekt: Wiki
field: %folder0%
rank: %folder1%

*settings:
  key_mode: strict
  keep_extra_keys: ["custom_field"]
```

### Nachher
```markdown
---
Datum: '2025-08-21'
Projekt: Wiki
field: Klausuren
rank: BWL
custom_field: BehaltenWert
---

# Meine Notiz
Inhalt...
```

## 🔧 Erweiterte Funktionen

### Datum-Handling
Das Skript verwendet intelligente Datum-Erkennung:
- **macOS/Windows**: Echte "birth time" (Erstellungszeit)
- **Linux**: Fallback auf Änderungszeit (`mtime`)

### Konsistenz-Garantie
- Mehrfache Ausführung produziert identische Ergebnisse
- Keine Duplikation von Feldern
- Deterministische Reihenfolge

## 🐛 Fehlerbehandlung

Das Skript:
- Überspringt ungültige YAML-Dateien mit Warnung
- Erstellt Backups vor Änderungen (optional)
- Protokolliert alle Änderungen im Verbose-Modus

## 🤝 Beitragen

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Committe deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne eine Pull Request

## 📝 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe [LICENSE](LICENSE) Datei für Details.


## 🙏 Danksagungen

- Inspiriert durch die Bedürfnisse beim Management von Obsidian Vaults
- Dank an die Python-Community für PyYAML