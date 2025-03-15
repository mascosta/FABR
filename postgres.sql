-- Criação da tabela network_traffic
CREATE TABLE network_traffic (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    src_ip VARCHAR(45) NOT NULL,
    dst_ip VARCHAR(45) NOT NULL,
    protocol_name VARCHAR(50),
    src_service VARCHAR(50),
    dst_service VARCHAR(50),
    src_country_code VARCHAR(3),
    src_city VARCHAR(255),
    src_latitude FLOAT,
    src_longitude FLOAT,
    dst_country_code VARCHAR(3),
    dst_city VARCHAR(255),
    dst_latitude FLOAT,
    dst_longitude FLOAT,
    src_port INT,
    dst_port INT
);

-- Criação da tabela wl_address_local para endereços permitidos
CREATE TABLE wl_address_local (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(45) UNIQUE NOT NULL,
    timestamp_added TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Criação da tabela tp_address_local para endereços em Tarpit
CREATE TABLE tp_address_local (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(45) UNIQUE NOT NULL,
    country_code VARCHAR(3),
    abuse_confidence_score INT,
    last_reported_at TIMESTAMP WITHOUT TIME ZONE,
    src_longitude FLOAT,
    src_latitude FLOAT
);

-- Criação da tabela bl_local_cache para cache de endereços bloqueados
CREATE TABLE bl_local_cache (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(45) UNIQUE NOT NULL,
    country_code VARCHAR(3),
    city VARCHAR(255),
    abuse_confidence_score INT,
    last_reported_at TIMESTAMP WITHOUT TIME ZONE,
    timestamp_added TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Criação da tabela bl_address_local para endereços na blacklist a serem bloqueados imediatamente
CREATE TABLE bl_address_local (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(45) UNIQUE NOT NULL,
    country_code VARCHAR(3),
    city VARCHAR(255),
    abuse_confidence_score INT,
    last_reported_at TIMESTAMP WITHOUT TIME ZONE,
    timestamp_added TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    src_latitude FLOAT,
    src_longitude FLOAT
);