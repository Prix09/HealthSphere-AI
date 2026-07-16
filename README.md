# HealthSphere AI

**HealthSphere AI** is a real-time health intelligence and predictive analytics platform engineered for scale. It ingests, analyzes, and visualizes complex biometric telemetry with clinical-grade machine learning.

## Key Features

- **Dynamic Data Ingestion & Analytics:** Automatically parses uploaded datasets (CSV), maps schemas, and generates personalized interactive dashboards.
- **Predictive ML Modeling:** Utilizes dynamic predictive models to assess health risks and forecast future trends based on longitudinal health data.
- **AI-Powered Assessments:** Generates actionable, deterministic, and AI-driven 5-step health insights based on your real-time vitals and environmental metrics.
- **Real-Time Enterprise Alerts:** Monitors metrics continuously and triggers severity-based alerts for critical health events or anomalous data trends.
- **High Performance & Microservices:** Built with a modern microservices architecture utilizing Docker for containerized deployment, ensuring robust scaling and observability.

## Architecture & Microservices

The backend infrastructure of HealthSphere AI is fully containerized using **Docker Compose** to manage several interconnected services. This enterprise-grade setup ensures high availability, real-time data streaming, and deep system observability:

* **FastAPI Backend (`fastapi-backend`)**: The core Python API that handles routing, machine learning inference, AI integrations, and database operations.
* **PostgreSQL (`postgres`)**: The primary relational database used for robust and scalable data storage of user profiles, health records, and system metadata.
* **pgAdmin (`pgadmin`)**: A web-based graphical administration tool for visually managing and querying the PostgreSQL database.
* **Apache Kafka (`kafka`) & Zookeeper (`zookeeper`)**: A distributed event streaming platform used to ingest high-throughput, real-time simulated telemetry and health metrics with minimal latency.
* **Prometheus (`prometheus`)**: A systems monitoring and alerting toolkit used to scrape and store real-time performance metrics from the backend and data pipelines.
* **Grafana (`grafana`)**: A powerful visualization dashboard that connects to Prometheus to provide deep, real-time insights into system health, API latency, and infrastructure performance.

## Tech Stack

### Frontend
- **Framework:** React 19 + TypeScript + Vite
- **UI Library:** Material-UI (MUI) v6
- **Data Visualization:** Recharts
- **Routing:** React Router v7

### Backend & Infrastructure
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Containerization:** Docker & Docker Compose
- **Observability:** Prometheus & Grafana
- **Message Broker:** Apache Kafka & Zookeeper
- **AI Integration:** OpenAI API (gpt-4o-mini)

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python 3.10+
- Docker & Docker Compose
- OpenAI API Key (set as `OPENAI_API_KEY` in environment)

### Infrastructure Setup (Docker)
To spin up the entire backend infrastructure (Database, Kafka, Monitoring, etc.), simply use Docker Compose from the root directory:
```bash
docker-compose up -d
```
*This will automatically provision PostgreSQL, pgAdmin, Kafka, Zookeeper, Prometheus, Grafana, and the FastAPI backend in isolated containers.*

### Local Backend Setup (Optional, without Docker)
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
4. Start the FastAPI server locally:
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