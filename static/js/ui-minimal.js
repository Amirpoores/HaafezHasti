/* تب‌ها */
document.querySelectorAll('.tab').forEach(t=>{
  t.onclick=()=>{document.querySelectorAll('.tab').forEach(z=>z.classList.remove('active'));
                 document.querySelectorAll('.pane').forEach(p=>p.classList.remove('active'));
                 t.classList.add('active');
                 document.getElementById('pane-'+t.dataset.tab).classList.add('active');
                 clearOut();};
});

/* util */
const br = t=>t.replace(/\n/g,'<br>');

/* خروجی */
function showLoading(){outBox().style.display='block';el('out-content').innerHTML='';el('out-loading').style.display='block';}
function showGhazal(d){
   el('out-loading').style.display='none';
   el('out-content').innerHTML = `<div class="gh-text">${br(d.text)}</div>`
       +(d.interpretation?`<div class="interp">${br(d.interpretation)}</div>`:'');
   outBox().style.display='block';
}
function clearOut(){outBox().style.display='none';el('suggest').innerHTML='';}

const el = id=>document.getElementById(id);
const outBox = ()=>document.getElementById('output');

/* ---------- با شماره ---------- */
function byNumber(){
  const n=+el('num-input').value;
  if(!n||n<1||n>495) return alert('شماره باید ۱-۴۹۵ باشد');
  showLoading();
  fetch('/get_ghazal/'+n).then(r=>r.json()).then(d=>{
     if(d.error)return alert(d.error);
     showGhazal(d);
  }).catch(e=>alert(e));
}

/* ---------- تصادفی ---------- */
function randomG(){
  showLoading();
  fetch('/get_fal').then(r=>r.json()).then(showGhazal).catch(e=>alert(e));
}

/* ---------- جستجوی متن (debounce) ---------- */
let timer; el('text-input').addEventListener('input',e=>{
  const q=e.target.value.trim();
  if(timer)clearTimeout(timer);
  if(!q){el('suggest').innerHTML='';return;}
  timer=setTimeout(()=>search(q),400);
});
function search(q){
 fetch('/search?q='+encodeURIComponent(q))
  .then(r=>r.json()).then(d=>{
     const box=el('suggest');
     if(!d.results.length){box.innerHTML='<em>یافت نشد</em>';return;}
     const re=new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'gi');
     box.innerHTML=d.results.map(r=>{
        const hl=r.match.replace(re,m=>`<mark>${m}</mark>`);
        return `<div onclick="loadG(${r.number})">غزل ${r.number} – ${hl}</div>`;
     }).join('');
  });
}
function loadG(n){ el('text-input').value=''; el('suggest').innerHTML=''; showLoading();
  fetch('/get_ghazal/'+n).then(r=>r.json()).then(showGhazal);}

/* Enter روی شماره */
el('num-input').addEventListener('keypress',e=>e.key==='Enter'&&byNumber());