# Volantini e Promozioni · F.lli Petrillo

Pagina web con le grafiche di volantini e promozioni, da aprire dall'icona "Volantini" dell'app aziendale.
Chi apre il link vede **solo questa pagina**, senza nessun'altra cartella o file.

---

## Configurazione iniziale (una volta sola, circa 10 minuti)

1. **Crea un account GitHub** (gratuito) su https://github.com, per esempio con l'email aziendale.
2. **Crea un repository**: in alto a destra fai clic su **+** → **New repository**
   - Nome: `volantini` (oppure quello che preferisci: comparirà nel link)
   - Visibilità: **Public** (GitHub Pages gratuito richiede un repository pubblico. Il codice della pagina è comunque visibile a chiunque, come per qualsiasi sito.)
   - Fai clic su **Create repository**
3. **Carica i file di questa cartella**: nella pagina del repository appena creato fai clic su **uploading an existing file** e trascina **tutto il contenuto** di questa cartella (`index.html`, `LEGGIMI.md`, la cartella `volantini` e la cartella `.github`).
   > ⚠️ La cartella `.github` è nascosta su Mac e Windows. Su Mac premi `Cmd + Shift + .` nel Finder per vederla. Su Windows attiva "Elementi nascosti" nel menu Visualizza.
   Poi fai clic su **Commit changes**.
4. **Attiva la pubblicazione**: **Settings** → **Pages** → alla voce *Source* scegli **GitHub Actions**.
5. Dopo uno o due minuti, nella scheda **Actions**, vedrai un pallino verde accanto a "Pubblica volantini". Il link sarà:

   **`https://NOME-UTENTE.github.io/volantini/`**

   Copia questo link nell'icona "Volantini" dell'app: non cambierà mai.

**Logo (facoltativo):** carica nella cartella principale (non dentro `volantini/`) un file chiamato `logo.png` e comparirà nella testata.

**Colori:** in `index.html`, all'inizio, trovi il blocco "COLORI DEL MARCHIO". Cambia i codici colore con quelli del marchio.

---

## Uso quotidiano: aggiungere o togliere una grafica

**Aggiungere:** apri il repository → cartella `volantini` → **Add file** → **Upload files** → trascina la grafica → **Commit changes**.
Funziona anche dal telefono, dal browser, aprendo github.com.
Dopo circa un minuto la grafica è online.

**Togliere:** apri il file nella cartella `volantini` → menu **···** → **Delete file** → **Commit changes**.
Di solito però non serve, perché le promo scadute si nascondono da sole (vedi sotto).

### Novità Canvass: ogni settimana
Carica il nuovo PDF nella cartella `volantini` chiamandolo **sempre** `Novità-Canvass.pdf`: sostituisce da solo quello vecchio.
Non ha date (le novità restano valide finché ci sono), sotto il titolo compare "Aggiornato il …" e per 7 giorni il badge **NUOVO**.

### Come chiamare i file (così le date le gestisce la pagina)

| Nome del file | Cosa succede |
|---|---|
| `2026-12-01_2026-12-24_Promo-Natale.jpg` | Visibile **dal 1 al 24 dicembre**, poi sparisce da sola |
| `2026-11-30_Volantino-Novembre.pdf` | Visibile **da subito fino al 30 novembre** |
| `Catalogo-Bevande.jpg` | **Sempre visibile**, finché non la elimini |

- Le date vanno scritte come **anno-mese-giorno** (`2026-12-01`), separate dal titolo con un trattino basso `_`.
- Il titolo mostrato sotto la grafica è quello del nome del file: i trattini diventano spazi.
- Formati accettati: **JPG, PNG, WEBP, PDF**.
- I PDF vengono trasformati da soli in immagini (copertina nella scheda e pagine da scorrere col dito), così si leggono bene su qualsiasi telefono. Il pulsante **Scarica** dà sempre il PDF originale.
- Le grafiche più recenti compaiono per prime. Quelle caricate negli ultimi 7 giorni hanno il badge **NUOVO**.
- **Offerte a scadenza:** se nel titolo c'è *Promo*, *Offerta*, *Sconti* o *Volantino* (per esempio `2026-12-01_2026-12-24_Promo-Natale.jpg`), la pagina la tratta come offerta: quella che scade prima va **In evidenza** in alto con il conto alla rovescia, e negli ultimi 3 giorni ha il badge **ULTIMI GIORNI**. Le **Novità Canvass** e i **cataloghi** non sono mai trattati come offerte in scadenza.
- Consiglio: esporta le immagini con una larghezza di circa 1500 px. Le grafiche restano nitide e la pagina si apre in fretta anche con il 4G.

---

## Se qualcosa non va
- **La grafica non compare:** controlla la scheda **Actions**. Se c'è una X rossa, apri l'esecuzione e leggi l'errore. Poi controlla che la data nel nome del file non sia già passata e che la data di inizio non sia nel futuro.
- **Ripubblicare a mano:** **Actions** → "Pubblica volantini" → **Run workflow**.

