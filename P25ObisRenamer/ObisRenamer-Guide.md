---
Datum: '2025-09-08'
Projekt: IUFS
Komponente: ObisRenamer
Version: Guide-Rev1
Tags: [Renamer, INI, Platzhalter, YAML, Obsidian]
---

# ObisRenamer – Technischer Leitfaden (überarbeitet)

> Rekursives, deterministisches Umbenennen von Dateien anhand einer INI-Konfiguration. Fokus: reproduzierbare Präfixe, klare Ebenen-Logik, sichere Umbenennungsphase, Excludes.

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

### 1.1 Ziel
- Konsistente Dateinamen entlang einer Ordnerhierarchie durch **Ebenen-basierte Muster** (`level1`, `level2`, …).
- Deterministische **Platzhalterersetzung** für Pfadsegmente, Datum, Altname u. a.
- **Nummerierung pro Ordner und Dateiendung**, Breite konfigurierbar (z. B. `01`, `002`).
- Sicherheit durch **zweiphasige Umbenennung** (Kollisionsvermeidung).
- **Ausschlusslisten** für Ordner, Dateitypen, Einzeldatenamen.

### 1.2 Nicht-Ziele
- Kein in-place Bearbeiten von Datei-Inhalten (nur Namen).
- Keine Metadatenbearbeitung (EXIF/ID3 etc.).
- Kein Netz-/Cloud-spezifisches Verhalten (lokales FS im Fokus).

### 1.3 Typische Einsatzgebiete
- Studien-/Kursordner: eindeutige, sortierbare Bezeichnungen.
- Projektsammlungen: konsistente, maschinenlesbare Präfixe.
- Medien-/Scan-Archive: Datum+Kontext+laufende Nummer.

### 1.4 Ergebnisseigenschaften
- **Idempotent** bei unveränderter Struktur/Konfiguration (erneute Runs erzeugen keine Änderungen).
- **Stabil** gegenüber Namenskollisionen (Fallback `_2`, `_3`, …).
- **Vorhersagbar** dank fester Regelwerke (INI + Platzhalter).

---

## 2. Installation und Setup

### 2.1 Voraussetzungen
- Python ≥ 3.8 (empfohlen; lauffähig ab 3.6).
- Standardbibliothek ausreichend (keine externen Abhängigkeiten).
- Schreibrechte im Zielbaum.

### 2.2 Verzeichnisstruktur (Beispiel)
```
Vault/
├─ ObisRenamer.py
├─ ObisRenamer.ini
└─ SE1/
   ├─ BBWL01/
   │  ├─ Skript/
   │  └─ Klausur/
   └─ STAT02/
```

### 2.3 Schnelltest
```bash
python --version
python ObisRenamer.py --dry
```

### 2.4 Backup dringend empfohlen
```bash
cp -r Vault Vault-backup-$(date +%Y%m%d)
# oder mit Git
git add . && git commit -m "Pre-rename backup"
```

---

## 3. Grundlegende Verwendung

### 3.1 Standardaufruf (aktuelles Verzeichnis als Root)
```bash
python ObisRenamer.py
```

### 3.2 Root definieren
```bash
python ObisRenamer.py --root /pfad/zu/Vault
```

### 3.3 Alternative INI angeben
```bash
python ObisRenamer.py --config ./MeinSchema.ini
```

### 3.4 Trockenlauf (empfohlen)
```bash
python ObisRenamer.py --dry
# zeigt geplante Umbenennungen ohne Änderungen
```

### 3.5 Exit-Codes (kurz)
- `0`: Erfolg.  
- `1`: Laufzeitfehler (z. B. Kollision, Rechteproblem).  
- `2`: Pfad-/Konfigurationsproblem (Root/INI nicht gefunden).

---

## 4. Konfiguration

> Die INI besteht aus **[patterns]**, **[options]** und **[excludes]**. Jeder **levelN**-Schlüssel in `[patterns]` beschreibt das **Präfix** für Dateien auf Ebene *N* (Dateien in Ordnern mit *N* Segmenten relativ zum Start-Root).

