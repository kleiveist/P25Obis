#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rename.py – Automatisches Umbenennen von Dateien mit optionaler
Ausführung zusätzlicher Skripte.

Erweitert um explizite Ausschlusslisten für Ordner- und Dateinamen.
"""

from __future__ import annotations

import os
import re
import datetime
import subprocess
import sys
from collections import defaultdict
from typing import Callable, List, Tuple

# =============================================================================
# SETTINGS – Hier nach Belieben anpassen
# =============================================================================
USE_DATE_PREFIX: bool = False          # jjmmdd Datum als Präfix verwenden?
USE_CREATION_DATE: bool = False        # True → Dateierstellungs­datum, False → Änderungsdatum
EXECUTE_ADDITIONAL_SCRIPTS: bool = True   # Weitere Skripte ausführen?
SCRIPT_FILES: List[str] = ["mdconfig.py"]       # Namen der auszuführenden Skripte
FOLDER_JOIN: str = "-"              # Trenner zwischen Ordnerteilen

# Ausschlusslisten
EXCLUDE_DIRS: List[str] = [".archive", "temp", "Wiki"]
EXCLUDE_FILES: List[str] = ["README.md", "config.yaml"]

# für fallunabhängige Vergleiche
EXCLUDE_DIRS_LOWER = [d.lower() for d in EXCLUDE_DIRS]
EXCLUDE_FILES_LOWER = [f.lower() for f in EXCLUDE_FILES]

# =============================================================================
# Interne Konstanten – bitte nicht verändern
# =============================================================================
_INVALID_WIN_CHARS = r'[<>:"/\\|?*\x00-\x1F]'
FOLDER_JOIN = re.sub(_INVALID_WIN_CHARS, "-", FOLDER_JOIN)

# Passende Zeitstempel-Funktion wählen
get_timestamp: Callable[[str], float] = (
    os.path.getctime if USE_CREATION_DATE else os.path.getmtime
)

# =============================================================================
# Hilfsfunktionen
# =============================================================================

def _clean_folder_name(name: str) -> str:
    """Entfernt führende Ziffern+"_" (z. B. "01_name" → "name")."""
    return re.sub(r"^\d+_", "", name).strip()


def _build_prefix(date_str: str, rel_parts: List[str], base_name: str) -> str:
    """Setzt den individuellen Präfix für *eine* Datei zusammen."""
    date_part = f"{date_str}_" if USE_DATE_PREFIX else ""

    # nur Ordner nutzen, die nicht mit "_" beginnen und nicht in EXCLUDE_DIRS
    cleaned = [
        _clean_folder_name(p)
        for p in rel_parts
        if not p.startswith("_") and p.lower() not in EXCLUDE_DIRS_LOWER
    ]
    middle = FOLDER_JOIN.join(cleaned)

    return f"{date_part}{base_name}{FOLDER_JOIN + middle if middle else ''}"


def _execute_scripts(script_files: List[str]) -> None:
    """Führt externe Python‑Skripte im gleichen Ordner wie dieses Skript aus.

    Existiert ein angegebenes Skript nicht, wird eine WARN‑Meldung ausgegeben,
    die Hauptlogik läuft ohne Abbruch weiter.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))

    for fname in script_files:
        script_path = os.path.join(base_dir, fname)
        if os.path.isfile(script_path):
            print(f"Starte zusätzliches Skript: {fname}")
            try:
                subprocess.run([sys.executable, script_path], check=True)
            except subprocess.CalledProcessError as exc:
                print(f"WARN: Skript '{fname}' beendet mit Exit-Code {exc.returncode}")
        else:
            print(f"WARN: Skript '{fname}' nicht gefunden – überspringe")

# =============================================================================
# Hauptlogik
# =============================================================================

def main() -> None:
    # Optionale Ausführung zusätzlicher Skripte
    if EXECUTE_ADDITIONAL_SCRIPTS:
        _execute_scripts(SCRIPT_FILES)

    base_dir: str = os.getcwd()
    base_name: str = os.path.basename(base_dir)

    files_to_rename: List[Tuple[str, str, str]] = []

    for root, dirs, files in os.walk(base_dir):
        # Verzeichnisbaum anpassen: keine Abstiege in EXCLUDE_DIRS
        dirs[:] = [d for d in dirs if d.lower() not in EXCLUDE_DIRS_LOWER]

        rel_dir = os.path.relpath(root, base_dir)
        rel_parts = [] if rel_dir == "." else rel_dir.split(os.sep)

        # falls doch ein EXCLUDE_DIR im Pfad steckt, überspringen
        if any(part.lower() in EXCLUDE_DIRS_LOWER for part in rel_parts):
            continue

        for file in files:
            # Exclude: Skriptdateien und konfigurierte Ausnahmen
            if file.lower().endswith(".py") or file.lower() in EXCLUDE_FILES_LOWER:
                continue

            full_path = os.path.join(root, file)
            timestamp = get_timestamp(full_path)
            date_str = datetime.datetime.fromtimestamp(timestamp).strftime("%y%m%d")

            prefix = _build_prefix(date_str, rel_parts, base_name)
            files_to_rename.append((full_path, prefix, file))

    # Schritt 2: pro Präfix sortieren & mit Sequenz versehen
    by_prefix: defaultdict[str, List[Tuple[str, str]]] = defaultdict(list)
    for full, pre, orig in files_to_rename:
        by_prefix[pre].append((full, orig))

    for prefix, file_list in by_prefix.items():
        file_list.sort()  # stabil: sortiert nach altem Dateinamen

        for seq, (full_path, orig_file) in enumerate(file_list, start=1):
            _, ext = os.path.splitext(orig_file)
            new_name = f"{prefix}_{seq:02d}{ext}"
            new_full_path = os.path.join(os.path.dirname(full_path), new_name)

            # bei Konflikten Sequenz hochzählen
            while os.path.exists(new_full_path) and os.path.abspath(full_path) != os.path.abspath(new_full_path):
                seq += 1
                new_name = f"{prefix}_{seq:02d}{ext}"
                new_full_path = os.path.join(os.path.dirname(full_path), new_name)

            # umbenennen
            if os.path.abspath(full_path) != os.path.abspath(new_full_path):
                print(f"{full_path}  →  {new_full_path}")
                os.rename(full_path, new_full_path)
            else:
                print(f"{full_path} bereits korrekt benannt.")

    print("Fertig – alle Dateien wurden überprüft und ggf. umbenannt!")


if __name__ == "__main__":
    main()
