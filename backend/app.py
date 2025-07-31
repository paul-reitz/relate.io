from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
from ingestion import import_clients_from_csv
from database import create_tables
from services import generate_and_send_update, submit_feedback, get_clients, get_feedback
from tasks import app as celery_app  # For reference
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()  # This must be here, at module level!

# Create tables on startup
create_tables()

@app.post("/onboard-advisor")
def onboard_advisor():
    logger.info("Advisor onboarded")
    return {"message": "Advisor onboarded"}

@app.post("/import-clients")
async def import_clients(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "Invalid file type")
    try:
        contents = await file.read()
        clients = import_clients_from_csv(contents)
        num_imported = len(clients)
        logger.info(f"Imported {num_imported} clients")
        return {"message": f"{num_imported} clients imported"}
    except Exception as e:
        logger.error(f"Error importing clients: {e}")
        raise HTTPException(500, "Failed to import clients")

@app.get("/clients")
def list_clients():
    try:
        clients = get_clients()
        return clients
    except Exception as e:
        logger.error(f"Error fetching clients: {e}")
        raise HTTPException(500, "Failed to fetch clients")

@app.post("/generate-update/{client_id}")
def generate_update(client_id: int):
    try:
        generate_and_send_update(client_id)
        return {"message": "Update sent"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error generating update for client {client_id}: {e}")
        raise HTTPException(500, "Failed to send update")

@app.post("/feedback")
def feedback_endpoint(payload: dict):
    client_id = payload.get('client_id')
    text = payload.get('text')
    if not client_id or not text:
        raise HTTPException(400, "Missing client_id or text")
    try:
        sentiment = submit_feedback(client_id, text)
        return {"sentiment": sentiment}
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(500, "Failed to submit feedback")

@app.get("/feedback")
def list_feedback():
    try:
        feedback = get_feedback()
        return feedback
    except Exception as e:
        logger.error(f"Error fetching feedback: {e}")
        raise HTTPException(500, "Failed to fetch feedback")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)