### 4.1 Beispiel-INI (kompakt)
```ini
[patterns]
level1 = %root1%
level2 = %root2%
level3 = %root2%-%root3%
level4 = %root2%-%root3%-%root4%

[options]
numbering_width = 2
use_birthtime = false

[excludes]
folders = .git, .venv, __pycache__, .obsidian, .archive, node_modules
filetypes = .md, .py, .ini, .exe
filenames = .wichtig.doxc, .setting.excel
```

### 4.2 Ebenen-Definition
- **level1**: Dateien in `<root>/<ordner1>/*`
- **level2**: Dateien in `<root>/<ordner1>/<ordner2>/*`
- usw.  
> Dateien **direkt im Root** (Tiefe 0) werden nur berücksichtigt, wenn `level0` definiert ist (Standard: nicht gesetzt → keine Umbenennung auf Ebene 0).

### 4.3 Platzhalter (gemeinsam für alle Patterns)
- `%root%` / `%folder%`: Name des Start-Roots (Basename des `--root`).
- `%rootN%` / `%folderN%` (N≥1): N‑tes Segment **ab Root** (1‑basiert). Außerhalb der Tiefe → leer.
- `%rootNB%` / `%folderNB%`: wie oben, nur **erster Buchstabe** (Uppercase). Außerhalb der Tiefe → leer.
- `%datum%`: Dateizeitstempel kompakt `YYYYMMDD` (Quelle siehe 5.7).
- `%date%`: Dateizeitstempel ISO `YYYY-MM-DD`.
- `%wert%`: alter Dateiname **ohne** Erweiterung (nur sinnvoll, wenn der alte Name als Teil ins Ziel übernommen werden soll).
- `%N%`: letzte Ziffernfolge aus **aktuellem Ordnernamen**; wiederholte `%N%`-Sequenzen (z. B. `%N%%N%`) → **Zero-Padding** auf die Anzahl der Sequenzen; kein Ziffernanteil vorhanden → entsprechend viele Nullen.

### 4.4 Nummerierung
- Läuft **pro Ordner und pro Dateiendung** (z. B. `.pdf` separat von `.docx`).
- Start bei `01` (oder `001` … gemäß `numbering_width`).
- Form: `<prefix>-<laufendeNummer><ext>`; Bindestrich wird automatisch gesetzt, wenn das Präfix **nicht** bereits mit `- _ .` oder Leerzeichen endet.

### 4.5 Optionen
- `numbering_width`: Breite der laufenden Nummer (Default `2`).
- `use_birthtime`: Versuche Erstellungszeit zu verwenden (OS-abhängig); sonst `mtime` (Änderungszeit).  
- `dry_run_note_limit`: Begrenzung der Dry-Run-Ausgaben (nur Konsolenanzeige, keine Funktionalitätseinbuße).

### 4.6 Excludes
- `folders`: Ordnernamen (exakt) werden **rekursiv** übersprungen (Pruning bei `os.walk`).
- `filetypes`: zu ignorierende Endungen (case-insensitive, mit/ohne Punkt erlaubt; intern normalisiert auf `.ext`).
- `filenames`: exakte Basenamen (z. B. `Thumbs.db`).
- **Toleranz**: Zusätzlich akzeptiert die Konfiguration alternative Schlüssel (`exclude_datatyp`, `exclude_data`) – sie werden auf `filetypes` bzw. `filenames` gemappt.

---

## 5. Funktionsweise im Detail

### 5.1 Traversierung
- `os.walk(root, topdown=True)`; Verzeichnisliste `dirs` wird in-place gefiltert (Excludes) → **keine** Abstieg in ausgeschlossene Ordner.
- Für jeden Ordner `curr` wird die relative Tiefe als Anzahl Segmente in `curr.relative_to(root)` bestimmt → **Ebene `depth`**.

### 5.2 Ebenen-Mapping
- Aktives Pattern: `patterns.get(depth, "")`.
- **Kein Pattern → Ordner wird übersprungen** (Dateien in dieser Ebene bleiben unverändert).

### 5.3 Dateifilter dieser Ebene
- Entferne Einträge, die
  - in `filenames` stehen,
  - deren Endung in `filetypes` steht.
- Übrig bleiben die **kandidaten** für Umbenennung.

