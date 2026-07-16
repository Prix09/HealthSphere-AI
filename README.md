# HealthSphere AI

**HealthSphere AI** is a real-time health intelligence and predictive analytics platform engineered for scale. It ingests, analyzes, and visualizes complex biometric telemetry with clinical-grade machine learning.

## Key Features

- **Dynamic Data Ingestion & Analytics:** Automatically parses uploaded datasets (CSV), maps schemas, and generates personalized interactive dashboards.
- **Predictive ML Modeling:** Utilizes dynamic predictive models to assess health risks and forecast future trends based on longitudinal health data.
- **AI-Powered Assessments:** Generates actionable, deterministic, and AI-driven 5-step health insights based on your real-time vitals and environmental metrics.
- **Real-Time Enterprise Alerts:** Monitors metrics continuously and triggers severity-based alerts for critical health events or anomalous data trends.
- **High Performance:** Built with a low-latency Python FastAPI backend and a responsive React frontend, supporting rapid dataset parsing and real-time inference.

## Tech Stack

### Frontend
- **Framework:** React 19 + TypeScript + Vite
- **UI Library:** Material-UI (MUI) v6
- **Data Visualization:** Recharts
- **Routing:** React Router v7

### Backend
- **Framework:** FastAPI (Python)
- **Database:** SQLite with SQLAlchemy ORM
- **AI Integration:** OpenAI API (gpt-4o-mini)
- **Data Processing:** Pandas & Scikit-Learn

### Data Engineering
- **Processing:** Apache Spark (PySpark) ETL Pipelines
- **Streaming:** Kafka (simulated telemetry ingestion)

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python 3.10+
- OpenAI API Key (set as `OPENAI_API_KEY` environment variable)

### Backend Setup
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## Architecture & Security
HealthSphere AI employs military-grade AES-256 encryption methodologies (conceptually), strict role-based access control (RBAC), and ephemeral ML processing environments to ensure complete data privacy and enterprise-level compliance.
