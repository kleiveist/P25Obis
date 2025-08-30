---
Datum: '2025-08-21'
Projekt: Wiki
field: Blobbite
tags:
- Wiki
- P24Python-OBSIDION
link1: ''
---

# Vollständiger Prompt: YAML-Frontmatter Manager mit Konfigurationsdatei

## Kurz & vollständig – verfügbare Platzhalter/Werte in `YAML.ini`:

- **Text**: Normale YAML-Werte (Text, Zahl, Bool, Listen, Maps)
- `%data%` → automatisch namen der datei in der geschrieben wird.
- `%root0%` , `%folder%` → Name des Start-Roots (wo Skript/--root läuft)
- `%root1%` , `%root2%`  … → vom Start-Root nach unten entlang des Dateipfads
- `%folder%` → Name des Start-Roots (wo Skript/--root läuft)
- `%folder0%` → Ordnername der .md (direkter Elternordner)
- `%folder1%`, `%folder2%`, … `%folderN%` → N Ebenen über der .md-Datei
- `%datum%` / `%date%` → Erstellungsdatum der Datei im Format YYYY-MM-DD
- `=leer=` → **Mapping**: Feld wird als leerer String gesetzt
- `%wert%` → vorhandenen Wert in der .md **beibehalten** (wenn Feld existiert); wenn nicht vorhanden, **kein** Feld anlegen

**Hinweis**: Platzhalter funktionieren auch in Strings (z. B. `"[[%folder1%-%folder0%]]"`).

## Ziel

Python-Skript, das eine YAML.ini Konfigurationsdatei verwendet, um YAML-Frontmatter in Markdown-Dateien automatisch zu verwalten.

## Funktionalität der YAML.ini

In der Konfigurationsdatei können so viele Attribute eingetragen werden wie gewünscht. Diese werden nach dem Ausführen des Skripts in die Markdown-Dateien übernommen.

**Das Skript verwendet selbständig den Pfad, in dem es ausgeführt wurde, und arbeitet sich dann abwärts nach unten durch alle Unterordner.**

## Datenkonistenz und Position

**Wichtig**: Daten müssen konsistent erhalten werden, sonst gibt es bei Änderung und erneutem Ausführen des Skripts immer mehr Attribute.

### Positionslogik:
- Die **Position** der Felder in der YAML.ini bestimmt die **Reihenfolge** im Frontmatter
- Felder können nach unten hin verlängert oder durch Entfernen aus der YAML.ini wieder entfernt werden
- **Nur in YAML.ini definierte Felder** werden verwaltet - andere bleiben unverändert, werden aber **entfernt**

### Beispiel - Feld entfernen:
**Vorher (.md)**
```yaml
---
rank: Altwert
---
```

**YAML.ini**
```yaml
field: %folder1%
```

**Nachher (.md)**
```yaml
---
# rank: Altwert wird entfernt (nicht mehr im Template)
field: BWL01       # NEUES Feld aus der INI
---
```

### Beispiel - Feld ersetzen:
**Vorher (.md)**
```yaml
---
rank: Altwert
---
```

**YAML.ini**
```yaml
rank: %folder1%
field: Altwert
```

**Nachher (.md)**
```yaml
---
rank: BWL01        # Ersetzt durch Template-Wert
field: Altwert     # NEUES Feld aus der INI
---
```

## Optionen für Werte:

- **Feste Werte**: Namen werden direkt übernommen
- **Leere Einträge**: `=leer=` erstellt leere Felder
- **Datum**: `%date%` verwendet automatisch das Erstellungsdatum der Datei (YYYY-MM-DD Format)
- **Wert beibehalten**: `%wert%` verwendet den vorhandenen Wert aus der .md (setzt nichts wenn nicht vorhanden)
- **Dateiname**: "%data%" verwendet automatisch namen der datei in der geschrieben wird.
### Optionen für Werte (Folder/Root)
- **Vom Start-Root nach unten (stabil pro Projektstruktur)**
    - `%root0%` → Start-Root-Name (entspricht `%folder%`)
    - `%root1%` → erster Unterordner unterhalb Start-Root auf dem Weg zur Date
    - `%root2%` → zweiter Unterordner, usw.
    - **Fallback:** Ist der Index zu groß, wird `%root0%` verwendet
- **Von der Datei nach oben (abhängig von Dateitiefe)**
    - `%folder0%` → Elternordner der Datei
    - `%folder1%` → 1 Ebene über der Datei
    - `%folder2%` → 2 Ebenen über der Datei, usw.
    - **Fallback:** Ist der Index zu groß, wird `%folder0%` verwendet
### Optionen für Werte (Folder):

- **Ordnername-md** (aktuell): `%folder0%` verwendet den Ordnernamen, in dem sich die .md-Datei befindet
- **Ordnername1** (2 Ebene höher): `%folder1%` verwendet den Ordnernamen 2 Ebene über der .md-Datei
- **Ordnername2** (1 Ebenen höher): `%folder2%` verwendet den Ordnernamen 1 Ebenen über der .md-Datei
- **Ordnernamex** (x Ebenen höher): `%folderx%` verwendet den Ordnernamen x Ebenen über der .md-Datei
  - **Fallback-Regel**: Falls nicht genügend Ordner vorhanden sind (z.B. `%folder10%` bei nur 3 Ordnern), wird `%folder0%` verwendet
- **Ordnername (Python-Ausführung)**: `%folder%` verwendet den Ordnernamen, wo das Python-Skript ausgeführt wurde

### Ordnerstruktur-Beispiele:

