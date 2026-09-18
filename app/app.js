"use strict";
const DB = window.FK_DATA || JSON.parse(document.getElementById('data').textContent);
const MENUS = DB.menus, LIBRARY = DB.library, SHOWPIECES = DB.showpieces || [];

/* ---------- persistence (per-viewer, may be unavailable) ---------- */
const store = {
  get(k, d){ try{ const v = localStorage.getItem('fk_'+k); return v ? JSON.parse(v) : d; }catch(e){ return d; } },
  set(k, v){ try{ localStorage.setItem('fk_'+k, JSON.stringify(v)); }catch(e){} }
};
let favs = store.get('favs', []);
let cart = store.get('cart', []).map(c => typeof c === 'string' ? {kind:'menu', id:c} : c);
function cartKey(e){ return e.kind === 'menu' ? 'm|' + e.id : 'r|' + e.id; }
function recipeKey(r){ return (r.menuId || r.chapterId || 'x') + '|' + r.title; }
function inCart(k){ return cart.some(e => cartKey(e) === k); }
function toggleCart(e){
  const k = cartKey(e);
  cart = inCart(k) ? cart.filter(x => cartKey(x) !== k) : cart.concat(e);
  store.set('cart', cart);
}
let checked = store.get('checked', {});    // ticked shopping items
let theme = store.get('theme', null);
if (theme) document.documentElement.setAttribute('data-theme', theme);

/* ---------- index ---------- */
MENUS.forEach(m => {
  m.courses = {};
  m.recipes.forEach(r => { (m.courses[r.course] = m.courses[r.course] || []).push(r); });
  const ing = m.recipes.flatMap(r => r.ingredients.map(i => i.text)).join(' ');
  const meth = m.recipes.map(r => r.title + ' ' + r.method.join(' ')).join(' ');
  m.hay = (m.title+' '+m.lead+' '+m.region+' '+(m.season||[]).join(' ')+' '+(m.proteins||[]).join(' ')+' '+
    (m.occasion||[]).join(' ')+' '+(m.technique||[]).join(' ')+' '+(m.wood||[]).join(' ')+' '+
    (m.special||[]).join(' ')+' '+ing+' '+meth).toLowerCase();
});
const ALLR = [];
MENUS.forEach(m => m.recipes.forEach(r => ALLR.push(Object.assign({}, r, {
  menuId:m.id, menuTitle:m.title, region:m.region, season:m.season, proteins:m.proteins,
  complexity:m.complexity, occasion:m.occasion, diet:m.diet, kettles:m.kettles,
  accessories:m.accessories, leadHours:m.leadHours, continent:m.continent, cost:m.cost,
  totalMin:m.totalMin, activeMin:m.activeMin, wood:m.wood, technique:m.technique,
  coldOK:m.coldOK, heat:m.heat, special:m.special,
  hay:(r.title+' '+r.native+' '+r.meta+' '+r.headnote+' '+r.ingredients.map(i=>i.text).join(' ')+' '+
       r.method.join(' ')+' '+m.title+' '+m.region+' '+
       (r.plating?r.plating.style+' '+r.plating.text:'')).toLowerCase()
}))));
SHOWPIECES.forEach(r => {
  r.menuTitle = 'Cook to Impress';
  r.hay = (r.title+' '+r.native+' '+r.meta+' '+r.headnote+' '+
    r.ingredients.map(i=>i.text).join(' ')+' '+r.method.join(' ')+' showpiece impress '+
    (r.plating?r.plating.style+' '+r.plating.text:'')).toLowerCase();
  ALLR.push(r);
});
LIBRARY.forEach(r => r.hay = (r.title+' '+r.native+' '+r.chapter+' '+r.headnote+' '+
  r.ingredients.map(i=>i.text).join(' ')+' '+r.method.join(' ')).toLowerCase());

/* ---------- facet definitions ---------- */
const uniq = (arr) => [...new Set(arr)].sort();
const flat = (key) => uniq(MENUS.flatMap(m => m[key] || []));
const LEAD = [
  {label:'Same day', test:m => m.leadHours <= 6},
  {label:'Night before', test:m => m.leadHours > 6 && m.leadHours <= 24},
  {label:'Two days', test:m => m.leadHours > 24}
];
const TIME = [
  {label:'Under 2 hr', test:m => m.totalMin <= 120},
  {label:'2–5 hr', test:m => m.totalMin > 120 && m.totalMin <= 300},
  {label:'All day', test:m => m.totalMin > 300}
];
const FACETS = [
  {id:'season',   label:'Season',       type:'arr',  key:'season',      opts:flat('season')},
  {id:'protein',  label:'Meat & fish',  type:'arr',  key:'proteins',    opts:flat('proteins')},
  {id:'continent',label:'Part of world',type:'val',  key:'continent',   opts:uniq(MENUS.map(m=>m.continent))},
  {id:'region',   label:'Country / region', type:'val', key:'region',   opts:uniq(MENUS.map(m=>m.region))},
  {id:'occasion', label:'Occasion',     type:'arr',  key:'occasion',    opts:flat('occasion')},
  {id:'complexity',label:'Complexity',  type:'val',  key:'complexity',  opts:['Light','Moderate','Heavy','All day']},
  {id:'time',     label:'Total time',   type:'fn',   fns:TIME},
  {id:'lead',     label:'Lead time',    type:'fn',   fns:LEAD},
  {id:'kettles',  label:'Kettles',      type:'val',  key:'kettles',     opts:[1,2], fmt:v=>v===1?'One kettle':'Two kettles'},
  {id:'accessory',label:'Accessory',    type:'arr',  key:'accessories', opts:flat('accessories'), extra:'None'},
  {id:'technique',label:'Technique',    type:'arr',  key:'technique',   opts:flat('technique')},
  {id:'wood',     label:'Wood',         type:'arr',  key:'wood',        opts:flat('wood')},
  {id:'diet',     label:'Dietary',      type:'arr',  key:'diet',        opts:flat('diet')},
  {id:'cost',     label:'Cost',         type:'val',  key:'cost',        opts:['$','$$','$$$','$$$$']},
  {id:'heat',     label:'Spice level',  type:'val',  key:'heat',        opts:[1,2,3,5], fmt:v=>['','Mild','Medium','Hot','','Fierce'][v]},
  {id:'cold',     label:'Cold weather', type:'bool', key:'coldOK',      opts:[true], fmt:()=>'Works in winter'},
  {id:'special',  label:'Special order',type:'arr',  key:'special',     opts:flat('special'), extra:'Nothing unusual'},
  {id:'impress',  label:'Showpiece',    type:'bool', key:'impress',     opts:[true], fmt:()=>'Has a moment'},
  {id:'plate',    label:'Served as',    type:'plate', opts:[...new Set(MENUS.flatMap(m=>m.recipes).filter(r=>r.plating).map(r=>r.plating.style))].sort()},
];
const COURSES = ['Starter','Main','Side','Sauce','Dessert','Drink','Showpiece'];

/* ---------- state ---------- */
const state = {
  view:'menus', q:'', sel:{}, course:null, detail:null, recipe:null,
  openGroups: store.get('groups', {season:true, protein:true, continent:true, complexity:true, kettles:true}),
  scale: store.get('scale', 8),
  bOpen:{}, bQ:{}, bSort:{}
};
FACETS.forEach(f => state.sel[f.id] = []);

/* ---------- matching ---------- */
function facetMatch(f, m){
  const sel = state.sel[f.id];
  if (!sel.length) return true;
  if (f.type === 'arr'){
    const vals = m[f.key] || [];
    return sel.some(s => s === f.extra ? vals.length === 0 : vals.includes(s));
  }
  if (f.type === 'fn') return sel.some(s => f.fns.find(x => x.label === s).test(m));
  if (f.type === 'plate'){
    if (m.plating) return sel.includes(m.plating.style);
    if (m.recipes) return m.recipes.some(r => r.plating && sel.includes(r.plating.style));
    return false;
  }
  if (f.type === 'bool') return !!m[f.key];
  return sel.some(s => String(m[f.key]) === String(s));
}
function filterMenus(){
  const q = state.q.trim().toLowerCase();
  return MENUS.filter(m => FACETS.every(f => facetMatch(f, m)) && (!q || m.hay.includes(q)));
}
function filterRecipes(){
  const q = state.q.trim().toLowerCase();
  return ALLR.filter(r => FACETS.every(f => facetMatch(f, r)) &&
    (!state.course || r.course === state.course) && (!q || r.hay.includes(q)));
}
function filterLibrary(){
  const q = state.q.trim().toLowerCase();
  return LIBRARY.filter(r => !q || r.hay.includes(q));
}
function activeCount(){ return FACETS.reduce((n,f)=>n+state.sel[f.id].length,0); }

/* ---------- helpers ---------- */
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function hl(text){
  const q = state.q.trim();
  if (!q || q.length < 2) return esc(text);
  const re = new RegExp('(' + q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&') + ')', 'ig');
  return esc(text).replace(re, '<mark>$1</mark>');
}

/* a small, hand-verified set of technique/ingredient terms worth a further-reading link —
   every URL here was checked to actually resolve, not guessed */
const GLOSSARY = [
  ['two-zone fire', 'https://en.wikipedia.org/wiki/Indirect_grilling'],
  ['reverse sear', 'https://en.wikipedia.org/wiki/Searing'],
  ['dry brine', 'https://en.wikipedia.org/wiki/Dry_brining'],
  ['spatchcock', 'https://en.wikipedia.org/wiki/Butterflying'],
  ['flanken', 'https://en.wikipedia.org/wiki/Short_ribs'],
  ['fennel pollen', 'https://en.wikipedia.org/wiki/Fennel'],
  ['schmaltz', 'https://en.wikipedia.org/wiki/Schmaltz'],
  ['tallow', 'https://en.wikipedia.org/wiki/Tallow'],
  ['robata', 'https://en.wikipedia.org/wiki/Robatayaki'],
  ['yakitori', 'https://en.wikipedia.org/wiki/Yakitori'],
  ['porchetta', 'https://en.wikipedia.org/wiki/Porchetta'],
  ['asado', 'https://en.wikipedia.org/wiki/Asado'],
];
/* link the first mention of each glossary term in a string that has already been through
   esc()/hl() — splits on existing tags so it never rewrites inside a <mark> or attribute */