### 5.4 Gruppierung & Sortierung
- Gruppiere Kandidaten nach **Dateiendung** (lowercased).
- Sortiere jede Gruppe **natürlich** (ziffernbewusst), damit Zählung reproduzierbar ist.

### 5.5 Präfix-Rendering (Platzhalter)
- Kontextparameter: `base_root = root.name`, `parent_parts = rel_parts(root, curr)` (Liste der Segmente), `stem = dateiname_ohne_ext`, `time = creation_date(file)`.
- Schritte:
  1) `%N%`-Sequenzen ersetzen (Breite = Anzahl Wiederholungen, Quelle = letzte Ziffernfolge des aktuellen Ordnernamens, sonst Nullen).  
  2) `%rootNB%`/`%folderNB%` durch ersten Buchstaben des jeweiligen Segments ersetzen.  
  3) `%rootN%`/`%folderN%` durch N‑tes Segment einsetzen.  
  4) `%root%`/`%folder%` → `base_root`.  
  5) `%datum%`/`%date%` einsetzen.  
  6) `%wert%` ggf. durch `stem` ersetzen.
  7) Umgebende Quotes/Backticks tolerant entfernen.

### 5.6 Zielname & Separator
- Wenn Präfix **nicht** leer und **nicht** auf `- _ .` oder Leerzeichen endet → automatischer `-` als Separator vor der Nummer.
- Zielbasis: `<prefix><sep><counter:0{width}d><ext>`.

### 5.7 Zeitquelle (`%datum%`/`%date%`)
- Wenn `use_birthtime = true` und OS liefert `st_birthtime` → Erstellungszeit.
- Sonst: `st_mtime` (letzte Inhaltsänderung).  
- Formate: `YYYYMMDD` und `YYYY-MM-DD`.

### 5.8 Eindeutigkeit & Kollisionen
- **Set `existing_now`**: bekannte Namen im Ordner (nur betrachtete Dateien) + verbotene Basenamen.
- **Reservierung**: geplanter Name wird in `reserved_targets` gesperrt.  
- **Kollisionen**: Falls Ziel bereits existiert/reserviert → Suffix `_2`, `_3`, … **vor** der Erweiterung (z. B. `prefix-01_2.pdf`).

### 5.9 Zweiphasige Umbenennung
- Phase 1: `src → __obis_tmp__{src.name}__{pid}__` (gleicher Ordner).
- Phase 2: `tmp → dst`.  
- Verhindert Zyklen/Kollisionen während eines Ordnerlaufs.

### 5.10 Dry-Run
- Statt Umbenennen werden Zeilen `"[DRY] <relpath> -> <ziel>"` ausgegeben.  
- Limit der Ausgabe über `dry_run_note_limit`.

### 5.11 Zusammenfassung/Exit
- Nicht-Dry: Ausgabe `Fertig. Umbenannte Dateien: <n>`.  
- Dry: `Trockenlauf abgeschlossen.`

---

## 6. Beispiele und Anwendungsfälle

### 6.1 Einfache Kursstruktur (Ebene 1)
**INI**
```ini
[patterns]
level1 = %root1%
[options]
numbering_width = 2
```
**Pfad**
```
SE1/
└─ BBWL01/
   ├─ alt1.pdf
   └─ alt2.docx
```
**Ergebnis**
```
BBWL01-01.pdf
BBWL01-01.docx
```
(Hinweis: Nummerierung separat pro Endung.)

### 6.2 Kombiniertes Präfix (Ebene 3)
**INI**
```ini
[patterns]
level3 = %root2%-%root3%
```
**Pfad**
```
SE1/BBWL01/Skript/
   ├─ Folien.pptx
   └─ Notizen.txt
```
**Ergebnis**
```
Skript-Lektion1-01.pptx
Skript-Lektion1-01.txt
```

### 6.3 Datum + Kurs (Ebene 1/2)
**INI**
```ini
[patterns]
level1 = %date%-%root1%
level2 = %datum%_%root2%
[options]
use_birthtime = true
```
**Resultat (Beispiel)**
```
2025-09-08-BBWL01-01.pdf
20250908_Skript-01.docx
```

