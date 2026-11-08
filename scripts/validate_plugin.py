#!/usr/bin/env python3
"""Validate a standalone Antigravity plugin repository without third-party packages."""
from pathlib import Path
import json, re, sys
ROOT = Path(__file__).resolve().parents[1]
errors = []

def parse_frontmatter(path: Path):
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        errors.append(f'{path.relative_to(ROOT)}: missing YAML frontmatter')
        return {}
    end = text.find('\n---', 4)
    if end < 0:
        errors.append(f'{path.relative_to(ROOT)}: unterminated frontmatter')
        return {}
    result = {}
    for line in text[4:end].splitlines():
        match = re.match(r'^([A-Za-z0-9_-]+):\s*(.*)$', line)
        if match:
            result[match.group(1)] = match.group(2).strip().strip('"\'')
    return result

manifest_path = ROOT / 'plugin.json'
if not manifest_path.is_file():
    errors.append('plugin.json must exist at repository root')
else:
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', manifest.get('name', '')):
            errors.append('plugin.json name must be lowercase kebab-case')
        if not re.fullmatch(r'\d+\.\d+\.\d+', manifest.get('version', '')):
            errors.append('plugin.json version must use MAJOR.MINOR.PATCH')
        if len(manifest.get('suggestedPrompts', [])) > 3:
            errors.append('plugin.json suggestedPrompts supports at most 3 items')
    except Exception as exc:
        errors.append(f'invalid plugin.json: {exc}')

for path in (ROOT / 'agents').glob('*.md') if (ROOT / 'agents').exists() else []:
    fm = parse_frontmatter(path)
    if fm.get('name') != path.stem:
        errors.append(f'{path.relative_to(ROOT)}: name must match filename')
    if not fm.get('description'):
        errors.append(f'{path.relative_to(ROOT)}: description is required')

for path in (ROOT / 'skills').glob('*/SKILL.md') if (ROOT / 'skills').exists() else []:
    fm = parse_frontmatter(path)
    if fm.get('name') != path.parent.name:
        errors.append(f'{path.relative_to(ROOT)}: skill name must match directory')
    if not fm.get('description'):
        errors.append(f'{path.relative_to(ROOT)}: skill description is required')

if errors:
    print('PLUGIN VALIDATION FAILED')
    for error in errors:
        print('ERROR:', error)
    sys.exit(1)
print('PLUGIN VALIDATION PASSED:', json.loads(manifest_path.read_text(encoding='utf-8'))['name'])
