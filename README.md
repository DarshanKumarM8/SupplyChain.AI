# SupplyChain.AI

SupplyChain.AI is a real-time, interactive simulation dashboard and AI decision-agent designed to help procurement managers navigate global supply chain disruptions. 

When a crisis hits (e.g., a typhoon shutting down a major port), most human buyers panic and rush to the same obvious backup supplier, creating a "stampede" effect that overloads secondary suppliers and crashes the service level. **SupplyChain.AI** intelligently redistributes orders across the network to prevent this cascading failure.

## 🚀 Key Features

- **Real-Time Simulation Engine:** Watch how a "Naive Market" crashes under pressure compared to an "AI-Optimized" market that smoothly redistributes volume.
- **Interactive Panic Sliders:** Adjust market panic (`Beta`) and AI adoption rates live to see how they impact supplier capacity, SLA misses, and carbon footprints.
- **SupplyChainAI Chat Assistant:** A built-in, context-aware AI assistant that can explain the simulation in plain English, justify why certain suppliers are overloaded, and trigger UI updates directly from the chat.
- **Clean, Professional UI:** A responsive, dark-mode React dashboard built for executive-level presentations and decision-making.

## 🛠️ Technology Stack

- **Frontend:** React, Vite, standard CSS (No external UI frameworks — completely custom, responsive styling).
- **Backend:** Python, FastAPI, Uvicorn.
- **AI Integration:** OpenAI API with a highly robust mock-fallback system for API rate-limit resilience.
- **Deployment:** Configured for Vercel (Frontend) and Render (Backend).

## 🧑‍💻 Team & Contributions

This project was built collaboratively:

- **Jason:** UI/UX Architecture, Frontend Dashboard logic, State Management, and Chat Integration.
- **Darshan:** Project Management, GitHub Repository Maintenance, and Core Backend API setup.
- **Mithun:** Data Pipeline Architecture, Fallback Mock Intelligence Design, and Backend-Frontend Integration Testing.

## 🏃‍♂️ How to Run Locally

### 1. Start the Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 run_chat_server.py
```
*(The backend will run on `http://localhost:8000`)*

### 2. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```
*(The frontend will run on `http://localhost:5173`)*

## 🌍 Deployment

- **Backend:** Automatically deployed via Render. 
- **Frontend:** Deployed via Vercel. 
  - *Note:* The production frontend automatically connects to the live backend using the `.env.production` configuration (`VITE_API_URL`).
