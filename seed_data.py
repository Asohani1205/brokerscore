from sqlalchemy.orm import Session
from database import SessionLocal
import models
import qrcode
from io import BytesIO
import base64

# Sample broker data
brokers_data = [
    {
        "name": "Abhjeet Geete",
        "image_url": "https://ui-avatars.com/api/?name=Abhjeet+Geete&background=random&color=fff&size=150&font-size=0.4",
        "score": 0
    },
    {
        "name": "Prateek Sahu",
        "image_url": "https://ui-avatars.com/api/?name=Prateek+Sahu&background=random&color=fff&size=150&font-size=0.4",
        "score": 0
    },
    {
        "name": "Lalit Sahu",
        "image_url": "https://ui-avatars.com/api/?name=Lalit+Sahu&background=random&color=fff&size=150&font-size=0.4",
        "score": 0
    },
    {
        "name": "Abhishek Sahu",
        "image_url": "https://ui-avatars.com/api/?name=Abhishek+Sahu&background=random&color=fff&size=150&font-size=0.4",
        "score": 0
    },
    {
        "name": "Sachin Sahu",
        "image_url": "https://ui-avatars.com/api/?name=Sachin+Sahu&background=random&color=fff&size=150&font-size=0.4",
        "score": 0
    },
    {
        "name": "Abhishek Mishra",
        "image_url": "https://ui-avatars.com/api/?name=Abhishek+Mishra&background=random&color=fff&size=150&font-size=0.4",
        "score": 0
    }
]

def generate_qr_code(broker_id: int) -> str:
    """Generate QR code for a broker"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data("https://endlessrealty.in")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def seed_database():
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(models.Referral).delete()
        db.query(models.Broker).delete()
        db.commit()

        # Add new brokers
        for broker_data in brokers_data:
            broker = models.Broker(**broker_data)
            db.add(broker)
            db.commit()
            db.refresh(broker)
            
            # Generate and update QR code
            broker.qr_code_url = generate_qr_code(broker.id)
            db.commit()

        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database() 