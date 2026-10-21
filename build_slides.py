"""Build a research-grounded, presenter-noted GraphRAG seminar deck.
Run: python build_slides.py
No OpenAI key or network access required.
"""
from __future__ import annotations
from pathlib import Path
import json
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR

ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/'research.json').read_text('utf-8'))
from data import METHODS
META={m['id']:m for m in METHODS}
OUT=ROOT/'slides'/'GraphRAG_Atlas_Tech_Seminar.pptx'
OUT.parent.mkdir(exist_ok=True)
P=Presentation();P.slide_width=Inches(13.333);P.slide_height=Inches(7.5)
BLANK=P.slide_layouts[6]
BG='081625';CARD='12263B';CARD2='0F2131';EDGE='284457';TEXT='F4F7F7';MUTED='A8B8C7';MINT='80E0CB';GOLD='F7C27A';LILAC='C4B0F4';CORAL='F0A9A9';BLUE='8AC7F4'
F_KO='Malgun Gothic'

def rgb(s):return RGBColor.from_string(s)
def rect(s,x,y,w,h,fill,stroke=None,radius=False,trans=None):
    sh=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    sh.fill.solid();sh.fill.fore_color.rgb=rgb(fill)
    if stroke:sh.line.color.rgb=rgb(stroke);sh.line.width=Pt(.8)
    else:sh.line.fill.background()
    if radius:
        try:sh.adjustments[0]=0.12
        except Exception: pass
    return sh

def txt(s,x,y,w,h,content,size=16,color=TEXT,bold=False,align=None,link=None,font=F_KO):
    sh=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    tf=sh.text_frame;tf.clear();tf.word_wrap=True
    tf.margin_top=Pt(0);tf.margin_bottom=Pt(0);tf.margin_left=Pt(0);tf.margin_right=Pt(0)
    for j,line in enumerate(str(content).split('\n')):
        p=tf.paragraphs[0] if j==0 else tf.add_paragraph()
        p.text=line;p.font.name=font;p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=rgb(color)
        p.space_after=Pt(5)
        if align is not None:p.alignment=align
        if link:
            for run in p.runs:run.hyperlink.address=link
    return sh

def circle(s,x,y,r,color,stroke=None):
    o=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x-r),Inches(y-r),Inches(r*2),Inches(r*2))
    o.fill.solid();o.fill.fore_color.rgb=rgb(color)
    if stroke:o.line.color.rgb=rgb(stroke)
    else:o.line.fill.background()
    return o

def line(s,x1,y1,x2,y2,c=EDGE,width=1.6):
    o=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x1),Inches(y1),Inches(x2),Inches(y2))
    o.line.color.rgb=rgb(c);o.line.width=Pt(width)
    return o

def notes(slide,text):
    slide.notes_slide.notes_text_frame.text=text

def base(kicker,title,subtitle='',accent=MINT):
    slide=P.slides.add_slide(BLANK)
    rect(slide,0,0,13.333,7.5,BG)
    rect(slide,.0,0,13.333,.08,accent)
    txt(slide,.58,.31,9.8,.27,kicker,10,accent,True)
    txt(slide,.58,.75,12.2,.62,title,28,TEXT,True)
    if subtitle:txt(slide,.59,1.49,12.1,.55,subtitle,12.5,MUTED)
    line(slide,.58,6.98,12.72,6.98,EDGE,.8)
    txt(slide,.61,7.075,6,.22,'GRAPHATLAS     /     TECHNICAL EXCHANGE 2026',9,MUTED)
    txt(slide,12.15,7.075,.5,.23,f'{len(P.slides):02}',10,accent,True,PP_ALIGN.RIGHT)
    return slide

def addlink(slide,label,url,x,y,w=5):
    txt(slide,x,y,w,.22,label,10,MINT,link=url)

