#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kompakte Platzhalter-Engine für Präfixe/Patterns.
Ziel: keine Umbenennungs-/Zähl-Logik, nur Rendering.

Unterstützte Platzhalter (case-insensitive):
- %root%           : Basename des Start-Roots (bereinigt, () entfernt)
- %root()%         : Basename des Start-Roots (roh, () beibehalten)
- %rootN%          : N-tes Segment ab Root (1-basiert, bereinigt)
- %rootN()%        : N-tes Segment ab Root (roh)
- %rootNB%         : erster Buchstabe von %rootN% (bereinigt, Uppercase)
- %folder%         : aktueller Ordnername (bereinigt)
- %folder()%       : aktueller Ordnername (roh)
- %folderN%        : N-tes Segment nach oben (1=Elternordner, bereinigt)
- %folderN()%      : wie oben (roh)
- %N%              : letzte Ziffernfolge aus aktuellem Ordnernamen;
                    Wiederholung steuert Zero-Padding: %N%%N% -> Breite 2;
                    ohne Ziffern -> Nullen mit passender Breite.
- %date%           : Datum ISO (YYYY-MM-DD) von Datei-ctime/birthtime* oder mtime
- %datum%          : Datum kompakt (YYYYMMDD)
- %wert%           : alter Dateiname (ohne Erweiterung, vom Context.file_path)

*Wenn st_birthtime vorhanden ist, wird sie verwendet, sonst mtime.
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional
import re
import time
import os

__all__ = ["Context", "expand"]

# ---------- Context ----------

@dataclass(frozen=True)
class Context:
    start_root: Path   # Root/Anker
    file_path: Path    # konkrete Datei innerhalb eines Ordners (aktueller Ordner = file_path.parent)

    @property
    def current_dir(self) -> Path:
        return self.file_path.parent

    @property
    def current_dirname(self) -> str:
        return self.current_dir.name

    @property
    def root_basename(self) -> str:
        return self.start_root.name

    def rel_parts_from_root(self) -> List[str]:
        """Segmente ab Root bis zum aktuellen Ordner (1-basiert für %rootN%)."""
        p = self.current_dir
        if self.start_root and (self.start_root in p.parents or p == self.start_root):
            rel = p.relative_to(self.start_root)
            return [] if str(rel) == "." else list(rel.parts)
        return list(p.parts)

    def parts_up_from_file(self) -> List[str]:
        """Segmente nach oben ab dem Elternordner der Datei (1=Eltern)."""
        out: List[str] = []
        cur = self.file_path.parent
        while True:
            parent = cur.parent
            if cur == parent:
                break
            out.append(cur.name)
            cur = parent
        return out


# ---------- Helpers ----------

_RE_N_BLOCK = re.compile(r"(?:%N%)+", flags=re.IGNORECASE)

def _strip_paren_content(s: str) -> str:
    """Entfernt (...) inkl. Inhalt und trimmt."""
    if not s:
        return s
    return re.sub(r"\([^)]*\)", "", s).strip()

def _extract_last_number(s: str) -> str:
    m = re.search(r"(\d+)(?!.*\d)", s)
    return m.group(1) if m else ""

def _replace_N_blocks(text: str, folder_name: str) -> str:
    digits = _extract_last_number(folder_name)
    def repl(m: re.Match) -> str:
        block = m.group(0)
        # Anzahl %N% im Block = len(block) // 3 ("%N%" hat 3 Zeichen)
        width = len(block) // 3
        v = digits if digits else "0"
        return v.zfill(width)
    return _RE_N_BLOCK.sub(repl, text)

def _file_timestamp(ctx: Context) -> float:
    st = ctx.file_path.stat()
    # birthtime wenn vorhanden, sonst mtime
    ts = getattr(st, "st_birthtime", None)
    if ts:
        return float(ts)
    return float(st.st_mtime)

def _dates(ctx: Context) -> Tuple[str, str]:
    t = time.localtime(_file_timestamp(ctx))
    return time.strftime("%Y%m%d", t), time.strftime("%Y-%m-%d", t)

