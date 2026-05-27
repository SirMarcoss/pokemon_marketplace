# Pokémon Marketplace - Engineering Roadmap & Documentation

Questo documento funge da **Unica Fonte di Verità (Single Source of Truth)** per lo sviluppo del marketplace e-commerce B2C dedicato alla vendita di carte Pokémon e collezionabili. Traccia l'architettura del sistema, lo stato dell'arte e la roadmap ingegneristica sequenziale per il team di sviluppo.

---

## 1. Visione del Progetto & Architettura Specifica

Il software è ingegnerizzato come un **E-commerce B2C Single-Vendor**. Il negozio fisico è l'unico amministratore autorizzato a inserire e gestire gli SKU (Stock Keeping Unit). L'architettura è interamente disaccoppiata (**Headless/Decoupled Architecture**) per massimizzare l'efficienza computazionale e abbattere i costi di hosting:

* **Database Layer:** `PostgreSQL` (Relazionale, ACID-compliente, ottimizzato per transazioni finanziarie concorrenti tramite indici B-Tree).
* **Application Layer (Backend):** `Python` + `FastAPI` (Asincrono, I/O non bloccante tramite ASGI, validazione dei dati nativa in Rust via Pydantic).
* **Presentation Layer (Frontend):** `Next.js` (React framework con Server-Side Rendering per ottimizzazione SEO del catalogo).

---

## 2. Diario di Bordo & Avanzamento

