import json, os

data = json.loads(os.environ['NEEDS_JSON'])
failed = [(k, v.get('result')) for k, v in data.items() if v.get('result') not in ('success', 'skipped')]
for k, v in data.items():
    print(f'{k}: {v.get("result")}')
if failed:
    print('Merge blocked due to failing RuneGate checks:')
    for item in failed:
        print(f'- {item[0]}: {item[1]}')
    raise SystemExit(1)
print('All RuneGate checks passed.')
