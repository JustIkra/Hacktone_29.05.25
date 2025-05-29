CREATE TABLE role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    permissions TEXT
);

CREATE TABLE client (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact_email VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE service (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    api_endpoint VARCHAR(256),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE tariff (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES service(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price NUMERIC(12, 2) NOT NULL,
    limits JSONB
);

CREATE TABLE client_service (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES client(id) ON DELETE CASCADE,
    service_id INTEGER NOT NULL REFERENCES service(id) ON DELETE CASCADE,
    tariff_id INTEGER REFERENCES tariff(id) ON DELETE SET NULL,
    subscribed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP
);

CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    name VARCHAR(100),
    role_id INTEGER REFERENCES role(id) ON DELETE SET NULL,
    client_id INTEGER REFERENCES client(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE user_service (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    client_service_id INTEGER NOT NULL REFERENCES client_service(id) ON DELETE CASCADE,
    granted_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE usage_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    service_id INTEGER NOT NULL REFERENCES service(id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    action VARCHAR(50),
    details JSONB
);