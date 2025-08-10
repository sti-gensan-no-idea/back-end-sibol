-- Drop tables to start fresh (optional; comment out if you want to keep existing data)
DROP TABLE IF EXISTS property_analytics CASCADE;
DROP TABLE IF EXISTS agent_performances CASCADE;
DROP TABLE IF EXISTS upcoming_events CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS property_listings CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS chatrooms CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS contracts CASCADE;
DROP TABLE IF EXISTS properties CASCADE;
DROP TABLE IF EXISTS balances CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create tables
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    role TEXT CHECK (role IN ('admin', 'agent', 'tenant')) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS balances (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(15, 2) DEFAULT 0.00,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    price DECIMAL(15, 2) NOT NULL,
    location TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES users(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    status TEXT CHECK (status IN ('pending', 'active', 'expired')) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    amount DECIMAL(15, 2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    status TEXT CHECK (status IN ('pending', 'completed', 'failed')) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chatrooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chatroom_id UUID REFERENCES chatrooms(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    read BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    property_id UUID REFERENCES properties(id) ON DELETE SET NULL,
    amount DECIMAL(15, 2) NOT NULL,
    type TEXT CHECK (type IN ('deposit', 'withdrawal', 'payment')) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS property_listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    status TEXT CHECK (status IN ('available', 'pending', 'sold')) DEFAULT 'available',
    views INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES properties(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type TEXT CHECK (event_type IN ('viewing', 'offer', 'contract_signed')) NOT NULL,
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS upcoming_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID REFERENCES events(id) ON DELETE CASCADE,
    reminder_sent BOOLEAN DEFAULT false,
    reminder_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agent_performances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES users(id) ON DELETE SET NULL,
    deals_closed INTEGER DEFAULT 0,
    total_sales DECIMAL(15, 2) DEFAULT 0.00,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS property_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    total_views INTEGER DEFAULT 0,
    total_offers INTEGER DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Disable RLS for seeding
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE balances DISABLE ROW LEVEL SECURITY;
ALTER TABLE properties DISABLE ROW LEVEL SECURITY;
ALTER TABLE contracts DISABLE ROW LEVEL SECURITY;
ALTER TABLE payments DISABLE ROW LEVEL SECURITY;
ALTER TABLE chatrooms DISABLE ROW LEVEL SECURITY;
ALTER TABLE messages DISABLE ROW LEVEL SECURITY;
ALTER TABLE transactions DISABLE ROW LEVEL SECURITY;
ALTER TABLE property_listings DISABLE ROW LEVEL SECURITY;
ALTER TABLE events DISABLE ROW LEVEL SECURITY;
ALTER TABLE upcoming_events DISABLE ROW LEVEL SECURITY;
ALTER TABLE agent_performances DISABLE ROW LEVEL SECURITY;
ALTER TABLE property_analytics DISABLE ROW LEVEL SECURITY;

-- Insert data (same as provided previously)
INSERT INTO users (id, email, hashed_password, role, is_active) VALUES
    (gen_random_uuid(), 'user1@example.com', 'hashed_password1', 'admin', true),
    (gen_random_uuid(), 'agent1@example.com', 'hashed_password2', 'agent', true),
    (gen_random_uuid(), 'tenant1@example.com', 'hashed_password3', 'tenant', true),
    (gen_random_uuid(), 'user2@example.com', 'hashed_password4', 'admin', true),
    (gen_random_uuid(), 'agent2@example.com', 'hashed_password5', 'agent', true),
    (gen_random_uuid(), 'tenant2@example.com', 'hashed_password6', 'tenant', true),
    (gen_random_uuid(), 'user3@example.com', 'hashed_password7', 'admin', true),
    (gen_random_uuid(), 'agent3@example.com', 'hashed_password8', 'agent', true),
    (gen_random_uuid(), 'tenant3@example.com', 'hashed_password9', 'tenant', true),
    (gen_random_uuid(), 'user4@example.com', 'hashed_password10', 'admin', true);

INSERT INTO balances (user_id, amount) VALUES
    ((SELECT id FROM users WHERE email = 'user1@example.com'), 1000.00),
    ((SELECT id FROM users WHERE email = 'agent1@example.com'), 500.00),
    ((SELECT id FROM users WHERE email = 'tenant1@example.com'), 200.00),
    ((SELECT id FROM users WHERE email = 'user2@example.com'), 1500.00),
    ((SELECT id FROM users WHERE email = 'agent2@example.com'), 700.00),
    ((SELECT id FROM users WHERE email = 'tenant2@example.com'), 300.00),
    ((SELECT id FROM users WHERE email = 'user3@example.com'), 1200.00),
    ((SELECT id FROM users WHERE email = 'agent3@example.com'), 600.00),
    ((SELECT id FROM users WHERE email = 'tenant3@example.com'), 400.00),
    ((SELECT id FROM users WHERE email = 'user4@example.com'), 1800.00);

INSERT INTO properties (id, owner_id, title, description, price, location) VALUES
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'user1@example.com'), 'Apartment 1', 'Cozy apartment', 100000.00, 'Downtown'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'user2@example.com'), 'House 1', 'Spacious house', 200000.00, 'Suburbs'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'user3@example.com'), 'Condo 1', 'Modern condo', 150000.00, 'City Center'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'user4@example.com'), 'Apartment 2', 'Luxury apartment', 120000.00, 'Downtown'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'user1@example.com'), 'House 2', 'Family house', 180000.00, 'Suburbs'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'user2@example.com'), 'Condo 2', 'New condo', 140000.00, 'City Center'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'user3@example.com'), 'Apartment 3', 'Affordable apartment', 90000.00, 'Downtown'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'user4@example.com'), 'House 3', 'Large house', 220000.00, 'Suburbs'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'user1@example.com'), 'Condo 3', 'Premium condo', 160000.00, 'City Center'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'user2@example.com'), 'Apartment 4', 'Modern apartment', 110000.00, 'Downtown');

