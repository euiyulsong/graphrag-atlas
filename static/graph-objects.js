'use strict';
window.GraphObjects=(()=>{
 const labels={community:'요약·그룹',atom:'작은 사실',document:'원문 문서',image:'업로드 이미지',entity:'엔티티'};
 const colors={community:'#b5adff',atom:'#f4c17b',document:'#86b9f9',image:'#ffbca9',entity:'#9dddbe'};
 const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 let selectedId=null;
 function score(n,frame){if(!frame)return null;const k=n.type==='entity'?(frame.namespace==='mixed'?'E:':'')+n.source_id:frame.namespace==='mixed'&&['document','image'].includes(n.type)?n.source_id:null;return k!==null&&Object.hasOwn(frame.scores,k)?Number(frame.scores[k]):null;}
 function frameFor(state,frame){return {...frame,namespace:state.resultGraph?.method==='linearrag'?'mixed':'entity'};}
 function render(state){const g=state.resultGraph;if(!g)return false;
  const canvas=document.querySelector('#graphCanvas'),status=document.querySelector('#graphObjectStatus'),legend=document.querySelector('#graphObjectLegend'),detail=document.querySelector('#graphObjectDetails');
  const buckets={community:[],atom:[],document:[],entity:[]};
  g.nodes.forEach(n=>buckets[n.type==='image'?'document':n.type]?.push(n));
  const frame=state.pprFrame,scored=g.nodes.map(n=>({id:n.id,score:score(n,frame)})).filter(n=>n.score!==null&&n.score>0).sort((a,b)=>b.score-a.score);
  const active=new Set(scored.slice(0,9).map(n=>n.id)),max=Math.max(0,...scored.map(n=>n.score));
  const height=Math.max(390,92+Math.max(buckets.community.length,buckets.atom.length,buckets.document.length,Math.ceil(buckets.entity.length/2))*72),pos={};
  const xs={},columns=[];let columnLeft=0;
  for(const [kind,items] of Object.entries(buckets)){if(!items.length)continue;const w=kind==='entity'&&items.length>1?430:220;xs[kind]=columnLeft+110;columns.push({kind,x:columnLeft+w/2,count:items.length});columnLeft+=w;}
  const width=Math.max(480,columnLeft+20);
  Object.entries(buckets).forEach(([kind,nodes])=>nodes.forEach((n,i)=>{pos[n.id]={x:xs[kind]+(kind==='entity'?i%2*210:0),y:88+(kind==='entity'?Math.floor(i/2):i)*72};}));
  const selected=g.nodes.filter(n=>n.selected),focused=g.nodes.filter(n=>frame?active.has(n.id):n.focused);
  status.textContent=`${labelsFor(selected)} · ${g.nodes.length}개 객체 표시${frame?' · PPR '+frame.iteration+'회차':''}`;
  legend.innerHTML=`<span>밝은 실선 테두리: 최종 답변 근거 ${selected.length}개</span><span>분홍 테두리: ${frame?'현재 PPR 상위 대상':'검색 중 주목한 대상'} ${focused.length}개</span><span>흐린 노드: 원문 연결 확인용</span>${frame?'<span>노드 안의 밝기: 현재 PPR 점수</span>':''}<p>연결은 실습 데이터에 저장된 관계입니다. 노드를 누르면 본문과 원문 연결을 읽을 수 있습니다.</p>${g.source_note?'<p>'+escape(g.source_note)+'</p>':''}${g.nodes.some(n=>n.type==='image')?'<p>이미지 노드는 업로드 자료입니다. Offline에서는 이미지 내용을 해석하지 않습니다.</p>':''}`;
  canvas.classList.add('object-graph');
  if(!g.nodes.length){canvas.innerHTML='<p class="object-empty">선택된 검색 객체가 없습니다. 입력 문서와 실행 기록을 확인하세요.</p>';detail.hidden=true;return true;}
  const edges=g.edges.map(e=>{const a=pos[e.source],b=pos[e.target];if(!a||!b)return '';return `<path d="M ${a.x} ${a.y} Q ${(a.x+b.x)/2} ${(a.y+b.y)/2-12} ${b.x} ${b.y}" fill="none" stroke="#426271" stroke-width="1.1" opacity=".6"><title>${escape(e.label)}${e.doc_id?' ['+escape(e.doc_id)+']':''}</title></path>`;}).join('');
  const nodes=g.nodes.map(n=>{const {x,y}=pos[n.id],s=score(n,frame),on=frame?active.has(n.id):n.focused;
   const fill=s!==null&&max>0?0.13+0.55*s/max:0.12;
   return `<g class="object-node ${n.selected?'selected':''} ${on?'focused':''}" role="button" tabindex="0" aria-label="${escape(labels[n.type]+' '+n.label)}" data-node="${escape(n.id)}" data-score="${s===null?'':s}" transform="translate(${x},${y})"><title>${escape(n.label)} · ${escape(labels[n.type])}</title>${on?'<rect x="-96" y="-29" width="192" height="58" rx="10" fill="none" stroke="#f4a7c4" stroke-width="2"/>':''}<rect x="-91" y="-25" width="182" height="50" rx="8" fill="${colors[n.type]}" fill-opacity="${fill}" stroke="${n.selected?'#d4ffed':colors[n.type]}" stroke-width="${n.selected?3:1}"/><text text-anchor="middle" y="-4" fill="#eff8f6" font-size="13">${escape(n.label.length>22?n.label.slice(0,21)+'…':n.label)}</text><text text-anchor="middle" y="15" fill="#c6d8de" font-size="10">${escape(labels[n.type])}${s===null?'':' · PPR '+s.toFixed(5)}</text></g>`;
  }).join('');
  canvas.innerHTML=`<svg viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" style="width:${width}px;max-width:none" role="img" aria-label="선택한 요약, 사실, 원문, 이미지 및 엔티티의 연결"><g>${columns.map(c=>`<text x="${c.x}" y="28" fill="#b6d9d1" text-anchor="middle" font-size="14">${c.kind==='document'?'원문·이미지':labels[c.kind]} (${c.count})</text>`).join('')}</g><g>${edges}</g><g>${nodes}</g></svg>`;
  function inspect(id){const n=g.nodes.find(n=>n.id===id);if(!n)return;selectedId=id;const s=score(n,frame),links=g.edges.filter(e=>e.source===id||e.target===id);
   detail.hidden=false;detail.innerHTML=`<div class="object-detail-title"><b>${escape(n.label)}</b><span>${escape(labels[n.type])} · ${n.selected?'최종 답변 근거':(frame?active.has(n.id):n.focused)?'검색 중 주목한 대상':'원문 연결 확인용'}</span></div>${s===null?'':`<p>PPR ${frame.iteration}회차 점수: ${s.toFixed(7)}</p>`}${n.score===undefined?'':`<p>검색 근거 점수: ${n.score}</p>`}${n.type==='image'&&/^data:image\/(png|jpeg|webp);base64,/.test(state.image||'')?`<img class="object-image-preview" src="${escape(state.image)}" alt="검색에 포함된 업로드 이미지">`:''}${n.text?`<p class="object-source-text">${escape(n.text)}</p>`:'<p>개체의 의미와 연결은 아래 관계 및 원문 문서에서 확인하세요.</p>'}${n.source_kind==='image_unparsed'?'<p>이미지는 업로드됐지만 Offline에서 내용 인식은 실행하지 않았습니다.</p>':''}<details><summary>연결 ${links.length}개 보기</summary><ul>${links.map(e=>`<li>${escape(g.nodes.find(n=>n.id===e.source)?.label)} → ${escape(e.label)} → ${escape(g.nodes.find(n=>n.id===e.target)?.label)}${e.doc_id?' ['+escape(e.doc_id)+']':''}</li>`).join('')}</ul></details>`;
  }
  canvas.querySelectorAll('[data-node]').forEach(el=>{el.onclick=()=>inspect(el.dataset.node);el.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();inspect(el.dataset.node);}};});
  inspect(g.nodes.some(n=>n.id===selectedId)?selectedId:(selected[0]||g.nodes[0]).id);
  return true;
 }
 function labelsFor(nodes){const counts={};nodes.forEach(n=>counts[n.type]=(counts[n.type]||0)+1);return Object.entries(counts).map(([k,n])=>labels[k]+' '+n+'개 선택').join(' · ')||'최종 근거 없음';}
 return {render,frameFor};
})();
