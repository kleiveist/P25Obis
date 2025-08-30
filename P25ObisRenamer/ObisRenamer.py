#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ObisRenamer – rekursives Dateiumbenennen nach INI-Vorlagen.
- Muster/Präfix je Tiefe (level1, level2, …) aus INI ([patterns]).
- Platzhalter (für [patterns] *und* [DB]):
    %root% / %folder%        : Name des Start-Roots
    %rootN% / %folderN%      : N-tes Ordnersegment ab Root (1-basiert)
    %rootNB% / %folderNB%    : wie oben, aber nur der erste Buchstabe (upper)
    %datum% / %date%         : YYYYMMDD / YYYY-MM-DD (bei [patterns] aus Datei, bei [DB] = aktuelles Datum)
    %wert%                   : alter Dateiname (ohne Endung) – nur in [patterns] sinnvoll
    %N%                      : Ziffernfolge aus *aktuellem Ordnernamen* (z.B. „Lektion3“ -> „3“).
                               Mehrfach (%N%%N% …) = Null-Auffüllung auf die Anzahl der Platzhalter (z.B. „03“).
                               Wenn keine Ziffern vorhanden: entsprechend viele Nullen.
- Nummerierung pro Ordner *und* Dateiendung neu (01, 02, …), Breite konfigurierbar.
- Excludes: komplette Ordner (rekursiv), Dateitypen (Endungen), Einzeldateien (Basename).
- Pro Ordner mit Umbenennungen kann eine Markdown-Dokumentation geschrieben werden:
  * Klassisch: fester Dateiname (options.data_name_filename)
  * Template-Modus ([DB]): pro Ebene eigener Name via level1/2/…
    → Umschaltbar über options.data_name_template = true/false
