# README.md

## Relate.io MVP

### Prerequisites
- PostgreSQL installed and running (or use Docker).
- Python virtual env: `python -m venv venv; source venv/bin/activate; pip install -r backend/requirements.txt`
- Node.js for frontend: `cd frontend; npm install`
- .env in root or backend with keys (see above).

### How to Run Locally (Without Docker)
1. Start Postgres: Ensure DB is created (`createdb relate_io`).
2. Run backend: `cd backend; uvicorn app:app --reload`
3. Run frontend: `cd frontend; npm run dev`
4. Run Celery worker: `cd backend; celery -A tasks worker --loglevel=info`
5. Run Celery beat: `cd backend; celery -A tasks beat --loglevel=info`

### How to Run with Docker
1. Create .env in root with variables.
2. `docker-compose up -d`
3. Access:
   - Backend Swagger: http://localhost:8000/docs
   - Frontend Dashboard: http://localhost:3000
   - Feedback form: http://localhost:3000/feedback?client_id=1 (after importing clients)

### Testing the App
1. Import clients: Use Swagger or curl to POST /import-clients with a CSV file.
   Example CSV: 
   name,email,portfolio_value
   John Doe,john@example.com,1000.5
   Jane Doe,jane@example.com,2000

2. Generate update: POST /generate-update/{client_id} or wait for scheduler.
3. Check email (use SendGrid dashboard or mailtrap for testing).
4. Submit feedback: Click link in email or visit /feedback?client_id=1, submit form.
5. View dashboard: Refresh http://localhost:3000 to see clients and feedback.

### Troubleshooting
- Ensure all env vars are set.
- Check logs for errors.
- For AI, verify OpenAI key is valid.
- If Torch/Transformers issues, ensure CPU/GPU compatibility.

This setup is robust for MVP; expand with auth, tests, etc., as per roadmap.