### 6.4 `%N%` aus Ordnername
**INI**
```ini
[patterns]
level3 = L%N%_%root3%
```
**Pfad**: `.../Skript/Lektion3/` → `%N% = 3`, `%N%%N% = 03`  
**Ergebnis**: `L3_Lektion3-01.pdf`

### 6.5 Anfangsbuchstaben (`%rootNB%`)
**INI**
```ini
[patterns]
level4 = %root1%%root2B%%root3B%  ; z. B. BBWL01SL
```
**Ergebnis**
```
BBWL01SL-01.png
```

### 6.6 Excludes
**INI**
```ini
[excludes]
folders = .git, .venv, node_modules, .obsidian
filetypes = .md, .ini
filenames = Thumbs.db, .DS_Store
```
Ausschlüsse gelten rekursiv für Ordner, global für Dateitypen/Namen.

### 6.7 Ebene 0 (optional)
**INI**
```ini
[patterns]
level0 = %root%   ; Dateien direkt im Root umbenennen
```
**Hinweis**: Standardmäßig nicht gesetzt; explizit hinzufügen falls benötigt.

---

## 7. Erweiterte Features

### 7.1 Zero-Padding via `%N%`
- Sequenzen von `%N%` bestimmen die **Mindestbreite**.  
- Beispiele: `Ordner „Lektion3"` → `%N% → 3`, `%N%%N% → 03`, `%N%%N%%N% → 003`.  
- Keine Ziffern im Ordnernamen → `0`, `00`, `000` …

### 7.2 Natürliches Sortieren vor Nummerierung
- Dateien werden ziffernbewusst sortiert (`A2 < A10`), sodass die resultierende Reihenfolge stabil und erwartbar ist.

### 7.3 Eindeutigkeitsgarantien
- `ensure_unique()` vermeidet Zusammenstöße im Zielordner durch `_2`, `_3`, … direkt **vor** der Endung.

### 7.4 Temporäre Namen hart gegen Kollisionen
- Temporärschema: `__obis_tmp__{altname}__{pid}__`.  
- Falls temporäre Reste existieren (z. B. nach Abbruch), manuell löschen.

### 7.5 Tolerante INI-Parsing-Details
- Listen können durch **Komma** oder **Zeilenumbrüche** getrennt sein, Quotes sind erlaubt; Normalisierung entfernt unnötige Zeichen.
- Alternativschlüssel (`exclude_datatyp`, `exclude_data`) werden gemappt.

### 7.6 Dry-Run-Output begrenzen
- `dry_run_note_limit` verhindert überlange Konsolenlogs in großen Bäumen.  
- Bei Überschreitung: Ausgabe wird gekürzt, Funktionalität unverändert.

### 7.7 Erweiterbarkeit
- Weitere Platzhalter sind zentral im Präfix-Renderer einfügbar.  
- Zusätzlich denkbar: **Benutzerdefinierte Funktionen** via Callbacks (nicht im Basisskript enthalten).

> Hinweis: Manche früheren Dokumente erwähnen einen **DB/Markdown-Generator** (automatische `Data-*.md`). Diese Funktion ist **nicht** Teil des Basisskripts dieses Guides. Sie kann als **separates Modul** implementiert werden (siehe 9.7 Hinweis).

---

## 8. Troubleshooting

### 8.1 „Root nicht gefunden“
- **Ursache**: `--root` zeigt auf nicht existierenden Pfad.  
- **Lösung**: Pfad prüfen; absolute/relative Angabe korrekt?

### 8.2 „INI nicht gefunden“
- **Ursache**: `--config` verweist auf nicht existente Datei.  
- **Lösung**: Datei anlegen/korrigieren; Standardname `ObisRenamer.ini` im Root verwenden.

### 8.3 „Temporärer Name existiert bereits“
- **Ursache**: Reste von abgebrochenem Lauf.  
- **Lösung**: Temporäre Dateien `__obis_tmp__*` im betroffenen Ordner löschen, erneut starten.

### 8.4 „Ziel existiert bereits“
- **Ursache**: Kollision mit existierendem Namen außerhalb der Renamer-Planung.  
- **Lösung**: Manuell prüfen; Skript fügt `_2`, `_3` an, sollte aber im Normalfall **keinen** Konflikt im zweiten Schritt erzeugen.

