"""Runnable, transparently simplified GraphRAG teaching engines.

Each method has genuinely different retrieval logic. These are educational
implementations, not the released research systems or paper benchmark replications.
"""
from __future__ import annotations

import base64
import math
import os
import re
import time
import uuid
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from typing import Any

from data import DEFAULT_DOCS, DEMO_TRIPLES, METHODS

METHOD_BY_ID = {m['id']: m for m in METHODS}
STOP = {'그리고','그러나','것으로','대한','에서','때문에','위한','하는','합니다','있다','있으며','서비스','시스템','데이터','질문','기술','문서','모델','사용','통해','관련','어떤','무엇','어떻게','설명해줘','내용','있어','한다','이를','로부터'}


def tokens(text: str) -> set[str]:
    words = re.findall(r'[가-힣]{2,}|[A-Za-z][A-Za-z0-9_-]*|\d+(?:\.\d+)?%?', text.lower())
    clean = {w for w in words if w not in STOP}
    # Character n-grams make inflected Korean phrases easier to match.
    for word in words:
        if len(word) >= 4:
            clean.update(word[j:j+3] for j in range(len(word)-2))
    return clean


def lexical(a: str, b: str) -> float:
    aa, bb = tokens(a), tokens(b)
    if not aa or not bb:
        return 0.0
    overlap = len(aa & bb)
    return min(1.0, overlap / math.sqrt(len(aa) * len(bb)))


def cosine(a: list[float] | None, b: list[float] | None) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x*y for x,y in zip(a,b))
    norm = math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(y*y for y in b))
    return max(0.0, dot / norm) if norm else 0.0


def parse_sentences(s: str) -> list[str]:
    return [p.strip() for p in re.split(r'(?<=[.!?])\s+|\n+', s.strip()) if p.strip()]


def get_openai():
    key = os.getenv('OPENAI_API_KEY','').strip()
    if not key:
        raise RuntimeError('OPENAI_API_KEY가 없습니다. 프로젝트 루트의 .env 파일에 넣고 서버를 다시 실행하세요.')
    from openai import OpenAI
    return OpenAI(api_key=key, timeout=60.0, max_retries=1)


def chat_model() -> str:
    return os.getenv('OPENAI_CHAT_MODEL', 'gpt-6-luna')


def chat_params() -> dict:
    model = chat_model()
    # GPT-6 Luna accepts Chat Completions with reasoning_effort='none'.
    # Avoid temperature/top_p with reasoning models.
    return {'model': model, **({'reasoning_effort': 'none'} if model.startswith('gpt-6') else {})}


def completion(system: str, user: str, json_mode: bool = False, limit: int = 1200) -> str:
    client = get_openai()
    kwargs = {**chat_params(),
              'messages': [{'role':'system','content':system}, {'role':'user','content':user}],
              'max_completion_tokens':limit}
    if json_mode:
        kwargs['response_format'] = {'type':'json_object'}
    result = client.chat.completions.create(**kwargs)
    return (result.choices[0].message.content or '').strip()


def embed_many(items: list[str]) -> list[list[float]]:
    if not items:
        return []
    result = get_openai().embeddings.create(model=os.getenv('OPENAI_EMBED_MODEL','text-embedding-3-small'), input=[s[:7000] for s in items])
    return [item.embedding for item in sorted(result.data, key=lambda x:x.index)]


def caption_image(url: str) -> str:
    if not url.startswith(('data:image/png;base64,', 'data:image/jpeg;base64,','data:image/webp;base64,')):
        raise ValueError('이미지는 PNG / JPEG / WEBP 형식만 지원합니다.')
    if len(url) > 2_800_000:
        raise ValueError('이미지는 약 2MB 이하로 업로드하세요.')
    response = get_openai().chat.completions.create(
        **({**chat_params(), 'model': os.getenv('OPENAI_VISION_MODEL',chat_model())}),
        messages=[{'role':'system','content':'다이어그램 또는 이미지에 보이는 사실만 한국어로 상세히 기술하라. 표시된 단어, 연결 화살표, 표 수치에 주목하라. 보이지 않는 사실은 추측하지 마라.'},
                  {'role':'user','content':[{'type':'text','text':'이 이미지에서 검색 가능한 사실과 관계를 설명해줘.'},
                                            {'type':'image_url','image_url':{'url':url,'detail':'high'}}]}],
        max_completion_tokens=800)
    return (response.choices[0].message.content or '').strip()


