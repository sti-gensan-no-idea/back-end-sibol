-- Disable RLS for seeding
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE balances DISABLE ROW LEVEL SECURITY;
ALTER TABLE properties DISABLE ROW LEVEL SECURITY;
ALTER TABLE contracts DISABLE ROW LEVEL SECURITY;
ALTER TABLE payments DISABLE ROW LEVEL SECURITY;
ALTER TABLE chatrooms DISABLE ROW LEVEL SECURITY;
ALTER TABLE messages DISABLE ROW LEVEL SECURITY;

-- Clear existing data
TRUNCATE TABLE messages, chatrooms, payments, balances, contracts, properties, users RESTART IDENTITY CASCADE;

-- Insert Users (20: 5 ADMIN, 5 AGENT, 10 CLIENT)
INSERT INTO users (id, email, hashed_password, role, is_active) VALUES
(1, 'admin1@sibol.com', '$2b$12$Q7z9X8Y2z3W4x5Y6z7A8B9C0D1E2F3G4H5I6J7K8L9M0N1O2P3Q4', 'ADMIN', true),
(2, 'admin2@sibol.com', '$2b$12$Q7z9X8Y2z3W4x5Y6z7A8B9C0D1E2F3G4H5I6J7K8L9M0N1O2P3Q4', 'ADMIN', true),
(3, 'admin3@sibol.com', '$2b$12$Q7z9X8Y2z3W4x5Y6z7A8B9C0D1E2F3G4H5I6J7K8L9M0N1O2P3Q4', 'ADMIN', true),
(4, 'admin4@sibol.com', '$2b$12$Q7z9X8Y2z3W4x5Y6z7A8B9C0D1E2F3G4H5I6J7K8L9M0N1O2P3Q4', 'ADMIN', true),
(5, 'admin5@sibol.com', '$2b$12$Q7z9X8Y2z3W4x5Y6z7A8B9C0D1E2F3G4H5I6J7K8L9M0N1O2P3Q4', 'ADMIN', true),
(6, 'agent1@sibol.com', '$2b$12$R8A9B0C1D2E3F4G5H6I7J8K9L0M1N2O3P4Q5R6S7T8U9V0W1X2Y3', 'AGENT', true),
(7, 'agent2@sibol.com', '$2b$12$R8A9B0C1D2E3F4G5H6I7J8K9L0M1N2O3P4Q5R6S7T8U9V0W1X2Y3', 'AGENT', true),
(8, 'agent3@sibol.com', '$2b$12$R8A9B0C1D2E3F4G5H6I7J8K9L0M1N2O3P4Q5R6S7T8U9V0W1X2Y3', 'AGENT', true),
(9, 'agent4@sibol.com', '$2b$12$R8A9B0C1D2E3F4G5H6I7J8K9L0M1N2O3P4Q5R6S7T8U9V0W1X2Y3', 'AGENT', true),
(10, 'agent5@sibol.com', '$2b$12$R8A9B0C1D2E3F4G5H6I7J8K9L0M1N2O3P4Q5R6S7T8U9V0W1X2Y3', 'AGENT', true),
(11, 'client1@sibol.com', '$2b$12$S9T0U1V2W3X4Y5Z6A7B8C9D0E1F2G3H4I5J6K7L8M9N0O1P2Q3R4', 'CLIENT', true),
(12, 'client2@sibol.com', '$2b$12$S9T0U1V2W3X4Y5Z6A7B8C9D0E1F2G3H4I5J6K7L8M9N0O1P2Q3R4', 'CLIENT', true),
(13, 'client3@sibol.com', '$2b$12$S9T0U1V2W3X4Y5Z6A7B8C9D0E1F2G3H4I5J6K7L8M9N0O1P2Q3R4', 'CLIENT', true),
(14, 'client4@sibol.com', '$2b$12$S9T0U1V2W3X4Y5Z6A7B8C9D0E1F2G3H4I5J6K7L8M9N0O1P2Q3R4', 'CLIENT', true),
(15, 'client5@sibol.com', '$2b$12$S9T0U1V2W3X4Y5Z6A7B8C9D0E1F2G3H4I5J6K7L8M9N0O1P2Q3R4', 'CLIENT', true),
(16, 'client6@sibol.com', '$2b$12$S9T0U1V2W3X4Y5Z6A7B8C9D0E1F2G3H4I5J6K7L8M9N0O1P2Q3R4', 'CLIENT', true),
(17, 'client7@sibol.com', '$2b$12$S9T0U1V2W3X4Y5Z6A7B8C9D0E1F2G3H4I5J6K7L8M9N0O1P2Q3R4', 'CLIENT', true),
(18, 'client8@sibol.com', '$2b$12$S9T0U1V2W3X4Y5Z6A7B8C9D0E1F2G3H4I5J6K7L8M9N0O1P2Q3R4', 'CLIENT', true),
(19, 'client9@sibol.com', '$2b$12$S9T0U1V2W3X4Y5Z6A7B8C9D0E1F2G3H4I5J6K7L8M9N0O1P2Q3R4', 'CLIENT', true),
(20, 'client10@sibol.com', '$2b$12$S9T0U1V2W3X4Y5Z6A7B8C9D0E1F2G3H4I5J6K7L8M9N0O1P2Q3R4', 'CLIENT', true);

