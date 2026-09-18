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
          recipeCartItems, splitIngredient, libraryRef, textForCurrentView };`)();

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

console.log(failed ? `\n${failed} failing\n` : '\nall passing\n');
process.exit(failed ? 1 : 0);
