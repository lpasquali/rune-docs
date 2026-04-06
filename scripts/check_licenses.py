import json
import re

blocked_ids = {
    'AGPL-3.0-ONLY',
    'AGPL-3.0-OR-LATER',
    'GPL-3.0-ONLY',
    'GPL-3.0-OR-LATER',
}

alias_map = {
    'AGPLV3': 'AGPL-3.0-ONLY',
    'AGPL V3': 'AGPL-3.0-ONLY',
    'AGPL-3': 'AGPL-3.0-ONLY',
    'AGPL-3.0': 'AGPL-3.0-ONLY',
    'GNU AFFERO GENERAL PUBLIC LICENSE V3': 'AGPL-3.0-ONLY',
    'GNU AFFERO GENERAL PUBLIC LICENSE VERSION 3': 'AGPL-3.0-ONLY',
    'GPLV3': 'GPL-3.0-ONLY',
    'GPL V3': 'GPL-3.0-ONLY',
    'GPL-3': 'GPL-3.0-ONLY',
    'GPL-3.0': 'GPL-3.0-ONLY',
    'GNU GENERAL PUBLIC LICENSE V3': 'GPL-3.0-ONLY',
    'GNU GENERAL PUBLIC LICENSE VERSION 3': 'GPL-3.0-ONLY',
}

def normalize_license_id(value):
    text = (value or '').strip().upper()
    if not text:
        return ''
    text = re.sub(r'\s+', ' ', text)
    return alias_map.get(text, text)

def extract_license_ids(value):
    text = (value or '').strip()
    if not text:
        return set()
    parts = re.split(r'\s+(?:OR|AND)\s+|[(),;|/]+', text, flags=re.IGNORECASE)
    return {normalize_license_id(part) for part in parts if normalize_license_id(part)}

blocked = []
for row in json.load(open('licenses-python.json', encoding='utf-8')):
    license_text = row.get('License') or ''
    if extract_license_ids(license_text) & blocked_ids:
        blocked.append((row.get('Name'), row.get('License')))
if blocked:
    for name, lic in blocked:
        print(f'BLOCK {name}: {lic}')
    raise SystemExit(1)
