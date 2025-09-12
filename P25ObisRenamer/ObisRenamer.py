#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ObisRenamer – rekursives Dateiumbenennen nach INI-Vorlagen.
Platzhalter-/Ebenen-Rendering via placeholders.py (expand()).

- Patterns je Tiefe (levelN) aus [patterns] der INI.
- Platzhalter: %rootN%, %rootN()%, %rootNB%, %root%, %root()%, %folder..., %N%, %date%, %datum%, %wert%.
- Nummerierung pro Ordner + Dateiendung (01, 02, …), Breite konfigurierbar.
- Excludes: Ordner (rekursiv), Dateiendungen, exakte Basenames.
"""

from __future__ import annotations
import argparse
import configparser
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import placeholders  # erwartet placeholders.py im Suchpfad (gleicher Ordner oder PYTHONPATH)


# ------------------------- Hilfsfunktionen -------------------------

def normalize_list(v: str) -> List[str]:
    if not v:
        return []
    items: List[str] = []
    for line in v.splitlines():
        for part in line.split(","):
            s = part.strip().strip('`"\'')
            if s:
                items.append(s)
    return items

def load_config(path: Path) -> dict:
    cp = configparser.ConfigParser(interpolation=None, strict=False)
    with path.open("r", encoding="utf-8") as f:
        cp.read_file(f)

    # Patterns aus INI laden
    patterns: Dict[int, str] = {}
    if cp.has_section("patterns"):
        for key, val in cp.items("patterns"):
            m = re.fullmatch(r"level(\d+)", key.strip(), flags=re.IGNORECASE)
            if not m:
                continue
            lvl = int(m.group(1))
            patterns[lvl] = val.strip().strip('`"\'')  # tolerant Quotes entfernen

    # Optionen
    opt = dict(
        numbering_width=2,
        use_birthtime=False,
        dry_run_note_limit=2000,
    )
    if cp.has_section("options"):
        if cp.has_option("options", "numbering_width"):
            try:
                opt["numbering_width"] = int(cp.get("options", "numbering_width"))
            except ValueError:
                pass
        if cp.has_option("options", "use_birthtime"):
            opt["use_birthtime"] = cp.getboolean("options", "use_birthtime", fallback=False)
        if cp.has_option("options", "dry_run_note_limit"):
            try:
                opt["dry_run_note_limit"] = int(cp.get("options", "dry_run_note_limit"))
            except ValueError:
                pass

    # Excludes
    excludes = dict(folders=[], filetypes=[], filenames=[])
    if cp.has_section("excludes"):
        excludes["folders"] = normalize_list(cp.get("excludes", "folders", fallback=""))
        raw_ft = cp.get(
            "excludes",
            "filetypes",
            fallback=cp.get("excludes", "exclude_datatyp", fallback="")
        )
        excludes["filetypes"] = [
            s.lower() if s.startswith(".") else f".{s.lower()}"
            for s in normalize_list(raw_ft)
        ]
        excludes["filenames"] = normalize_list(
            cp.get("excludes", "filenames", fallback=cp.get("excludes", "exclude_data", fallback=""))
        )

    return {"patterns": patterns, "options": opt, "excludes": excludes}

def rel_parts(root: Path, p: Path) -> List[str]:
    rel = p.relative_to(root)
    return [] if str(rel) == "." else list(rel.parts)

def natural_key(s: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

def ensure_unique(target_name: str, reserved: set, existing: set) -> str:
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
    opts = cfg["options"]
    excl = cfg["excludes"]

    numbering_width = int(opts.get("numbering_width", 2))

    exclude_dirs = set(excl.get("folders", []))
    exclude_exts = set(excl.get("filetypes", []))          # .ext in lower()
    base_exclude_names = set(excl.get("filenames", []))

    total_renamed = 0
    printed = 0
    note_limit = int(opts.get("dry_run_note_limit", 2000))

    for curr_dir, dirs, files in os.walk(root, topdown=True):
        # Ordner-Ausschlüsse
        dirs[:] = [d for d in dirs if not should_skip_dir(d, list(exclude_dirs))]

        curr = Path(curr_dir)
        depth = len(rel_parts(root, curr))
        pattern = patterns.get(depth, "").strip()
        if not pattern:
            continue  # Ebene ignorieren

        # Dateien filtern
        entries: List[str] = []
        for name in files:
            if name in base_exclude_names:
                continue
            ext = Path(name).suffix.lower()
            if ext in exclude_exts:
                continue
            entries.append(name)

        if not entries:
            continue

        # Gruppierung nach Erweiterung
        by_ext: Dict[str, List[str]] = {}
        for name in entries:
            by_ext.setdefault(Path(name).suffix.lower(), []).append(name)
        for ext in by_ext:
            by_ext[ext].sort(key=natural_key)

        existing_now = set(entries) | base_exclude_names
        renames: List[Tuple[Path, Path]] = []
        reserved_targets: set = set()

        for ext, names in by_ext.items():
            counter = 1
            for old_name in names:
                src = curr / old_name

                # Präfix via placeholders.expand() – mit ()-Logik, %N%, %rootN% etc.
                ctx = placeholders.Context(start_root=root, file_path=src)
                prefix = placeholders.expand(pattern, ctx)

                # Separator-Logik
                sep = ""
                if prefix and not re.search(r"[-_. ]$", prefix):
                    sep = "-"

                target_basename = f"{prefix}{sep}{counter:0{numbering_width}d}{ext}"
                target_basename = ensure_unique(target_basename, reserved_targets, existing_now)
                dst = curr / target_basename
                if src.name != dst.name:
                    renames.append((src, dst))
                counter += 1

        if not renames:
            continue

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

    if dry_run:
        return 0
    return total_renamed


# ------------------------- CLI -------------------------

def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description="ObisRenamer – Umbenennen nach INI-Vorlagen (placeholders.py)")
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