-- Insert Balances (20: one per user)
INSERT INTO balances (user_id, amount) VALUES
(1, 10000.00), (2, 8000.00), (3, 6000.00), (4, 4000.00), (5, 2000.00),
(6, 1500.00), (7, 1200.00), (8, 1000.00), (9, 800.00), (10, 500.00),
(11, 0.00), (12, 0.00), (13, 0.00), (14, 0.00), (15, 0.00),
(16, 0.00), (17, 0.00), (18, 0.00), (19, 0.00), (20, 0.00);

-- Insert Properties (20: owned by ADMIN or AGENT)
INSERT INTO properties (id, owner_id, title, description, address, price, ar_model_url) VALUES
(1, 1, 'Villa 1', 'Luxurious beachfront villa', '101 Coastal Rd, Manila', 2500000.00, 'https://storage.example.com/ar-models/villa1.glb'),
(2, 1, 'Villa 2', 'Spacious villa with pool', '102 Coastal Rd, Manila', 2700000.00, 'https://storage.example.com/ar-models/villa2.glb'),
(3, 2, 'Apartment 1', 'Modern downtown apartment', '201 Urban St, Quezon City', 1500000.00, 'https://storage.example.com/ar-models/apt1.glb'),
(4, 2, 'Apartment 2', 'Cozy city apartment', '202 Urban St, Quezon City', 1400000.00, 'https://storage.example.com/ar-models/apt2.glb'),
(5, 3, 'House 1', 'Family house with garden', '301 Suburb Ln, Makati', 1800000.00, 'https://storage.example.com/ar-models/house1.glb'),
(6, 3, 'House 2', 'Modern suburban house', '302 Suburb Ln, Makati', 1900000.00, 'https://storage.example.com/ar-models/house2.glb'),
(7, 4, 'Condo 1', 'High-rise condo with view', '401 Sky Rd, Taguig', 2000000.00, 'https://storage.example.com/ar-models/condo1.glb'),
(8, 4, 'Condo 2', 'Luxury condo in BGC', '402 Sky Rd, Taguig', 2100000.00, 'https://storage.example.com/ar-models/condo2.glb'),
(9, 5, 'Townhouse 1', 'Modern townhouse', '501 Town St, Pasig', 1600000.00, 'https://storage.example.com/ar-models/townhouse1.glb'),
(10, 5, 'Townhouse 2', 'Spacious townhouse', '502 Town St, Pasig', 1700000.00, 'https://storage.example.com/ar-models/townhouse2.glb'),
(11, 6, 'Villa 3', 'Beachfront villa with terrace', '103 Coastal Rd, Manila', 2600000.00, 'https://storage.example.com/ar-models/villa3.glb'),
(12, 6, 'Apartment 3', 'Downtown studio apartment', '203 Urban St, Quezon City', 1300000.00, 'https://storage.example.com/ar-models/apt3.glb'),
(13, 7, 'House 3', 'Suburban family house', '303 Suburb Ln, Makati', 1850000.00, 'https://storage.example.com/ar-models/house3.glb'),
(14, 7, 'Condo 3', 'City-view condo', '403 Sky Rd, Taguig', 2050000.00, 'https://storage.example.com/ar-models/condo3.glb'),
(15, 8, 'Townhouse 3', 'Cozy townhouse', '503 Town St, Pasig', 1650000.00, 'https://storage.example.com/ar-models/townhouse3.glb'),
(16, 8, 'Villa 4', 'Luxury beach villa', '104 Coastal Rd, Manila', 2800000.00, 'https://storage.example.com/ar-models/villa4.glb'),
(17, 9, 'Apartment 4', 'Modern city apartment', '204 Urban St, Quezon City', 1350000.00, 'https://storage.example.com/ar-models/apt4.glb'),
(18, 9, 'House 4', 'Spacious suburban house', '304 Suburb Ln, Makati', 1950000.00, 'https://storage.example.com/ar-models/house4.glb'),
(19, 10, 'Condo 4', 'High-rise luxury condo', '404 Sky Rd, Taguig', 2150000.00, 'https://storage.example.com/ar-models/condo4.glb'),
(20, 10, 'Townhouse 4', 'Modern townhouse with garage', '504 Town St, Pasig', 1750000.00, 'https://storage.example.com/ar-models/townhouse4.glb');