INSERT INTO contracts (id, property_id, tenant_id, content, status) VALUES
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Apartment 1'), (SELECT id FROM users WHERE email = 'tenant1@example.com'), 'Lease agreement', 'active'),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'House 1'), (SELECT id FROM users WHERE email = 'tenant2@example.com'), 'Lease agreement', 'pending'),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Condo 1'), (SELECT id FROM users WHERE email = 'tenant3@example.com'), 'Lease agreement', 'active'),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Apartment 2'), (SELECT id FROM users WHERE email = 'tenant1@example.com'), 'Lease agreement', 'pending'),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'House 2'), (SELECT id FROM users WHERE email = 'tenant2@example.com'), 'Lease agreement', 'active'),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Condo 2'), (SELECT id FROM users WHERE email = 'tenant3@example.com'), 'Lease agreement', 'pending'),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Apartment 3'), (SELECT id FROM users WHERE email = 'tenant1@example.com'), 'Lease agreement', 'active'),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'House 3'), (SELECT id FROM users WHERE email = 'tenant2@example.com'), 'Lease agreement', 'pending'),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Condo 3'), (SELECT id FROM users WHERE email = 'tenant3@example.com'), 'Lease agreement', 'active'),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Apartment 4'), (SELECT id FROM users WHERE email = 'tenant1@example.com'), 'Lease agreement', 'pending');

INSERT INTO payments (id, user_id, amount, currency, status) VALUES
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant1@example.com'), 1000.00, 'USD', 'completed'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant2@example.com'), 1500.00, 'USD', 'pending'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant3@example.com'), 1200.00, 'USD', 'completed'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant1@example.com'), 800.00, 'USD', 'pending'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant2@example.com'), 2000.00, 'USD', 'completed'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant3@example.com'), 900.00, 'USD', 'pending'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant1@example.com'), 1100.00, 'USD', 'completed'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant2@example.com'), 1300.00, 'USD', 'pending'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant3@example.com'), 1400.00, 'USD', 'completed'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant1@example.com'), 1000.00, 'USD', 'pending');

INSERT INTO transactions (id, user_id, property_id, amount, type) VALUES
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant1@example.com'), (SELECT id FROM properties WHERE title = 'Apartment 1'), 1000.00, 'payment'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant2@example.com'), (SELECT id FROM properties WHERE title = 'House 1'), 1500.00, 'deposit'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant3@example.com'), (SELECT id FROM properties WHERE title = 'Condo 1'), 1200.00, 'payment'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant1@example.com'), (SELECT id FROM properties WHERE title = 'Apartment 2'), 800.00, 'deposit'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant2@example.com'), (SELECT id FROM properties WHERE title = 'House 2'), 2000.00, 'payment'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant3@example.com'), (SELECT id FROM properties WHERE title = 'Condo 2'), 900.00, 'deposit'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant1@example.com'), (SELECT id FROM properties WHERE title = 'Apartment 3'), 1100.00, 'payment'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant2@example.com'), (SELECT id FROM properties WHERE title = 'House 3'), 1300.00, 'deposit'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant3@example.com'), (SELECT id FROM properties WHERE title = 'Condo 3'), 1400.00, 'payment'),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'tenant1@example.com'), (SELECT id FROM properties WHERE title = 'Apartment 4'), 1000.00, 'deposit');

