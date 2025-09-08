# Obis Tools – Projektübersicht

> Sammlung schlanker Python‑Skripte zur Verwaltung von Markdown‑Repos/Vaults (Obsidian‑kompatibel):
>
> - **ObisDatabase** – YAML‑Frontmatter Manager
> - **ObisRenamer** – Deterministischer Datei‑Renamer
> - **P25ObisLinks** – Automatische Index/Links‑Generatoren

---

## Inhaltsverzeichnis

1. Überblick
2. Features
3. Module
   - 3.1 ObisDatabase
   - 3.2 ObisRenamer
   - 3.3 P25ObisLinks
4. Installation & Systemvoraussetzungen
5. Quickstart
6. Repository‑Struktur
7. Konfiguration (INI/YAML)
8. Zusammenspiel der Module (Pipelines)
9. CLI‑Referenz (Kurz)
10. Best Practices
11. Troubleshooting (Kurz)
12. Roadmap
13. Beiträge/Contributing
14. Lizenz

---

## 1) Überblick

Die **Obis Tools** standardisieren Dateinamen, Metadaten (YAML‑Frontmatter) und Ordner‑Indexe in Markdown‑Repos. Fokus: deterministische Ergebnisse, reproduzierbare Regeln, einfache Abhängigkeiten, plattformneutral.

- **Zielgruppe:** technische Doku, Studien‑/Lehr‑Vaults, Wissensdatenbanken.
- **Designprinzipien:** Idempotenz, klare Ebenenlogik, minimale Konfiguration.

Weiterführende Doku pro Modul:
- 📘 **ObisDatabase – Guide:** [`./ObisDatabase-Guide.md`](./ObisDatabase-Guide.md)
- 📘 **ObisRenamer – Guide:** [`./ObisRenamer-Guide.md`](./ObisRenamer-Guide.md)
- 📘 **P25ObisLinks – Guide:** [`./P25ObisLinks-Guide.md`](./P25ObisLinks-Guide.md)

---

## 2) Features

- **Deterministische Pipelines:** Umbenennen → Frontmatter → Index.
- **Platzhalter‑System:** `%rootN%`, `%folderN%`, `%data%`, `%date%`, `%datum%`, `%wert%`, `%N%` (Ordnernummer‑Extraktion).
- **Skalierbar:** rekursive Verarbeitung, Ausschlüsse (Ordner/Endungen/Namen).
- **Sicher:** Dry‑Run (Renamer/Links), zweiphasige Umbenennung, idempotente Frontmatter‑Writes.
- **Git‑freundlich:** stabile Reihenfolgen, Block‑YAML, klare Diffs.

---

## 3) Module

### 3.1 ObisDatabase (YAML‑Frontmatter)
- **Script:** `ObisDatabase.py`
- **Aufgabe:** Setzt/aktualisiert YAML‑Frontmatter anhand einer Vorlage (INI/YAML) mit strikter Feldreihenfolge.
- **Modi:** `strict` (Whitelist für Extra‑Keys) und `merge`.
- **Anker/Scope:** `base_root` + `scope_under_base_root` beschränken den Wirkungsbereich.
- **Guide:** [`./ObisDatabase-Guide.md`](./ObisDatabase-Guide.md)

### 3.2 ObisRenamer (Datei‑Renamer)
- **Script:** `ObisRenamer.py`
- **Aufgabe:** deterministisches Umbenennen nach Ebenen‑Patterns (`levelN`) und Platzhaltern; Nummerierung pro Ordner **und** Dateiendung.
- **Sicherheit:** zweiphasige Umbenennung, Kollision‑Suffix `_2`, `_3` …
- **Dry‑Run:** `--dry` zeigt geplante Änderungen.
- **Guide:** [`./ObisRenamer-Guide.md`](./ObisRenamer-Guide.md)

### 3.3 P25ObisLinks (Index/Links)
- **Script:** `P25ObisLinks.py` (benannt wie im Guide; einfache Standardbibliothek)
- **Aufgabe:** erzeugt/aktualisiert Ordner‑Indexseiten mit Sektionen `#Folder`, `#Markdown`, `#Files` zwischen Marker‑Blöcken.
- **Dry‑Run:** `--dry-run` simuliert die Änderungen.
- **Guide:** [`./P25ObisLinks-Guide.md`](./P25ObisLinks-Guide.md)

---

## 4) Installation & Systemvoraussetzungen

- **Python:** 3.8+ (3.6 kompatibel, empfohlen ≥3.8).
- **Abhängigkeiten:**
  - `ObisDatabase.py`: `PyYAML` (`pip install pyyaml`)
  - `ObisRenamer.py`: Standardbibliothek
  - `P25ObisLinks.py`: Standardbibliothek
- **Empfehlung:** Git für Backups/Diffs.

```bash
# global
python --version

# Dependency für ObisDatabase
pip install pyyaml
```

---

## 5) Quickstart

