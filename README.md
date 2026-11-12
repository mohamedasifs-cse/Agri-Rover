# AgriRover — AI Disease Monitoring for Bitter Gourd Pandal Farms

> Real-time AI-powered disease detection and farm monitoring with a farmer-friendly web interface.

## 🏗️ Project Structure

```
d:\Agri_ML\
├── agri-rover/     🖥️  Next.js 15 frontend
└── backend/        🐍  Python FastAPI backend
```

## 🚀 Quick Start

### 1. Start the Python Backend

```powershell
cd d:\Agri_ML\backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000
```

Open API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Start the Next.js Frontend

```powershell
cd d:\Agri_ML\agri-rover
npm run dev
```

Open app: [http://localhost:3000](http://localhost:3000)

---

## 📱 Pages

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/` | Farm health overview, IoT sensors, latest detection |
| Farm Map | `/map` | Interactive hexagonal grid map of pandal |
| Disease Details | `/detection` | Full analysis with AI recommendations |
| AI Assistant | `/assistant` | Chat interface for farmer queries |
| History & Trends | `/history` | Charts, timeline, disease distribution |
| Settings | `/settings` | Farm profile, notifications, CSV export |

---

## 🐍 Python Backend API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/detections` | GET | Latest + historical detections |
| `/api/detections/latest` | GET | Most recent detection |
| `/api/detections/trends` | GET | 14-day trend data for charts |
| `/api/sensors` | GET | Current IoT sensor readings |
| `/api/farm/grid` | GET | Farm cell grid with health status |
| `/api/farm/summary` | GET | Health summary statistics |
| `/api/farm/disease-info/{class}` | GET | Disease info + recommendations |
| `/api/chat` | POST | AI assistant response |
| `/api/chat/suggestions` | GET | Suggested farmer questions |
| `/health` | GET | Backend health check |

---

## 🧬 Disease Classes Supported

| Class | Display Name |
|-------|-------------|
| `healthy` | Healthy |
| `powdery_mildew` | Powdery Mildew |
| `downy_mildew` | Downy Mildew |
| `fungal_leaf_spot` | Fungal Leaf Spot |
| `viral_symptoms` | Viral Disease |
| `pest_damage` | Pest Damage |

---

## 📊 Detection JSON Schema

```json
{
  "timestamp": "2026-09-11T14:30:00Z",
  "rover_location": { "row": 2, "section": "B", "distance_from_start_meters": 18 },
  "detection_result": {
    "disease_class": "powdery_mildew",
    "confidence": 0.94,
    "severity_class": "moderate",
    "affected_area_percentage": 25,
    "symptoms_detected": ["white_coating", "leaf_curling"]
  },
  "environmental_data": {
    "temperature_celsius": 31,
    "humidity_percentage": 78,
    "soil_moisture_percentage": 62,
    "light_intensity_lux": 720
  }
}
```

---

## 🔮 Phase Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Done | MVP — dashboard, map, detection, chat, history, settings |
| Phase 2 | 📋 Planned | PostgreSQL database, real-time WebSocket updates |
| Phase 3 | 📋 Planned | TensorFlow/ONNX ML model, Claude API chat, image upload |
| Phase 4 | 📋 Planned | PDF reports, offline mode, multi-language |