function glossify(safeHtml){
  const used = new Set();
  return safeHtml.split(/(<[^>]+>)/g).map(part => {
    if (part.startsWith('<')) return part;
    let out = part;
    GLOSSARY.forEach(([term, url]) => {
      if (used.has(term)) return;
      const re = new RegExp('\\b(' + term.replace(/[.*+?^${}()|[\]\\]/g,'\\$&') + ')\\b', 'i');
      if (re.test(out)){
        used.add(term);
        out = out.replace(re, '<a class="gloss" href="' + url + '" target="_blank" rel="noopener" title="More about $1">$1</a>');
      }
    });
    return out;
  }).join('');
}
const HRS = h => h <= 6 ? 'Same day' : h <= 24 ? 'Night before'
  : h <= 72 ? Math.round(h/24) + ' days ahead' : Math.round(h/24) + ' days ahead';
const MINS = t => t >= 60 ? (t % 60 ? Math.floor(t/60)+' hr '+(t%60)+' min' : t/60 + ' hr') : t + ' min';

/* quantity scaling: handles 2, 1½, ½, 1.5, ranges like 4–5 */
const VULGAR = {'½':.5,'¼':.25,'¾':.75,'⅓':1/3,'⅔':2/3,'⅛':.125,'⅜':.375,'⅝':.625,'⅞':.875};
function fmtQty(n){
  if (!isFinite(n)) return '';
  const whole = Math.floor(n + 1e-9), frac = n - whole;
  const near = Object.entries(VULGAR).find(([,v]) => Math.abs(frac - v) < 0.02);
  if (near) return (whole ? whole : '') + near[0];
  if (Math.abs(n - Math.round(n)) < 0.02) return String(Math.round(n));
  return String(Math.round(n * 100) / 100);
}
function scaleText(txt, factor){
  if (factor === 1) return txt;
  // Only the first quantity in a line is scaled — later numbers are pan sizes,
  // can sizes, inch measurements and temperatures, which must not move.
  const re = /(\d+(?:\.\d+)?)?\s*([\u00bd\u00bc\u00be\u2153\u2154\u215b\u215c\u215d\u215e])|(\d+(?:\.\d+)?)/;
  const mm = txt.match(re);
  if (!mm) return txt;
  const [full, w, v, plain] = mm;
  let n = v ? (w ? parseFloat(w) : 0) + VULGAR[v] : parseFloat(plain);
  if (!isFinite(n)) return txt;
  const after = txt.slice(mm.index + full.length);
  if (/^\s*(?:°|-?inch|-inch|in\b)/i.test(after)) return txt;   // 1½-inch discs
  return txt.slice(0, mm.index) + fmtQty(n * factor) + after;
}


/* ---------- capacity: what the equipment can actually take ---------- */
const K = DB.kettle;
const r1 = n => Math.round(n * 10) / 10;
function dutchFor(qt){
  const fit = K.dutchSizes.find(x => qt <= x * 0.85);
  if (fit) return 'one ' + fit + '-qt Dutch oven';
  const big = Math.ceil(qt / (12 * 0.85)), six = Math.ceil(qt / (6 * 0.85));
  return big + ' × 12-qt, or ' + six + ' × 6-qt pots';
}
function verdictFor(item, f){
  const t = item.type;
  if (t === 'dutch'){
    const qt = item.qt8 * f;
    return {need: r1(qt) + ' qt capacity', verdict: dutchFor(qt)};
  }
  if (t === 'skillet'){
    const n = Math.ceil(item.loads8 * f - 0.001);
    return {need: n + ' pan load' + (n>1?'s':''),
            verdict: n === 1 ? 'one 12-inch skillet' : n + ' × 12-inch skillet, or ' + n + ' rounds in one'};
  }
  if (t === 'grate'){
    const need = item.sqin8 * f;
    const cap = item.zone === 'direct' ? K.grateDirect : item.zone === 'indirect' ? K.grateIndirect : K.grateFull;
    const n = Math.ceil(need / cap - 0.001);
    return {need: Math.round(need) + ' sq in of ' + item.zone + ' grate',
            verdict: n <= 1 ? 'fits one kettle in a single load'
              : n === 2 ? 'two loads — use both kettles, or cook in two rounds'
              : n + ' loads — both kettles and ' + Math.ceil(n/2) + ' rounds each'};
  }
  if (t === 'spit'){
    const lb = item.lb8 * f, len = item.len8 * f;
    const n = Math.max(Math.ceil(lb / K.spitLb - 0.001), Math.ceil(len / K.spitLen - 0.001));
    return {need: r1(lb) + ' lb on ' + r1(len) + ' in of spit',
            verdict: n <= 1 ? 'one spit load' : n + ' spit loads — cook in rounds, or move part of it to the second kettle'};
  }
  if (t === 'stone'){
    const u = Math.round(item.units8 * f), mins = Math.round(u * item.minEach);
    return {need: u + ' off the stone', verdict: '≈ ' + mins + ' min of continuous stone work'};
  }
  if (t === 'vortex'){
    const p = Math.round(item.pieces8 * f), n = Math.ceil(p / K.vortexPieces - 0.001);
    return {need: p + ' pieces', verdict: n <= 1 ? 'one vortex load' : n + ' vortex loads'};
  }
  if (t === 'steamer'){
    const qt = item.qt8 * f, n = Math.ceil(qt / K.steamerQt - 0.001);
    return {need: r1(qt) + ' qt of steamer', verdict: n <= 1 ? 'one large roasting pan' :
            n + ' pans — steam on both kettles at once, or run ' + n + ' rounds'};
  }
  if (t === 'fry'){
    const n = Math.ceil(f - 0.001);
    return {need: 'same ' + item.qt8 + ' qt of oil', verdict: n <= 1 ? 'one pot, one pass' :
            'one pot, ≈ ' + Math.round(f * 10) / 10 + '× the frying passes'};
  }
  if (t === 'pan'){
    const n = Math.ceil(item.count8 * f - 0.001);
    return {need: n + ' × ' + item.name, verdict: n === 1 ? 'one ' + item.name :
            n + ' × ' + item.name + ', or bake in ' + n + ' rounds'};
  }
  return {need: '', verdict: ''};
}
function capRows(items, f){
  return items.map(it => {
    const now = verdictFor(it, f), base = verdictFor(it, 1);
    return Object.assign({}, now, {
      label: it.label, note: it.note || '',
      changed: now.verdict !== base.verdict, base: base.verdict
    });
  });
}
function fuelAt(m, f){ return Math.round((m.fuel * (f <= 1 ? f : 1 + (f - 1) * 0.8)) * 2) / 2; }
function activeAt(m, f){ return Math.round(m.activeMin * (f <= 1 ? f : 1 + (f - 1) * 0.6) / 5) * 5; }

function capPanel(m, f, items){
  const rows = capRows(items, f);
  const changed = rows.filter(r => r.changed);
  const over = state.scale > m.maxServes;
  let h = '<div class="sect"><h2>Fits on two kettles?</h2>';
  if (over){
    h += '<div class="callout warn"><span class="lbl">Past the limit of two kettles</span>' +
      'This menu tops out at about <strong>' + m.maxServes + '</strong> without a third grill. ' +
      'You can still cook it for ' + state.scale + ' — but only by running extra rounds and serving in waves. ' +
      (m.capNotes.length ? esc(m.capNotes[0]) : '') + '</div>';
  } else if (f === 1){
    h += '<div class="callout ahead"><span class="lbl">As written</span>' +
      'Everything below fits two 22-inch kettles as the recipes stand. Comfortable ceiling for this menu: about ' +
      m.maxServes + ' people.</div>';
  } else if (!changed.length){
    h += '<div class="callout ahead"><span class="lbl">No equipment changes</span>' +
      'At ' + state.scale + ', every vessel and every zone still works as written.</div>';
  } else {
    h += '<div class="callout warn"><span class="lbl">' + changed.length + ' thing' +
      (changed.length>1?'s change':' changes') + ' at ' + state.scale + '</span>' +
      'Ingredient quantities scale. Pots, grates and spits do not — here is what you actually need.</div>';
  }
  h += '<div class="captable">';
  rows.forEach(r => {
    h += '<div class="caprow' + (r.changed ? ' chg' : '') + '">' +
      '<div class="cl">' + esc(r.label) + '</div>' +
      '<div class="cn">' + esc(r.need) + '</div>' +
      '<div class="cv">' + esc(r.verdict) +
        (r.changed ? '<span class="was">was: ' + esc(r.base) + '</span>' : '') +
        (r.note ? '<span class="cnote">' + esc(r.note) + '</span>' : '') +
      '</div></div>';
  });
  h += '</div>';
  h += '<div class="captable" style="margin-top:10px">' +
    '<div class="caprow' + (f !== 1 ? ' chg' : '') + '"><div class="cl">Charcoal</div>' +
      '<div class="cn">' + fuelAt(m, f) + ' chimneys</div>' +
      '<div class="cv">across both kettles' + (f !== 1 ? '<span class="was">was: ' + m.fuel + '</span>' : '') + '</div></div>' +
    '<div class="caprow' + (f !== 1 ? ' chg' : '') + '"><div class="cl">Active time</div>' +
      '<div class="cn">' + MINS(activeAt(m, f)) + '</div>' +
      '<div class="cv">hands-on at the fire' + (f !== 1 ? '<span class="was">was: ' + MINS(m.activeMin) + '</span>' : '') + '</div></div>' +
    '</div>';
  m.capNotes.forEach((n, i) => { if (!(over && i === 0))
    h += '<div class="callout note"><span class="lbl">Scaling this menu</span>' + esc(n) + '</div>'; });
  return h + '</div>';
}

/* ---------- render: facets ---------- */
function isOpen(id){ return state.openGroups[id] === true; }
function renderFacets(){
  const box = document.getElementById('facets');
  let h = '<div class="resetbar"><span class="count">' + activeCount() + ' filters</span>' +
          (activeCount() ? '<button class="linkbtn" data-act="reset">Clear all</button>' : '') + '</div>';
  FACETS.forEach(f => {
    const open = isOpen(f.id) || state.sel[f.id].length > 0;
    const opts = f.type === 'fn' ? f.fns.map(x => x.label) : (f.opts || []).slice();
    if (f.extra) opts.push(f.extra);
    h += '<div class="fgroup" data-open="' + (open ? 'true':'false') + '">' +
      '<button data-grp="' + f.id + '">' + f.label +
      (state.sel[f.id].length ? ' <span style="color:var(--ember)">· ' + state.sel[f.id].length + '</span>' : '') +
      '<span class="chev">▾</span></button><div class="fbody">';
    opts.forEach(o => {
      const on = state.sel[f.id].includes(o) || (f.type==='bool' && state.sel[f.id].length);
      const label = f.fmt ? f.fmt(o) : o;
      h += '<button class="chip" aria-pressed="' + (on?'true':'false') +
           '" data-f="' + f.id + '" data-v="' + esc(String(o)) + '">' + esc(String(label)) + '</button>';
    });
    h += '</div></div>';
  });
  box.innerHTML = h;
  document.getElementById('fcount').textContent = activeCount() ? '· ' + activeCount() : '';
}

