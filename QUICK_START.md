# SmartSwapML - Quick Setup Guide

## 🚀 Get Started in 3 Steps

### Step 1: Extract Files
```bash
unzip smartswapml-complete.zip
cd smartswapml-complete
```

### Step 2: Start Application (Linux/macOS)
```bash
./start.sh
```

### Step 2: Start Application (Windows)
```cmd
docker-compose up --build -d
```

### Step 3: Access Your Application
- 🌐 Frontend: http://localhost:3000
- 📡 Backend API: http://localhost:8000/docs
- 🗄️ Database UI: http://localhost:8081

**Login Credentials:**
- Username: demo
- Password: demo123

## 📁 Project Structure
```
smartswapml-complete/
├── 📄 README.md              # Comprehensive documentation
├── 🐳 docker-compose.yml     # Docker services configuration
├── 🚀 start.sh              # Quick start script
├── 🛑 stop.sh               # Stop script
├── 🐍 main.py               # FastAPI backend
├── 📦 requirements.txt       # Python dependencies
├── 🐳 Dockerfile            # Backend container
├── ⚙️ .env                  # Environment configuration
├── 🗄️ mongo-init.js         # Database initialization
├── 🌐 nginx.conf            # Web server configuration
└── 📂 frontend/             # Web application
    ├── 🏠 index.html        # Main dashboard
    ├── 🎨 css/style.css     # Styles
    ├── ⚙️ js/dashboard.js   # App logic
    ├── 🔌 js/api.js         # Backend integration
    ├── 📱 manifest.json     # PWA configuration
    └── 👷 sw.js             # Service worker
```

## 💡 Need Help?
Read the complete README.md for detailed instructions and troubleshooting.
