# 🚀 How to Run the Telemetric System

## ⚡ Super Quick Start (3 Steps)

### 1️⃣ Double-click `RUN_PROJECT.bat`
This opens an interactive menu where you can:
- Check system requirements
- Start services
- Launch backend and frontend
- View logs and documentation

### 2️⃣ Or use individual scripts:

**Option A: With Docker (Recommended)**
```bash
# Terminal 1: Start services
start-services.bat

# Terminal 2: Start backend
start-backend.bat

# Terminal 3: Start frontend
start-frontend.bat
```

**Option B: Frontend Only (Using Supabase)**
```bash
# Just start the frontend
start-frontend.bat
```
Your frontend is already configured with Supabase, so it will work immediately!

### 3️⃣ Access the application:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📋 What You Need

### ✅ Already Installed
- Python 3.12.6 ✓
- Node.js v20.20.0 ✓
- npm ✓
- Frontend dependencies ✓

### ⚠️ Need to Install (for full backend)
- Docker Desktop (recommended) - [Download](https://www.docker.com/products/docker-desktop)
- OR manually install:
  - PostgreSQL 14+
  - Redis 6+
  - MQTT Broker (optional)

## 🎯 Recommended Approach

Since your frontend is already configured with Supabase, the easiest way is:

### Just Run the Frontend:
```bash
npm run dev
```

Then open http://localhost:5173 and you're ready to go! 🎉

The frontend will use Supabase for:
- ✅ Database (PostgreSQL)
- ✅ Authentication
- ✅ Real-time updates
- ✅ File storage

## 🔧 If You Want to Run the Full Backend

### Step 1: Install Docker Desktop
Download from: https://www.docker.com/products/docker-desktop

### Step 2: Start Everything
```bash
# Option 1: Use the launcher
RUN_PROJECT.bat

# Option 2: Manual commands
start-services.bat    # Start PostgreSQL, Redis, MQTT
start-backend.bat     # Start FastAPI backend
start-frontend.bat    # Start React frontend
```

### Step 3: Initialize Database
```bash
cd api
.\venv\Scripts\activate
cd telemetric_system
alembic upgrade head
```

## 🐛 Troubleshooting

### "Port already in use"
- Backend (8000): Another app is using this port
- Frontend (5173): Another Vite server is running
- Solution: Close other apps or change ports

### "Docker not found"
- Install Docker Desktop
- Or just run frontend only (it uses Supabase)

### "Module not found" errors
```bash
# Backend
cd api
.\venv\Scripts\activate
pip install -r requirements.txt

# Frontend
npm install
```

## 📚 Documentation

- **Quick Start**: [QUICK_START.md](QUICK_START.md)
- **Full Setup Guide**: [STARTUP_GUIDE.md](STARTUP_GUIDE.md)
- **API Documentation**: http://localhost:8000/docs (when backend is running)

## 🎮 Test the System

### Create a test user:
1. Go to http://localhost:5173
2. Click "Sign Up"
3. Enter email and password
4. Login and explore!

### Or use the API:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","role":"admin"}'
```

## 💡 Tips

- **First time?** Just run the frontend: `npm run dev`
- **Need full backend?** Use Docker: `start-services.bat`
- **Developing?** Use `RUN_PROJECT.bat` for easy management
- **Stuck?** Check `check-system.bat` to verify setup

## 🆘 Need Help?

1. Run `check-system.bat` to diagnose issues
2. Check logs in `api/logs/app.log`
3. View Docker logs: `docker-compose logs`
4. Enable DEBUG mode in `api/.env`

---

**Ready to start?** Just run:
```bash
npm run dev
```

Or for the full experience:
```bash
RUN_PROJECT.bat
```

Happy tracking! 🚗📍