def mini_graph(slide,typ,x,y,c=MINT):
    # Purpose-built conceptual motifs, not reproductions of copyrighted paper figures.
    kinds={
    'raptor':([(0.05,1.1),(.65,.70),(1.25,1.1),(.65,.14)],[(0,1),(2,1),(1,3)]),
    'graphrag':([(0.08,.25),(.52,.1),(.45,.7),(.95,.47),(1.35,.2),(1.37,.92)],[(0,1),(0,2),(1,2),(2,3),(3,4),(3,5),(4,5)]),
    'lightrag':([(0.05,.15),(.53,.16),(.3,.90),(1.07,.2),(1.4,.72)],[(0,1),(1,2),(1,3),(3,4)]),
    'hipporag':([(0.08,.60),(.48,.2),(.88,.64),(1.32,.18),(1.4,.93)],[(0,1),(1,2),(2,3),(2,4)]),
    'hipporag2':([(0.07,.2),(.53,.2),(.94,.20),(.4,.95),(1.18,.95)],[(0,1),(1,2),(0,3),(1,3),(1,4),(2,4)]),
    'archrag':([(0,.15),(.5,.15),(1.0,.15),(.25,.78),(.77,.78),(1.3,.78)],[(0,1),(1,2),(0,3),(1,3),(1,4),(2,5),(3,4),(4,5)]),
    'linearrag':([(0,.60),(.45,.15),(.45,1),(1,.45),(1.35,.7)],[(0,1),(0,2),(1,3),(2,3),(3,4)]),
    'atomicrag':([(0,.3),(.55,.15),(1.1,.25),(.22,.95),(.94,.95)],[(0,1),(1,2),(0,3),(1,3),(1,4),(2,4)]),
    'minirag':([(0.07,.62),(.44,.10),(.9,.55),(1.27,.1),(1.35,.99)],[(0,1),(1,2),(2,3),(2,4)]),
    'gfmrag':([(0,.15),(.43,.15),(.86,.15),(.2,.82),(.65,.82),(1.15,.82)],[(0,1),(1,2),(0,3),(1,4),(2,5),(3,4),(4,5)]),
    'greasoner':([(0,.07),(.5,.07),(1,.07),(0,.85),(.5,.85),(1,.85)],[(0,1),(1,2),(0,3),(1,4),(2,5),(3,4),(4,5)]),
    'raganything':([(0,.2),(.42,.12),(.83,.2),(1.2,.15),(.33,.91),(.94,.87)],[(0,4),(1,4),(1,5),(2,5),(3,5),(4,5)]),
    'whenuse':([(0,.6),(.5,.2),(.5,1),(1.25,.2),(1.25,1)],[(0,1),(0,2),(1,3),(2,4)])}
    nodes,edges=kinds.get(typ,kinds['graphrag'])
    for a,b in edges:
        p,q=nodes[a],nodes[b];line(slide,x+p[0],y+p[1],x+q[0],y+q[1],EDGE,2.2)
    for i,(px,py) in enumerate(nodes):circle(slide,x+px,y+py,.102 if i else .14,c if i==0 else ('28465A' if i%2 else '53778A'),c if i==0 else None)