### 8.5 „Keine Ausgabe im Dry-Run“
- **Ursache**: Kein passendes `levelN`-Pattern für die aktuelle Tiefe, oder alle Dateien durch Excludes gefiltert.  
- **Lösung**: Tiefe prüfen (`tree -d`), `levelN` ergänzen, Excludes justieren.

### 8.6 Falsches Datum
- **Ursache**: OS liefert keine Erstellzeit (`birthtime`), Fallback `mtime`.  
- **Lösung**: `use_birthtime = true` testen (falls OS unterstützt) oder Datumslogik im Pattern anpassen.

### 8.7 Unerwartete Präfixe (leere Segmente)
- **Ursache**: `%rootN%` außerhalb der vorhandenen Tiefe.  
- **Lösung**: Fallback ist leer; Pattern so wählen, dass leere Segmente keine Artefakte erzeugen (z. B. abschließende Trennzeichen vermeiden).

### 8.8 Rechte/Lock-Probleme
- **Symptom**: Umbenennen schlägt sporadisch fehl (Windows: Datei geöffnet).  
- **Lösung**: Alle Viewer/Editoren schließen; mit Adminrechten versuchen.

### 8.9 Zu viele Dry-Run-Zeilen
- **Lösung**: `dry_run_note_limit` erhöhen oder Teilbäume separat testen.

### 8.10 Encoding/Unicode
- **Hinweis**: Skript verwendet UTF‑8; exotische FS-Codierungen können dennoch Probleme machen.  
- **Lösung**: Locale/Terminal auf UTF‑8 konfigurieren.

---

## 9. Best Practices

### 9.1 Sicherer Workflow
1) **Backup/Commit** vor jedem Lauf.  
2) **Dry-Run** auf Teilbaum.  
3) **Review** der Vorschläge.  
4) **Vollständige Ausführung**.  
5) **Diff/Abnahme** (z. B. mit Git).

### 9.2 Musterdesign
- Präfixe **kurz, aussagekräftig**; semantische Reihenfolge: Kontext → Unterkontext → Datum → Nummer.  
- Keine überflüssigen Trennzeichen am Ende (automatischer `-` folgt nur wenn nötig).

### 9.3 Platzhalter gezielt
- `%rootN%` für **stabile** Hierarchie (vom Root abwärts).  
- `%N%` wenn die **Ordnernummer** (z. B. „Lektion7“) semantisch relevant ist.  
- `%wert%` nur einsetzen, wenn Altname informativ ist (sonst deterministisch bleiben).

### 9.4 Excludes pflegen
- Häufige Störer (`.git`, `.venv`, `node_modules`, `.obsidian`) immer ausnehmen.  
- Dateitypen wie `.md`, `.ini` vermeiden, wenn sie **nicht** umbenannt werden sollen.

### 9.5 Nummerierungsbreite planen
- Kleine Sammlungen: `2` (01–99).  
- Große Sammlungen: `3` oder `4` (001–9999).  
- Einheitlich je Projekt halten.

### 9.6 Dokumentation
- INI mit Kommentaren versehen (Wozu dient welches Pattern?).  
- Beispiele in der Repo-README pflegen (Vorher/Nachher).

### 9.7 DB/Markdown-Generator als Add-On
- Wenn gewünscht, kann ein **separates Skript/Modul** Data‑Dateien (`Data-*.md`) erzeugen, die Obsidian‑Links zu umbenannten Dateien enthalten.  
- Empfehlung: Ausführung **nach** dem Renamer, basierend auf aktuellem Zustand; eigene INI‑Sektion `[DB]` definieren.  
- Vorteil der Trennung: Renamer bleibt **einfach/robust**; DB‑Generator kann unabhängig iterieren.

### 9.8 Qualitätssicherung
- Stichproben auf jeder Ebene durchführen.  
- Sonderzeichen/Leerzeichen in Originalnamen prüfen; nach Run sollten Namen maschinenfreundlich sein.

### 9.9 Performance
- Große Bäume in **Teilbatches** (Unterwurzeln) mit eigenem Run bearbeiten.  
- Excludes früh und großzügig setzen.

