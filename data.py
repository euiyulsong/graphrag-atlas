"""Original Korean teaching examples and method metadata. Not copied from WikiDocs."""

DEFAULT_DOCS = [
    {"id":"D1","title":"Atlas 개발 개요","topic":"architecture","text":"루멘랩은 지능형 물류 시스템 Atlas를 개발했다. Atlas는 배송 지연 예측 모델 Beacon을 사용한다. Atlas는 수도권 배송 관제에 활용된다."},
    {"id":"D2","title":"교통 데이터 수집","topic":"architecture","text":"Beacon은 실시간 교통 데이터 TrafficStream을 입력으로 사용한다. TrafficStream은 서울 도심 320개 교차로의 센서 정보를 수집한다."},
    {"id":"D3","title":"고객사 운영 성과","topic":"operations","text":"오로라 물류는 Atlas를 수도권 배송 거점에 도입했다. 도입 후 평균 배송 지연시간이 18% 감소했다. 이 값은 내부 운영 보고의 관측치다."},
    {"id":"D4","title":"설명가능성 대시보드","topic":"architecture","text":"Atlas는 Prism 대시보드로 예측 이유를 표시한다. Prism은 온톨로지 관계를 그래프로 시각화하며 운영자의 원인 분석을 돕는다."},
    {"id":"D5","title":"데이터 품질 정책","topic":"operations","text":"TrafficStream 데이터 품질 검사는 Nova 팀이 담당한다. Nova 팀은 누락 데이터가 발생하면 구간별 재처리를 수행하고 품질 리포트를 남긴다."},
    {"id":"D6","title":"2026 기술 전략","topic":"strategy","text":"루멘랩의 2026년 기술 전략은 비용 최적화, 설명가능성, 데이터 신뢰성을 세 가지 우선순위로 제시한다. 주요 사업 과제로 Atlas의 운영 복잡도 감소를 꼽는다."},
    {"id":"D7","title":"실시간 파이프라인","topic":"architecture","text":"Orion 데이터 파이프라인은 TrafficStream을 전처리해 Beacon에 전달한다. Orion 장애 시 배송 지연 예측의 품질이 저하될 수 있다."},
    {"id":"D8","title":"모델 평가 및 지표","topic":"operations","text":"2026년 2분기 Beacon의 배송 지연 예측 MAE는 4.2분이었다. 오로라 물류 운영팀은 매주 운영 KPI를 점검했다."},
    {"id":"D9","title":"멀티모달 아키텍처 메모","topic":"architecture","text":"시스템 아키텍처 다이어그램에는 TrafficStream에서 Orion을 거쳐 Beacon, Atlas, Prism으로 이어지는 데이터 흐름이 표현된다. 데이터 흐름은 고객사 오로라 물류의 배송 관제와 연결된다."},
    {"id":"D10","title":"별도 서비스 경계","topic":"strategy","text":"새벽 배송 시스템 Hermes는 독립된 물류 서비스다. Hermes는 Beacon을 사용하지 않으며 Atlas 예측 파이프라인과 분리돼 있다."}
]

DEMO_TRIPLES = [
    ("루멘랩","개발","Atlas","D1"),("Atlas","사용","Beacon","D1"),
    ("Beacon","입력 데이터","TrafficStream","D2"),("TrafficStream","수집 범위","서울 320개 교차로","D2"),
    ("오로라 물류","도입","Atlas","D3"),("Atlas","관측 성과","배송 지연 18% 감소","D3"),
    ("Atlas","설명 제공","Prism","D4"),("Prism","시각화","온톨로지 관계","D4"),
    ("Nova 팀","품질 검사","TrafficStream","D5"),("Nova 팀","처리","누락 데이터 재처리","D5"),
    ("루멘랩","전략 우선순위","비용 최적화","D6"),("루멘랩","전략 우선순위","설명가능성","D6"),
    ("루멘랩","전략 우선순위","데이터 신뢰성","D6"),
    ("Orion","전처리","TrafficStream","D7"),("Orion","전달","Beacon","D7"),
    ("Beacon","평가 지표","MAE 4.2분","D8"),("오로라 물류","모니터링","운영 KPI","D8"),
    ("TrafficStream","흐름","Orion","D9"),("Orion","흐름","Beacon","D9"),
    ("Beacon","흐름","Atlas","D9"),("Atlas","흐름","Prism","D9"),
    ("Hermes","독립","Atlas","D10")
]

