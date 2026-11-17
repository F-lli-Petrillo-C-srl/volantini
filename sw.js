// Permette di installare la pagina sul telefono e di rivedere senza rete
// le ultime grafiche aperte. Pagina ed elenco vengono sempre presi aggiornati
// quando c'è connessione.
const VERSIONE = 'v2';
const BASE = 'volantini-base-' + VERSIONE;
const GRAFICHE = 'volantini-grafiche';
const MAX_GRAFICHE = 400;   // immagini tenute in memoria al massimo

const FILE_BASE = ['./', 'index.html', 'logo.png', 'manifest.webmanifest', 'lib/page-flip.browser.js',
  'icone/icona-192.png', 'icone/apple-touch-icon.png', 'icone/favicon-32.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(BASE).then(c => c.addAll(FILE_BASE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(chiavi => Promise.all(
    chiavi.filter(k => k.startsWith('volantini-base-') && k !== BASE).map(k => caches.delete(k))
  )).then(() => self.clients.claim()));
});

async function primaLaRete(req){
  try {
    const r = await fetch(req, {cache: 'no-store'});
    if(r.ok){ const c = await caches.open(BASE); c.put(req.url.split('?')[0], r.clone()); }
    return r;
  } catch(err) {
    const c = await caches.match(req.url.split('?')[0]);
    if(c) return c;
    throw err;
  }
}

async function primaLaMemoria(req){
  const c = await caches.match(req);
  if(c) return c;
  const r = await fetch(req);
  if(r.ok){
    const cache = await caches.open(GRAFICHE);
    await cache.put(req, r.clone());
    const chiavi = await cache.keys();
    for(let i = 0; i < chiavi.length - MAX_GRAFICHE; i++) await cache.delete(chiavi[i]);
  }
  return r;
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if(req.method !== 'GET') return;
  const url = new URL(req.url);
  if(url.origin !== location.origin) return;
  if(/\.pdf$/i.test(url.pathname)) return;            // i PDF scaricati non si tengono in memoria
  if(req.mode === 'navigate' || url.pathname.endsWith('volantini.json')){
    e.respondWith(primaLaRete(req));
  } else if(url.pathname.includes('/pagine/') || url.pathname.includes('/volantini/volantini/')){
    e.respondWith(primaLaMemoria(req));                // indirizzi con ?v=: cambiano se cambia il file
  } else {
    e.respondWith(fetch(req).catch(() => caches.match(req)));   // logo, icone: aggiornati, ma disponibili anche senza rete
  }
});