def heuristic_triples(docs: list[dict]) -> list[dict]:
    """Offline custom corpus: co-occurrence graph, explicitly NOT semantic KG."""
    result=[]
    for d in docs:
        for sent in parse_sentences(d['text']):
            candidates = list(dict.fromkeys(re.findall(r'[A-Za-z][A-Za-z0-9_-]{2,}|[가-힣]{3,}', sent)))
            candidates = [x for x in candidates if x.lower() not in STOP]
            for a,b in zip(candidates, candidates[1:4]):
                if a != b:
                    result.append({'source':a,'relation':'같은 문장에 등장','target':b,'doc_id':d['id']})
    return result[:150]


def extract_live(docs: list[dict]) -> tuple[list[dict],list[dict]]:
    import json
    prompt = '\n'.join(f"[{d['id']}] {d['text']}" for d in docs)
    raw = completion(
        'You build a grounded graph index. Return ONLY a JSON object with keys "triples" and "atoms". '
        'triples elements contain source, relation, target, doc_id. atoms elements contain text, doc_id. '
        'Use original Korean names, keep negations and numbers; make at most 5 triples and 4 self-contained atomic facts per document. '
        'Every element must be explicitly supported by the corresponding document. No speculation.',
        prompt, json_mode=True, limit=4000)
    parsed = json.loads(raw)
    allowed = {d['id'] for d in docs}
    triples=[]
    for t in parsed.get('triples', [])[:120]:
        if isinstance(t,dict) and str(t.get('doc_id','')) in allowed and all(str(t.get(k,'')).strip() for k in ('source','target','relation')):
            triples.append({k:str(t[k])[:100] for k in ('source','target','relation','doc_id')})
    atoms=[]
    for a in parsed.get('atoms',[])[:100]:
        if isinstance(a,dict) and str(a.get('doc_id','')) in allowed and str(a.get('text','')).strip():
            atoms.append({'id':f'A{len(atoms)+1}','doc_id':str(a['doc_id']),'text':str(a['text'])[:550]})
    return triples, atoms


def group_docs(docs: list[dict]) -> list[dict]:
    groups={}
    if all(d.get('topic') for d in docs):
        for d in docs:
            groups.setdefault(d['topic'],[]).append(d)
    else:
        # Lightweight deterministic semantic/lexical greedy grouping; not Leiden.
        group_list=[]
        for doc in docs:
            if not group_list:
                group_list.append([doc]); continue
            scores=[max(lexical(doc['text'], other['text']) for other in g) for g in group_list]
            best=max(range(len(scores)), key=lambda i:scores[i])
            if len(group_list)<min(3,max(1,math.ceil(len(docs)/2))) and scores[best]<0.17:
                group_list.append([doc])
            else:
                group_list[best].append(doc)
        groups={f'Topic {i+1}':g for i,g in enumerate(group_list)}
    out=[]
    for i,(topic,children) in enumerate(groups.items()):
        sentences = [s for d in children for s in parse_sentences(d['text'])]
        preview = ' '.join(sentences[:min(5,len(sentences))])[:850]
        out.append({'id':f'C{i+1}','title':topic.replace('_',' ').title(),'doc_ids':[d['id'] for d in children], 'text':preview})
    return out


@dataclass
class Index:
    id: str
    mode: str
    docs: list[dict]
    triples: list[dict]
    atoms: list[dict]
    groups: list[dict]
    vectors: dict[str,list[float]] = field(default_factory=dict)
    stats: dict = field(default_factory=dict)

    @property
    def entities(self) -> list[str]:
        return sorted({t['source'] for t in self.triples} | {t['target'] for t in self.triples})

    def lookup(self, identifier: str) -> str:
        if identifier.startswith('D'):
            return next((d['text'] for d in self.docs if d['id']==identifier),'')
        if identifier.startswith('C'):
            return next((g['text'] for g in self.groups if g['id']==identifier),'')
        if identifier.startswith('A'):
            return next((a['text'] for a in self.atoms if a['id']==identifier),'')
        if identifier.startswith('E:'):
            return identifier[2:]
        return ''