/* ---------- render: cards ---------- */
/* CC-licensed photos are sourced with attribution attached. `credit:true` prints it
   inline (required wherever the photo isn't inside another clickable element — an <a>
   nested in a <button>, like a card, is invalid HTML and double-fires the card's own click) */
function photoTag(img, title, cls, credit){
  if (!img || !img.file) return '';
  // the image sits in its own fixed-aspect-ratio, clipped frame; the credit line is a
  // sibling *outside* that frame so a `overflow:hidden` box for cropping the photo can
  // never also clip the attribution text (a real bug the first version of this had)
  return '<div class="' + cls + '">' +
    '<div class="ph-frame"><img src="./images/' + img.file + '" alt="' + esc(title || '') +
      '" loading="lazy" onerror="this.closest(\'.' + cls + '\').remove()"></div>' +
    (credit && img.credit ? '<a class="credit" href="' + esc(img.sourceUrl || img.creditUrl || '#') +
      '" target="_blank" rel="noopener">Photo: ' + esc(img.credit) +
      (img.license ? ' (' + esc(img.license) + ')' : '') + '</a>' : '') +
    '</div>';
}
function menuCard(m){
  const on = favs.includes(m.id);
  return '<div class="cardwrap"><button class="card" data-menu="' + m.id + '">' +
    photoTag(m.image, m.title, 'card-photo', false) +
    '<div class="kicker">' + esc(m.region) + '</div>' +
    '<h3>' + hl(m.title) + '</h3>' +
    '<p>' + hl(m.lead.replace(/ · /g, ' · ')) + '</p>' +
    '<div class="meta-row">' +
      '<span class="tag hot">' + esc((m.season||[]).join('/')) + '</span>' +
      '<span class="tag">' + esc((m.proteins||[]).join(', ')) + '</span>' +
      '<span class="tag">' + (m.kettles === 1 ? '1 kettle' : '2 kettles') + '</span>' +
      '<span class="tag">' + esc(m.complexity) + '</span>' +
      '<span class="tag">' + MINS(m.totalMin) + '</span>' +
      (m.leadHours > 24 ? '<span class="tag hot">48 hr lead</span>' : '') +
      (m.maxServes < 12 ? '<span class="tag hot">caps at ' + m.maxServes + '</span>' : '') +
      (m.impress ? '<span class="tag hot">★ showpiece</span>' : '') +
    '</div></button>' +
    '<button class="fav" data-fav="' + m.id + '" aria-pressed="' + (on?'true':'false') + '" aria-label="Favourite">' +
    (on ? '★' : '☆') + '</button></div>';
}
function recipeRow(r, i){
  return '<button class="rrow" data-recipe="' + i + '">' +
    '<span class="c">' + esc(r.course) + '</span>' +
    '<span class="t">' + (r.impress ? '★ ' : '') + hl(r.title) + (r.native ? ' <span class="drop">' + esc(r.native) + '</span>' : '') + '</span>' +
    '<span class="m">' + (r.plating ? '<span class="tag">' + esc(r.plating.style) + '</span> ' : '') +
    esc(r.menuTitle || r.chapter || '') + '</span></button>';
}

/* ---------- render: views ---------- */
function viewMenus(){
  const list = filterMenus();
  if (!list.length) return emptyState();
  const favList = list.filter(m => favs.includes(m.id));
  let h = '<div class="resetbar"><span class="count">' + list.length + ' of ' + MENUS.length + ' menus</span></div>';
  if (favList.length && !state.q){
    h += '<div class="sect"><h2>Saved</h2><div class="grid">' + favList.map(menuCard).join('') + '</div></div>';
  }
  const parts = [...new Set(list.map(m => m.part))];
  parts.forEach(p => {
    h += '<div class="sect"><h2>' + esc(p) + '</h2><div class="grid">' +
         list.filter(m => m.part === p).map(menuCard).join('') + '</div></div>';
  });
  return h;
}
function viewRecipes(){
  const list = filterRecipes();
  let h = '<div class="courserow">' +
    '<button class="chip" aria-pressed="' + (!state.course?'true':'false') + '" data-course="">All courses</button>' +
    COURSES.map(c => '<button class="chip" aria-pressed="' + (state.course===c?'true':'false') +
      '" data-course="' + c + '">' + c + 's</button>').join('') + '</div>';
  h += '<div class="resetbar"><span class="count">' + list.length + ' recipes</span></div>';
  if (!list.length) return h + emptyState();
  window.__rlist = list;
  h += '<div class="rlist">' + list.map((r,i) => recipeRow(r,i)).join('') + '</div>';
  return h;
}
function viewLibrary(){
  const list = filterLibrary();
  window.__rlist = list;
  let h = '<div class="resetbar"><span class="count">The Common Library · ' + list.length +
          ' shared doughs, sauces, rubs and marinades</span></div>';
  const chapters = [...new Set(list.map(r => r.chapter))];
  chapters.forEach(c => {
    h += '<div class="sect"><h2>' + esc(c) + '</h2><div class="rlist">' +
      list.map((r,i) => [r,i]).filter(([r]) => r.chapter === c)
          .map(([r,i]) => '<button class="rrow" data-recipe="' + i + '">' +
            '<span class="c">Library</span><span class="t">' + hl(r.title) +
            (r.native ? ' <span class="drop">' + esc(r.native) + '</span>' : '') + '</span>' +
            '<span class="m">' + esc(r.meta.split('·')[0].trim()) + '</span></button>').join('') +
      '</div></div>';
  });
  return h;
}
function emptyState(){
  return '<div class="empty"><h3>Nothing matches</h3><p>Try clearing a filter or searching for an ingredient.</p>' +
         '<p style="margin-top:14px"><button class="btn" data-act="reset">Clear filters</button></p></div>';
}

/* ---------- shopping list ---------- */

/* ---------- export as text ----------
   window.print() is blocked inside the sandboxed artifact frame, so it silently
   does nothing. Copying to the clipboard works, with a selectable panel as a
   fallback for browsers that refuse clipboard access too. ---------- */
function stripHTML(html){
  const d = document.createElement('div');
  d.innerHTML = html;
  return (d.textContent || '').replace(/\n{3,}/g, '\n\n').replace(/[ \t]+\n/g, '\n').trim();
}
function recipeText(r, factor){
  let t = r.title + (r.native ? ' (' + r.native + ')' : '') + '\n' + r.meta + '\n';
  if (r.headnote) t += '\n' + r.headnote + '\n';
  if (r.ingredients.length){
    t += '\nINGREDIENTS\n';
    r.ingredients.forEach(i => {
      t += i.type === 'sub' ? '\n  ' + i.text.toUpperCase() + '\n'
                            : '  - ' + scaleText(i.text, factor || 1) + '\n';
    });
  }
  if (r.method.length){
    t += '\nMETHOD\n';
    r.method.forEach((m, i) => { t += '  ' + (i+1) + '. ' + m + '\n'; });
  }
  r.notes.forEach(n => { t += '\n' + n.label.toUpperCase() + ': ' + n.text + '\n'; });
  if (r.plating) t += '\n' + (r.plating.style === 'keeping' ? 'KEEPING' : 'TO THE TABLE (' + r.plating.style + ')') + ': ' + r.plating.text + '\n';
  return t;
}
function textForCurrentView(){
  const factor = state.scale / 8;
  if (state.recipe !== null) return recipeText(state.recipe, factor);

  if (state.detail){
    const m = state.detail;
    let t = m.title.toUpperCase() + '\n' + m.region + ' · ' + m.part + '\n' + m.lead + '\n';
    t += '\nServes ' + state.scale + ' · ' + m.complexity + ' · ' +
         (m.kettles === 1 ? 'one kettle' : 'two kettles') +
         ' · ' + ((m.accessories||[]).join(', ') || 'no accessories') + '\n';
    t += 'Active ' + MINS(m.activeMin) + ' · total ' + MINS(m.totalMin) +
         ' · start prep ' + HRS(m.leadHours) + ' · ' + fuelAt(m, factor) + ' chimneys\n';
    if (m.blocks.menu)     t += '\n--- THE MENU ---\n' + stripHTML(m.blocks.menu) + '\n';
    if (m.blocks.grill)    t += '\n--- GRILL PLAN ---\n' + stripHTML(m.blocks.grill) + '\n';
    if (m.blocks.timeline) t += '\n--- PREP COUNTDOWN ---\n' + stripHTML(m.blocks.timeline) + '\n';
    if (m.blocks.shopping) t += '\n--- SHOPPING LIST (for 8) ---\n' + stripHTML(m.blocks.shopping) + '\n';
    t += '\n--- RECIPES ---\n';
    COURSES.forEach(c => (m.courses[c] || []).forEach(r => {
      t += '\n\n' + '='.repeat(48) + '\n' + recipeText(r, factor);
    }));
    return t;
  }

  if (state.view === 'list'){
    const items = cart.flatMap(id => { const m = MENUS.find(x => x.id === id); return m ? parseShopping(m) : []; });
    let t = 'SHOPPING LIST\n' + cart.map(id => (MENUS.find(m=>m.id===id)||{}).title).join(' · ') + '\n';
    [...new Set(items.map(i => i.cat))].forEach(c => {
      t += '\n' + c.toUpperCase() + '\n';
      items.filter(i => i.cat === c).forEach(i => {
        t += (checked[i.menuId + '|' + i.item] ? '  [x] ' : '  [ ] ') + i.item +
             (cart.length > 1 ? '   (' + i.from + ')' : '') + '\n';
      });
    });
    return t;
  }

  if (state.view === 'build'){
    const items = build.items(), rep = builderReport(items);
    let t = 'MY MENU\n';
    BUILD_COURSES.forEach(c => items.filter(i => i.course === c).forEach(i => {
      t += '  ' + c.padEnd(9) + i.title + '  (' + i.menuTitle + ')\n';
    }));
    t += '\nActive ~' + MINS(rep.activeMin) + ' · ~' + rep.fuel + ' chimneys · start prep ' + HRS(rep.lead) + '\n';
    if (rep.warnings.length) t += '\nCHECK THIS\n' + rep.warnings.map(w => '  - ' + w).join('\n') + '\n';
    t += '\n\n' + items.map(i => recipeText(i, 1)).join('\n\n' + '='.repeat(48) + '\n');
    return t;
  }
  return '';
}
function exportText(){
  const text = textForCurrentView();
  if (!text) return;
  const done = ok => {
    const bar = document.getElementById('toast');
    if (bar){ bar.textContent = ok ? 'Copied to clipboard' : 'Select the text below and copy';
              bar.style.display = 'block';
              setTimeout(() => { bar.style.display = 'none'; }, 2600); }
  };
  if (navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).then(() => done(true)).catch(() => showTextPanel(text));
  } else {
    showTextPanel(text);
  }
}
function showTextPanel(text){
  const c = document.getElementById('content');
  const box = document.createElement('div');
  box.className = 'sect';
  box.innerHTML = '<h2>Copy this</h2><textarea class="exportbox" readonly></textarea>';
  box.querySelector('textarea').value = text;
  c.insertBefore(box, c.firstChild);
  const ta = box.querySelector('textarea');
  ta.focus(); ta.select();
  window.scrollTo(0, 0);
}

