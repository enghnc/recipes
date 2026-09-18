/**
 * Runs the built app in a stub DOM and exercises every view.
 * Catches the class of bug that a syntax check cannot: code that parses
 * fine but throws, or lands in the wrong <script>/<style> block.
 *
 *   node tests/smoke.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const FILE = path.join(ROOT, 'dist', 'fire-and-kettle-app.html');
const html = fs.readFileSync(FILE, 'utf8');

const dataRaw = html.match(/<script id="data" type="application\/json">([\s\S]*?)<\/script>/)[1];
const code = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].pop()[1];

const store = {};
globalThis.localStorage = { getItem: k => store[k] ?? null, setItem: (k, v) => { store[k] = v; } };
globalThis.matchMedia = () => ({ matches: false });
const el = t => ({
  textContent: t || '', innerHTML: '', style: {}, dataset: {}, value: '',
  setAttribute() {}, getAttribute: () => null, focus() {}, select() {},
  classList: { toggle() {}, add() {}, remove() {} },
  addEventListener() {}, querySelectorAll: () => [], querySelector: () => null, closest: () => null,
});
globalThis.document = {
  getElementById: id => el(id === 'data' ? dataRaw : ''),
  querySelector: () => el(), querySelectorAll: () => [],
  addEventListener() {}, createElement: () => el(),
};
globalThis.window = { scrollTo() {}, print() {} };
try { globalThis.navigator ??= {}; } catch { /* Node 22 defines it read-only */ }

let failed = 0;
const check = (name, fn) => {
  try {
    const out = fn();
    console.log(`  ok    ${name}${out ? '  ' + out : ''}`);
  } catch (e) {
    failed++;
    console.log(`  FAIL  ${name}\n        ${e.message}`);
  }
};

const api = new Function(code + `
;return { state, MENUS, LIBRARY, ALLR, build, viewMenus, viewRecipes, viewLibrary,
          viewBuild, viewList, viewMenuDetail, viewRecipeDetail, menuCartItems,
          recipeCartItems, splitIngredient, libraryRef, textForCurrentView,
          cart, recipeKey, aggregate, buyLinks, glossify, photoTag };`)();

