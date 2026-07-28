#!/usr/bin/env python3
"""Extract readable text from a DOCX using only Python stdlib.

Use as a no-upload fallback when python-docx is unavailable or unnecessary:
    python3 scripts/docx_extract_text.py input.docx > extracted.txt
    python3 scripts/docx_extract_text.py input.docx --out extracted.txt

This preserves paragraph text and simple table rows. It is intentionally
conservative: it does not upload data, call network services, or attempt OCR.
"""
from __future__ import annotations

import argparse
import sys
import zipfile
import xml.etree.ElementTree as ET

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def paragraph_text(p: ET.Element) -> str:
    parts: list[str] = []
    for node in p.iter():
        tag = node.tag.split("}")[-1]
        if tag == "t" and node.text:
            parts.append(node.text)
        elif tag == "tab":
            parts.append("\t")
        elif tag == "br":
            parts.append("\n")
    return "".join(parts)


def extract_docx(path: str) -> str:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    body = root.find("w:body", NS)
    if body is None:
        return ""

    lines: list[str] = []
    for child in list(body):
        local = child.tag.split("}")[-1]
        if local == "p":
            text = paragraph_text(child).strip()
            if text:
                lines.append(text)
        elif local == "tbl":
            for tr in child.findall(".//w:tr", NS):
                cells: list[str] = []
                for tc in tr.findall("./w:tc", NS):
                    ps = [paragraph_text(p).strip() for p in tc.findall(".//w:p", NS)]
                    cells.append(" / ".join(p for p in ps if p))
                if any(cells):
                    lines.append(" | ".join(cells))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract text from DOCX locally with stdlib zipfile/XML.")
    parser.add_argument("docx")
    parser.add_argument("--out", help="Write output to this text file instead of stdout")
    args = parser.parse_args()

    text = extract_docx(args.docx)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
            if text and not text.endswith("\n"):
                f.write("\n")
    else:
        sys.stdout.write(text)
        if text and not text.endswith("\n"):
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