/* ================= MENU BUILDER ================= */
const MENU_BY_ID = Object.fromEntries(MENUS.map(m => [m.id, m]));
const build = {
  picks: store.get('build', []),          // array of {menuId, title}
  add(r){ if (!this.has(r)) { this.picks.push({menuId:r.menuId, title:r.title}); this.save(); } },
  remove(r){ this.picks = this.picks.filter(p => !(p.menuId===r.menuId && p.title===r.title)); this.save(); },
  has(r){ return this.picks.some(p => p.menuId===r.menuId && p.title===r.title); },
  save(){ store.set('build', this.picks); },
  clear(){ this.picks = []; this.save(); },
  items(){ return this.picks.map(p => ALLR.find(r => r.menuId===p.menuId && r.title===p.title)).filter(Boolean); }
};
const BUILD_COURSES = ['Starter','Main','Side','Dessert','Drink'];

function accOf(r){
  const m = MENU_BY_ID[r.menuId];
  return m ? (m.accessories || []) : [];
}
function capTypes(r){ return (r.cap || []).map(c => c.type); }

/* score a candidate against the current picks */
function pairScore(cand, picks){
  if (!picks.length) return {score:1, why:'A good place to start'};
  let score = 0; const reasons = [];
  const anchor = picks.find(p => p.course === 'Main') || picks[0];

  if (cand.region === anchor.region){ score += 6; reasons.push('same tradition as ' + anchor.title); }
  else if (cand.continent === anchor.continent){ score += 2; reasons.push('same part of the world'); }

  const seasons = new Set(picks.flatMap(p => p.season || []));
  if ((cand.season || []).some(s => seasons.has(s))){ score += 1.5; reasons.push('same season'); }

  // the book's own pairing is evidence
  if (picks.some(p => p.menuId === cand.menuId)){ score += 2.5; reasons.push('written for this menu'); }

  // equipment conflicts are judged per recipe, not per menu
  const anchorTypes = new Set(picks.flatMap(capTypes));
  const candTypes = capTypes(cand);
  const CONTESTED = {spit:'the rotisserie', stone:'the stone', fry:'the frying pot', steamer:'the steamer'};
  const clash = candTypes.filter(t => anchorTypes.has(t) && CONTESTED[t]);
  if (clash.length){ score -= 4; reasons.push('competes for ' + CONTESTED[clash[0]]); }
  else if (candTypes.length && candTypes.every(t => !anchorTypes.has(t))){
    score += 1.5; reasons.push('uses a different vessel');
  }

  // the anchor is a long cook: favour things that are quick or cold
  const am = MENU_BY_ID[anchor.menuId], cm = MENU_BY_ID[cand.menuId];
  if (am && cm){
    if (am.totalMin > 300 && cm.activeMin < 90){ score += 1.5; reasons.push('quick, while the long cook runs'); }
    if (am.heat >= 3 && cm.heat <= 1 && (cand.course === 'Side' || cand.course === 'Drink')){
      score += 2; reasons.push('cools down a hot main');
    }
    if (Math.abs((am.heat||1) - (cm.heat||1)) >= 3 && cand.course === 'Main'){ score -= 1; }
  }

  // a no-cook item is nearly always welcome
  if (/no cook|make ahead/i.test(cand.meta)){ score += 1.5; reasons.push('no fire needed'); }

  return {score, why: reasons.slice(0,2).join(' · ') || 'Works alongside what you have'};
}

function builderReport(items){
  const menus = [...new Set(items.map(i => i.menuId))].map(id => MENU_BY_ID[id]).filter(Boolean);
  const acc = {}; items.forEach(i => accOf(i).forEach(a => acc[a] = (acc[a]||0)+1));
  const types = {}; items.forEach(i => capTypes(i).forEach(t => types[t] = (types[t]||0)+1));
  const warnings = [];
  if ((acc['Rotisserie']||0) > 1) warnings.push('Two dishes want the rotisserie. One spit load at a time \u2014 cook them in rounds, or move one to a deflector.');
  if ((types['spit']||0) > 1) warnings.push('More than one spit load. Stagger them; a second cannot go on until the first is resting.');
  if ((types['stone']||0) > 2) warnings.push('Three or more things need the pizza stone. The stone drops about 25\u00b0F per item \u2014 budget recovery time between them.');
  if ((types['dutch']||0) > 2) warnings.push('Three Dutch-oven dishes. Check you own that many pots, or make one of them a day ahead.');
  if ((types['fry']||0) > 1) warnings.push('Two frying pots. Use one and run the batches in sequence; never two pots of hot oil at once.');
  const longs = items.filter(i => (MENU_BY_ID[i.menuId]||{}).totalMin > 300);
  if (longs.length > 1) warnings.push('Two all-day cooks. That is both kettles committed for the day with nothing left for sides.');
  if (!items.some(i => i.course === 'Main')) warnings.push('No main course yet \u2014 pick one and the suggestions will sharpen considerably.');

  const activeMin = items.reduce((n,i) => n + ((MENU_BY_ID[i.menuId]||{}).activeMin || 0) / Math.max(1, (MENU_BY_ID[i.menuId]||{}).recipes.length) * 1.6, 0);
  const fuel = Math.round(items.reduce((n,i) => n + ((MENU_BY_ID[i.menuId]||{}).fuel || 0) / Math.max(1,(MENU_BY_ID[i.menuId]||{}).recipes.length) * 1.4, 0) * 2) / 2;
  const lead = Math.max(0, ...items.map(i => (MENU_BY_ID[i.menuId]||{}).leadHours || 0));
  return {warnings, activeMin: Math.round(activeMin/5)*5, fuel, lead, menus, acc, types};
}

function viewBuild(){
  const items = build.items();
  const rep = builderReport(items);
  let h = '<div class="detail"><h1>Build a menu</h1>' +
    '<p class="lede">Pick a main, then let the book suggest what goes with it. Every recipe in the collection is fair game \u2014 the suggestions weigh tradition, season, and which piece of equipment each dish is already competing for.</p>';

  // current build
  h += '<div class="sect"><h2>Your menu</h2>';
  if (!items.length){
    h += '<div class="panel">Nothing chosen yet. Start with a main below.</div>';
  } else {
    h += '<div class="rlist">';
    BUILD_COURSES.forEach(c => items.filter(i => i.course === c).forEach(i => {
      h += '<div class="rrow"><span class="c">' + esc(c) + '</span>' +
        '<span class="t">' + esc(i.title) + '</span>' +
        '<span class="m">' + esc(i.menuTitle) + ' <button class="linkbtn" data-unpick="' +
        esc(i.menuId + '|' + i.title) + '">remove</button></span></div>';
    }));
    h += '</div>';
    h += '<div class="captable" style="margin-top:12px">' +
      '<div class="caprow"><div class="cl">Courses</div><div class="cn">' +
        BUILD_COURSES.filter(c => items.some(i => i.course===c)).join(', ') + '</div>' +
        '<div class="cv">' + BUILD_COURSES.filter(c => !items.some(i => i.course===c)).map(c=>'no '+c.toLowerCase()).join(', ') + '</div></div>' +
      '<div class="caprow"><div class="cl">Active time</div><div class="cn">~' + MINS(rep.activeMin) + '</div><div class="cv">rough, hands-on</div></div>' +
      '<div class="caprow"><div class="cl">Charcoal</div><div class="cn">~' + rep.fuel + ' chimneys</div><div class="cv">across both kettles</div></div>' +
      '<div class="caprow"><div class="cl">Start prep</div><div class="cn">' + HRS(rep.lead) + '</div><div class="cv">driven by the longest lead item</div></div>' +
      '</div>';
    rep.warnings.forEach(w => { h += '<div class="callout warn"><span class="lbl">Check this</span>' + esc(w) + '</div>'; });
    if (!rep.warnings.length) h += '<div class="callout ahead"><span class="lbl">No conflicts</span>Nothing here fights for the same vessel or the same zone. This will run on two kettles.</div>';
    h += '<div class="resetbar" style="margin-top:12px">' +
      '<button class="btn ghost" data-act="buildclear">Start over</button>' +
      '<button class="btn ghost" data-act="buildlist">Shopping list for these menus</button>' +
      '<button class="btn ghost" data-act="copy">Copy as text</button></div>';
  }
  h += '</div>';

  // ---- pick from everything, ranked ----
  const gq = state.q.trim().toLowerCase();
  BUILD_COURSES.forEach(course => {
    const chosen = items.filter(i => i.course === course).length;
    const all = ALLR.filter(r => r.course === course ||
      (course === 'Main' && r.course === 'Showpiece'));
    const open = !!state.bOpen[course];
    const cq = (state.bQ[course] || '').trim().toLowerCase();
    const sort = state.bSort[course] || 'suggested';

    let pool = all.filter(r => !build.has(r));
    if (gq) pool = pool.filter(r => r.hay.includes(gq));
    if (cq) pool = pool.filter(r => r.hay.includes(cq));

    let ranked = pool.map(r => Object.assign({r}, pairScore(r, items)));
    if (sort === 'az') ranked.sort((a,b) => a.r.title.localeCompare(b.r.title));
    else if (sort === 'region') ranked.sort((a,b) =>
      a.r.region.localeCompare(b.r.region) || b.score - a.score);
    else ranked.sort((a,b) => b.score - a.score);

    const shown = open ? ranked : ranked.slice(0, 5);

    h += '<div class="sect"><h2>' + course + 's' +
         ' <span style="color:var(--mute);font-weight:400;text-transform:none;letter-spacing:0">· ' +
         all.length + ' in the book' + (chosen ? ' · ' + chosen + ' chosen' : '') + '</span></h2>';

    if (open){
      h += '<div class="pickbar">' +
        '<input class="picksearch" id="bq-' + course + '" data-bq="' + course + '" type="search" ' +
          'placeholder="Search ' + all.length + ' ' + course.toLowerCase() + 's\u2026" value="' + esc(state.bQ[course] || '') + '">' +
        ['suggested','region','az'].map(m => '<button class="chip" aria-pressed="' + (sort===m?'true':'false') +
          '" data-bsort="' + course + '|' + m + '">' +
          (m==='suggested'?'Best fit':m==='region'?'By region':'A\u2013Z') + '</button>').join('') +
        '</div>';
    }

    if (!shown.length){
      h += '<div class="panel">' + (cq || gq ? 'Nothing matches that search.' : 'Everything here is already on your menu.') + '</div>';
    } else {
      h += '<div class="rlist' + (open ? ' picklist' : '') + '">';
      let lastRegion = null;
      shown.forEach(x => {
        if (open && sort === 'region' && x.r.region !== lastRegion){
          lastRegion = x.r.region;
          h += '<div class="pickgroup">' + esc(lastRegion) + '</div>';
        }
        const strong = x.score >= 6;
        h += '<button class="rrow" data-pick="' + esc(x.r.menuId + '|' + x.r.title) + '">' +
          '<span class="c">' + (strong ? '\u2605 add' : '+ add') + '</span>' +
          (x.r.course === 'Showpiece' ? '' : '') +
          '<span class="t">' + esc(x.r.title) +
            '<span class="pickwhy">' + esc(x.why) + '</span></span>' +
          '<span class="m">' + esc(x.r.menuTitle) + '</span></button>';
      });
      h += '</div>';
    }

    const hiddenCount = ranked.length - shown.length;
    h += '<div class="resetbar" style="margin-top:8px">' +
      '<button class="linkbtn" data-bopen="' + course + '">' +
        (open ? 'Show fewer' : 'Browse all ' + ranked.length + ' ' + course.toLowerCase() + 's') +
      '</button>' +
      (!open && hiddenCount > 0 ? '<span class="count">' + hiddenCount + ' more</span>' : '') +
      '</div></div>';
  });
  return h + '</div>';
}