def create_index(mode: str, docs: list[dict], use_sample: bool = False, image_data_url: str | None = None) -> Index:
    t0=time.perf_counter()
    if mode not in ('live','offline'):
        raise ValueError('mode는 live 또는 offline 이어야 합니다.')
    clean=[]
    for i,d in enumerate(docs[:20]):
        content = str(d.get('text','')).strip()[:6000]
        if content:
            clean.append({'id':f'D{len(clean)+1}','title':str(d.get('title',f'문서 {i+1}'))[:100],
                          'text':content, 'topic': d.get('topic','') if use_sample else ''})
    if use_sample:
        clean=[dict(d) for d in DEFAULT_DOCS]
    if not clean:
        raise ValueError('먼저 하나 이상의 문서를 입력하세요.')
    if sum(len(d['text']) for d in clean)>45000:
        raise ValueError('전체 문서는 45,000자를 넘을 수 없습니다.')
    if image_data_url:
        if mode == 'live':
            description=caption_image(image_data_url)
            clean.append({'id':f'D{len(clean)+1}','title':'업로드 이미지 · Vision 해석','text':'[이미지에서 관찰한 내용] '+description,'topic':'image'})
        else:
            clean.append({'id':f'D{len(clean)+1}','title':'업로드 이미지 (Offline 미해석)','text':'이미지가 첨부되었습니다. 실제 이미지 내용은 Live 모드에서 Vision API로 분석됩니다.','topic':'image'})
    if mode=='live':
        triples, atoms = extract_live(clean)
        if not triples:
            triples=heuristic_triples(clean)
    elif use_sample:
        triples=[{'source':a,'relation':r,'target':b,'doc_id':d} for a,r,b,d in DEMO_TRIPLES]
        atoms=[]
    else:
        triples=heuristic_triples(clean)
        atoms=[]
    if not atoms:
        for d in clean:
            for s in parse_sentences(d['text']):
                atoms.append({'id':f'A{len(atoms)+1}','doc_id':d['id'],'text':s})
    groups=group_docs(clean)
    index=Index(id=str(uuid.uuid4()), mode=mode, docs=clean, triples=triples, atoms=atoms, groups=groups)
    if mode=='live':
        # Real OpenAI vectors. Similarity is hybrid embedding + lexical.
        content=[('D'+d['id'][1:], d['text']) for d in clean]
        content += [(a['id'],a['text']) for a in atoms]
        content += [(g['id'],g['text']) for g in groups]
        content += [('E:'+e,e) for e in index.entities]
        vectors=embed_many([v for k,v in content])
        index.vectors={key:vec for (key,_),vec in zip(content,vectors)}
    index.stats={'documents':len(clean),'entities':len(index.entities),'relations':len(triples),'atoms':len(atoms),
                 'communities':len(groups),'seconds':round(time.perf_counter()-t0,2),
                 'api':'OpenAI API' if mode=='live' else '로컬 알고리즘',
                 'vision':bool(image_data_url and mode=='live')}
    return index


@dataclass
class Retriever:
    index: Index
    query: str
    qvec: list[float] | None

    def score(self, identifier: str, text: str) -> float:
        lex=lexical(self.query,text)
        if self.index.mode=='live':
            sem=cosine(self.qvec,self.index.vectors.get(identifier))
            return 0.72*sem + 0.28*lex
        return lex

    def docs(self) -> list[tuple[str,float]]:
        return sorted([(d['id'],self.score(d['id'],d['text'])) for d in self.index.docs],key=lambda x:x[1],reverse=True)

    def groups(self) -> list[tuple[str,float]]:
        return sorted([(g['id'],self.score(g['id'],g['text'])) for g in self.index.groups],key=lambda x:x[1],reverse=True)

    def atom_scores(self) -> list[tuple[str,float]]:
        return sorted([(a['id'],self.score(a['id'],a['text'])) for a in self.index.atoms],key=lambda x:x[1],reverse=True)

    def entity_scores(self) -> dict[str,float]:
        out={}
        for e in self.index.entities:
            plain=lexical(self.query,e)
            exact=0.92 if e.casefold() in self.query.casefold() else 0
            sem=self.score('E:'+e,e)
            out[e]=max(exact,plain,sem*0.75)
        return out


def ppr(adjacency: dict[str,set[str]], seeds: dict[str,float], damping: float=.82, steps: int=22) -> dict[str,float]:
    nodes=set(adjacency)|set(seeds)
    if not nodes: return {}
    vals={n:max(0.,seeds.get(n,0.)) for n in nodes}
    total=sum(vals.values())
    if total==0:
        vals={n:1/len(nodes) for n in nodes}
    else:
        vals={n: v/total for n,v in vals.items()}
    init=dict(vals)
    for _ in range(steps):
        nextvals={n:(1-damping)*init[n] for n in nodes}
        leak=0.0
        for node in nodes:
            nei=adjacency.get(node,set()) & nodes
            if nei:
                for target in nei: nextvals[target]+=damping*vals[node]/len(nei)
            else: leak+=damping*vals[node]
        for n in nodes: nextvals[n]+=leak*init[n]
        vals=nextvals
    return vals


