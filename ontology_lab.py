"""Executable, local ontology lessons: RDF, OWL RL, SHACL and fixed SPARQL."""
import time
from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal, URIRef
from owlrl import DeductiveClosure, OWLRL_Semantics
from pyshacl import validate
EX=Namespace('https://example.org/logistics/')
SH=Namespace('http://www.w3.org/ns/shacl#')
PREFIX='''@prefix ex: <https://example.org/logistics/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
'''
SCHEMA=PREFIX+'''ex:Company a owl:Class .
ex:SoftwareSystem a owl:Class .
ex:PredictionModel a owl:Class ; rdfs:subClassOf ex:SoftwareSystem .
ex:uses a owl:ObjectProperty ; owl:inverseOf ex:usedBy .
ex:dependsOn a owl:ObjectProperty, owl:TransitiveProperty .
ex:Document a owl:Class .
ex:describes a owl:ObjectProperty .
ex:text a owl:DatatypeProperty .
'''
FACTS=PREFIX+'''ex:물류사 a ex:Company ; ex:uses ex:배차시스템 .
ex:배차시스템 a ex:SoftwareSystem ; ex:dependsOn ex:도착예측모델 .
ex:도착예측모델 a ex:PredictionModel ; ex:dependsOn ex:날씨API .
ex:날씨API a ex:SoftwareSystem .
ex:운영문서 a ex:Document ; ex:describes ex:배차시스템 ;
  ex:text "배차시스템은 도착예측모델의 결과로 배차 순서를 정한다." .
ex:모델문서 a ex:Document ; ex:describes ex:도착예측모델 ;
  ex:text "도착예측모델은 날씨API의 강수량을 입력으로 사용한다." .
'''
DATA=SCHEMA+'\n'+FACTS
SHAPES='''@prefix ex: <https://example.org/logistics/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
ex:CompanyShape a sh:NodeShape ; sh:targetClass ex:Company ;
 sh:property [ sh:path ex:uses ; sh:minCount 1 ; sh:nodeKind sh:IRI ; sh:class ex:SoftwareSystem ;
 sh:message "회사는 SoftwareSystem 개체를 하나 이상 사용해야 합니다." ] .
'''
QUERIES={
 'systems':{'label':'유형 질의: 모든 SoftwareSystem','text':'''PREFIX ex: <https://example.org/logistics/>
SELECT ?system WHERE { ?system a ex:SoftwareSystem } ORDER BY ?system''',
 'explain':'명시된 타입은 배차시스템·날씨API입니다. 추론하면 PredictionModel의 상위 타입을 가진 도착예측모델도 조회됩니다.'},
 'impact':{'label':'영향 질의: 날씨API 의존 시스템','text':'''PREFIX ex: <https://example.org/logistics/>
SELECT ?system WHERE { ?system ex:dependsOn ex:날씨API } ORDER BY ?system''',
 'explain':'추론 OFF에서는 직접 의존하는 도착예측모델만 나옵니다. ON에서는 전이 관계로 배차시스템도 나옵니다. 의존 관계는 장애 원인의 확률적 증명이 아닙니다.'},
 'inverse':{'label':'역관계 질의: 배차시스템 사용자','text':'''PREFIX ex: <https://example.org/logistics/>
SELECT ?company WHERE { ex:배차시스템 ex:usedBy ?company } ORDER BY ?company''',
 'explain':'uses의 inverseOf 선언으로 usedBy 관계를 도출합니다. 원본 데이터에는 usedBy 문장이 없습니다.'}}
QUERY=QUERIES['systems']['text']

