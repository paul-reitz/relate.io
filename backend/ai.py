# backend/ai.py
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from transformers import pipeline
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logger = logging.getLogger(__name__)

try:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))
    sentiment_pipeline = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
except Exception as e:
    logger.error(f"Error initializing AI models: {e}")
    raise

def generate_narrative(data: dict) -> str:
    try:
        prompt = ChatPromptTemplate.from_template(
            "Generate a weekly portfolio summary: PnL: {pnl}%, Top holdings: {top_holdings}. Keep it professional and match the organization's tone."
        )
        chain = prompt | llm
        response = chain.invoke(data)
        return response.content
    except Exception as e:
        logger.error(f"Error generating narrative: {e}")
        raise ValueError("Failed to generate narrative")

def analyze_feedback(text: str) -> str:
    try:
        if not text:
            return "NEUTRAL"
        result = sentiment_pipeline(text)[0]
        label = result['label']
        if '1 star' in label or '2 stars' in label:
            return "NEGATIVE"
        elif '4 stars' in label or '5 stars' in label:
            return "POSITIVE"
        else:
            return "NEUTRAL"
    except Exception as e:
        logger.error(f"Error analyzing feedback: {e}")
        return "ERROR"