```
C:\Studium\                     ← %folder% (Python ausgeführt) 
├── Wiki\                       ← %root%
│   └── BZ\                     ← %root1%
│       └── Gameentwicklung\    ← %root0%
│           └── test.md
```

```
C:\Studium\                    ← %folder% (Python ausgeführt)
├── YAML.ini
├── script.py
├── Universität\               ← %folder1% (5 Ebenen über .md)
│   └── Fakultät\              ← %folder2% (4 Ebenen über .md)
│       └── Studiengang\       ← %folder3% (3 Ebenen über .md)
│           └── SE1\           ← %folder4% (2 Ebenen über .md)
│               └── BWL01\     ← %folder5% (1 Ebene über .md)
│                   └── Klausuren\ ← %folder0% (.md-Ordner)
│                       └── test.md
```

## Datum-Funktionalität

```python
def get_creation_date(p: Path) -> str:
    """
    YYYY-MM-DD. Bevorzugt echte 'birth time' (macOS/Windows),
    sonst fällt zurück auf st_mtime (Inhaltsänderung).
    """
    st = p.stat()
    try:
        # macOS/Windows
        ts = st.st_birthtime  # type: ignore[attr-defined]
    except AttributeError:
        # Linux-Fallback: mtime statt ctime (meist stabiler bzgl. Kopieren)
        ts = st.st_mtime
    return datetime.date.fromtimestamp(ts).isoformat()
```

## Beispiel YAML.ini Konfigurationsdatei

```yaml
# YAML.ini - Konfiguration für Frontmatter Manager
# Diese Datei definiert, welche YAML-Felder in alle .md-Dateien eingefügt werden

# Grundlegende Metadaten (Position bestimmt Reihenfolge!)
Datum: %datum%                    # Automatisches Erstellungsdatum der .md-Datei
Projekt: IUFS                     # Fester Projektwert
Semester: %folder2%               # Verwendet Ordnername 2 Ebenen höher
Section: %wert%                   # Behält vorhandenen Wert bei
rank: %folder1%                   # Verwendet Ordnername 1 Ebene höher
status: draft                     # Fester Statuswert

# Tags (Liste)
tags:
  - %folder1%                     # Ordnername als Tag
  - BWL01                         # Fester Tag
  - Klausurpng01                  # Fester Tag
  - =leer=                        # Wird als leerer String gesetzt

# Links und Referenzen
link: "[[%folder1%]]"             # Link zum übergeordneten Ordner
link1: "[[BWL01-Klausurpng01]]"   # Fester Link
backlink: =leer=                  # Leeres Feld
reference: "Semester %folder2%"   # Kombinierter Text mit Ordnername

# Zusätzliche Felder (auskommentiert = nicht aktiv)
#author: =leer=                   # Leeres Autorfeld
#priority: medium                 # Feste Priorität
#reviewed: false                  # Boolean-Wert
```

## Anforderungen an das Skript

1. **Konfiguration laden**: Das Skript soll die Einstellungen aus der YAML.ini abrufen
2. **Markdown-Verarbeitung**: Entsprechend den Einträgen soll das YAML-Frontmatter bei jeder .md-Datei durchgeführt werden
3. **Konsistenz**: Nur in YAML.ini definierte Felder verwalten, andere entfernen
4. **Position**: Reihenfolge der Felder entspricht der Reihenfolge in YAML.ini
5. **Dateiname**: Die Einstellungsdatei soll den Namen YAML.ini haben

## Settings-Konfiguration

### *settings.key_mode*
**Werte**: `strict` (Default) oder `merge`

- **strict**: Nur die in YAML.ini definierten Keys werden geschrieben (Reihenfolge = Vorlage). Alle anderen vorhandenen Frontmatter-Keys werden entfernt, außer sie sind in `keep_extra_keys` whitelisted.
- **merge**: Vorlage überschreibt gleichnamige Keys. Zusätzliche vorhandene Keys bleiben erhalten (werden unter den Template-Keys angehängt). `keep_extra_keys` ist hier wirkungslos.

### *settings.keep_extra_keys*
**Wert**: Liste von Key-Namen oder Glob-Patterns (fnmatch), nur relevant bei `key_mode: strict`.

**Zweck**: Bestimmte vorhandene Keys trotz strict behalten.

**Beispiele**:
```yaml
keep_extra_keys:
  - rank              # exakter Key
  - custom-*          # alle Keys, die mit 'custom-' beginnen
  - obsidian_*        # Unterstrich-Pattern (optional)
```

### *settings.exclude_folders*
**Wert**: Liste von Ordnernamen/Globs, die rekursiv übersprungen werden.

**Beispiel**:
```yaml
exclude_folders: [".git", "node_modules", ".obsidian", ".venv", "__pycache__"]
```

### Mini-Beispiele

#### Strict + Whitelist
```yaml
*settings:
  key_mode: strict
  keep_extra_keys: ["rank", "custom-*"]

# Ergebnis: Nur Template-Keys in vorgegebener Reihenfolge
# + vorhandene 'rank' und alle 'custom-*' bleiben zusätzlich erhalten.
```

#### Merge
```yaml
*settings:
  key_mode: merge

# Ergebnis: Template-Keys überschreiben; alle anderen vorhandenen Keys bleiben unten erhalten.
```

## Gewünschtes Verhalten

Das Skript durchsucht alle .md-Dateien in einem Verzeichnis und wendet die YAML.ini Konfiguration auf das Frontmatter jeder Datei an, wobei:

- Dynamische Werte wie Ordnernamen automatisch ersetzt werden
- Die Position der Felder der YAML.ini entspricht
- Nur definierte Felder verwaltet werden
- Konsistenz bei mehrfacher Ausführung gewährleistet ist