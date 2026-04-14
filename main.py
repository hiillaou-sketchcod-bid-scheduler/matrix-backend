import os
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

# Database Setup
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./matrix.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class MatrixRecord(Base):
    __tablename__ = "matrix_records"
    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    data = Column(Text) # JSON string

class MatrixPendingRecord(Base):
    __tablename__ = "matrix_pending_records"
    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    data = Column(Text) # JSON string

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Enterprise Matrix API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/history")
def get_history():
    db = SessionLocal()
    try:
        records = db.query(MatrixRecord).order_by(MatrixRecord.created_at.desc()).all()
        return [json.loads(r.data) for r in records]
    finally:
        db.close()

@app.post("/api/history")
async def save_history(request: Request):
    data = await request.json()
    record_id = str(data.get("id"))
    if not record_id:
        raise HTTPException(status_code=400, detail="Missing ID")
    
    db = SessionLocal()
    try:
        new_record = MatrixRecord(
            id=record_id,
            data=json.dumps(data)
        )
        db.add(new_record)
        db.commit()
        return {"status": "success"}
    finally:
        db.close()

@app.delete("/api/history/{record_id}")
def delete_history(record_id: str):
    db = SessionLocal()
    try:
        record = db.query(MatrixRecord).filter(MatrixRecord.id == record_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Not found")
        db.delete(record)
        db.commit()
        return {"status": "success"}
    finally:
        db.close()

@app.get("/api/pending")
def get_pending():
    db = SessionLocal()
    try:
        records = db.query(MatrixPendingRecord).order_by(MatrixPendingRecord.created_at.desc()).all()
        return [json.loads(r.data) for r in records]
    finally:
        db.close()

@app.post("/api/pending")
async def save_pending(request: Request):
    data = await request.json()
    record_id = str(data.get("id"))
    if not record_id:
        raise HTTPException(status_code=400, detail="Missing ID")
    
    db = SessionLocal()
    try:
        new_record = MatrixPendingRecord(
            id=record_id,
            data=json.dumps(data)
        )
        db.add(new_record)
        db.commit()
        return {"status": "success"}
    finally:
        db.close()

@app.delete("/api/pending/{record_id}")
def delete_pending(record_id: str):
    db = SessionLocal()
    try:
        record = db.query(MatrixPendingRecord).filter(MatrixPendingRecord.id == record_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Not found")
        db.delete(record)
        db.commit()
        return {"status": "success"}
    finally:
        db.close()