const AISLES = [
  ['Fuel & wood', /\b(charcoal|briquette|lump charcoal|wood chunk|oak chunk|hickory|mesquite|pecan wood|alder|kiawe|pimento wood|vine cutting|cedar plank|chimney)/i],
  ['Pantry',      /\b(dried |ground |powder|paste\b|canned|tinned|syrup|molasses|vinegar|flakes|seeds?\b|peppercorn|\w*\s?salt\b|sugar|flour|stock\b|oil\b|spice|masala|rub\b|cinnamon|clove\b|cloves\b(?! garlic)|nutmeg|cumin|paprika|saffron|bay lea)/i],
  ['Drinks',      /\b(wine|beer|lager|rum\b|bourbon|whisk|vodka|tequila|mezcal|pisco|gin\b|soda|cola|cider\b|sake|vermouth|cava|champagne|liqueur|brandy|aquavit|ouzo|pastis|fernet|curaçao|orgeat|seltzer|tonic|cachaça|sherry|madeira|nectar|juice\b|tea\b|coffee)/i],
  ['Meat & fish', /\b(beef|pork|chicken|lamb|mutton|goat|brisket|belly|shoulder|rib\b|ribs\b|steak|sausage|chorizo|bacon|ham\b|duck|turkey|venison|rabbit|quail|capon|shrimp|prawn|fish|salmon|oyster|clam|mussel|lobster|crab|octopus|squid|anchov|tuna|ahi|liver|marrow|spam|sucuk|merguez|andouille|boudin|linguiça|pastrami|mackerel|cod\b|bass|bream|turbot|snapper|branzino|bologna|lardon|pancetta|hock|tri-tip|picanha|hanger|bavette|porterhouse|tomahawk|ribeye|entrec|filet|oxtail|bone\b|bones\b)/i],
  ['Bakery',      /\b(bread|bun\b|buns\b|roll\b|rolls\b|baguette|tortilla|pita|naan|khobz|loaf|loaves|brioche|wafer|cracker|puff pastry|cantucci|saltine|simit|papad|cookie|biscuit)/i],
  ['Dairy & eggs',/\b(butter|milk|cream|cheese|yogurt|yoghurt|egg|crème|crema|kaymak|ghee|provolone|feta|halloumi|parmesan|cheddar|mozzarella|queso|cotija|paneer|gruy|comté|roquefort|brie|buttermilk|curd)/i],
  ['Produce',     /\b(onion|garlic|tomato|tomatillo|pepper|chilli|chili|chile|lemon|lime|orange|potato|carrot|celery|cucumber|parsley|cilantro|mint|thyme|rosemary|sage|dill|basil|oregano|lettuce|cabbage|apple|peach|banana|pineapple|mango|berr|corn\b|avocado|ginger|scallion|shallot|leek|fennel|eggplant|aubergine|squash|mushroom|chanterelle|shiitake|plantain|yuca|okra|collard|kale|radish|beet|fig\b|apricot|cherr|melon|grape|plum|date\b|nopal|calçot|rabe|artichoke|asparagus|sprout|greens|herb)/i],
];
function aisleFor(text){
  for (const [name, re] of AISLES) if (re.test(text)) return name;
  return 'Pantry';
}
const PER_UNIT = /per (glass|serving|person|drink|cup|bun|taco|roll|sandwich)/i;

const UNITS = 'cups?|tbsp|tablespoons?|tsp|teaspoons?|kg|g|lbs?|oz|ml|cl|l|qt|quarts?|pints?|' +
  'cans?|jars?|bottles?|sticks?|cloves?|bunch(?:es)?|heads?|slices?|sprigs?|pinch(?:es)?|dozen|' +
  'racks?|links?|ears?|sheets?|bags?|packets?|stalks?|leaves|rashers?|fillets?|skewers?';
const QTY_RE = new RegExp('^\\s*(\\d+(?:[.,]\\d+)?)?\\s*([\u00bd\u00bc\u00be\u2153\u2154\u215b\u215c\u215d\u215e])?\\s*(' + UNITS + ')?\\b\\.?\\s*(.+)$', 'i');
const IRREGULAR = {cloves:'clove', leaves:'leaf', bunches:'bunch', pinches:'pinch',
  inches:'inch', slices:'slice', boxes:'box', tablespoons:'tbsp', teaspoons:'tsp',
  quarts:'qt', quart:'qt', pints:'pint', pounds:'lb', lbs:'lb'};
const SINGULAR = u => {
  const x = (u || '').toLowerCase();
  if (IRREGULAR[x]) return IRREGULAR[x];
  return x.replace(/s$/, '');
};

function parseIngredient(text){
  // ranges ("5\u20136 lb", "1\u20132 tsp") are not a single quantity \u2014 leave them as written
  if (/^\s*\d+\s*[\u2013\u2014-]\s*\d/.test(text)) return {qty:null, unit:'', name:text.trim(), raw:text};
  const m = text.match(QTY_RE);
  if (!m) return {qty:null, unit:'', name:text.trim(), raw:text};
  const whole = m[1] ? parseFloat(m[1].replace(',','.')) : 0;
  const frac  = m[2] ? VULGAR[m[2]] : 0;
  const qty   = (whole || frac) ? whole + frac : null;
  return {qty, unit: SINGULAR(m[3]), name: (m[4] || '').trim(), raw:text};
}
const PURPOSE = /\s+(for (the top|wrapping|frying|basting|brushing|dusting|the pan|the grate|poaching|the lattice|glazing|serving)|as a binder|to (serve|finish|taste|top|glaze)|plus more.*)$/i;
function cleanName(n){
  return n.replace(/\((?!about|roughly|around)[^)]*\)/gi, '').replace(PURPOSE, '')
          .replace(/,\s*(diced|chopped|minced|sliced|shredded|grated|crushed|torn|seeded|halved|quartered|softened|melted|drained|rinsed|peeled|trimmed|husked|muddled|warmed|cooled|toasted|room temperature)\b.*$/i, '')
          .replace(/\s+/g, ' ').trim();
}
function nameKey(n){
  return cleanName(n).toLowerCase().split(',')[0]
          .replace(/\b(finely|coarsely|coarse|roughly|thinly|freshly|fresh|very|large|small|medium|kosher|sea|table|flaky|good|ripe|firm-ripe)\b/g,'')
          .replace(/[^a-z ]/g,'').replace(/\s+/g,' ').trim();
}

/* ---------- one line can name several things you have to buy ---------- */
const PREP_ONLY = /^(diced|chopped|minced|sliced|shredded|grated|crushed|torn|seeded|halved|quartered|softened|melted|drained|rinsed|peeled|trimmed|stemmed|husked|pitted|cubed|julienned|whole|thinly sliced|finely diced|room temperature|warmed|cooled|chilled|toasted|of choice|lightly beaten|at room temperature|to taste|to serve|to finish|for (frying|basting|brushing|dusting|the pan|the grate)|plus more.*|optional)$/i;
const hasQty = t => /^\s*(\d|[\u00bc\u00bd\u00be\u2153\u2154\u215b\u215c\u215d\u215e])/.test(t);

const MEASURE_ONLY = /^[\d\s\u00bc\u00bd\u00be\u2013\u2014-]+(lb|lbs|oz|g|kg|ml|l|inch|inches|cups?)?$/i;
function splitOne(t){
  t = (t || '').trim().replace(/^[A-Z][a-z ]{2,18}:\s*/, '');   // "Spritz: ..." \u2192 drop the label
  if (/\+/.test(t) && t.split('+').filter(x => hasQty(x.trim())).length >= 2)
    return t.split('+').reduce((a, x) => a.concat(splitOne(x)), []);
  // "1 tbsp each granulated garlic and onion"
  let m = t.match(/^(.+?)\s+each\s+(.+?)\s+and\s+(.+)$/i);
  if (m){
    const qty = m[1].trim();
    let a = m[2].trim(), b = m[3].trim();
    const aw = a.split(' ');
    if (aw.length > 1 && b.split(' ').length === 1) b = aw[0] + ' ' + b;   // "granulated" carries over
    return [qty + ' ' + a, qty + ' ' + b];
  }
  // "1 green cabbage and 4 carrots, shredded"
  m = t.match(/^(.+?)\s+and\s+(.+)$/i);
  if (m && hasQty(m[1]) && hasQty(m[2]))
    return splitOne(m[1]).concat(splitOne(m[2]));
  // "1 tsp granulated onion, ½ tsp cayenne, black pepper"
  const commas = t.split(',').map(x => x.trim()).filter(Boolean);
  if (commas.length > 1 && commas.filter(hasQty).length >= 2)
    return commas.filter(c => !PREP_ONLY.test(c)).reduce((a, c) => a.concat(splitOne(c)), []);
  // "butter, salt" or "Salt and pepper" \u2014 a bare list of separate things
  if (!hasQty(t)){
    const bare = t.split(/,| and /i).map(x => x.trim()).filter(Boolean);
    if (bare.length > 1 && bare.every(x => x.split(' ').length <= 3 && !PREP_ONLY.test(x))) return bare;
  }
  return [t];
}
function splitIngredient(text){
  return text.split('\u00b7').map(x => x.trim()).filter(x => x.length > 1)
    .reduce((a, p) => a.concat(splitOne(p)), [])
    .filter(x => x.length > 1 && !PREP_ONLY.test(x) && !MEASURE_ONLY.test(x)
                 && !/^(cold |hot |warm |iced |boiling )?water\b/i.test(x));
}

