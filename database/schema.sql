-- Enable UUID extension (Senior standard for distributed systems)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. ENUMS (Ensures data integrity at the database level)
CREATE TYPE message_source AS ENUM ('whatsapp', 'booking_com', 'airbnb', 'instagram', 'direct');

CREATE TYPE query_category AS ENUM (
    'pre_sales_availability', 
    'pre_sales_pricing', 
    'post_sales_checkin', 
    'special_request', 
    'complaint', 
    'general_enquiry'
);

CREATE TYPE message_status AS ENUM (
    'ai_drafted', 
    'agent_edited', 
    'auto_sent', 
    'escalated'
);

CREATE TYPE message_direction AS ENUM ('inbound', 'outbound');

-- 2. GUEST PROFILES
-- Identifies a unique human across all messaging channels.
CREATE TABLE guests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone_number TEXT UNIQUE,
    -- identity resolution: stores {"whatsapp": "+91...", "airbnb": "user_id_123"}
    external_identities JSONB DEFAULT '{}', 
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. PROPERTIES
CREATE TABLE properties (
    id TEXT PRIMARY KEY, -- e.g., 'villa-b1'
    name TEXT NOT NULL,
    location TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. RESERVATIONS
-- Links a Guest to a specific stay at a Property.
CREATE TABLE reservations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_ref TEXT UNIQUE NOT NULL, -- e.g., 'NIS-2024-0891'
    guest_id UUID REFERENCES guests(id) ON DELETE CASCADE,
    property_id TEXT REFERENCES properties(id),
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. CONVERSATIONS
-- A thread of messages. Can be linked to a specific reservation if one exists.
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    guest_id UUID REFERENCES guests(id) NOT NULL,
    reservation_id UUID REFERENCES reservations(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_message_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. UNIFIED MESSAGES TABLE
-- Stores every inbound query and outbound AI/Agent response.
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    direction message_direction NOT NULL,
    source message_source NOT NULL,
    content TEXT NOT NULL,
    
    -- AI Metadata (The "Brain" of the message)
    query_type query_category,
    ai_confidence_score DECIMAL(3, 2), -- Stores 0.00 to 1.00
    
    -- Status Tracking
    status message_status,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- raw_metadata stores the original webhook JSON for debugging
    raw_metadata JSONB
);

-- INDEXES (Optimizing for common search patterns)
CREATE INDEX idx_guest_phone ON guests(phone_number);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_reservations_ref ON reservations(booking_ref);
CREATE INDEX idx_guests_identities ON guests USING GIN (external_identities);