### 9.10 Rollback-Strategie
- Git: Branch/Tag vor Run; andernfalls Backup-Verzeichnis.  
- Manuell rückgängig: anhand Dry-Run-Log und vorheriger Namensliste (z. B. via `find -type f > before.txt`).

---

## 10. FAQ

**F1:** Werden Dateien im Root (Tiefe 0) umbenannt?  
**A:** Nur wenn `level0` definiert ist. Standardmäßig beginnen Muster bei `level1`.

**F2:** Warum startet die Nummerierung pro Endung neu?  
**A:** Um heterogene Sammlungen sauber zu trennen (z. B. `01.pdf` und `01.docx` jeweils unabhängig). Das verbessert Sortierbarkeit und Erwartbarkeit.

**F3:** Was passiert bei Kollisionen?  
**A:** Der Algorithmus vergibt `_2`, `_3`, … vor der Endung, bis ein freier Name gefunden ist.

**F4:** Wie werden `%N%`-Breiten bestimmt?  
**A:** Durch die Anzahl der direkt aneinandergereihten `%N%`-Platzhalter: `%N%%N%` → Breite 2 (`03`).

**F5:** Was ist, wenn `%rootN%` außerhalb der Tiefe liegt?  
**A:** Es wird ein leerer String eingesetzt. Plane Patterns so, dass daraus keine störenden Doppelseparatoren entstehen.

**F6:** Warum weicht `%date%` manchmal von `ls -l` ab?  
**A:** Unterschiedliche Zeitquelle: `birthtime` (wenn verfügbar) vs. `mtime`. Steuerbar per `use_birthtime`.

**F7:** Kann ich Sonderzeichen erzwingen (z. B. Unterstriche statt Bindestrich)?  
**A:** Ja, schreibe sie **ins Pattern**: endet das Präfix auf `_`, wird **kein** zusätzlicher `-` eingefügt.

**F8:** Ist die Reihenfolge der Verarbeitung deterministisch?  
**A:** Ja, durch natürliche Sortierung innerhalb jeder Endungsgruppe.

**F9:** Warum sehe ich keine Änderungen im Dry-Run?  
**A:** Entweder greifen Excludes oder es existiert kein Pattern für die Ebene (`levelN`). Prüfe beides.

**F10:** Unterstützt das Skript parallele Verarbeitung?  
**A:** Nein (bewusst I/O-einfach gehalten). Vorteil: weniger Komplexität und geringeres Kollisionsrisiko.

---

### Anhang A – Muster-Bibliothek (Snippet-Sammlung)
```ini
# Kurs / Kapitel / Lektion mit Nummer aus Ordnernamen
[patterns]
level1 = %root1%
level2 = %root1%-%root2%
level3 = %root1%-%root2%-L%N%

# Fotoarchiv nach Datum
[patterns]
level1 = %date%_%root1%
[options]
numbering_width = 3
use_birthtime = true

# Kurzpräfixe über Initialen
[patterns]
level3 = %root1%%root2B%%root3B%

# Ebene 0 (Root-Dateien) explizit aufnehmen
[patterns]
level0 = %root%
```

### Anhang B – Prüfliste vor dem Run
- [ ] Backup/Commit vorhanden  
- [ ] Excludes vollständig  
- [ ] Level-Patterns definiert  
- [ ] Dry-Run ausgeführt  
- [ ] Stichproben validiert  
- [ ] Nummerierungsbreite plausibel  
- [ ] OS-Zeitquelle akzeptabel

### Anhang C – CLI-Referenz (kompakt)
```text
--root PATH     Start-Root (Default: cwd)
--config PATH   INI-Datei (Default: ObisRenamer.ini)
--dry           Trockenlauf (nur anzeigen)
```

### Anhang D – Entscheidungslogik (Kurzform)
1) Ordner durchlaufen; Excludes anwenden.  
2) Ebene bestimmen → `levelN` suchen.  
3) Dateien filtern (Endungen/Namen).  
4) Gruppieren nach Endung, natürlich sortieren.  
5) Präfix rendern (Platzhalter).  
6) Zielnamen bilden; Eindeutigkeit sichern.  
7) Zweiphasig umbenennen (oder Dry-Run melden).  
8) Zusammenfassen.

