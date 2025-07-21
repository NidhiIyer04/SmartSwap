// MongoDB initialization script
db = db.getSiblingDB('smartswapml');

// Create collections
db.createCollection('batteries');
db.createCollection('stations');
db.createCollection('users');
db.createCollection('routes');

// Create indexes for better performance
db.batteries.createIndex({ "id": 1 }, { unique: true });
db.stations.createIndex({ "id": 1 }, { unique: true });
db.users.createIndex({ "username": 1 }, { unique: true });

print("Database initialized successfully");