/* ---------- turning a measurement into something a shop sells ---------- */

/* spices and dry goods nobody sells by the spoon */
const PACKS = [
  [/granulated (garlic|onion)|garlic powder|onion powder|garlic salt|onion salt|seasoned salt|seasoning salt|chilli-lime salt|chili-lime salt|paprika|cayenne|cumin|coriander seed|ground coriander|dried oregano|dried thyme|dried mint|allspice|cinnamon|nutmeg|turmeric|chilli powder|chili powder|five-spice|garam masala|ras el hanout|celery s(eed|alt)|caraway|fennel (seed|pollen)|mustard seed|peppercorn|black pepper|white pepper|shichimi|togarashi|sumac|kasoori|amchur|chaat masala|pul biber|aleppo pepper|red pepper flakes|chilli flakes|^pepper$|^salt and pepper$|saffron|cardamom|clove|star anise|bay lea|juniper|pickling spice|creole seasoning|curing salt|baking powder|baking soda|cornstarch|yeast/i,
    'jar', 6],                                   // ~6 tbsp in a supermarket jar; compound flavored salts belong here, not the plain-salt box below
  [/\bsalt\b/i, 'box', 96],
  [/sugar|flour|masa harina|cornmeal|semolina|matzo meal|mochiko|rice\b|lentil|bean|oats|polenta|grits/i, 'bag', 64],
  [/olive oil|neutral oil|vegetable oil|frying oil|sesame oil|ghee|lard|tallow|schmaltz/i, 'bottle', 32],
  [/soy sauce|fish sauce|mirin|worcestershire|hot sauce|vinegar|molasses|honey|maple syrup|pomegranate molasses|pekmez|tahini|mustard\b|ketchup|mayonnaise|hoisin|oyster sauce|cajeta|condensed milk|coconut milk|stock\b|vanilla|extract|liquid smoke|rose water|orange-blossom/i,
    'bottle', 32],
];
const TO_TBSP = {tsp: 1/3, tbsp: 1, cup: 16, oz: 2, ml: 0.0676, l: 67.6, g: 0.0667, kg: 66.7, qt: 64, pint: 32, lb: 30};

/* sensible default quantities for lines the book leaves open */
const DEFAULT_BUY = [
  [/^(fresh\s+)?(mint|parsley|cilantro|coriander|dill|basil|thyme|rosemary|sage|chives|tarragon|oregano|scallion|spring onion|garlic chive|betel|perilla|shiso|curry lea)/i, n => '1 bunch ' + n],
  [/^(lemon|lime)s?\b/i,  n => '3 ' + pluralise(n.replace(/s$/, ''), 3)],
  [/^oranges?\b/i,        n => '3 oranges'],
  [/^garlic$/i,           () => '1 head garlic'],
  [/^ginger/i,            n => '1 knob ' + n],
  [/lettuce|cabbage/i,    n => '1 ' + n],
  [/bread|baguette|loaf/i, n => '1 loaf ' + n],
  [/ice\b/i,              n => null],
];
function pluralise(name, n){
  if (n <= 1) return name;
  const [head, ...rest] = name.split(',');
  const words = head.trim().split(' ');
  let last = words[words.length - 1];
  if (/s$|^\d/.test(last)) return name;
  last = /(o)$/i.test(last) ? last + 'es'
       : /(ch|sh|x|s)$/i.test(last) ? last + 'es'
       : /f$/i.test(last) ? last.replace(/f$/, 'ves')
       : last + 's';
  words[words.length - 1] = last;
  return [words.join(' '), ...rest].join(',');
}
function vagueLine(name, servings){
  if (/^(plenty of |lots of |a bag of )?ice\b[\s,]*$/i.test(name.trim())){
    const bags = Math.max(1, Math.ceil(servings / 10));
    return bags + ' bag' + (bags > 1 ? 's' : '') + ' of ice (about 5 lb each)';
  }
  return null;
}
const BOTTLES = [
  [/fernet|branca|amaro|chartreuse|absinthe|boukha|aquavit|ouzo|tsipouro|pastis|pisco|cacha|baijiu|kaoliang|soju|mezcal|tequila|bourbon|whisk|rye\b|vodka|rum\b|gin\b|brandy|cognac|calvados|curaçao|orgeat|liqueur|vermouth|sherry|madeira|marc\b|sake\b|cassis|peychaud|angostura/i, 700],
  [/wine|cava|champagne|crémant|prosecco|riesling|malbec|chianti|garnacha|pinot|zinfandel|assyrtiko|rosé|burgund|rioja|vin santo/i, 750],
  [/coca-cola|coke\b|cola\b|ginger ale|ginger beer|soda water|seltzer|tonic|lemon-lime|birch beer|root beer|ting\b|inca kola|materva|ironbeer|cheerwine|barq|jarritos|ramune|calpico|chinotto|moxie/i, 1000],
  [/beer|lager|ale\b|stout|porter|cider\b/i, 330],
];
const TO_ML = {ml:1, cl:10, l:1000, oz:29.57, cup:236.6, tbsp:14.8, tsp:4.9, qt:946, pint:473};
function fmtVol(ml){ return ml >= 1000 ? (Math.round(ml/100)/10) + ' L' : Math.round(ml) + ' ml'; }

function shoppingLine(g, servings){
  const vague = vagueLine(g.name, servings);
  if (vague) return {text: vague, cat: g.cat};

  // bottled drinks
  const bottle = /vinegar|juice|stock|syrup|extract|essence/i.test(g.name)
    ? null : BOTTLES.find(b => b[0].test(g.name));
  if (bottle && g.qty != null && TO_ML[g.unit]){
    const ml = g.qty * TO_ML[g.unit], size = bottle[1];
    const count = Math.max(1, Math.ceil(ml / size));
    const sz = size >= 1000 ? (size / 1000) + ' L' : size + ' ml';
    return {text: count + ' \u00d7 ' + sz + ' ' + g.name + '  (about ' + fmtVol(ml) + ' needed)', cat: 'Drinks'};
  }

  // spices and dry goods sold by the jar, bag or bottle
  const pack = PACKS.find(x => x[0].test(g.name));
  if (pack && g.qty != null && TO_TBSP[g.unit]){
    const tbsp = g.qty * TO_TBSP[g.unit];
    const count = Math.max(1, Math.ceil(tbsp / pack[2]));
    const cups = tbsp / 16;
    const need = tbsp >= 16
      ? fmtQty(Math.round(cups * 4) / 4) + (Math.abs(cups - 1) < 0.13 ? ' cup' : ' cups')
      : fmtQty(Math.round(tbsp * 4) / 4) + ' tbsp';
    return {text: count + ' ' + pack[1] + (count > 1 ? 's' : '') + ' ' + g.name +
            '  (about ' + need + ' needed)', cat: 'Pantry'};
  }

  // nothing stated: give it a default you can actually put in a basket
  if (g.qty == null){
    for (const [re, fn] of DEFAULT_BUY){
      if (re.test(g.name.trim())){ const v = fn(g.name.trim()); if (v) return {text: v, cat: g.cat}; }
    }
    if (pack) return {text: '1 ' + pack[1] + ' ' + g.name, cat: 'Pantry'};
    return {text: '1 ' + g.name, cat: g.cat};
  }

  const unit = g.unit ? ' ' + g.unit +
    (g.qty > 1 && !/^(tsp|tbsp|oz|ml|cl|l|g|kg|lb|qt|pint)$/.test(g.unit) ? 's' : '') : '';
  const body = g.unit ? g.name : pluralise(g.name, g.qty);
  let out = fmtQty(g.qty) + unit + ' ' + body;
  out = out.replace(/\((about|roughly|around)\s+(\d+(?:\.\d+)?)/gi,
    (mm, w, n) => '(' + w + ' ' + fmtQty(parseFloat(n) * g.yieldMult));
  return {text: out, cat: g.cat};
}

/* resolve "Chimichurri (Chapter 22)" into the library recipe it points at */
function libraryRef(text){
  const m = text.match(/\(Chapters?\s*\d+[^)]*\)/i);
  if (!m) return null;
  const bare = text.slice(0, m.index).replace(/^[\d\u00bd\u00bc\u00be\u2153\u2154\u215b\s.,\/]+/, '')
    .replace(new RegExp('^(' + UNITS + ')\\b\\.?\\s*', 'i'), '')
    .replace(/^(batch(es)? of|batch|a|the)\s+/i, '').replace(/,.*$/, '').trim();
  const k = x => x.toLowerCase().replace(/[^a-z]/g, '');
  const want = k(bare);
  if (want.length < 4) return null;
  return LIBRARY.find(r => { const t = k(r.title);
    return t.startsWith(want.slice(0, 10)) || want.startsWith(t.slice(0, 10)) ||
           (want.length >= 4 && (t.endsWith(want) || t.includes(want))); }) || null;
}

/* flatten one recipe into raw shopping entries, expanding library cross-references */
function recipeEntries(r, servings, depth){
  const out = [];
  let sect = '';
  r.ingredients.forEach(i => {
    if (i.type === 'sub'){ sect = i.text; return; }
    const perUnit = PER_UNIT.test(sect) || (!sect && PER_UNIT.test(r.meta));
    const mult = perUnit ? servings : servings / 8;
    splitIngredient(i.text).forEach(part => {
      const ref = (depth || 0) < 1 ? libraryRef(part) : null;
      if (ref){ out.push(...recipeEntries(ref, servings, (depth || 0) + 1)); return; }
      const parsed = parseIngredient(part);
      out.push({...parsed, mult, cat: aisleFor(part), from: r.title});
    });
  });
  return out;
}
function recipeCartItems(r, servings){ return aggregate(recipeEntries(r, servings, 0), servings); }