def lessons():
    cases=[
      dict(id='types',title='1. 클래스와 개체',goal='상위 타입을 추론해 동일한 SPARQL 결과가 늘어나는지 확인합니다.',facts=FACTS,expected='systems: 추론 OFF 2행, ON 3행. ON에서 도착예측모델이 추가됩니다.',query_id='systems'),
      dict(id='impact',title='2. 전이 관계와 원문 근거',goal='날씨API 의존 경로를 조회하고 두 문서의 근거를 확인합니다.',facts=FACTS,expected='impact: OFF 도착예측모델 1행, ON 배차시스템·도착예측모델 2행.',query_id='impact'),
      dict(id='inverse',title='3. 역관계 생성',goal='uses를 usedBy 방향으로 조회합니다.',facts=FACTS,expected='inverse: OFF 0행, ON 물류사 1행.',query_id='inverse'),
      dict(id='missing',title='4. 필수 관계 누락',goal='회사 개체는 남겨 두고 uses만 삭제합니다. SHACL minCount 실패 위치를 봅니다.',facts=FACTS.replace(' ; ex:uses ex:배차시스템',''),expected='추론 ON/OFF 모두 SHACL 실패. focusNode=물류사, path=uses.',query_id='systems'),
      dict(id='literal',title='5. 개체 대신 문자열',goal='IRI 관계값과 문자열의 차이를 검증합니다.',facts=FACTS.replace('ex:uses ex:배차시스템','ex:uses "배차시스템"'),expected='SHACL 실패. 문자열은 SoftwareSystem 개체 IRI가 아닙니다.',query_id='systems'),
      dict(id='range',title='6. domain/range의 함정',goal='uses의 domain/range 선언을 추가하고 명시 타입이 없는 개체의 타입을 확인합니다.',schema=SCHEMA+'\nex:uses rdfs:domain ex:Company ; rdfs:range ex:SoftwareSystem .',facts=PREFIX+'ex:미등록조직 ex:uses ex:미등록도구 .',expected='OFF SHACL 대상 Company가 없어 통과할 수 있습니다. ON에서는 Company/System 타입을 추론해 통과합니다. domain/range는 입력 거절 규칙이 아닙니다.',query_id='systems')]
    return [dict(schema=SCHEMA,shapes=SHAPES,**c) if 'schema' not in c else dict(shapes=SHAPES,**c) for c in cases]