def paper_slide(method_id,phase,idx):
    m=META[method_id];r=next(a for a in DATA if a['id']==method_id)
    stage='INDEXING' if phase=='index' else 'RETRIEVAL'
    acc=BLUE if phase=='index' else MINT
    s=base(f"{idx:02} / 13  •  {m['family'].upper()}  •  {stage}",f"{m['name']}  /  {stage.title()}",m['idea'],acc)
    txt(s,.6,2.11,9,.28,'BUILD THE KNOWLEDGE STRUCTURE' if phase=='index' else 'QUERY-TIME EVIDENCE FLOW',11,acc,True)
    stages=r[phase]
    cardw=2.32;gap=.25
    for i,step in enumerate(stages):
        x=.58+i*(cardw+gap)
        rect(s,x,2.64,cardw,1.35,CARD,EDGE,True)
        txt(s,x+.14,2.81,1,.24,f'{i+1:02} / 05',10,acc,True)
        txt(s,x+.14,3.13,cardw-.28,.73,step,12.2,TEXT,True)
        if i!=len(stages)-1:txt(s,x+cardw+.03,3.17,.19,.36,'→',14,acc,True)
    rect(s,.58,4.30,7.85,1.94,CARD2,EDGE,True)
    txt(s,.82,4.54,6,.28,'CONCRETE SCENARIO / 예시 질문',10,GOLD,True)
    txt(s,.83,4.91,7.2,.55,r['example'],15,TEXT,True)
    txt(s,.83,5.64,7.15,.42,('→ 저장 산출물: '+stages[-1]) if phase=='index' else '→ 최종 생성에는 선택된 Evidence 및 출처 ID 사용',11.3,MUTED)
    rect(s,8.66,4.3,4.08,1.94,'132C3E',EDGE,True)
    txt(s,8.91,4.49,2.85,.30,'STRUCTURE AT A GLANCE',10,acc,True)
    mini_graph(s,method_id,9.09,4.97,acc)
    txt(s,10.98,5.0,1.48,.95,'knowledge\npath',11,MUTED)
    addlink(s,'↗ PAPER  /  arXiv',r['paper'],.68,6.61,2.7)
    addlink(s,'↗ CODE  /  GitHub',r['repo'],3.48,6.61,3.25)
    txt(s,7.65,6.59,4.95,.29,'Educational reconstruction · Not exact reproduction',8.6,MUTED,align=PP_ALIGN.RIGHT)
    spoken=(f"[{m['name']} — {stage}] 약 50~75초 설명.\n"
            f"핵심 문제: {m['idea']}\n"
            f"단계별 순서:\n"+"\n".join(f"  {j+1}. {z}" for j,z in enumerate(stages))+"\n"
            f"발표 예시: {r['example']}\n"
            f"논문 근거·구현 주의점: {r['note']}\n"
            f"장점: {m['fit']}\n한계: {m['limit']}\n"
            f"웹 실습은 교육용 축소 구현: {m['fidelity']}\n"
            f"논문: {r['paper']}\n원 구현: {r['repo']}\n"
            "발표 중 원논문의 공식 파이프라인과 교육용 재구성을 혼동하지 않도록 설명하세요.")
    notes(s,spoken)
    return s

def feature_slide():
    s=base('SEMINAR / OPENING','From Chunks to Knowledge','GraphRAG — 13 Papers, 13 Architectures, 1 Interactive Laboratory',MINT)
    image=ROOT/'static'/'assets'/'knowledge-universe.png'
    if image.exists():s.shapes.add_picture(str(image),Inches(6.0),Inches(2.05),width=Inches(6.75),height=Inches(4.35))
    rect(s,.6,2.16,5.32,3.84,CARD2,EDGE,True)
    txt(s,.88,2.64,4.63,.67,'질문을 해결하는\n최소 지식 단위는?',23,TEXT,True)
    for j,t in enumerate(['Chunk / Summary','Entity / Relation','Passage / Atom','Community / GFM']):
        txt(s,1.00,4.22+j*.36,4,.28,f'{j+1:02}  {t}',13, MINT if j==2 else MUTED)
    txt(s,.72,6.52,10,.26,'Interactive Lab · Graph Trace · Streaming Answers · GPT-6 Luna',11,MINT)
    notes(s,'오프닝 (2분): 오늘은 그래프가 언제 필요한지 판단하고, 인덱싱과 검색을 구분해 13개 논문을 비교합니다. 모든 그림은 발표용 재구성입니다. 현장 데모에서 일부 방법은 논문 그대로가 아닌 proxy 구현입니다.')

def concept_slide():
    s=base('01 / FUNDAMENTALS','Indexing vs. Retrieval','오프라인 준비 비용과 온라인 질의 처리 비용을 분리해서 생각합니다.',BLUE)
    for j,(ttl,items,col) in enumerate([
        ('INDEXING / Offline',['Corpus & parsing','Entity / Atom / Chunk extraction','Graph, vector, community / hierarchy','Persistent indices & provenance'],BLUE),
        ('RETRIEVAL / Online',['User query & grounding','Vector or graph seed selection','Expansion: PPR / path / community','Evidence ranking → Generator'],MINT)]):
        x=.64+j*6.34;rect(s,x,2.2,5.98,3.92,CARD,EDGE,True)
        txt(s,x+.25,2.46,5.4,.35,ttl,17,col,True)
        for i,t in enumerate(items):
            rect(s,x+.24,3.01+i*.65,5.49,.52,CARD2,EDGE,True)
            txt(s,x+.47,3.14+i*.65,4.9,.3,f'{i+1:02}   {t}',12,TEXT)
    txt(s,.79,6.49,11.77,.23,'Same corpus  ·  Same generator  ·  Compare evidence quality, correctness, latency, and indexing cost',11,GOLD)
    notes(s,'Indexing(사전 구축)은 청크·문서 구조화와 KG 추출, community detection, embedding, provenance 저장이 핵심입니다. Retrieval(질의시)은 seed 찾기, graph 확장, 랭킹 및 LLM prompt 구성이 핵심입니다. 인덱싱 비용과 1회 검색 latency를 구분해 평가합니다.')

