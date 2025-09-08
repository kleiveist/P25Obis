#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import re
from pathlib import Path
from typing import List, Dict, Any

# =========================
# USER SETTINGS (hier anpassen)
# =========================
SETTINGS: Dict[str, Any] = {
    # Ordnernamen (genau, ohne Pfad) die NICHT bearbeitet / NICHT traversiert werden
    "EXCLUDE_FOLDERS": {
        ".git",
        "node_modules",
        ".venv",
        "__pycache__",
        ".obsidian",
        ".archive",
    },
    # Prefix für Ordner-Links unter #Folder, z. B. "Data-" -> [[Data-Unternehmertum]]
    "FOLDER_LINK_PREFIX": "",
    # Versteckte Elemente (beginnen mit ".") generell ignorieren?
    "IGNORE_DOT_ITEMS": True,
}

AUTOGEN_START = "<!-- AUTOGEN_START -->"
AUTOGEN_END = "<!-- AUTOGEN_END -->"


# ---------- Hilfsfunktionen ----------

def is_hidden(p: Path) -> bool:
    return SETTINGS["IGNORE_DOT_ITEMS"] and p.name.startswith(".")

def list_immediate(path: Path, excluded: set):
    subs = sorted([d for d in path.iterdir()
                   if d.is_dir() and not is_hidden(d) and d.name not in excluded],
                  key=lambda p: p.name.lower())
    mds  = sorted([f for f in path.iterdir()
                   if f.is_file() and f.suffix.lower()==".md" and not is_hidden(f)],
                  key=lambda p: p.name.lower())
    files= sorted([f for f in path.iterdir()
                   if f.is_file() and f.suffix.lower()!=".md" and not is_hidden(f)],
                  key=lambda p: p.name.lower())
    return subs, mds, files

def build_block(subfolders: List[Path], md_files: List[Path], other_files: List[Path],
                index_filename: str) -> str:
    parts: List[str] = [AUTOGEN_START]

    # #Folder
    folder_lines = []
    for d in subfolders:
        link_target = f"{SETTINGS['FOLDER_LINK_PREFIX']}{d.name}" if SETTINGS["FOLDER_LINK_PREFIX"] else d.name
        folder_lines.append(f"[[{link_target}]]")
    if folder_lines:
        parts.append("\n---\n#Folder")
        parts.extend(folder_lines)

    # #Markdown
    md_lines = []
    for f in md_files:
        if f.name == index_filename:
            continue  # nicht sich selbst einbetten
        md_lines.append(f"![[{f.name}]]")
    if md_lines:
        parts.append("\n---\n#Markdown")
        parts.extend(md_lines)

    # #Files
    file_lines = [f"![[{f.name}]]" for f in other_files]
    if file_lines:
        parts.append("\n---\n#Files")
        parts.extend(file_lines)

    parts.append(AUTOGEN_END)
    return ("\n".join(parts)).strip() + "\n"

def strip_placeholder_links(content: str) -> str:
    """
    Entfernt NUR einen Platzhalterblock mit leeren Links:
    # Links
    [[]]
    [[]]
    ...
    """
    pattern = re.compile(
        r"(^|\n)#{1,6}\s*Links\s*\n(?:\s*\[\[\]\]\s*\n?)+",
        flags=re.IGNORECASE
    )
    return re.sub(pattern, r"\1", content)

def merge_content(existing: str, new_block: str) -> str:
    if not existing:
        return new_block
    cleaned = strip_placeholder_links(existing)
    if AUTOGEN_START in cleaned and AUTOGEN_END in cleaned:
        pattern = re.compile(
            re.escape(AUTOGEN_START) + r".*?" + re.escape(AUTOGEN_END),
            flags=re.DOTALL
        )
        merged = pattern.sub(new_block.strip(), cleaned)
        if not merged.endswith("\n"):
            merged += "\n"
        return merged
    else:
        sep = "" if cleaned.endswith("\n\n") else ("\n" if cleaned.endswith("\n") else "\n\n")
        return f"{cleaned}{sep}{new_block}"

def determine_index_name(dir_name: str) -> str:
    # Immer <Ordnername>.md (kein Sonderfall)
    return f"{dir_name}.md"

# ---------- Verarbeitung ----------

def process_dir(dir_path: Path, excluded: set):
    subs, mds, files = list_immediate(dir_path, excluded)

    index_name = determine_index_name(dir_path.name)
    index_path = dir_path / index_name

    block = build_block(
        subfolders=subs,
        md_files=mds,
        other_files=files,
        index_filename=index_name,
    )

    existing = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    merged = merge_content(existing, block)
    index_path.write_text(merged, encoding="utf-8")
    print(f"[OK]  {index_path}")

def walk_all(root: Path, excluded: set):
    for dirpath, dirnames, filenames in os.walk(root):
        p = Path(dirpath)

        # Prune bevor Abstieg
        dirnames[:] = [
            d for d in dirnames
            if not (SETTINGS["IGNORE_DOT_ITEMS"] and d.startswith(".")) and d not in excluded
        ]

        # Falls doch in ausgeschlossenen/versteckten Ordner geraten -> überspringen
        if (SETTINGS["IGNORE_DOT_ITEMS"] and p.name.startswith(".")) or p.name in excluded:
            continue

        process_dir(p, excluded)

def main():
    parser = argparse.ArgumentParser(
        description="Erzeuge/aktualisiere Ordner-Index-Markdown-Dateien ab Startpunkt rekursiv nach unten."
    )
    parser.add_argument("root", nargs="?", default=Path("."), type=Path,
                        help="Startordner (Default: aktuelles Verzeichnis '.')")
    parser.add_argument("--dry-run", action="store_true", help="Nur Ausgabe simulieren (keine Schreibzugriffe).")
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root nicht gefunden/kein Ordner: {root}")

    excluded = set(SETTINGS["EXCLUDE_FOLDERS"])

    if args.dry_run:
        # Trockenlauf: nur anzeigen, welche Indexdateien betroffen wären
        for dirpath, dirnames, filenames in os.walk(root):
            p = Path(dirpath)
            dirnames[:] = [
                d for d in dirnames
                if not (SETTINGS["IGNORE_DOT_ITEMS"] and d.startswith(".")) and d not in excluded
            ]
            if (SETTINGS["IGNORE_DOT_ITEMS"] and p.name.startswith(".")) or p.name in excluded:
                continue
            index_name = determine_index_name(p.name)
            print(f"[DRY] würde schreiben: {p / index_name}")
        return

    walk_all(root, excluded)

if __name__ == "__main__":
    main()