INSERT INTO property_listings (id, property_id, status, views) VALUES
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Apartment 1'), 'available', 100),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'House 1'), 'pending', 150),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Condo 1'), 'sold', 120),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Apartment 2'), 'available', 80),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'House 2'), 'pending', 200),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Condo 2'), 'sold', 90),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Apartment 3'), 'available', 110),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'House 3'), 'pending', 130),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Condo 3'), 'sold', 140),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Apartment 4'), 'available', 100);

INSERT INTO chatrooms (id, name, created_at) VALUES
    (gen_random_uuid(), 'Apartment 1 Discussion', CURRENT_TIMESTAMP),
    (gen_random_uuid(), 'House 1 Discussion', CURRENT_TIMESTAMP),
    (gen_random_uuid(), 'Condo 1 Discussion', CURRENT_TIMESTAMP),
    (gen_random_uuid(), 'Apartment 2 Discussion', CURRENT_TIMESTAMP),
    (gen_random_uuid(), 'House 2 Discussion', CURRENT_TIMESTAMP),
    (gen_random_uuid(), 'Condo 2 Discussion', CURRENT_TIMESTAMP),
    (gen_random_uuid(), 'Apartment 3 Discussion', CURRENT_TIMESTAMP),
    (gen_random_uuid(), 'House 3 Discussion', CURRENT_TIMESTAMP),
    (gen_random_uuid(), 'Condo 3 Discussion', CURRENT_TIMESTAMP),
    (gen_random_uuid(), 'Apartment 4 Discussion', CURRENT_TIMESTAMP);

INSERT INTO messages (id, chatroom_id, user_id, content, read) VALUES
    (gen_random_uuid(), (SELECT id FROM chatrooms WHERE name = 'Apartment 1 Discussion'), (SELECT id FROM users WHERE email = 'tenant1@example.com'), 'Interested in viewing', false),
    (gen_random_uuid(), (SELECT id FROM chatrooms WHERE name = 'House 1 Discussion'), (SELECT id FROM users WHERE email = 'tenant2@example.com'), 'When is it available?', false),
    (gen_random_uuid(), (SELECT id FROM chatrooms WHERE name = 'Condo 1 Discussion'), (SELECT id FROM users WHERE email = 'tenant3@example.com'), 'What are the terms?', false),
    (gen_random_uuid(), (SELECT id FROM chatrooms WHERE name = 'Apartment 2 Discussion'), (SELECT id FROM users WHERE email = 'tenant1@example.com'), 'Can I schedule a visit?', false),
    (gen_random_uuid(), (SELECT id FROM chatrooms WHERE name = 'House 2 Discussion'), (SELECT id FROM users WHERE email = 'tenant2@example.com'), 'Is it pet-friendly?', false),
    (gen_random_uuid(), (SELECT id FROM chatrooms WHERE name = 'Condo 2 Discussion'), (SELECT id FROM users WHERE email = 'tenant3@example.com'), 'What’s the price?', false),
    (gen_random_uuid(), (SELECT id FROM chatrooms WHERE name = 'Apartment 3 Discussion'), (SELECT id FROM users WHERE email = 'tenant1@example.com'), 'Any parking available?', false),
    (gen_random_uuid(), (SELECT id FROM chatrooms WHERE name = 'House 3 Discussion'), (SELECT id FROM users WHERE email = 'tenant2@example.com'), 'Can I see photos?', false),
    (gen_random_uuid(), (SELECT id FROM chatrooms WHERE name = 'Condo 3 Discussion'), (SELECT id FROM users WHERE email = 'tenant3@example.com'), 'Is it furnished?', false),
    (gen_random_uuid(), (SELECT id FROM chatrooms WHERE name = 'Apartment 4 Discussion'), (SELECT id FROM users WHERE email = 'tenant1@example.com'), 'What’s the lease term?', false);

