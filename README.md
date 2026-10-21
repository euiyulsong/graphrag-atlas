# ◈ GRAPHATLAS — GraphRAG 기술 교류회 웹사이트

**60분 발표 + 13개 논문별 실습 + OpenAI API 실제 호출 + 그래프/근거 시각화** 를 하나의 실행형 웹사이트로 제공하는 교육용 프로젝트입니다.

자료: [김우영, *GraphRAG의 개념과 최신연구동향*, WikiDocs](https://wikidocs.net/book/19813), 최종 편집 2026-05. 저자 및 논문 개발팀과는 무관하며, 본문의 복제본이 아닌 별도로 작성한 개념 정리·예시·코드입니다. 논문 수치나 평가 결과를 그대로 재현했다고 주장하지 않습니다.

## 1. 빠른 시작

사전 준비: **Python 3.10 이상**, 인터넷 연결(최초 설치 및 Live API 사용 시). Node.js, 별도 프런트엔드 빌드, 데이터베이스가 필요하지 않습니다.

macOS / Linux:

```bash
cd graphrag-seminar
./run.sh
```

Windows (cmd):

```bat
cd graphrag-seminar
run.bat
```

브라우저에서 **http://127.0.0.1:8000** 을 엽니다. 한 번에 백엔드와 웹페이지가 실행됩니다. 오프라인 예제 인덱스는 페이지가 로드되면 자동으로 생성됩니다.

일반 실행:

```bash
python -m pip install -r requirements.txt
python app.py
```

### OpenAI API로 실제 실험

프로젝트 루트에 `.env.example`을 복사해 `.env`를 만들고 OpenAI API 키를 입력합니다.

```bash
cp .env.example .env
# .env의 OPENAI_API_KEY=... 부분에 실제 키 입력
./run.sh
```

Windows의 경우 `.env.example`을 `.env`로 복사한 후 `run.bat`을 다시 실행합니다. **키는 브라우저·HTML·JS에 넣지 않습니다.** FastAPI 서버 환경변수에서만 로드됩니다. `OPENAI_CHAT_MODEL`, `OPENAI_EMBED_MODEL`, `OPENAI_VISION_MODEL`은 `.env`에서 변경 가능합니다.

사이트의 `OpenAI Live` 버튼을 선택하고 `Run pipeline`을 누르면 새 Live 인덱스를 만들고 실제 모델을 호출합니다. **OpenAI API에 요금이 발생합니다.** 최초 Live 인덱싱에는 관계 추출, 임베딩(및 이미지가 있으면 Vision) API 호출이 필요합니다. 각 질문은 임베딩 및 답변 생성 API 호출을 수행합니다. 같은 페이지에서 재질문하면 만들어 둔 인덱스는 재사용합니다.

모델에 대한 접근 권한이나 API 사용 한도가 없으면 Live는 실패 메시지를 보여줍니다. 사용 가능한 모델 ID로 환경변수를 바꿔주세요.

## 2. 기능

- **발표 모드 (P 키):** 19장으로 구성한 약 60분 발표 플로우. 방향키/스페이스로 이동, N 키로 발표자 노트, ESC로 종료. 각 방법별 단계 흐름 그림 및 출처.
- **13개 방법 브라우저:** 계열별 필터, 3단계 파이프라인 SVG, 사용 상황/한계/구현 충실도, 방법 전용 데모 질문.
- **실험실:** 데이터셋 편집·문서 추가, API 모드 전환, 질문 예제, 실제 method별 검색 파이프라인 실행.
- **시각화:** 생성된 Knowledge Graph, 엔티티 활성화, 검색 trace, 원문 `D1`/atom `A1`/community `C1` 근거 및 처리시간.
- **Head-to-head:** 동일 인덱스·질문에 대해 2개 방법의 실제 검색 결과·답변·근거 비교.
- **멀티모달 데모:** PNG/JPG/WebP 이미지를 선택해 Live 모드에서 OpenAI Vision 설명으로 인덱싱. 이미지 추론 없는 Offline 모드에서는 그 한계 명시.
- **오프라인 전용 흐름:** 고정 예제에 대해 준비된 관계로 검색 알고리즘 실제 실행. 커스텀 문서는 단순 동시출현 그래프를 구성. LLM 답변 생성은 하지 않으며 근거 미리보기만 반환.

## 3. 방법론별 실제 구현 범위

| 논문/방법 | 웹사이트에서 실행하는 핵심 아이디어 | 재현의 한계 |
|---|---|---|
| RAPTOR | 계층형 클러스터 요약 + 원문 검색 | 완전한 재귀 트리·원 논문 임베딩 clustering 아님 |
| Microsoft GraphRAG | community 리포트 + 전체/국소 검색 | Leiden 및 원본 map-reduce 체인 아님 |
| LightRAG | entity/relationship dual-level 검색 | 원본의 키워드 프롬프트·전체 인덱스 생략 |
| HippoRAG | 실제 Personalized PageRank(22 iterations) + passage mapping | OpenIE/동의어 처리 축소 |
| HippoRAG 2 | passage 인식 seed + KG PPR 혼합 | 논문 고유 recognition memory 학습 없음 |
| ArchRAG | 상위 커뮤니티 → 관련 하위 문서 검색 | C-HNSW, attributed community detection 미구현 |
| LinearRAG | entity–passage 이분 그래프에서 relation-free PPR | 논문의 Tri-Graph 전체 아님 |
| AtomicRAG | atomic fact 분해/검색 | 원본 atom sieve/graph 알고리즘 일부 생략 |
| MiniRAG | entity shortest path 기반 근거 압축 | SLM 및 원본 heterograph 미구현 |
| GFM-RAG | 고정 가중치 query-conditioned message propagation | **학습된 GNN이 없는 교육용 proxy** |
| G-Reasoner | entity/attribute/document/community 4레이어 retrieval | **QuadGraph GFM을 학습·재현하지 않은 proxy** |
| RAG-Anything | 실제 Vision 캡션 + 텍스트 기반 복합 검색 | 논문 원본 멀티모달 parser 전체 미구현 |
| When to Use Graphs in RAG | 질의 특성 기반 retrieval 전략 라우팅 | 의사결정 데모; 원 논문은 적용 조건 분석 연구 |

**Baseline Vector RAG** 도 포함해 전체 UI에서 14가지 실험 옵션을 제공합니다. `13 methods`는 WikiDocs 수록 연구 13편만 셉니다.

### 공평한 실험에 대한 주의

방법 간 비교는 동일 데이터셋과 동일 질문을 사용하지만, 각 방법이 반환하는 정보 단위(chunks/atoms/reports)가 다르고 context length를 동일하게 정규화하지 않았습니다. 또한 여기에는 정답 라벨 기반 EM, recall, 비용당 성능 평가가 포함되지 않습니다. **이 데모의 결과는 논문 성능 비교나 SOTA 주장으로 쓰면 안 됩니다.** 프로덕션 검증에는 평가 세트, gold evidence, 동일 모델/토큰 예산, indexing/online 비용 측정이 추가로 필요합니다.

## 4. 예제 질의

- Multi-hop: `오로라 물류에서 배송 지연이 줄어든 과정을 교통 데이터 수집부터 설명해줘.`
- Global: `루멘랩의 2026년 핵심 기술 과제와 제품 운영상의 쟁점을 정리해줘.`
- Single fact: `2026년 2분기 Beacon의 MAE는 몇 분이야?`
- Entity path: `TrafficStream과 Prism이 Atlas에서 어떤 경로로 연결되는지 설명해줘.`
- Contradiction guard: `Hermes도 Beacon을 사용하는 거야?`

예제 문서는 **가상 조직과 가상 물류 시스템** 으로 직접 작성했습니다. 성공률·MAE·지연 개선율 등은 예제 문서 속 임의의 설정값이며 실세계 연구/운영 성과가 아닙니다.

## 5. 60분 발표 운영안

| 시간대 | 섹션 |
|---|---|
| 00–03분 | Intro / 목표 |
| 03–08분 | Chunk RAG의 한계 |
| 08–12분 | 6개 연구 흐름 |
| 12–44분 30초 | 13개 연구법 × 약 2분 30초 |
| 44분 30초–54분 30초 | OpenAI 실시간 데모 / Head-to-head |
| 54분 30초–57분 30초 | 프로덕션 의사결정 |
| 57분 30초–60분 | Q&A |

전원 및 인터넷 장애 대비: 행사 전에 기본 예제와 예상 질문을 Offline 모드에서도 진행해 두세요. **Live 모드가 없더라도 검색 및 발표 UI는 계속 동작합니다.** 발표자 노트 N 키로 현재 슬라이드 핵심 설명을 봅니다.

## 6. 테스트

```bash
python -m pip install pytest httpx
python -m pytest -q
```

테스트는 13개 방법의 검색 실행, 비교, 커스텀 데이터, 이미지 제한 안내, 보안 키 누락 처리, OpenAI Live 호출 경로의 mock을 검증합니다. **실제 OpenAI 서비스 응답은 API 키가 없는 환경에서 테스트하지 않았습니다.**

## 7. 구성 및 보안

```text
graphrag-seminar/
├── app.py                   # FastAPI routes; same-origin frontend/API
├── engine.py                # Method-specific retrievers, PPR, LLM integration
├── data.py                  # 13 papers metadata + original teaching corpus
├── static/
│   ├── index.html           # Seminar website
│   ├── styles.css           # Responsive design / presentation mode
│   ├── app.js               # Client interactions / SVG graph renderer
│   └── assets/knowledge-universe.png  # Original AI-generated concept visual
├── tests/test_app.py
├── .env.example
├── requirements.txt
├── run.sh / run.bat
└── README.md
```

이 프로그램은 **로컬 발표용** 입니다. 세션 인덱스는 서버 메모리에만 저장되고 서버 종료 시 사라집니다. 제3자에게 공개하는 웹서비스로 운영하려면 인증, 요청·토큰 크기/횟수 제한, 키 관리, HTTPS, 접근 로깅 최소화, 사용자 파일 보안 검증, persistent vector index, 평가 파이프라인을 별도로 추가해야 합니다. 기본 주소는 `127.0.0.1`만 바인딩합니다.

출처의 저작권은 원저자에게 있습니다. 본 웹사이트의 도형, 시나리오 및 컨셉 이미지는 새로 제작했습니다. 일부 기술 내용의 오류 가능성이 있으므로 학술 발표에서 중요한 주장은 원 논문과 교차 확인하세요.


## GPT-6 Luna 설정 (2026-10-20)

공식 모델 ID: `gpt-6-luna`. 서버의 `.env` 파일에서 `OPENAI_CHAT_MODEL=gpt-6-luna` 를 설정합니다.
GPT-6 Luna Chat Completions는 `reasoning_effort=none`으로 동작하도록 설정되어 있으며,
Streaming은 `/api/ask/stream` 의 SSE `retrieval → delta → done` 이벤트로 전송됩니다.
실제로 사용 중인 모델은 `/api/bootstrap` 의 `models.chat`에서 확인하세요.
**API 키는 .env, OS 환경변수 또는 비밀 관리 서비스에만 입력하세요. 이미 외부에 공유된 키는 회전하세요.**

## 발표 자료

- `slides/GraphRAG_Atlas_Tech_Seminar.pptx`: 논문 13개 × Indexing/Retrieval 아키텍처 두 장 + 도입/평가/실습. 모든 슬라이드에 발표자 노트 포함.
- 슬라이드에서 원 논문 arXiv 및 구현 GitHub로 이동할 수 있습니다.
- PPT 아키텍처는 설명을 위해 재구성한 다이어그램입니다. 공식 논문 그림을 복제하거나 원 구현이 모두 탑재되었다고 주장하지 않습니다.
- 동일 자료는 웹사이트 상단의 **PPTX 다운로드**에서 내려받을 수 있습니다.

## 외부 배포 전 필수 점검

이 프로젝트는 개발용 데모입니다. 로컬 접속만 허용하는 것이 기본입니다. 공개 배포 시 반드시 인증,
사용량 제한 및 요청별 결제 한도, CSRF/CORS 검토, 업로드·SSE 요청 크기 제한, 안전한 secret store를 추가하세요.
인덱스는 프로세스 메모리에 저장되므로 서버 재시작 시 사라집니다.

## Render 배포

1. 새 키를 발급받고 외부에 공유됐던 키는 폐기하세요.
2. GitHub에 이 프로젝트를 **키 없이** 업로드합니다 (`.env`는 .gitignore에 포함).
3. Render에서 **New → Blueprint → GitHub 저장소 연결**을 선택합니다.
4. `OPENAI_API_KEY`와 `DEMO_PASSWORD`를 Render의 Secret Environment Variables로 입력합니다.
5. 빌드 및 배포 완료 후 Render에 표시되는 URL을 열고 `seminar` 사용자 이름 + 설정한 비밀번호로 로그인합니다.

`render.yaml`은 배포 템플릿이며, 배포와 실제 공개 URL 발급은 계정 연결 후 가능합니다.
`DEMO_PASSWORD`가 비어있으면 사이트 인증이 꺼지므로 공개 배포에서는 반드시 설정하세요.
브라우저 내 Method 탐색은 `Ctrl+K` / `Cmd+K`, 발표 모드는 `P`, 발표 노트는 `N`, PPTX는 상단 다운로드를 이용합니다.
