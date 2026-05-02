// ── Helpers ──
const $=s=>document.querySelector(s),$$=s=>document.querySelectorAll(s);
const assetById=id=>ASSETS.find(a=>a.id===id);
const userById=id=>USERS.find(u=>u.id===id);
const fmt=n=>n.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});

function makeTable(cols,rows){
  let h='<table><thead><tr>'+cols.map(c=>`<th>${c}</th>`).join('')+'</tr></thead><tbody>';
  h+=rows.map(r=>'<tr>'+r.map(c=>`<td>${c}</td>`).join('')+'</tr>').join('');
  return h+'</tbody></table>';
}

function badge(text,cls){return `<span class="badge badge-${cls}">${text}</span>`}

function toast(msg,type){
  const c=$('#toastContainer'),t=document.createElement('div');
  t.className=`toast toast-${type}`;t.textContent=msg;c.appendChild(t);
  setTimeout(()=>t.remove(),3000);
}

// ── Navigation ──
$$('.nav-btn').forEach(btn=>{
  btn.addEventListener('click',()=>{
    $$('.nav-btn').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    $$('.page').forEach(p=>p.classList.remove('active'));
    $(`#page-${btn.dataset.section}`).classList.add('active');
    const init={dashboard:initDashboard,users:initUsers,assets:initAssets,
      orders:initOrders,transactions:initTxns,placeorder:initPlaceOrder,sqlref:initSQL};
    if(init[btn.dataset.section])init[btn.dataset.section]();
  });
});

// ── Dashboard ──
function initDashboard(){
  $('#headerDate').textContent=new Date().toLocaleDateString('en-GB',{day:'2-digit',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'});

  // Ticker
  let tk='';
  ASSETS.forEach(a=>{
    const p=latestPrice(a.id),arr=PRICES[a.id],prev=arr[arr.length-2].close;
    const chg=((p-prev)/prev*100).toFixed(2),up=chg>=0;
    tk+=`<div class="ticker-item"><span class="ticker-symbol">${a.symbol}</span>
      <span class="ticker-price ${up?'ticker-up':'ticker-down'}">$${fmt(p)}</span>
      <span class="ticker-change ${up?'ticker-up':'ticker-down'}">${up?'▲':'▼'} ${Math.abs(chg)}%</span></div>`;
  });
  $('#tickerStrip').innerHTML=tk;

  // Stats
  const activeUsers=USERS.filter(u=>u.status==='ACTIVE').length;
  const pendingOrders=ORDERS.filter(o=>o.status==='PENDING').length;
  const totalTxns=TXNS.length;
  const vol=TXNS.reduce((s,t)=>s+t.total,0);
  const stats=[
    ['Active Users',activeUsers,'green'],['Pending Orders',pendingOrders,'amber'],
    ['Total Transactions',totalTxns,'accent'],['Volume (USD)','$'+fmt(vol),'purple']
  ];
  $('#statsGrid').innerHTML=stats.map(([l,v,c])=>`<div class="stat-card" data-color="${c}">
    <div class="stat-label">${l}</div><div class="stat-value" data-color="${c}">${v}</div></div>`).join('');

  // Charts
  initCharts();

  // Recent txns table
  const rows=TXNS.slice().reverse().map(t=>{
    const u=userById(t.uid),a=assetById(t.aid);
    return [t.id,u.username,a.symbol,badge(t.type,t.type.toLowerCase()),t.qty,'$'+fmt(t.price),'$'+fmt(t.total),t.at.slice(0,10)];
  });
  $('#dashTxnTable').innerHTML=makeTable(['TXN','User','Asset','Type','Qty','Price','Amount','Date'],rows);
}

function initCharts(){
  // Portfolio Doughnut
  const holdings={};
  WALLETS.forEach(w=>{const a=assetById(w.aid);if(a)holdings[a.symbol]=(holdings[a.symbol]||0)+w.balance*latestPrice(w.aid)});
  const labels=Object.keys(holdings),values=Object.values(holdings);
  const colors=['#58A6FF','#3FB950','#DA8FFF','#F85149','#D29922'];

  const ctx1=$('#portfolioChart');
  if(ctx1._chart)ctx1._chart.destroy();
  ctx1._chart=new Chart(ctx1,{type:'doughnut',data:{labels,datasets:[{data:values,backgroundColor:colors,borderWidth:0,hoverOffset:8}]},
    options:{responsive:true,maintainAspectRatio:false,cutout:'65%',plugins:{legend:{position:'bottom',labels:{color:'#8B949E',font:{family:'Inter',size:11},padding:12}}}}});

  // Price line chart (BTC)
  const btcP=PRICES[1],ctx2=$('#priceChart');
  if(ctx2._chart)ctx2._chart.destroy();
  ctx2._chart=new Chart(ctx2,{type:'line',data:{labels:btcP.map(p=>p.date.slice(5)),
    datasets:[{label:'BTC Close',data:btcP.map(p=>p.close),borderColor:'#58A6FF',backgroundColor:'rgba(88,166,255,0.08)',fill:true,tension:0.4,pointRadius:4,pointBackgroundColor:'#58A6FF',borderWidth:2}]},
    options:{responsive:true,maintainAspectRatio:false,scales:{x:{ticks:{color:'#8B949E',font:{size:11}},grid:{color:'rgba(48,54,61,0.4)'}},y:{ticks:{color:'#8B949E',font:{size:11},callback:v=>'$'+v.toLocaleString()},grid:{color:'rgba(48,54,61,0.4)'}}},
      plugins:{legend:{labels:{color:'#8B949E',font:{family:'Inter'}}}}}});
}

// ── Users ──
function initUsers(){
  renderUsers('');
  $('#userSearch').oninput=e=>renderUsers(e.target.value.toLowerCase());
}
function renderUsers(q){
  const filtered=USERS.filter(u=>!q||u.username.includes(q)||u.full_name.toLowerCase().includes(q)||u.country.toLowerCase().includes(q));
  const rows=filtered.map(u=>[u.id,u.username,u.email,u.full_name,u.country,
    badge(u.kyc==='Y'?'Verified':'Pending',u.kyc==='Y'?'kyc-y':'kyc-n'),
    badge(u.status,u.status.toLowerCase()),u.created]);
  $('#usersTable').innerHTML=makeTable(['ID','Username','Email','Full Name','Country','KYC','Status','Created'],rows);
}

// ── Assets ──
function initAssets(){
  let html='';
  ASSETS.forEach(a=>{
    const p=latestPrice(a.id),arr=PRICES[a.id],prev=arr[arr.length-2].close;
    const chg=((p-prev)/prev*100).toFixed(2),up=chg>=0;
    const sparkId='spark_'+a.id;
    html+=`<div class="asset-card">
      <div class="asset-card-header">
        <div class="asset-card-info"><h4>${a.symbol}</h4><span>${a.name} · ${badge(a.type,a.type.toLowerCase())} · ${a.exchange}</span></div>
      </div>
      <div class="asset-price ${up?'ticker-up':'ticker-down'}">$${fmt(p)}</div>
      <div class="asset-change ${up?'ticker-up':'ticker-down'}">${up?'▲':'▼'} ${Math.abs(chg)}% (24h)</div>
      <div class="sparkline-wrap"><canvas id="${sparkId}"></canvas></div>
    </div>`;
  });
  $('#assetsGrid').innerHTML=html;
  ASSETS.forEach(a=>{
    const arr=PRICES[a.id],ctx=document.getElementById('spark_'+a.id);
    new Chart(ctx,{type:'line',data:{labels:arr.map(p=>p.date.slice(5)),datasets:[{data:arr.map(p=>p.close),borderColor:'#58A6FF',backgroundColor:'rgba(88,166,255,0.1)',fill:true,tension:0.4,pointRadius:0,borderWidth:2}]},
      options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{display:false},y:{display:false}}}});
  });
}