METHODS = [
 {"id":"baseline","name":"Vector RAG","family":"Baseline","level":"입문","source":"https://wikidocs.net/352195","tag":"Chunk","idea":"질문과 가까운 원문 Chunk를 검색합니다.","fit":"단순 사실 질의·짧은 문서","limit":"문서 사이 연결과 전체 맥락에 약함","steps":["질문 임베딩","Top-k Chunk 검색","선택된 근거로 답변"],"fidelity":"실행형 기본 RAG","formula":"TopK cosine(q, chunks)","accent":"#86b9f9"},
 {"id":"raptor","name":"RAPTOR","family":"Hierarchy","level":"중급","source":"https://wikidocs.net/352213","tag":"Tree","idea":"원문과 상위 요약을 함께 검색해 여러 해상도의 맥락을 찾습니다.","fit":"장문 문서·요약과 세부사항을 모두 요구하는 질의","limit":"요약 노드가 세부사실을 누락할 수 있음","steps":["문서 클러스터 구성","상위 Summary 생성","Summary + 원문 검색"],"fidelity":"2단계 계층·요약을 사용하는 축소 재현; 원 논문 클러스터링·재귀 트리 전체 구현은 아님","formula":"TopK(q, leaf ∪ summary)","accent":"#a7a1ff"},
 {"id":"graphrag","name":"Microsoft GraphRAG","family":"Community","level":"중급","source":"https://wikidocs.net/352214","tag":"Community","idea":"관계 그래프로 공동체를 만들고 보고서를 모아 전체적인 질문에 답합니다.","fit":"전체 데이터의 테마·트렌드·핵심 이슈","limit":"엔티티 추출·커뮤니티 리포트 생성 비용","steps":["엔티티·관계 추출","Community Report 생성","보고서 선택·종합"],"fidelity":"간소화한 클러스터 리포트 검색; Leiden / full map-reduce 미포함","formula":"Community → Report → Synthesis","accent":"#f7bb7b"},
 {"id":"lightrag","name":"LightRAG","family":"Cost & Noise","level":"중급","source":"https://wikidocs.net/352215","tag":"Dual level","idea":"엔티티의 국소 정보와 관계의 상위 정보를 함께 조회합니다.","fit":"엔티티 중심 질의·가벼운 증분형 RAG","limit":"키워드 및 추출된 관계 품질에 민감","steps":["Low-level 엔티티 검색","High-level 관계 검색","원문과 Triple 병합"],"fidelity":"엔티티·관계 이중 검색의 핵심을 구현; 원 논문 키워드 프롬프트와 인덱스는 축약","formula":"Low(entity) + High(relation)","accent":"#7addc7"},
 {"id":"hipporag","name":"HippoRAG","family":"Graph Memory","level":"중급","source":"https://wikidocs.net/352216","tag":"PPR","idea":"질문 엔티티에서 Personalized PageRank로 관련 근거를 확산 검색합니다.","fit":"여러 문서에 걸친 multi-hop 질문","limit":"잘못 연결된 엔티티가 전파 오류를 만듦","steps":["질문 Entity Seed","Personalized PageRank","Entity → Passage 선택"],"fidelity":"실제 PPR 기반 교육용 재현; OpenIE/동의어 링크는 단순화","formula":"p = αs + (1−α)Pᵀp","accent":"#f39cb9"},
 {"id":"hipporag2","name":"HippoRAG 2","family":"Graph Memory","level":"중급","source":"https://wikidocs.net/352217","tag":"Phrase + Passage","idea":"질문에 맞는 Passage를 먼저 인식하고 그래프 메모리와 함께 확산합니다.","fit":"문맥이 중요한 multi-hop 검색","limit":"추가 연결과 seed 보정에 따른 비용","steps":["Passage 인식 검색","Phrase + Passage seed","Graph PPR로 근거 확장"],"fidelity":"passage-aware seed + PPR 교육용 축소; 실제 recognition memory 학습 과정 없음","formula":"seed(entity) + seed(passage) → PPR","accent":"#efa0c4"},
 {"id":"archrag","name":"ArchRAG","family":"Hierarchy","level":"고급","source":"https://wikidocs.net/352218","tag":"Hierarchy","idea":"구조와 의미를 고려한 커뮤니티 중 필요한 계층만 탐색합니다.","fit":"전체 요약과 특정 사실을 모두 질문할 때","limit":"계층 인덱스·커뮤니티 구축 복잡도","steps":["의미/연결 클러스터","상위 요약에서 후보 선택","선택한 클러스터만 내려가 검색"],"fidelity":"coarse-to-fine 계층 검색 구현; C-HNSW / attributed Leiden 재현 아님","formula":"Coarse → Fine community search","accent":"#e1b7ff"},
 {"id":"linearrag","name":"LinearRAG","family":"Cost & Noise","level":"중급","source":"https://wikidocs.net/352219","tag":"Relation-free","idea":"관계 문장 추출 없이 엔티티와 문서 포함 관계로 전파합니다.","fit":"관계 추출 비용이 부담인 다중 문서 검색","limit":"연결의 의미를 명시적으로 이해하기 어려움","steps":["Entity–Passage bipartite graph","Seed 설정","Relation-free 확산"],"fidelity":"relation-free bipartite diffusion 구현; 원 논문의 Tri-Graph와 검색 전체와 다름","formula":"Entity ↔ Passage ↔ Entity","accent":"#a8e7a7"},
 {"id":"atomicrag","name":"AtomicRAG","family":"Cost & Noise","level":"중급","source":"https://wikidocs.net/352220","tag":"Atom","idea":"긴 Chunk를 독립적으로 이해할 수 있는 원자적 사실로 나눠 검색합니다.","fit":"세부 사실이 여러 개 섞인 Chunk·긴 근거 제거","limit":"잘못 나눈 atom은 문맥을 잃을 수 있음","steps":["Atomic Fact 분해","Fact + Graph relevance","필요한 Atom만 전달"],"fidelity":"독립 문장 atom 검색; 원 논문 PPR/atomic sieve 전체 구현은 아님","formula":"Chunk → Atomic fact → TopK","accent":"#f9d178"},
 {"id":"minirag","name":"MiniRAG","family":"Cost & Noise","level":"중급","source":"https://wikidocs.net/352221","tag":"Compact path","idea":"작은 모델이 읽기 쉬운 짧은 엔티티 경로로 근거를 압축합니다.","fit":"SLM·적은 컨텍스트 예산","limit":"짧은 경로에서 중요한 원문 정보 생략 가능","steps":["질문 엔티티 추출","Shortest path 확장","짧은 Path + 원문 전달"],"fidelity":"최단 경로 압축 근사; 논문 이질 그래프·전체 검색기와 다름","formula":"Seed → Shortest path → Context","accent":"#8cdde2"},
 {"id":"gfmrag","name":"GFM-RAG","family":"Learned Graph","level":"연구","source":"https://wikidocs.net/352206","tag":"Message passing","idea":"질문 관련성이 그래프 이웃으로 전파되는 방식을 보여 줍니다.","fit":"학습된 그래프 검색기의 필요성·비교 실험","limit":"실제 GFM은 별도 학습된 GNN 가중치 필요","steps":["Query-conditioned node 초기화","2-step message propagation","상위 관련 노드로 Passage 선택"],"fidelity":"설명용 비학습 propagation proxy — 학습 GNN, 논문 성능 재현 불가","formula":"hᵗ⁺¹ = βh⁰ + (1−β)Ahᵗ","accent":"#f7a9a3"},
 {"id":"greasoner","name":"G-Reasoner","family":"Learned Graph","level":"연구","source":"https://wikidocs.net/352207","tag":"QuadGraph","idea":"엔티티·속성·문서·커뮤니티의 여러 계층을 한 화면에서 검색합니다.","fit":"이질 그래프 검색의 통합 인터페이스 탐색","limit":"원 논문의 학습된 QuadGraph relevance 모델 필요","steps":["Entity / Attribute / Document / Community 구성","질문과 계층별 관련성 산출","상위 계층 근거 융합"],"fidelity":"QuadGraph 레이어 선택의 비학습 proxy — 원 논문의 GFM 모델 아님","formula":"Score(E,A,D,C|q) → Evidence","accent":"#d6aafa"},
 {"id":"raganything","name":"RAG-Anything","family":"Multimodal","level":"고급","source":"https://wikidocs.net/352208","tag":"Multimodal","idea":"텍스트와 이미지 설명을 같은 구조적 검색 공간으로 연결합니다.","fit":"보고서 속 그림·표·도식 중심 질의","limit":"실제 이미지 이해는 Live mode와 vision 지원 모델 필요","steps":["이미지 업로드 후 Vision 캡셔닝","텍스트와 구조 관계로 인덱싱","멀티모달 근거 검색"],"fidelity":"실제 Vision API 캡션+텍스트 검색 데모; 논문 멀티모달 parsing 전 과정 아님","formula":"Text + Image caption → Graph → QA","accent":"#ffb5ad"},
 {"id":"whenuse","name":"When to Use Graphs in RAG","family":"Diagnosis","level":"입문","source":"https://wikidocs.net/352209","tag":"Router","idea":"질문 특성에 따라 Chunk·Graph·Community 전략을 선택합니다.","fit":"기술 선택·성능 및 비용 트레이드오프 진단","limit":"실제 선택 기준은 벤치마크로 검증해야 함","steps":["Query type 진단","Baseline / multi-hop / global 중 선택","선택 검색기로 답변"],"fidelity":"질문 유형 기반 교육용 휴리스틱 라우터; 원 논문은 비교·분석 연구","formula":"Router(q) → Retriever","accent":"#b7df92"}
]