### Giorno 0: Fondamenta, Versionamento e Data Modeling
* **Infrastruttura di Versioning:** Inizializzazione della repository privata su GitHub. Configurazione delle regole di scomposizione dei Line Endings (`.gitattributes`) per prevenire conflitti distruttivi tra l'ambiente Unix-based (`LF` su macOS) e l'ambiente Windows (`CRLF`). Configurazione del filtro `.gitignore` per l'isolamento dei file di metadati di sistema e delle credenziali sensibili.
* **Modellazione dei Dati:** Progettazione del Diagramma Entità-Relazione (ER) normalizzato in Terza Forma Normale (3NF). Strutturazione delle tabelle core (`users`, `expansions`, `products`, `addresses`, `carts`, `cart_items`, `orders`, `order_items`) con risoluzione esplicita delle relazioni Molti-a-Molti tramite entità deboli (tabelle ponte) dotate di persistenza dello stato storico dei prezzi.
* **Analisi dei Requisiti Funzionali:** Definizione del flusso logico delle transazioni (Carrello asincrono salvato su DB $
ightarrow$ Checkout con indirizzo vincolato $
ightarrow$ Transazione Stripe $
ightarrow$ Cristallizzazione dell'ordine fiscale).

---

## 3. Roadmap Sequenziale di Sviluppo (Product Backlog)

Il flusso di lavoro segue un approccio rigoroso dal basso verso l'alto (Bottom-Up): dai dati all'interfaccia utente.

### Fase 1: Setup Ambiente & Database Object Mapping (ORM)
* **Task 1.1: Isolamento dei Runtime:** Configurazione degli ambienti virtuali locali (`venv` per Python, gestione dei moduli `npm` per Node).
* **Task 1.2: Configurazione dell'ORM (SQLAlchemy / SQLModel):** Traduzione dello schema DBML in classi ed entità Python. I tipi di dato devono essere rigidi (es. UUID per le chiavi primarie, `Integer` in centesimi per i prezzi finanziari).
* **Task 1.3: Sistema di Migrazione (Alembic):** Configurazione di Alembic per tracciare storicamente le evoluzioni dello schema del database senza mai ricorrere alla distruzione dei dati esistenti.

### Fase 2: Sviluppo delle API Core & Logica di Business (Backend)
* **Task 2.1: Sottosistema di Autenticazione (Auth Service):** Implementazione della registrazione e del login utente. hashing sicuro delle password tramite algoritmo `bcrypt`. Generazione e validazione di Stateful/Stateless Tokens via `JWT` (JSON Web Tokens) trasmessi tramite cookie HTTP-only per prevenire attacchi XSS.
* **Task 2.2: Catalogo Service (CRUD Prodotti):** Implementazione degli endpoint di lettura del catalogo con parametri obbligatori di paginazione, filtraggio binario per attributi indicizzati (`is_foil`, `condition`, `language`) e join efficienti con la tabella normalizzata delle espansioni.
* **Task 2.3: Carrello Asincrono (Cart Service):** Sviluppo della logica di mutazione delle quantità nel carrello sul database, garantendo la consistenza logica (es. impedire l'aggiunta a carrello di una quantità superiore allo `stock_quantity` effettivo del prodotto).

### Fase 3: Integrazione dei Pagamenti & Gestione degli Stati di Transazione
* **Task 3.1: Stripe SDK Integration:** Creazione degli endpoint per l'inizializzazione del `PaymentIntent` di Stripe a partire dal calcolo matematico del totale carrello eseguito lato server.
* **Task 3.2: Sviluppo dei Webhooks Asincroni:** Creazione di un endpoint dedicato all'ascolto delle chiamate di rete crittografate provenienti dai server di Stripe. La transazione nella tabella `orders` cambia stato in `PAID` solo ed esclusivamente alla ricezione del webhook verificato, prevenendo attacchi di manomissione dei prezzi lato client.

### Fase 4: Sviluppo del Presentation Layer (Frontend Next.js)
* **Task 4.1: Design System & Componenti Atomici:** Setup di Tailwind CSS e creazione dei componenti riutilizzabili (`ProductCard`, `CartModal`, `Layout`).
* **Task 4.2: Data Fetching & Caching (React Query / SWR):** Integrazione dei client di rete per consumare le API di FastAPI, implementando il caching automatico per ridurre le chiamate al server e ottimizzare i costi computazionali.
* **Task 4.3: Flusso di Checkout:** Implementazione dei form protetti per l'inserimento dell'indirizzo e del modulo di pagamento sicuro Stripe Elements.

### Fase 5: Testing, Continuous Integration (CI) e Rilascio
* **Task 5.1: Suite di Unit Testing:** Scrittura di test di unità per la logica finanziaria del carrello e della tassazione degli ordini.
* **Task 5.2: GitHub Actions (CI Bot):** Scrittura del workflow in formato YAML per l'esecuzione automatica del build e dei test ad ogni apertura di Pull Request verso `main`.
* **Task 5.3: Cloud Provisioning & Deployment:** Configurazione dei server di produzione (Vercel per il frontend Next.js, Render/AWS per il backend FastAPI e il database gestito PostgreSQL).

---

## 4. Regolamento Interno di Sviluppo (Git Workflow)

Lavorando in un ambiente cross-platform, l'osservanza di queste regole previene il debito tecnico:

1.  **Stabilità del Main:** Il branch `main` rappresenta l'ambiente stabile di produzione. È severamente vietato effettuare `push` diretti su `main`.
2.  **GitHub Flow:** Ogni nuova feature o bugfix deve nascere in un ramo isolato (`feature/nome-funzionalità` o `bugfix/nome-bug`).
3.  **Code Review Obbligatoria:** L'unione di un branch in `main` avviene esclusivamente tramite Pull Request. Il collega che non ha scritto il codice deve ispezionare la logica e approvare formalmente il merge.
4.  **Convenzione dei Commit (Conventional Commits):** Ogni commit deve auto-esplicare la sua natura algoritmica seguendo lo standard:
    * `feat(scope): ...` (Nuova funzionalità)
    * `fix(scope): ...` (Risoluzione di un bug o di un crash)
    * `chore(scope): ...` (Aggiornamento di configurazioni o dipendenze


## 5. Informazioni Utili 
stack da usare/studiare:

BACK-END

*linguaggio core: python
*web framework : FastAPI
*Application server: Uvicorn (FastAPI è solo il framework. Uvicorn è il server fisico in ascolto sulla porta di rete (es. la porta 8000) che traduce i byte in arrivo da internet in oggetti Python leggibili da FastAPI.
*Validazione Dati Automatica: Pydantic
*Motore Database: PostgreSQL
*ORM: SQLAlchemy 2.0
Versionamento DB: Alembic (Tipo git per databse)
Sicurezza informatica ed autenticazione: Passlib e python-jose (crittografia unidirezionale (hashing) per le password e a generare JSON Web Tokens per mantenere gli utenti loggati in modo stateless (senza salvare le sessioni nel database)
Integrazione Pagamenti: Stripe Python SDK



FRONT-END
Libreria core: React.js 
Meta-Framework: Next.js (eact puro genera pagine "vuote" che si riempiono solo dopo il caricamento, distruggendo l'indicizzazione di Google. Next.js introduce il Server-Side Rendering (SSR): pre-compila le pagine delle carte Pokemon sul server prima di inviarle al client, garantendo una SEO perfetta. La SEO è la Search engine optimization, algoritmo che li fa spunatre in alto su google)
linguaggio core: TypeScript
Styling Engine: Tailwind CSS (integrato direttamente nel codice)
Gestione di Rete: TanStack Query (È il ponte tra il frontend e FastAPI. Gestisce automaticamente il caricamento (mostrando gli spinner di loading), la cache (se l'utente torna indietro alla pagina precedente, i dati non vengono riscaricati ma presi dalla memoria) e la sincronizzazione in background.)
Gestione dello Stato Globale: Zustand (o React Context) (Se un utente aggiunge Charizard al carrello nella pagina "Catalogo", il numero sull'icona del carrello nella barra di navigazione in alto deve aggiornarsi istantaneamente. Zustand permette a componenti completamente distanti di leggere e scrivere sulle stesse variabili in tempo reale.)


Componenti Interfaccia (Libreria UI): shadcn/ui (consigliata) IMPORTANRE PER LO STYLING DELLA LENDING PAGE
. Offre componenti accessibili e pre-costruiti (menù a tendina, modali, bottoni, tabelle) di cui tu hai il pieno controllo del codice sorgente per personalizzarli.