def entity_adj(index: Index) -> dict[str,set[str]]:
    adj=defaultdict(set)
    for t in index.triples:
        adj[t['source']].add(t['target']); adj[t['target']].add(t['source'])
    return dict(adj)


def docs_from_entity(index: Index, rank: dict[str,float]) -> list[tuple[str,float]]:
    accum=defaultdict(float)
    for t in index.triples:
        accum[t['doc_id']]+=0.5*(rank.get(t['source'],0)+rank.get(t['target'],0))
    return sorted(accum.items(),key=lambda x:x[1],reverse=True)


def top_entity_seeds(ret: Retriever, limit: int = 4) -> dict[str,float]:
    ents=ret.entity_scores()
    ranked=sorted(ents.items(),key=lambda x:x[1],reverse=True)
    positive=[(e,s) for e,s in ranked if s>.07]
    if not positive:
        # Doc-derived fallback for indirect phrasing.
        docids={did for did,_ in ret.docs()[:2]}
        positive=[(e,.2) for t in ret.index.triples if t['doc_id'] in docids for e in (t['source'],t['target'])]
    return dict(positive[:limit])


def evidence(index: Index, ids: list[str], scores: dict[str,float] | None = None, limit: int = 5) -> list[dict]:
    seen=set(); out=[]
    for k in ids:
        if k in seen: continue
        seen.add(k)
        text=index.lookup(k)
        if not text: continue
        typ='document' if k.startswith('D') else 'community' if k.startswith('C') else 'atom' if k.startswith('A') else 'entity'
        title=next((d['title'] for d in index.docs if d['id']==k),None) if typ=='document' else None
        if typ=='community': title=next((g['title'] for g in index.groups if g['id']==k),None)
        out.append({'id':k,'type':typ,'title':title or k, 'text':text,'score':round((scores or {}).get(k,0),3)})
        if len(out)>=limit: break
    return out


