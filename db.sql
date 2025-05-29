CREATE TABLE Tariffs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    max_users INTEGER NOT NULL,
    max_services INTEGER NOT NULL,
    period_days INTEGER NOT NULL,
    price NUMERIC(12, 2) NOT NULL
);

CREATE TABLE Clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    tariff_id INTEGER NOT NULL REFERENCES Tarrifs(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(256) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    email VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('portal_admin', 'client_admin', 'user')),
    client_id INTEGER REFERENCES Clients(id)
);

CREATE TABLE Services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE ClientServices (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES Clients(id) ON DELETE CASCADE,
    service_id INTEGER NOT NULL REFERENCES Services(id) ON DELETE CASCADE,
    connected_id TIMESTAMP NOT NULL DEFAULT NOW()
    expires_at TIMESTAMP
);

CREATE TABLE Usage (
    id SERIAL PRIMARY KEY,
    client_service_id INTEGER NOT NULL REFERENCES ClientServices(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
    usage_date DATE NOT NULL,
    usage_amount NUMERIC(12, 2) NOT NULL
);