def _segment_root(ctx: Context, n: int, raw: bool) -> str:
    """%rootN% / %rootN()% (N>=1)."""
    if n < 1:
        return _strip_paren_content(ctx.root_basename) if not raw else ctx.root_basename
    parts = ctx.rel_parts_from_root()
    seg = parts[n-1] if 0 <= (n-1) < len(parts) else ""
    return seg if raw else _strip_paren_content(seg)

def _segment_folder(ctx: Context, n: int, raw: bool) -> str:
    """%folderN% / %folderN()% (N>=1; 1=Elternordner)."""
    if n < 1:
        name = ctx.current_dirname
        return name if raw else _strip_paren_content(name)
    up = ctx.parts_up_from_file()
    seg = up[n-1] if 0 <= (n-1) < len(up) else (up[-1] if up else ctx.current_dirname)
    return seg if raw else _strip_paren_content(seg)


# ---------- Expand ----------

def expand(pattern: str, ctx: Context, unknown_passthrough: bool = True) -> str:
    """
    Rendert ein Pattern mit allen oben beschriebenen Platzhaltern.
    Reihenfolge der Ersetzungen ist relevant (erst %N%).
    """
    if not pattern:
        return ""
    pat = pattern.strip().strip('`"\'')  # tolerantes Entfernen von Quotes/Backticks

    # 1) %N% Blöcke
    pat = _replace_N_blocks(pat, ctx.current_dirname)

    # 2) %rootNB% / %folderNB% (bereinigt, Initial)
    def repl_B(m: re.Match) -> str:
        kind = m.group(1).lower()
        n = int(m.group(2))
        if kind == "root":
            seg = _segment_root(ctx, n, raw=False)
        else:
            seg = _segment_folder(ctx, n, raw=False)
        return seg[:1].upper() if seg else ""
    pat = re.sub(r"%(root|folder)(\d+)B%", repl_B, pat, flags=re.IGNORECASE)

    # 3) %rootN()% / %folderN()% (roh)
    def repl_N_raw(m: re.Match) -> str:
        kind = m.group(1).lower()
        n = int(m.group(2))
        return _segment_root(ctx, n, raw=True) if kind == "root" \
               else _segment_folder(ctx, n, raw=True)
    pat = re.sub(r"%(root|folder)(\d+)\(\)%", repl_N_raw, pat, flags=re.IGNORECASE)

    # 4) %rootN% / %folderN% (bereinigt)
    def repl_N(m: re.Match) -> str:
        kind = m.group(1).lower()
        n = int(m.group(2))
        return _segment_root(ctx, n, raw=False) if kind == "root" \
               else _segment_folder(ctx, n, raw=False)
    pat = re.sub(r"%(root|folder)(\d+)%", repl_N, pat, flags=re.IGNORECASE)

    # 5) %root()% / %folder()% (roh)
    pat = re.sub(r"%root\(\)%", ctx.root_basename, pat, flags=re.IGNORECASE)
    pat = re.sub(r"%folder\(\)%", ctx.current_dirname, pat, flags=re.IGNORECASE)

    # 6) %root% / %folder% (bereinigt)
    pat = re.sub(r"%root%", _strip_paren_content(ctx.root_basename), pat, flags=re.IGNORECASE)
    pat = re.sub(r"%folder%", _strip_paren_content(ctx.current_dirname), pat, flags=re.IGNORECASE)

    # 7) %datum% / %date%
    d_compact, d_iso = _dates(ctx)
    pat = re.sub(r"%datum%", d_compact, pat, flags=re.IGNORECASE)
    pat = re.sub(r"%date%",  d_iso,     pat, flags=re.IGNORECASE)

    # 8) %wert%
    pat = re.sub(r"%wert%", ctx.file_path.stem, pat, flags=re.IGNORECASE)

    # unbekannte %...% ggf. durchlassen
    return pat if unknown_passthrough else re.sub(r"%[^%]+%", "", pat)
