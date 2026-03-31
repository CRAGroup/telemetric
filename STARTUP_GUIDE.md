# Telemetric System - Startup Guide

## Prerequisites

### Required Software
- ✅ Python 3.12+ (Installed: 3.12.6)
- ✅ Node.js 18+ (Installed: v20.20.0)
- ❌ PostgreSQL 14+ (Not running on port 5433)
- ❌ Redis 6+ (Not running on port 6379)
- ⚠️ MQTT Broker (Optional - Mosquitto recommended)

## Quick Start Options

### Option 1: Run with Docker (Recommended)

If you have Docker installed, this is the easiest way:

```bash
# Start all services (PostgreSQL, Redis, MQTT)
docker-compose up -d

# Install Python dependencies
cd api
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start backend
uvicorn telemetric_system.app.main:app --reload --host 0.0.0.0 --port 8000

# In a new terminal, start frontend
npm run dev
```

### Option 2: Manual Setup (Windows)

#### Step 1: Install PostgreSQL
1. Download from: https://www.postgresql.org/download/windows/
2. Install and set password
3. Create database:
```bash
psql -U postgres
CREATE DATABASE telemetric_db;
CREATE USER telemetric_user WITH PASSWORD 'mysecretpass';
GRANT ALL PRIVILEGES ON DATABASE telemetric_db TO telemetric_user;
\q
```

#### Step 2: Install Redis
1. Download from: https://github.com/microsoftarchive/redis/releases
2. Or use WSL: `wsl --install` then `sudo apt install redis-server`
3. Start Redis: `redis-server`

#### Step 3: Install MQTT Broker (Optional)
```bash
# Using Chocolatey
choco install mosquitto

# Or download from: https://mosquitto.org/download/
```

#### Step 4: Setup Backend
```bash
# Navigate to api directory
cd api

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Update .env file with correct database connection
# DATABASE_URL=postgresql://telemetric_user:mysecretpass@localhost:5432/telemetric_db

# Run migrations
cd telemetric_system
alembic upgrade head
cd ..

# Start the backend server
uvicorn telemetric_system.app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 5: Setup Frontend
```bash
# In a new terminal, from project root
npm install  # Already done

# Start development server
npm run dev
```

### Option 3: Use Supabase (Current Setup)

Your project is already configured with Supabase! You can run just the frontend:

```bash
# Start frontend only
npm run dev
```

The frontend will connect to Supabase for:
- Database (PostgreSQL)
- Authentication
- Real-time subscriptions
- Storage

## Environment Configuration

### Backend (.env in api/ folder)
```env
DATABASE_URL=postgresql://telemetric_user:mysecretpass@localhost:5432/telemetric_db
REDIS_URL=redis://localhost:6379/0
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
JWT_SECRET=your-secret-key-here
```

### Frontend (.env in root folder)
Already configured with Supabase credentials ✅

## Testing the Setup

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
```

### 2. Check API Documentation
Open browser: http://localhost:8000/docs

### 3. Check Frontend
Open browser: http://localhost:5173

### 4. Test WebSocket Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws?token=YOUR_JWT_TOKEN');
ws.onopen = () => console.log('Connected!');
```

## Common Issues

### PostgreSQL Connection Failed
- Check if PostgreSQL is running: `pg_isready`
- Verify port in .env matches PostgreSQL port (default: 5432)
- Check credentials in DATABASE_URL

### Redis Connection Failed
- Start Redis: `redis-server`
- Or on Windows: `redis-server.exe`
- Check if running: `redis-cli ping` (should return PONG)

### Port Already in Use
- Backend (8000): Change in uvicorn command `--port 8001`
- Frontend (5173): Change in vite.config.ts

### Python Dependencies Installation Failed
- Upgrade pip: `python -m pip install --upgrade pip`
- Install build tools: `pip install wheel setuptools`
- For psycopg2 issues on Windows, use: `pip install psycopg2-binary`

## Development Workflow

### Backend Development
```bash
cd api
.\venv\Scripts\activate
uvicorn telemetric_system.app.main:app --reload --port 8000
```

### Frontend Development
```bash
npm run dev
```

### Database Migrations
```bash
cd api/telemetric_system
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Running Tests
```bash
# Backend tests
cd api
pytest

# Frontend tests (if configured)
npm test
```

## Next Steps

1. **Create Admin User**: Use the auth endpoints to register
2. **Add Test Vehicles**: Use the vehicles API or frontend
3. **Configure MQTT**: For real-time telemetry from devices
4. **Setup Raspberry Pi**: Use scripts in `api/raspberry/`

## Architecture Overview

```
┌─────────────────┐
│   Frontend      │ (React + Vite)
│   Port: 5173    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Backend API   │ (FastAPI)
│   Port: 8000    │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ↓         ↓          ↓          ↓
┌────────┐ ┌──────┐ ┌────────┐ ┌──────┐
│Postgres│ │Redis │ │  MQTT  │ │ IoT  │
│  5432  │ │ 6379 │ │  1883  │ │Device│
└────────┘ └──────┘ └────────┘ └──────┘
```

## Support

For issues or questions:
1. Check logs in `api/logs/app.log`
2. Enable DEBUG mode in .env
3. Check browser console for frontend errors
4. Review API docs at http://localhost:8000/docs
