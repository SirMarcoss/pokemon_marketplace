-- ============================================================
-- 0. ESTENSIONI
-- ============================================================
-- Necessario solo per versioni di PostgreSQL antecedenti alla 13
-- CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- 1. TIPI ENUMERATI (Domini ristretti per integrità dei dati)
-- ============================================================
CREATE TYPE user_role_enum AS ENUM (
    'customer',
    'admin' -- L'admin è il proprietario/staff del negozio fisico
);

CREATE TYPE payment_status_enum AS ENUM (
    'pending',
    'authorized', -- Fondi bloccati ma non ancora incassati (Auth & Capture)
    'paid',
    'failed',
    'refunded'
);

CREATE TYPE fulfillment_status_enum AS ENUM (
    'unfulfilled',
    'processing',
    'shipped',
    'ready_for_pickup', -- Cruciale per un negozio fisico (ritiro in sede)
    'delivered',
    'cancelled'
);

CREATE TYPE card_condition_enum AS ENUM (
    'mint',
    'near_mint',
    'excellent',
    'good',
    'lightly_played',
    'played',
    'poor'
);

-- ============================================================
-- 2. UTENTI E AUTENTICAZIONE (RBAC Centralizzato)
-- ============================================================
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name    VARCHAR(100),
    last_name     VARCHAR(100),
    role          user_role_enum NOT NULL DEFAULT 'customer',
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        deleted_at    TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- ============================================================
-- 3. GERARCHIA DEL CATALOGO (TCG Domain)
-- ============================================================
CREATE TABLE categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL, -- es. 'Pokémon', 'Yu-Gi-Oh!', 'Accessori'
    slug        VARCHAR(255) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE expansions (
    id           SERIAL PRIMARY KEY,
    category_id  INT NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    name         VARCHAR(255) NOT NULL, -- es. 'Set Base', 'Orizzonti Moderni 2'
    release_date DATE,
    total_cards  INT
);

-- ============================================================
-- 4. PRODOTTI (L'astrazione)
-- ============================================================
CREATE TABLE products (
    id           SERIAL PRIMARY KEY,
    title        VARCHAR(255) NOT NULL,
    slug         VARCHAR(255) UNIQUE NOT NULL,
    description  TEXT,
    category_id  INT NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    expansion_id INT REFERENCES expansions(id) ON DELETE SET NULL,
    is_active    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at   TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- ============================================================
-- 5. VARIANTI (L'oggetto fisico e lo SKU)
-- ============================================================
CREATE TABLE product_variants (
    id                SERIAL PRIMARY KEY,
    product_id        INT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    sku               VARCHAR(100) UNIQUE NOT NULL,

    -- Attributi Dominio TCG
    card_condition    card_condition_enum, -- NULL se è un accessorio (es. bustine protettive)
    language          VARCHAR(2) DEFAULT 'IT',
    is_foil           BOOLEAN NOT NULL DEFAULT FALSE,
    is_first_edition  BOOLEAN NOT NULL DEFAULT FALSE,

    -- Dati Finanziari e Logistici
    price_net_cents   INT NOT NULL CONSTRAINT price_net_positivo CHECK (price_net_cents > 0),
    tax_rate          NUMERIC(5,2) NOT NULL DEFAULT 22.00 CONSTRAINT tax_rate_valida CHECK (tax_rate >= 0 AND tax_rate <= 100),
    price_gross_cents INT GENERATED ALWAYS AS (
                          CAST(ROUND(price_net_cents * (1 + tax_rate / 100.0)) AS INT)
                      ) STORED,
    stock             INT NOT NULL DEFAULT 0 CONSTRAINT stock_non_negativo CHECK (stock >= 0),

    -- Optimistic Concurrency Control
    version           INT NOT NULL DEFAULT 1,

    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at        TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- ============================================================
-- 6. CARRELLO (Shopping Cart)
-- ============================================================
CREATE TABLE carts (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE, -- UNIQUE perché 1 utente = 1 carrello attivo
    session_id VARCHAR(255) UNIQUE, -- Per i guest checkout senza account
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT cart_owner_check CHECK (user_id IS NOT NULL OR session_id IS NOT NULL)
);

CREATE TABLE cart_items (
    id         SERIAL PRIMARY KEY,
    cart_id    UUID NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    variant_id INT NOT NULL REFERENCES product_variants(id) ON DELETE CASCADE,
    quantity   INT NOT NULL CONSTRAINT cart_qty_positiva CHECK (quantity > 0),
    added_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(cart_id, variant_id) -- Evita duplicati dello stesso item nel carrello
);

-- ============================================================
-- 7. ORDINI E SNAPSHOT FINANZIARI
-- ============================================================
CREATE TABLE orders (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id            UUID REFERENCES users(id) ON DELETE SET NULL,
    customer_email     VARCHAR(255) NOT NULL,

    -- Snapshot dell'indirizzo in JSONB per flessibilità e immutabilità
    shipping_address   JSONB NOT NULL,
    billing_address    JSONB NOT NULL,

    total_amount_cents INT NOT NULL CONSTRAINT total_positivo CHECK (total_amount_cents > 0),
    stripe_intent_id   VARCHAR(255) UNIQUE,
    payment_status     payment_status_enum NOT NULL DEFAULT 'pending',
    fulfillment_status fulfillment_status_enum NOT NULL DEFAULT 'unfulfilled',
    notes              TEXT, -- Eventuali note del cliente o del negozio

    created_at         TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at         TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE order_items (
    id         SERIAL PRIMARY KEY,
    order_id   UUID NOT NULL REFERENCES orders(id) ON DELETE RESTRICT,
    variant_id INT REFERENCES product_variants(id) ON DELETE SET NULL,

    -- Snapshot Immutabile (Se il prodotto cambia prezzo o nome domani, l'ordine non si altera)
    quantity                      INT NOT NULL CONSTRAINT order_qty_positiva CHECK (quantity > 0),
    product_name_at_purchase      VARCHAR(255) NOT NULL,
    sku_at_purchase               VARCHAR(100) NOT NULL,
    price_net_cents_at_purchase   INT NOT NULL,
    tax_rate_at_purchase          NUMERIC(5,2) NOT NULL,
    price_gross_cents_at_purchase INT NOT NULL,

    created_at                    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- 8. FUNZIONI E TRIGGER
-- ============================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_variants_updated_at BEFORE UPDATE ON product_variants FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_carts_updated_at BEFORE UPDATE ON carts FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- 9. INDICI STRATEGICI (Performance Tuning)
-- ============================================================
-- Indici per Foreign Keys (PostgreSQL non li crea in automatico)
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_expansion_id ON products(expansion_id);
CREATE INDEX idx_variants_product_id ON product_variants(product_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_variant_id ON order_items(variant_id);
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Indici per ottimizzare le query lato client (es. mostra solo prodotti attivi e non eliminati)
CREATE INDEX idx_products_catalog ON products(id) WHERE is_active = TRUE AND deleted_at IS NULL;
CREATE INDEX idx_variants_catalog ON product_variants(product_id) WHERE is_active = TRUE AND deleted_at IS NULL AND stock > 0;

-- Indici per le lookup frequenti
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_variants_sku ON product_variants(sku);