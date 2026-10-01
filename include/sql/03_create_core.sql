
CREATE TABLE IF NOT EXISTS core.customers (
    customerid    VARCHAR(12)  PRIMARY KEY,
    customername  CHAR(64)     NOT NULL,
    segment       VARCHAR(20)  NOT NULL,
    country       VARCHAR(50)  NOT NULL,
    city          VARCHAR(100),
    state         VARCHAR(50),
    postal_code   CHAR(5),
    region        VARCHAR(20),
    CONSTRAINT ck_customers_name_is_hash CHECK (customername ~ '^[0-9a-f]{64}$'),
    CONSTRAINT ck_customers_postal_code  CHECK (postal_code ~ '^[0-9]{5}$')
);

CREATE TABLE IF NOT EXISTS core.products (
    productid     VARCHAR(20)   PRIMARY KEY,
    category      VARCHAR(30)   NOT NULL,
    subcategory   VARCHAR(30)   NOT NULL,
    product_name  VARCHAR(255)  NOT NULL,
    unit_price    NUMERIC(10,2) NOT NULL,
    CONSTRAINT ck_products_unit_price CHECK (unit_price > 0)
);

CREATE TABLE IF NOT EXISTS core.orders (
    rowid             INTEGER       PRIMARY KEY,
    orderid           VARCHAR(20)   NOT NULL,
    customerid        VARCHAR(12)   NOT NULL REFERENCES core.customers (customerid),
    productid         VARCHAR(20)   NOT NULL REFERENCES core.products (productid),
    orderdate         DATE          NOT NULL,
    shipdate          DATE          NOT NULL,
    shipmode          VARCHAR(20)   NOT NULL,
    sales             NUMERIC(12,4) NOT NULL,
    quantity          SMALLINT      NOT NULL,
    discount          NUMERIC(3,2)  NOT NULL,
    profit            NUMERIC(12,4) NOT NULL,
    deliverytime      SMALLINT      NOT NULL,
    profit_margin     NUMERIC(8,4)  NOT NULL,
    ship_city         VARCHAR(100),
    ship_state        VARCHAR(50),
    ship_postal_code  CHAR(5),
    ship_region       VARCHAR(20),
    CONSTRAINT ck_orders_sales         CHECK (sales > 0),
    CONSTRAINT ck_orders_quantity      CHECK (quantity > 0),
    CONSTRAINT ck_orders_discount      CHECK (discount BETWEEN 0 AND 1),
    CONSTRAINT ck_orders_ship_after    CHECK (shipdate >= orderdate),
    CONSTRAINT ck_orders_deliverytime  CHECK (deliverytime = shipdate - orderdate)
);

CREATE INDEX IF NOT EXISTS idx_orders_orderid    ON core.orders (orderid);
CREATE INDEX IF NOT EXISTS idx_orders_customerid ON core.orders (customerid);
CREATE INDEX IF NOT EXISTS idx_orders_productid  ON core.orders (productid);
