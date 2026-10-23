from fastapi import FastAPI
from pydantic import BaseModel, Field
from src.engine import analyze, load_incidents

app = FastAPI(title='IncidentIQ AI API', version='1.0.0', description='Offline incident similarity and team suggestion.')

class IncidentInput(BaseModel):
    short_description: str = Field(min_length=1, max_length=300)
    description: str = Field(default='', max_length=5000)
    top_k: int = Field(default=5, ge=1, le=50)
    minimum_score: float = Field(default=0.1, ge=0, le=1)

@app.get('/health')
def health():
    return {'status': 'ok', 'indexed_incidents': len(load_incidents())}

@app.post('/analyze')
def analyze_incident(payload: IncidentInput):
    return analyze(payload.short_description, payload.description, payload.top_k, payload.minimum_score)
