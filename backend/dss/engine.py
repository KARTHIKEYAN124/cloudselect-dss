import math
from copy import deepcopy

CRITERIA = {'cost': 'Monthly infrastructure cost', 'security': 'Security controls assessment', 'scalability': 'Scaling flexibility assessment', 'performance': 'Illustrative workload suitability; not a benchmark', 'management': 'Operational simplicity assessment'}
DEFAULT = dict(workload='web_application', budget_eur=100, min_vcpu=2, min_ram_gib=8, storage_gb=100, hours=730, egress_gb=100, region='europe', required_security=[], weights=dict(cost=30, security=25, scalability=20, performance=15, management=10))

def validate(raw):
    if not isinstance(raw, dict):
        raise ValueError('Request must be a JSON object')
    u = deepcopy(DEFAULT)
    u.update(raw)
    for key, low, high in [('budget_eur', 0, 1000000), ('min_vcpu', 1, 1024), ('min_ram_gib', 1, 10000), ('storage_gb', 1, 65536), ('hours', 1, 744), ('egress_gb', 0, 1000000)]:
        v = u[key]
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or not low <= v <= high:
            raise ValueError(f'{key} must be a finite number between {low} and {high}')
    if u['workload'] != 'web_application' or u['region'] not in ['europe', 'us', 'asia']:
        raise ValueError('Unsupported workload or region')
    if not isinstance(u['required_security'], list) or any(x not in ['encryption_at_rest', 'iam', 'customer_managed_keys'] for x in u['required_security']):
        raise ValueError('Unknown security capability')
    w = u['weights']
    if not isinstance(w, dict) or set(w) != set(CRITERIA):
        raise ValueError('Provide all five criterion weights')
    if any(isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v) or v < 0 for v in w.values()) or not math.isfinite(sum(w.values())) or sum(w.values()) <= 0:
        raise ValueError('Weights must be non-negative with a positive finite total')
    total = sum(w.values())
    u['weights'] = {k: v / total for k, v in w.items()}
    return u

def evaluate(records, raw):
    u = validate(raw)
    results = []
    for record in records:
        r = deepcopy(record)
        costs = dict(compute=round(r['hourly_eur'] * u['hours'], 2), storage=round(r['storage_eur_gb'] * u['storage_gb'], 2), network=round(r['egress_eur_gb'] * u['egress_gb'], 2))
        total = round(sum(costs.values()), 2)
        reasons = []
        if total > u['budget_eur']: reasons.append('Exceeds monthly budget')
        if r['vcpu'] < u['min_vcpu']: reasons.append('Insufficient CPU')
        if r['ram_gib'] < u['min_ram_gib']: reasons.append('Insufficient RAM')
        if u['storage_gb'] > r['max_storage_gb']: reasons.append('Storage capacity exceeded')
        if u['region'] not in r['supported_regions']: reasons.append('Region unavailable in dataset')
        for feature in u['required_security']:
            if feature not in r['security_capabilities']: reasons.append(f'No verified dataset evidence for {feature}')
        if any(not isinstance(r['scores'].get(k), (int, float)) or not 1 <= r['scores'][k] <= 5 for k in CRITERIA if k != 'cost'):
            reasons.append('Missing or invalid criterion evidence')
        r.update(cost_breakdown=costs, monthly_cost_eur=total, eligible=not reasons, reasons=reasons, rank=None, weighted_score=None, contributions={})
        results.append(r)
    # Fixed reference population prevents removing an expensive alternative from changing other scores.
    prices = [r['monthly_cost_eur'] for r in results]
    lo, hi = min(prices), max(prices)
    for r in results:
        r['ratings'] = dict(r['scores'], cost=5 if hi == lo else 1 + 4 * (hi - r['monthly_cost_eur']) / (hi - lo))
        if r['eligible']:
            r['contributions'] = {k: u['weights'][k] * r['ratings'][k] for k in CRITERIA}
            r['weighted_score'] = sum(r['contributions'].values())
            best = max(r['contributions'], key=r['contributions'].get)
            r['explanation'] = f'Meets all mandatory requirements. Largest weighted contribution: {best}. Scores reflect the demonstration rubric.'
    ranked = sorted((r for r in results if r['eligible']), key=lambda r: (-r['weighted_score'], r['id']))
    previous = None
    for i, r in enumerate(ranked, 1):
        r['rank'] = previous['rank'] if previous and math.isclose(previous['weighted_score'], r['weighted_score'], abs_tol=1e-9) else i
        previous = r
    excluded = [r for r in results if not r['eligible']]
    return dict(status='evaluated' if ranked else 'no_eligible_configurations', requirements=u, results=ranked + excluded, winners=[r['id'] for r in ranked if r['rank'] == 1], dataset_mode='illustrative', methodology='Weighted sum, 1–5 ratings; cost min-max across all three alternatives; shared ranks for ties.')

def sensitivity(records, raw):
    baseline = evaluate(records, raw)
    cases = []
    for key in CRITERIA:
        u = deepcopy(baseline['requirements'])
        old = u['weights'][key]
        new = min(1, old + .1)
        u['weights'] = {k: (new if k == key else (v * (1-new)/(1-old) if old < 1 else 0)) for k, v in u['weights'].items()}
        result = evaluate(records, u)
        cases.append(dict(criterion=key, weights=u['weights'], winners=result['winners'], changed=result['winners'] != baseline['winners'], results=[dict(id=r['id'], provider=r['provider'], score=r['weighted_score'], rank=r['rank']) for r in result['results']]))
    return dict(baseline=baseline, experiments=cases)