-- Insert Contracts (20: linking properties to CLIENT users)
INSERT INTO contracts (id, property_id, tenant_id, content) VALUES
(1, 1, 11, 'Lease agreement for Villa 1, 1 year'),
(2, 2, 12, 'Lease agreement for Villa 2, 1 year'),
(3, 3, 13, 'Lease agreement for Apartment 1, 6 months'),
(4, 4, 14, 'Lease agreement for Apartment 2, 6 months'),
(5, 5, 15, 'Lease agreement for House 1, 1 year'),
(6, 6, 16, 'Lease agreement for House 2, 1 year'),
(7, 7, 17, 'Lease agreement for Condo 1, 1 year'),
(8, 8, 18, 'Lease agreement for Condo 2, 1 year'),
(9, 9, 19, 'Lease agreement for Townhouse 1, 6 months'),
(10, 10, 20, 'Lease agreement for Townhouse 2, 6 months'),
(11, 11, 11, 'Lease agreement for Villa 3, 1 year'),
(12, 12, 12, 'Lease agreement for Apartment 3, 6 months'),
(13, 13, 13, 'Lease agreement for House 3, 1 year'),
(14, 14, 14, 'Lease agreement for Condo 3, 1 year'),
(15, 15, 15, 'Lease agreement for Townhouse 3, 6 months'),
(16, 16, 16, 'Lease agreement for Villa 4, 1 year'),
(17, 17, 17, 'Lease agreement for Apartment 4, 6 months'),
(18, 18, 18, 'Lease agreement for House 4, 1 year'),
(19, 19, 19, 'Lease agreement for Condo 4, 1 year'),
(20, 20, 20, 'Lease agreement for Townhouse 4, 6 months');

