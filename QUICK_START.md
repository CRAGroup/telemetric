# Quick Start - Telemetric System

## 🚀 Fastest Way to Run

### Step 1: Check Your System
```bash
check-system.bat
```
This will verify all prerequisites are installed.

### Step 2: Start Services (Choose One Option)

#### Option A: With Docker (Recommended)
```bash
# Start PostgreSQL, Redis, and MQTT
start-services.bat
```

#### Option B: Without Docker
You'll need to manually install and start:
- PostgreSQL on port 5433
- Redis on port 6379
- MQTT Broker on port 1883 (optional)

### Step 3: Start Backend
```bash
# In one terminal
start-backend.bat
```
This will:
- Create Python virtual environment
- Install dependencies
- Start FastAPI server on http://localhost:8000

### Step 4: Start Frontend
```bash
# In another terminal
start-frontend.bat
```
This will:
- Install npm dependencies (if needed)
- Start Vite dev server on http://localhost:5173

## 🎯 Access Points

Once everything is running:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## 🔐 First Time Setup

### Create Admin User
1. Go to http://localhost:5173
2. Click "Sign Up"
3. Register with your email and password
4. Or use API:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123",
    "full_name": "Admin User",
    "role": "admin"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

## 📊 Test the System

### Add a Test Vehicle
```bash
curl -X POST http://localhost:8000/api/v1/vehicles \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "vehicle_id": "TEST_001",
    "registration_number": "KAA-123X",
    "make": "Toyota",
    "model": "Hilux",
    "year": 2023,
    "status": "active"
  }'
```

### Send Test Telemetry
```bash
curl -X POST http://localhost:8000/api/v1/telemetry \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "vehicle_identifier": "TEST_001",
    "timestamp": 1234567890,
    "vehicle": {
      "lat": -1.2921,
      "lon": 36.8219,
      "speed_kph": 60,
      "heading_deg": 180
    },
    "engine": {
      "rpm": 2500,
      "engine_temp_c": 85,
      "fuel_level_pct": 75
    }
  }'
```

## 🛑 Stop Everything

### Stop Backend
Press `Ctrl+C` in the backend terminal

### Stop Frontend
Press `Ctrl+C` in the frontend terminal

### Stop Services
```bash
docker-compose down
```

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Verify PostgreSQL is running: `docker-compose ps`
- Check logs: `docker-compose logs postgres`

### Frontend won't start
- Check if port 5173 is already in use
- Delete `node_modules` and run `npm install` again

### Database connection error
- Verify DATABASE_URL in `api/.env`
- Check PostgreSQL is running on port 5433
- Test connection: `docker exec -it telemetric_postgres psql -U telemetric_user -d telemetric_db`

### Can't login
- Check JWT_SECRET is set in `api/.env`
- Verify user was created successfully
- Check backend logs for errors

## 📚 More Information

- Full setup guide: [STARTUP_GUIDE.md](STARTUP_GUIDE.md)
- API documentation: http://localhost:8000/docs
- Architecture details: [api/telemetric_system/docs/architecture.md](api/telemetric_system/docs/architecture.md)

## 🎉 You're Ready!

Your telemetric system is now running. You can:
- Add vehicles and drivers
- Monitor real-time telemetry
- Set up geofences
- View analytics and reports
- Configure alerts

Happy tracking! 🚗📍