// ── Orders ──
function initOrders(){
  renderOrders('ALL');
  $$('#orderFilters .filter-btn').forEach(btn=>{
    btn.onclick=()=>{$$('#orderFilters .filter-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');renderOrders(btn.dataset.filter)};
  });
}
function renderOrders(filter){
  const list=ORDERS.filter(o=>filter==='ALL'||o.status===filter);
  const rows=list.map(o=>{const u=userById(o.uid),a=assetById(o.aid);
    return [o.id,u.username,a.symbol,badge(o.type,o.type.toLowerCase()),o.mode,o.qty,o.limit?'$'+fmt(o.limit):'—',badge(o.status,o.status.toLowerCase()),o.placed.slice(0,10)];});
  $('#ordersTable').innerHTML=makeTable(['ID','User','Symbol','Type','Mode','Qty','Limit $','Status','Placed'],rows);
}

// ── Transactions ──
function initTxns(){
  const rows=TXNS.slice().reverse().map(t=>{const u=userById(t.uid),a=assetById(t.aid);
    return [t.id,u.username,a.symbol,badge(t.type,t.type.toLowerCase()),t.qty,'$'+fmt(t.price),'$'+fmt(t.total),'$'+fmt(t.fee),'$'+fmt(t.net)];});
  $('#txnTable').innerHTML=makeTable(['TXN','User','Symbol','Type','Qty','Price/Unit','Total','Fee','Net'],rows);
}

