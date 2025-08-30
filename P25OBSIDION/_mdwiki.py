import os
from pathlib import Path
from datetime import datetime

# ========== Einstellungen (anpassen oder erweitern) ==========
SETTINGS = {
    # Datum wird dynamisch mit dem Erstellungsdatum gefüllt
    'Projekt': 'IUFS',
    'Semester': 'SE1',
    'encyclopedie': 'Wiki',
    # Weitere Eigenschaften hier hinzufügen
}
# ===========================================================

def get_creation_date(file_path: Path) -> str:
    """Ermittelt das Erstellungsdatum der Datei im Format YYYY-MM-DD"""
    try:
        ts = file_path.stat().st_ctime
    except Exception:
        ts = file_path.stat().st_mtime
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d')


def process_md_file(file_path: Path):
    """Fügt oder aktualisiert Front-Matter-Einträge in einer Markdown-Datei"""
    lines = file_path.read_text(encoding='utf-8').splitlines(keepends=True)
    if not lines or lines[0].strip() != '---':
        return  # keine Front Matter vorhanden

    # Erstellungsdatum ermitteln
    creation_date = get_creation_date(file_path)

    # Datum separat verarbeiten, immer direkt unter '---'
    date_inserted = False
    for i, l in enumerate(lines[1:], start=1):
        if l.strip().lower().startswith('datum:'):
            lines[i] = f'Datum: {creation_date}\n'
            date_inserted = True
            break
    if not date_inserted:
        lines.insert(1, f'Datum: {creation_date}\n')

    # Suche nach tags:-Zeile
    tags_idx = None
    for idx, line in enumerate(lines[1:], start=1):
        if line.strip().lower().startswith('tags:'):
            tags_idx = idx
            break

    # Einfügeposition für die anderen Einstellungen: direkt nach Datum
    # Datum ist immer an Index 1
    insert_at = 2
    if tags_idx is not None and insert_at > tags_idx:
        insert_at = tags_idx

    # Aktualisiere oder füge übrige SETTINGS-Einträge ein
    for key, val in SETTINGS.items():
        found = False
        for i, l in enumerate(lines[1:], start=1):
            if l.strip().lower().startswith(f'{key.lower()}:'):
                lines[i] = f'{key}: {val}\n'
                found = True
                break
        if not found:
            lines.insert(insert_at, f'{key}: {val}\n')
            insert_at += 1

    # Falls tags:-Block fehlt, hinzufügen
    if tags_idx is None:
        lines.insert(insert_at, 'tags:\n')

    # Zurückschreiben
    file_path.write_text(''.join(lines), encoding='utf-8')


def main():
    # Starte Suche im aktuellen Arbeitsverzeichnis
    base_dir = Path.cwd()
    wiki_dirs = []

    # Rekursive Suche nach Ordnern namens 'wiki' (case-insensitive)
    for root, dirs, _ in os.walk(base_dir):
        for d in dirs:
            if d.lower() == 'wiki':
                wiki_dirs.append(Path(root) / d)

    if not wiki_dirs:
        print('Keine Wiki-Ordner gefunden!')
        return

    # Prozessiere alle Markdown-Dateien in gefundenen Wiki-Ordnern
    for wiki_dir in wiki_dirs:
        for root, _, files in os.walk(wiki_dir):
            for f in files:
                if f.lower().endswith('.md'):
                    fp = Path(root) / f
                    process_md_file(fp)
                    print(f'Bearbeitet: {fp}')


if __name__ == '__main__':
    main()
