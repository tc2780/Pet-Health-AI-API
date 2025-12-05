-- Database initialization script for Pet Health API
-- This script creates the database schema and initial data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create pets table
CREATE TABLE IF NOT EXISTS pets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    species VARCHAR(50) NOT NULL,
    breed VARCHAR(100),
    age_years INTEGER,
    weight_kg DECIMAL(5,2),
    sex VARCHAR(20),
    neutered BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create symptoms table
CREATE TABLE IF NOT EXISTS symptoms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pet_id UUID REFERENCES pets(id) ON DELETE CASCADE,
    symptom_name VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT,
    observed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_hours INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create symptom assessments table
CREATE TABLE IF NOT EXISTS symptom_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pet_id UUID REFERENCES pets(id) ON DELETE CASCADE,
    symptoms_json JSONB NOT NULL,
    ai_analysis TEXT,
    urgency_level VARCHAR(20) NOT NULL,
    recommendations TEXT,
    possible_causes JSONB,
    ai_provider VARCHAR(50),
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_pets_user_id ON pets(user_id);
CREATE INDEX IF NOT EXISTS idx_symptoms_pet_id ON symptoms(pet_id);
CREATE INDEX IF NOT EXISTS idx_symptoms_observed_at ON symptoms(observed_at);
CREATE INDEX IF NOT EXISTS idx_symptom_assessments_pet_id ON symptom_assessments(pet_id);
CREATE INDEX IF NOT EXISTS idx_symptom_assessments_created_at ON symptom_assessments(created_at);

-- Create trigger function for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updating timestamps
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_pets_updated_at ON pets;
CREATE TRIGGER update_pets_updated_at
    BEFORE UPDATE ON pets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for development (optional)
-- Uncomment for development environment

/*
-- Sample user
INSERT INTO users (email, password_hash, is_verified) 
VALUES ('demo@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewNQ4gDQ21oGjfAq', true)
ON CONFLICT (email) DO NOTHING;

-- Sample pet (assuming user exists)
INSERT INTO pets (user_id, name, species, breed, age_years, weight_kg, sex, neutered)
SELECT id, 'Buddy', 'dog', 'Golden Retriever', 3, 30.5, 'male', true
FROM users WHERE email = 'demo@example.com'
ON CONFLICT DO NOTHING;
*/