// ── Place Order ──
function initPlaceOrder(){
  const uSel=$('#orderUser'),aSel=$('#orderAsset');
  uSel.innerHTML=USERS.filter(u=>u.status==='ACTIVE').map(u=>`<option value="${u.id}">${u.id} — ${u.username}</option>`).join('');
  aSel.innerHTML=ASSETS.filter(a=>a.active==='Y').map(a=>`<option value="${a.id}">${a.symbol} — ${a.name}</option>`).join('');

  let orderType='BUY';
  $('#typeBuy').onclick=()=>{orderType='BUY';$('#typeBuy').classList.add('active');$('#typeSell').classList.remove('active')};
  $('#typeSell').onclick=()=>{orderType='SELL';$('#typeSell').classList.add('active');$('#typeBuy').classList.remove('active')};

  function updateSummary(){
    const aid=+aSel.value,qty=parseFloat($('#orderQty').value)||0;
    const lp=$('#orderPrice').value?parseFloat($('#orderPrice').value):latestPrice(aid);
    const total=qty*lp,fee=total*0.0015,net=total-fee;
    if(qty>0)$('#orderSummary').innerHTML=`Price: <span class="val">$${fmt(lp)}</span> · Total: <span class="val">$${fmt(total)}</span> · Fee: <span class="val">$${fmt(fee)}</span> · Net: <span class="val">$${fmt(net)}</span>`;
    else $('#orderSummary').innerHTML='Enter quantity to see summary';
  }
  $('#orderQty').oninput=updateSummary;$('#orderPrice').oninput=updateSummary;aSel.onchange=updateSummary;

  $('#submitOrder').onclick=()=>{
    const uid=+uSel.value,aid=+aSel.value,qty=parseFloat($('#orderQty').value);
    const res=$('#orderResult');
    if(!qty||qty<=0){res.className='order-result error';res.textContent='✗ Enter a valid quantity';return}
    const user=userById(uid);
    if(user.status!=='ACTIVE'){res.className='order-result error';res.textContent=`✗ Order rejected: account is ${user.status}`;return}
    const price=$('#orderPrice').value?parseFloat($('#orderPrice').value):latestPrice(aid);
    const total=qty*price,fee=+(total*0.0015).toFixed(6),net=+(total-fee).toFixed(6);
    const newOid=Math.max(...ORDERS.map(o=>o.id),0)+1;
    const newTid=Math.max(...TXNS.map(t=>t.id),0)+1;
    const now=new Date().toISOString();
    ORDERS.push({id:newOid,uid,aid,type:orderType,mode:$('#orderMode').value,qty,limit:price,status:'FILLED',placed:now,filled:now});
    TXNS.push({id:newTid,oid:newOid,uid,aid,type:orderType,qty,price,total,fee,net,at:now});
    const w=WALLETS.find(x=>x.uid===uid&&x.aid===aid);
    const delta=orderType==='BUY'?qty:-qty;
    if(w)w.balance=Math.max(0,w.balance+delta);
    else WALLETS.push({id:WALLETS.length+1,uid,aid,balance:Math.max(0,delta)});
    res.className='order-result success';
    res.textContent=`✓ Order #${newOid} placed! Total=$${fmt(total)}  Fee=$${fmt(fee)}`;
    toast(`Order #${newOid} executed successfully`,'success');
    $('#orderQty').value='';$('#orderPrice').value='';$('#orderSummary').innerHTML='';
  };
}

// ── SQL Reference ──
function initSQL(){
  const wrap=$('#sqlSections');
  wrap.innerHTML=SQL_SECTIONS.map((s,i)=>`<div class="sql-accordion${i===0?' open':''}">
    <div class="sql-accordion-header" onclick="this.parentElement.classList.toggle('open')">
      <h4>${s.title}</h4><span class="arrow">▼</span></div>
    <div class="sql-accordion-body">
      <p class="sql-desc">${s.desc}</p>
      <div class="sql-code-wrap">
        <button class="copy-btn" onclick="navigator.clipboard.writeText(this.nextElementSibling.textContent);this.textContent='Copied!';setTimeout(()=>this.textContent='Copy',1500)">Copy</button>
        <pre class="sql-code">${highlightSQL(s.code)}</pre>
      </div>
    </div></div>`).join('');
}

function highlightSQL(code){
  const kws=['CREATE','TABLE','OR','REPLACE','PROCEDURE','FUNCTION','TRIGGER','BEGIN','END','IF','THEN','ELSE','RETURN','DECLARE','AS','IS','IN','OUT','NOT','NULL','DEFAULT','PRIMARY','KEY','UNIQUE','REFERENCES','CHECK','SELECT','INSERT','INTO','VALUES','UPDATE','SET','DELETE','FROM','WHERE','AND','JOIN','ON','ORDER','BY','GROUP','HAVING','DESC','ASC','COMMIT','ROLLBACK','WHEN','MATCHED','MERGE','USING','FOR','EACH','ROW','LOOP','OPEN','FETCH','CLOSE','EXCEPTION','RAISE_APPLICATION_ERROR','AFTER','BEFORE','CURSOR','NUMBER','VARCHAR2','CHAR','DATE','TIMESTAMP','REAL','INTEGER','TEXT','ROUND','NVL','SUM','COUNT','MAX','ROWNUM','SYSTIMESTAMP','SYSDATE','TRUNC','CURRENT_TIMESTAMP'];
  let h=code.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  h=h.replace(/(--.*)/gm,'<span class="cm">$1</span>');
  h=h.replace(/'([^']*)'/g,"<span class='str'>'$1'</span>");
  h=h.replace(/\b(\d+\.?\d*)\b/g,'<span class="num">$1</span>');
  const re=new RegExp('\\b('+kws.join('|')+')\\b','gi');
  h=h.replace(re,(m)=>`<span class="kw">${m}</span>`);
  return h;
}

// ── Init ──
initDashboard();