```bash
# 1) Backup anlegen
cp -r Vault Vault-backup-$(date +%Y%m%d)

# 2) (optional) Umbenennen – Dry‑Run prüfen
python ObisRenamer.py --root ./Vault --dry
python ObisRenamer.py --root ./Vault

# 3) Frontmatter setzen/aktualisieren
python ObisDatabase.py --root ./Vault

# 4) Indexe generieren/aktualisieren (Dry‑Run optional)
python P25ObisLinks.py ./Vault --dry-run
python P25ObisLinks.py ./Vault
```

- Konfigurationen/Guides vorher prüfen:
  - [`./ObisRenamer-Guide.md`](./ObisRenamer-Guide.md)
  - [`./ObisDatabase-Guide.md`](./ObisDatabase-Guide.md)
  - [`./P25ObisLinks-Guide.md`](./P25ObisLinks-Guide.md)

---

## 6) Repository‑Struktur (Beispiel)

```
📂 P25Python-Obis
├── LICENSE.md
├── README.md
├── 📂 P25ObisDatabase/
│   ├── ObisDatabase.py
│   ├── ObisDatabase-Guide.md
│   └── ObisDatabase.ini
├── 📂 P25ObisRenamer/
│   ├── ObisRenamer.py
│   ├── ObisRenamer-Guide.md
│   └── ObisRenamer.ini
└── 📂 P25ObisLinks/
    ├── P25ObisLinks.py
    └── P25ObisLinks-Guide.md
```

> Hinweis: Archiv‑ und Versionsordner (`.archive`, `V0.0.x`) sind hier verkürzt dargestellt. Die Guides liegen in den jeweiligen Modulordnern.

## 7) Konfiguration (INI/YAML) (INI/YAML) (INI/YAML)

- **ObisDatabase:** Vorlage + `_settings` (Modus, Whitelist, Excludes, Anker). Platzhalter: `%rootN%`, `%folderN%`, `%data%`, `%date%`/`%datum%`, `%wert%`, `=leer=`.
- **ObisRenamer:** `[patterns] levelN` pro Tiefe, `[options] numbering_width / use_birthtime`, `[excludes] folders/filetypes/filenames`. Platzhalter: `%rootN%`, `%rootNB%`, `%folder%`, `%N%`, `%date%`/`%datum%`, `%wert%`.
- **P25ObisLinks:** `SETTINGS` im Script (Excludes, Präfixe, Dot‑Items) – siehe Guide.

Konkrete Beispiele: siehe Modul‑Guides.

---

## 8) Zusammenspiel der Module (Pipelines)

**Empfohlene Reihenfolge:**

1. **Renamer** – stabile, sortierbare Dateinamen (kontextuelle Präfixe + Nummer).
2. **Database** – konsistentes Frontmatter aus Vorlage (idempotent).
3. **Links** – saubere Ordner‑Indexe mit Ordner/Markdown/Files‑Sektionen.

**Varianten:**
- Bei existierender starker Frontmatter‑Struktur: Database zuerst, Renamer optional.
- Für reine Link‑Übersichten: nur P25ObisLinks ausführen.

---

## 9) CLI‑Referenz (Kurz)

### ObisDatabase
```bash
python ObisDatabase.py [--root PATH]
```

### ObisRenamer
```bash
python ObisRenamer.py [--root PATH] [--config PATH] [--dry]
```

### P25ObisLinks
```bash
python P25ObisLinks.py [ROOT] [--dry-run]
```

---

## 10) Best Practices

- **Immer Backup/Git‑Commit** vor einem Run.
- **Dry‑Run** beim Renamer/Links, dann Stichproben prüfen.
- **Strikte Templates** (Database) mit minimaler Whitelist.
- **Excludes** früh setzen (`.git`, `node_modules`, `.venv`, `.obsidian`, `__pycache__`, `.archive`).
- **ISO‑Daten/Block‑YAML** für saubere Diffs und Dataview‑Kompatibilität.

---

## 11) Troubleshooting (Kurz)

- **PyYAML fehlt:** `pip install pyyaml` (für ObisDatabase).
- **Keine Änderungen im Renamer‑Dry‑Run:** passendes `levelN` fehlt oder Excludes greifen zu stark.
- **Falsches Datum:** `use_birthtime` (OS‑abhängig), sonst `mtime`.
- **Marker/Index fehlt:** P25ObisLinks erzeugt Datei neu; bestehender Inhalt außerhalb der Marker bleibt erhalten.

→ Details und Checklisten: Modul‑Guides.

---

## 12) Roadmap

- Optionales **DB‑Generator‑Addon** (Data‑*.md) als separates Modul.
- Zusätzliche Platzhalter/Funktionen im Renamer.
- Tests & CI (Smoke/Dry‑Run auf Beispielvault).

---

## 13) Beiträge / Contributing

1. Fork & Branch (`feature/…`).
2. Lint/Format (PEP8‑konform, kurze Funktionen, keine Fremd‑Deps ohne Not).
3. PR mit kurzen Before/After‑Beispielen (Screens/Diffs).

---

## 14) Lizenz

MIT – siehe [`LICENSE.md`](./LICENSE.md).