console.log(`\nFire & Kettle smoke tests — ${path.relative(ROOT, FILE)}\n`);
check('data loads', () => `${api.MENUS.length} menus, ${api.LIBRARY.length} library, ${api.ALLR.length} recipes`);
check('menus view', () => `${api.viewMenus().length} chars`);
check('recipes view', () => `${api.viewRecipes().length} chars`);
check('library view', () => `${api.viewLibrary().length} chars`);
check('build view', () => `${api.viewBuild().length} chars`);
check('menu detail', () => `${api.viewMenuDetail(api.MENUS[0]).length} chars`);
check('recipe detail', () => {
  api.state.recipe = api.ALLR[0];
  return `${api.viewRecipeDetail(api.ALLR[0]).length} chars`;
});
check('whole-menu shopping list', () => {
  const items = api.menuCartItems(api.MENUS[0], 8);
  if (!items.length) throw new Error('no items');
  if (!items.some(i => i.cat === 'Drinks')) throw new Error('drinks missing');
  if (!items.some(i => i.cat === 'Fuel & wood')) throw new Error('fuel missing');
  return `${items.length} lines, drinks + fuel present`;
});
check('compound lines split', () => {
  const r = api.splitIngredient('1 tbsp each granulated garlic and onion');
  if (r.length !== 2) throw new Error(JSON.stringify(r));
  return r.join(' / ');
});
check('library cross-reference resolves', () => {
  const r = api.libraryRef('Chimichurri (Chapter 22)');
  if (!r) throw new Error('unresolved');
  return r.title;
});
check('per-glass does not scale', () => {
  const d = api.ALLR.find(x => /Fernet con Coca/.test(x.title));
  api.state.scale = 16;
  const h = api.viewRecipeDetail(d);
  if (!/50 ml Fernet/.test(h)) throw new Error('per-glass quantity was scaled');
  api.state.scale = 8;
  return '50 ml held at 16 servings';
});
check('text export', () => `${api.textForCurrentView().length} chars`);
check('glossary links a known term without breaking existing markup', () => {
  const out = api.glossify('Rest the <strong>porchetta</strong> for asado night.');
  if (!/<a class="gloss" href="https:\/\/en\.wikipedia\.org\/wiki\/Porchetta"[^>]*>porchetta<\/a>/.test(out))
    throw new Error(`porchetta not linked: ${out}`);
  if (!/<a class="gloss" href="https:\/\/en\.wikipedia\.org\/wiki\/Asado"[^>]*>asado<\/a>/.test(out))
    throw new Error(`asado not linked: ${out}`);
  if (!/<strong>.*<\/strong>/.test(out)) throw new Error(`existing <strong> tag was corrupted: ${out}`);
  return out;
});
check('photoTag never puts a credit link inside a clickable card (invalid HTML + double-nav)', () => {
  const img = {file: 'menus/ch99.jpg', credit: 'Someone', sourceUrl: 'https://example.com', license: 'CC BY 2.0'};
  const card = api.photoTag(img, 'Test Menu', 'card-photo', false);
  if (/<a /.test(card)) throw new Error(`card photo must not include a link when nested in a <button>: ${card}`);
  const detail = api.photoTag(img, 'Test Menu', 'detail-photo', true);
  if (!/<a class="credit"[^>]*>Photo: Someone \(CC BY 2\.0\)<\/a>/.test(detail))
    throw new Error(`detail photo should show a credit link: ${detail}`);
  if (api.photoTag(null, 'x', 'card-photo', false) !== '') throw new Error('missing image should render nothing');
  return 'card has no link, detail has credit';
});
check('recipe detail pages actually surface a glossary link', () => {
  const withTerm = api.ALLR.find(r => /\bporchetta\b/i.test(r.title + ' ' + r.headnote + ' ' + r.method.join(' ')));
  if (!withTerm) throw new Error('no recipe mentions a known glossary term to test against');
  const html = api.viewRecipeDetail(withTerm);
  if (!/class="gloss"/.test(html)) throw new Error('no .gloss link rendered on a recipe that mentions one');
  return withTerm.title;
});
check('shopping list merges a shared ingredient across two different cart items', () => {
  const hasSalt = r => (r.ingredients || []).some(i => i.type === 'item' && /\bsalt\b/i.test(i.text));
  const salty = api.ALLR.filter(hasSalt);
  if (salty.length < 2) throw new Error('need two salty recipes in the book to test this');
  const [rA, rB] = salty;
  api.cart.length = 0;
  api.cart.push({kind: 'recipe', id: api.recipeKey(rA)}, {kind: 'recipe', id: api.recipeKey(rB)});
  const html = api.viewList();
  const saltRows = html.match(/data-check="salt\|/g) || [];
  api.cart.length = 0;
  if (saltRows.length !== 1) throw new Error(`expected 1 merged "salt" row across both recipes, got ${saltRows.length}`);
  return `${rA.title} + ${rB.title} -> 1 merged salt line`;
});
check('garlic salt buys as a jar, not a box', () => {
  const out = api.aggregate([{qty: 1, unit: 'tbsp', name: 'garlic salt', mult: 1, cat: 'Pantry', from: 'Test'}], 8);
  if (out.length !== 1) throw new Error(`expected 1 line, got ${JSON.stringify(out)}`);
  if (!/\bjar\b/i.test(out[0].item)) throw new Error(`expected "jar", got: ${out[0].item}`);
  return out[0].item;
});
check('shopping list rows carry buy links', () => {
  const out = api.aggregate([{qty: 1, unit: 'lb', name: 'flank steak (about 2 steaks)', mult: 1, cat: 'Meat & fish', from: 'Test'}], 8);
  if (!out[0].name) throw new Error('aggregate row is missing a plain "name" field for link-building');
  const buy = api.buyLinks(out[0].name);
  if (!/^https:\/\/www\.amazon\.com\/s\?k=/.test(buy.amazon)) throw new Error(`bad amazon link: ${buy.amazon}`);
  if (/%28|%29/.test(buy.amazon)) throw new Error(`parenthetical leaked into query: ${buy.amazon}`);
  if (!/near\+me|near%20me/.test(buy.nearby)) throw new Error(`bad nearby link: ${buy.nearby}`);
  return buy.amazon;
});

console.log(failed ? `\n${failed} failing\n` : '\nall passing\n');
process.exit(failed ? 1 : 0);