SAMPLE_QUESTIONS = [
 {"label":"Multi-hop · 원인 추적","question":"오로라 물류에서 배송 지연이 줄어든 과정을 교통 데이터 수집부터 설명해줘.","hint":"D2 → D7 → D1 → D3의 연결이 중요"},
 {"label":"Global · 전략 요약","question":"루멘랩의 2026년 핵심 기술 과제와 제품 운영상의 쟁점을 정리해줘.","hint":"여러 문서 주제를 요약"},
 {"label":"Local · 단일 사실","question":"2026년 2분기 Beacon의 MAE는 몇 분이야?","hint":"D8의 사실 하나"},
 {"label":"Ontology · 관계 탐색","question":"TrafficStream과 Prism이 Atlas에서 어떤 경로로 연결되는지 설명해줘.","hint":"엔티티 경로를 추적"},
 {"label":"Boundary · 잘못된 연결","question":"Hermes도 Beacon을 사용하는 거야?","hint":"부정·독립 관계 정확성 확인"}
]

# A useful, different live-demo query for every research idea.
EXAMPLES_BY_METHOD = {
  "baseline":"2026년 2분기 Beacon의 MAE는 몇 분이야?",
  "raptor":"Atlas 시스템의 전체 구성과 관련 제품의 주요 기능을 요약해줘.",
  "graphrag":"루멘랩의 2026년 기술 전략, 제품 운영 성과, 위험 요소를 전체적으로 분석해줘.",
  "lightrag":"Atlas가 사용하는 모델과 대시보드 간 관계를 설명해줘.",
  "hipporag":"TrafficStream이 오로라 물류의 배송 지연 개선에 어떻게 연결되는지 설명해줘.",
  "hipporag2":"오로라 물류에서 배송 지연이 줄어든 과정을 교통 데이터 수집부터 설명해줘.",
  "archrag":"Atlas의 전체 구조와 Beacon의 2분기 성능 지표를 함께 설명해줘.",
  "linearrag":"TrafficStream과 Prism 사이에 어떤 데이터 흐름이 있어?",
  "atomicrag":"Nova 팀은 누락 데이터가 생기면 구체적으로 무엇을 하는가?",
  "minirag":"TrafficStream에서 Prism까지 거치는 시스템 경로를 알려줘.",
  "gfmrag":"Orion에서 오류가 나면 어떤 시스템과 기능에 영향이 있나?",
  "greasoner":"루멘랩 기술 전략과 Atlas 구성요소, 관련 운영 사실을 함께 연결해줘.",
  "raganything":"아키텍처 다이어그램에서 데이터가 어떤 순서로 이동해?",
  "whenuse":"오로라 물류에 배송 지연 개선이 발생한 이유와 경로는 무엇인가?"
}
for _item in METHODS:
    _item['example'] = EXAMPLES_BY_METHOD[_item['id']]
