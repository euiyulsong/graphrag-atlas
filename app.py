"""Same-origin FastAPI server: never sends the OpenAI key to the browser."""
from __future__ import annotations
import json
import os
import base64
import hmac
from collections import OrderedDict
from pathlib import Path
from threading import Lock

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from data import DEFAULT_DOCS, METHODS, SAMPLE_QUESTIONS
from engine import answer, create_index, graph_payload, stream_answer

ROOT=Path(__file__).resolve().parent
RESEARCH=json.loads((ROOT/'research.json').read_text(encoding='utf-8'))
RESEARCH_BY_ID={item['id']:item for item in RESEARCH}
load_dotenv(ROOT/'.env')
app=FastAPI(title='GraphRAG Seminar Studio', docs_url='/api/docs', redoc_url=None)
app.mount('/static', StaticFiles(directory=ROOT/'static'), name='static')
STATES:OrderedDict=OrderedDict()

@app.middleware('http')
async def deploy_auth(request: Request, call_next):
    # Only enabled when DEMO_PASSWORD is set; development remains friction-free.
    password=os.getenv('DEMO_PASSWORD','')
    if os.getenv('RENDER') and not password:
        return Response('Deployment requires DEMO_PASSWORD',status_code=503)
    if request.url.path == '/api/health':
        return await call_next(request)
    if not password:
        return await call_next(request)
    provided=request.headers.get('Authorization','')
    expected='Basic '+base64.b64encode(('seminar:'+password).encode()).decode()
    if not hmac.compare_digest(provided,expected):
        return Response('Authentication required',status_code=401,
                        headers={'WWW-Authenticate':'Basic realm="GraphRAG Seminar"',
                                 'Cache-Control':'no-store'})
    return await call_next(request)

LOCK=Lock()

class Doc(BaseModel):
    title: str = Field(max_length=100)
    text: str = Field(max_length=6000)
    topic: str = ''

class IndexRequest(BaseModel):
    mode: str = Field(pattern='^(offline|live)$')
    use_sample: bool = False
    documents: list[Doc] = Field(default_factory=list, max_length=20)
    image_data_url: str|None = None

class AskRequest(BaseModel):
    index_id: str
    method: str
    question: str = Field(min_length=1,max_length=1200)

class CompareRequest(BaseModel):
    index_id: str
    methods: list[str] = Field(min_length=2, max_length=4)
    question: str = Field(min_length=1,max_length=1200)

@app.get('/')
def home():
    return FileResponse(ROOT/'static'/'index.html')

@app.get('/api/health')
def health():
    return {'ok': True, 'version':'ontology-workshop-connected-2026-10-26'}

@app.get('/api/download/slides')
def download_slides():
    ppt = ROOT/'slides'/'GraphRAG_Atlas_Tech_Seminar.pptx'
    if not ppt.is_file():
        raise HTTPException(404,'발표 자료가 없습니다. python build_slides.py를 실행하세요.')
    return FileResponse(ppt,media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation',
        filename=ppt.name)

@app.get('/api/bootstrap')
def bootstrap():
    return {'methods':METHODS,'research':RESEARCH,'workshop':json.loads((ROOT/'workshop.json').read_text()),'documents':DEFAULT_DOCS,'questions':SAMPLE_QUESTIONS,
            'live_available':bool(os.getenv('OPENAI_API_KEY','').strip()),
            'models':{'chat':os.getenv('OPENAI_CHAT_MODEL','gpt-6-luna'),
                      'embedding':os.getenv('OPENAI_EMBED_MODEL','text-embedding-3-small')},
            'note':'모든 논문은 핵심 아이디어 기반 교육용 축소/근사 구현입니다. 연구용 원본 코드 및 벤치마크 재현이 아닙니다.'}

