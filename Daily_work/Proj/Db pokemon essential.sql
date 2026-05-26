-- ============================================================
-- ESTENSIONI
-- ============================================================

-- gen_random_uuid() è built-in da PostgreSQL 13.
-- Se usi una versione precedente, decommenta:
-- CREATE EXTENSION IF NOT EXISTS "pgcrypto";


-- ============================================================
-- TIPI ENUMERATI
-- ============================================================

CREATE TYPE payment_status_enum AS ENUM (
    'pending',
    'paid',
    'failed',
    'refunded'
);

CREATE TYPE fulfillment_status_enum AS ENUM (
    'unfulfilled',
    'processing',
    'shipped',
    'delivered',
    'cancelled'
);


-- ============================================================
-- 1. AMMINISTRATORI
-- ============================================================

CREATE TABLE admins (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ============================================================
-- 2. CATEGORIE
-- ============================================================

CREATE TABLE categories (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL
);


-- ============================================================
-- 3. PRODOTTI (MASTER)
-- ============================================================

CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(255) NOT NULL,
    slug        VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    category_id INT REFERENCES categories(id) ON DELETE RESTRICT,
    is_active   BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ============================================================
-- 4. VARIANTI (OGGETTO FISICO / SKU)
-- ============================================================

CREATE TABLE product_variants (
    id                SERIAL PRIMARY KEY,
    product_id        INT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    sku               VARCHAR(100) UNIQUE NOT NULL,
    size              VARCHAR(50),
    color             VARCHAR(50),
    price_net_cents   INT NOT NULL
                      CONSTRAINT price_net_positivo CHECK (price_net_cents > 0),
    tax_rate          NUMERIC(5,2) NOT NULL DEFAULT 22.00
                      CONSTRAINT tax_rate_valida CHECK (tax_rate >= 0 AND tax_rate <= 100),
    price_gross_cents INT GENERATED ALWAYS AS (
                          CAST(ROUND(price_net_cents * (1 + tax_rate / 100.0)) AS INT)
                      ) STORED,
    stock             INT NOT NULL DEFAULT 0
                      CONSTRAINT stock_non_negativo CHECK (stock >= 0),
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    img_master_url    TEXT,
    img_thumb_url     TEXT,
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ============================================================
-- 5. ORDINI
-- ============================================================

CREATE TABLE orders (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_email     VARCHAR(255) NOT NULL,
    customer_name      VARCHAR(255) NOT NULL,
    shipping_street    VARCHAR(255) NOT NULL,
    shipping_city      VARCHAR(255) NOT NULL,
    shipping_zip_code  VARCHAR(20)  NOT NULL,
    shipping_province  VARCHAR(100) NOT NULL,
    shipping_country   VARCHAR(100) NOT NULL DEFAULT 'Italia',
    total_amount_cents INT NOT NULL CONSTRAINT total_positivo CHECK (total_amount_cents > 0),
    stripe_intent_id   VARCHAR(255) UNIQUE,
    payment_status     payment_status_enum     NOT NULL DEFAULT 'pending',
    fulfillment_status fulfillment_status_enum NOT NULL DEFAULT 'unfulfilled',
    -- NULL = guest checkout; diventerà FK quando si implementa la tabella users
    user_id            UUID DEFAULT NULL,
    created_at         TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ============================================================
-- 6. VOCI ORDINE (SNAPSHOT STORICO IMMUTABILE)
-- ============================================================

CREATE TABLE order_items (
    id         SERIAL PRIMARY KEY,
    order_id   UUID NOT NULL REFERENCES orders(id) ON DELETE RESTRICT,
    -- NULL intenzionale: se la variante viene eliminata dal catalogo,
    -- lo snapshot storico dell'ordine deve sopravvivere comunque
    variant_id INT REFERENCES product_variants(id) ON DELETE SET NULL,

    quantity                      INT          NOT NULL CONSTRAINT quantita_positiva CHECK (quantity > 0),
    product_name_at_purchase      VARCHAR(255) NOT NULL,
    sku_at_purchase               VARCHAR(100) NOT NULL,
    price_net_cents_at_purchase   INT          NOT NULL CONSTRAINT snap_net_positivo CHECK (price_net_cents_at_purchase > 0),
    tax_rate_at_purchase          NUMERIC(5,2) NOT NULL,
    price_gross_cents_at_purchase INT          NOT NULL CONSTRAINT snap_gross_positivo CHECK (price_gross_cents_at_purchase > 0),
    created_at                    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ============================================================
-- FUNZIONE TRIGGER (riutilizzabile su qualsiasi tabella)
-- ============================================================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- TRIGGER
-- ============================================================

CREATE TRIGGER trg_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_variants_updated_at
    BEFORE UPDATE ON product_variants
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- INDICI
-- ============================================================

CREATE INDEX idx_products_category_id   ON products(category_id);
CREATE INDEX idx_variants_product_id    ON product_variants(product_id);
CREATE INDEX idx_order_items_order_id   ON order_items(order_id);
CREATE INDEX idx_order_items_variant_id ON order_items(variant_id);
CREATE INDEX idx_orders_customer_email  ON orders(customer_email);

CREATE INDEX idx_products_is_active ON products(is_active)
    WHERE is_active = TRUE;

CREATE INDEX idx_variants_is_active ON product_variants(is_active)
    WHERE is_active = TRUE;

-- Da aggiungere nella migration che implementa la tabella users:
-- CREATE INDEX idx_orders_user_id ON orders(user_id);