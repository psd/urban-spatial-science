#!/usr/bin/env python3
"""Convert vault sub-vault frontmatter to CSV on stdout.

Usage: python3 scripts/frontmatter_to_csv.py vault/<subvault>
"""
import csv
import re
import sys
import yaml
from pathlib import Path


def unwrap_wikilink(val):
    """[[prefix/slug]] -> slug"""
    m = re.match(r'^\[\[(?:[^/\]]+/)?([^\]]+)\]\]$', val.strip())
    return m.group(1) if m else val


def flatten(val):
    if val is None:
        return ''
    if isinstance(val, list):
        # reading-lists: [{list: "[[...]]", importance: "..."}]
        if val and isinstance(val[0], dict) and 'list' in val[0]:
            parts = []
            for item in val:
                uuid = unwrap_wikilink(str(item.get('list', '')))
                imp = item.get('importance', '')
                parts.append(f'{uuid}:{imp}' if imp else uuid)
            return ';'.join(parts)
        # plain lists: isbn10, isbn13
        return ';'.join(str(flatten(v)) for v in val)
    if isinstance(val, str):
        return unwrap_wikilink(val)
    return str(val)


def parse_frontmatter(path):
    text = path.read_text(encoding='utf-8')
    m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


vault_dir = Path(sys.argv[1])
md_files = sorted(vault_dir.glob('*.md'))

records = []
fieldnames = []
seen = set()

for f in md_files:
    fm = parse_frontmatter(f)
    records.append(fm)
    for k in fm:
        if k not in seen:
            fieldnames.append(k)
            seen.add(k)

writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames,
                        extrasaction='ignore', lineterminator='\n')
writer.writeheader()
for rec in records:
    writer.writerow({k: flatten(rec.get(k)) for k in fieldnames})