@app.post('/api/index')
def build(payload:IndexRequest):
    try:
        idx=create_index(payload.mode,[d.model_dump() for d in payload.documents],payload.use_sample,payload.image_data_url)
    except (ValueError,RuntimeError) as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(502,f'인덱싱 중 외부 API 호출이 실패했습니다: {str(exc)[:340]}') from exc
    with LOCK:
        STATES[idx.id]=idx
        while len(STATES)>12:STATES.popitem(last=False)
    return {'index_id':idx.id,'stats':idx.stats,'graph':graph_payload(idx),'steps':idx.audit,
            'documents':[{'id':d['id'],'title':d['title']} for d in idx.docs],
            'groups':[{'id':g['id'],'title':g['title'],'documents':g['doc_ids']} for g in idx.groups]}

def get_idx(idx_id:str):
    with LOCK:
        idx=STATES.get(idx_id)
    if idx is None:
        raise HTTPException(404,'인덱스가 없습니다. 서버 재시작 후에는 다시 인덱싱해주세요.')
    return idx

@app.post('/api/ask')
def ask(payload:AskRequest):
    idx=get_idx(payload.index_id)
    try:
        return answer(idx,payload.method,payload.question)
    except ValueError as exc:
        raise HTTPException(400,str(exc)) from exc
    except Exception as exc:
        raise HTTPException(502,f'검색/답변 도중 API 오류가 발생했습니다: {str(exc)[:340]}') from exc

@app.post('/api/ask/stream')
def ask_stream(payload: AskRequest):
    idx = get_idx(payload.index_id)
    if payload.method not in {m['id'] for m in METHODS}:
        raise HTTPException(400,'지원하지 않는 method입니다.')
    if not payload.question.strip():
        raise HTTPException(400,'질문을 입력하세요.')
    def events():
        try:
            for event, data in stream_answer(idx, payload.method, payload.question):
                yield f"event: {event}\ndata: {json.dumps(data,ensure_ascii=False)}\n\n"
        except Exception as exc:
            yield f"event: error\ndata: {json.dumps({'message':str(exc)[:350]},ensure_ascii=False)}\n\n"
    return StreamingResponse(events(), media_type='text/event-stream',headers={
        'Cache-Control':'no-cache, no-transform','X-Accel-Buffering':'no',
        'X-Content-Type-Options':'nosniff'})

@app.get('/api/research')
def research():
    return RESEARCH

@app.post('/api/compare')
def compare(payload:CompareRequest):
    idx=get_idx(payload.index_id)
    if len(set(payload.methods))!=len(payload.methods):
        raise HTTPException(400,'비교할 방법이 중복됐습니다.')
    try:
        return {'methods':payload.methods,'results':[answer(idx,method,payload.question) for method in payload.methods]}
    except ValueError as exc:
        raise HTTPException(400,str(exc)) from exc
    except Exception as exc:
        raise HTTPException(502,f'방법별 비교에 실패했습니다: {str(exc)[:340]}') from exc

if __name__=='__main__':
    import uvicorn
    uvicorn.run('app:app',host=os.getenv('HOST','127.0.0.1'),port=int(os.getenv('PORT','8000')))


@app.get('/api/ontology/example')
def ontology_example():
    from ontology_lab import DATA,SHAPES,QUERY,SCHEMA,FACTS,QUERIES,lessons
    return {'data':DATA,'shapes':SHAPES,'query':QUERY,'schema':SCHEMA,'facts':FACTS,'queries':QUERIES,'lessons':lessons()}

class OntologyRequest(BaseModel):
    data: str = Field(default="",max_length=18000)
    schema_text: str|None = Field(default=None,alias="schema",max_length=12000)
    facts: str|None = Field(default=None,max_length=12000)
    query_id: str = "systems"
    shapes: str = Field(max_length=12000)
    infer: bool = True

@app.post('/api/ontology/run')
def ontology_run(payload:OntologyRequest):
    from ontology_lab import run_ontology
    try: return run_ontology(payload.data,payload.shapes,payload.infer,payload.query_id,payload.schema_text,payload.facts)
    except Exception as exc: raise HTTPException(400,str(exc)[:240]) from exc