def retrieve(index: Index, query: str, method: str, qvec: list[float] | None = None) -> dict:
    if method not in METHOD_BY_ID:
        raise ValueError('지원하지 않는 Method입니다.')
    ret=Retriever(index,query,qvec)
    docs=ret.docs(); doc_score=dict(docs)
    groups=ret.groups(); group_score=dict(groups)
    selected=[]; trace=[]; focus=[]; reason=''
    scores=dict(doc_score)
    if method=='baseline':
        selected=[d for d,_ in docs[:4]]
        trace=['Query → Chunk 유사도 계산','관련 Chunk Top-4 선택','Graph 이동 없이 직접 근거 구성']
    elif method=='raptor':
        winners=groups[:2]
        children=[d for g,_ in winners for d in next((gg['doc_ids'] for gg in index.groups if gg['id']==g),[])]
        selected=[g for g,_ in winners]+ sorted(children,key=lambda k:doc_score.get(k,0),reverse=True)[:3]
        scores.update(group_score); focus=[g for g,_ in winners]
        trace=['Chunk를 문서군으로 묶어 상위 요약 노드 생성','Query에 가까운 요약 노드 최대 2개 선택','요약 하위의 원문 근거를 펼쳐 결합']
    elif method=='graphrag':
        # Global queries inspect every compact report; local ones top reports.
        global_query=any(w in query for w in ('전체','전반','핵심','전략','쟁점','공통','요약','주제','트렌드'))
        winners=groups if global_query else groups[:2]
        selected=[g for g,_ in winners]+[d for d,_ in docs if any(d in g['doc_ids'] for g in index.groups if g['id'] in {x for x,_ in winners})][:2]
        scores.update(group_score);focus=[g for g,_ in winners]
        trace=['엔티티 관계에서 Community 단위를 구성 (교육용 클러스터)','각 Community를 짧은 Report로 정리',f'{len(winners)}개 Community Report의 질문 관련 내용을 합성']
    elif method=='lightrag':
        seeds=top_entity_seeds(ret,3)
        related=[t for t in index.triples if t['source'] in seeds or t['target'] in seeds]
        edge_scores={t['doc_id']:max(seeds.get(t['source'],0),seeds.get(t['target'],0)) for t in related}
        ranked=sorted(edge_scores,key=lambda d:edge_scores[d]+0.2*doc_score.get(d,0),reverse=True)
        selected=ranked[:4] or [d for d,_ in docs[:4]]
        focus=list(seeds)
        trace=['Low-level: 질문 엔티티 검색','High-level: 관련 엔티티의 Relation 확장','Entity + Relation에 연결된 원문 수집']
    elif method=='hipporag':
        seeds=top_entity_seeds(ret)
        rank=ppr(entity_adj(index),seeds)
        ranked=docs_from_entity(index,rank)
        selected=[d for d,_ in ranked[:4]] or [d for d,_ in docs[:4]]
        focus=[e for e,_ in sorted(rank.items(),key=lambda x:x[1],reverse=True)[:9]]
        scores.update(dict(ranked))
        trace=['Query entity seed: '+(', '.join(seeds) if seeds else 'fallback'),'Knowledge Graph에서 Personalized PageRank 22회 반복','활성화된 엔티티가 연결된 Passage 재정렬']
    elif method=='hipporag2':
        seeds=top_entity_seeds(ret)
        recall_docs={d for d,_ in docs[:3]}
        for t in index.triples:
            if t['doc_id'] in recall_docs:
                seeds[t['source']]=seeds.get(t['source'],0)+0.18
                seeds[t['target']]=seeds.get(t['target'],0)+0.18
        rank=ppr(entity_adj(index),seeds)
        spread=dict(docs_from_entity(index,rank))
        combined={d:0.58*spread.get(d,0)+0.42*doc_score.get(d,0) for d in doc_score}
        selected=sorted(combined,key=combined.get,reverse=True)[:4]
        focus=[e for e,_ in sorted(rank.items(),key=lambda x:x[1],reverse=True)[:9]]
        scores.update(combined)
        trace=['Recognition: 질문과 비슷한 Passage 3개 검색','Passage 연관 phrase를 seed로 추가','Phrase/Passage 혼합 신호로 PPR 실행']
    elif method=='archrag':
        winners=[g for g,_ in groups[:2]]
        children=[d for g in index.groups if g['id'] in winners for d in g['doc_ids']]
        selected=winners+sorted(children,key=lambda d:doc_score.get(d,0),reverse=True)[:3]
        scores.update(group_score); focus=winners
        trace=['Coarse-level: 상위 Community 유사도 탐색','Top 2 커뮤니티만 하위로 탐색 (계층식 후보 제한)','Fine-level: 해당 원문만 추가 검색 (C-HNSW는 사용하지 않음)']
    elif method=='linearrag':
        adj=defaultdict(set)
        for t in index.triples:
            for ent in (t['source'],t['target']):
                ek='E:'+ent
                adj[ek].add(t['doc_id']);adj[t['doc_id']].add(ek)
        seeds={'E:'+e:val for e,val in top_entity_seeds(ret).items()}
        for d,val in docs[:2]:seeds[d]=seeds.get(d,0)+0.15*val
        ranks=ppr(dict(adj),seeds)
        selected=sorted((d['id'] for d in index.docs),key=lambda k:ranks.get(k,0),reverse=True)[:4]
        focus=[n[2:] for n,_ in sorted(ranks.items(),key=lambda x:x[1],reverse=True) if n.startswith('E:')][:8]
        scores.update({d:ranks.get(d,0) for d in selected})
        trace=['관계 label을 무시하고 Entity–Passage 링크만 구성','Relation-free 이분 그래프 위 PPR','활성화된 Passage를 근거로 선택']
    elif method=='atomicrag':
        atomic=ret.atom_scores()
        selected=[a for a,_ in atomic[:5]]
        scores.update(dict(atomic));focus=[a for a,_ in atomic[:5]]
        trace=['각 문장을 self-contained Knowledge Atom으로 분리','질문–Atom 유사도 계산','토큰 예산이 작은 5개 사실만 전달']
    elif method=='minirag':
        adj=entity_adj(index)
        seeds=list(top_entity_seeds(ret,2))
        targets=[e for e,s in sorted(ret.entity_scores().items(),key=lambda x:x[1],reverse=True)[2:7] if s>0.06]
        found=[]
        for start in seeds[:2]:
            queue=deque([[start]]); visited={start}
            while queue:
                path=queue.popleft()
                if len(path)>4:continue
                if path[-1] in targets and len(path)>1:
                    found=path;break
                for nei in adj.get(path[-1],set()):
                    if nei not in visited:
                        visited.add(nei);queue.append(path+[nei])
            if found:break
        focus=found or seeds
        linked=[t['doc_id'] for t in index.triples if (t['source'] in focus or t['target'] in focus)]
        selected=list(dict.fromkeys(linked))[:3] or [d for d,_ in docs[:3]]
        trace=['질문 엔티티 노드 시작: '+(', '.join(seeds) or '없음'),
               '최단 1~3 hop 연결 경로: '+(' → '.join(found) if found else '직접 인접 확장'),
               '작은 컨텍스트: 경로에 걸친 원문만 전달']
    elif method=='gfmrag':
        adj=entity_adj(index); init=ret.entity_scores()
        denom=max(init.values(),default=1) or 1
        initial={e:s/denom for e,s in init.items()}
        h=initial.copy()
        for _ in range(2):
            h={node:0.58*initial.get(node,0)+0.42*(sum(h.get(n,0) for n in neigh)/max(len(neigh),1)) for node,neigh in adj.items()}
        ranked=docs_from_entity(index,h)
        selected=[d for d,_ in ranked[:4]] or [d for d,_ in docs[:4]]
        scores.update(dict(ranked));focus=[e for e,_ in sorted(h.items(),key=lambda x:x[1],reverse=True)[:9]]
        trace=['초기 Entity relevance: 질의 텍스트와 유사도','2회 이웃 메시지 전파 (고정 가중치, 비학습)','Node activation에서 문서 근거 투영 — GNN 학습 불포함']
    elif method=='greasoner':
        ent=sorted(ret.entity_scores().items(),key=lambda x:x[1],reverse=True)[:3]
        attrs=ret.atom_scores()[:2]
        winner_groups=groups[:1]
        selected=[g for g,_ in winner_groups]+[a for a,_ in attrs]+[d for d,_ in docs[:2]]
        scores.update(group_score); scores.update(dict(attrs))
        focus=[e for e,_ in ent]+[g for g,_ in winner_groups]
        trace=['QuadGraph 레이어: Entity / Attribute(atom) / Document / Community','각 레이어를 개별 질의 관련성으로 조회','레이어별 상위 evidence 결합 (학습된 relevance prediction 아님)']
    elif method=='raganything':
        multimodal=[d for d in index.docs if '이미지' in d['title'] or '다이어그램' in d['title']]
        selected=[d['id'] for d in multimodal[:2]]+[d for d,_ in docs[:3]]
        focus=['멀티모달 이미지/다이어그램','문서 연결']
        trace=['Vision 모드에서 이미지→텍스트 설명 인덱싱 (인덱싱 단계)','Image 설명과 Document를 같은 검색 공간에서 검색','가장 관련 있는 텍스트/이미지 근거를 종합']
    elif method=='whenuse':
        globalq=any(w in query for w in ('전체','전반','핵심','전략','쟁점','공통','요약','주제','트렌드'))
        multiq=any(w in query for w in ('경로','과정','연결','어떤 관계','이유','원인','거쳐','어떻게','부터','영향'))
        routed='graphrag' if globalq else 'hipporag2' if multiq else 'baseline'
        inner=retrieve(index,query,routed,qvec)
        inner['trace']=['Query 진단: '+('Global' if globalq else 'Multi-hop' if multiq else 'Factoid'),f'선택 검색기: {METHOD_BY_ID[routed]["name"]}']+inner['trace']
        inner['route']=routed
        inner['reason']='Global 요약 조건' if globalq else '여러 근거 연결 조건' if multiq else '직접 사실 확인 조건'
        inner['method']='whenuse'
        return inner

    ev=evidence(index,selected,scores,limit=5)
    return {'method':method,'evidence':ev,'trace':trace,'focus':focus,'route':None,'reason':reason}


