from fastapi.testclient import TestClient
from app import app
from ontology_lab import lessons,run_ontology,SCHEMA,SHAPES
client=TestClient(app)

def test_ontology_six_lessons():
    expected={'types':(2,3,True),'impact':(1,2,True),'inverse':(0,1,True),'missing':(2,3,False),'literal':(2,3,False),'range':(0,1,True)}
    for c in lessons():
        r=client.post('/api/ontology/run',json={k:c[k] for k in ['schema','facts','shapes','query_id']})
        assert r.status_code==200,r.text
        v=r.json();assert (len(v['before_results']),len(v['results']),v['conforms'])==expected[c['id']]
        assert all(p['reasons'] for p in v['proofs'])
        if c['id']=='impact':
            assert len(v['evidence'])==2
            assert any(p['reasons'][0]['rule']=='owl:TransitiveProperty' for p in v['proofs'])
        if c['id']=='missing':
            assert any(x['focus']=='ex:물류사' and x['path']=='ex:uses' for x in v['violations'])

def test_inference_off_retains_only_asserted_facts():
    c=lessons()[1]
    r=run_ontology(schema=c['schema'],facts=c['facts'],query_id=c['query_id'],infer=False)
    assert len(r['results'])==1
    assert not r['inferred'] and r['results']==r['before_results']

def test_invalid_turtle_and_unapproved_queries():
    for payload in [{'schema':'bad turtle','facts':'','shapes':SHAPES},{'schema':SCHEMA,'facts':'','shapes':SHAPES,'query_id':'remote'}]:
        assert client.post('/api/ontology/run',json=payload).status_code==400

def test_shapes_do_not_execute_remote_sparql():
    shapes='@prefix sh: <http://www.w3.org/ns/shacl#> . <urn:s> sh:sparql <urn:q> .'
    assert client.post('/api/ontology/run',json={'schema':SCHEMA,'facts':'','shapes':shapes}).status_code==400

def test_workshop_presentation_available():
    ex=client.get('/api/ontology/example').json();assert len(ex['lessons'])==6
    data=client.get('/api/bootstrap').json();assert len(data['workshop'])==59
    assert all(x['sources'] and x['notes'] for x in data['workshop'])
