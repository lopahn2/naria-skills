#!/usr/bin/env python3
"""Read-only inventory for a downloaded lecture archive.

    python3 inventory.py <day_dir>

Finds transcripts, PDFs, and raster source visuals before the workflow copies
them into the canonical audio/, slides/, and figures/ directories.
"""
from __future__ import annotations

import os
import struct
import sys
from pathlib import Path


ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
SKIP = {"notes", "out", "qa", "tmp", "__pycache__"}
TEXT = {".txt", ".srt", ".vtt"}
PDF = {".pdf"}
RASTER = {".png", ".jpg", ".jpeg", ".webp"}


def candidates() -> list[Path]:
    return [path for path in ROOT.rglob("*") if path.is_file() and not set(path.parts).intersection(SKIP)]


def encoding_hint(path: Path) -> str:
    raw = path.read_bytes()[:4096]
    if raw.startswith(b"\xff\xfe"):
        return "UTF-16LE BOM"
    if raw.startswith(b"\xfe\xff"):
        return "UTF-16BE BOM"
    if raw.startswith(b"\xef\xbb\xbf"):
        return "UTF-8 BOM"
    if raw and raw.count(b"\x00") > len(raw) // 5:
        return "UTF-16 likely"
    return "UTF-8/legacy unknown"


def png_size(path: Path) -> str:
    raw = path.read_bytes()[:24]
    if raw[:8] != b"\x89PNG\r\n\x1a\n" or len(raw) < 24:
        return "invalid PNG"
    width, height = struct.unpack(">II", raw[16:24])
    return f"{width:,} × {height:,} ({width / height:.2f}:1)"


def report(label: str, paths: list[Path]) -> None:
    print(f"\n=== {label} ({len(paths)}) ===")
    for path in paths:
        extra = encoding_hint(path) if path.suffix.lower() in TEXT else \
            png_size(path) if path.suffix.lower() == ".png" else ""
        print(f"  {path.relative_to(ROOT)}  {path.stat().st_size:,} bytes  {extra}")


if not ROOT.exists():
    raise SystemExit(f"Not found: {ROOT}")

files = candidates()
report("transcripts", [p for p in files if p.suffix.lower() in TEXT])
report("PDFs", [p for p in files if p.suffix.lower() in PDF])
report("raster visuals", [p for p in files if p.suffix.lower() in RASTER])
print("\nNext: copy transcripts to audio/pNN.txt, PDFs to slides/, and raster originals to figures/; keep archive paths in manifest.json.")