def offline_answer(result: dict, query: str) -> str:
    ev=result.get('evidence',[])
    if not ev: return '현재 질문에 연결되는 근거를 찾지 못했습니다.'
    sentences=[]
    for item in ev[:4]:
        first=parse_sentences(item['text'])
        if first: sentences.append(f"[{item['id']}] "+' '.join(first[:2]))
    return 'OFFLINE · 검색된 근거 미리보기 (LLM 생성 답변이 아닙니다)\n\n'+'\n\n'.join(sentences)


def answer_live(result: dict, query: str) -> str:
    context='\n\n'.join(f"[{e['id']}] {e['text']}" for e in result['evidence'])
    if not context:
        return '관련 근거를 찾지 못했습니다.'
    return completion(
        '너는 GraphRAG 기술 교류회용 검증 가능한 Q&A 어시스턴트다. '
        '주어진 evidence에 근거한 짧고 명확한 한국어 답변을 만들어라. '
        '원문에 없는 인과관계는 추측하지 마라. 부정문을 보존하라. '
        '각 핵심 주장 끝에 반드시 [D1] 또는 [A3], [C1] 형식의 실제 evidence ID를 달아라. '
        '근거가 부족하면 그 한계를 직접 말하라. 원문 Community/Atom 요약에 있는 수치가 원문과 충돌하면 원문을 우선한다.',
        f'질문: {query}\n\n검색 근거:\n{context}')


