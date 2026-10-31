import math
import sys
from copy import deepcopy
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from dss.engine import DEFAULT, evaluate, sensitivity, validate
from dss.repository import load_records

@pytest.fixture
def records(tmp_path): return load_records(tmp_path / 'test.db')

def test_cost_and_manual_weighted_sum(records):
    result = evaluate(records, DEFAULT)
    aws = next(r for r in result['results'] if r['id'] == 'aws')
    assert aws['monthly_cost_eur'] == 86.35
    assert aws['cost_breakdown'] == {'compute':69.35, 'storage':9, 'network':8}
    expected_cost = 1 + 4 * (94.65 - 86.35) / (94.65 - 74.75)
    assert aws['weighted_score'] == pytest.approx(.3 * expected_cost + .25*4 + .2*5 + .15*4 + .1*3)
    assert result['winners'] == ['gcp']

@pytest.mark.parametrize('key,value,reason',[('budget_eur',1,'budget'),('min_vcpu',4,'CPU'),('min_ram_gib',16,'RAM'),('region','us','Region'),('storage_gb',20000,'Storage')])
def test_hard_constraints(records,key,value,reason):
    result=evaluate(records,dict(DEFAULT,**{key:value}))
    assert result['status']=='no_eligible_configurations'
    assert result['winners']==[]
    assert all(r['rank'] is None and r['weighted_score'] is None and any(reason in s for s in r['reasons']) for r in result['results'])

def test_security_evidence(records):
    result=evaluate(records,dict(DEFAULT,required_security=['customer_managed_keys']))
    assert result['winners']==['azure']

@pytest.mark.parametrize('weights',[dict(cost=0,security=0,scalability=0,performance=0,management=0),dict(DEFAULT['weights'],cost=-1),dict(DEFAULT['weights'],cost=math.nan),dict(DEFAULT['weights'],cost=True),{'cost':1}])
def test_invalid_weights(weights):
    with pytest.raises(ValueError): validate(dict(DEFAULT,weights=weights))

def test_normalization_and_sensitivity(records):
    assert sum(validate(DEFAULT)['weights'].values())==pytest.approx(1)
    result=sensitivity(records,DEFAULT)
    assert len(result['experiments'])==5
    for case in result['experiments']:
        assert sum(case['weights'].values())==pytest.approx(1)
        key=case['criterion']
        assert case['weights'][key]==pytest.approx(DEFAULT['weights'][key]/100+.1)
    assert sensitivity(records,dict(DEFAULT,weights=dict(cost=100,security=0,scalability=0,performance=0,management=0)))

def test_missing_score_excluded(records):
    del records[0]['scores']['performance']
    result=evaluate(records,DEFAULT)
    assert not next(r for r in result['results'] if r['id']==records[0]['id'])['eligible']

def test_tied_scores_share_rank(records):
    for r in records: r['scores']['performance']=4
    result=evaluate(records,dict(DEFAULT,weights=dict(cost=0,security=0,scalability=0,performance=1,management=0)))
    assert len(result['winners'])==3
    assert all(r['rank']==1 for r in result['results'])

def test_api_and_scenarios(tmp_path):
    client=create_app(tmp_path/'api.db').test_client()
    assert client.get('/api/health').json['alternatives']==3
    assert client.get('/api/criteria').status_code==200
    assert client.get('/api/alternatives').status_code==200
    assert client.post('/api/evaluate',json={'budget_eur':-1}).status_code==400
    assert client.post('/api/evaluate',json=[]).status_code==400
    for scenario in client.get('/api/scenarios').json:
        response=client.post('/api/compare',json=scenario['requirements'])
        assert response.status_code==200
        assert response.json['winners']==[{'startup':'gcp','security':'azure','growth':'aws'}[scenario['id']]]
    assert client.post('/api/sensitivity',json={}).status_code==200
    assert client.get('/api/unknown').status_code==404