"""

from __future__ import annotations
import argparse
import configparser
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Iterable

# ------------------------- Hilfsfunktionen -------------------------

def normalize_list(v: str) -> List[str]:
    """Zerlegt Komma/Zeilen-getrennte Listen, trimmt, entfernt Quotes/Backticks."""
    if not v:
        return []
    items = []
    for line in v.splitlines():
        for part in line.split(","):
            s = part.strip().strip('`"\'')
            if s:
                items.append(s)
    return items

def parse_bool(val: str, *, default: bool=False) -> bool:
    if val is None:
        return default
    s = str(val).strip().lower()
    # tolerant: 'ture' wird wie 'true' interpretiert
    return s in {"1","true","ture","yes","y","on","ja","wahr"}

def load_config(path: Path) -> dict:
    cp = configparser.ConfigParser(interpolation=None, strict=False)
    with path.open("r", encoding="utf-8") as f:
        cp.read_file(f)

    # Patterns: level1, level2, ...
    patterns: Dict[int, str] = {}
    if cp.has_section("patterns"):
        for key, val in cp.items("patterns"):
            m = re.fullmatch(r"level(\d+)", key.strip(), flags=re.IGNORECASE)
            if m:
                lvl = int(m.group(1))
                patterns[lvl] = val.strip().strip(' \t`"\'')

    # DB-Dateinamen-Templates (optional)
    db_templates: Dict[int, str] = {}
    if cp.has_section("DB"):
        for key, val in cp.items("DB"):
            m = re.fullmatch(r"level(\d+)", key.strip(), flags=re.IGNORECASE)
            if m:
                lvl = int(m.group(1))
                db_templates[lvl] = val.strip().strip(' \t`"\'')

    # Optionen
    opt = dict(
        numbering_width = 2,
        data_name_filename = "Data-Name der Umbenennung.md",
        data_name_template = False,   # Schalter für [DB]-Modus
        use_birthtime = False,
        dry_run_note_limit = 2000,  # Schutz gegen zu große Konsolenlogs
    )
    if cp.has_section("options"):
        if cp.has_option("options", "numbering_width"):
            try:
                opt["numbering_width"] = int(cp.get("options", "numbering_width"))
            except ValueError:
                pass
        if cp.has_option("options", "data_name_filename"):
            opt["data_name_filename"] = cp.get("options", "data_name_filename").strip().strip('`"\'')
        if cp.has_option("options", "use_birthtime"):
            opt["use_birthtime"] = cp.getboolean("options", "use_birthtime", fallback=False)
        if cp.has_option("options", "data_name_template"):
            opt["data_name_template"] = parse_bool(cp.get("options", "data_name_template"), default=False)

    # Excludes
    excludes = dict(folders=[], filetypes=[], filenames=[])
    if cp.has_section("excludes"):
        excludes["folders"]   = normalize_list(cp.get("excludes", "folders", fallback=""))
        # Akzeptiere auch die vom Nutzer gewünschte Schreibweise 'exclude_datatyp'
        raw_ft = cp.get("excludes", "filetypes", fallback=cp.get("excludes", "exclude_datatyp", fallback=""))
        excludes["filetypes"] = [s.lower() if s.startswith(".") else f".{s.lower()}" for s in normalize_list(raw_ft)]
        excludes["filenames"] = normalize_list(cp.get("excludes", "filenames", fallback=cp.get("excludes", "exclude_data", fallback="")))

    return {"patterns": patterns, "db_templates": db_templates, "options": opt, "excludes": excludes}

def creation_date(path: Path, use_birthtime: bool) -> float:
    """Liefert bevorzugt 'Erstellzeitpunkt' (wenn OS unterstützt), sonst mtime."""
    try:
        if use_birthtime and hasattr(os.stat_result, "st_birthtime"):
            st = path.stat()
            if getattr(st, "st_birthtime", None):
                return st.st_birthtime
    except Exception:
        pass
    # Fallback: mtime
    return path.stat().st_mtime

def format_date(ts: float) -> Tuple[str, str]:
    t = time.localtime(ts)
    return time.strftime("%Y%m%d", t), time.strftime("%Y-%m-%d", t)  # (%datum%, %date%)

def today_strings() -> Tuple[str, str]:
    t = time.localtime()
    return time.strftime("%Y%m%d", t), time.strftime("%Y-%m-%d", t)

def rel_parts(root: Path, p: Path) -> List[str]:
    rel = p.relative_to(root)
    if rel == Path("."):
        return []
    return [part for part in rel.parts]

def _first_letter(s: str) -> str:
    return (s[0].upper() if s else "")

def _extract_last_number(s: str) -> str:
    m = re.search(r"(\d+)(?!.*\d)", s)
    return m.group(1) if m else ""

def _replace_N_sequences(text: str, curr_dirname: str) -> str:
    digits = _extract_last_number(curr_dirname)
    pat = re.compile(r"(?:%N%)+", flags=re.IGNORECASE)
    def repl(m: re.Match) -> str:
        width = len(m.group(0)) // 3  # '%N%' Länge 3
        val = digits if digits else "0"
        return val.zfill(width)
    return pat.sub(repl, text)

def _expand_common_placeholders(pattern: str, *, base_root: str, parent_parts: List[str], dt_compact: str, dt_iso: str, stem: str|None, curr_dirname: str) -> str:
    # Vorbehandlung: %N% Blöcke
    pat = _replace_N_sequences(pattern, curr_dirname)

    # %rootNB% / %folderNB%
    def repl_B(m: re.Match) -> str:
        idx = int(m.group(2)) - 1
        seg = parent_parts[idx] if 0 <= idx < len(parent_parts) else ""
        return _first_letter(seg)
    pat = re.sub(r"%(root|folder)(\d+)B%", repl_B, pat, flags=re.IGNORECASE)

    # %rootN% / %folderN%
    def repl_N(m: re.Match) -> str:
        idx = int(m.group(2)) - 1
        return parent_parts[idx] if 0 <= idx < len(parent_parts) else ""
    pat = re.sub(r"%(root|folder)(\d+)%", repl_N, pat, flags=re.IGNORECASE)

    # %root% / %folder%
    pat = re.sub(r"%(root|folder)%", base_root, pat, flags=re.IGNORECASE)

    # %datum% / %date%
    pat = re.sub(r"%datum%", dt_compact, pat, flags=re.IGNORECASE)
    pat = re.sub(r"%date%", dt_iso, pat, flags=re.IGNORECASE)

    # %wert% (falls vorhanden)
    if stem is not None:
        pat = re.sub(r"%wert%", stem, pat, flags=re.IGNORECASE)

    # Strip umgebende Quotes/Backticks tolerant
    return pat.strip().strip('`"\'')

def render_pattern_prefix(pattern: str, file_path: Path, root: Path, parent_parts: List[str], use_birthtime: bool) -> str:
    """Platzhalterersetzung für [patterns] (Datei-Umbenennung)."""
    base_root = root.name
    stem = file_path.stem
    dt_compact, dt_iso = format_date(creation_date(file_path, use_birthtime))
    curr_dirname = parent_parts[-1] if parent_parts else base_root
    return _expand_common_placeholders(pattern, base_root=base_root, parent_parts=parent_parts, dt_compact=dt_compact, dt_iso=dt_iso, stem=stem, curr_dirname=curr_dirname)

def render_db_filename(pattern: str, root: Path, parent_parts: List[str]) -> str:
    """Platzhalterersetzung für [DB] (Dokumentationsdatei)."""
    base_root = root.name
    dt_compact, dt_iso = today_strings()  # aktuelles Datum
    curr_dirname = parent_parts[-1] if parent_parts else base_root
    # In [DB] ist %wert% unlogisch -> None
    name = _expand_common_placeholders(pattern, base_root=base_root, parent_parts=parent_parts, dt_compact=dt_compact, dt_iso=dt_iso, stem=None, curr_dirname=curr_dirname)
    return name

def natural_key(s: str) -> List:
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

def ensure_unique(target_name: str, reserved: set, existing: set) -> str:
    """Erzwingt eindeutigen Dateinamen im Ordner (ohne Pfad). Falls Kollision, hänge _2, _3, ... vor der Endung an."""
    if target_name not in reserved and target_name not in existing:
        reserved.add(target_name)
        return target_name
    stem, ext = os.path.splitext(target_name)
    i = 2
    while True:
        cand = f"{stem}_{i}{ext}"
        if cand not in reserved and cand not in existing:
            reserved.add(cand)
            return cand
        i += 1

def two_phase_rename(renames: List[Tuple[Path, Path]]) -> None:
    """Kollision-sicheres Umbenennen: Quelle -> tmp -> Ziel (nur innerhalb desselben Ordners)."""
    tmps: List[Tuple[Path, Path]] = []
    for src, dst in renames:
        if src == dst:
            continue
        tmp = src.with_name(f"__obis_tmp__{src.name}__{os.getpid()}__")
        if tmp.exists():
            raise RuntimeError(f"Temporärer Name existiert bereits: {tmp}")
        src.rename(tmp)
        tmps.append((tmp, dst))
    for tmp, dst in tmps:
        if dst.exists():
            raise FileExistsError(f"Ziel existiert bereits: {dst}")
        tmp.rename(dst)

# ------------------------- Hauptlogik -------------------------

def should_skip_dir(dir_name: str, exclude_dirs: List[str]) -> bool:
    return dir_name in exclude_dirs

def run(root: Path, cfg: dict, dry_run: bool) -> int:
    patterns: Dict[int, str] = cfg["patterns"]
    db_templates: Dict[int, str] = cfg.get("db_templates", {})
    opts = cfg["options"]
    excl = cfg["excludes"]

    numbering_width = int(opts.get("numbering_width", 2))
    fixed_data_md_name = opts.get("data_name_filename", "Data-Name der Umbenennung.md")
    use_birthtime = bool(opts.get("use_birthtime", False))
    use_db_templates = bool(opts.get("data_name_template", False))

    exclude_dirs = set(excl.get("folders", []))
    exclude_exts = set(excl.get("filetypes", []))          # mit führendem Punkt, lower()
    base_exclude_names = set(excl.get("filenames", []))
    # Altes Standard-Notizfile nie umbenennen (falls vorhanden)
    base_exclude_names.add(fixed_data_md_name)

    total_renamed = 0
    printed = 0
    note_limit = int(opts.get("dry_run_note_limit", 2000))

    for curr_dir, dirs, files in os.walk(root, topdown=True):
        # Ordner-Ausschlüsse: pruning
        dirs[:] = [d for d in dirs if not should_skip_dir(d, list(exclude_dirs))]

        curr = Path(curr_dir)
        parent_rel = rel_parts(root, curr)
        depth = len(parent_rel)  # Dateien in curr liegen auf dieser Ebene

        # Muster für diese Ebene?
        pattern = patterns.get(depth, "").strip()
        if not pattern:
            continue  # Ebene ignorieren

        # Optionalen DB-Dateinamen im Voraus bestimmen und lokal von Umbenennungen ausschließen
        doc_name = None
        if use_db_templates:
            tmpl = db_templates.get(depth, "").strip()
            if tmpl:
                doc_name = render_db_filename(tmpl, root, parent_rel)
                # Keine zusätzliche Formatierung erzwingen; .md wird vom Benutzer vorgegeben
        # Lokale Excludes inkl. der ggf. vorhandenen Ziel-Notiz
        exclude_names = set(base_exclude_names)
        if doc_name:
            exclude_names.add(doc_name)

        # Dateien filtern
        entries = []
        for name in files:
            if name in exclude_names:
                continue
            ext = Path(name).suffix.lower()
            if ext in exclude_exts:
                continue
            entries.append(name)

        if not entries:
            continue

        # Gruppierung nach Dateiendung (lokale Zählung)
        by_ext: Dict[str, List[str]] = {}
        for name in entries:
            by_ext.setdefault(Path(name).suffix.lower(), []).append(name)
        for ext in by_ext:
            by_ext[ext].sort(key=natural_key)

        # Existierende Namen im Ordner (für Kollisionsprüfung)
        existing_now = set(entries) | exclude_names  # nur betrachtete Dateien

        renames: List[Tuple[Path, Path]] = []
        reserved_targets: set = set()

        for ext, names in by_ext.items():
            counter = 1
            for old_name in names:
                src = curr / old_name
                prefix = render_pattern_prefix(pattern, src, root, parent_rel, use_birthtime)

                # Separator-Logik: wenn Präfix nicht leer und nicht bereits mit [-_. ] endet -> "-"
                sep = ""
                if prefix and not re.search(r"[-_. ]$", prefix):
                    sep = "-"

                target_basename = f"{prefix}{sep}{counter:0{numbering_width}d}{ext}"
                # Kollisionen vermeiden
                target_basename = ensure_unique(target_basename, reserved_targets, existing_now)
                dst = curr / target_basename
                if src.name != dst.name:
                    renames.append((src, dst))
                counter += 1

        if not renames:
            continue

        # Anwenden
        if dry_run:
            for src, dst in renames:
                line = f"[DRY] {src.relative_to(root)}  ->  {dst.name}"
                print(line)
                printed += 1
                if printed >= note_limit:
                    print("… (gekürzt)")
                    break
        else:
            two_phase_rename(renames)
            total_renamed += len(renames)

            # Markdown-Notiz schreiben (nur dieser Ordner), wenn eingeschaltet
            if use_db_templates:
                # Falls kein Template für diese Ebene gesetzt war, auf festen Namen zurückfallen
                note_filename = doc_name if doc_name else fixed_data_md_name
                files_after = sorted(
                    [p.name for p in curr.iterdir() if p.is_file() and p.name != note_filename],
                    key=natural_key,
                )
                content = "# Umbenannte Dateien in diesem Verzeichnis\n\n" + "\n".join(f"![[{n}]]" for n in files_after)
                (curr / note_filename).write_text(content + ("\n" if content else ""), encoding="utf-8")

    if dry_run:
        return 0
    return total_renamed

# ------------------------- CLI -------------------------

def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description="ObisRenamer – Umbenennen nach INI-Vorlagen")
    ap.add_argument("--root", type=Path, default=Path.cwd(), help="Start-Root (Standard: aktuelles Verzeichnis)")
    ap.add_argument("--config", type=Path, default=Path("ObisRenamer.ini"), help="INI-Datei (Standard: ObisRenamer.ini)")
    ap.add_argument("--dry", action="store_true", help="Nur anzeigen, nichts umbenennen")
    args = ap.parse_args(argv)

    root = args.root.resolve()
    if not root.exists():
        print(f"Root nicht gefunden: {root}", file=sys.stderr)
        return 2

    ini_path = args.config.resolve()
    if not ini_path.exists():
        print(f"INI nicht gefunden: {ini_path}", file=sys.stderr)
        return 2

    cfg = load_config(ini_path)
    try:
        changed = run(root, cfg, dry_run=args.dry)
        if args.dry:
            print("Trockenlauf abgeschlossen.")
        else:
            print(f"Fertig. Umbenannte Dateien: {changed}")
        return 0
    except Exception as e:
        print(f"Fehler: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
