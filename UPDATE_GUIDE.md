# GraphRAG / Ontology 업데이트

## 적용 방법

이 폴더의 내용을 GitHub 저장소 루트에 덮어쓰고 커밋하세요. Render 자동 배포가 시작됩니다.
requirements.txt, ontology_lab.py, app.py, engine.py, research.json, static 폴더와 slides 폴더를 함께 반영해야 합니다.
실제 API 키는 Render Environment의 OPENAI_API_KEY에만 보관합니다. 이 패키지에는 키가 없습니다.

## 온톨로지 실습

1. Ontology Studio에서 기본 예제를 실행합니다.
2. OWL RL 추론을 끄고 다시 실행해 SPARQL 결과를 비교합니다.
3. 회사의 uses 트리플을 지워 SHACL minCount 위반을 확인합니다.
4. uses의 목적어를 문자열로 바꿔 nodeKind/class 위반을 확인합니다.

## 실제 검색 과정

Pipeline Observatory에서 인덱스와 검색 로그를 펼쳐봅니다. 질문 원문과 실제 검색 쿼리, 엔티티·관계, 문서 후보 점수, PPR 반복 프레임, 선택된 근거 및 생성 context를 확인할 수 있습니다.
이 버전은 질문 rewrite를 실행하지 않습니다. 검색 문자열은 원래 질문이며, 그 사실을 로그에 명시합니다.
Entity extraction은 Live 인덱싱에서 실행됩니다. 질문 시점에는 기존 엔티티 유사도 grounding을 실행합니다.
표시되는 로그는 앱의 중간 산출물이며 모델 내부 사고 과정이 아닙니다.

## 연구와 구현 차이

공식 구현의 전체 설치·실행이나 benchmark 재현은 하지 않았습니다. 논문과 공식 저장소를 대조해 설명을 수정하고, 이 사이트에서 실행하는 축소 구현을 별도로 표시했습니다.
특히 GFM-RAG/G-reasoner는 pretrained GFM을 사용하지 않습니다. Microsoft GraphRAG의 Leiden/map-reduce와 ArchRAG C-HNSW도 이 경량 데모에서는 실행하지 않습니다.
각 방식은 research.json의 index/query(논문)와 implemented(실행 코드)를 확인하세요.

| 연구 | 논문 | 공식 구현 |
|---|---|---|
| raptor | https://arxiv.org/abs/2401.18059 | https://github.com/parthsarthi03/raptor |
| graphrag | https://arxiv.org/abs/2404.16130 | https://github.com/microsoft/graphrag |
| lightrag | https://arxiv.org/abs/2410.05779 | https://github.com/HKUDS/LightRAG |
| hipporag | https://arxiv.org/abs/2405.14831 | https://github.com/OSU-NLP-Group/HippoRAG |
| hipporag2 | https://arxiv.org/abs/2502.14802 | https://github.com/OSU-NLP-Group/HippoRAG |
| archrag | https://arxiv.org/abs/2502.09891 | https://github.com/sam234990/ArchRAG |
| linearrag | https://arxiv.org/abs/2510.10114 | https://github.com/DEEP-PolyU/LinearRAG |
| atomicrag | https://arxiv.org/abs/2604.20844 | https://github.com/7HHHHH/AtomicRAG |
| minirag | https://arxiv.org/abs/2501.06713 | https://github.com/HKUDS/MiniRAG |
| gfmrag | https://arxiv.org/abs/2502.01113 | https://github.com/RManLuo/gfm-rag |
| greasoner | https://arxiv.org/abs/2509.24276 | https://github.com/RManLuo/gfm-rag |
| raganything | https://arxiv.org/abs/2510.12323 | https://github.com/HKUDS/RAG-Anything |
| whenuse | https://arxiv.org/abs/2506.05690 | https://github.com/GraphRAG-Bench/GraphRAG-Benchmark |

직접 대조한 핵심 코드: RAPTOR raptor/cluster_tree_builder.py (raptor 디렉터리), LightRAG lightrag/operate.py, MiniRAG minirag/operate.py, AtomicRAG atomicrag/atomicrag.py. 나머지는 논문 및 공식 저장소 설명과 대조했습니다.

W3C 기준: https://www.w3.org/TR/rdf11-concepts/ / https://www.w3.org/TR/owl2-primer/ / https://www.w3.org/TR/shacl/

## 검증

- 기존 API 테스트 15개 통과
- 모든 14개 retrieval 경로에서 evidence와 구조화 trace 확인
- OWL RL 추론 ON/OFF, SHACL 관계 누락, SPARQL 결과 검증
- 실제 API 응답을 사용한 DOM 통합 검사: 초기화, 인덱스 로그, ontology 실행, SSE trace, PPR 슬라이더, 발표 이동 통과
- 브라우저 바이너리 다운로드 실패로 실제 브라우저 화면 검수는 완료하지 못했습니다.
- Live 키 설정은 Render에 적용됐지만 이 수정본의 실제 OpenAI 호출 성공은 별도로 확인하지 못했습니다.
- PPT 27장 렌더링 검수 및 구조·글꼴·레이아웃 검사 완료

검토일: 2026-10-21