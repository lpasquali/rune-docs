import json
from pathlib import Path

threshold = 8.8
vex_path = Path('.vex/permanent.openvex.json')
VENDOR_CONSTRAINED = set()
if vex_path.exists():
    import json as _json
    vex_doc = _json.loads(vex_path.read_text(encoding='utf-8'))
    for _stmt in vex_doc.get('statements', []):
        _vuln_name = (_stmt.get('vulnerability') or {}).get('name', '')
        if _vuln_name and _stmt.get('status') in {'affected', 'not_affected'}:
            VENDOR_CONSTRAINED.add(_vuln_name)

findings = []
for f in sorted(Path('sbom').glob('*.json')):
    if not f.exists():
        continue
    data = json.loads(f.read_text(encoding='utf-8'))
    if 'matches' in data:
        for m in data.get('matches', []):
            vuln = m.get('vulnerability', {})
            fixable = ((vuln.get('fix') or {}).get('state', 'unknown') == 'fixed')
            score = 0.0
            for c in vuln.get('cvss', []) or []:
                score = max(score, float((c.get('metrics') or {}).get('baseScore') or 0.0))
            if score > 0:
                findings.append((vuln.get('id', 'UNKNOWN'), score, fixable))
    elif 'Results' in data:
        for r in data.get('Results', []) or []:
            for v in r.get('Vulnerabilities', []) or []:
                score = 0.0
                for vendor in ('nvd', 'redhat', 'ghsa'):
                    score = max(score, float((((v.get('CVSS') or {}).get(vendor) or {}).get('V3Score')) or 0.0))
                if score > 0:
                    findings.append((v.get('VulnerabilityID', 'UNKNOWN'), score, bool((v.get('FixedVersion') or '').strip())))
above_threshold = [f for f in findings if f[1] > threshold]
blocked = [f for f in above_threshold if f[2] and f[0] not in VENDOR_CONSTRAINED]
if blocked:
    print(f"CVE policy violation: {len(blocked)} high-risk fixable vulnerabilities found (threshold: {threshold})")
    for cve, score, _ in blocked[:5]:
        print(f"  - {cve}: {score}")
    raise SystemExit(1)
else:
    print(
        f"✓ CVE policy passed: {len(findings)} vulnerabilities total, "
        f"{len(above_threshold)} above threshold, "
        f"{len(blocked)} fixable above threshold"
    )