INSERT INTO events (id, property_id, user_id, event_type, scheduled_at) VALUES
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Apartment 1'), (SELECT id FROM users WHERE email = 'tenant1@example.com'), 'viewing', CURRENT_TIMESTAMP + INTERVAL '1 day'),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'House 1'), (SELECT id FROM users WHERE email = 'tenant2@example.com'), 'offer', CURRENT_TIMESTAMP + INTERVAL '2 days'),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Condo 1'), (SELECT id FROM users WHERE email = 'tenant3@example.com'), 'contract_signed', CURRENT_TIMESTAMP + INTERVAL '3 days'),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Apartment 2'), (SELECT id FROM users WHERE email = 'tenant1@example.com'), 'viewing', CURRENT_TIMESTAMP + INTERVAL '4 days'),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'House 2'), (SELECT id FROM users WHERE email = 'tenant2@example.com'), 'offer', CURRENT_TIMESTAMP + INTERVAL '5 days'),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Condo 2'), (SELECT id FROM users WHERE email = 'tenant3@example.com'), 'contract_signed', CURRENT_TIMESTAMP + INTERVAL '6 days'),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Apartment 3'), (SELECT id FROM users WHERE email = 'tenant1@example.com'), 'viewing', CURRENT_TIMESTAMP + INTERVAL '7 days'),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'House 3'), (SELECT id FROM users WHERE email = 'tenant2@example.com'), 'offer', CURRENT_TIMESTAMP + INTERVAL '8 days'),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Condo 3'), (SELECT id FROM users WHERE email = 'tenant3@example.com'), 'contract_signed', CURRENT_TIMESTAMP + INTERVAL '9 days'),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Apartment 4'), (SELECT id FROM users WHERE email = 'tenant1@example.com'), 'viewing', CURRENT_TIMESTAMP + INTERVAL '10 days');

INSERT INTO upcoming_events (id, event_id, reminder_sent, reminder_at) VALUES
    (gen_random_uuid(), (SELECT id FROM events WHERE event_type = 'viewing' LIMIT 1), false, CURRENT_TIMESTAMP + INTERVAL '12 hours'),
    (gen_random_uuid(), (SELECT id FROM events WHERE event_type = 'offer' LIMIT 1), false, CURRENT_TIMESTAMP + INTERVAL '1 day'),
    (gen_random_uuid(), (SELECT id FROM events WHERE event_type = 'contract_signed' LIMIT 1), false, CURRENT_TIMESTAMP + INTERVAL '2 days'),
    (gen_random_uuid(), (SELECT id FROM events WHERE event_type = 'viewing' LIMIT 1 OFFSET 1), false, CURRENT_TIMESTAMP + INTERVAL '3 days'),
    (gen_random_uuid(), (SELECT id FROM events WHERE event_type = 'offer' LIMIT 1 OFFSET 1), false, CURRENT_TIMESTAMP + INTERVAL '4 days'),
    (gen_random_uuid(), (SELECT id FROM events WHERE event_type = 'contract_signed' LIMIT 1 OFFSET 1), false, CURRENT_TIMESTAMP + INTERVAL '5 days'),
    (gen_random_uuid(), (SELECT id FROM events WHERE event_type = 'viewing' LIMIT 1 OFFSET 2), false, CURRENT_TIMESTAMP + INTERVAL '6 days'),
    (gen_random_uuid(), (SELECT id FROM events WHERE event_type = 'offer' LIMIT 1 OFFSET 2), false, CURRENT_TIMESTAMP + INTERVAL '7 days'),
    (gen_random_uuid(), (SELECT id FROM events WHERE event_type = 'contract_signed' LIMIT 1 OFFSET 2), false, CURRENT_TIMESTAMP + INTERVAL '8 days'),
    (gen_random_uuid(), (SELECT id FROM events WHERE event_type = 'viewing' LIMIT 1 OFFSET 3), false, CURRENT_TIMESTAMP + INTERVAL '9 days');

INSERT INTO agent_performances (id, agent_id, deals_closed, total_sales) VALUES
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'agent1@example.com'), 5, 500000.00),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'agent2@example.com'), 3, 300000.00),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'agent3@example.com'), 7, 700000.00),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'agent1@example.com'), 2, 200000.00),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'agent2@example.com'), 4, 400000.00),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'agent3@example.com'), 6, 600000.00),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'agent1@example.com'), 1, 100000.00),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'agent2@example.com'), 8, 800000.00),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'agent3@example.com'), 9, 900000.00),
    (gen_random_uuid(), (SELECT id FROM users WHERE email = 'agent1@example.com'), 10, 1000000.00);

INSERT INTO property_analytics (id, property_id, total_views, total_offers) VALUES
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Apartment 1'), 100, 5),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'House 1'), 150, 3),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Condo 1'), 120, 7),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Apartment 2'), 80, 2),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'House 2'), 200, 4),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Condo 2'), 90, 6),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Apartment 3'), 110, 1),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'House 3'), 130, 8),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Condo 3'), 140, 9),
    (gen_random_uuid(), (SELECT id FROM properties WHERE title = 'Apartment 4'), 100, 10);

-- Re-enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE balances ENABLE ROW LEVEL SECURITY;
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE contracts ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE chatrooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE property_listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE upcoming_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_performances ENABLE ROW LEVEL SECURITY;
ALTER TABLE property_analytics ENABLE ROW LEVEL SECURITY;