-- Insert Payments (20: made by CLIENT users)
INSERT INTO payments (id, user_id, amount, status, transaction_id, description, created_at) VALUES
(1, 11, 50000.00, 'PENDING', 'payfusion-txn-001', 'Initial payment for Villa 1', '2025-07-28 15:00:00+00'),
(2, 12, 52000.00, 'PENDING', 'payfusion-txn-002', 'Initial payment for Villa 2', '2025-07-28 15:01:00+00'),
(3, 13, 30000.00, 'PENDING', 'payfusion-txn-003', 'Deposit for Apartment 1', '2025-07-28 15:02:00+00'),
(4, 14, 28000.00, 'PENDING', 'payfusion-txn-004', 'Deposit for Apartment 2', '2025-07-28 15:03:00+00'),
(5, 15, 35000.00, 'PENDING', 'payfusion-txn-005', 'Initial payment for House 1', '2025-07-28 15:04:00+00'),
(6, 16, 36000.00, 'PENDING', 'payfusion-txn-006', 'Initial payment for House 2', '2025-07-28 15:05:00+00'),
(7, 17, 40000.00, 'PENDING', 'payfusion-txn-007', 'Initial payment for Condo 1', '2025-07-28 15:06:00+00'),
(8, 18, 42000.00, 'PENDING', 'payfusion-txn-008', 'Initial payment for Condo 2', '2025-07-28 15:07:00+00'),
(9, 19, 32000.00, 'PENDING', 'payfusion-txn-009', 'Deposit for Townhouse 1', '2025-07-28 15:08:00+00'),
(10, 20, 34000.00, 'PENDING', 'payfusion-txn-010', 'Deposit for Townhouse 2', '2025-07-28 15:09:00+00'),
(11, 11, 51000.00, 'PENDING', 'payfusion-txn-011', 'Initial payment for Villa 3', '2025-07-28 15:10:00+00'),
(12, 12, 29000.00, 'PENDING', 'payfusion-txn-012', 'Deposit for Apartment 3', '2025-07-28 15:11:00+00'),
(13, 13, 37000.00, 'PENDING', 'payfusion-txn-013', 'Initial payment for House 3', '2025-07-28 15:12:00+00'),
(14, 14, 41000.00, 'PENDING', 'payfusion-txn-014', 'Initial payment for Condo 3', '2025-07-28 15:13:00+00'),
(15, 15, 33000.00, 'PENDING', 'payfusion-txn-015', 'Deposit for Townhouse 3', '2025-07-28 15:14:00+00'),
(16, 16, 53000.00, 'PENDING', 'payfusion-txn-016', 'Initial payment for Villa 4', '2025-07-28 15:15:00+00'),
(17, 17, 31000.00, 'PENDING', 'payfusion-txn-017', 'Deposit for Apartment 4', '2025-07-28 15:16:00+00'),
(18, 18, 38000.00, 'PENDING', 'payfusion-txn-018', 'Initial payment for House 4', '2025-07-28 15:17:00+00'),
(19, 19, 43000.00, 'PENDING', 'payfusion-txn-019', 'Initial payment for Condo 4', '2025-07-28 15:18:00+00'),
(20, 20, 35000.00, 'PENDING', 'payfusion-txn-020', 'Deposit for Townhouse 4', '2025-07-28 15:19:00+00');

-- Insert Chatrooms (10: for property discussions)
INSERT INTO chatrooms (id, name, created_at) VALUES
(1, 'Villa 1 Discussion', '2025-07-28 15:20:00+00'),
(2, 'Villa 2 Discussion', '2025-07-28 15:21:00+00'),
(3, 'Apartment 1 Inquiry', '2025-07-28 15:22:00+00'),
(4, 'Apartment 2 Inquiry', '2025-07-28 15:23:00+00'),
(5, 'House 1 Discussion', '2025-07-28 15:24:00+00'),
(6, 'House 2 Discussion', '2025-07-28 15:25:00+00'),
(7, 'Condo 1 Inquiry', '2025-07-28 15:26:00+00'),
(8, 'Condo 2 Inquiry', '2025-07-28 15:27:00+00'),
(9, 'Townhouse 1 Discussion', '2025-07-28 15:28:00+00'),
(10, 'Townhouse 2 Discussion', '2025-07-28 15:29:00+00');

-- Insert Messages (10: in chatrooms, sent by users)
INSERT INTO messages (id, chatroom_id, user_id, content, reactions, created_at) VALUES
(1, 1, 11, 'Is Villa 1 available for rent?', '{"👍": [1], "😊": [6]}', '2025-07-28 15:30:00+00'),
(2, 1, 1, 'Yes, Villa 1 is available! Contact for details.', '{"👍": [11]}', '2025-07-28 15:31:00+00'),
(3, 2, 12, 'What’s the monthly rent for Villa 2?', '{}', '2025-07-28 15:32:00+00'),
(4, 3, 13, 'Can I view Apartment 1?', '{"😊": [8]}', '2025-07-28 15:33:00+00'),
(5, 4, 14, 'Is Apartment 2 pet-friendly?', '{}', '2025-07-28 15:34:00+00'),
(6, 5, 15, 'Does House 1 have a garage?', '{"👍": [3]}', '2025-07-28 15:35:00+00'),
(7, 6, 16, 'What’s the lease term for House 2?', '{}', '2025-07-28 15:36:00+00'),
(8, 7, 17, 'Is Condo 1 furnished?', '{"😊": [4]}', '2025-07-28 15:37:00+00'),
(9, 8, 18, 'Can I schedule a tour for Condo 2?', '{}', '2025-07-28 15:38:00+00'),
(10, 9, 19, 'Is Townhouse 1 near schools?', '{"👍": [5]}', '2025-07-28 15:39:00+00');

-- Re-enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE balances ENABLE ROW LEVEL SECURITY;
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE contracts ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE chatrooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