def run_ontology(data=DATA,shapes=SHAPES,infer=True,query_id='systems',schema=None,facts=None):
    start=time.perf_counter()
    if query_id not in QUERIES: raise ValueError('지원하지 않는 질의입니다.')
    if schema is not None or facts is not None: data=(schema or '')+'\n'+(facts or '')
    if len(data)>18000 or len(shapes)>12000: raise ValueError('Turtle 입력이 너무 큽니다.')
    graph=Graph().parse(data=data,format='turtle'); sg=Graph().parse(data=shapes,format='turtle')
    if len(graph)>700 or len(sg)>300: raise ValueError('실습은 데이터 700개·제약 300개 트리플 이내로 작성하세요.')
    if any(p in {SH.sparql,OWL.imports,SH.js,SH.rule} or str(p).startswith(str(SH)+'js') for g in (graph,sg) for s,p,o in g):
        raise ValueError('이 실습은 로컬 Turtle과 SHACL Core만 지원합니다. imports/SPARQL/JS/rule 제약은 지원하지 않습니다.')
    before=set(graph)
    def short(x):
        if isinstance(x,Literal): return '"'+str(x)+'"'
        for ns,p in [(str(EX),'ex:'),(str(RDF),'rdf:'),(str(RDFS),'rdfs:'),(str(OWL),'owl:')]:
            if str(x).startswith(ns): return str(x).replace(ns,p,1)
        return str(x)
    def row(t): return [short(x) for x in t]
    def select(g):
        return [{str(v):short(r[v]) for v in r.labels if r[v] is not None} for r in g.query(QUERIES[query_id]['text'])]
    before_results=select(graph)
    before_ok,_,_=validate(graph,shacl_graph=sg,inference='none',advanced=False)
    if infer: DeductiveClosure(OWLRL_Semantics).expand(graph)
    conforms,report,report_text=validate(graph,shacl_graph=sg,inference='none',advanced=False)
    domain=lambda t:str(t[0]).startswith(str(EX)) and (str(t[1]).startswith(str(EX)) or (t[1]==RDF.type and str(t[2]).startswith(str(EX))))
    added=sorted((t for t in set(graph)-before if domain(t)),key=str)
    proofs=[]
    for s,p,o in added:
        reasons=[]
        if p==RDF.type:
            for child in graph.objects(s,RDF.type):
                if (s,RDF.type,child) in before and (child,RDFS.subClassOf,o) in graph:
                    reasons.append({'rule':'rdfs:subClassOf','premises':[row((s,RDF.type,child)),row((child,RDFS.subClassOf,o))]})
            for a,rel,b in before:
                if a==s and (rel,RDFS.domain,o) in graph: reasons.append({'rule':'rdfs:domain','premises':[row((a,rel,b)),row((rel,RDFS.domain,o))]})
                if b==s and (rel,RDFS.range,o) in graph: reasons.append({'rule':'rdfs:range','premises':[row((a,rel,b)),row((rel,RDFS.range,o))]})
        else:
            for inv in graph.objects(p,OWL.inverseOf):
                if (o,inv,s) in graph: reasons.append({'rule':'owl:inverseOf','premises':[row((o,inv,s)),row((p,OWL.inverseOf,inv))]})
            for inv in graph.subjects(OWL.inverseOf,p):
                if (o,inv,s) in graph: reasons.append({'rule':'owl:inverseOf','premises':[row((o,inv,s)),row((inv,OWL.inverseOf,p))]})
            if (p,RDF.type,OWL.TransitiveProperty) in graph:
                for mid in graph.objects(s,p):
                    if mid not in (s,o) and (mid,p,o) in graph: reasons.append({'rule':'owl:TransitiveProperty','premises':[row((s,p,mid)),row((mid,p,o))]})
        proofs.append({'triple':row((s,p,o)),'reasons':reasons,'note':'학습용 규칙 설명이며 OWL RL 엔진 전체의 증명 트리는 아닙니다.'})
    violations=[]
    for result in report.subjects(RDF.type,SH.ValidationResult):
        violations.append({k:short(report.value(result,term)) if report.value(result,term) is not None else '' for k,term in [('focus',SH.focusNode),('path',SH.resultPath),('value',SH.value),('constraint',SH.sourceConstraintComponent),('message',SH.resultMessage)]})
    results=select(graph)
    matched={v for r in results for v in r.values()}
    evidence=[]
    for doc in graph.subjects(RDF.type,EX.Document):
        entities=list(graph.objects(doc,EX.describes))
        if any(short(e) in matched for e in entities):
            evidence.append({'document':short(doc),'entities':[short(e) for e in entities],'text':str(graph.value(doc,EX.text) or '')})
    graph_rows=[{'triple':row(t),'inferred':t not in before} for t in sorted(graph,key=str) if domain(t) and t[1]!=EX.text]
    return {'conforms':bool(conforms),'before_conforms':bool(before_ok),'report':report_text,'violations':violations,
      'asserted':[row(t) for t in sorted(before,key=str)],'inferred':[row(t) for t in added],'proofs':proofs,
      'query':QUERIES[query_id]['text'],'query_explain':QUERIES[query_id]['explain'],'results':results,'before_results':before_results,
      'graph':graph_rows,'evidence':evidence,'reasoner':'OWL RL' if infer else '없음','seconds':round(time.perf_counter()-start,3),
      'note':'규칙 추론·SHACL 검증·원문 검색은 별도 단계입니다. SHACL은 현재 그래프를 검사하며 추론 전후 결과가 달라질 수 있습니다. 문서 근거는 describes로 연결한 원문을 조회합니다. LLM 생성은 이 실습에서 실행하지 않습니다.'}
