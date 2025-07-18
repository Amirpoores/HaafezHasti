/* ---------- سوییچ بین حالت‌ها ---------- */
function switchMode(){
  const mode=document.getElementById('mode').value;
  document.getElementById('num-input').style.display  = mode==='num'  ? 'inline-block':'none';
  document.getElementById('text-input').style.display = mode==='text' ? 'inline-block':'none';
  document.getElementById('results').innerHTML='';
  document.getElementById('output').innerHTML='';
}

/* ---------- دکمه «نمایش» ---------- */
function handleAction(){
  const mode=document.getElementById('mode').value;
  if(mode==='num')  showByNumber();
  // در حالت text، لیست نتایج کلیک می‌شود؛ اینجا کاری نمی‌کنیم
}

/* ---------- util ---------- */
const br = t=>t.replace(/\n/g,'<br>');

function renderGhazal(d){
  const out=document.getElementById('output');
  out.innerHTML = `
     <div class="ghazal">${br(d.text)}</div>
     ${d.interpretation ? `<div class="interp">${br(d.interpretation)}</div>` : ''}
  `;
}

/* ---------- نمایش با شماره ---------- */
function showByNumber(){
  const n=+document.getElementById('num-input').value;
  if(!n||n<1||n>495) return alert('شماره باید بین ۱ تا ۴۹۵ باشد');
  fetch('/get_ghazal/'+n).then(r=>r.json()).then(d=>{
     if(d.error) return alert(d.error);
     renderGhazal(d);
  }).catch(e=>alert(e));
}

/* ---------- جستجوی متنی با دی‌بونس ---------- */
let timer=null;
document.getElementById('text-input').addEventListener('input',e=>{
  const q=e.target.value.trim();
  clearTimeout(timer);
  if(!q){ document.getElementById('results').innerHTML=''; return;}
  timer=setTimeout(()=>searchText(q), 500);
});

function searchText(q){
  fetch('/search?q='+encodeURIComponent(q))
    .then(r=>r.json())
    .then(d=>{
       const box=document.getElementById('results');
       if(d.results.length===0){ box.innerHTML='<em>یافت نشد</em>'; return;}
       const re=new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'gi');
       box.innerHTML=d.results.map(it=>{
         const hl=it.match.replace(re,m=>`<mark>${m}</mark>`);
         return `<div onclick="loadG(${it.number})">غزل ${it.number} – ${hl}</div>`;
       }).join('');
    })
    .catch(e=>alert(e));
}

function loadG(num){
  document.getElementById('results').innerHTML='';
  fetch('/get_ghazal/'+num).then(r=>r.json()).then(renderGhazal);
}

/* ---------- init ---------- */
switchMode();