def context_slide():
    s=base('02 / WHY GRAPHS','One answer across four documents','배송 지연 감소 경로를 알아내려면 분리된 문서의 관계를 조합해야 합니다.',LILAC)
    examples=[('D2','TrafficStream','지연 신호 수집'),('D7','Orion','운영 신호 중계'),('D1','Beacon','추천 의사결정'),('D3','Aurora','배송 지연 감소')]
    for i,(doc,node,detail) in enumerate(examples):
        x=.61+i*3.23;rect(s,x,2.55,2.91,2.15,CARD,EDGE,True);txt(s,x+.24,2.83,2.25,.29,doc,12,LILAC,True)
        txt(s,x+.24,3.25,2.48,.37,node,18,TEXT,True);txt(s,x+.24,3.83,2.49,.34,detail,12,MUTED)
        if i<3:txt(s,x+2.94,3.36,.28,.4,'→',20,MINT,True)
    txt(s,.73,5.23,11,.45,'Question  /  “TrafficStream이 오로라 물류의 지연 감소에 어떻게 기여했나?”',16,TEXT,True)
    txt(s,.74,6.02,11,.38,'Baseline: similarity matching   ·   Graph: entity grounding + multi-hop expansion + passage provenance',12,MUTED)
    notes(s,'예제는 프로젝트 내의 합성 문서입니다. 특정 회사에 관한 실존 사실을 주장하지 않습니다. Vector retrieval은 관련 문서를 찾고 Graph retrieval은 여러 문서 간 경로를 확장할 수 있습니다. 잘못 추출된 edge가 있으면 경로도 틀릴 수 있습니다.')

