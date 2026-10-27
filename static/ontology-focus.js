'use strict';
// Audience explanations follow the selected example; result summaries use server output.
window.OntologyFocus=(()=>{
 const $=s=>document.querySelector(s);
 const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const cases={
  types:{kind:'비교 실험',question:'예측모델도 소프트웨어 목록에 나올까요?',key:'스키마의 상위 종류 규칙이 팩트의 개체에 적용됩니다.',issue:'입력 오류를 심은 예제가 아닙니다. 원본에 직접 적지 않은 상위 타입을 추론으로 얻는지 봅니다.',expect:'기본 질문: 원본 2행 / 추론 ON 3행. 도착예측모델이 추가됩니다.',
   schema:{match:/subClassOf/,tokens:['rdfs:subClassOf'],explain:'PredictionModel은 SoftwareSystem의 한 종류라는 규칙입니다.'},
   facts:{match:/^ex:도착예측모델 /,tokens:['ex:도착예측모델','ex:PredictionModel'],explain:'도착예측모델의 종류는 PredictionModel이라고만 직접 적었습니다.'}},
  impact:{kind:'비교 실험',question:'날씨API에 간접 의존하는 배차시스템도 찾을까요?',key:'스키마의 전이 규칙이 팩트의 두 의존 관계를 이어 줍니다.',issue:'데이터 오류가 아닙니다. 직접 연결만 조회할 때 빠지는 간접 의존 대상을 확인합니다.',expect:'기본 질문: 원본은 도착예측모델 1행 / 추론 ON은 배차시스템까지 2행.',
   schema:{match:/TransitiveProperty/,tokens:['owl:TransitiveProperty'],explain:'dependsOn은 여러 단계를 이어 해석할 수 있다고 정의했습니다.'},
   facts:{match:/ex:dependsOn/,tokens:['ex:dependsOn','ex:날씨API','ex:도착예측모델'],explain:'배차시스템은 모델에, 모델은 날씨API에 의존합니다. 두 문장이 추론의 전제입니다.'}},
  inverse:{kind:'비교 실험',question:'uses로 적은 사실을 usedBy로도 찾을까요?',key:'스키마의 역관계 선언으로 연결을 반대 방향에서도 읽습니다.',issue:'조회 결과 0행이 문법 오류를 뜻하지는 않습니다. 원본에는 usedBy 문장이 없기 때문입니다.',expect:'기본 질문: 원본 0행 / 추론 ON은 물류사 1행.',
   schema:{match:/inverseOf/,tokens:['owl:inverseOf','ex:usedBy'],explain:'uses와 usedBy는 반대 방향 관계라고 정했습니다.'},
   facts:{match:/^ex:물류사 /,tokens:['ex:uses','ex:배차시스템'],explain:'직접 적은 것은 물류사가 배차시스템을 uses로 사용한다는 사실입니다.'}},
  missing:{kind:'오류 실험',question:'물류사의 사용 시스템이 빠졌습니다',key:'문제는 팩트의 관계 누락이고, 이를 잡는 기준은 SHACL의 최소 개수입니다.',issue:'기본 예제에는 물류사 개체만 남아 있고 uses 관계가 없습니다. 추론을 켜도 필수 관계가 자동 복구되지는 않습니다.',expect:'기본 예제는 SHACL 실패. uses 관계를 추가한 뒤 다시 실행해 통과 여부를 확인합니다.',
   schema:{match:/^ex:uses /,tokens:['ex:uses','owl:ObjectProperty'],explain:'uses라는 관계의 정의입니다. 이 선언 자체가 각 회사에 사용 시스템을 채워 주지는 않습니다.'},
   facts:{match:/^ex:물류사 /,tokens:['ex:물류사','ex:Company'],explain:'이 줄에 회사 개체는 있습니다. 기본 예제에는 그 회사의 uses 연결이 빠져 있습니다.'},
   repair:'ex:물류사 ex:uses ex:배차시스템 .',repairExplain:'기본 예제의 팩트에 추가할 관계입니다. 스키마나 SHACL을 지우지 않습니다.'},
  literal:{kind:'오류 실험',question:'시스템 개체 대신 이름 문자열을 넣었습니다',key:'같은 이름이어도 "배차시스템" 문자열과 ex:배차시스템 개체는 다릅니다.',issue:'기본 예제의 uses 값에는 따옴표로 감싼 문자열이 있습니다. SHACL은 소프트웨어 개체의 식별자(IRI)를 요구합니다.',expect:'문자열 상태는 SHACL 실패. uses 값을 ex:배차시스템으로 바꾼 뒤 다시 실행합니다.',
   schema:{match:/^ex:uses /,tokens:['owl:ObjectProperty'],explain:'uses는 대상과 대상을 연결하는 관계로 정의했습니다. 입력 조건 검사는 SHACL에서 따로 합니다.'},
   facts:{match:/^ex:물류사 /,tokens:['"배차시스템"'],explain:'따옴표가 핵심입니다. 이 값은 시스템을 가리키는 개체 식별자가 아니라 글자입니다.'},
   repair:'ex:uses "배차시스템"  →  ex:uses ex:배차시스템',repairExplain:'팩트에서 uses의 값만 바꿉니다. 전체 코드 편집을 열어 따옴표 문자열을 개체로 교체하세요.'},
  range:{kind:'해석 주의',question:'검사가 통과했는데, 검사 대상이 없었던 건 아닐까요?',key:'domain/range는 종류를 붙입니다. 필수 입력 검사와 역할이 다릅니다.',issue:'기본 예제는 타입을 직접 적지 않았습니다. 추론 OFF에서는 Company 대상이 없어 회사 제약이 검사할 대상을 못 찾을 수 있습니다.',expect:'기본 질문: 원본 0행 / 추론 ON은 미등록도구 1행. 새로 붙은 Company·SoftwareSystem 타입도 봅니다.',
   schema:{match:/rdfs:domain/,tokens:['rdfs:domain','rdfs:range','ex:Company','ex:SoftwareSystem'],explain:'uses의 주어는 회사, 목적어는 소프트웨어로 해석하라는 타입 추론 선언입니다.'},
   facts:{match:/^ex:미등록조직 /,tokens:['ex:미등록조직','ex:미등록도구'],explain:'사용 관계만 직접 적었고 Company나 SoftwareSystem 타입은 아직 적지 않았습니다.'}}
 };
 let lesson,bound=false,lastRun=null;
 const ids=['ontologySchema','ontologyData','ontologyShapes'];
 const currentInput=()=>({schema:$('#ontologySchema').value,facts:$('#ontologyData').value,shapes:$('#ontologyShapes').value,infer:$('#ontologyInfer').checked,query_id:$('#ontologyQueryChoice').value});
 function highlighted(line,tokens){
  let rest=line,out='';const keys=tokens.filter(Boolean).sort((a,b)=>b.length-a.length);
  while(rest){let at=-1,word='';for(const t of keys){const i=rest.indexOf(t);if(i>=0&&(at<0||i<at)){at=i;word=t;}}if(at<0){out+=escape(rest);break;}out+=escape(rest.slice(0,at))+'<mark>'+escape(word)+'</mark>';rest=rest.slice(at+word.length);}return out;
 }
 function excerpt(text,spec){const lines=text.split('\n').map((t,i)=>({t,n:i+1})).filter(x=>spec.match.test(x.t));return lines.length?'<div class="onto-code-title">주목할 코드 줄 <small>번호는 전체 코드의 줄 위치입니다</small></div><div class="onto-key-lines">'+lines.slice(0,5).map(x=>`<div><span class="onto-line-number">${x.n}</span><code>${highlighted(x.t,spec.tokens)}</code></div>`).join('')+'</div>':'<p class="onto-input-note">현재 입력에서는 이 예제의 핵심 줄을 찾지 못했습니다. 전체 코드를 확인하고 다시 실행하세요.</p>';}
 function render(){if(!lesson)return;const c=cases[lesson.id];if(!c)return;
  const changed=ids.some((id,i)=>$('#'+id).value!==[lesson.schema,lesson.facts,lesson.shapes][i]);
  $('#ontologyGoal').innerHTML=`<span class="onto-case-kind ${c.kind==='오류 실험'?'error-case':''}">${escape(c.kind)}</span><h3>${escape(c.question)}</h3><div class="onto-focus-grid"><div><b>이번 실습의 핵심</b><p>${escape(c.key)}</p></div><div><b>${c.kind==='오류 실험'?'기본 예제의 문제':'꼭 확인할 점'}</b><p>${escape(c.issue)}</p></div></div><p class="onto-expected"><b>기본 예제의 예상 결과</b> ${escape(c.expect)}</p>${changed?'<p class="onto-input-note">입력을 수정했습니다. 위 예상 결과는 기본 예제 기준입니다. 현재 입력은 다시 실행해 확인하세요.</p>':''}`;
  $('#ontologySchemaFocus').innerHTML=`<p class="onto-focus-caption">${escape(c.schema.explain)}</p>${excerpt($('#ontologySchema').value,c.schema)}`;
  $('#ontologyFactsFocus').innerHTML=`<p class="onto-focus-caption">${escape(c.facts.explain)}</p>${excerpt($('#ontologyData').value,c.facts)}${c.repair?`<div class="onto-repair"><b>기본 예제를 고치는 방법</b><code>${escape(c.repair)}</code><p>${escape(c.repairExplain)}</p></div>`:''}`;
  const validation=c.kind==='오류 실험';
  $('#ontologyShaclFocus').innerHTML=`<p class="onto-focus-caption">${lesson.id==='missing'?'minCount 1은 사용 시스템을 최소 하나 기록하라는 조건입니다.':lesson.id==='literal'?'nodeKind IRI는 개체 식별자, class는 SoftwareSystem 종류를 요구합니다.':lesson.id==='range'?'targetClass Company는 현재 그래프에서 Company 타입인 대상을 검사하겠다는 뜻입니다.':'이번에는 수정하지 않습니다. SHACL은 입력 조건을 검사하며 새 사실을 추론하지 않습니다.'}</p>${excerpt($('#ontologyShapes').value,{match:/sh:targetClass|sh:property/,tokens:lesson.id==='missing'?['sh:path','ex:uses','sh:minCount 1']:lesson.id==='literal'?['sh:nodeKind sh:IRI','sh:class ex:SoftwareSystem']:['sh:targetClass ex:Company']})}<p class="onto-layer-note">${validation?'수정할 곳은 위의 팩트입니다. 조건을 없애 통과시키는 대신 누락·값 오류를 고쳐 보세요.':'검사 통과는 작성한 SHACL 조건을 만족한다는 뜻입니다. 모든 사실이 정확하거나 모든 대상이 검사됐다는 뜻은 아닙니다.'}</p>`;
  $('#ontologyInferState').textContent=$('#ontologyInfer').checked?'ON · 규칙으로 새 사실 도출':'OFF · 직접 적은 사실만 조회';
  const stale=$('#ontologyStale');if(stale&&lastRun)stale.hidden=JSON.stringify(currentInput())===JSON.stringify(lastRun.input);
 }
 function select(c){lesson=c;lastRun=null;if(!bound){ids.forEach(id=>$('#'+id).addEventListener('input',render));$('#ontologyInfer').addEventListener('change',render);$('#ontologyQueryChoice').addEventListener('change',render);bound=true;}render();}
 function result(r,input){lastRun={input};
  const key=row=>JSON.stringify(Object.entries(row).sort());const before=new Set(r.before_results.map(key));const added=r.results.filter(row=>!before.has(key(row))).map(row=>Object.values(row).join(', '));
  const violations=r.violations.map(v=>{const rule=v.constraint||'';let why=rule.includes('MinCount')?'필수 관계의 값이 최소 개수보다 적습니다.':rule.includes('NodeKind')?'값의 종류가 맞지 않습니다. IRI 조건에서는 문자열 대신 개체 식별자가 필요합니다.':rule.includes('ClassConstraint')?'연결된 값이 요구한 클래스에 속하지 않습니다.':v.message||'작성한 SHACL 조건을 위반했습니다.';return `<li><strong>${escape(v.focus)}</strong>의 <strong>${escape(v.path||'검사 항목')}</strong><p>${escape(why)}</p><small>검사 값: ${escape(v.value||'없음')} · ${escape(rule.split(/[#/]/).pop())}</small></li>`;}).join('');
  const h=`<section class="onto-result-summary"><span class="overline">먼저 볼 핵심 결과 / 방금 실행한 입력 기준</span><h3>${r.conforms?'정의한 SHACL 조건에서 위반이 없습니다':'입력 조건 위반이 발견됐습니다'}</h3><div class="onto-result-grid"><div><b>조회 결과의 변화</b><p>원본 ${r.before_results.length}행 / 현재 ${r.results.length}행</p><p>${input.infer?(added.length?'추가로 조회된 대상: '+escape(added.join(' · ')):'이번 조회에서 추가된 대상은 없습니다.'):'추론 OFF입니다. 같은 데이터와 질문으로 ON을 켜고 다시 실행해 비교하세요.'}</p></div><div><b>입력 검사</b>${r.conforms?'<p>현재 SHACL 조건을 통과했습니다. 조회 결과가 늘어난 것과 검사 통과는 서로 다른 결과입니다.</p>':`<ul class="onto-plain-errors">${violations}</ul>`}</div></div><p class="onto-input-note" id="ontologyStale" hidden>입력·질문·추론 설정이 바뀌었습니다. 아래는 이전 실행 결과입니다. 다시 실행해 주세요.</p></section>`;
  $('#ontologyResults').insertAdjacentHTML('afterbegin',h);render();
 }
 return {select,render,result};
})();
