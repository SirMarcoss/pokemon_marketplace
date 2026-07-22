# Pokémon Marketplace - High-Performance Backend Architecture & RESTful API

Questo documento funge da Unica Fonte di Verità (Single Source of Truth) per l'architettura backend di un marketplace e-commerce B2C ad alte prestazioni dedicato alla gestione e vendita di asset collezionabili. 

Sviluppato inizialmente partendo da requisiti commerciali reali, il sistema è ora mantenuto come architettura open-source focalizzata su latenze sub-200ms, transazioni ACID-complienti, e sicurezza stateless. Il progetto implementa un'architettura rigorosamente decostruita (Headless), esponendo unicamente endpoint RESTful pronti per essere consumati da qualsiasi client o microservizio.

## 1. Visione del Progetto & Architettura Specifica

Il sistema è ingegnerizzato per massimizzare l'efficienza computazionale, la scalabilità orizzontale e l'integrità dei dati finanziari:
*   **Database Layer:** PostgreSQL (Relazionale, ACID-compliente, ottimizzato per transazioni finanziarie concorrenti tramite indici B-Tree su attributi di catalogo e carrello).
*   **Application Layer (API):** Python + FastAPI (Asincrono, I/O non bloccante tramite ASGI, con validazione dei dati nativa in Rust via Pydantic).
*   **Infrastructure & Testing Layer:** Docker per la containerizzazione degli ambienti, Pytest per l'integrazione continua dei flussi finanziari.

## 2. Diario di Bordo & Avanzamento

**Giorno 0: Fondamenta, Versionamento e Data Modeling**
*   **Infrastruttura di Versioning:** Inizializzazione della repository con configurazione rigorosa del filtro `.gitignore` per l'isolamento dei segreti (file `.env`) e dei metadati di sistema. Configurazione di `.gitattributes` per la normalizzazione dei Line Endings (LF vs CRLF).
*   **Modellazione dei Dati:** Progettazione del Diagramma Entità-Relazione (ER) normalizzato in Terza Forma Normale (3NF). Strutturazione delle tabelle core (`users`, `expansions`, `products`, `addresses`, `carts`, `cart_items`, `orders`, `order_items`) con risoluzione esplicita delle relazioni Molti-a-Molti e persistenza dello stato storico dei prezzi per prevenire anomalie contabili.
*   **Analisi dei Requisiti Funzionali:** Definizione del flusso transazionale di stato: Carrello Asincrono -> Checkout Vincolato -> Validazione Pagamento Stripe -> Cristallizzazione dell'Ordine.

## 3. Roadmap Sequenziale di Sviluppo (Engineering Backlog)

Il flusso di lavoro segue un approccio rigoroso dal basso verso l'alto (Bottom-Up), partendo dallo schema dati fino all'esposizione sicura degli endpoint.

**Fase 1: Setup Ambiente & Database Object Mapping (ORM)**
*   **Task 1.1 - Isolamento dei Runtime:** Configurazione degli ambienti virtuali locali Python e gestione rigorosa delle dipendenze.
*   **Task 1.2 - Data Access Layer (SQLAlchemy 2.0):** Traduzione dello schema DB in modelli Python. Tipizzazione rigida dei campi (es. UUID per le chiavi primarie, `Integer` per i prezzi finanziari rappresentati in centesimi per evitare errori di floating-point).
*   **Task 1.3 - Sistema di Migrazione (Alembic):** Configurazione del tracciamento storico delle evoluzioni dello schema DDL, garantendo l'integrità dei dati esistenti durante i deployment.

**Fase 2: Sviluppo delle API Core & Logica di Business**
*   **Task 2.1 - Sottosistema di Autenticazione Stateless:** Implementazione di registrazione e login. Hashing crittografico delle password tramite `bcrypt`. Generazione di JSON Web Tokens (JWT) trasmessi e validati in modo stateless.
*   **Task 2.2 - Catalogo Service (CRUD Ottimizzato):** Sviluppo degli endpoint di interrogazione del catalogo con paginazione efficiente (limit/offset o cursor-based), filtraggio dinamico su attributi indicizzati (`is_foil`, `condition`) e JOIN ottimizzate con SQLAlchemy.
*   **Task 2.3 - Carrello Asincrono (Concurrency Control):** Sviluppo della logica di mutazione delle quantità nel carrello. Implementazione di controlli a livello di database per garantire la consistenza logica e prevenire l'allocazione di quantità superiori allo `stock_quantity` effettivo.

**Fase 3: Integrazione Finanziaria & Webhooks**
*   **Task 3.1 - Stripe SDK Integration:** Costruzione degli endpoint di inizializzazione del `PaymentIntent`, assicurando che il calcolo matematico del totale carrello avvenga esclusivamente e in modo autoritativo lato server.
*   **Task 3.2 - Asynchronous Webhooks:** Implementazione di un listener crittografato per i webhook di Stripe. L'aggiornamento dello stato dell'ordine in `PAID` è subordinato alla verifica crittografica della firma del webhook, azzerando il rischio di frodi client-side.

**Fase 4: Containerizzazione, Testing & Documentazione**
*   **Task 4.1 - Dockerizzazione:** Creazione di `Dockerfile` e `docker-compose.yml` per l'orchestrazione locale simultanea di PostgreSQL e del server Uvicorn, permettendo un setup "one-click" per i revisori.
*   **Task 4.2 - Suite di Testing (Pytest):** Copertura con test di integrazione dei flussi critici (calcolo tasse, concorrenza sul carrello, decodifica JWT).
*   **Task 4.3 - Interactive Documentation:** Esposizione automatica delle specifiche OpenAPI (Swagger UI) per facilitare l'esplorazione e il testing manuale degli endpoint.

## 4. Regolamento Interno di Sviluppo (Git Workflow)

L'osservanza di queste regole previene il debito tecnico e mantiene lo standard enterprise della repository:
*   **Stabilità del Main:** Il branch `main` rappresenta l'ambiente stabile. I push diretti su `main` sono categoricamente vietati.
*   **GitHub Flow:** Ogni feature o bugfix nasce in un ramo isolato (`feature/nome` o `bugfix/nome`).
*   **Code Review Obbligatoria:** Il merge verso `main` avviene unicamente tramite Pull Request. Giulio (o il peer reviewer assegnato) deve ispezionare la logica, verificare la copertura dei test e approvare formalmente la PR prima dell'integrazione.
*   **Conventional Commits:** Ogni commit deve dichiarare il proprio intento algoritmico:
    *   `feat(scope): ...` (Nuova funzionalità API / Modello)
    *   `fix(scope): ...` (Risoluzione bug)
    *   `chore(scope): ...` (Aggiornamento configurazioni, Docker, CI)
    *   `test(scope): ...` (Aggiunta o refactoring test suite)

## 5. Stack Tecnologico di Riferimento

*   **Linguaggio Core:** Python 3.x
*   **Web Framework:** FastAPI
*   **Application Server:** Uvicorn (Traduzione asincrona ASGI per massimizzare il throughput HTTP).
*   **Validazione Dati:** Pydantic (Validazione e serializzazione rigorosa in fase di runtime).
*   **Motore Database:** PostgreSQL
*   **Object-Relational Mapper (ORM):** SQLAlchemy 2.0
*   **Versionamento Database:** Alembic
*   **Sicurezza & Crittografia:** `passlib[bcrypt]` e `python-jose` (Hashing password e generazione JWT).
*   **Integrazione Pagamenti:** Stripe Python SDK
*   **Testing & Infrastructure:** Pytest, Docker, Docker Compose, GitHub Actions (CI).