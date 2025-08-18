-- Initialize Energize Database with TimescaleDB
-- Run this script to set up the database schema

-- Create database if not exists (run as superuser)
-- CREATE DATABASE energize;

-- Connect to energize database
\c energize;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- Create schema
CREATE SCHEMA IF NOT EXISTS energize;
SET search_path TO energize, public;

-- Tenants table (multi-tenancy)
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name VARCHAR(255) NOT NULL,
    subscription_plan VARCHAR(50) DEFAULT 'trial',
    max_buildings INTEGER DEFAULT 5,
    max_users INTEGER DEFAULT 10,
    billing_email VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'viewer' CHECK (role IN ('admin', 'manager', 'viewer')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_tenant_id ON users(tenant_id);

-- Buildings table
CREATE TABLE IF NOT EXISTS buildings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    area_sqft INTEGER CHECK (area_sqft > 0),
    building_type VARCHAR(50),
    timezone VARCHAR(50) DEFAULT 'UTC',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_buildings_tenant_id ON buildings(tenant_id);

-- Sensors table
CREATE TABLE IF NOT EXISTS sensors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    building_id UUID REFERENCES buildings(id) ON DELETE CASCADE,
    sensor_type VARCHAR(50) NOT NULL,
    name VARCHAR(255),
    location VARCHAR(255),
    unit VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance', 'error')),
    last_reading_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_sensors_building_id ON sensors(building_id);
CREATE INDEX idx_sensors_status ON sensors(status);

-- Energy readings (TimescaleDB hypertable)
CREATE TABLE IF NOT EXISTS energy_readings (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    sensor_id UUID REFERENCES sensors(id) ON DELETE CASCADE,
    building_id UUID REFERENCES buildings(id) ON DELETE CASCADE,
    value DOUBLE PRECISION NOT NULL,
    quality_flag INTEGER DEFAULT 0 CHECK (quality_flag IN (0, 1, 2, 3)),
    metadata JSONB DEFAULT '{}'
);

-- Convert to hypertable
SELECT create_hypertable('energy_readings', 'time', if_not_exists => TRUE);

-- Create indexes for performance
CREATE INDEX idx_energy_readings_building_time ON energy_readings (building_id, time DESC);
CREATE INDEX idx_energy_readings_sensor_time ON energy_readings (sensor_id, time DESC);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    building_id UUID REFERENCES buildings(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('anomaly', 'threshold', 'system', 'maintenance')),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    message TEXT,
    threshold_value DOUBLE PRECISION,
    actual_value DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by UUID REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_alerts_building_id ON alerts(building_id);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);

-- Create continuous aggregates for performance
CREATE MATERIALIZED VIEW IF NOT EXISTS energy_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS hour,
    building_id,
    sensor_id,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    COUNT(*) as reading_count
FROM energy_readings
GROUP BY hour, building_id, sensor_id
WITH NO DATA;

-- Create continuous aggregate for daily summaries
CREATE MATERIALIZED VIEW IF NOT EXISTS energy_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS day,
    building_id,
    sensor_id,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    SUM(value) as total_value,
    COUNT(*) as reading_count
FROM energy_readings
GROUP BY day, building_id, sensor_id
WITH NO DATA;

-- Add refresh policies
SELECT add_continuous_aggregate_policy('energy_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE);

SELECT add_continuous_aggregate_policy('energy_daily',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day',
    if_not_exists => TRUE);

-- Add compression policy for old data
SELECT add_compression_policy('energy_readings', INTERVAL '7 days', if_not_exists => TRUE);

-- Add data retention policy (2 years)
SELECT add_retention_policy('energy_readings', INTERVAL '730 days', if_not_exists => TRUE);

-- Create update trigger for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_buildings_updated_at BEFORE UPDATE ON buildings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sensors_updated_at BEFORE UPDATE ON sensors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample tenant and user for testing
INSERT INTO tenants (company_name, subscription_plan, billing_email)
VALUES ('Demo Company', 'trial', 'demo@energize.io')
ON CONFLICT DO NOTHING;

-- Password is 'demo123' (hashed with bcrypt)
INSERT INTO users (tenant_id, email, hashed_password, full_name, role)
SELECT 
    id,
    'demo@energize.io',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY.MLeNJJAA1Sw6',
    'Demo User',
    'admin'
FROM tenants 
WHERE company_name = 'Demo Company'
ON CONFLICT (email) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA energize TO energize;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA energize TO energize;
GRANT USAGE ON SCHEMA energize TO energize;