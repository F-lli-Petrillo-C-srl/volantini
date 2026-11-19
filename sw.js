// Permette di installare la pagina sul telefono e di rivedere senza rete
// le ultime grafiche aperte. Pagina ed elenco vengono sempre presi aggiornati
// quando c'è connessione.
const VERSIONE = 'v6';
const BASE = 'volantini-base-' + VERSIONE;
const GRAFICHE = 'volantini-grafiche';
const MAX_GRAFICHE = 400;   // immagini tenute in memoria al massimo

const FILE_BASE = ['./', 'index.html', 'manifest.webmanifest', 'lib/page-flip.browser.js',
  'icone/icona-192.png', 'icone/apple-touch-icon.png', 'icone/favicon-32.png'];

self.addEventListener('install', e => {
  // 'reload': i file si prendono dal sito, mai da una copia vecchia del telefono
  e.waitUntil(caches.open(BASE).then(c => c.addAll(FILE_BASE.map(f => new Request(f, {cache: 'reload'}))))
    .then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(chiavi => Promise.all(
    chiavi.filter(k => k.startsWith('volantini-base-') && k !== BASE).map(k => caches.delete(k))
  )).then(() => self.clients.claim()));
});

async function primaLaRete(req){
  try {
    // richiesta nuova costruita dall'indirizzo: alcuni telefoni (iPhone) con la richiesta
    // di navigazione originale riusano la pagina vecchia invece di chiederla al sito
    const r = await fetch(req.url, {cache: 'no-store', credentials: 'same-origin'});
    if(r.ok){ const c = await caches.open(BASE); c.put(req.url.split('?')[0], r.clone()); }
    return r;
  } catch(err) {
    const c = await caches.match(req.url.split('?')[0]);
    if(c) return c;
    throw err;
  }
}

// Immagini: se già in memoria arrivano all'istante; altrimenti si mostrano mentre
// scaricano e si salvano dopo, senza far aspettare. Una stessa immagine chiesta
// due volte (precaricamento + pagina) si scarica una volta sola.
const inViaggio = new Map();
let daPulire = 0;
async function primaLaMemoria(e){
  const req = e.request;
  const c = await caches.match(req);
  if(c) return c;
  if(inViaggio.has(req.url)) return (await inViaggio.get(req.url)).clone();
  const p = fetch(req);
  inViaggio.set(req.url, p);
  try {
    const r = await p;
    if(r.ok){
      const copia = r.clone();
      e.waitUntil(caches.open(GRAFICHE).then(cache => cache.put(req, copia)).then(() => {
        if(++daPulire % 20) return;                      // controllo dello spazio ogni tanto, non ogni volta
        return caches.open(GRAFICHE).then(async cache => {
          const chiavi = await cache.keys();
          for(let i = 0; i < chiavi.length - MAX_GRAFICHE; i++) await cache.delete(chiavi[i]);
        });
      }).catch(() => {}).finally(() => inViaggio.delete(req.url)));
    } else inViaggio.delete(req.url);
    return r.clone();
  } catch(err) {
    inViaggio.delete(req.url);
    throw err;
  }
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
    e.respondWith(primaLaMemoria(e));              // indirizzi con ?v=: cambiano se cambia il file
  } else {
    e.respondWith(fetch(req).catch(() => caches.match(req)));   // logo, icone: aggiornati, ma disponibili anche senza rete
  }
});
