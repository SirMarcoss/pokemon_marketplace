CREATE TABLE "users" (
  "id" uuid PRIMARY KEY DEFAULT (gen_random_uuid()),
  "email" varchar UNIQUE NOT NULL,
  "password_hash" varchar NOT NULL,
  "role" varchar NOT NULL DEFAULT 'CUSTOMER',
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "expansions" (
  "id" uuid PRIMARY KEY DEFAULT (gen_random_uuid()),
  "name" varchar UNIQUE NOT NULL,
  "release_date" date,
  "series" varchar
);

CREATE TABLE "addresses" (
  "id" uuid PRIMARY KEY DEFAULT (gen_random_uuid()),
  "user_id" uuid,
  "full_name" varchar NOT NULL,
  "street_address" varchar NOT NULL,
  "city" varchar NOT NULL,
  "postal_code" varchar NOT NULL,
  "country" varchar NOT NULL DEFAULT 'IT'
);

CREATE TABLE "products" (
  "id" uuid PRIMARY KEY DEFAULT (gen_random_uuid()),
  "name" varchar NOT NULL,
  "expansion_id" uuid,
  "condition" varchar NOT NULL,
  "language" varchar NOT NULL,
  "is_foil" boolean DEFAULT false,
  "price" integer NOT NULL,
  "stock_quantity" integer NOT NULL DEFAULT 0,
  "image_url" varchar,
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "carts" (
  "id" uuid PRIMARY KEY DEFAULT (gen_random_uuid()),
  "user_id" uuid UNIQUE,
  "updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "orders" (
  "id" uuid PRIMARY KEY DEFAULT (gen_random_uuid()),
  "user_id" uuid,
  "shipping_address_id" uuid,
  "status" varchar NOT NULL DEFAULT 'PENDING',
  "stripe_payment_intent_id" varchar UNIQUE,
  "total_amount" integer NOT NULL,
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "order_items" (
  "id" uuid PRIMARY KEY DEFAULT (gen_random_uuid()),
  "order_id" uuid,
  "product_id" uuid,
  "quantity" integer NOT NULL DEFAULT 1,
  "unit_price_at_purchase" integer NOT NULL
);

CREATE TABLE "cart_items" (
  "id" uuid PRIMARY KEY DEFAULT (gen_random_uuid()),
  "cart_id" uuid,
  "product_id" uuid,
  "quantity" integer NOT NULL DEFAULT 1
);

ALTER TABLE "addresses" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "products" ADD FOREIGN KEY ("expansion_id") REFERENCES "expansions" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "carts" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "orders" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "orders" ADD FOREIGN KEY ("shipping_address_id") REFERENCES "addresses" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "order_items" ADD FOREIGN KEY ("order_id") REFERENCES "orders" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "order_items" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "cart_items" ADD FOREIGN KEY ("cart_id") REFERENCES "carts" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "cart_items" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("id") DEFERRABLE INITIALLY IMMEDIATE;
