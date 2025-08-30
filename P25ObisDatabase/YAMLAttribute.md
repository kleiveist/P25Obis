
* **Datum**
* **Projekt**
* **Section**
* **Task**
* **Semester**
* **Courses**
* **Prio**
* **Stratus**
* **Stratus_**
* **Text**

| Attribut   | Bemerkung | Attributwerte |
|------------|-----------|---------------|
| **Datum**  | Erstellungsdatum der Datei | Variabel, Format: `YYYY-MM-DD` |
| **Projekt** | Name oder Kennung des Projekts | z. B. `IUFS`, `HEI-West`, `P25Name` |
| **Section** | Abschnitt oder Teilbereich, z. B. Kapitel, Modul | – |
| **Task** | Typ der Aufgabe | `Settings`, `Improvement`, `Process`, `Timetable` |
| **Semester** | Studiensemester | `SE1` bis `SE6` |
| **Courses** | Zugeordnete Kurse oder Lehrveranstaltungen | – |
| **Prio** | Priorität / Wichtigkeit | `hoch`, `mittel`, `niedrig` oder Skala `1–5` |
| **Stratus** | Status der Aufgabe | `Open`, `Done`, `Canceled`, `Progress`, `Onhold` |
| **Stratus_** | Icon-basierter Status | 🟠, 🔵, ❌, ✅, ⚫ |
| **Text** | Freitextfeld für Beschreibung, Notizen oder Kommentare | – |
# Attributbeschreibung

Die folgenden Attribute sind in fester Reihenfolge definiert.  
Es dürfen keine zusätzlichen Attribute ergänzt oder die Reihenfolge verändert werden.

---

## 1. Datum
- **Beschreibung**: Erstellungsdatum der Datei.  
- **Format**: `YYYY-MM-DD` (ISO-Format).  
- **Beispiel**: `2025-08-26`.

---

## 2. Projekt
- **Beschreibung**: Name oder Kennung des Projekts.  
- **Attributwerte**: `IUFS`, `HEI-West`, `P25Name`.  
- **Bemerkung**: Dient zur eindeutigen Projektzuordnung.

---

## 3. Section
- **Beschreibung**: Abschnitt oder Teilbereich (z. B. Kapitel, Modul).  
- **Attributwerte**: variabel nach Bedarf.  
- **Bemerkung**: Strukturelement zur Untergliederung.

---

## 4. Task
- **Beschreibung**: Typ der Aufgabe.  
- **Attributwerte**: `Settings`, `Improvement`, `Process`, `Timetable`.  
- **Bemerkung**: Legt den Charakter oder die Art der Aufgabe fest.

---
==Nur Für die UI==
## 5. Semester
- **Beschreibung**: Zugehöriges Studiensemester.  
- **Attributwerte**: `SE1` bis `SE6`.  
- **Bemerkung**: Ordnet Aufgabe/Projekt einem Studienabschnitt zu.

---
==Nur Für die UI==
## 6. Courses
- **Beschreibung**: Zugeordnete Kurse oder Lehrveranstaltungen.  
- **Attributwerte**: variabel nach Bedarf.  
- **Bemerkung**: Referenz auf Lehrinhalte.

---

## 7. Prio
- **Beschreibung**: Priorität der Aufgabe.  
- **Attributwerte**: `hoch`, `mittel`, `niedrig` oder numerisch `1–5`.  
- **Bemerkung**: Bestimmt Dringlichkeit und Bearbeitungsreihenfolge.

---

## 8. Stratus
- **Beschreibung**: Status der Aufgabe.  
- **Attributwerte**: `Open`, `Done`, `Canceled`, `Progress`, `Onhold`.  
- **Bemerkung**: Klassischer Workflow-Status.

---

## 9. Stratus_
- **Beschreibung**: Icon-basierter Status (visuelle Darstellung).  
- **Attributwerte**: 🟠 (offen), 🔵 (in Arbeit), ❌ (abgebrochen), ✅ (erledigt), ⚫ (on hold).  
- **Bemerkung**: Ergänzende visuelle Statusanzeige.

---

## 10. Text
- **Beschreibung**: Freitextfeld.  
- **Attributwerte**: variabel.  
- **Bemerkung**: Für Notizen, Kommentare oder zusätzliche Infos.
