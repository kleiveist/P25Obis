#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob

def format_md(lines):
    clean = [l.rstrip('\n') for l in lines if l.strip() != '']
    out = []
    for i, line in enumerate(clean):
        # 1) Überschrift: keine Leerzeile davor
        if line.startswith('#'):
            if out and out[-1] == '':
                out.pop()
            out.append(line)
            continue

        # 2) Horizontal Rule: immer Leerzeile davor,
        #    danach nur bei echtem Fließtext
        if line.strip() == '---':
            if out and out[-1] != '':
                out.append('')
            out.append(line)
            if i + 1 < len(clean):
                nxt = clean[i + 1]
                if not nxt.startswith(('-', '#', '|')):
                    out.append('')
            continue

        # 3) Tabelle: nur vor erstem Tabellen-Eintrag und nicht nach '---'
        if line.startswith('|'):
            if not (out and out[-1].startswith('|')) and out and out[-1] not in ('', '---'):
                out.append('')
            out.append(line)
            continue

        # 4) Aller Rest (Listen-Items, Fließtext usw.):
        out.append(line)

    return out

def main():
    skript_dir = os.path.dirname(os.path.abspath(__file__))
    for pfad in glob.glob(os.path.join(skript_dir, '*.md')):
        with open(pfad, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        neu = format_md(lines)
        with open(pfad, 'w', encoding='utf-8') as f:
            f.write('\n'.join(neu))
        print(f"{os.path.basename(pfad)} formatiert")

if __name__ == '__main__':
    main()