function menuRawEntries(m, servings){
  const entries = m.recipes.flatMap(r => recipeEntries(r, servings, 0));
  // fuel and any non-food line from the book's own list
  entries.push({qty: fuelAt(m, servings / 8), unit: 'chimney', name: 'charcoal', mult: 1,
                cat: 'Fuel & wood', from: m.title});
  (m.wood || []).forEach(w => entries.push({qty: 3, unit: 'chunk', name: w + ' wood',
                mult: 1, cat: 'Fuel & wood', from: m.title}));
  parseShopping(m).filter(x => /special/i.test(x.cat)).forEach(x =>
    entries.push({qty: null, unit: '', name: x.item, mult: 1, cat: 'Special', from: m.title}));
  return entries;
}
function menuCartItems(m, servings){ return aggregate(menuRawEntries(m, servings), servings); }

/* merge duplicates: one line per ingredient, quantities summed where they are comparable */
function aggregate(entries, servings){
  const byName = new Map();
  entries.forEach(e => {
    const k = nameKey(e.name);
    if (!k || /^(cold |hot |warm |iced |boiling |filtered )?water$/.test(k)) return;
    if (/^(sauce of choice|of choice|more|extra|garnish|optional)$/.test(k)) return;
    if (!byName.has(k))
      byName.set(k, {name: cleanName(e.name), cat: e.cat, froms: new Set(),
                     units: new Map(), yieldMult: e.mult});
    const g = byName.get(k);
    g.froms.add(e.from);
    if (e.mult > g.yieldMult) g.yieldMult = e.mult;
    const cn = cleanName(e.name);
    if (cn.length && cn.length < g.name.length) g.name = cn;     // keep the plainest wording
    const u = e.unit || '';
    const scaled = e.qty == null ? null : e.qty * e.mult;
    const cur = g.units.get(u) || {unit: u, qty: null};
    if (scaled != null) cur.qty = (cur.qty || 0) + scaled;
    g.units.set(u, cur);
  });

  const out = [];
  byName.forEach(g => {
    const pack = PACKS.find(x => x[0].test(g.name));
    const units = [...g.units.values()];
    const emit = sub => {
      const line = shoppingLine({name: g.name, unit: sub.unit, qty: sub.qty,
                                 cat: g.cat, yieldMult: g.yieldMult}, servings);
      out.push({cat: line.cat, item: line.text, name: g.name,
                from: [...g.froms].slice(0, 3).join(', ') + (g.froms.size > 3 ? ' +' + (g.froms.size - 3) : ''),
                menuId: nameKey(g.name) + '|' + sub.unit});
    };
    if (pack){
      // one jar/bag/bottle however many recipes call for it
      let tbsp = 0, any = false;
      units.forEach(u => { if (u.qty != null && TO_TBSP[u.unit]){ tbsp += u.qty * TO_TBSP[u.unit]; any = true; } });
      emit({unit: any ? 'tbsp' : '', qty: any ? tbsp : null});
    } else {
      units.forEach(emit);
    }
  });
  return out;
}

function parseShopping(m){
  const div = document.createElement('div');
  div.innerHTML = m.blocks.shopping || '';
  const out = [];
  div.querySelectorAll('li').forEach(li => {
    const strong = li.querySelector('strong');
    let cat = 'Other';
    if (strong){ cat = strong.textContent.replace(/:$/,'').trim(); strong.remove(); }
    li.textContent.split('·').map(s => s.trim()).filter(s => s.length > 1).forEach(item => {
      out.push({cat, item: item.replace(/^[:\s]+/,''), from: m.title, menuId: m.id});
    });
  });
  return out;
}
/* where to actually buy a shopping-list item: Amazon, and a local-results search for everyone else */
function buyLinks(name){
  const clean = name.replace(/\s*\(.*?\)\s*/g, '').trim();
  return {
    amazon: 'https://www.amazon.com/s?k=' + encodeURIComponent(clean),
    nearby: 'https://www.google.com/search?q=' + encodeURIComponent('buy ' + clean + ' near me'),
  };
}
function viewList(){
  if (!cart.length){
    return '<div class="empty"><h3>Your shopping list is empty</h3>' +
      '<p>Add a whole menu from its page, or a single recipe from any recipe page. Mix as many as you like — ' +
      'items group by aisle and everything stays ticked between visits.</p></div>';
  }
  const entries = cart.flatMap(e => {
    if (e.kind === 'menu'){ const m = MENUS.find(x => x.id === e.id); return m ? menuRawEntries(m, state.scale) : []; }
    const r = ALLR.concat(LIBRARY).find(x => recipeKey(x) === e.id);
    return r ? recipeEntries(r, state.scale, 0) : [];
  });
  const items = aggregate(entries, state.scale);
  const AISLE_ORDER = ['Meat & fish','Produce','Dairy & eggs','Bakery','Pantry','Drinks','Special','Fuel & wood'];
  const AISLE_EXTRA = ['Special'];
  const cats = [...new Set(items.map(i => i.cat))]
    .sort((a,b) => { const ia = AISLE_ORDER.indexOf(a), ib = AISLE_ORDER.indexOf(b);
                     return (ia<0?99:ia) - (ib<0?99:ib) || a.localeCompare(b); });
  const names = cart.map(e => e.kind === 'menu'
    ? ((MENUS.find(m => m.id === e.id) || {}).title || '') + ' (whole menu)'
    : e.id.split('|').slice(1).join('|')).filter(Boolean);
  let h = '<div class="detail"><h1>Shopping list</h1>' +
    '<p class="lede">' + esc(names.join(' · ')) + '</p>' +
    '<div class="resetbar"><span class="count">' + items.length + ' items · for ' + state.scale + '</span>' +
    '<button class="linkbtn" data-act="listserves">Change servings</button>' +
    '<button class="linkbtn" data-act="untick">Untick all</button>' +
    '<button class="linkbtn" data-act="clearcart">Empty list</button>' +
    '<button class="linkbtn" data-act="copy">Copy as text</button></div>';
  cats.forEach(c => {
    h += '<div class="shopcat">' + esc(c) + '</div>';
    items.filter(i => i.cat === c).forEach(i => {
      const key = i.menuId + '|' + i.item;
      const done = !!checked[key];
      const buy = buyLinks(i.name || i.item);
      h += '<div class="shopitem' + (done ? ' done' : '') + '">' +
        '<label><input type="checkbox" data-check="' + esc(key) + '"' + (done ? ' checked' : '') + '>' +
        '<span>' + esc(i.item) + (cart.length > 1 ? '<span class="from">' + esc(i.from) + '</span>' : '') +
        '</span></label>' +
        '<span class="buy">' +
        '<a href="' + esc(buy.amazon) + '" target="_blank" rel="noopener">Amazon</a>' +
        '<a href="' + esc(buy.nearby) + '" target="_blank" rel="noopener">Nearby stores</a>' +
        '</span></div>';
    });
  });
  return h + '</div>';
}

/* ---------- detail views ---------- */
function viewMenuDetail(m){
  const onList = inCart('m|' + m.id);
  const fav = favs.includes(m.id);
  let h = '<div class="detail"><button class="backbtn" data-act="back">← All menus</button>' +
    photoTag(m.image, m.title, 'detail-photo', true) +
    '<div class="kicker">' + esc(m.part) + ' · ' + esc(m.region) + '</div>' +
    '<h1>' + esc(m.title) + '</h1><p class="lede">' + esc(m.lead) + '</p>' +
    '<div class="factgrid">' +
      fact('Season', (m.season||[]).join(', ')) +
      fact('Serves', String(state.scale) + (state.scale !== 8 ? ' (scaled)' : '')) +
      fact('Kettles', m.kettles === 1 ? 'One' : 'Two') +
      fact('Accessory', (m.accessories||[]).join(', ') || 'None') +
      fact('Complexity', m.complexity) +
      fact('Active', MINS(m.activeMin)) +
      fact('Total', MINS(m.totalMin)) +
      fact('Start prep', HRS(m.leadHours)) +
      fact('Wood', (m.wood||[]).join(', ') || 'None') +
      fact('Cost', m.cost) +
      fact('Heat', ['','Mild','Medium','Hot','','Fierce'][m.heat]) +
      fact('Cold weather', m.coldOK ? 'Yes' : 'No') +
    '</div>' +
    '<div class="resetbar">' +
      '<button class="btn' + (onList ? ' ghost' : '') + '" data-act="cart" data-id="' + m.id + '">' +
        (onList ? '✓ Whole menu on your list' : 'Add whole menu to shopping list') + '</button>' +
      '<button class="btn ghost" data-fav="' + m.id + '">' + (fav ? '★ Saved' : '☆ Save') + '</button>' +
      '<button class="btn ghost" data-act="copy">Copy as text</button>' +
    '</div>';

  if (m.impress) h += '<div class="callout warn"><span class="lbl">★ Showpiece</span>' + esc(m.impressWhy) + '</div>';
  h += '<div class="scaler"><span class="lbl">Cooking for</span>' +
    [4,8,12,16].map(n => '<button class="chip" aria-pressed="' + (state.scale===n?'true':'false') +
      '" data-scale="' + n + '">' + n + '</button>').join('') + '</div>';
  h += capPanel(m, state.scale / 8, m.cap);

  if (m.blocks.menu) h += sect('The menu', m.blocks.menu);
  if (m.blocks.grill) h += sect('Grill plan &amp; fuel', m.blocks.grill);
  if (m.blocks.timeline) h += sect('Prep countdown', m.blocks.timeline);

  window.__rlist = m.recipes;
  h += '<div class="sect"><h2>Recipes</h2><div class="rlist">';
  COURSES.forEach(c => (m.courses[c] || []).forEach(r => {
    const i = m.recipes.indexOf(r);
    h += '<button class="rrow" data-recipe="' + i + '"><span class="c">' + esc(r.course) + '</span>' +
      '<span class="t">' + esc(r.title) + (r.native ? ' <span class="drop">' + esc(r.native) + '</span>' : '') +
      '</span><span class="m">' + esc(r.meta.split('·').slice(1).join('·').trim()) + '</span></button>';
  }));
  h += '</div></div>';

  if (m.special && m.special.length)
    h += '<div class="callout warn"><span class="lbl">Order ahead</span>' + esc(m.special.join(' · ')) +
         ' — these may not be on a supermarket shelf.</div>';
  if (m.blocks.shopping) h += sect('Shopping list', m.blocks.shopping +
    '<p class="pill-note">Quantities as written, for 8. Open a recipe to scale its ingredients.</p>');
  return h + '</div>';
}
function fact(k, v){ return '<div class="fact"><dt>' + k + '</dt><dd>' + esc(v || '—') + '</dd></div>'; }
function sect(t, html){ return '<div class="sect"><h2>' + t + '</h2><div class="panel">' + html + '</div></div>'; }

