"""Local RDF/OWL-RL/SHACL exercise. No external ontology fetching."""
import time
from rdflib import Graph, Namespace
from owlrl import DeductiveClosure, OWLRL_Semantics
from pyshacl import validate

DATA='''@prefix ex: <https://example.org/logistics/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
ex:SoftwareSystem a owl:Class .
ex:PredictionModel a owl:Class ; rdfs:subClassOf ex:SoftwareSystem .
ex:Company a owl:Class .
ex:uses a owl:ObjectProperty ; rdfs:domain ex:Company ; rdfs:range ex:SoftwareSystem .
ex:uses owl:inverseOf ex:usedBy .
ex:배송예측모델 a ex:PredictionModel .
ex:고객물류사 a ex:Company ; ex:uses ex:배송예측모델 .
'''
SHAPES='''@prefix ex: <https://example.org/logistics/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
ex:CompanyShape a sh:NodeShape ; sh:targetClass ex:Company ;
  sh:property [ sh:path ex:uses ; sh:minCount 1 ; sh:nodeKind sh:IRI ;
                sh:class ex:SoftwareSystem ] .
'''
QUERY='''PREFIX ex: <https://example.org/logistics/>
SELECT ?company ?system WHERE {
  ?company a ex:Company ; ex:uses ?system .
  ?system a ex:SoftwareSystem .
} ORDER BY ?company ?system'''

def run_ontology(data: str=DATA, shapes: str=SHAPES, infer: bool=True):
    start=time.perf_counter()
    if len(data)>18000 or len(shapes)>12000: raise ValueError('Turtle 입력이 너무 큽니다.')
    graph=Graph().parse(data=data,format='turtle')
    shape_graph=Graph().parse(data=shapes,format='turtle')
    before=set(graph)
    if infer: DeductiveClosure(OWLRL_Semantics).expand(graph)
    conforms, report, report_text=validate(graph,shacl_graph=shape_graph,inference='none',advanced=False)
    ns='https://example.org/logistics/'
    def row(t): return [str(x).replace(ns,'ex:') for x in t]
    added=sorted((t for t in set(graph)-before if str(t[0]).startswith(ns) and str(t[1])!='http://www.w3.org/2002/07/owl#sameAs'),key=str)
    bindings=[{str(v):str(r[v]).replace(ns,'ex:') for v in r.labels if r[v] is not None} for r in graph.query(QUERY)]
    return {'conforms':bool(conforms),'report':report_text,'asserted':[row(t) for t in sorted(before,key=str)],
            'inferred':[row(t) for t in added], 'query':QUERY,'results':bindings,'reasoner':'OWL RL' if infer else '없음',
            'seconds':round(time.perf_counter()-start,3),'note':'RDFS domain/range는 타입 추론에 사용됩니다. 값의 필수 여부와 타입 적합성은 SHACL로 별도 검사합니다. 누락된 사실을 거짓으로 단정하지 않습니다.'}