def answer(index: Index, method: str, query: str) -> dict:
    if not query.strip() or len(query)>1200:
        raise ValueError('질문은 1~1,200자로 입력하세요.')
    t0=time.perf_counter()
    qvec=embed_many([query])[0] if index.mode=='live' else None
    retrieved=retrieve(index,query,method,qvec)
    retrieved['answer']=answer_live(retrieved,query) if index.mode=='live' else offline_answer(retrieved,query)
    retrieved['metrics']={'seconds':round(time.perf_counter()-t0,2),'evidence_count':len(retrieved['evidence']),
                          'mode':index.mode, 'answer_kind':'generated' if index.mode=='live' else 'retrieved-preview'}
    return retrieved


def graph_payload(index: Index, limit=46) -> dict:
    counts=Counter()
    for t in index.triples:
        counts[t['source']]+=1;counts[t['target']]+=1
    top={e for e,_ in counts.most_common(limit)}
    nodes=[{'id':e,'label':e,'type':'entity','weight':counts[e]} for e in top]
    edges=[{'source':t['source'],'target':t['target'],'label':t['relation'],'doc_id':t['doc_id']} for t in index.triples if t['source'] in top and t['target'] in top]
    return {'nodes':nodes,'edges':edges[:95]}


def stream_answer(index: Index, method: str, query: str):
    """Stream answer tokens AFTER one real retrieval; never fabricates LLM deltas."""
    if not query.strip() or len(query) > 1200:
        raise ValueError('질문은 1~1,200자로 입력하세요.')
    start = time.perf_counter()
    qvec = embed_many([query])[0] if index.mode == 'live' else None
    result = retrieve(index, query, method, qvec)
    result['metrics'] = {'seconds': round(time.perf_counter()-start, 2),
                         'evidence_count':len(result['evidence']),
                         'mode':index.mode,
                         'answer_kind':'generated' if index.mode=='live' else 'retrieved-preview'}
    yield ('retrieval', result)
    if index.mode != 'live':
        yield ('delta', {'text':offline_answer(result, query)})
        yield ('done', {'seconds':round(time.perf_counter()-start,2),'mode':index.mode})
        return
    context = '\n\n'.join(f"[{e['id']}] {e['text']}" for e in result['evidence'])
    if not context:
        yield ('delta', {'text':'관련 근거를 찾지 못했습니다.'})
        yield ('done', {'seconds':round(time.perf_counter()-start,2),'mode':index.mode})
        return
    client = get_openai()
    chunks = client.chat.completions.create(
        **chat_params(),
        messages=[{'role':'system','content':(
            '너는 GraphRAG 기술 교류회용 Q&A 어시스턴트다. 반드시 제공한 근거에서만 대답하라. '
            '근거 없으면 모른다고 말하라. 수치·부정문을 보존하라. 모든 주장은 [D1] [A1] [C1] 형식 근거 ID 표시. '
            '질문에 대한 한국어 답변을 간결하고 구조적으로 스트리밍하라.')},
            {'role':'user','content':f'질문: {query}\n\n근거:\n{context}'}],
        stream=True, max_completion_tokens=1200,
    )
    for part in chunks:
        for choice in getattr(part, 'choices', []):
            fragment = getattr(getattr(choice,'delta',None),'content',None)
            if fragment:
                yield ('delta', {'text': fragment})
    yield ('done',{'seconds':round(time.perf_counter()-start,2),'mode':index.mode})
