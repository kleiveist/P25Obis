#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mdconf.py – Generiert/aktualisiert für jeden Unterordner eine Obsidian-kompatible
MD-Datei und räumt veraltete MD-Dateien auf.

Funktion:
1. Traversiert rekursiv ab dem Ausführungs­ordner.
2. Ignoriert Ordner, deren Namen in EXCLUDE_DIRS stehen.
3. Legt pro Ordner eine MD-Datei <PfadSegmenteOhneTrenner>.md an
   (z. B. IUFSSE1BWL01Lektion1.md).
4. Überschreibt vorhandene MD-Dateien gleichen Namens.
5. Entfernt sonstige *.md im selben Ordner (manuell umbenannte Reste).
6. Front-Matter enthält:
   - Projekt   = erstes Segment
   - Semester  = zweites Segment (falls vorhanden)
   - tags      = relativer Pfad (Backslash-getrennt)
   - link      = Referenz auf die Eltern­ebene (falls vorhanden)
   - link1     = Referenz auf den aktuellen Ordner
7. Anhängt anschließend Em­beds (![[…]]) aller Nicht-MD-Dateien im Ordner.

Anpassbar über die Konstanten unten.
"""
from __future__ import annotations

import os
from typing import List

# --------------------------------------------------------------------------- #
# Einstellungen                                                               #
# --------------------------------------------------------------------------- #
EXCLUDE_DIRS: set[str] = {"Wiki", ".git", "__pycache__"}  # auszuschließende Ordner
DELETE_OLD_MD: bool = True        # veraltete/umbenannte *.md löschen?
EMBED_EXTENSIONS: tuple[str, ...] = ()  # leer = alle Dateien einbetten

# --------------------------------------------------------------------------- #
# Hilfsfunktionen                                                             #
# --------------------------------------------------------------------------- #
def _md_filename(parts: List[str]) -> str:
    """Erzeugt den MD-Dateinamen aus allen Pfadsegmenten."""
    return "".join(parts) + ".md"


def _front_matter(parts: List[str], rel_path: str) -> str:
    """Erstellt das YAML-Front-Matter."""
    projekt = parts[0] if parts else ""
    semester = parts[1] if len(parts) > 1 else ""
    parent = parts[-2] if len(parts) > 1 else ""
    current = parts[-1] if parts else ""

    lines = [
        "---",
        f"Projekt: {projekt}",
        f"Semester: {semester}",
        "tags:",
        f"  - {rel_path}",
        f'link: "[[{parent}]]"' if parent else "",
        f'link1: "[[{current}]]"',
        "---",
        "---",
    ]
    return "\n".join(l for l in lines if l) + "\n"


def _embed_lines(files: List[str]) -> str:
    """Erzeugt Zeilen mit ![[…]]-Einbettungen."""
    embeds = [
        f"![[{f}]]" for f in sorted(files)
        if not f.lower().endswith(".md")
        and (not EMBED_EXTENSIONS or f.lower().endswith(EMBED_EXTENSIONS))
    ]
    return "\n".join(embeds) + ("\n" if embeds else "")


# --------------------------------------------------------------------------- #
# Hauptlogik                                                                  #
# --------------------------------------------------------------------------- #
def main() -> None:
    base_dir = os.getcwd()

    for root, dirs, files in os.walk(base_dir):
        # Unterordner, die nicht weiter untersucht werden sollen, aussortieren
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        rel_path = os.path.relpath(root, base_dir)
        if rel_path == ".":
            continue  # für das Start­verzeichnis selbst keine MD erzeugen

        parts = rel_path.split(os.sep)
        md_name = _md_filename(parts)
        md_path = os.path.join(root, md_name)

        # Front-Matter + Embeds erzeugen
        content = _front_matter(parts, rel_path) + _embed_lines(files)

        # Datei (über-)schreiben
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"aktualisiert: {md_path}")

        # Veraltete MD-Dateien löschen
        if DELETE_OLD_MD:
            for fname in files:
                if fname.lower().endswith(".md") and fname != md_name:
                    try:
                        os.remove(os.path.join(root, fname))
                        print(f"gelöscht:     {os.path.join(root, fname)}")
                    except OSError as err:
                        print(f"WARN: {err}")

    print("MD-Generierung abgeschlossen.")


if __name__ == "__main__":
    main()