def map_slide():
    s=base('03 / RESEARCH MAP','Six families + one benchmark','기술의 우열보다 해결하는 검색 실패 유형을 먼저 보세요.',GOLD)
    cats=[('HIERARCHY','RAPTOR · ArchRAG','계층 요약 & coarse-to-fine',BLUE),('COMMUNITY','Microsoft GraphRAG','Global question & report',GOLD),('MEMORY','HippoRAG · HippoRAG2','PPR & long-range links',CORAL),('COST / NOISE','LightRAG · LinearRAG · AtomicRAG · MiniRAG','경량 추출 & 정밀 증거',MINT),('LEARNED','GFM-RAG · G-Reasoner','Pretrained graph learning',LILAC),('MULTIMODAL','RAG-Anything','Cross-modal evidence',BLUE)]
    for i,(name,items,desc,color) in enumerate(cats):
        x=.58+(i%3)*4.25;y=2.22+(i//3)*1.86
        rect(s,x,y,4.03,1.63,CARD,EDGE,True)
        rect(s,x+.20,y+.2,.06,1.17,color)
        txt(s,x+.38,y+.19,3.38,.25,name,11,color,True)
        txt(s,x+.38,y+.56,3.43,.5,items,12,TEXT,True)
        txt(s,x+.38,y+1.24,3.46,.23,desc,9.4,MUTED)
    txt(s,.72,6.30,11,.34,'Benchmark lens: When to use Graphs in RAG?   •   Fact / Multi-hop / Contextual Summary / Creative',11.4,GOLD)
    notes(s,'6가지 설계 흐름과 benchmark를 나눠 소개합니다. When to use Graphs in RAG는 새로운 그래프 검색 알고리즘이 아니라 평가 연구입니다. 논문 소개 자료의 순서는 비교를 돕기 위해 재배열했습니다.')

def decision_slide():
    s=base('04 / PRODUCTION DECISION','Choose by query distribution','GraphRAG 도입 여부는 질문 유형별 베이스라인 대비 개선으로 판단합니다.',MINT)
    rec=[('Single fact','Vector / Hybrid + reranker','일반 검색 대비 정확도·지연 검증'),('Global synthesis','GraphRAG / RAPTOR','커뮤니티 요약 충실도 검증'),('Multi-hop','HippoRAG / LightRAG','graph noise와 supporting fact recall'),('Low-cost build','LinearRAG / MiniRAG','트리플 추출 예산과 품질 균형')]
    for i,(category,method,details) in enumerate(rec):
        x=.62+(i%2)*6.32;y=2.28+(i//2)*1.78
        rect(s,x,y,6.01,1.51,CARD,EDGE,True)
        txt(s,x+.22,y+.16,5.53,.25,category.upper(),10,GOLD,True)
        txt(s,x+.22,y+.52,5.44,.36,method,17,TEXT,True)
        txt(s,x+.22,y+1.05,5.44,.25,details,11.2,MUTED)
    txt(s,.73,6.43,11.7,.23,'Metrics: Recall@k  /  Support Recall  /  Answer Correctness  /  Faithfulness  /  Indexing Cost  /  P95 Latency',10.7,MINT)
    notes(s,'검증 설계: 단일 데이터셋, retrieval top-k, 동일 generator와 동일 질문 집합으로 비교합니다. 정답이 없는 경우에는 abstention / insufficient context 같은 케이스를 별도로 설계합니다. 실제 결과는 실험하지 않았으므로 수치를 제시하지 않습니다.')

def demo_slide():
    s=base('05 / LIVE DEMO','Run → Inspect → Compare','GraphRAG Atlas 웹사이트에서 직접 확인하는 흐름입니다.',MINT)
    steps=[('01','Index','샘플 문서를 인덱싱'),('02','Select','RAPTOR / HippoRAG 선택'),('03','Stream','LLM 토큰 실시간 전송'),('04','Inspect','Graph + citation 확인'),('05','Compare','두 방법을 동일 질문으로 비교')]
    for i,(num,name,detail) in enumerate(steps):
        x=.58+i*2.55
        rect(s,x,2.52,2.31,2.29,CARD,EDGE,True)
        txt(s,x+.17,2.74,1,.26,num,12,MINT,True)
        txt(s,x+.16,3.26,2.02,.39,name,17,TEXT,True)
        txt(s,x+.16,3.86,2,.70,detail,12,MUTED)
    rect(s,.58,5.17,12.18,.91,CARD2,EDGE,True)
    txt(s,.86,5.48,11.5,.33,'http://127.0.0.1:8000   ·   Offline demo first   ·   OpenAI Live only with a fresh server-side key',15,GOLD,True)
    notes(s,'데모 흐름 (10분): 1) 로컬 접속, 2) 예제 인덱스, 3) 질문 하나로 baseline과 hipporag 검색 비교, 4) Trace에서 선택된 근거 확인, 5) Live API로 변경한 뒤 GPT-6 Luna 스트리밍. 원 논문 파이프라인과 교육용 근사를 다시 강조합니다. 외부 노출 키는 절대 스크린에 띄우지 않습니다.')

def closing():
    s=base('Q&A / CLOSING','Build evidence, not just edges.','적절한 Knowledge Unit × Retrieval Operator × Provenance → Better Answers',GOLD)
    txt(s,.79,2.41,10.9,.73,'Graph structures help when the question needs them.',25,TEXT,True)
    txt(s,.81,3.6,10.8,.6,'“어떤 질문을 해결하려는가?”로 시스템 설계를 시작하세요.',20,MINT)
    rect(s,.69,5.04,11.95,.9,CARD,EDGE,True)
    txt(s,.99,5.29,10.8,.32,'Paper & code links: per-paper slide footer  /  All sources: website Research Index',12.5,MUTED)
    notes(s,'Q&A (약 5분): 인덱싱 비용, 그래프 추출 오류, PPR와 shortest path, 커뮤니티 retrieval, GFM 배포 환경 등의 질문을 받습니다. 키를 공개하는 데모는 피하세요. 공식 원 구현 재현은 별도의 dependency와 벤치마크 검증이 필요합니다.')

feature_slide();context_slide();concept_slide();map_slide()
for idx, item in enumerate(DATA,1):
    paper_slide(item['id'],'index',idx)
    paper_slide(item['id'],'query',idx)
decision_slide();demo_slide();closing()
P.save(OUT)
print(f'SAVED: {OUT} | slides={len(P.slides)} | notes={sum(bool(sl.notes_slide.notes_text_frame.text.strip()) for sl in P.slides)}')
