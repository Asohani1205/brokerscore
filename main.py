from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
import models
from database import SessionLocal, engine
from pydantic import BaseModel
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class BrokerBase(BaseModel):
    id: int
    name: str
    image_url: str
    score: int
    qr_code_url: str

    class Config:
        from_attributes = True

class CustomerBase(BaseModel):
    id: int
    name: str
    contact_number: str
    email: str
    registration_date: datetime
    broker_id: int

    class Config:
        from_attributes = True

class CustomerCreate(BaseModel):
    name: str
    contact_number: str
    email: str
    broker_id: int

# Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        brokers = db.query(models.Broker).all()
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "brokers": brokers}
        )
    except Exception as e:
        logger.error(f"Error in dashboard route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/broker/{broker_id}", response_class=HTMLResponse)
async def broker_detail(request: Request, broker_id: int, db: Session = Depends(get_db)):
    try:
        broker = db.query(models.Broker).filter(models.Broker.id == broker_id).first()
        if not broker:
            raise HTTPException(status_code=404, detail="Broker not found")
        
        customers = db.query(models.Customer).filter(models.Customer.broker_id == broker_id).all()
        
        # Log the data being passed to the template
        logger.info(f"Broker data: {broker.__dict__}")
        logger.info(f"Number of customers: {len(customers)}")
        
        return templates.TemplateResponse(
            "broker_detail.html",
            {
                "request": request,
                "broker": broker,
                "customers": customers
            }
        )
    except Exception as e:
        logger.error(f"Error in broker_detail route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/customers/")
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    try:
        # Check if broker exists
        broker = db.query(models.Broker).filter(models.Broker.id == customer.broker_id).first()
        if not broker:
            raise HTTPException(status_code=404, detail="Broker not found")
        
        # Check if customer already exists
        existing_customer = db.query(models.Customer).filter(
            (models.Customer.contact_number == customer.contact_number) |
            (models.Customer.email == customer.email)
        ).first()
        
        if existing_customer:
            raise HTTPException(status_code=400, detail="Customer with this contact number or email already exists")
        
        # Create new customer
        db_customer = models.Customer(**customer.dict())
        db.add(db_customer)
        
        # Create referral
        db_referral = models.Referral(
            broker_id=customer.broker_id,
            customer_id=db_customer.id
        )
        db.add(db_referral)
        
        # Update broker score
        broker.score += 1
        
        db.commit()
        return {"message": "Customer registered successfully"}
    except Exception as e:
        logger.error(f"Error in create_customer route: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# API endpoints
@app.get("/api/brokers", response_model=List[BrokerBase])
def get_brokers(db: Session = Depends(get_db)):
    try:
        return db.query(models.Broker).all()
    except Exception as e:
        logger.error(f"Error in get_brokers route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/broker/{broker_id}", response_model=BrokerBase)
def get_broker(broker_id: int, db: Session = Depends(get_db)):
    try:
        broker = db.query(models.Broker).filter(models.Broker.id == broker_id).first()
        if not broker:
            raise HTTPException(status_code=404, detail="Broker not found")
        return broker
    except Exception as e:
        logger.error(f"Error in get_broker route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False) 