from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Anomaly
from app.services.explain import explain_anomaly

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ExplainReq(BaseModel):
    anomaly_id: int

@router.post("/explain")
def explain(req: ExplainReq, db: Session = Depends(get_db)):
    a = db.query(Anomaly).filter(Anomaly.id == req.anomaly_id).first()
    if not a:
        return {"error": "anomaly not found"}
    payload = {
        "metric": a.metric,
        "direction": a.direction,
        "zscore": a.zscore,
        "observed": a.observed,
        "expected": a.expected,
        "entity_type": a.entity_type,
        "entity_id": a.entity_id,
    }
    out = explain_anomaly(payload)
    return {"anomaly_id": a.id, **out}