function viewRecipeDetail(r){
  const factor = state.scale / 8;
  let h = '<div class="detail"><button class="backbtn" data-act="back">← Back</button>' +
    photoTag(r.image, r.title, 'detail-photo', true) +
    '<div class="kicker">' + esc(r.course === 'Library' ? r.chapter : r.course) +
      (r.menuTitle ? ' · ' + esc(r.menuTitle) : '') + '</div>' +
    '<h1>' + esc(r.title) + '</h1>' +
    (r.native ? '<p class="lede">' + esc(r.native) + '</p>' : '') +
    '<p class="count">' + esc(r.meta) + '</p>';
  if (r.headnote) h += '<p class="lede" style="font-style:normal;margin-top:14px">' + glossify(esc(r.headnote)) + '</p>';

  const rOn = inCart('r|' + recipeKey(r));
  h += '<div class="resetbar" style="margin-top:14px">' +
    '<button class="btn' + (rOn ? ' ghost' : '') + '" data-act="rcart">' +
      (rOn ? '✓ Ingredients on your list' : 'Add ingredients to shopping list') + '</button>' +
    '<button class="btn ghost" data-act="copy">Copy as text</button></div>';
  h += '<div class="scaler"><span class="lbl">Serves</span>' +
    [4,8,12,16].map(n => '<button class="chip" aria-pressed="' + (state.scale===n?'true':'false') +
      '" data-scale="' + n + '">' + n + '</button>').join('') +
    (factor !== 1 ? '<span class="pill-note">Quantities scaled ×' + (Math.round(factor*100)/100) + '</span>' : '') +
    '</div>';

  if (r.cap && r.cap.length){
    const rows = capRows(r.cap, factor);
    h += '<div class="captable" style="margin-bottom:18px">';
    rows.forEach(x => {
      h += '<div class="caprow' + (x.changed ? ' chg' : '') + '">' +
        '<div class="cl">Equipment</div><div class="cn">' + esc(x.need) + '</div>' +
        '<div class="cv">' + esc(x.verdict) +
        (x.changed ? '<span class="was">at 8 it was: ' + esc(x.base) + '</span>' : '') +
        (x.note ? '<span class="cnote">' + esc(x.note) + '</span>' : '') + '</div></div>';
    });
    h += '</div>';
  }
  if (r.ingredients.length){
    let sect = '';
    const rows = r.ingredients.map(i => {
      if (i.type === 'sub'){
        sect = i.text;
        return '<li class="sub">' + esc(i.text) +
          (PER_UNIT.test(sect) ? ' <span class="perunit">\u2014 does not scale</span>' : '') + '</li>';
      }
      const f = PER_UNIT.test(sect) || (!sect && PER_UNIT.test(r.meta)) ? 1 : factor;
      return '<li>' + hl(scaleText(i.text, f)) + '</li>';
    });
    h += '<div class="ingbox"><ul>' + rows.join('') + '</ul></div>';
    if (r.ingredients.some(i => i.type === 'sub' && PER_UNIT.test(i.text)) || PER_UNIT.test(r.meta)){
      h += '<p class="pill-note" style="margin-top:-10px">Per-glass quantities stay fixed however many you are ' +
           'serving \u2014 the shopping list multiplies them up for you.</p>';
    }
  }
  if (r.method.length) h += '<ol class="steps">' + r.method.map(s => '<li>' + glossify(hl(s)) + '</li>').join('') + '</ol>';
  if (r.plating){
    const plbl = r.plating.style === 'keeping' ? 'Keeping' : 'To the table · ' + r.plating.style;
    h += '<div class="callout plate"><span class="lbl">' + esc(plbl) + '</span>' +
         esc(r.plating.text) + '</div>';
  }
  r.notes.forEach(n => {
    h += '<div class="callout ' + n.kind + '"><span class="lbl">' + esc(n.label) + '</span>' + esc(n.text) + '</div>';
  });
  if (r.menuId){
    h += '<hr class="sep"><button class="btn ghost" data-menu="' + r.menuId + '">Open the full ' +
         esc(r.menuTitle) + ' menu →</button>';
  }
  return h + '</div>';
}

/* ---------- router ---------- */
function render(){
  const c = document.getElementById('content');
  if (state.recipe !== null){ c.innerHTML = viewRecipeDetail(state.recipe); }
  else if (state.detail){ c.innerHTML = viewMenuDetail(state.detail); }
  else if (state.view === 'menus'){ c.innerHTML = viewMenus(); }
  else if (state.view === 'recipes'){ c.innerHTML = viewRecipes(); }
  else if (state.view === 'library'){ c.innerHTML = viewLibrary(); }
  else if (state.view === 'build'){ c.innerHTML = viewBuild(); }
  else { c.innerHTML = viewList(); }
  renderFacets();
  document.querySelectorAll('.tabs button').forEach(b =>
    b.setAttribute('aria-selected', b.dataset.view === state.view ? 'true' : 'false'));
  document.getElementById('qclr').style.display = state.q ? 'block' : 'none';
  const solo = !!(state.detail || state.recipe !== null || state.view === 'list' || state.view === 'build');
  document.querySelector('.layout').classList.toggle('solo', solo);
  if (state.detail || state.recipe !== null) window.scrollTo(0,0);
}

/* ---------- events ---------- */
document.addEventListener('click', e => {
  const t = e.target.closest('[data-menu],[data-recipe],[data-f],[data-grp],[data-act],[data-course],[data-scale],[data-fav],[data-view],[data-pick],[data-unpick],[data-bopen],[data-bsort]');
  if (!t) return;
  const d = t.dataset;

  if (d.bopen){ state.bOpen[d.bopen] = !state.bOpen[d.bopen]; return render(); }
  if (d.bsort){ const [c, mode] = d.bsort.split('|'); state.bSort[c] = mode; return render(); }
  if (d.pick){ const [mid, ...rest] = d.pick.split('|'); const tt = rest.join('|');
    const r = ALLR.find(x => x.menuId === mid && x.title === tt); if (r) build.add(r); return render(); }
  if (d.unpick){ const [mid, ...rest] = d.unpick.split('|'); const tt = rest.join('|');
    build.remove({menuId:mid, title:tt}); return render(); }
  if (d.view){ state.view = d.view; state.detail = null; state.recipe = null; return render(); }
  if (d.fav !== undefined){
    favs = favs.includes(d.fav) ? favs.filter(x => x !== d.fav) : favs.concat(d.fav);
    store.set('favs', favs); return render();
  }
  if (d.menu){ state.detail = MENUS.find(m => m.id === d.menu); state.recipe = null; return render(); }
  if (d.recipe !== undefined){ state.recipe = window.__rlist[+d.recipe]; return render(); }
  if (d.scale){ state.scale = +d.scale; store.set('scale', state.scale); return render(); }
  if (d.course !== undefined){ state.course = d.course || null; return render(); }
  if (d.grp){ state.openGroups[d.grp] = !isOpen(d.grp);
              store.set('groups', state.openGroups); return renderFacets(); }
  if (d.f){
    const f = FACETS.find(x => x.id === d.f), sel = state.sel[d.f];
    let v = d.v;
    if (f.type === 'val' && f.opts && typeof f.opts[0] === 'number') v = +v;
    if (f.type === 'bool') { state.sel[d.f] = sel.length ? [] : [true]; }
    else state.sel[d.f] = sel.map(String).includes(String(v))
      ? sel.filter(x => String(x) !== String(v)) : sel.concat(v);
    return render();
  }
  if (d.act === 'reset'){ FACETS.forEach(f => state.sel[f.id] = []); state.course = null; return render(); }
  if (d.act === 'back'){
    if (state.recipe !== null && state.detail){ state.recipe = null; }
    else { state.recipe = null; state.detail = null; }
    return render();
  }
  if (d.act === 'cart'){ toggleCart({kind:'menu', id:d.id}); return render(); }
  if (d.act === 'rcart'){
    const r = state.recipe; if (r) toggleCart({kind:'recipe', id:recipeKey(r)});
    return render();
  }
  if (d.act === 'listserves'){
    const order = [4,8,12,16]; state.scale = order[(order.indexOf(state.scale) + 1) % order.length];
    store.set('scale', state.scale); return render();
  }
  if (d.act === 'untick'){ checked = {}; store.set('checked', checked); return render(); }
  if (d.act === 'clearcart'){ cart = []; store.set('cart', cart); return render(); }
  if (d.act === 'buildclear'){ build.clear(); return render(); }
  if (d.act === 'buildlist'){
    build.items().forEach(r => { if (!inCart('r|' + recipeKey(r))) cart.push({kind:'recipe', id:recipeKey(r)}); });
    store.set('cart', cart); state.view = 'list'; return render();
  }
  if (d.act === 'print' || d.act === 'copy'){ exportText(); return; }
});
document.addEventListener('change', e => {
  const cb = e.target.closest('[data-check]');
  if (!cb) return;
  checked[cb.dataset.check] = cb.checked;
  store.set('checked', checked);
  cb.closest('.shopitem').classList.toggle('done', cb.checked);
});
document.addEventListener('input', e => {
  const el = e.target.closest('[data-bq]');
  if (!el) return;
  const course = el.dataset.bq, pos = el.selectionStart;
  state.bQ[course] = el.value;
  render();
  const again = document.getElementById('bq-' + course);
  if (again){ again.focus(); try { again.setSelectionRange(pos, pos); } catch(err){} }
});
const qEl = document.getElementById('q');
let tId;
qEl.addEventListener('input', () => {
  clearTimeout(tId);
  tId = setTimeout(() => {
    state.q = qEl.value;
    if (state.q && (state.detail || state.recipe !== null)){ state.detail = null; state.recipe = null; }
    render();
  }, 130);
});
document.getElementById('qclr').onclick = () => { qEl.value = ''; state.q = ''; render(); qEl.focus(); };
document.getElementById('brand').onclick = () => {
  state.detail = null; state.recipe = null; state.view = 'menus'; state.q = ''; qEl.value = ''; render();
};
document.getElementById('openfilters').onclick = () => document.getElementById('aside').classList.add('open');
document.getElementById('closefilters').onclick = () => document.getElementById('aside').classList.remove('open');
document.getElementById('tolist').onclick = () => { state.view='list'; state.detail=null; state.recipe=null; render(); };
document.getElementById('themebtn').onclick = () => {
  const cur = document.documentElement.getAttribute('data-theme');
  const next = cur === 'dark' ? 'light' : cur === 'light' ? 'dark'
    : (matchMedia('(prefers-color-scheme: dark)').matches ? 'light' : 'dark');
  document.documentElement.setAttribute('data-theme', next);
  store.set('theme', next);
};
render();
