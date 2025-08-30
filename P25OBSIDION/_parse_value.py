#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

# Parsen eines numerischen Werts (mit oder ohne Anführungszeichen)
def parse_value(line, key):
    match = re.match(rf'\s*{key}:\s*"?(\d+)"?', line)
    return int(match.group(1)) if match else None

# Status-Icon (ab 50 % bestanden)
def get_status_icon(percent):
    if percent >= 50:
        return "✅", "Bestanden"
    else:
        return "❌", "Nicht bestanden"

# Notenschlüssel: 90–100→1, 80–89→2, 70–79→3, 60–69→4, 45–59→5, <45→6
def get_grade_icon_and_number(percent):
    if percent >= 90:
        return "🔵", 1
    elif percent >= 80:
        return "🟢", 2
    elif percent >= 70:
        return "🟡", 3
    elif percent >= 50:
        return "🟠", 4
    elif percent >= 45:
        return "🔴", 5
    else:
        return "⚫", 6

def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        original_lines = f.readlines()

    keys = ["MuiChoi", "Textaufgabe1", "Textaufgabe2", "Trans"]
    values = {}
    new_lines = []
    inserted = False

    # Zunächst alle Werte sammeln (unabhängig von Position)
    for line in original_lines:
        for key in keys:
            val = parse_value(line, key)
            if val is not None:
                values[key] = val

    total = sum(values.get(k, 0) for k in keys)
    percent = round((total / 45) * 100) if total > 0 else 0

    # Spezieller Fall: noch nicht begonnen (0 Punkte, 0 %)
    if total == 0 and percent == 0:
        ergebnis_zeile = f'Ergebnis: 0 | 🚫 Nicht begonnen\n'
        prozent_zeile  = f'Prozent: 0% | ⚪ 0\n'
    else:
        status_icon, status_text = get_status_icon(percent)
        grade_icon, grade_number = get_grade_icon_and_number(percent)
        ergebnis_zeile = f'Ergebnis: {total} | {status_icon} {status_text}\n'
        prozent_zeile  = f'Prozent: {percent}% | {grade_icon} {grade_number}\n'

    # Jetzt Zeile für Zeile neu aufbauen und alte Ergebnis/Prozent überspringen
    for line in original_lines:
        if re.match(r'\s*Ergebnis:', line) or re.match(r'\s*Prozent:', line):
            continue

        if not inserted and re.match(r'\s*MuiChoi\s*:', line):
            new_lines.append(ergebnis_zeile)
            new_lines.append(prozent_zeile)
            inserted = True

        new_lines.append(line)

    # Datei mit aktualisierten Zeilen überschreiben
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def main():
    for filename in os.listdir('.'):
        if filename.lower().endswith('.md'):
            process_file(filename)

if __name__ == "__main__":
    main()
